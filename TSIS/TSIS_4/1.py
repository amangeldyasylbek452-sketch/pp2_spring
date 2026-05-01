import json
import os
import random
import sys
import pygame
from configparser import ConfigParser
from datetime import datetime

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    psycopg2 = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.path.join(BASE_DIR, "settings.json")
DB_CONFIG_PATH = os.path.join(BASE_DIR, "database.ini")
FALLBACK_DB_PATH = os.path.join(BASE_DIR, "fallback_leaderboard.json")
BACKGROUND_MUSIC_PATH = os.path.join(BASE_DIR, "music.mp3")

SCREEN_WIDTH = 760
SCREEN_HEIGHT = 760
PLAY_AREA = pygame.Rect(60, 60, 640, 640)
CELL_SIZE = 20
GRID_COLS = PLAY_AREA.width // CELL_SIZE
GRID_ROWS = PLAY_AREA.height // CELL_SIZE

WHITE = (245, 245, 245)
GRAY = (90, 90, 90)
DARK_GRAY = (40, 40, 40)
BLACK = (18, 18, 18)
GREEN = (80, 200, 80)
RED = (220, 50, 50)
DARK_RED = (150, 20, 20)
GOLD = (250, 215, 75)
BLUE = (70, 120, 225)
YELLOW = (235, 210, 85)

DEFAULT_SETTINGS = {
    "snake_color": [50, 200, 50],
    "grid": True,
    "sound": True,
    "username": "",
}

POWERUP_TYPES = ["speed_boost", "slow_motion", "shield"]
POWERUP_COLORS = {
    "speed_boost": (70, 190, 240),
    "slow_motion": (140, 80, 220),
    "shield": (240, 170, 50),
}

pygame.init()
audio_available = True
try:
    pygame.mixer.init()
except Exception:
    audio_available = False

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("SNAKI SNAKI")
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 22)
title_font = pygame.font.SysFont(None, 48)
large_font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 18)

button_sound = None
if audio_available:
    if os.path.exists(BACKGROUND_MUSIC_PATH):
        try:
            button_sound = pygame.mixer.Sound(BACKGROUND_MUSIC_PATH)
        except Exception:
            button_sound = None
        try:
            pygame.mixer.music.load(BACKGROUND_MUSIC_PATH)
            pygame.mixer.music.set_volume(0.45)
        except Exception:
            pass


