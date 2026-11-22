import asyncio
import os
import re
import time
import uuid
from typing import Any

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from loguru import logger
from pydantic import BaseModel, Field

from app.core.config import settings
from app.graph.workflow import research_graph
from app.infrastructure.document_loader import DocumentLoaderService
from app.infrastructure.job_repository import job_repository
from app.infrastructure.vector_store import VectorStoreService
from app.schemas.state import ResearchState

router = APIRouter()
vector_store = VectorStoreService()
doc_loader = DocumentLoaderService()


class ResearchRequest(BaseModel):
    objective: str = Field(..., min_length=3, max_length=1500)
    max_iterations: int = Field(default=2, ge=1, le=5)
    background: bool = Field(default=False, description="If true, returns immediately with job_id for polling.")


class ResearchResponse(BaseModel):
    job_id: str
    status: str
    objective: str
    final_report_markdown: str | None = None
    evaluation_metrics: dict[str, Any] | None = None
    citation_verification: dict[str, Any] | None = None
    retrieved_papers_count: int = 0
    retrieved_web_count: int = 0
    retrieved_github_count: int = 0
    retrieved_user_docs_count: int = 0
    agent_logs_count: int = 0
    agent_logs: list[dict[str, Any]] = Field(default_factory=list)
    execution_time_seconds: float = 0.0
    error_message: str | None = None


def _execute_graph_sync(job_id: str, objective: str, max_iterations: int) -> dict[str, Any]:
    """Synchronous worker that executes the research graph in a separate thread."""
    start_time = time.time()
    job_repository.update_progress(job_id, status="running", progress_percent=15, current_step="planning")

    initial_state: ResearchState = {
        "job_id": job_id,
        "objective": objective,
        "sub_tasks": [],
        "retrieved_papers": [],
        "retrieved_web_sources": [],
        "retrieved_github_repos": [],
        "retrieved_user_docs": [],
        "synthesized_knowledge": {},
        "method_comparisons": [],
        "research_gaps": [],
        "experiment_plan": [],
        "iteration_count": 0,
        "max_iterations": max_iterations,
        "status": "planning",
        "agent_logs": []
    }

    try:
        final_state = research_graph.invoke(initial_state)
        elapsed = round(time.time() - start_time, 2)
        job_repository.complete_job(job_id, final_state, execution_time_seconds=elapsed)
        return final_state
    except Exception as e:
        logger.error(f"Research execution failure for job {job_id}: {e}")
        job_repository.fail_job(job_id, error_message=str(e))
        raise


@router.post("/research", response_model=ResearchResponse)
async def start_research(request: ResearchRequest):
    """
    Initiates an autonomous multi-agent research workflow.
    Non-blocking: Executes the graph in a worker thread to preserve the async event loop.
    Supports both immediate polling (background=True) and synchronous response (background=False).
    """
    clean_obj = request.objective.strip()
    if len(clean_obj) < 3:
        raise HTTPException(status_code=400, detail="Objective must be at least 3 characters long.")

    job_id = f"job_{uuid.uuid4().hex[:10]}"
    job_repository.create_job(job_id=job_id, objective=clean_obj, max_iterations=request.max_iterations)

    if request.background:
        # Launch background task and return job_id immediately
        asyncio.create_task(asyncio.to_thread(_execute_graph_sync, job_id, clean_obj, request.max_iterations))
        return ResearchResponse(
            job_id=job_id,
            status="running",
            objective=clean_obj,
            execution_time_seconds=0.0
        )

    # Synchronous execution off the main event loop
    start_time = time.time()
    try:
        final_state = await asyncio.wait_for(
            asyncio.to_thread(_execute_graph_sync, job_id, clean_obj, request.max_iterations),
            timeout=float(settings.JOB_TIMEOUT_SECONDS)
        )
    except TimeoutError:
        job_repository.fail_job(job_id, "Execution exceeded maximum configured timeout.")
        raise HTTPException(status_code=504, detail=f"Research job timed out after {settings.JOB_TIMEOUT_SECONDS}s.")
    except Exception as e:  # noqa: BLE001
        logger.error(f"Endpoint execution error for job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Research graph execution failed: {e!s}")

    elapsed = round(time.time() - start_time, 2)
    eval_metrics = final_state.get("evaluation_metrics")
    metrics_dict = eval_metrics.model_dump() if hasattr(eval_metrics, "model_dump") else eval_metrics
    citation_verif = final_state.get("citation_verification")
    citation_dict = citation_verif.model_dump() if hasattr(citation_verif, "model_dump") else citation_verif

    raw_logs = final_state.get("agent_logs", [])
    logs_list = [l.model_dump() if hasattr(l, "model_dump") else l for l in raw_logs]

    return ResearchResponse(
        job_id=job_id,
        status=final_state.get("status", "completed"),
        objective=clean_obj,
        final_report_markdown=final_state.get("final_report_markdown"),
        evaluation_metrics=metrics_dict,
        citation_verification=citation_dict,
        retrieved_papers_count=len(final_state.get("retrieved_papers", [])),
        retrieved_web_count=len(final_state.get("retrieved_web_sources", [])),
        retrieved_github_count=len(final_state.get("retrieved_github_repos", [])),
        retrieved_user_docs_count=len(final_state.get("retrieved_user_docs", [])),
        agent_logs_count=len(logs_list),
        agent_logs=logs_list,
        execution_time_seconds=elapsed,
    )


