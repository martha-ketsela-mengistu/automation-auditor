# Feature Specification: Deep Auditor Swarm

**Feature Branch**: `001-langgraph-auditor`  
**Created**: 2026-02-25  
**Status**: Draft  
**Input**: User description: "Implement deep multi-agent governance system built on a hierarchical StateGraph orchestration designed to automate the quality assurance of AI-generated code. The architecture employs a two-layer parallel orchestration: a Detective Layer (RepoInvestigator, DocAnalyst, VisionInspector) that uses forensic tools like AST parsing and PDF ingestion to collect objective evidence, followed by a Judicial Layer (Prosecutor, Defense, Tech Lead) that analyzes that evidence through distinct dialectical lenses. All findings are synthesized by a Chief Justice node using deterministic conflict-resolution rules—such as capping scores for security vulnerabilities—resulting in a production-grade Markdown Audit Report with actionable remediation steps."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run a full audit (Priority: P1)

An auditor operator provides a Git repository URL and an architectural PDF report. The system runs Detectives in parallel to collect factual Evidence, fans-in to aggregate Evidence, runs three Judges (Prosecutor, Defense, Tech Lead) in parallel for each rubric dimension, and the Chief Justice synthesizes a final Markdown Audit Report.

Why this priority: This is the core value: automated, reproducible audits that produce actionable remediation.

Independent Test:
- Execute the system with a known sample repo + PDF. Verify the produced Markdown report validates against the `AuditReport` model and that cited file paths exist in the repository.

Acceptance Scenarios:
1. Given a valid repo URL and PDF, When the audit runs, Then a Markdown report is produced and saved under `audit/report_<repo-name>.md` and the `final_report` field in `AgentState` contains a serialized `AuditReport`.
2. Given the PDF cites `src/nodes/judges.py` but the file is missing, Then the DocAnalyst records a Hallucinated Path and the report lists it under `Report Accuracy`.

---

### User Story 2 - Run Detectives-only (Priority: P2)

An operator can run only the Detective layer to gather evidence quickly (useful for debugging or partial runs).

Why this priority: Useful for fast verification and to support re-evaluation flows triggered by the Chief Justice.

Independent Test:
- Run detectives against a repo; expect JSON evidence objects for `git_forensic_analysis`, `state_management_rigor`, and `graph_orchestration` written to disk.

Acceptance Scenarios:
1. Given a repo URL, When RepoInvestigator runs, Then it returns `Evidence` objects containing `found`, `location`, `content` (code snippet), `rationale`, and `confidence`.

---

### User Story 3 - Replay Judges for a single criterion (Priority: P3)

Operators can re-run the three Judges on a single aggregated evidence bundle for debugging and post-hoc review.

Why this priority: Enables deterministic re-evaluation required by the Chief Justice when score variance exceeds threshold.

Independent Test:
- Provide an `Evidence` bundle for one criterion and run the three Judges; verify three `JudicialOpinion` objects are generated and validated.

Acceptance Scenarios:
1. Given an evidence bundle, When Judges run, Then each returns a validated `JudicialOpinion` with `judge`, `criterion_id`, `score`, `argument`, and `cited_evidence`.

---

### Edge Cases

- What happens when the repo is very large (> 1000 files)? System should still sandbox and timeout gracefully (see FRs).  
- What if the language model returns malformed JSON? Judges must retry and escalate to deterministic fallback after N attempts.  
- VisionInspector image extraction fails (no images) — proceed without visual evidence and record absence in Evidence.

## Requirements *(mandatory)*

### Functional Requirements