def load_settings():
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)
                return {**DEFAULT_SETTINGS, **data}
        except Exception:
            pass
    save_settings(DEFAULT_SETTINGS)
    return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    with open(SETTINGS_PATH, "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=2)


def load_fallback_leaderboard():
    if os.path.exists(FALLBACK_DB_PATH):
        try:
            with open(FALLBACK_DB_PATH, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            pass
    return []


def save_fallback_leaderboard(records):
    with open(FALLBACK_DB_PATH, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=2, default=str)


class DatabaseManager:
    def __init__(self):
        self.connected = False
        self.connection = None
        self.fallback_data = load_fallback_leaderboard()
        self.error = None
        if psycopg2 is None:
            self.error = "psycopg2 not installed"
            return

        if not os.path.exists(DB_CONFIG_PATH):
            self.error = "Missing database.ini"
            return

        try:
            config = self.load_db_config()
            self.connection = psycopg2.connect(**config)
            self.connection.autocommit = True
            self.ensure_tables()
            self.connected = True
        except Exception as error:
            self.error = str(error)

    def load_db_config(self):
        parser = ConfigParser()
        parser.read(DB_CONFIG_PATH)
        if parser.has_section("postgresql"):
            return {key: value for key, value in parser.items("postgresql")}
        raise FileNotFoundError("Section [postgresql] missing in database.ini")

    def ensure_tables(self):
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS players (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS game_sessions (
                    id SERIAL PRIMARY KEY,
                    player_id INTEGER REFERENCES players(id),
                    score INTEGER NOT NULL,
                    level_reached INTEGER NOT NULL,
                    played_at TIMESTAMP DEFAULT NOW()
                )
                """
            )

    def get_player_id(self, username):
        if not self.connected:
            return None
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO players (username) VALUES (%s) ON CONFLICT (username) DO NOTHING",
                (username,),
            )
            cursor.execute("SELECT id FROM players WHERE username = %s", (username,))
            row = cursor.fetchone()
            return row[0] if row else None

    def get_personal_best(self, username):
        if not self.connected:
            return self.get_personal_best_fallback(username)
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT MAX(score) FROM game_sessions g JOIN players p ON g.player_id = p.id WHERE p.username = %s",
                (username,),
            )
            row = cursor.fetchone()
            return row[0] or 0

    def save_game_session(self, username, score, level_reached):
        if self.connected:
            player_id = self.get_player_id(username)
            if player_id is None:
                return
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s, %s, %s)",
                    (player_id, score, level_reached),
                )
        else:
            self.save_game_session_fallback(username, score, level_reached)

    def get_top_scores(self):
        if self.connected:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT p.username, g.score, g.level_reached, g.played_at
                    FROM game_sessions g
                    JOIN players p ON g.player_id = p.id
                    ORDER BY g.score DESC, g.played_at ASC
                    LIMIT 10
                    """
                )
                return cursor.fetchall()
        return sorted(self.fallback_data, key=lambda item: item["score"], reverse=True)[:10]

    def get_personal_best_fallback(self, username):
        records = [item for item in self.fallback_data if item["username"] == username]
        if not records:
            return 0
        return max(record["score"] for record in records)

    def save_game_session_fallback(self, username, score, level_reached):
        record = {
            "username": username,
            "score": score,
            "level_reached": level_reached,
            "played_at": datetime.now().isoformat(sep=" ", timespec="seconds"),
        }
        self.fallback_data.insert(0, record)
        self.fallback_data = sorted(self.fallback_data, key=lambda item: item["score"], reverse=True)[:100]
        save_fallback_leaderboard(self.fallback_data)


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


class Button:
    def __init__(self, text, rect, enabled=True):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.enabled = enabled

    def draw(self, surface, mouse_pos):
        hovered = self.rect.collidepoint(mouse_pos) and self.enabled
        color = (200, 200, 200) if hovered else (160, 160, 160)
        outline = (255, 255, 255) if hovered else BLACK
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, outline, self.rect, 2)
        draw_text(self.text, self.rect.centerx, self.rect.centery, BLACK, True, font)

    def clicked(self, mouse_pos):
        return self.enabled and self.rect.collidepoint(mouse_pos)


def draw_text(text, x, y, color=WHITE, center=False, font_obj=None):
    font_obj = font_obj or font
    surface = font_obj.render(str(text), True, color)
    rect = surface.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surface, rect)
    return rect


def draw_grid():
    for x in range(GRID_COLS + 1):
        start = (PLAY_AREA.left + x * CELL_SIZE, PLAY_AREA.top)
        end = (PLAY_AREA.left + x * CELL_SIZE, PLAY_AREA.bottom)
        pygame.draw.line(screen, DARK_GRAY, start, end)
    for y in range(GRID_ROWS + 1):
        start = (PLAY_AREA.left, PLAY_AREA.top + y * CELL_SIZE)
        end = (PLAY_AREA.right, PLAY_AREA.top + y * CELL_SIZE)
        pygame.draw.line(screen, DARK_GRAY, start, end)


def grid_to_rect(position):
    x, y = position
    return pygame.Rect(
        PLAY_AREA.left + x * CELL_SIZE,
        PLAY_AREA.top + y * CELL_SIZE,
        CELL_SIZE,
        CELL_SIZE,
    )


def random_grid_position(exclude):
    while True:
        pos = (random.randrange(GRID_COLS), random.randrange(GRID_ROWS))
        if pos not in exclude:
            return pos


def positions_around(position, radius=1):
    x, y = position
    positions = set()
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            if dx == 0 and dy == 0:
                continue
            candidate = (x + dx, y + dy)
            if 0 <= candidate[0] < GRID_COLS and 0 <= candidate[1] < GRID_ROWS:
                positions.add(candidate)
    return positions