@router.get("/jobs", response_model=list[dict[str, Any]])
async def list_jobs(limit: int = Query(default=20, ge=1, le=100)):
    """Lists persistent research jobs ordered by recency."""
    return job_repository.list_jobs(limit=limit)


@router.get("/jobs/{job_id}")
async def get_job_by_id(job_id: str):
    """Returns the persistent status, artifacts, and telemetry of a specific research job."""
    job = job_repository.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
    return job


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    """Cancels a pending or running research job."""
    success = job_repository.cancel_job(job_id)
    if not success:
        raise HTTPException(status_code=400, detail=f"Job '{job_id}' could not be cancelled or is already finished.")
    return {"job_id": job_id, "status": "cancelled", "message": "Job cancellation recorded."}


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Secure document ingestion endpoint.
    Guarantees:
    - Path traversal protection (canonical path checking).
    - Server-generated unique temporary filename.
    - File extension and magic byte validation.
    - Streaming byte size enforcement (prevents memory exhaustion).
    - Guaranteed cleanup of only application-owned temp files.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename.")

    # 1. Sanitize and validate filename & extension
    original_name = os.path.basename(file.filename.replace("\\", "/"))
    ext = os.path.splitext(original_name)[1].lower()

    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # 2. Canonical upload directory resolution
    canonical_upload_dir = os.path.realpath(settings.UPLOAD_DIR)
    safe_name = f"{uuid.uuid4().hex}_{re.sub(r'[^a-zA-Z0-9_\-\.]', '_', original_name)}"
    temp_path = os.path.join(canonical_upload_dir, safe_name)
    resolved_path = os.path.realpath(temp_path)

    if not resolved_path.startswith(canonical_upload_dir):
        raise HTTPException(status_code=400, detail="Invalid path destination detected (path traversal rejected).")

    # 3. Stream content to disk with strict size limit
    bytes_read = 0
    chunk_size = 64 * 1024  # 64 KB
    header_bytes = b""

    try:
        with open(resolved_path, "wb") as buffer:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                if len(header_bytes) < 16:
                    header_bytes += chunk[:16 - len(header_bytes)]
                bytes_read += len(chunk)
                if bytes_read > settings.MAX_UPLOAD_SIZE_BYTES:
                    max_mb = settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)
                    raise HTTPException(
                        status_code=413,
                        detail=f"File exceeds maximum allowed size of {max_mb}MB."
                    )
                buffer.write(chunk)

        # 4. Content / Magic byte validation
        if ext == ".pdf" and not header_bytes.startswith(b"%PDF-"):
            raise HTTPException(status_code=400, detail="Corrupted file: Expected valid PDF header (%PDF-).")
        elif ext in [".docx", ".pptx"] and not header_bytes.startswith(b"PK\x03\x04"):
            raise HTTPException(status_code=400, detail=f"Corrupted file: Expected valid Office Zip container for {ext}.")

        # 5. Extract and index chunks into hybrid vector store off the main event loop
        def _process_and_index():
            loaded_docs = doc_loader.load_file(resolved_path, filename=original_name)
            vector_store.delete_document(original_name)
            vector_store.add_documents(loaded_docs)
            return loaded_docs

        docs = await asyncio.to_thread(_process_and_index)

        return {
            "filename": original_name,
            "status": "success",
            "chunks_ingested": len(docs),
            "message": f"Successfully ingested {len(docs)} chunks from {original_name} into knowledge base."
        }
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve)) from ve
    except Exception as e:
        logger.error(f"Document ingestion failed for {original_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e!s}") from e
    finally:
        # Guaranteed cleanup of application-created temporary file
        if os.path.exists(resolved_path) and resolved_path.startswith(canonical_upload_dir):
            try:
                os.remove(resolved_path)
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Could not remove temporary file {resolved_path}: {e}")


@router.get("/documents")
async def list_ingested_documents():
    """Returns the list of documents currently ingested into the knowledge base."""
    return vector_store.list_documents()


