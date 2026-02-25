# Automaton Auditor Architecture

The Automaton Auditor is a deep multi-agent governance system built on a hierarchical LangGraph `StateGraph`. It follows a "Digital Courtroom" model using a three-layer orchestration.

## Architecture Diagram

```mermaid
graph TD
    %% Input and Entry
    StartNode((START)) --> |"Repo"| RepoInvestigator
    StartNode --> |"File"| DocAnalyst
    StartNode --> |"File"| VisionInspector

    %% Layer 1: Detective Layer
    subgraph DetectiveLayer ["Layer 1: Detective Layer"]
        RepoInvestigator["RepoInvestigator<br/>(AST/Git)"]
        DocAnalyst["DocAnalyst<br/>(PDF/Docs)"]
        VisionInspector["VisionInspector<br/>(Diagrams)"]
    end

    %% Fan-In to Aggregator
    RepoInvestigator --> |"Evidence"| Aggregator
    DocAnalyst --> |"Evidence"| Aggregator
    VisionInspector --> |"Evidence"| Aggregator

    Aggregator["Evidence Aggregator<br/>(JSON Synthesis)"] --> |"Contextual State"| Prosecutor
    Aggregator --> |"Contextual State"| Defense
    Aggregator --> |"Contextual State"| TechLead

    %% Layer 2: Judicial Layer
    subgraph JudicialLayer ["Layer 2: Judicial Layer"]
        Prosecutor["Prosecutor<br/>(Critical)"]
        Defense["Defense<br/>(Optimistic)"]
        TechLead["Tech Lead<br/>(Pragmatic)"]
    end

    %% Fan-In to Chief Justice
    Prosecutor --> |"Judgment"| ChiefJustice
    Defense --> |"Judgment"| ChiefJustice
    TechLead --> |"Judgment"| ChiefJustice

    ChiefJustice["Chief Justice Node<br/>(Deterministic)"]

    %% Rules Context
    subgraph JusticeRules ["Chief Justice Rules"]
        SecurityOverride["Security Capping"]
        FactSupremacy["Evidence > Vibe"]
    end
    ChiefJustice -.- JusticeRules

    %% Output
    ChiefJustice --> |"Final Markdown"| EndNode((END))

    %% Styling
    classDef detective fill:#e1f5fe,stroke:#01579b;
    classDef judicial fill:#fff3e0,stroke:#e65100;
    classDef synthesis fill:#f3e5f5,stroke:#4a148c;
    class RepoInvestigator,DocAnalyst,VisionInspector detective;
    class Prosecutor,Defense,TechLead judicial;
    class ChiefJustice,Aggregator synthesis;
```

## Key Architectural Principles

1.  **Hierarchical StateGraph**: The system utilizes LangGraph to manage complex state transitions and parallel execution branches.
2.  **Two-Layer Parallel Orchestration**: 
    - **Detective Layer**: Parallel forensic collection of objective facts.
    - **Judicial Layer**: Parallel dialectical analysis of facts through distinct personas.
3.  **Deterministic Synthesis**: The Chief Justice node uses hardcoded Python logic (Constitutional Rules) rather than another LLM prompt to ensure consistency and security adherence.
4.  **Typed State Management**: Uses Pydantic and `TypedDict` with state reducers (`operator.add`, `operator.ior`) to handle concurrent updates without data loss.
