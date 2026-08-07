from app.schemas.state import ResearchState


def should_continue_or_refine(state: ResearchState) -> str:
    """
    Evaluates whether the report meets quality standards or needs a refinement loop back to Writer.
    """
    iteration = state.get("iteration_count", 0)
    max_iters = state.get("max_iterations", 2)
    metrics = state.get("evaluation_metrics")

    if iteration >= max_iters:
        return "end"

    if metrics and metrics.is_acceptable:
        return "end"

    # Increment iteration count and loop back to writer
    state["iteration_count"] = iteration + 1
    return "refine"
