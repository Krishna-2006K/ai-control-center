# AICC Architecture — Initial Contract

## 1. Canonical state

AICC is intended to become the canonical store for project state.

External systems are evidence sources or integrations unless explicitly promoted to canonical status.

## 2. Evidence pipeline

```
Raw evidence
    -> normalized evidence
    -> human review
    -> canonical state
```

Raw evidence must remain recoverable. A summary must never silently replace its source.

## 3. Core entities

- Project
- AI Account
- AI Session
- Evidence
- Decision
- Handoff

The model can grow later with artifacts, changes, client profiles, and provenance records.

## 4. Free-tier constraint

The core application must remain useful without paid Claude/GPT APIs.

Provider-specific automation is therefore an adapter, not a dependency of the core.

## 5. Authority

AI suggestions are not automatically canonical. High-impact state changes require confirmation.

## 6. First milestone

A user should eventually be able to answer, for any project:

1. Where was I?
2. What changed?
3. Which AI worked on it?
4. What should I do next?

## 7. Explicit non-goals for the first milestone

- Browser automation
- Autonomous reconciliation
- Always-on agents
- Paid API dependence
- Replacing Notion
- Complex multi-user deployment
- Cloud infrastructure

## 8. Phase 2 workflow

The first usable application workflow is deliberately manual and local:

```text
Create Project
    -> Record AI Session
    -> Update Project State
    -> Record Evidence
    -> Record Decision
    -> Generate Handoff
```

The Handoff is a canonical snapshot generated from AICC project state plus recorded sessions, evidence, and decisions. It answers four questions: where I was, what changed, which AI worked on it, and what to do next.

No provider API, browser automation, Notion synchronization, or conversation importer is required for this workflow.
