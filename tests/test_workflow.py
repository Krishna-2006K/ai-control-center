import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("AICC_DB_PATH", str(tmp_path / "aicc.db"))
    from app.main import app
    from app.db.database import initialize
    initialize()
    return TestClient(app)


def test_complete_phase_two_workflow(client):
    project = client.post("/api/projects", json={
        "name": "Phase 2 Demo",
        "current_state": "Foundation complete",
        "next_action": "Record the first real session",
    })
    assert project.status_code == 201
    project_id = project.json()["id"]

    account = client.post("/api/accounts", json={
        "provider": "Claude",
        "account_name": "Claude Free",
        "tier": "free",
    })
    assert account.status_code == 201
    account_id = account.json()["id"]

    session = client.post(f"/api/projects/{project_id}/sessions", json={
        "provider": "Claude",
        "account_id": account_id,
        "source_type": "Manual",
        "summary": "Reviewed the Phase 2 workflow and implemented the local UI.",
    })
    assert session.status_code == 201

    update = client.patch(f"/api/projects/{project_id}", json={
        "current_state": "End-to-end workflow implemented locally",
        "next_action": "Generate a handoff and review it",
        "status": "in_progress",
    })
    assert update.status_code == 200
    assert update.json()["current_state"] == "End-to-end workflow implemented locally"

    evidence = client.post(f"/api/projects/{project_id}/evidence", json={
        "evidence_type": "Git",
        "source_location": "Krishna-2006K/ai-control-center",
        "notes": "Phase 2 implementation commit",
    })
    assert evidence.status_code == 201
    evidence_id = evidence.json()["id"]

    decision = client.post(f"/api/projects/{project_id}/decisions", json={
        "title": "Keep Phase 2 local-first",
        "decision": "Do not add provider APIs or Notion sync yet.",
        "rationale": "Preserve the free-tier and simple-core constraints.",
        "confidence": "confirmed",
        "evidence_id": evidence_id,
    })
    assert decision.status_code == 201

    handoff = client.post(f"/api/projects/{project_id}/handoff")
    assert handoff.status_code == 201
    body = handoff.json()
    assert body["where_i_was"] == "End-to-end workflow implemented locally"
    assert "decision" in body["what_changed"]
    assert "Claude Free" in body["which_ai_worked_on_it"]
    assert body["what_to_do_next"] == "Generate a handoff and review it"

    detail = client.get(f"/api/projects/{project_id}")
    assert detail.status_code == 200
    assert len(detail.json()["sessions"]) == 1
    assert len(detail.json()["evidence"]) == 1
    assert len(detail.json()["decisions"]) == 1
    assert detail.json()["handoff"]["id"] == handoff.json()["id"]


def test_validation_rejects_blank_project_name(client):
    response = client.post("/api/projects", json={"name": "  "})
    assert response.status_code == 422