def generate_obstacles(snake_positions, level):
    candidate_positions = [
        (x, y)
        for x in range(GRID_COLS)
        for y in range(GRID_ROWS)
        if (x, y) not in snake_positions
        and (x, y) not in positions_around(snake_positions[0], 2)
    ]
    random.shuffle(candidate_positions)
    count = min(4 + level * 2, len(candidate_positions) // 4)
    obstacles = set()
    for pos in candidate_positions:
        if len(obstacles) >= count:
            break
        nearby = sum(1 for adjacent in [
            (pos[0] + dx, pos[1] + dy)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
        ] if adjacent in obstacles or not (0 <= adjacent[0] < GRID_COLS and 0 <= adjacent[1] < GRID_ROWS))
        if nearby >= 3:
            continue
        if any(abs(pos[0] - p[0]) <= 1 and abs(pos[1] - p[1]) <= 1 for p in snake_positions[:3]):
            continue
        obstacles.add(pos)
    return obstacles


def spawn_food(exclude):
    return random_grid_position(exclude)


def spawn_powerup(exclude):
    return random_grid_position(exclude)


def apply_powerup(state, powerup_type):
    now = pygame.time.get_ticks()
    if powerup_type == "speed_boost":
        state["powerup_active"] = "speed_boost"
        state["powerup_expires_at"] = now + 5000
        state["speed_modifier"] = 5
    elif powerup_type == "slow_motion":
        state["powerup_active"] = "slow_motion"
        state["powerup_expires_at"] = now + 5000
        state["speed_modifier"] = -3
    elif powerup_type == "shield":
        state["powerup_active"] = "shield"
        state["powerup_expires_at"] = None
        state["shield_active"] = True


def clamp_color(rgb):
    return [clamp(rgb[0], 0, 255), clamp(rgb[1], 0, 255), clamp(rgb[2], 0, 255)]


def format_scoreboard(records):
    lines = []
    for index, record in enumerate(records, 1):
        dt = record.get("played_at")
        if isinstance(dt, datetime):
            dt = dt.strftime("%Y-%m-%d %H:%M")
        lines.append((index, record["username"], record["score"], record["level_reached"], dt))
    return lines


def draw_top_border():
    pygame.draw.rect(screen, DARK_GRAY, PLAY_AREA, 4)


def play_sound(sound):
    if sound and settings.get("sound", True):
        try:
            sound.play()
        except Exception:
            pass


def main():
    global settings
    db_manager = DatabaseManager()
    settings = load_settings()

    if audio_available and settings.get("sound", True):
        try:
            pygame.mixer.music.play(-1)
        except Exception:
            pass

    username = settings.get("username", "")[:16]
    username_active = False
    warning_text = ""

    menu_buttons = [
        Button("Play", (520, 140, 160, 50)),
        Button("Leaderboard", (520, 210, 160, 50)),
        Button("Settings", (520, 280, 160, 50)),
        Button("Quit", (520, 350, 160, 50)),
    ]
    leaderboard_back = Button("Back", (520, 680, 160, 50))
    settings_save = Button("Save & Back", (520, 680, 160, 50))
    game_over_retry = Button("Retry", (220, 620, 160, 50))
    game_over_menu = Button("Main Menu", (380, 620, 160, 50))

    r_plus = Button("R+", (520, 170, 70, 40))
    r_minus = Button("R-", (610, 170, 70, 40))
    g_plus = Button("G+", (520, 230, 70, 40))
    g_minus = Button("G-", (610, 230, 70, 40))
    b_plus = Button("B+", (520, 290, 70, 40))
    b_minus = Button("B-", (610, 290, 70, 40))
    grid_toggle = Button("Toggle Grid", (520, 350, 160, 50))
    sound_toggle = Button("Toggle Sound", (520, 420, 160, 50))

    state = "menu"
    clock_tick = pygame.time.Clock()

    game_state = None
    personal_best = db_manager.get_personal_best(username) if username else 0
    if not db_manager.connected:
        warning_text = f"DB unavailable: {db_manager.error or 'fallback mode'}"

    def new_game():
        nonlocal game_state
        now = pygame.time.get_ticks()
        food_pos = None
        poison_pos = None
        powerup_item = None
        obstacles = set()

        snake = [
            (GRID_COLS // 2, GRID_ROWS // 2),
            (GRID_COLS // 2 - 1, GRID_ROWS // 2),
            (GRID_COLS // 2 - 2, GRID_ROWS // 2),
        ]
        direction = (1, 0)
        score = 0
        level = 1
        last_move = now
        speed_modifier = 0
        powerup_active = None
        powerup_expires_at = None
        shield_active = False
        next_poison_spawn = now + 8000
        next_powerup_spawn = now + 12000
        food_pos = spawn_food(set(snake))
        return {
            "snake": snake,
            "direction": direction,
            "score": score,
            "level": level,
            "last_move": last_move,
            "base_speed": 9,
            "speed_modifier": speed_modifier,
            "powerup_active": powerup_active,
            "powerup_expires_at": powerup_expires_at,
            "shield_active": shield_active,
            "food_pos": food_pos,
            "poison_pos": poison_pos,
            "powerup_item": powerup_item,
            "powerup_spawn_at": next_powerup_spawn,
            "poison_spawn_at": next_poison_spawn,
            "obstacles": obstacles,
            "game_over": False,
            "game_over_reason": "",
            "level_up_score": 60,
            "score_to_next_level": 60,
            "food_eaten": 0,
        }

    def restart_game():
        nonlocal game_state
        game_state = new_game()

    restart_game()

    def place_obstacles():
        nonlocal game_state
        if game_state["level"] < 3:
            game_state["obstacles"] = set()
            return
        snake_positions = set(game_state["snake"])
        obstacles = generate_obstacles(list(game_state["snake"]), game_state["level"])
        if not obstacles:
            obstacles = set()
        game_state["obstacles"] = obstacles

    def reset_level_data():
        nonlocal game_state
        place_obstacles()
        forbidden = set(game_state["snake"]) | game_state["obstacles"]
        if game_state["food_pos"] in forbidden:
            game_state["food_pos"] = spawn_food(forbidden)
        if game_state["poison_pos"] in forbidden:
            game_state["poison_pos"] = None
        if game_state["powerup_item"] and game_state["powerup_item"]["pos"] in forbidden:
            game_state["powerup_item"] = None

    def spawn_missing_items():
        nonlocal game_state
        forbidden = set(game_state["snake"]) | game_state["obstacles"]
        if game_state["food_pos"] is None:
            game_state["food_pos"] = spawn_food(forbidden)
        if game_state["poison_pos"] is None and pygame.time.get_ticks() >= game_state["poison_spawn_at"]:
            game_state["poison_pos"] = spawn_food(forbidden)
        if game_state["powerup_item"] is None and pygame.time.get_ticks() >= game_state["powerup_spawn_at"]:
            powerup_type = random.choice(POWERUP_TYPES)
            position = spawn_powerup(forbidden | {game_state["food_pos"], game_state["poison_pos"]})
            game_state["powerup_item"] = {"type": powerup_type, "pos": position, "spawned_at": pygame.time.get_ticks()}

    def update_speed():
        if game_state["powerup_active"] in ("speed_boost", "slow_motion") and game_state["powerup_expires_at"]:
            if pygame.time.get_ticks() >= game_state["powerup_expires_at"]:
                game_state["powerup_active"] = None
                game_state["speed_modifier"] = 0
        game_state["current_speed"] = clamp(game_state["base_speed"] + game_state["speed_modifier"], 4, 18)

    def game_over(reason):
        nonlocal state, personal_best
        if not game_state["game_over"]:
            game_state["game_over"] = True
            game_state["game_over_reason"] = reason
            if username:
                db_manager.save_game_session(username, game_state["score"], game_state["level"])
                personal_best = db_manager.get_personal_best(username)
            else:
                personal_best = max(personal_best, game_state["score"])
            play_sound(button_sound)
            state = "game_over"

    def move_snake():
        head_x, head_y = game_state["snake"][0]
        dx, dy = game_state["direction"]
        new_head = (head_x + dx, head_y + dy)
        if not (0 <= new_head[0] < GRID_COLS and 0 <= new_head[1] < GRID_ROWS):
            if game_state["shield_active"]:
                game_state["shield_active"] = False
                game_state["powerup_active"] = None
                game_state["speed_modifier"] = 0
                return
            game_over("Hit wall")
            return
        if new_head in game_state["obstacles"]:
            game_over("Hit obstacle")
            return
        if new_head in game_state["snake"]:
            if game_state["shield_active"]:
                game_state["shield_active"] = False
                game_state["powerup_active"] = None
                game_state["speed_modifier"] = 0
            else:
                game_over("Ran into self")
                return
        game_state["snake"].insert(0, new_head)
        ate_food = new_head == game_state["food_pos"]
        ate_poison = new_head == game_state["poison_pos"]
        ate_powerup = game_state["powerup_item"] and new_head == game_state["powerup_item"]["pos"]

        if ate_food:
            game_state["score"] += 10
            game_state["food_eaten"] += 1
            game_state["food_pos"] = None
        if ate_poison:
            game_state["poison_pos"] = None
            game_state["snake"].pop()
            if len(game_state["snake"]) > 1:
                game_state["snake"].pop()
            if len(game_state["snake"]) <= 1:
                game_over("Poison killed you")
                return
            game_state["score"] = max(0, game_state["score"] - 5)
        if ate_powerup:
            apply_powerup(game_state, game_state["powerup_item"]["type"])
            game_state["powerup_item"] = None
            game_state["powerup_spawn_at"] = pygame.time.get_ticks() + 12000

        if not ate_food:
            if not ate_poison:
                game_state["snake"].pop()
        else:
            if game_state["food_eaten"] and game_state["food_eaten"] % 6 == 0:
                game_state["level"] += 1
                game_state["base_speed"] += 1
                place_obstacles()

    def draw_play_state():
        screen.fill(BLACK)
        pygame.draw.rect(screen, DARK_GRAY, (0, 0, SCREEN_WIDTH, 50))
        draw_text("Snake Game", 20, 14, GOLD, False, large_font)
        draw_text(f"Player: {username or 'Guest'}", 20, 42, WHITE)
        draw_text(f"Score: {game_state['score']}", 220, 14, WHITE)
        draw_text(f"Level: {game_state['level']}", 220, 42, WHITE)
        draw_text(f"Personal best: {personal_best}", 380, 14, WHITE)
        if game_state["shield_active"]:
            draw_text("Shield Active", 380, 42, BLUE)
        if game_state["powerup_active"] in ("speed_boost", "slow_motion"):
            draw_text(f"Power-up: {game_state['powerup_active'].replace('_', ' ').title()}", 520, 14, WHITE)
        pygame.draw.rect(screen, WHITE, PLAY_AREA, 4)
        if settings["grid"]:
            draw_grid()

        for pos in game_state["obstacles"]:
            pygame.draw.rect(screen, GRAY, grid_to_rect(pos))

        for segment in game_state["snake"]:
            pygame.draw.rect(screen, settings["snake_color"], grid_to_rect(segment))
        if game_state["food_pos"]:
            pygame.draw.rect(screen, YELLOW, grid_to_rect(game_state["food_pos"]))
        if game_state["poison_pos"]:
            pygame.draw.rect(screen, DARK_RED, grid_to_rect(game_state["poison_pos"]))
        if game_state["powerup_item"]:
            powerup_color = POWERUP_COLORS[game_state["powerup_item"]["type"]]
            pygame.draw.rect(screen, powerup_color, grid_to_rect(game_state["powerup_item"]["pos"]))

    def draw_menu_state():
        screen.fill((18, 18, 18))
        draw_text("Snake Leaderboard", SCREEN_WIDTH // 2, 60, GOLD, True, title_font)
        draw_text("Enter username and press Play", SCREEN_WIDTH // 2, 120, WHITE, True)
        input_rect = pygame.Rect(180, 170, 320, 50)
        pygame.draw.rect(screen, DARK_GRAY, input_rect)
        pygame.draw.rect(screen, WHITE if username_active else GRAY, input_rect, 2)
        draw_text(username or "Type username...", input_rect.left + 12, input_rect.top + 14, WHITE if username else GRAY, False, large_font)
        if warning_text:
            draw_text(warning_text, SCREEN_WIDTH // 2, 230, RED, True)
        if db_manager.connected:
            draw_text("Connected to PostgreSQL", 520, 20, GREEN, False, small_font)
        else:
            draw_text("Fallback local leaderboard active", 520, 20, RED, False, small_font)
        for button in menu_buttons:
            button.draw(screen, pygame.mouse.get_pos())

    def draw_leaderboard_state():
        screen.fill((8, 18, 38))
        draw_text("Leaderboard", SCREEN_WIDTH // 2, 40, GOLD, True, title_font)
        columns = [(140, "Rank"), (260, "Username"), (420, "Score"), (520, "Level"), (620, "Date")]
        for x, title in columns:
            draw_text(title, x, 90, WHITE, True)
        scores = db_manager.get_top_scores()
        for index, entry in enumerate(scores[:10], start=1):
            date_value = entry["played_at"]
            if isinstance(date_value, datetime):
                date_value = date_value.strftime("%Y-%m-%d")
            draw_text(str(index), 140, 110 + index * 40, WHITE, True)
            draw_text(entry["username"], 260, 110 + index * 40, WHITE, True)
            draw_text(str(entry["score"]), 420, 110 + index * 40, WHITE, True)
            draw_text(str(entry["level_reached"]), 520, 110 + index * 40, WHITE, True)
            draw_text(str(date_value), 620, 110 + index * 40, WHITE, True)
        leaderboard_back.draw(screen, pygame.mouse.get_pos())

    def draw_settings_state():
        screen.fill((25, 20, 40))
        draw_text("Settings", SCREEN_WIDTH // 2, 40, GOLD, True, title_font)
        draw_text(f"Grid overlay: {'On' if settings['grid'] else 'Off'}", 520, 140, WHITE)
        draw_text(f"Sound: {'On' if settings['sound'] else 'Off'}", 520, 210, WHITE)
        draw_text("Snake color", 520, 280, WHITE)
        pygame.draw.rect(screen, tuple(settings["snake_color"]), pygame.Rect(520, 320, 160, 80))
        r_plus.draw(screen, pygame.mouse.get_pos())
        r_minus.draw(screen, pygame.mouse.get_pos())
        g_plus.draw(screen, pygame.mouse.get_pos())
        g_minus.draw(screen, pygame.mouse.get_pos())
        b_plus.draw(screen, pygame.mouse.get_pos())
        b_minus.draw(screen, pygame.mouse.get_pos())
        draw_text(f"R: {settings['snake_color'][0]}", 520, 170, WHITE)
        draw_text(f"G: {settings['snake_color'][1]}", 520, 230, WHITE)
        draw_text(f"B: {settings['snake_color'][2]}", 520, 290, WHITE)
        grid_toggle.text = f"Grid: {'On' if settings['grid'] else 'Off'}"
        sound_toggle.text = f"Sound: {'On' if settings['sound'] else 'Off'}"
        grid_toggle.draw(screen, pygame.mouse.get_pos())
        sound_toggle.draw(screen, pygame.mouse.get_pos())
        settings_save.draw(screen, pygame.mouse.get_pos())

    def draw_game_over_state():
        screen.fill((10, 10, 10))
        draw_text("Game Over", SCREEN_WIDTH // 2, 80, RED, True, title_font)
        draw_text(f"Score: {game_state['score']}", SCREEN_WIDTH // 2, 160, WHITE, True, large_font)
        draw_text(f"Level reached: {game_state['level']}", SCREEN_WIDTH // 2, 210, WHITE, True, large_font)
        draw_text(f"Personal best: {personal_best}", SCREEN_WIDTH // 2, 260, WHITE, True, large_font)
        draw_text(f"Reason: {game_state['game_over_reason']}", SCREEN_WIDTH // 2, 310, GRAY, True, font)
        game_over_retry.draw(screen, pygame.mouse.get_pos())
        game_over_menu.draw(screen, pygame.mouse.get_pos())

    while True:
        mouse_pos = pygame.mouse.get_pos()
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if state == "menu":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if pygame.Rect(180, 170, 320, 50).collidepoint(mouse_pos):
                        username_active = True
                    else:
                        username_active = False
                    for button in menu_buttons:
                        if button.clicked(mouse_pos):
                            if button.text == "Play":
                                if not username.strip():
                                    warning_text = "Please enter a username first."
                                else:
                                    settings["username"] = username.strip()
                                    save_settings(settings)
                                    personal_best = db_manager.get_personal_best(username.strip())
                                    restart_game()
                                    state = "playing"
                            elif button.text == "Leaderboard":
                                state = "leaderboard"
                            elif button.text == "Settings":
                                state = "settings"
                            elif button.text == "Quit":
                                pygame.quit()
                                sys.exit()
                if event.type == pygame.KEYDOWN and username_active:
                    if event.key == pygame.K_BACKSPACE:
                        username = username[:-1]
                    elif event.key == pygame.K_RETURN:
                        username_active = False
                    elif len(username) < 16 and event.unicode.isprintable():
                        username += event.unicode
                        warning_text = ""
            elif state == "leaderboard":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if leaderboard_back.clicked(mouse_pos):
                        state = "menu"
            elif state == "settings":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    click_pos = event.pos
                    if grid_toggle.clicked(click_pos):
                        settings["grid"] = not settings["grid"]
                        play_sound(button_sound)
                    elif sound_toggle.clicked(click_pos):
                        settings["sound"] = not settings["sound"]
                        if settings["sound"]:
                            try:
                                pygame.mixer.music.play(-1)
                            except Exception:
                                pass
                        else:
                            try:
                                pygame.mixer.music.stop()
                            except Exception:
                                pass
                        play_sound(button_sound)
                    elif settings_save.clicked(mouse_pos):
                        save_settings(settings)
                        state = "menu"
                        play_sound(button_sound)
                    elif r_plus.clicked(mouse_pos):
                        settings["snake_color"][0] = clamp(settings["snake_color"][0] + 15, 0, 255)
                    elif r_minus.clicked(mouse_pos):
                        settings["snake_color"][0] = clamp(settings["snake_color"][0] - 15, 0, 255)
                    elif g_plus.clicked(mouse_pos):
                        settings["snake_color"][1] = clamp(settings["snake_color"][1] + 15, 0, 255)
                    elif g_minus.clicked(mouse_pos):
                        settings["snake_color"][1] = clamp(settings["snake_color"][1] - 15, 0, 255)
                    elif b_plus.clicked(mouse_pos):
                        settings["snake_color"][2] = clamp(settings["snake_color"][2] + 15, 0, 255)
                    elif b_minus.clicked(mouse_pos):
                        settings["snake_color"][2] = clamp(settings["snake_color"][2] - 15, 0, 255)
            elif state == "playing":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and game_state["direction"] != (0, 1):
                        game_state["direction"] = (0, -1)
                    elif event.key == pygame.K_DOWN and game_state["direction"] != (0, -1):
                        game_state["direction"] = (0, 1)
                    elif event.key == pygame.K_LEFT and game_state["direction"] != (1, 0):
                        game_state["direction"] = (-1, 0)
                    elif event.key == pygame.K_RIGHT and game_state["direction"] != (-1, 0):
                        game_state["direction"] = (1, 0)
                    elif event.key == pygame.K_ESCAPE:
                        state = "menu"
            elif state == "game_over":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if game_over_retry.clicked(mouse_pos):
                        restart_game()
                        state = "playing"
                    elif game_over_menu.clicked(mouse_pos):
                        state = "menu"

        if state == "playing" and not game_state["game_over"]:
            update_speed()
            spawn_missing_items()
            if game_state["powerup_item"] and now - game_state["powerup_item"]["spawned_at"] >= 8000:
                game_state["powerup_item"] = None
                game_state["powerup_spawn_at"] = now + 10000
            if now - game_state["last_move"] >= 1000 // game_state["current_speed"]:
                if game_state["direction"]:
                    move_snake()
                    game_state["last_move"] = now
        if state == "playing":
            draw_play_state()
        elif state == "menu":
            draw_menu_state()
        elif state == "leaderboard":
            draw_leaderboard_state()
        elif state == "settings":
            draw_settings_state()
        elif state == "game_over":
            draw_game_over_state()

        pygame.display.flip()
        clock_tick.tick(60)


if __name__ == "__main__":
    main()
