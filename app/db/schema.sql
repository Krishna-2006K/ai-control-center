PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'not_started',
    current_state TEXT,
    next_action TEXT,
    confidence TEXT NOT NULL DEFAULT 'unverified',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ai_accounts (
    id TEXT PRIMARY KEY,
    provider TEXT NOT NULL,
    account_name TEXT NOT NULL,
    tier TEXT NOT NULL DEFAULT 'free',
    client_context TEXT,
    notes TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ai_sessions (
    id TEXT PRIMARY KEY,
    provider TEXT NOT NULL,
    account_id TEXT,
    project_id TEXT,
    source_type TEXT NOT NULL,
    session_date TEXT,
    summary TEXT,
    provenance TEXT,
    reviewed INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (account_id) REFERENCES ai_accounts(id),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE TABLE IF NOT EXISTS evidence (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    evidence_type TEXT NOT NULL,
    source_location TEXT,
    status TEXT NOT NULL DEFAULT 'raw',
    content_hash TEXT,
    notes TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE TABLE IF NOT EXISTS decisions (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    title TEXT NOT NULL,
    decision TEXT NOT NULL,
    rationale TEXT,
    confidence TEXT NOT NULL DEFAULT 'unverified',
    evidence_id TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (evidence_id) REFERENCES evidence(id)
);

CREATE TABLE IF NOT EXISTS handoffs (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    where_i_was TEXT,
    what_changed TEXT,
    which_ai_worked_on_it TEXT,
    what_to_do_next TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE INDEX IF NOT EXISTS idx_sessions_project ON ai_sessions(project_id);
CREATE INDEX IF NOT EXISTS idx_evidence_project ON evidence(project_id);
CREATE INDEX IF NOT EXISTS idx_decisions_project ON decisions(project_id);
CREATE INDEX IF NOT EXISTS idx_handoffs_project ON handoffs(project_id);
