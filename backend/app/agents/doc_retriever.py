import time
from typing import Any

from app.agents.base import BaseAgent
from app.infrastructure.vector_store import VectorStoreService
from app.schemas.state import ResearchState


class DocRetrievalAgent(BaseAgent):
    def __init__(self, vector_store: VectorStoreService = None):
        super().__init__(name="Document Retrieval Agent")
        self.vector_store = vector_store or VectorStoreService()

    def run(self, state: ResearchState) -> dict[str, Any]:
        start_time = time.time()
        objective = state.get("objective", "")

        try:
            docs = self.vector_store.hybrid_search(query=objective, top_k=5)
            # Only keep documents with genuine relevance to this query to prevent injecting unrelated past uploads
            relevant_docs = [d for d in docs if getattr(d, "score", 0.0) >= 0.25]
        except Exception as e:  # noqa: BLE001
            relevant_docs = []
            self.log_execution("warning", start_time, f"Vector search error: {e}")

        log = self.log_execution(
            status="completed",
            start_time=start_time,
            reasoning=f"Retrieved {len(relevant_docs)} relevant internal vector documents using hybrid dense + BM25 search.",
            details={"doc_count": len(relevant_docs)}
        )

        return {
            "retrieved_user_docs": relevant_docs,
            "agent_logs": [log]
        }
