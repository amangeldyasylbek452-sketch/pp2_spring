#!/usr/bin/env python3
"""
The Cursed Kingdom
-------------------
A 2D pixel-art action-adventure vertical slice built with Pygame CE.

Run with:  python main.py
Controls:  A/D or Arrows move · Space jump · Shift sprint · J attack
           K hold heavy attack · L hold block/parry · Ctrl roll · E interact
           Esc pause · F1 toggle debug overlay
"""
from __future__ import annotations
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game import Game


def main() -> None:
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
