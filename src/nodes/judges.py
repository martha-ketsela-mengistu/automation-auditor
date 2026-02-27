import json
import os
from typing import List, Dict, Any
# from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from src.state import AgentState, JudicialOpinion, Evidence

# Load rubric to know what we are judging
RUBRIC_PATH = os.path.join(os.getcwd(), "rubric.json")
with open(RUBRIC_PATH, "r") as f:
    RUBRIC = json.load(f)

# Initialize LLM (assuming OPENAI_API_KEY is in environment)
# In a production setting, this would be configurable
# llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

llm = ChatOllama(
    model="llama3.1", 
    base_url="http://192.168.1.9:11434", 
    temperature=0
)

def get_judicial_opinion(
    judge_persona: str, 
    persona_name: str, 
    criterion: Dict[str, Any], 
    evidence_list: List[Evidence]
) -> JudicialOpinion:
    """
    Helper function to invoke the LLM for a specific judge and criterion.
    """
    structured_llm = llm.with_structured_output(JudicialOpinion)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"{judge_persona}\n\nYou must evaluate the provided evidence against the specific rubric criterion. "
                   "Your output must be a structured JudicialOpinion."),
        ("human", "Rubric Criterion: {criterion_name}\n"
                  "Success Pattern: {success_pattern}\n"
                  "Failure Pattern: {failure_pattern}\n\n"
                  "Forensic Evidence Collected:\n{evidence_text}\n\n"
                  "Provide your score (1-5), your detailed argument, and cite the specific evidence used.")
    ])
    
    # Format evidence for the prompt
    evidence_text = ""
    for idx, e in enumerate(evidence_list):
        status = "FOUND" if e.found else "NOT FOUND"
        evidence_text += f"Evidence [{idx}] ({e.location}): {e.rationale}\nContent snippet: {e.content}\n\n"
    
    if not evidence_text:
        evidence_text = "No specific forensic evidence was collected for this criterion."

    # Invoke
    chain = prompt | structured_llm
    opinion = chain.invoke({
        "criterion_name": criterion["name"],
        "success_pattern": criterion["success_pattern"],
        "failure_pattern": criterion["failure_pattern"],
        "evidence_text": evidence_text
    })
    
    # Ensure metadata is correct
    opinion.judge = persona_name
    opinion.criterion_id = criterion["id"]
    return opinion

def prosecutor_node(state: AgentState) -> Dict[str, Any]:
    """
    Prosecutor: Cynical, detail-oriented, looks for missing pieces.
    """
    print("--- Prosecutor is scrutinizing the evidence ---")
    persona = ("You are a cynical, detail-oriented prosecutor. Your job is to "
               "assume the developer cut corners. Scrutinize the Evidence for absence. "
               "If a file exists but is incomplete, argue for a low score. "
               "Your core question: 'What is missing?'.")
    
    new_opinions = []
    evidences = state.get("evidences", {})
    
    for dim in RUBRIC["dimensions"]:
        criterion_id = dim["id"]
        evidence_list = evidences.get(criterion_id, [])
        opinion = get_judicial_opinion(persona, "Prosecutor", dim, evidence_list)
        new_opinions.append(opinion)
        
    return {"opinions": new_opinions}

def defense_node(state: AgentState) -> Dict[str, Any]:
    """
    Defense: Empathetic, assumes good intent, highlights clever workarounds.
    """
    print("--- Defense is building the case for the developer ---")
    persona = ("You are an empathetic defense attorney. Your job is to assume "
               "good intent and look for the 'spirit of the law.' Highlight clever workarounds and "
               "effort. If a component is partially implemented, argue for partial credit. "
               "Your core question: 'What was attempted, and what can be learned from it?'.")
    
    new_opinions = []
    evidences = state.get("evidences", {})
    
    for dim in RUBRIC["dimensions"]:
        criterion_id = dim["id"]
        evidence_list = evidences.get(criterion_id, [])
        opinion = get_judicial_opinion(persona, "Defense", dim, evidence_list)
        new_opinions.append(opinion)
        
    return {"opinions": new_opinions}

def tech_lead_node(state: AgentState) -> Dict[str, Any]:
    """
    Tech Lead: Pragmatic, cares about maintainability and architecture. Tie-breaker.
    """
    print("--- Tech Lead is evaluating architectural soundness ---")
    persona = ("You are a pragmatic Tech Lead. You don't care about intent "
               "or cynicism. You only care about the artifacts. Is the code maintainable? "
               "Does the architecture actually solve the problem? You are the tie-breaker.")
    
    new_opinions = []
    evidences = state.get("evidences", {})
    
    for dim in RUBRIC["dimensions"]:
        criterion_id = dim["id"]
        evidence_list = evidences.get(criterion_id, [])
        opinion = get_judicial_opinion(persona, "TechLead", dim, evidence_list)
        new_opinions.append(opinion)
        
    return {"opinions": new_opinions}
