# Automaton Auditor Architecture

The Automaton Auditor is a deep multi-agent governance system built on a hierarchical LangGraph `StateGraph`. It follows a "Digital Courtroom" model using a three-layer orchestration.

## Architecture Diagram

```mermaid
graph TD
    %% Input
    Input[("Input: GitHub Repo URL & PDF")] --> StartNode

    subgraph DetectiveLayer ["Layer 1: Detective Layer (Forensic Analysis)"]
        direction LR
        RepoInvestigator["RepoInvestigator<br/>(AST Parser, Git History)"]
        DocAnalyst["DocAnalyst<br/>(PDF Ingestion, Cross-Ref)"]
        VisionInspector["VisionInspector<br/>(Diagram Analysis)"]
    end

    subgraph JudicialLayer ["Layer 2: Judicial Layer (Dialectical Bench)"]
        direction LR
        Prosecutor["Prosecutor<br/>(Critical Lens)"]
        Defense["Defense<br/>(Optimistic Lens)"]
        TechLead["Tech Lead<br/>(Pragmatic Lens)"]
    end

    %% Flow: Start to Detectives
    StartNode(("Start")) --> RepoInvestigator
    StartNode --> DocAnalyst
    StartNode --> VisionInspector

    %% Fan-In from Detectives to Aggregator
    RepoInvestigator --> EvidenceAggregator["Evidence Aggregator<br/>(JSON Synthesis)"]
    DocAnalyst --> EvidenceAggregator
    VisionInspector --> EvidenceAggregator

    %% Flow: Aggregator to Judges (Fan-Out)
    EvidenceAggregator --> Prosecutor
    EvidenceAggregator --> Defense
    EvidenceAggregator --> TechLead

    %% Fan-In from Judges to Chief Justice
    Prosecutor --> ChiefJustice["Chief Justice Node<br/>(Deterministic Logic)"]
    Defense --> ChiefJustice
    TechLead --> ChiefJustice

    %% Rules in Chief Justice
    subgraph JusticeRules ["Chief Justice Synthesis Rules"]
        direction TB
        SecurityOverride["Security Override<br/>(Capping Scores)"]
        FactSupremacy["Fact Supremacy<br/>(Evidence vs. Vibe)"]
        DissentRequirement["Dissent Summary<br/>(Var > 2)"]
    end
    
    ChiefJustice -.- JusticeRules

    %% Output
    ChiefJustice --> FinalReport[("Final Output: Markdown Audit Report")]

    %% Styling
    classDef detective fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef judicial fill:#fff3e0,stroke:#e65100,stroke-width:2px;
    classDef synthesis fill:#f3e5f5,stroke:#4a148c,stroke-width:2px;
    classDef rules fill:#fafafa,stroke:#9e9e9e,stroke-dasharray: 5 5;
    
    class RepoInvestigator,DocAnalyst,VisionInspector detective;
    class Prosecutor,Defense,TechLead judicial;
    class ChiefJustice synthesis;
    class JusticeRules,SecurityOverride,FactSupremacy,DissentRequirement rules;
```

## Key Architectural Principles

1.  **Hierarchical StateGraph**: The system utilizes LangGraph to manage complex state transitions and parallel execution branches.
2.  **Two-Layer Parallel Orchestration**: 
    - **Detective Layer**: Parallel forensic collection of objective facts.
    - **Judicial Layer**: Parallel dialectical analysis of facts through distinct personas.
3.  **Deterministic Synthesis**: The Chief Justice node uses hardcoded Python logic (Constitutional Rules) rather than another LLM prompt to ensure consistency and security adherence.
4.  **Typed State Management**: Uses Pydantic and `TypedDict` with state reducers (`operator.add`, `operator.ior`) to handle concurrent updates without data loss.
