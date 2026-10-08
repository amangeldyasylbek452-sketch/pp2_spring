"""
settings.py - Global constants, configuration, colors, key bindings.
"""
import pygame

# ---------------------------------------------------------------------------
# Window / performance
# ---------------------------------------------------------------------------
SCREEN_W, SCREEN_H = 1280, 720
FPS = 60
TITLE = "The Cursed Kingdom"

# ---------------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------------
KEY_UP = pygame.K_w
KEY_DOWN = pygame.K_s
KEY_LEFT = pygame.K_a
KEY_RIGHT = pygame.K_d
KEY_ATTACK = pygame.K_SPACE
KEY_DASH = pygame.K_LSHIFT
KEY_INTERACT = pygame.K_e
KEY_PAUSE = pygame.K_ESCAPE

# ---------------------------------------------------------------------------
# Color palette (moody medieval-horror pixel palette)
# ---------------------------------------------------------------------------
NIGHT_SKY_TOP = (10, 12, 30)
NIGHT_SKY_BOTTOM = (35, 40, 70)
MOON_COLOR = (200, 210, 255)
FOG_COLOR = (150, 160, 190)
GROUND_DARK = (28, 30, 40)
GROUND_LIGHT = (44, 48, 62)
MOUNTAIN_FAR = (20, 22, 38)
MOUNTAIN_NEAR = (30, 33, 50)
TORCH_ORANGE = (255, 140, 40)
BLOOD_DARK = (90, 10, 10)
UI_GOLD = (212, 175, 55)
UI_BG = (18, 16, 22)
WHITE = (235, 235, 240)
BLACK = (0, 0, 0)
SKIN = (210, 170, 140)
STEEL = (150, 155, 165)
STEEL_DARK = (90, 95, 105)
CLOAK_RED = (120, 20, 30)
BONE = (225, 220, 200)
GHOST_BLUE = (140, 180, 220)

# ---------------------------------------------------------------------------
# Player tuning
# ---------------------------------------------------------------------------
PLAYER_MAX_HP = 100
PLAYER_WALK_SPEED = 140
PLAYER_RUN_SPEED = 240
PLAYER_DASH_SPEED = 620
PLAYER_DASH_TIME = 0.18
PLAYER_DASH_COOLDOWN = 0.9
PLAYER_IFRAME_TIME = 0.6
PLAYER_ATTACK_COOLDOWN = 0.32
PLAYER_COMBO_WINDOW = 0.55
PLAYER_STAMINA_MAX = 100
PLAYER_STAMINA_REGEN = 18  # per second
DASH_STAMINA_COST = 25
ATTACK_STAMINA_COST = 12

TILE = 48

# Paths
DATA_DIR = "data"
SAVE_PATH = f"{DATA_DIR}/save.json"
SETTINGS_PATH = f"{DATA_DIR}/settings.json"