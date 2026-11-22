from app.schemas.state import ResearchState


def should_continue_or_refine(state: ResearchState) -> str:
    """
    Pure conditional edge function that determines whether the report meets quality standards
    or should route back to the Writer node. Does NOT mutate state.
    """
    iteration = state.get("iteration_count", 0)
    max_iters = state.get("max_iterations", 2)
    metrics = state.get("evaluation_metrics")

    if iteration >= max_iters:
        return "end"

    if metrics and getattr(metrics, "is_acceptable", False):
        return "end"

    return "refine"
