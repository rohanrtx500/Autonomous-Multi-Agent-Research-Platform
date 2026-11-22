import os
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from loguru import logger

from app.api.v1.endpoints import router as api_v1_router
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Autonomous Multi-Agent AI Research Platform Backend powered by LangGraph, ChromaDB & FastAPI",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Production-Grade Permissive CORS (Allows Localhost, Vercel deployments, & custom domains)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    """Injects a unique request ID and logs execution latency."""
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
    start_time = time.time()

    try:
        response: Response = await call_next(request)
        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-Ms"] = str(elapsed_ms)
        logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({elapsed_ms}ms) [{request_id}]")
        return response
    except Exception as exc:  # noqa: BLE001
        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        logger.error(f"{request.method} {request.url.path} uncaught error ({elapsed_ms}ms): {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "InternalServerError",
                "message": f"An unexpected error occurred during request processing: {exc!s}",
                "request_id": request_id
            },
            headers={
                "X-Request-ID": request_id,
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )


app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API v{settings.VERSION}",
        "docs": "/docs",
        "api_v1": settings.API_V1_STR,
        "environment": settings.ENVIRONMENT
    }


@app.get("/api/v1/download-sample/{filename}")
async def download_sample(filename: str):
    """
    Safely serves pre-packaged sample files without hardcoded platform paths.
    """
    allowed_files = [
        "Universal_Basic_Income_Research_2025.txt",
        "Universal_Basic_Income_Research_2025.pdf",
        "Universal_Basic_Income_Research_2025.md",
        "Quantum_Grid_Optimization_Whitepaper_2025.pdf"
    ]
    clean_name = os.path.basename(filename)
    if clean_name not in allowed_files:
        raise HTTPException(status_code=404, detail="Requested sample file not found.")

    # Search in project root or data directory
    candidate_paths = [
        Path(settings.PROJECT_ROOT) / clean_name,
        Path(settings.DATA_DIR) / clean_name,
        Path(settings.BACKEND_ROOT) / clean_name,
    ]

    for p in candidate_paths:
        if p.exists() and p.is_file():
            return FileResponse(path=str(p), filename=clean_name, media_type="application/octet-stream")

    raise HTTPException(status_code=404, detail="Sample file does not exist on disk.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
