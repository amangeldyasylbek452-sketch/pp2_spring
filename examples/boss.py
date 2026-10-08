"""examples/boss.py — boss module wrapper."""
from __future__ import annotations

try:
    from .entities.boss import SkeletonCaptain
except ImportError:
    from entities.boss import SkeletonCaptain

__all__ = ["SkeletonCaptain"]
