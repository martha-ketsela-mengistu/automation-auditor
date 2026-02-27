from dotenv import load_dotenv
load_dotenv()

import argparse
import sys
from src.graph import audit_graph


def main():
    parser = argparse.ArgumentParser(
        description="Automaton Auditor: Deep Multi-Agent Governance System"
    )
    parser.add_argument(
        "--repo-url", 
        required=True, 
        help="The GitHub Repository URL to audit"
    )
    parser.add_argument(
        "--pdf-path", 
        required=True, 
        help="Path to the architectural PDF/Markdown report"
    )

    args = parser.parse_args()

    print(f"--- Launching Automaton Auditor Swarm ---")
    print(f"Target Repo: {args.repo_url}")
    print(f"Report Path: {args.pdf_path}\n")

    # Initial Agent State
    initial_state = {
        "repo_url": args.repo_url,
        "pdf_path": args.pdf_path,
        "evidences": {},
        "opinions": [],
        "rubric_dimensions": []  # Placeholder for Phase 2
    }

    try:
        # Execute the Graph
        final_state = audit_graph.invoke(initial_state)

        print("\n=== AUDIT FORENSIC SUMMARY ===")
        evidences = final_state.get("evidences", {})
        
        if not evidences:
            print("No forensic evidence collected.")
            return

        for category, items in evidences.items():
            print(f"\n[Artifact: {category}]")
            for evidence in items:
                status = "✅" if evidence.found else "❌"
                print(f"  {status} Requirement: {evidence.goal}")
                print(f"    Confidence: {evidence.confidence:.2f}")
                print(f"    Rationale: {evidence.rationale}")
                if evidence.location:
                    print(f"    Source: {evidence.location}")

        # Final Judicial Verdict
        report = final_state.get("final_report")
        if report:
            print("\n" + "="*40)
            print("         FINAL JUDICIAL VERDICT         ")
            print("="*40)
            print(f"OVERALL SCORE: {report.overall_score}/5.0")
            print(f"EXECUTIVE SUMMARY: {report.executive_summary}")
            print("\nDIMENSION BREAKDOWN:")
            for crit in report.criteria:
                print(f"- {crit.dimension_name}: {crit.final_score}/5")
                if crit.dissent_summary:
                    print(f"  ⚠️ {crit.dissent_summary}")
            
            print("\nREMEDIATION PLAN:")
            print(report.remediation_plan)
            print("="*40)

        print("\n--- Audit Swarm Execution Finished ---")

    except Exception as e:
        print(f"Critical error during swarm execution: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
