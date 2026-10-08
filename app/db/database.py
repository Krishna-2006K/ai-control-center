from __future__ import annotations

import os
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = ROOT / "data" / "aicc.db"

def database_path() -> Path:
    return Path(os.getenv("AICC_DB_PATH", str(DEFAULT_DB_PATH)))

def connect() -> sqlite3.Connection:
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def initialize() -> None:
    schema_path = Path(__file__).with_name("schema.sql")
    with connect() as connection:
        connection.executescript(schema_path.read_text(encoding="utf-8"))
