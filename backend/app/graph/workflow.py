from langgraph.graph import StateGraph, START, END
from app.schemas.state import ResearchState
from app.graph.nodes import (
    planner_node,
    paper_retrieval_node,
    web_retrieval_node,
    github_retrieval_node,
    doc_retrieval_node,
    synthesizer_node,
    comparator_node,
    gap_node,
    exp_planner_node,
    writer_node,
    critic_node,
    citation_node,
    eval_node,
)
from app.graph.edges import should_continue_or_refine


def create_research_graph():
    builder = StateGraph(ResearchState)

    # Add Nodes
    builder.add_node("planner", planner_node)
    builder.add_node("paper_agent", paper_retrieval_node)
    builder.add_node("web_agent", web_retrieval_node)
    builder.add_node("github_agent", github_retrieval_node)
    builder.add_node("doc_agent", doc_retrieval_node)
    builder.add_node("synthesizer", synthesizer_node)
    builder.add_node("comparator", comparator_node)
    builder.add_node("gap_analyzer", gap_node)
    builder.add_node("experiment_planner", exp_planner_node)
    builder.add_node("writer", writer_node)
    builder.add_node("critic", critic_node)
    builder.add_node("citation_verifier", citation_node)
    builder.add_node("evaluator", eval_node)

    # Workflow Connections
    builder.add_edge(START, "planner")

    # Parallel Research Fan-out from Planner
    builder.add_edge("planner", "paper_agent")
    builder.add_edge("planner", "web_agent")
    builder.add_edge("planner", "github_agent")
    builder.add_edge("planner", "doc_agent")

    # Fan-in to Knowledge Synthesizer
    builder.add_edge("paper_agent", "synthesizer")
    builder.add_edge("web_agent", "synthesizer")
    builder.add_edge("github_agent", "synthesizer")
    builder.add_edge("doc_agent", "synthesizer")

    # Sequential Reasoning & Comparison Pipeline
    builder.add_edge("synthesizer", "comparator")
    builder.add_edge("comparator", "gap_analyzer")
    builder.add_edge("gap_analyzer", "experiment_planner")
    builder.add_edge("experiment_planner", "writer")
    builder.add_edge("writer", "critic")
    builder.add_edge("critic", "citation_verifier")
    builder.add_edge("citation_verifier", "evaluator")

    # Conditional Routing Edge
    builder.add_conditional_edges(
        "evaluator",
        should_continue_or_refine,
        {
            "end": END,
            "refine": "writer"
        }
    )

    return builder.compile()


research_graph = create_research_graph()
