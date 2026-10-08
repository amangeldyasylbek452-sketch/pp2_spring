"""examples/ai.py — compatibility shim for the examples package.

The package currently uses a `Camera` helper from `ai` in `examples/game.py`.
This module forwards that export to `camera.py` so the import stays stable
while the actual implementation lives in the correctly named module.
"""
from __future__ import annotations
from .camera import Camera

__all__ = ["Camera"]
