import time
from typing import Any

from loguru import logger

from app.core.config import settings
from app.schemas.evaluation import AgentExecutionLog

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_groq import ChatGroq
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None
    ChatGroq = None
    ChatGoogleGenerativeAI = None


def extract_llm_text(response: Any) -> str:
    """Safely extracts text content across different LangChain message and multimodal structures."""
    if response is None:
        return ""
    content = getattr(response, "content", response)
    if isinstance(content, str):
        return content.strip()
    elif isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            elif hasattr(item, "text"):
                parts.append(str(item.text))
            else:
                parts.append(str(item))
        return "".join(parts).strip()
    return str(content).strip()


def build_unified_source_registry(
    papers: list[Any],
    web_sources: list[Any],
    user_docs: list[Any]
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    """
    Standardizes source ordering and 1-based indexing identically across
    WriterAgent, CitationVerificationAgent, and EvaluatorAgent.
    """
    all_sources: list[dict[str, Any]] = []
    registry: dict[str, dict[str, Any]] = {}

    idx = 1
    # 1. Registered Web Sources (Real-time Web Analysis)
    for w in web_sources:
        title = getattr(w, "title", "") or "Web Source"
        content = getattr(w, "content", "") or ""
        url = getattr(w, "url", "") or ""
        source_id = getattr(w, "id", "") or f"web_{idx}"
        item = {
            "index": idx,
            "id": source_id,
            "type": "Web Source",
            "title": title,
            "url": url,
            "snippet": content[:350],
            "text": f"{title}. {content}",
            "meta": "Real-world web analysis",
        }
        all_sources.append(item)
        registry[str(idx)] = item
        if source_id:
            registry[source_id] = item
        idx += 1

    # 2. Registered Academic Papers (Scholarly Literature)
    for p in papers:
        title = getattr(p, "title", "") or "Academic Paper"
        abstract = getattr(p, "abstract", "") or ""
        url = getattr(p, "url", "") or ""
        source_id = getattr(p, "id", "") or f"paper_{idx}"
        authors = getattr(p, "authors", []) or []
        year = getattr(p, "published_year", None) or 2024
        meta = f"{', '.join(authors[:2]) if authors else 'Scholarly Publication'} ({year})"
        item = {
            "index": idx,
            "id": source_id,
            "type": "Academic Paper",
            "title": title,
            "url": url,
            "snippet": abstract[:350],
            "text": f"{title}. {abstract}",
            "meta": meta,
        }
        all_sources.append(item)
        registry[str(idx)] = item
        if source_id:
            registry[source_id] = item
        idx += 1

    # 3. Registered User Documents (Knowledge Base)
    for d in user_docs:
        title = getattr(d, "title", "") or "Internal Document"
        content = getattr(d, "content", "") or ""
        url = getattr(d, "url", "") or ""
        source_id = getattr(d, "id", "") or f"doc_{idx}"
        item = {
            "index": idx,
            "id": source_id,
            "type": "Internal Document",
            "title": title,
            "url": url,
            "snippet": content[:350],
            "text": f"{title}. {content}",
            "meta": "User Knowledge Base",
        }
        all_sources.append(item)
        registry[str(idx)] = item
        if source_id:
            registry[source_id] = item
        idx += 1

    return all_sources, registry


class BaseAgent:
    def __init__(self, name: str):
        self.name = name
        self.llm = self._init_llm()

    def _init_llm(self):
        try:
            if settings.DEFAULT_MODEL_PROVIDER == "openai" and settings.OPENAI_API_KEY and ChatOpenAI:
                return ChatOpenAI(
                    model=settings.DEFAULT_MODEL_NAME or "gpt-4o-mini",
                    api_key=settings.OPENAI_API_KEY,
                    temperature=0.2,
                )
            elif settings.DEFAULT_MODEL_PROVIDER == "groq" and settings.GROQ_API_KEY and ChatGroq:
                return ChatGroq(
                    model="llama-3.3-70b-versatile",
                    api_key=settings.GROQ_API_KEY,
                    temperature=0.2,
                )
            elif settings.DEFAULT_MODEL_PROVIDER == "gemini" and settings.GEMINI_API_KEY and ChatGoogleGenerativeAI:
                # Use high-quota, reliable gemini-3.5-flash-lite
                model_name = settings.DEFAULT_MODEL_NAME or "gemini-3.5-flash-lite"
                if model_name in ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-1.5-flash"]:
                    model_name = "gemini-3.5-flash-lite"
                return ChatGoogleGenerativeAI(
                    model=model_name,
                    google_api_key=settings.GEMINI_API_KEY,
                    temperature=0.3,
                    max_retries=1,
                    request_timeout=20,
                )
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Could not initialize LLM provider '{settings.DEFAULT_MODEL_PROVIDER}': {e}. Falling back to rule-based generation.")
        return None

    def extract_text(self, response: Any) -> str:
        return extract_llm_text(response)

    def log_execution(
        self,
        status: str,
        start_time: float,
        reasoning: str,
        details: dict[str, Any] | None = None
    ) -> AgentExecutionLog:
        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        log = AgentExecutionLog(
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            agent_name=self.name,
            status=status,
            execution_time_ms=elapsed_ms,
            decision_reasoning=reasoning,
            details=details or {}
        )
        logger.info(f"[{self.name}] {status} in {elapsed_ms}ms - {reasoning}")
        return log
