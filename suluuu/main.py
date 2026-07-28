"""
main.py
-------
Entry point for Rising Lava Ball. Run this file to play:

    python main.py

Controls:
    A / Left Arrow  - Move left
    D / Right Arrow - Move right
    SPACE           - Jump (only while touching a platform)
    P / ESC         - Pause
    F11             - Toggle fullscreen
"""

from game import Game


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
