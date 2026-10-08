"""entities/entity.py — base class with physics, animation timing and rects."""
from __future__ import annotations
import pygame
from core.settings import GRAVITY, GROUND_FRICTION, AIR_FRICTION


class Entity:
    def __init__(self, game, x: float, y: float, w: int, h: int) -> None:
        self.game = game
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.w, self.h = w, h
        self.on_ground = False
        self.facing = 1
        self.alive = True
        self.anim_timer = 0.0
        self.anim_frame = 0
        self.anim_action = "idle"
        self.anim_fps = 8

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.pos.x - self.w / 2), int(self.pos.y - self.h), self.w, self.h)

    @property
    def hurtbox(self) -> pygame.Rect:
        return self.rect.inflate(-6, -4)

    def apply_gravity(self, dt: float) -> None:
        if not self.on_ground:
            self.vel.y += GRAVITY * dt
        self.vel.y = min(self.vel.y, 900)

    def apply_friction(self) -> None:
        self.vel.x *= GROUND_FRICTION if self.on_ground else AIR_FRICTION

    def move_and_collide(self, dt: float, solids: list[pygame.Rect]) -> None:
        self.pos.x += self.vel.x * dt
        r = self.rect
        for s in solids:
            if r.colliderect(s):
                if self.vel.x > 0:
                    self.pos.x -= (r.right - s.left)
                elif self.vel.x < 0:
                    self.pos.x += (s.right - r.left)
                r = self.rect

        self.pos.y += self.vel.y * dt
        r = self.rect
        self.on_ground = False
        for s in solids:
            if r.colliderect(s):
                if self.vel.y > 0:
                    self.pos.y -= (r.bottom - s.top)
                    self.vel.y = 0
                    self.on_ground = True
                elif self.vel.y < 0:
                    self.pos.y += (s.bottom - r.top)
                    self.vel.y = 0
                r = self.rect

    def set_anim(self, action: str, fps: int = 8) -> None:
        if self.anim_action != action:
            self.anim_action = action
            self.anim_frame = 0
            self.anim_timer = 0.0
            self.anim_fps = fps

    def tick_anim(self, dt: float, frame_count: int) -> None:
        self.anim_timer += dt
        if self.anim_timer >= 1.0 / self.anim_fps:
            self.anim_timer = 0.0
            self.anim_frame = (self.anim_frame + 1) % max(1, frame_count)
