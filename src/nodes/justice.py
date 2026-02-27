import json
import os
import statistics
from typing import List, Dict, Any
from src.state import AgentState, JudicialOpinion, CriterionResult, AuditReport, Evidence

# Load rubric for metadata
RUBRIC_PATH = os.path.join(os.getcwd(), "rubric.json")
with open(RUBRIC_PATH, "r") as f:
    RUBRIC_DATA = json.load(f)

def chief_justice_node(state: AgentState) -> dict:
    """
    Chief Justice (Synthesis Node):
    Collects opinions from all judges and renders a final verdict using deterministic rules.
    """
    print("--- Chief Justice is rendering the final verdict ---")
    
    opinions = state.get("opinions", [])
    evidences = state.get("evidences", {})
    
    # Group opinions by criterion
    criterion_opinions: Dict[str, List[JudicialOpinion]] = {}
    for op in opinions:
        if op.criterion_id not in criterion_opinions:
            criterion_opinions[op.criterion_id] = []
        criterion_opinions[op.criterion_id].append(op)
    
    final_criteria_results = []
    
    for dimension in RUBRIC_DATA["dimensions"]:
        c_id = dimension["id"]
        c_name = dimension["name"]
        ops = criterion_opinions.get(c_id, [])
        evidence_list = evidences.get(c_id, [])
        
        if not ops:
            continue
            
        # 1. Base Score (Average)
        scores = [op.score for op in ops]
        avg_score = sum(scores) / len(scores)
        
        # 2. Rule: Tech Lead Weight (Architecture Supremacy)
        if c_id == "graph_orchestration":
            tech_lead_op = next((op for op in ops if op.judge == "TechLead"), None)
            if tech_lead_op:
                # Tech lead has double weight for architecture
                weighted_scores = scores + [tech_lead_op.score]
                avg_score = sum(weighted_scores) / len(weighted_scores)

        # 3. Rule: Fact Supremacy (Evidence Check)
        any_missing = any(not e.found for e in evidence_list)
        if any_missing:
            # If evidence is missing, high defense scores are penalized
            defense_op = next((op for op in ops if op.judge == "Defense"), None)
            if defense_op and defense_op.score > 3:
                avg_score -= 0.5 # Penalty for hallucinated intent
        
        # 4. Rule: Security Override
        if c_id == "safe_tool_engineering":
            prosecutor_op = next((op for op in ops if op.judge == "Prosecutor"), None)
            if prosecutor_op and prosecutor_op.score == 1:
                # Confirmed vulnerability caps score at 3
                avg_score = min(avg_score, 3.0)

        final_score = round(max(1, min(5, avg_score)))

        # 5. Dissent Identification
        dissent = None
        if len(scores) > 1:
            variance = max(scores) - min(scores)
            if variance > 2:
                p_op = next((op for op in ops if op.judge == "Prosecutor"), None)
                d_op = next((op for op in ops if op.judge == "Defense"), None)
                dissent = f"Major disagreement: Prosecutor ({p_op.score if p_op else 'N/A'}) vs Defense ({d_op.score if d_op else 'N/A'}). "
                dissent += "The Prosecutor found critical gaps that the Defense considered workarounds."

        # 6. Construct Criterion Result
        result = CriterionResult(
            dimension_id=c_id,
            dimension_name=c_name,
            final_score=final_score,
            judge_opinions=ops,
            dissent_summary=dissent,
            remediation=f"Review the Prosecutor's gaps and Defense's workarounds for {c_name}. Focus on specific implementation markers cited in the evidence."
        )
        final_criteria_results.append(result)

    # Calculate Overall Score
    total_score = sum(r.final_score for r in final_criteria_results) / len(final_criteria_results)
    
    # Final Report
    report = AuditReport(
        repo_url=state["repo_url"],
        executive_summary=f"Audit completed for {state['repo_url']}. Parallel orchestration and forensic markers were analyzed.",
        overall_score=round(total_score, 2),
        criteria=final_criteria_results,
        remediation_plan="Review critical dissents and address the lowest scoring dimensions first."
    )

    # --- Save Report to audit/AuditReport.md ---
    os.makedirs("audit", exist_ok=True)
    report_path = os.path.join("audit", "AuditReport.md")
    
    with open(report_path, "w", encoding="utf-8") as md_file:
        md_file.write(f"# Automaton Auditor: Final Audit Report\n\n")
        md_file.write(f"**Target Repo:** {report.repo_url}\n")
        md_file.write(f"**Overall Score:** {report.overall_score}/5.0\n\n")
        md_file.write(f"## Executive Summary\n{report.executive_summary}\n\n")
        
        md_file.write(f"## Dimension Breakdown\n")
        for res in report.criteria:
            md_file.write(f"### {res.dimension_name}\n")
            md_file.write(f"- **Score:** {res.final_score}/5\n")
            if res.dissent_summary:
                md_file.write(f"- **Dissent:** {res.dissent_summary}\n")
            md_file.write(f"- **Remediation:** {res.remediation}\n\n")
            
            md_file.write("#### Judicial Opinions\n")
            for op in res.judge_opinions:
                md_file.write(f"- **{op.judge}:** (Score: {op.score}) {op.argument}\n")
            md_file.write("\n")
            
        md_file.write(f"## Remediation Plan\n{report.remediation_plan}\n")

    print(f"--- Final report saved to {report_path} ---")

    return {"final_report": report}
