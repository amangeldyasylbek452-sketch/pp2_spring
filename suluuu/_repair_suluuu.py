from pathlib import Path

root = Path(__file__).resolve().parent
files = {
    "constants.py": '''import os

BASE_DIR = os.path.dirname(__file__)
SOUND_DIR = os.path.join(BASE_DIR, "sounds")

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

BALL_RADIUS = 18
BALL_COLOR = (255, 130, 60)
BALL_OUTLINE = (245, 245, 245)

GRAVITY = 1900.0
MOVE_ACCEL = 3800.0
MAX_MOVE_SPEED = 520.0
FRICTION = 5200.0
AIR_FRICTION = 1400.0
JUMP_VELOCITY = -760.0
DOUBLE_JUMP_VELOCITY = -700.0
HIGH_JUMP_MULTIPLIER = 1.3
MAX_FALL_SPEED = 1400.0
COYOTE_TIME = 0.12
BOUNCE_PLATFORM_MULTIPLIER = 1.25
MAGNET_RADIUS = 180.0

PLATFORM_HEIGHT = 28
PLATFORM_COLOR = (255, 200, 140)
PLATFORM_EDGE = (220, 160, 110)
MOVING_PLATFORM_COLOR = (220, 190, 255)
BOUNCY_PLATFORM_COLOR = (120, 255, 160)
DISAPPEARING_PLATFORM_COLOR = (255, 145, 145)
DISAPPEAR_TIME = 1.8

COIN_RADIUS = 10
COIN_COLOR = (255, 220, 80)
COIN_SPARKLE = (255, 240, 170)

POWERUP_COLORS = {
    "double_jump": (130, 200, 255),
    "slow_lava": (255, 190, 120),
    "high_jump": (200, 140, 255),
    "shield": (135, 255, 210),
    "magnet": (250, 250, 120),
}

SKY_TOP = (25, 28, 62)
SKY_BOTTOM = (35, 60, 115)
STAR_COLOR = (255, 255, 255)
CLOUD_COLOR = (190, 205, 255)

UI_TEXT = (245, 245, 245)
UI_ACCENT = (255, 200, 80)
BUTTON_BG = (40, 50, 80)
BUTTON_HOVER = (82, 105, 175)
BUTTON_BORDER = (240, 240, 255)
''',
    "collectables.py": '''import math
import random
import pygame

from constants import COIN_COLOR, COIN_RADIUS, COIN_SPARKLE, POWERUP_COLORS, SCREEN_WIDTH

POWERUP_DURATION = {
    "double_jump": 8.0,
    "slow_lava": 6.0,
    "high_jump": 6.0,
    "shield": 1.0,
    "magnet": 7.0,
}


class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = COIN_RADIUS
        self.collected = False
        self.bob = random.uniform(0.0, math.pi * 2)

    @property
    def rect(self):
        return pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            int(self.radius * 2),
            int(self.radius * 2),
        )

    def update(self, dt):
        self.bob += dt * 5.0

    def draw(self, surface, cam_x, cam_y):
        if self.collected:
            return
        offset = math.sin(self.bob) * 5
        center = (int(self.x - cam_x), int(self.y + offset - cam_y))
        pygame.draw.circle(surface, COIN_COLOR, center, self.radius)
        pygame.draw.circle(surface, COIN_SPARKLE, center, max(1, self.radius // 2))

    def collect(self):
        if self.collected:
            return False
        self.collected = True
        return True


class PowerUp:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.radius = 16
        self.color = POWERUP_COLORS.get(kind, (255, 255, 255))
        self.bob = random.uniform(0.0, math.pi * 2)

    @property
    def rect(self):
        return pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            int(self.radius * 2),
            int(self.radius * 2),
        )

    def update(self, dt):
        self.bob += dt * 3.0

    def draw(self, surface, cam_x, cam_y):
        offset = math.sin(self.bob) * 6
        center = (int(self.x - cam_x), int(self.y + offset - cam_y))
        pygame.draw.circle(surface, self.color, center, self.radius)
        pygame.draw.circle(surface, (255, 255, 255), center, self.radius, 2)
        text = pygame.font.SysFont("arial", 18, bold=True).render(self.kind[0].upper(), True, (30, 30, 30))
        text_rect = text.get_rect(center=center)
        surface.blit(text, text_rect)

    def apply(self, player):
        if self.kind == "shield":
            player.activate_powerup(self.kind, 0.0)
        else:
            player.activate_powerup(self.kind, POWERUP_DURATION.get(self.kind, 5.0))
        return True
''',
    "level_generator.py": '''import random

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, POWERUP_COLORS
from collectables import Coin, PowerUp
from platforms import MovingPlatform, Platform


class LevelGenerator:
    def __init__(self):
        self.platforms = []
        self.coins = []
        self.powerups = []
        self._generate_initial_layout()

    def _generate_initial_layout(self):
        floor = Platform(
            SCREEN_WIDTH * 0.12,
            SCREEN_HEIGHT - 50,
            SCREEN_WIDTH * 0.76,
            bouncy=False,
            disappearing=False,
        )
        self.platforms.append(floor)

        current_y = SCREEN_HEIGHT - 170
        for index in range(28):
            width = random.randint(140, 260)
            x = random.randint(40, SCREEN_WIDTH - width - 40)
            current_y -= random.randint(120, 165)
            bouncy = (index % 7 == 0)
            disappearing = (index % 6 == 0)

            if index % 5 == 0:
                platform = MovingPlatform(
                    x, current_y, width, range_px=120, speed=1.1,
                    bouncy=bouncy, disappearing=disappearing,
                )
            else:
                platform = Platform(x, current_y, width,
                                    bouncy=bouncy, disappearing=disappearing)

            self.platforms.append(platform)
            self._spawn_coin(platform)
            self._spawn_powerup(platform)

    def _spawn_coin(self, platform):
        if random.random() < 0.64:
            coin_x = platform.x + platform.width * 0.5
            coin_y = platform.y - 30
            self.coins.append(Coin(coin_x, coin_y))

    def _spawn_powerup(self, platform):
        if random.random() < 0.14:
            kind = random.choice(list(POWERUP_COLORS.keys()))
            powerup_x = min(SCREEN_WIDTH - 40, max(40, platform.x + platform.width * 0.5))
            powerup_y = platform.y - 42
            self.powerups.append(PowerUp(powerup_x, powerup_y, kind))
''',
    "lava.py": '''import math
import pygame

from constants import SCREEN_WIDTH, SCREEN_HEIGHT


class Lava:
    def __init__(self):
        self.y = SCREEN_HEIGHT + 140
        self.rise_rate = 26.0
        self.color = (255, 105, 40)
        self.wave_time = 0.0

    def update(self, dt, slow=False):
        self.wave_time += dt * 3.4
        speed = self.rise_rate * (0.45 if slow else 1.0)
        self.y -= speed * dt

    def draw(self, surface, cam_x, cam_y):
        top = self.y - cam_y
        lava_rect = pygame.Rect(0, top, SCREEN_WIDTH, SCREEN_HEIGHT - top)
        pygame.draw.rect(surface, self.color, lava_rect)

        wave = 16 + math.sin(self.wave_time) * 7
        points = []
        for x in range(0, SCREEN_WIDTH + 120, 80):
            points.append((x - cam_x % 80, top + wave + math.sin((x + self.wave_time * 30) * 0.04) * 16))
        points.insert(0, (0, top + SCREEN_HEIGHT))
        points.append((SCREEN_WIDTH, top + SCREEN_HEIGHT))
        pygame.draw.polygon(surface, (255, 155, 65), points)

    def check_death(self, player):
        return player.y + player.radius > self.y
''',
    "game.py": '''import math
import os
import random
import pygame

from constants import FPS, SCREEN_HEIGHT, SCREEN_WIDTH
from achievements import AchievementSystem
from camera import Camera
from collectables import Coin, PowerUp
from lava import Lava
from level_generator import LevelGenerator
from particles import ParticleSystem
from player import Player
from sound_manager import SoundManager
from ui import UI


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Rising Lava Ball")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 18)

        self.ui = UI()
        self.sound = SoundManager()
        self.achievements = AchievementSystem()
        self.score = 0
        self.high_score = 0

        self.state = "menu"
        self.paused = False
        self.fullscreen = False
        self.buttons = {}

        self._reset_run()

    def _reset_run(self):
        self.level = LevelGenerator()
        self.player = Player(SCREEN_WIDTH * 0.5, SCREEN_HEIGHT - 150)
        self.start_y = self.player.y
        self.camera = Camera()
        self.lava = Lava()
        self.particles = ParticleSystem()
        self.coins = 0
        self.combo = 1
        self.powerups_collected = 0
        self.time_survived = 0.0
        self.score = 0
        self.game_over_reason = None
        self.achievements.reset_session_flags()

    def start_game(self):
        self._reset_run()
        self.state = "playing"
        self.paused = False

    def _toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            self.ui.update_background(dt)

            if self.state == "playing" and not self.paused:
                self._update(dt)

            self._draw(dt)

            pygame.display.flip()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    self._toggle_fullscreen()
                if event.key == pygame.K_p:
                    if self.state == "playing":
                        self.paused = not self.paused
                if event.key == pygame.K_ESCAPE:
                    if self.state == "playing":
                        self.paused = not self.paused
                    elif self.state == "game_over":
                        self.state = "menu"
                    else:
                        pygame.quit()
                        raise SystemExit
                if event.key == pygame.K_SPACE and self.state == "playing":
                    self.player.try_jump(self.sound, self.particles)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == "menu":
                    for label, btn in self.buttons.items():
                        if btn.clicked(event.pos, True):
                            if label == "Play":
                                self.start_game()
                            elif label == "Quit":
                                pygame.quit()
                                raise SystemExit
                elif self.state == "game_over":
                    for label, btn in self.buttons.items():
                        if btn.clicked(event.pos, True):
                            if label == "Play Again":
                                self.start_game()
                            elif label == "Main Menu":
                                self.state = "menu"
                            elif label == "Quit":
                                pygame.quit()
                                raise SystemExit
                elif self.state == "paused":
                    for label, btn in self.buttons.items():
                        if btn.clicked(event.pos, True):
                            if label == "Resume":
                                self.paused = False
                            elif label == "Main Menu":
                                self.state = "menu"
                            elif label == "Quit":
                                pygame.quit()
                                raise SystemExit

    def _update(self, dt):
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys, dt)
        self.player.update_timers(dt)
        self.player.apply_physics(dt)

        landed, on_ground = self.player.resolve_platform_collisions(
            self.level.platforms, self.particles, self.sound)
        if landed is not None and hasattr(landed, "delta_x"):
            self.player.x += landed.delta_x

        for platform in self.level.platforms:
            platform.update(dt, platform is landed)

        self._update_collectables(dt)
        self._update_powerups(dt)

        slow_lava = self.player.powerups.get("slow_lava", 0) > 0
        self.lava.update(dt, slow=slow_lava)

        if self.lava.check_death(self.player):
            self._end_run()
            return

        self.camera.follow(self.player)
        self.camera.update(dt)
        self.particles.update(dt)

        self.time_survived += dt
        height = max(0.0, self.start_y - self.player.y)
        self.score = int(self.coins * 12 + height * 0.9 + self.time_survived * 2.5)
        self.high_score = max(self.high_score, height)

        self.achievements.check({
            "coins": self.coins,
            "height": height,
            "time": self.time_survived,
            "powerups_collected": self.powerups_collected,
            "max_combo": self.combo,
        })

    def _update_collectables(self, dt):
        for coin in self.level.coins:
            coin.update(dt)
            if not coin.collected and coin.rect.collidepoint(self.player.x, self.player.y):
                if coin.collect():
                    self.coins += 1
                    self.sound.play("coin")
                    self.particles.coin_sparkle(self.player.x, self.player.y)

    def _update_powerups(self, dt):
        for powerup in list(self.level.powerups):
            powerup.update(dt)
            if powerup.rect.collidepoint(self.player.x, self.player.y):
                powerup.apply(self.player)
                self.level.powerups.remove(powerup)
                self.sound.play("powerup")
                self.powerups_collected += 1

    def _end_run(self):
        self.state = "game_over"
        self.game_over_reason = "Lava"

    def _draw(self, dt):
        self.ui.draw_background(self.screen)

        if self.state == "menu":
            self.buttons = self.ui.draw_main_menu(self.screen)
            for button in self.buttons.values():
                button.draw(self.screen)
        elif self.state == "playing":
            self._draw_playfield()
            self.ui.draw_hud(
                self.screen,
                max(0.0, self.start_y - self.player.y),
                self.time_survived,
                self.coins,
                int(self.high_score),
                self.combo,
                self.player,
            )
            self.ui.draw_toast(self.screen, self.achievements.current_toast)
            if self.paused:
                self.state = "paused"
        elif self.state == "paused":
            self._draw_playfield()
            self.buttons = self.ui.draw_pause_menu(self.screen)
            for button in self.buttons.values():
                button.draw(self.screen)
        elif self.state == "game_over":
            self._draw_playfield()
            self.buttons = self.ui.draw_game_over(
                self.screen,
                max(0.0, self.start_y - self.player.y),
                self.time_survived,
                self.coins,
                self.score,
                int(self.high_score),
                False,
            )
            for button in self.buttons.values():
                button.draw(self.screen)

    def _draw_playfield(self):
        cam_x, cam_y = self.camera.offset
        for platform in self.level.platforms:
            platform.draw(self.screen, cam_x, cam_y)
        for coin in self.level.coins:
            coin.draw(self.screen, cam_x, cam_y)
        for powerup in self.level.powerups:
            powerup.draw(self.screen, cam_x, cam_y)
        self.player.draw(self.screen, cam_x, cam_y)
        self.lava.draw(self.screen, cam_x, cam_y)
        self.particles.draw(self.screen, cam_x, cam_y)
''',
    "README.md": '''# Rising Lava Ball

A lightweight Pygame platform climber where you jump from platform to platform while lava rises from below.

## Run the game

1. Install Pygame:

   pip install pygame

2. Run from the `suluuu` directory:

   python main.py
''',
    "requirements (3).txt": "pygame\n",
    "player.py": '''"
player.py
---------
Player physics, jumping, power-ups, collisions.
"""

import math
import pygame
from constants import (
    BALL_RADIUS, BALL_COLOR, BALL_OUTLINE, GRAVITY, MOVE_ACCEL,
    MAX_MOVE_SPEED, FRICTION, AIR_FRICTION, JUMP_VELOCITY,
    DOUBLE_JUMP_VELOCITY, HIGH_JUMP_MULTIPLIER, MAX_FALL_SPEED,
    COYOTE_TIME, BOUNCE_PLATFORM_MULTIPLIER, MAGNET_RADIUS, SCREEN_WIDTH,
)


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = BALL_RADIUS
        self.alive = True
        self.on_ground = False
        self.can_double_jump = False
        self.jump_buffer = 0.0
        self.coyote_timer = 0.0
        self.max_height_y = y
        self.powerups = {
            'double_jump': 0.0,
            'slow_lava': 0.0,
            'high_jump': 0.0,
            'shield': 0,
            'magnet': 0.0,
        }
        self.contact_platform = None

    def handle_input(self, keys, dt):
        accel = MOVE_ACCEL
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vx -= accel * dt
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vx += accel * dt
        if not (keys[pygame.K_a] or keys[pygame.K_LEFT] or keys[pygame.K_d] or keys[pygame.K_RIGHT]):
            friction = FRICTION if self.on_ground else AIR_FRICTION
            if self.vx > 0:
                self.vx = max(0.0, self.vx - friction * dt)
            elif self.vx < 0:
                self.vx = min(0.0, self.vx + friction * dt)
        self.vx = max(-MAX_MOVE_SPEED, min(MAX_MOVE_SPEED, self.vx))

    def update_timers(self, dt):
        if self.coyote_timer > 0:
            self.coyote_timer = max(0.0, self.coyote_timer - dt)
        for key in ('double_jump', 'slow_lava', 'high_jump', 'magnet'):
            self.powerups[key] = max(0.0, self.powerups[key] - dt)
        if self.powerups['double_jump'] > 0:
            self.can_double_jump = True

    def apply_physics(self, dt):
        self.vy += GRAVITY * dt
        self.vy = min(self.vy, MAX_FALL_SPEED)
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.max_height_y = min(self.max_height_y, self.y)
        if self.x < 0:
            self.x = 0
            self.vx = 0
        elif self.x > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH
            self.vx = 0

    def try_jump(self, sound, particles):
        can_jump = self.on_ground or self.coyote_timer > 0 or self.powerups['double_jump'] > 0
        if not can_jump:
            return
        jump_velocity = JUMP_VELOCITY
        if self.powerups['high_jump'] > 0:
            jump_velocity *= HIGH_JUMP_MULTIPLIER
        if not self.on_ground and self.coyote_timer <= 0:
            self.powerups['double_jump'] = 0.0
            self.can_double_jump = False
        self.vy = jump_velocity
        self.on_ground = False
        self.coyote_timer = 0.0
        if sound:
            sound.play('jump')
        if particles:
            particles.powerup_burst(self.x, self.y, (255, 255, 255))

    def activate_powerup(self, kind, duration):
        if kind == 'shield':
            self.powerups['shield'] += 1
        else:
            self.powerups[kind] = max(self.powerups[kind], duration)
        if kind == 'double_jump':
            self.can_double_jump = True

    def consume_shield(self):
        if self.powerups['shield'] > 0:
            self.powerups['shield'] -= 1
            return True
        return False

    def apply_magnet(self, coins, dt):
        if self.powerups['magnet'] <= 0:
            return
        for coin in coins:
            if coin.collected:
                continue
            dx = self.x - coin.x
            dy = self.y - coin.y
            dist = math.hypot(dx, dy)
            if dist < MAGNET_RADIUS and dist > 0:
                strength = (MAGNET_RADIUS - dist) / MAGNET_RADIUS
                coin.x += dx / dist * 180 * dt * strength
                coin.y += dy / dist * 180 * dt * strength

    def resolve_platform_collisions(self, platforms, particles, sound):
        landed = None
        self.on_ground = False
        self.coyote_timer = max(0.0, self.coyote_timer)
        for platform in platforms:
            if platform.is_gone:
                continue
            rect = pygame.Rect(platform.x, platform.y, platform.width, platform.height)
            if rect.collidepoint(self.x, self.y + self.radius) and self.vy >= 0:
                if self.y + self.radius <= platform.y + 12:
                    self.y = platform.y - self.radius
                    self.vy = 0.0
                    self.on_ground = True
                    self.coyote_timer = COYOTE_TIME
                    landed = platform
                    if platform.bouncy:
                        self.vy = JUMP_VELOCITY * BOUNCE_PLATFORM_MULTIPLIER
                        if sound:
                            sound.play('jump')
                    break
        return landed, self.on_ground

    def draw(self, surface, cam_x, cam_y):
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        pygame.draw.circle(surface, BALL_COLOR, (sx, sy), self.radius)
        pygame.draw.circle(surface, BALL_OUTLINE, (sx, sy), self.radius, 3)
''',
}

for path_name, content in files.items():
    target = root / path_name
    target.write_text(content, encoding="utf-8")
    print(f"Wrote {path_name}")
