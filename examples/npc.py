"""systems/particles.py — lightweight pooled particle system.

Handles combat feedback (sparks, dust) and atmospheric effects
(rain, embers, fog motes, ghost wisps, falling leaves) using cheap
Vector2-free tuples for performance at large particle counts.
"""
from __future__ import annotations
import random
from dataclasses import dataclass
import pygame


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    kind: str
    gravity: float = 0.0
    fade: bool = True


class ParticleSystem:
    def __init__(self, assets) -> None:
        self.assets = assets
        self.particles: list[Particle] = []
        self.max_particles = 900

    def spawn(self, x, y, kind, count=1, speed=40, spread=360, life=0.6, gravity=0.0):
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                self.particles.pop(0)
            ang = random.uniform(0, spread) - spread / 2
            import math
            rad = math.radians(ang)
            v = random.uniform(speed * 0.4, speed)
            vx = math.cos(rad) * v
            vy = math.sin(rad) * v
            self.particles.append(Particle(x, y, vx, vy, life, life, kind, gravity))

    def spawn_rain(self, cam_x, cam_y, w, h):
        for _ in range(3):
            self.spawn(cam_x + random.uniform(0, w), cam_y + random.uniform(-20, 0),
                       "rain", count=1, speed=0, life=1.6, gravity=0)
            p = self.particles[-1]
            p.vx, p.vy = -40, 480

    def spawn_embers(self, cam_x, cam_y, w, h):
        self.spawn(cam_x + random.uniform(0, w), cam_y + h, "ember", count=1,
                   speed=20, spread=40, life=3.0, gravity=-30)

    def update(self, dt: float) -> None:
        alive = []
        for p in self.particles:
            p.life -= dt
            if p.life <= 0:
                continue
            p.vy += p.gravity * dt
            p.x += p.vx * dt
            p.y += p.vy * dt
            alive.append(p)
        self.particles = alive

    def draw(self, surf: pygame.Surface, cam) -> None:
        for p in self.particles:
            sx, sy = cam.apply((p.x, p.y))
            if -20 < sx < surf.get_width() + 20 and -20 < sy < surf.get_height() + 20:
                img = self.assets.particle(p.kind)
                alpha = int(255 * (p.life / p.max_life)) if p.fade else 255
                img = img.copy()
                img.set_alpha(max(0, min(255, alpha)))
                surf.blit(img, (sx, sy))
