"""
particles.py
------------
Particle system and drawing helpers used during gameplay.
"""

import math
import random
import pygame
from constants import BALL_COLOR, BALL_OUTLINE, COIN_COLOR, COIN_SPARKLE, POWERUP_COLORS, SCREEN_WIDTH, SCREEN_HEIGHT

class Particle:
    def __init__(self, x, y, vx, vy, radius, color, life, fade=True):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = radius
        self.color = color
        self.life = life
        self.fade = fade
        self.age = 0.0

    def update(self, dt):
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.fade:
            self.radius = max(0, self.radius - dt * 4)

    def is_alive(self):
        return self.age < self.life and self.radius > 0

    def draw(self, surface, cam_x, cam_y):
        if self.radius <= 0:
            return
        pos = (int(self.x - cam_x), int(self.y - cam_y))
        alpha = int(255 * max(0.0, 1.0 - self.age / self.life)) if self.fade else 255
        surf = pygame.Surface((int(self.radius * 2 + 2), int(self.radius * 2 + 2)), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, alpha), (int(self.radius + 1), int(self.radius + 1)), int(self.radius))
        surface.blit(surf, (pos[0] - int(self.radius), pos[1] - int(self.radius)))


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def update(self, dt):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.is_alive()]

    def draw(self, surface, cam_x, cam_y):
        for p in self.particles:
            p.draw(surface, cam_x, cam_y)

    def coin_sparkle(self, x, y):
        for i in range(8):
            self.particles.append(Particle(
                x + random.uniform(-5, 5),
                y + random.uniform(-5, 5),
                random.uniform(-30, 30),
                random.uniform(-80, -20),
                random.uniform(2, 4),
                COIN_SPARKLE,
                0.45,
            ))

    def powerup_burst(self, x, y, color):
        for i in range(12):
            self.particles.append(Particle(
                x + random.uniform(-8, 8),
                y + random.uniform(-8, 8),
                random.uniform(-90, 90),
                random.uniform(-120, -40),
                random.uniform(3, 5),
                color,
                0.65,
            ))

    def lava_death_burst(self, x, y):
        for i in range(18):
            self.particles.append(Particle(
                x + random.uniform(-12, 12),
                y + random.uniform(-12, 12),
                random.uniform(-60, 60),
                random.uniform(-140, -40),
                random.uniform(3, 6),
                (255, 120, 40),
                0.85,
            ))

    def lava_bubble(self, x, y):
        self.particles.append(Particle(
            x + random.uniform(-12, 12),
            y + random.uniform(-4, 4),
            random.uniform(-10, 10),
            random.uniform(-50, -20),
            random.uniform(4, 7),
            (255, 180, 80),
            1.4,
            fade=True,
        ))
