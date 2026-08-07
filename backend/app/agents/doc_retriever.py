import time
from typing import Dict, Any
from app.agents.base import BaseAgent
from app.infrastructure.vector_store import VectorStoreService
from app.schemas.state import ResearchState


class DocRetrievalAgent(BaseAgent):
    def __init__(self, vector_store: VectorStoreService = None):
        super().__init__(name="Document Retrieval Agent")
        self.vector_store = vector_store or VectorStoreService()

    def run(self, state: ResearchState) -> Dict[str, Any]:
        start_time = time.time()
        objective = state.get("objective", "")

        docs = self.vector_store.hybrid_search(query=objective, top_k=5)

        log = self.log_execution(
            status="completed",
            start_time=start_time,
            reasoning=f"Retrieved {len(docs)} internal vector documents using hybrid dense + BM25 search.",
            details={"doc_count": len(docs)}
        )

        return {
            "retrieved_user_docs": docs,
            "agent_logs": [log]
        }
