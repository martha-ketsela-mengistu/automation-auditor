from langgraph.graph import StateGraph, START, END
from src.state import AgentState
from src.nodes.detectives import repo_investigator_node, doc_analyst_node, vision_inspector_node
from src.nodes.aggregators import evidence_aggregator_node
from src.nodes.judges import prosecutor_node, defense_node, tech_lead_node
from src.nodes.justice import chief_justice_node

def create_graph():
    """
    Creates the Automaton Auditor StateGraph.
    Full architecture with parallel Detectives and parallel Judges.
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

    # --- Graph Wiring ---

    # 1. Detective Layer: Parallel Fan-Out
    builder.add_edge(START, "repo_investigator")
    builder.add_edge(START, "doc_analyst")
    builder.add_edge(START, "vision_inspector")

    # 2. Detective Layer: Parallel Fan-In (Aggregation)
    builder.add_edge("repo_investigator", "evidence_aggregator")
    builder.add_edge("doc_analyst", "evidence_aggregator")
    builder.add_edge("vision_inspector", "evidence_aggregator")

    # 3. Judicial Layer: Parallel Fan-Out
    # After evidence is aggregated, all judges analyze it simultaneously
    builder.add_edge("evidence_aggregator", "prosecutor")
    builder.add_edge("evidence_aggregator", "defense")
    builder.add_edge("evidence_aggregator", "tech_lead")

    # 4. Judicial Layer: Parallel Fan-In (Chief Justice Synthesis)
    builder.add_edge("prosecutor", "chief_justice")
    builder.add_edge("defense", "chief_justice")
    builder.add_edge("tech_lead", "chief_justice")

    # 5. Final Exit
    builder.add_edge("chief_justice", END)

    return builder.compile()

# Compile the graph for export/usage
audit_graph = create_graph()
