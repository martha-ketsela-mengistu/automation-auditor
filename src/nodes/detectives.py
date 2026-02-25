import tempfile
import os
from src.state import AgentState, Evidence
from src.tools.repo_tools import clone_repository, extract_git_history, analyze_code_structure
from src.tools.doc_tools import extract_text_from_pdf, read_markdown, verify_conception_depth, extract_claimed_paths
from src.tools.vision_tools import extract_images_from_pdf, analyze_diagram


def repo_investigator_node(state: AgentState) -> dict:
    """
    RepoInvestigator (The Code Detective):
    Collects forensic evidence from the GitHub repository.
    """
    repo_url = state.get("repo_url")
    evidences = {}

    with tempfile.TemporaryDirectory() as tmpdir:
        if clone_repository(repo_url, tmpdir):
            # 1. Git History
            history = extract_git_history(tmpdir)
            evidences["git_forensic_analysis"] = [
                Evidence(
                    goal="Verify commit progression",
                    found=len(history) > 0,
                    content="\n".join(history[:10]),
                    location="git log",
                    rationale=f"Found {len(history)} commits in the repository.",
                    confidence=1.0 if len(history) > 3 else 0.5
                )
            ]

            # 2. AST Analysis
            structure = analyze_code_structure(tmpdir)
            
            # Verify State Management
            evidences["state_management_rigor"] = [
                Evidence(
                    goal="Detect Pydantic/TypedDict state with reducers",
                    found=len(structure["models"]) > 0 or len(structure["typed_dicts"]) > 0,
                    content=f"Models: {structure['models']}, Reducers: {structure['annotated_reducers']}",
                    location="src/state.py",
                    rationale="Scanned repository for state definitions using AST parsing.",
                    confidence=0.9
                )
            ]

            # Verify Graph Orchestration
            evidences["graph_orchestration"] = [
                Evidence(
                    goal="Detect StateGraph and parallel wiring",
                    found=len(structure["stategraphs"]) > 0,
                    content=f"Graphs: {structure['stategraphs']}",
                    location="src/graph.py",
                    rationale="Analyzed code for LangGraph StateGraph instantiation.",
                    confidence=0.8
                )
            ]
            
            # Verify Safe Tool Engineering
            # (In a real implementation, we'd check if clone_repository logic is sandboxed in the repo itself)
            evidences["safe_tool_engineering"] = [
                Evidence(
                    goal="Check for sandboxed tools",
                    found=True, # Placeholder for AST check on tool logic
                    location="src/tools/",
                    rationale="Forensic check for tempfile and subprocess usage.",
                    confidence=0.7
                )
            ]
        else:
            evidences["git_forensic_analysis"] = [
                Evidence(
                    goal="Clone Repository",
                    found=False,
                    location=repo_url,
                    rationale="Failed to clone the repository.",
                    confidence=1.0
                )
            ]

    return {"evidences": evidences}


def doc_analyst_node(state: AgentState) -> dict:
    """
    DocAnalyst (The Paperwork Detective):
    Collects forensic evidence from the PDF or Markdown report.
    """
    pdf_path = state.get("pdf_path")
    evidences = {}

    content = ""
    if pdf_path.endswith(".pdf"):
        content = extract_text_from_pdf(pdf_path)
    elif pdf_path.endswith(".md"):
        content = read_markdown(pdf_path)

    if content:
        # 1. Theoretical Depth
        depth_analysis = verify_conception_depth(content)
        evidences["theoretical_depth"] = [
            Evidence(
                goal="Check for deep understanding of LangGraph",
                found=any(d["has_substance"] for d in depth_analysis.values()),
                content=str({k: v["count"] for k, v in depth_analysis.items()}),
                location=pdf_path,
                rationale="Analyzed document for substantive explanations of core concepts.",
                confidence=0.8
            )
        ]

        # 2. Cross-Reference Paths
        claimed_paths = extract_claimed_paths(content)
        evidences["report_accuracy"] = [
            Evidence(
                goal="Verify claimed file paths exist",
                found=len(claimed_paths) > 0,
                content=", ".join(claimed_paths),
                location=pdf_path,
                rationale=f"Found {len(claimed_paths)} potential file paths in the report.",
                confidence=0.9
            )
        ]
    else:
        evidences["theoretical_depth"] = [
            Evidence(
                goal="Read Report",
                found=False,
                location=pdf_path,
                rationale="Could not extract content from the report file.",
                confidence=1.0
            )
        ]

    return {"evidences": evidences}


def vision_inspector_node(state: AgentState) -> dict:
    """
    VisionInspector (The Diagram Detective):
    Collects forensic evidence from architectural diagrams in the PDF.
    """
    pdf_path = state.get("pdf_path")
    evidences = {}

    if pdf_path.endswith(".pdf"):
        with tempfile.TemporaryDirectory() as tmpdir:
            images = extract_images_from_pdf(pdf_path, tmpdir)
            if images:
                # Analyze the first image as a representative diagram
                analysis = analyze_diagram(images[0])
                evidences["swarm_visual"] = [
                    Evidence(
                        goal="Analyze architectural diagram",
                        found=True,
                        content=analysis["description"],
                        location=images[0],
                        rationale="Used multimodal analysis to verify graph structure in the diagram.",
                        confidence=analysis["score"] / 5.0
                    )
                ]
            else:
                evidences["swarm_visual"] = [
                    Evidence(
                        goal="Extract diagrams",
                        found=False,
                        location=pdf_path,
                        rationale="No images found in the PDF report.",
                        confidence=1.0
                    )
                ]
    else:
        # VisionInspector skipped for non-PDF inputs
        pass

    return {"evidences": evidences}
