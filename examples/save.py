"""systems/save.py — JSON-backed save/load with multiple slots and settings persistence."""
from __future__ import annotations
import json
import os
from core.settings import SAVE_FILE, SAVE_DIR, SETTINGS_FILE


def ensure_dirs() -> None:
    os.makedirs(SAVE_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)


def save_game(slot: int, data: dict) -> None:
    ensure_dirs()
    path = SAVE_FILE.format(slot)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_game(slot: int) -> dict | None:
    path = SAVE_FILE.format(slot)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def slot_exists(slot: int) -> bool:
    return os.path.exists(SAVE_FILE.format(slot))


def delete_slot(slot: int) -> None:
    path = SAVE_FILE.format(slot)
    if os.path.exists(path):
        os.remove(path)


DEFAULT_SETTINGS = {
    "music_volume": 0.7,
    "sfx_volume": 0.8,
    "fullscreen": False,
    "show_fps": False,
}


def load_settings() -> dict:
    ensure_dirs()
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return dict(DEFAULT_SETTINGS)
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    merged = dict(DEFAULT_SETTINGS)
    merged.update(data)
    return merged


def save_settings(settings: dict) -> None:
    ensure_dirs()
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
