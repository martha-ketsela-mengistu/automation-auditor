from src.state import AgentState


def evidence_aggregator_node(state: AgentState) -> dict:
    """
    EvidenceAggregator (Fan-In Node):
    Synchronizes results from the parallel Detective layer.
    Validates that forensic evidence has been collected across all targeted dimensions.
    """
    evidences = state.get("evidences", {})
    
    # --- Report Accuracy Cross-Reference Forensic Step ---
    repo_files_ev = evidences.get("_repo_file_list", [])
    report_acc_ev = evidences.get("report_accuracy", [])
    
    if repo_files_ev and report_acc_ev:
        # Extract files from internal evidence
        repo_files = set(repo_files_ev[0].content.split(","))
        
        # Extract claimed paths from doc analyst evidence
        content_str = report_acc_ev[0].content
        claimed_paths = [p.strip() for p in content_str.split(",")]
        
        verified = [p for p in claimed_paths if p in repo_files or any(rf.endswith(p) for rf in repo_files)]
        hallucinated = [p for p in claimed_paths if p not in verified and p.strip()]
        
        # Add detailed forensic results to report_accuracy
        from src.state import Evidence
        evidences["report_accuracy"].append(
            Evidence(
                goal="Identify Verified Paths (Reality Check)",
                found=len(verified) > 0,
                content=", ".join(verified) if verified else "None",
                location="Cross-Reference",
                rationale=f"Confirmed {len(verified)} file paths mentioned in the report actually exist in the repo.",
                confidence=1.0
            )
        )
        evidences["report_accuracy"].append(
            Evidence(
                goal="Identify Hallucinated Paths (Hallucination Check)",
                found=len(hallucinated) > 0,
                content=", ".join(hallucinated) if hallucinated else "None",
                location="Cross-Reference",
                rationale=f"Found {len(hallucinated)} paths mentioned in the report that do NOT exist in the repo.",
                confidence=1.0
            )
        )
        
    # Clean up internal keys
    if "_repo_file_list" in evidences:
        del evidences["_repo_file_list"]

    # Log summary for tracing
    summary = {dim: len(evs) for dim, evs in evidences.items()}
    print(f"--- Evidence Aggregation Summary ---")
    for dim, count in summary.items():
        print(f"  {dim}: {count} artifacts found")
    
    return {"evidences": evidences}
