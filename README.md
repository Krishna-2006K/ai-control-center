# AICC — AI Control Center

A local-first control plane for tracking work across AI assistants, projects, sessions, evidence, decisions, and handoffs.

## Design goals

- Work with free Claude and free GPT accounts.
- Keep AICC useful without paid AI APIs.
- Keep canonical project state separate from external tools.
- Preserve raw evidence and provenance.
- Prefer human-confirmed state over autonomous mutation.
- Start local and simple; add integrations only when they solve a real problem.

## Architecture

```
AI assistants / exports / local files / GitHub / Notion
                         |
                      Evidence
                         |
                  Normalization
                         |
                    AICC Core
                 /      |       \
            Projects Sessions Decisions
                 \      |       /
                    Handoffs
                         |
                    Local UI
```

## Repository layout

```
app/                 Application package
  db/                SQLite schema and persistence
  models/            Domain models
  services/          Core application services
  web/               Web interface
tests/               Automated tests
docs/                Architecture and operating decisions
data/                Local runtime data (gitignored)
```

## Free-tier operating model

AICC does not require an AI API key to function. Import/export and human-entered records are first-class workflows. AI-assisted features can be added later when a compatible provider or local model is available.

## Development

The first implementation milestone is deliberately small: establish the canonical data model and a local application boundary before adding provider-specific ingestion.
