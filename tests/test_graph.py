import os
import pprint
from src.graph import audit_graph

def run_test_audit():
    """
    Runs a test audit using the partial StateGraph.
    Verifies that detectives execute and aggregate evidence correctly.
    """
    print("--- Starting Partial Graph Test ---")
    
    # Use the current project as the target for the audit
    current_repo_url = "https://github.com/martha-ketsela-mengistu/automation-auditor" # Placeholder/Real URL
    sample_report = "reports/interim_report.md"
    
    if not os.path.exists(sample_report):
        print(f"Error: {sample_report} not found. Please run the doc tools test first.")
        return

    # Initial State
    initial_state = {
        "repo_url": current_repo_url,
        "pdf_path": sample_report,
        "evidences": {},
        "opinions": [],
        "rubric_dimensions": [] # Placeholder
    }

    # Execute the Graph
    print(f"Executing graph for repo: {current_repo_url}")
    try:
        final_state = audit_graph.invoke(initial_state)
        
        print("\n--- Graph Execution Complete ---")
        
        # Verify Evidences
        evidences = final_state.get("evidences", {})
        print(f"\nCollected Evidence Categories: {list(evidences.keys())}")
        
        for category, items in evidences.items():
            print(f"\nCategory: {category}")
            for i, evidence in enumerate(items):
                print(f"  [{i}] Goal: {evidence.goal}")
                print(f"      Confidence: {evidence.confidence}")
                print(f"      Location: {evidence.location}")
        
        print("\nTest Status: SUCCESS")
        
    except Exception as e:
        print(f"\nGraph execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Ensure reports/interim_report.md exists (created in previous step)
    if not os.path.exists("reports"):
        os.makedirs("reports")
    
    run_test_audit()
