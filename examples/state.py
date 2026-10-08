"""examples/state.py — entity wrapper."""
from __future__ import annotations

try:
    from .entities.entity import Entity
except ImportError:
    from entities.entity import Entity

__all__ = ["Entity"]
