import time
from typing import Dict, Any
from app.agents.base import BaseAgent
from app.schemas.research import ResearchSubTask
from app.schemas.state import ResearchState


class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Planner Agent")

    def run(self, state: ResearchState) -> Dict[str, Any]:
        start_time = time.time()
        objective = state.get("objective", "General AI Research")

        tasks = [
            ResearchSubTask(
                id="task_1",
                title="Academic Literature Retrieval",
                description=f"Search arXiv and Semantic Scholar papers related to {objective}.",
                assigned_agent="Paper Retrieval Agent",
                status="pending"
            ),
            ResearchSubTask(
                id="task_2",
                title="Web & Documentation Search",
                description=f"Search Tavily for recent developments, benchmarks, and blogs on {objective}.",
                assigned_agent="Web Research Agent",
                status="pending"
            ),
            ResearchSubTask(
                id="task_3",
                title="GitHub Open-Source Repositories Search",
                description=f"Search GitHub for popular repositories and implementations of {objective}.",
                assigned_agent="GitHub Research Agent",
                status="pending"
            ),
            ResearchSubTask(
                id="task_4",
                title="Internal Document Knowledge Query",
                description=f"Query local vector store knowledge base for context on {objective}.",
                assigned_agent="Document Retrieval Agent",
                status="pending"
            ),
        ]

        log = self.log_execution(
            status="completed",
            start_time=start_time,
            reasoning=f"Decomposed research objective '{objective}' into {len(tasks)} parallel research sub-tasks.",
            details={"sub_task_count": len(tasks)}
        )

        return {
            "sub_tasks": tasks,
            "status": "retrieving",
            "agent_logs": [log]
        }
