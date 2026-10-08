"""
save.py - JSON-based save/load system (auto save + manual save).
Persists: position, inventory, HP, current level, quest progress.
"""
import json
import os
from pathlib import Path
from settings import SAVE_PATH, DATA_DIR

ROOT = Path(__file__).resolve().parent


def ensure_data_dir():
    os.makedirs(ROOT / DATA_DIR, exist_ok=True)


def save_game(player, level_name, quest_state, slot="manual"):
    ensure_data_dir()
    data = {}
    save_path = ROOT / SAVE_PATH
    if os.path.exists(save_path):
        try:
            with open(save_path, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            data = {}

    data[slot] = {
        "position": [player.pos.x, player.pos.y],
        "hp": player.hp,
        "max_hp": player.max_hp,
        "gold": player.gold,
        "inventory": player.inventory,
        "level": level_name,
        "quest_state": quest_state,
    }
    with open(save_path, "w") as f:
        json.dump(data, f, indent=2)
    return data[slot]


def load_game(slot="manual"):
    save_path = ROOT / SAVE_PATH
    if not os.path.exists(save_path):
        return None
    try:
        with open(save_path, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None
    return data.get(slot)


def has_save():
    save_path = ROOT / SAVE_PATH
    if not os.path.exists(save_path):
        return False
    try:
        with open(save_path, "r") as f:
            data = json.load(f)
        return bool(data)
    except (json.JSONDecodeError, OSError):
        return False