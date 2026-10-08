"""examples/player.py — player wrapper."""
from __future__ import annotations

try:
    from .entities.player import Player
except ImportError:
    from entities.player import Player

__all__ = ["Player"]
