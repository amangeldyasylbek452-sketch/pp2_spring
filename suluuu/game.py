import math
import os
import random
import pygame

from constants import FPS, SCREEN_HEIGHT, SCREEN_WIDTH, JUMP_VELOCITY
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

        self.level.update(self.player.y)

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
            self._bounce_from_lava()

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

    def _bounce_from_lava(self):
        self.player.y = self.lava.y - self.player.radius - 8
        self.player.vy = JUMP_VELOCITY * 0.8
        self.player.on_ground = False
        self.player.powerups['shield'] = max(self.player.powerups['shield'], 1)
        self.particles.lava_death_burst(self.player.x, self.player.y + self.player.radius)
        self.sound.play('jump')

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
