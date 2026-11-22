import json
from datetime import UTC, datetime, timedelta
from typing import Any

from loguru import logger

from app.infrastructure.database import ResearchJobModel, SessionLocal


class JobRepository:
    def __init__(self):
        self.session_factory = SessionLocal

    def create_job(self, job_id: str, objective: str, max_iterations: int = 2) -> dict[str, Any]:
        """Creates a new job in the pending state."""
        if not self.session_factory:
            return {"job_id": job_id, "status": "pending", "objective": objective}

        with self.session_factory() as session:
            job = ResearchJobModel(
                job_id=job_id,
                objective=objective,
                status="pending",
                progress_percent=5,
                current_step="pending",
                max_iterations=max_iterations,
                iteration_count=0
            )
            session.add(job)
            session.commit()
            session.refresh(job)
            return job.to_dict()

    def update_progress(
        self,
        job_id: str,
        status: str,
        progress_percent: int,
        current_step: str,
        error_message: str | None = None
    ):
        """Updates job progress and current execution step."""
        if not self.session_factory:
            return

        try:
            with self.session_factory() as session:
                job = session.query(ResearchJobModel).filter_by(job_id=job_id).first()
                if job:
                    job.status = status
                    job.progress_percent = progress_percent
                    job.current_step = current_step
                    if error_message:
                        job.error_message = error_message
                    job.updated_at = datetime.now(UTC)
                    session.commit()
        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to update progress for job {job_id}: {e}")

    def complete_job(
        self,
        job_id: str,
        final_state: dict[str, Any],
        execution_time_seconds: float
    ) -> dict[str, Any] | None:
        """Marks job as completed and stores final artifacts."""
        if not self.session_factory:
            return None

        try:
            with self.session_factory() as session:
                job = session.query(ResearchJobModel).filter_by(job_id=job_id).first()
                if not job:
                    return None

                eval_metrics = final_state.get("evaluation_metrics")
                if hasattr(eval_metrics, "model_dump"):
                    eval_metrics = eval_metrics.model_dump()

                citation_verif = final_state.get("citation_verification")
                if hasattr(citation_verif, "model_dump"):
                    citation_verif = citation_verif.model_dump()

                raw_logs = final_state.get("agent_logs", [])
                logs_list = [l.model_dump() if hasattr(l, "model_dump") else l for l in raw_logs]

                counts = {
                    "papers": len(final_state.get("retrieved_papers", [])),
                    "web": len(final_state.get("retrieved_web_sources", [])),
                    "github": len(final_state.get("retrieved_github_repos", [])),
                    "user_docs": len(final_state.get("retrieved_user_docs", []))
                }

                job.status = final_state.get("status", "completed")
                job.progress_percent = 100
                job.current_step = "completed"
                job.completed_at = datetime.now(UTC)
                job.execution_time_seconds = execution_time_seconds
                job.iteration_count = final_state.get("iteration_count", 0)
                job.final_report_markdown = final_state.get("final_report_markdown")
                job.evaluation_metrics_json = json.dumps(eval_metrics) if eval_metrics else None
                job.citation_verification_json = json.dumps(citation_verif) if citation_verif else None
                job.retrieved_counts_json = json.dumps(counts)
                job.agent_logs_json = json.dumps(logs_list)

                session.commit()
                session.refresh(job)
                return job.to_dict()
        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to persist completion for job {job_id}: {e}")
            return None

    def fail_job(self, job_id: str, error_message: str):
        """Marks job as failed with descriptive error message."""
        if not self.session_factory:
            return

        try:
            with self.session_factory() as session:
                job = session.query(ResearchJobModel).filter_by(job_id=job_id).first()
                if job:
                    job.status = "failed"
                    job.error_message = error_message
                    job.completed_at = datetime.now(UTC)
                    job.updated_at = datetime.now(UTC)
                    session.commit()
        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to record failure for job {job_id}: {e}")

    def cancel_job(self, job_id: str) -> bool:
        """Sets job status to cancelled."""
        if not self.session_factory:
            return False

        try:
            with self.session_factory() as session:
                job = session.query(ResearchJobModel).filter_by(job_id=job_id).first()
                if job and job.status in ["pending", "running"]:
                    job.status = "cancelled"
                    job.error_message = "Execution cancelled by user."
                    job.completed_at = datetime.now(UTC)
                    session.commit()
                    return True
        except Exception as e:  # noqa: BLE001
            logger.error(f"Failed to cancel job {job_id}: {e}")
        return False

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        """Retrieves a single job by ID."""
        if not self.session_factory:
            return None

        with self.session_factory() as session:
            job = session.query(ResearchJobModel).filter_by(job_id=job_id).first()
            return job.to_dict() if job else None

    def list_jobs(self, limit: int = 50) -> list[dict[str, Any]]:
        """Lists recent research jobs ordered by creation date."""
        if not self.session_factory:
            return []

        with self.session_factory() as session:
            jobs = session.query(ResearchJobModel).order_by(ResearchJobModel.created_at.desc()).limit(limit).all()
            return [job.to_dict() for job in jobs]

    def cleanup_old_jobs(self, retention_days: int = 30) -> int:
        """Removes jobs older than retention_days."""
        if not self.session_factory:
            return 0

        cutoff = datetime.now(UTC) - timedelta(days=retention_days)
        with self.session_factory() as session:
            deleted = session.query(ResearchJobModel).filter(ResearchJobModel.created_at < cutoff).delete()
            session.commit()
            return deleted


job_repository = JobRepository()
