from fastapi.testclient import TestClient

from app.db.database import initialize
from app.main import app


def test_health(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("AICC_DB_PATH", str(tmp_path / "health.db"))
    initialize()
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "aicc"}


def test_projects_start_empty(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("AICC_DB_PATH", str(tmp_path / "projects.db"))
    initialize()
    response = TestClient(app).get("/api/projects")
    assert response.status_code == 200
    assert response.json() == {"projects": []}