+ **FR-001 (Detective Parallelism)**: The system MUST execute `RepoInvestigator`, `DocAnalyst`, and `VisionInspector` in parallel for each rubric dimension and fan-in their results to an `EvidenceAggregator` before invoking Judges. (Test: instrument traces showing parallel start times and a single aggregator invocation.)
+ **FR-002 (Typed Evidence)**: Evidence returned by Detectives MUST conform to the `Evidence` typed model/schema: `goal`, `found`, `content?`, `location`, `rationale`, `confidence`. (Test: schema validation of all detective outputs.)
+ **FR-003 (AST-based Repo Analysis)**: `RepoInvestigator` MUST perform AST parsing of source code to locate typed state definitions, `StateGraph` builder usage, and `builder.add_edge()` patterns. Regex-only checks are not acceptable. (Test: unit tests verifying AST extraction for representative code samples.)
+ **FR-004 (Sandboxed Cloning)**: Git cloning MUST occur inside a temporary isolated sandbox environment, using secure subprocess invocation with proper error handling; raw shell `git clone` into the working directory is disallowed. (Test: unit test inspects clone logic for sandboxing and captured return codes.)
+ **FR-005 (Judge Structured Output)**: Each Judge node (Prosecutor, Defense, TechLead) MUST be invoked with structured-output enforcement and produce `JudicialOpinion` objects validated against the specified schema. If a Judge returns malformed output, node must retry up to 3 times then escalate. (Test: simulate malformed model response and assert retry and fallback behavior.)
+ **FR-006 (Chief Justice Deterministic Rules)**: `ChiefJusticeNode` MUST implement deterministic conflict-resolution rules (security override, fact supremacy, functionality weight, variance re-evaluation) and output a validated `AuditReport` model and a Markdown serialization. (Test: unit tests cover each hardcoded rule.)
+ **FR-007 (Audit Report Format)**: The final output MUST be a Markdown file containing Executive Summary, Criterion Breakdown (with final score and three judge opinions per criterion), Dissent Summaries when variance > 2, and a Remediation Plan with file-level actions. (Test: rendered Markdown validated against expected sections and that referenced file paths exist or are annotated as hallucinated.)
+ **FR-008 (Observability & Tracing)**: Structured tracing metadata and observability events MUST be emitted for Detective runs, Judge deliberations, and Chief Justice synthesis. (Test: traces contain node start/stop and evidence payloads.)
+ **FR-009 (Retry and Error Handling)**: The graph MUST include conditional edges to handle node failures (e.g., Evidence missing, Node failure) and allow re-evaluation or graceful degradation. (Test: inject node error and assert controlled fallback.)
+ **FR-010 (Configurable Rubric)**: The system MUST load the rubric JSON at runtime and dispatch `forensic_instruction` to Detectives and `judicial_logic` to Judges. (Test: swap rubric file and verify different instructions are applied.)

### Key Entities *(include if feature involves data)*

- **Evidence**: `{ goal: str, found: bool, content?: str, location: str, rationale: str, confidence: float }` (typed model/schema)
- **JudicialOpinion**: `{ judge: 'Prosecutor'|'Defense'|'TechLead', criterion_id: str, score: int[1-5], argument: str, cited_evidence: List[str] }`
- **CriterionResult**: `{ dimension_id, dimension_name, final_score, judge_opinions: List[JudicialOpinion], dissent_summary?, remediation }`
- **AuditReport**: `{ repo_url, executive_summary, overall_score, criteria: List[CriterionResult], remediation_plan }`
- **AgentState**: Typed structure containing `repo_url`, `pdf_path`, `rubric_dimensions`, `evidences`, `opinions`, `final_report` with reducers to prevent overwrite during parallel execution.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For a provided repository under 250 files and a single PDF, the system MUST produce a complete Markdown `AuditReport` within 5 minutes on a standard developer workstation. (Measure via run time.)
- **SC-002**: The produced report MUST have zero hallucinated paths for P1 acceptance (i.e., every file path cited in `Report Accuracy` must exist in the cloned repo) for the sample test dataset. (Measure by cross-referencing cited paths against the cloned repository.)
- **SC-003**: Judges MUST return structured `JudicialOpinion` objects for 99% of runs; malformed responses must be handled and logged. (Measure via validation ratio across test runs.)
- **SC-004**: When score variance across judges for any criterion exceeds 2, the final Markdown report MUST include a `Dissent Summary` explaining the conflict. (Measure by checking report content.)
- **SC-005**: Security vulnerabilities identified by the Prosecutor that meet the `security_override` rule MUST cap the affected criterion score at 3 in the final report. (Verify via unit tests for the Chief Justice rules.)

## Assumptions

- Language model provider selection, token limits, and API keys are environment-specific and out of scope for this spec; the system will treat the model provider as a configurable dependency.  
- VisionInspector image analysis is implemented but may be optional during evaluation runs; absence of images is acceptable and must be recorded.  
- Performance targets are reasonable estimates for demo hardware; production horizontal scaling is out of scope.

## Notes

- This spec follows the Week 2 Rubric attached to the project and aims to produce testable artifacts that map directly to the rubric dimensions.
 
