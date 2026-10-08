"""Minimal STELLAR KINGDOM Game class for the Mario package."""
from __future__ import annotations
import pygame
import random
from particles import ParticleSystem
from asset import make_player_surf
from convig import SCREEN_W, SCREEN_H, FPS, TILE, GRAVITY, MAX_FALL, PLAYER_SPEED, JUMP_FORCE, DEEP_SPACE, WHITE


class Game:
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock) -> None:
        self.screen = screen
        self.clock = clock
        self.running = True
        self.player_pos = pygame.Vector2(120.0, SCREEN_H - 140.0)
        self.player_vel = pygame.Vector2(0.0, 0.0)
        self.on_ground = False
        self.particles = ParticleSystem()
        self.frame = 0
        self.font = pygame.font.SysFont(None, 24)

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._draw()
        pygame.quit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE and self.on_ground:
                    self.player_vel.y = JUMP_FORCE
                    self.on_ground = False
                    self.particles.dust(self.player_pos.x + 16, self.player_pos.y + 52, -1 if self.player_vel.x < 0 else 1)

    def _update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        move = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move += 1

        self.player_vel.x += move * PLAYER_SPEED * 45 * dt
        self.player_vel.x *= 0.88
        self.player_vel.y = min(self.player_vel.y + GRAVITY, MAX_FALL)

        self.player_pos += self.player_vel
        if self.player_pos.x < 0:
            self.player_pos.x = 0
            self.player_vel.x = 0
        elif self.player_pos.x > SCREEN_W - 32:
            self.player_pos.x = SCREEN_W - 32
            self.player_vel.x = 0

        ground_y = SCREEN_H - 96
        if self.player_pos.y >= ground_y:
            self.player_pos.y = ground_y
            self.player_vel.y = 0
            self.on_ground = True
        else:
            self.on_ground = False

        if move != 0 and self.on_ground:
            self.particles.dust(self.player_pos.x + 18, self.player_pos.y + 56, move)

        self.particles.update()
        self.frame = (self.frame + 1) % 12

    def _draw(self) -> None:
        self.screen.fill(DEEP_SPACE)
        pygame.draw.rect(self.screen, (25, 35, 75), (0, SCREEN_H - 96, SCREEN_W, 96))
        for x in range(0, SCREEN_W, TILE):
            pygame.draw.rect(self.screen, (35, 50, 90), (x, SCREEN_H - 96, TILE - 1, 96))

        player_surf = make_player_surf((self.frame // 2) % 6)
        self.screen.blit(player_surf, (self.player_pos.x, self.player_pos.y))
        self.particles.draw(self.screen, 0.0, 0.0)

        fps_text = self.font.render(f"FPS: {int(self.clock.get_fps())}", True, WHITE)
        self.screen.blit(fps_text, (16, 16))
        pygame.display.flip()
