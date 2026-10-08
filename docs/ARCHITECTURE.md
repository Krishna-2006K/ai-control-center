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
