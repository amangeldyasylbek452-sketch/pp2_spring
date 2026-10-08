"""
config.py - Central configuration for GeoCube Runner
All tunable constants, color palettes, key bindings and difficulty tables live here.
"""
import os
import json

# ---------------------------------------------------------------------------
# Window / engine
# ---------------------------------------------------------------------------
WINDOW_TITLE = "GeoCube Runner"
DEFAULT_WIDTH = 1024
DEFAULT_HEIGHT = 576
FPS = 60
FIXED_DT = 1.0 / FPS  # fixed timestep in seconds

RESOLUTIONS = [(960, 540), (1024, 576), (1280, 720), (1600, 900)]

SAVE_DIR = os.path.join(os.path.expanduser("~"), ".geocube_runner")
SAVE_FILE = os.path.join(SAVE_DIR, "save.json")

# ---------------------------------------------------------------------------
# Physics
# ---------------------------------------------------------------------------
GRAVITY = 2200.0                 # px/s^2
JUMP_VELOCITY = -780.0            # px/s (initial jump impulse)
JUMP_CUT_MULTIPLIER = 0.45        # releasing jump early cuts upward velocity
MAX_FALL_SPEED = 1500.0
COYOTE_TIME = 0.09                # seconds after leaving ground where jump still works
JUMP_BUFFER_TIME = 0.12           # seconds a jump press is remembered before landing
DOUBLE_JUMP_VELOCITY = -680.0
GROUND_Y_RATIO = 0.78             # fraction of screen height where the ground sits

CUBE_SIZE = 42
BASE_SCROLL_SPEED = 360.0         # px/s at difficulty 1
SPEED_PER_DIFFICULTY = 55.0       # extra scroll speed per difficulty star

ROTATION_SPEED = 380.0            # degrees / second while airborne

# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------
WHITE = (255, 255, 255)
BLACK = (10, 10, 14)
UI_BG = (18, 20, 28)
UI_PANEL = (28, 32, 44)
UI_ACCENT = (90, 200, 255)
UI_ACCENT_2 = (255, 120, 190)
UI_TEXT = (235, 238, 245)
UI_MUTED = (150, 158, 175)
GOLD = (255, 205, 80)
DANGER = (255, 80, 90)
SUCCESS = (110, 230, 150)

# ---------------------------------------------------------------------------
# Key bindings (defaults, overridable via settings)
# ---------------------------------------------------------------------------
import pygame

DEFAULT_KEYBINDS = {
    "jump": pygame.K_SPACE,
    "jump_alt": pygame.K_UP,
    "restart": pygame.K_r,
    "pause": pygame.K_ESCAPE,
}

# ---------------------------------------------------------------------------
# Difficulty
# ---------------------------------------------------------------------------
DIFFICULTY_STARS = {
    1: "Easy",
    2: "Normal",
    3: "Hard",
    4: "Insane",
    5: "Demon",
}

DIFFICULTY_COLOR = {
    1: (110, 230, 150),
    2: (110, 190, 255),
    3: (255, 190, 90),
    4: (255, 110, 90),
    5: (220, 90, 255),
}


def stars_string(n):
    return "\u2605" * n + "\u2606" * (5 - n)


# ---------------------------------------------------------------------------
# World / level definitions
# ---------------------------------------------------------------------------
# Each world defines its visual theme, palette, difficulty and length.
# Levels are procedurally assembled from these parameters (see level.py).
WORLDS = [
    {
        "id": "green_hills",
        "name": "Green Hills",
        "difficulty": 1,
        "length": 2600,
        "sky_top": (140, 205, 245),
        "sky_bottom": (210, 240, 250),
        "ground": (86, 160, 90),
        "ground_dark": (64, 128, 70),
        "accent": (255, 255, 255),
        "decor": "hills",
        "seed": 101,
    },
    {
        "id": "crystal_cave",
        "name": "Crystal Cave",
        "difficulty": 2,
        "length": 2900,
        "sky_top": (18, 26, 48),
        "sky_bottom": (36, 48, 80),
        "ground": (52, 66, 110),
        "ground_dark": (34, 44, 78),
        "accent": (110, 190, 255),
        "decor": "crystals",
        "seed": 202,
    },
    {
        "id": "volcano",
        "name": "Volcano",
        "difficulty": 3,
        "length": 3200,
        "sky_top": (48, 18, 18),
        "sky_bottom": (90, 30, 20),
        "ground": (60, 30, 28),
        "ground_dark": (38, 18, 16),
        "accent": (255, 120, 40),
        "decor": "volcano",
        "seed": 303,
    },
    {
        "id": "ice_kingdom",
        "name": "Ice Kingdom",
        "difficulty": 3,
        "length": 3200,
        "sky_top": (150, 200, 235),
        "sky_bottom": (225, 245, 255),
        "ground": (200, 225, 240),
        "ground_dark": (160, 195, 220),
        "accent": (140, 220, 255),
        "decor": "ice",
        "seed": 404,
    },
    {
        "id": "ancient_temple",
        "name": "Ancient Temple",
        "difficulty": 4,
        "length": 3500,
        "sky_top": (60, 42, 26),
        "sky_bottom": (110, 80, 46),
        "ground": (120, 100, 70),
        "ground_dark": (86, 70, 48),
        "accent": (255, 180, 90),
        "decor": "temple",
        "seed": 505,
    },
    {
        "id": "cyber_city",
        "name": "Cyber City",
        "difficulty": 4,
        "length": 3600,
        "sky_top": (12, 10, 28),
        "sky_bottom": (30, 14, 46),
        "ground": (26, 22, 44),
        "ground_dark": (16, 14, 30),
        "accent": (255, 60, 210),
        "decor": "cyber",
        "seed": 606,
    },
    {
        "id": "space_station",
        "name": "Space Station",
        "difficulty": 5,
        "length": 3800,
        "sky_top": (4, 4, 14),
        "sky_bottom": (12, 10, 30),
        "ground": (70, 74, 90),
        "ground_dark": (46, 50, 64),
        "accent": (150, 220, 255),
        "decor": "space",
        "seed": 707,
    },
]

WORLD_BY_ID = {w["id"]: w for w in WORLDS}