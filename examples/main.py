#!/usr/bin/env python3
"""Play the Cursed Kingdom example game."""
from __future__ import annotations
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    from .game import Game
except ImportError:
    from game import Game


def main() -> None:
    Game().run()


if __name__ == "__main__":
    main()
