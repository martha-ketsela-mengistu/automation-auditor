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

        print("\n--- Audit Swarm Execution Finished ---")

    except Exception as e:
        print(f"Critical error during swarm execution: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
