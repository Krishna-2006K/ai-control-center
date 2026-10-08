from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.db.database import connect, initialize


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def ensure_initialized() -> None:
    initialize()


def create_project(name: str, current_state: str | None, next_action: str | None) -> dict:
    project_id = new_id("proj")
    timestamp = now()
    with connect() as db:
        db.execute(
            """INSERT INTO projects
            (id, name, status, current_state, next_action, confidence, created_at, updated_at)
            VALUES (?, ?, 'not_started', ?, ?, 'unverified', ?, ?)""",
            (project_id, name, current_state, next_action, timestamp, timestamp),
        )
        return get_project(project_id)


def update_project(project_id: str, **fields: str | None) -> dict | None:
    allowed = {"name", "status", "current_state", "next_action", "confidence"}
    changes = {k: v for k, v in fields.items() if k in allowed and v is not None}
    if not changes:
        return get_project(project_id)
    changes["updated_at"] = now()
    assignments = ", ".join(f"{key} = ?" for key in changes)
    values = list(changes.values()) + [project_id]
    with connect() as db:
        cursor = db.execute(
            f"UPDATE projects SET {assignments} WHERE id = ?", values
        )
        if cursor.rowcount == 0:
            return None
    return get_project(project_id)


def list_projects() -> list[dict]:
    with connect() as db:
        rows = db.execute(
            """SELECT id, name, status, current_state, next_action, confidence,
                      created_at, updated_at
               FROM projects ORDER BY updated_at DESC"""
        ).fetchall()
    return [dict(row) for row in rows]


def get_project(project_id: str) -> dict | None:
    with connect() as db:
        row = db.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    return dict(row) if row else None


def create_account(provider: str, account_name: str, tier: str = "free",
                   client_context: str | None = None, notes: str | None = None) -> dict:
    account_id = new_id("acct")
    timestamp = now()
    with connect() as db:
        db.execute(
            """INSERT INTO ai_accounts
            (id, provider, account_name, tier, client_context, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (account_id, provider, account_name, tier, client_context, notes, timestamp, timestamp),
        )
        row = db.execute("SELECT * FROM ai_accounts WHERE id = ?", (account_id,)).fetchone()
    return dict(row)


def list_accounts() -> list[dict]:
    with connect() as db:
        rows = db.execute("SELECT * FROM ai_accounts ORDER BY updated_at DESC").fetchall()
    return [dict(row) for row in rows]


def create_session(project_id: str, provider: str, source_type: str,
                   summary: str | None, account_id: str | None,
                   session_date: str | None, provenance: str | None) -> dict:
    session_id = new_id("sess")
    timestamp = now()
    with connect() as db:
        if not db.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone():
            raise ValueError("Project not found")
        if account_id and not db.execute(
            "SELECT 1 FROM ai_accounts WHERE id = ?", (account_id,)
        ).fetchone():
            raise ValueError("AI account not found")
        db.execute(
            """INSERT INTO ai_sessions
            (id, provider, account_id, project_id, source_type, session_date, summary,
             provenance, reviewed, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)""",
            (session_id, provider, account_id, project_id, source_type, session_date,
             summary, provenance, timestamp, timestamp),
        )
        row = db.execute(
            """SELECT s.*, a.account_name
               FROM ai_sessions s LEFT JOIN ai_accounts a ON a.id = s.account_id
               WHERE s.id = ?""",
            (session_id,),
        ).fetchone()
    return dict(row)


def list_sessions(project_id: str) -> list[dict]:
    with connect() as db:
        rows = db.execute(
            """SELECT s.*, a.account_name
               FROM ai_sessions s LEFT JOIN ai_accounts a ON a.id = s.account_id
               WHERE s.project_id = ? ORDER BY s.created_at DESC""",
            (project_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def create_evidence(project_id: str, evidence_type: str, source_location: str | None,
                    notes: str | None, content_hash: str | None) -> dict:
    evidence_id = new_id("ev")
    timestamp = now()
    with connect() as db:
        if not db.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone():
            raise ValueError("Project not found")
        db.execute(
            """INSERT INTO evidence
            (id, project_id, evidence_type, source_location, status, content_hash,
             notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, 'raw', ?, ?, ?, ?)""",
            (evidence_id, project_id, evidence_type, source_location, content_hash,
             notes, timestamp, timestamp),
        )
        row = db.execute("SELECT * FROM evidence WHERE id = ?", (evidence_id,)).fetchone()
    return dict(row)


def list_evidence(project_id: str) -> list[dict]:
    with connect() as db:
        rows = db.execute(
            "SELECT * FROM evidence WHERE project_id = ? ORDER BY created_at DESC",
            (project_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def create_decision(project_id: str, title: str, decision: str,
                    rationale: str | None, confidence: str, evidence_id: str | None) -> dict:
    decision_id = new_id("dec")
    timestamp = now()
    with connect() as db:
        if not db.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone():
            raise ValueError("Project not found")
        if evidence_id and not db.execute(
            "SELECT 1 FROM evidence WHERE id = ? AND project_id = ?",
            (evidence_id, project_id),
        ).fetchone():
            raise ValueError("Evidence not found for this project")
        db.execute(
            """INSERT INTO decisions
            (id, project_id, title, decision, rationale, confidence, evidence_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (decision_id, project_id, title, decision, rationale, confidence, evidence_id, timestamp),
        )
        row = db.execute("SELECT * FROM decisions WHERE id = ?", (decision_id,)).fetchone()
    return dict(row)


def list_decisions(project_id: str) -> list[dict]:
    with connect() as db:
        rows = db.execute(
            "SELECT * FROM decisions WHERE project_id = ? ORDER BY created_at DESC",
            (project_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def generate_handoff(project_id: str) -> dict:
    project = get_project(project_id)
    if not project:
        raise ValueError("Project not found")
    sessions = list_sessions(project_id)
    evidence = list_evidence(project_id)
    decisions = list_decisions(project_id)
    ai_names = []
    for session in sessions:
        label = session["account_name"] or session["provider"]
        if label and label not in ai_names:
            ai_names.append(label)
    changed_parts = []
    if decisions:
        changed_parts.append(f"{len(decisions)} decision(s) recorded")
    if evidence:
        changed_parts.append(f"{len(evidence)} evidence item(s) recorded")
    if sessions:
        changed_parts.append(f"{len(sessions)} AI session(s) recorded")
    handoff_id = new_id("handoff")
    with connect() as db:
        db.execute(
            """INSERT INTO handoffs
            (id, project_id, where_i_was, what_changed, which_ai_worked_on_it,
             what_to_do_next, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                handoff_id,
                project_id,
                project["current_state"] or "No current state recorded yet.",
                "; ".join(changed_parts) or "No changes recorded yet.",
                ", ".join(ai_names) or "No AI session recorded yet.",
                project["next_action"] or "No next action recorded yet.",
                now(),
            ),
        )
        row = db.execute("SELECT * FROM handoffs WHERE id = ?", (handoff_id,)).fetchone()
    return dict(row)


def get_latest_handoff(project_id: str) -> dict | None:
    with connect() as db:
        row = db.execute(
            "SELECT * FROM handoffs WHERE project_id = ? ORDER BY created_at DESC LIMIT 1",
            (project_id,),
        ).fetchone()
    return dict(row) if row else None
