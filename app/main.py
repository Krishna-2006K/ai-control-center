from __future__ import annotations

from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from app.db.database import initialize
from app.services.workflow import (
    create_account,
    create_decision,
    create_evidence,
    create_project,
    create_session,
    generate_handoff,
    get_latest_handoff,
    get_project,
    list_accounts,
    list_decisions,
    list_evidence,
    list_projects,
    list_sessions,
    update_project,
)

app = FastAPI(title="AICC — AI Control Center", version="0.2.0")
initialize()

Status = Literal["not_started", "in_progress", "done"]
Confidence = Literal["unverified", "tentative", "confirmed"]


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    current_state: str | None = Field(default=None, max_length=5000)
    next_action: str | None = Field(default=None, max_length=2000)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    current_state: str | None = Field(default=None, max_length=5000)
    next_action: str | None = Field(default=None, max_length=2000)
    status: Status | None = None
    confidence: Confidence | None = None


class AccountCreate(BaseModel):
    provider: str = Field(min_length=1, max_length=50)
    account_name: str = Field(min_length=1, max_length=200)
    tier: str = Field(default="free", min_length=1, max_length=50)
    client_context: str | None = Field(default=None, max_length=500)
    notes: str | None = Field(default=None, max_length=2000)


class SessionCreate(BaseModel):
    provider: str = Field(min_length=1, max_length=50)
    source_type: str = Field(min_length=1, max_length=50)
    summary: str | None = Field(default=None, max_length=5000)
    account_id: str | None = None
    session_date: str | None = Field(default=None, max_length=100)
    provenance: str | None = Field(default=None, max_length=2000)


class EvidenceCreate(BaseModel):
    evidence_type: str = Field(min_length=1, max_length=100)
    source_location: str | None = Field(default=None, max_length=2000)
    notes: str | None = Field(default=None, max_length=5000)
    content_hash: str | None = Field(default=None, max_length=128)


class DecisionCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    decision: str = Field(min_length=1, max_length=5000)
    rationale: str | None = Field(default=None, max_length=5000)
    confidence: Confidence = "unverified"
    evidence_id: str | None = None


def require_project(project_id: str) -> None:
    if not get_project(project_id):
        raise HTTPException(status_code=404, detail="Project not found")


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    html_path = Path(__file__).with_name("web") / "index.html"
    return html_path.read_text(encoding="utf-8")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "aicc"}


@app.get("/api/projects")
def api_list_projects() -> dict[str, list[dict]]:
    return {"projects": list_projects()}


@app.post("/api/projects", status_code=201)
def api_create_project(payload: ProjectCreate) -> dict:
    cleaned_name = payload.name.strip()
    if not cleaned_name:
        raise HTTPException(status_code=422, detail="Project name cannot be blank")
    return create_project(cleaned_name, payload.current_state, payload.next_action)


@app.get("/api/projects/{project_id}")
def api_get_project(project_id: str) -> dict:
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {
        "project": project,
        "sessions": list_sessions(project_id),
        "evidence": list_evidence(project_id),
        "decisions": list_decisions(project_id),
        "handoff": get_latest_handoff(project_id),
    }


@app.patch("/api/projects/{project_id}")
def api_update_project(project_id: str, payload: ProjectUpdate) -> dict:
    require_project(project_id)
    values = payload.model_dump(exclude_none=True)
    if "name" in values and not values["name"].strip():
        raise HTTPException(status_code=422, detail="Project name cannot be blank")
    project = update_project(project_id, **values)
    return project


@app.get("/api/accounts")
def api_list_accounts() -> dict[str, list[dict]]:
    return {"accounts": list_accounts()}


@app.post("/api/accounts", status_code=201)
def api_create_account(payload: AccountCreate) -> dict:
    return create_account(**payload.model_dump())


@app.post("/api/projects/{project_id}/sessions", status_code=201)
def api_create_session(project_id: str, payload: SessionCreate) -> dict:
    require_project(project_id)
    try:
        return create_session(project_id=project_id, **payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/projects/{project_id}/sessions")
def api_list_sessions(project_id: str) -> dict[str, list[dict]]:
    require_project(project_id)
    return {"sessions": list_sessions(project_id)}


@app.post("/api/projects/{project_id}/evidence", status_code=201)
def api_create_evidence(project_id: str, payload: EvidenceCreate) -> dict:
    require_project(project_id)
    return create_evidence(project_id, **payload.model_dump())


@app.get("/api/projects/{project_id}/evidence")
def api_list_evidence(project_id: str) -> dict[str, list[dict]]:
    require_project(project_id)
    return {"evidence": list_evidence(project_id)}


@app.post("/api/projects/{project_id}/decisions", status_code=201)
def api_create_decision(project_id: str, payload: DecisionCreate) -> dict:
    require_project(project_id)
    try:
        return create_decision(project_id, **payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/projects/{project_id}/decisions")
def api_list_decisions(project_id: str) -> dict[str, list[dict]]:
    require_project(project_id)
    return {"decisions": list_decisions(project_id)}


@app.post("/api/projects/{project_id}/handoff", status_code=201)
def api_generate_handoff(project_id: str) -> dict:
    require_project(project_id)
    try:
        return generate_handoff(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
