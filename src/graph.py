from langgraph.graph import StateGraph, START, END
from src.state import AgentState
from src.nodes.detectives import repo_investigator_node, doc_analyst_node, vision_inspector_node
from src.nodes.aggregators import evidence_aggregator_node

def create_graph():
    """
    Creates the Automaton Auditor StateGraph.
    Phase 1: Partial implementation with parallel Detectives and Fan-In.
    """
    builder = StateGraph(AgentState)

    # Add Detective Nodes
    builder.add_node("repo_investigator", repo_investigator_node)
    builder.add_node("doc_analyst", doc_analyst_node)
    builder.add_node("vision_inspector", vision_inspector_node)
    
    # Add Aggregator Node
    builder.add_node("evidence_aggregator", evidence_aggregator_node)

    # --- Graph Wiring ---

    # 1. Parallel Fan-Out from START to all Detectives
    builder.add_edge(START, "repo_investigator")
    builder.add_edge(START, "doc_analyst")
    builder.add_edge(START, "vision_inspector")

    # 2. Parallel Fan-In from Detectives to Aggregator
    builder.add_edge("repo_investigator", "evidence_aggregator")
    builder.add_edge("doc_analyst", "evidence_aggregator")
    builder.add_edge("vision_inspector", "evidence_aggregator")

    # 3. Temporary END for partial graph testing
    builder.add_edge("evidence_aggregator", END)

    return builder.compile()

# Compile the graph for export/usage
audit_graph = create_graph()
