"""entities/projectile.py — lightweight ranged-attack projectiles."""
from __future__ import annotations
import pygame


class Projectile:
    def __init__(self, x, y, direction, owner, damage, kind="arrow", speed=520):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(speed * direction, 0)
        self.owner = owner
        self.damage = damage
        self.kind = kind
        self.alive = True
        self.life = 2.2

    def update(self, dt, solids):
        self.pos.x += self.vel.x * dt
        self.life -= dt
        if self.life <= 0:
            self.alive = False
            return
        r = pygame.Rect(int(self.pos.x - 4), int(self.pos.y - 4), 8, 8)
        for s in solids:
            if r.colliderect(s):
                self.alive = False
                return

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.pos.x - 10), int(self.pos.y - 3), 20, 6)

    def draw(self, surf, cam):
        sx, sy = cam.apply((self.pos.x, self.pos.y))
        color = (200, 60, 40) if self.kind == "bone" else (210, 200, 180)
        pygame.draw.line(surf, color, (sx - 10, sy), (sx + 10, sy), 3)
