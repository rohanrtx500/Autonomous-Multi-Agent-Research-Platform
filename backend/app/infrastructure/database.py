import json
from datetime import UTC, datetime
from typing import Any

from loguru import logger
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

Base = declarative_base()


class ResearchJobModel(Base):
    __tablename__ = "research_jobs"

    job_id = Column(String(64), primary_key=True, index=True)
    objective = Column(Text, nullable=False)
    status = Column(String(32), nullable=False, default="pending", index=True)
    progress_percent = Column(Integer, default=0)
    current_step = Column(String(64), default="initialized")
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    completed_at = Column(DateTime, nullable=True)
    execution_time_seconds = Column(Float, default=0.0)
    max_iterations = Column(Integer, default=2)
    iteration_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    final_report_markdown = Column(Text, nullable=True)
    evaluation_metrics_json = Column(Text, nullable=True)
    citation_verification_json = Column(Text, nullable=True)
    retrieved_counts_json = Column(Text, nullable=True)
    agent_logs_json = Column(Text, nullable=True)

    def to_dict(self) -> dict[str, Any]:
        eval_metrics = json.loads(self.evaluation_metrics_json) if self.evaluation_metrics_json else None
        citation_verif = json.loads(self.citation_verification_json) if self.citation_verification_json else None
        counts = json.loads(self.retrieved_counts_json) if self.retrieved_counts_json else {}
        logs = json.loads(self.agent_logs_json) if self.agent_logs_json else []

        return {
            "job_id": self.job_id,
            "objective": self.objective,
            "status": self.status,
            "progress_percent": self.progress_percent,
            "current_step": self.current_step,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "execution_time_seconds": self.execution_time_seconds,
            "max_iterations": self.max_iterations,
            "iteration_count": self.iteration_count,
            "error_message": self.error_message,
            "final_report_markdown": self.final_report_markdown,
            "evaluation_metrics": eval_metrics,
            "citation_verification": citation_verif,
            "retrieved_counts": counts,
            "retrieved_papers_count": counts.get("papers", 0),
            "retrieved_web_count": counts.get("web", 0),
            "retrieved_github_count": counts.get("github", 0),
            "retrieved_user_docs_count": counts.get("user_docs", 0),
            "agent_logs": logs,
            "agent_logs_count": len(logs)
        }


# Database engine setup
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

try:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        pool_pre_ping=True
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    logger.info(f"Database initialized successfully with URL schema: {settings.DATABASE_URL.split('://')[0]}://***")
except Exception as e:  # noqa: BLE001
    logger.error(f"Failed to initialize database: {e}")
    engine = None
    SessionLocal = None


def get_db():
    if not SessionLocal:
        raise RuntimeError("Database session factory is not configured.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
