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

            # 2. AST Analysis and Code Sampling
            structure = analyze_code_structure(tmpdir)
            
            # Helper to read file safely
            def get_file_content(path):
                full_path = os.path.join(tmpdir, path)
                if os.path.exists(full_path):
                    with open(full_path, "r", encoding="utf-8") as f:
                        return f.read()
                return "File not found."

            # Verify State Management (Deep Evidence)
            state_code = get_file_content("src/state.py")
            evidences["state_management_rigor"] = [
                Evidence(
                    goal="Detect Pydantic/TypedDict state with reducers",
                    found="AgentState" in state_code,
                    content=state_code[:2000], # Provide enough context for the judge
                    location="src/state.py",
                    rationale="Scanned repository and extracted the core state definition for judicial review.",
                    confidence=0.9
                )
            ]

            # Verify Graph Orchestration (Deep Evidence)
            graph_code = get_file_content("src/graph.py")
            evidences["graph_orchestration"] = [
                Evidence(
                    goal="Detect StateGraph and parallel wiring",
                    found="StateGraph" in graph_code,
                    content=graph_code[:2000],
                    location="src/graph.py",
                    rationale="Extracted graph orchestration logic to verify parallel fan-out/fan-in patterns.",
                    confidence=0.8
                )
            ]
            
            # Verify Structured Output & Judicial Nuance
            judges_code = get_file_content("src/nodes/judges.py")
            evidences["structured_output_enforcement"] = [
                Evidence(
                    goal="Verify .bind_tools() and Pydantic validation",
                    found=".bind_tools" in judges_code,
                    content=judges_code[:2000],
                    location="src/nodes/judges.py",
                    rationale="Extracted judicial node logic to verify structured output enforcement.",
                    confidence=0.9
                )
            ]
            evidences["judicial_nuance"] = [
                Evidence(
                    goal="Verify distinct Prosecutor, Defense, and TechLead personas",
                    found=all(p in judges_code for p in ["Prosecutor", "Defense", "TechLead"]),
                    content=judges_code[2000:4000], # Capture the persona definitions
                    location="src/nodes/judges.py",
                    rationale="Extracted judge personas to verify dialectical separation.",
                    confidence=0.9
                )
            ]

            # Verify Chief Justice Engine
            justice_code = get_file_content("src/nodes/justice.py")
            evidences["chief_justice_synthesis"] = [
                Evidence(
                    goal="Verify deterministic Python rules (Security, Fact Supremacy)",
                    found="min(avg_score, 3.0)" in justice_code and "avg_score -= 0.5" in justice_code,
                    content=justice_code[:2000],
                    location="src/nodes/justice.py",
                    rationale="Extracted synthesis logic to verify deterministic governance rules.",
                    confidence=0.9
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
