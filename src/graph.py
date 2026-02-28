from typing import List
from langgraph.graph import StateGraph, START, END
from src.state import AgentState
from src.nodes.detectives import repo_investigator_node, doc_analyst_node, vision_inspector_node
from src.nodes.aggregators import evidence_aggregator_node
from src.nodes.judges import prosecutor_node, defense_node, tech_lead_node
from src.nodes.justice import chief_justice_node

def error_node(state: AgentState) -> dict:
    """
    Error Node:
    Handles cases where critical evidence is missing or a node failed.
    """
    print(f"--- Critical Error: {state.get('error', 'Unknown failure')} ---")
    # Return a dummy report or update state to indicate failure
    return {}

def router(state: AgentState) -> List[str]:
    """
    Router:
    Decides whether to proceed to Judges (parallel) or fail based on evidence quality.
    """
    evidences = state.get("evidences", {})
    # Check if repo was cloned successfully
    git_ev = evidences.get("git_forensic_analysis", [])
    if not git_ev or not git_ev[0].found:
        return ["error_handling"]
    return ["prosecutor", "defense", "tech_lead"]

def create_graph():
    """
    Creates the Automaton Auditor StateGraph.
    Full architecture with parallel Detectives, parallel Judges, and Conditional Edges.
    """
    builder = StateGraph(AgentState)

    # --- Node Registration ---
    builder.add_node("repo_investigator", repo_investigator_node)
    builder.add_node("doc_analyst", doc_analyst_node)
    builder.add_node("vision_inspector", vision_inspector_node)
    builder.add_node("evidence_aggregator", evidence_aggregator_node)
    
    builder.add_node("prosecutor", prosecutor_node)
    builder.add_node("defense", defense_node)
    builder.add_node("tech_lead", tech_lead_node)
    builder.add_node("chief_justice", chief_justice_node)
    builder.add_node("error_handling", error_node)

    # --- Graph Wiring ---

    # 1. Detective Layer: Parallel Fan-Out
    builder.add_edge(START, "repo_investigator")
    builder.add_edge(START, "doc_analyst")
    builder.add_edge(START, "vision_inspector")

    # 2. Detective Layer: Parallel Fan-In (Aggregation)
    builder.add_edge("repo_investigator", "evidence_aggregator")
    builder.add_edge("doc_analyst", "evidence_aggregator")
    builder.add_edge("vision_inspector", "evidence_aggregator")

    # 3. Conditional Strategic Edge
    # Router returns the next node(s) to visit. 
    # Can return a list for parallel fan-out.
    builder.add_conditional_edges(
        "evidence_aggregator",
        router
    )

    # 4. Judicial Layer: Parallel Fan-In (Chief Justice Synthesis)
    builder.add_edge("prosecutor", "chief_justice")
    builder.add_edge("defense", "chief_justice")
    builder.add_edge("tech_lead", "chief_justice")

    # 5. Final Exit
    builder.add_edge("chief_justice", END)
    builder.add_edge("error_handling", END)

    return builder.compile()

# Compile the graph for export/usage
audit_graph = create_graph()
