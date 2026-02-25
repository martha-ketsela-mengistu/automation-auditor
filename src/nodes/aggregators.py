from src.state import AgentState


def evidence_aggregator_node(state: AgentState) -> dict:
    """
    EvidenceAggregator (Fan-In Node):
    Synchronizes results from the parallel Detective layer.
    Validates that forensic evidence has been collected across all targeted dimensions.
    """
    evidences = state.get("evidences", {})
    
    # Log summary for tracing
    summary = {dim: len(evs) for dim, evs in evidences.items()}
    print(f"--- Evidence Aggregation Summary ---")
    for dim, count in summary.items():
        print(f"  {dim}: {count} artifacts found")
    
    # Check if we have minimum required evidence (Repo + Doc)
    has_repo = "git_forensic_analysis" in evidences
    has_doc = "theoretical_depth" in evidences
    
    if not (has_repo and has_doc):
        print("Warning: Missing core detective evidence (Repo or Doc analysis failed).")

    # This node primarily serves as a synchronization barrier (Fan-In)
    # in LangGraph. The state is already merged by the reducers.
    return {}