@router.delete("/documents/{filename}")
async def delete_ingested_document(filename: str):
    """Deletes an ingested document and all its chunks from the knowledge base."""
    safe_name = os.path.basename(filename.replace("\\", "/"))
    deleted_count = vector_store.delete_document(safe_name)
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Document '{safe_name}' not found in knowledge base.")
    return {
        "filename": safe_name,
        "deleted_chunks": deleted_count,
        "message": f"Successfully removed '{safe_name}' ({deleted_count} chunks deleted)."
    }


@router.get("/status")
async def get_status(job_id: str | None = Query(None)):
    """Returns persistent job status or system telemetry."""
    if job_id:
        job = job_repository.get_job(job_id)
        if job:
            return {
                "job_id": job_id,
                "status": job["status"],
                "iteration": job["iteration_count"],
                "progress_percent": job["progress_percent"],
                "current_step": job["current_step"],
                "agent_logs": job["agent_logs"]
            }
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    jobs = job_repository.list_jobs(limit=100)
    completed_jobs = [j for j in jobs if j["status"] == "completed"]
    return {
        "active_jobs_count": sum(1 for j in jobs if j["status"] in ["pending", "running"]),
        "total_jobs_stored": len(jobs),
        "completed_jobs_count": len(completed_jobs),
        "system_status": "Healthy",
        "environment": settings.ENVIRONMENT
    }


@router.get("/papers")
async def get_papers(job_id: str | None = Query(None)):
    """Returns retrieved academic papers for a given research job."""
    if job_id:
        job = job_repository.get_job(job_id)
        if job and job.get("final_report_markdown"):
            return {"job_id": job_id, "retrieved_counts": job.get("retrieved_counts")}
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found or has no papers.")

    return {"message": "Specify a job_id to inspect retrieved literature."}


@router.get("/metrics")
async def get_metrics():
    """
    Returns empirical evaluation metrics aggregated from genuine persisted jobs.
    No synthetic score fabrication.
    """
    jobs = job_repository.list_jobs(limit=100)
    completed_with_metrics = [
        j["evaluation_metrics"] for j in jobs
        if j.get("evaluation_metrics") and j.get("status") == "completed"
    ]

    if not completed_with_metrics:
        return {
            "status": "no_telemetry_collected",
            "message": "No completed research jobs recorded yet. Run a research query to generate real metrics.",
            "total_research_jobs_executed": 0,
            "faithfulness_avg": None,
            "relevance_avg": None,
            "grounding_avg": None,
            "confidence_avg": None,
            "precision_at_k_avg": None,
            "mrr_avg": None
        }

    n = len(completed_with_metrics)
    faithfulness_avg = round(sum(m.get("faithfulness_score", 0.0) for m in completed_with_metrics) / n, 4)
    relevance_avg = round(sum(m.get("relevance_score", 0.0) for m in completed_with_metrics) / n, 4)
    grounding_avg = round(sum(m.get("grounding_score", 0.0) for m in completed_with_metrics) / n, 4)
    confidence_avg = round(sum(m.get("confidence_score", 0.0) for m in completed_with_metrics) / n, 4)

    prec_scores = [m.get("precision_at_k") for m in completed_with_metrics if m.get("precision_at_k") is not None]
    precision_avg = round(sum(prec_scores) / len(prec_scores), 4) if prec_scores else None

    mrr_scores = [m.get("mrr") for m in completed_with_metrics if m.get("mrr") is not None]
    mrr_avg = round(sum(mrr_scores) / len(mrr_scores), 4) if mrr_scores else None

    return {
        "status": "active_telemetry",
        "total_research_jobs_executed": n,
        "faithfulness_avg": faithfulness_avg,
        "relevance_avg": relevance_avg,
        "grounding_avg": grounding_avg,
        "confidence_avg": confidence_avg,
        "precision_at_k_avg": precision_avg,
        "mrr_avg": mrr_avg,
        "supported_agent_nodes": 13
    }


@router.get("/health")
async def health_check():
    """System health check endpoint covering vector storage and database status."""
    vstore_health = vector_store.health_check()
    db_ok = job_repository.session_factory is not None

    return {
        "status": "ok" if db_ok and vstore_health["status"] in ["healthy", "ready"] else "degraded",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": "connected" if db_ok else "unavailable",
        "vector_store": vstore_health,
        "llm_provider": settings.DEFAULT_MODEL_PROVIDER,
        "llm_configured": bool(settings.GEMINI_API_KEY or settings.OPENAI_API_KEY or settings.GROQ_API_KEY),
        "tavily_configured": bool(settings.TAVILY_API_KEY)
    }
