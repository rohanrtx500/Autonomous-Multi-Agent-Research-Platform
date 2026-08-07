import time
from typing import Dict, Any, Optional
from loguru import logger
from app.core.config import settings
from app.schemas.evaluation import AgentExecutionLog

try:
    from langchain_openai import ChatOpenAI
    from langchain_groq import ChatGroq
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatOpenAI = None
    ChatGroq = None
    ChatGoogleGenerativeAI = None


class BaseAgent:
    def __init__(self, name: str):
        self.name = name
        self.llm = self._init_llm()

    def _init_llm(self):
        try:
            if settings.DEFAULT_MODEL_PROVIDER == "openai" and settings.OPENAI_API_KEY and ChatOpenAI:
                return ChatOpenAI(
                    model=settings.DEFAULT_MODEL_NAME,
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
                return ChatGoogleGenerativeAI(
                    model=settings.DEFAULT_MODEL_NAME or "gemini-2.0-flash",
                    google_api_key=settings.GEMINI_API_KEY,
                    temperature=0.2,
                    max_retries=1,
                    request_timeout=8,
                )
        except Exception as e:
            logger.warning(f"Could not initialize LLM provider '{settings.DEFAULT_MODEL_PROVIDER}': {e}. Falling back to rule-based generation.")
        return None

    def log_execution(
        self,
        status: str,
        start_time: float,
        reasoning: str,
        details: Optional[Dict[str, Any]] = None
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
