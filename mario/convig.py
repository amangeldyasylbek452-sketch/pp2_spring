"""Game-wide constants."""

# Screen
SCREEN_W = 1280
SCREEN_H = 720
FPS = 60
TILE = 48

# Physics
GRAVITY = 0.65
MAX_FALL = 22
PLAYER_SPEED = 5.2
PLAYER_ACCEL = 0.9
PLAYER_FRICTION = 0.82
JUMP_FORCE = -15.5
JUMP_BUFFER = 10       # frames
COYOTE_TIME = 8        # frames
WALL_SLIDE_SPEED = 2.0
WALL_JUMP_X = 6.0
WALL_JUMP_Y = -13.0

# Colors
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
DEEP_SPACE = (5,   5,   20)
NEBULA_BLUE= (20,  40,  100)
STAR_WHITE = (220, 230, 255)
GOLD       = (255, 215, 50)
CRYSTAL    = (100, 200, 255)
PLASMA     = (80,  255, 180)
RED        = (220, 60,  60)
GREEN      = (60,  220, 100)
ORANGE     = (255, 160, 30)
PURPLE     = (160, 60,  220)
PINK       = (255, 100, 200)
CYAN       = (0,   220, 255)
YELLOW     = (255, 240, 80)
DARK_BLUE  = (10,  20,  60)
HEALTH_RED = (220, 50,  50)
SHIELD_BLU = (50,  150, 255)
ENERGY_GRN = (50,  220, 120)

# Game states
STATE_MENU    = "menu"
STATE_PLAYING = "playing"
STATE_PAUSED  = "paused"
STATE_GAMEOVER= "gameover"
STATE_WIN     = "win"
STATE_BOSS    = "boss"
STATE_SHOP    = "shop"
STATE_CUTSCENE= "cutscene"

# Tile types
TILE_EMPTY   = 0
TILE_SOLID   = 1
TILE_PLATFORM= 2   # pass-through from below
TILE_SPIKE   = 3
TILE_BOUNCE  = 4
TILE_ICE     = 5
TILE_CONVEYOR_R = 6
TILE_CONVEYOR_L = 7
TILE_LAVA    = 8
TILE_PORTAL_A= 9
TILE_PORTAL_B= 10
TILE_CHECKPOINT=11
TILE_GOAL    = 12
TILE_LOW_GRAV= 13
TILE_MAGNETIC= 14

# Entity categories
CAT_PLAYER = "player"
CAT_ENEMY  = "enemy"
CAT_BULLET = "bullet"
CAT_ITEM   = "item"
CAT_EFFECT = "effect"

# Difficulty multipliers
DIFFICULTY = {
    "easy":      {"enemy_hp": 0.7,  "enemy_dmg": 0.6, "player_hp": 1.4, "checkpoint_freq": 1.5},
    "normal":    {"enemy_hp": 1.0,  "enemy_dmg": 1.0, "player_hp": 1.0, "checkpoint_freq": 1.0},
    "hard":      {"enemy_hp": 1.5,  "enemy_dmg": 1.4, "player_hp": 0.8, "checkpoint_freq": 0.7},
    "nightmare": {"enemy_hp": 2.5,  "enemy_dmg": 2.0, "player_hp": 0.6, "checkpoint_freq": 0.4},
}

LEVEL_NAMES = [
    "Luna Drift — Low Gravity Moon",
    "Crystalis — Frozen Crystal Planet",
    "Station Omega — Abandoned Orbital Platform",
    "Asteroid Gauntlet — The Rock Field",
    "Nebula Shores — Glowing Gas Clouds",
    "Singularity — Black Hole Gravity Zone",
    "Ignis Prime — Volcanic Alien Terrain",
    "Void Citadel — The Dark Emperor's Fortress",
]

BOSS_NAMES = [
    "Arachno-Void — Giant Cosmic Spider",
    "MECH-TITAN — Rogue Battle Robot",
    "Draconis — The Space Dragon",
    "Gravitas — Black Hole Guardian",
    "Emperor Nox — Ruler of the Void",
]