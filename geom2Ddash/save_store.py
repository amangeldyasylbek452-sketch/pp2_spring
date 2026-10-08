"""Save helpers for the game using SQLite with a JSON fallback."""
import json
import sqlite3
from pathlib import Path

import config


def _db_path(save_path=None, db_path=None):
    if db_path:
        return Path(db_path)
    base = Path(save_path or config.SAVE_FILE)
    return base.with_suffix(".db")


def _ensure_schema(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS save_data (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )
    conn.commit()


def load_save_data(save_path=None, db_path=None):
    path = Path(save_path or config.SAVE_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    db_file = _db_path(path, db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)

    data = {}
    conn = sqlite3.connect(db_file)
    try:
        _ensure_schema(conn)
        row = conn.execute("SELECT value FROM save_data WHERE key = 'data'").fetchone()
        if row is not None:
            try:
                data = json.loads(row[0])
            except (TypeError, json.JSONDecodeError):
                data = {}
        elif path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (TypeError, json.JSONDecodeError, OSError):
                data = {}
    finally:
        conn.close()

    if not isinstance(data, dict):
        data = {}

    data.setdefault("coins", 0)
    data.setdefault("unlocked_skins", ["classic"])
    data.setdefault("equipped_skin", "classic")
    data.setdefault("last_world_id", config.WORLDS[0]["id"])
    return data, path


def save_save_data(save_data, save_path=None, db_path=None):
    path = Path(save_path or config.SAVE_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    db_file = _db_path(path, db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_file)
    try:
        _ensure_schema(conn)
        conn.execute(
            "INSERT OR REPLACE INTO save_data(key, value) VALUES (?, ?)",
            ("data", json.dumps(save_data, indent=2)),
        )
        conn.commit()
    finally:
        conn.close()

    path.write_text(json.dumps(save_data, indent=2), encoding="utf-8")
    return path
