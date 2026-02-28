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
                    content="\n".join(history[:50]),
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
                    content=state_code[:10000], # Provide enough context for the judge
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
                    content=graph_code[:10000],
                    location="src/graph.py",
                    rationale="Extracted graph orchestration logic to verify parallel fan-out/fan-in patterns.",
                    confidence=0.8
                )
            ]
            
            # Verify Structured Output & Judicial Nuance

            judges_code = get_file_content("src/nodes/judges.py")
            evidences["structured_output_enforcement"] = [
                Evidence(
                    goal="Verify .with_structured_output() or .bind_tools() and Pydantic validation",
                    found=".with_structured_output" in judges_code or ".bind_tools" in judges_code,
                    content=judges_code[:10000],
                    location="src/nodes/judges.py",
                    rationale="Extracted judicial node logic to verify structured output enforcement.",
                    confidence=0.9
                )
            ]

            evidences["judicial_nuance"] = [
                Evidence(
                    goal="Verify distinct Prosecutor, Defense, and TechLead personas",
                    found=all(p in judges_code for p in ["Prosecutor", "Defense", "TechLead"]),
                    content=judges_code[:10000], # Capture the persona definitions
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
                    content=justice_code[:10000],
                    location="src/nodes/justice.py",
                    rationale="Extracted synthesis logic to verify deterministic governance rules.",
                    confidence=0.9
                )
            ]

            # Verify Safe Tool Engineering (Plural Evidence)
            # 1. Check Tool Implementation
            tools_code = get_file_content("src/tools/repo_tools.py")
            evidences["safe_tool_engineering"] = [
                Evidence(
                    goal="Verify subprocess usage over os.system",
                    found="subprocess.run" in tools_code and "os.system" not in tools_code,
                    content=tools_code[:5000],
                    location="src/tools/repo_tools.py",
                    rationale="Scanned tool logic for safe command execution patterns.",
                    confidence=0.9
                ),
                Evidence(
                    goal="Verify sandboxed environment (TemporaryDirectory)",
                    # Check detectives.py itself since it implements the sandbox
                    found="with tempfile.TemporaryDirectory()" in get_file_content("src/nodes/detectives.py"),
                    content=get_file_content("src/nodes/detectives.py")[:2000],
                    location="src/nodes/detectives.py",
                    rationale="Verified that forensic operations are executed within a temporary sandbox.",
                    confidence=1.0
                )
            ]

            # Collect all repo files for cross-referencing in the aggregator
            all_files = []
            for root, _, files in os.walk(tmpdir):
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root, file), tmpdir)
                    all_files.append(rel_path.replace("\\", "/"))
            
            # Internal key for aggregator sync
            evidences["_repo_file_list"] = [
                Evidence(
                    goal="Internal: Repo file list for accuracy check",
                    found=True,
                    content=",".join(all_files),
                    location="repository root",
                    rationale=f"Found {len(all_files)} files in the repository for cross-referencing.",
                    confidence=1.0
                )
            ]
        else:
            return {
                "error": f"Failed to clone repository: {repo_url}",
                "evidences": {
                    "git_forensic_analysis": [
                        Evidence(
                            goal="Clone Repository",
                            found=False,
                            location=repo_url,
                            rationale="Failed to clone the repository.",
                            confidence=1.0
                        )
                    ]
                }
            }
            
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
                all_vision_evidence = []
                for i, img_path in enumerate(images):
                    analysis = analyze_diagram(img_path)
                    
                    # 1. Classification Evidence
                    all_vision_evidence.append(
                        Evidence(
                            goal=f"Classify diagram [{i}]",
                            found=True,
                            content=analysis["diagram_type"],
                            location=img_path,
                            rationale=f"Verified if diagram {i} is a LangGraph State Machine, Sequence, or Flowchart.",
                            confidence=0.9
                        )
                    )
                    
                    # 2. Parallel Flow Evidence
                    all_vision_evidence.append(
                        Evidence(
                            goal=f"Verify parallel split in diagram [{i}]",
                            found=analysis["has_parallel_split"],
                            content=analysis["description"],
                            location=img_path,
                            rationale="Checked for START -> [Detectives] -> Aggregation -> [Judges] -> Synthesis -> END flow.",
                            confidence=0.9
                        )
                    )
                    
                    # 3. Pipeline Linearity Flag (Failure Pattern)
                    if analysis["is_linear_pipeline"]:
                        all_vision_evidence.append(
                            Evidence(
                                goal=f"Detect linear pipeline anomaly in diagram [{i}]",
                                found=True,
                                content="Misleading Architecture Visual",
                                location=img_path,
                                rationale="Diagram shows a simple linear pipeline which contradicts the parallel implementation.",
                                confidence=1.0
                            )
                        )
                
                evidences["swarm_visual"] = all_vision_evidence
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
