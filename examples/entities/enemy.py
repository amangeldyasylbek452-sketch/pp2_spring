"""entities/enemy.py — minimal enemy base class for the example game."""
from __future__ import annotations
import pygame
from .entity import Entity


class DummyFSM:
    def __init__(self) -> None:
        self.state = "idle"

    def update(self, dt: float) -> None:
        pass


class Enemy(Entity):
    def __init__(self, game, x: float, y: float, w: int, h: int, health: int = 100) -> None:
        super().__init__(game, x, y, w, h)
        self.health = health
        self.max_health = health
        self.hit_cooldown = 0.0
        self.stagger_flash = 0.0
        self.dead_timer = 0.0
        self.fsm = DummyFSM()
        self.is_boss = False

    def move_patrol(self, dt: float) -> None:
        self.vel.x = getattr(self, "move_speed", 120) * self.facing * 0.35

    def take_damage(self, amount: float, crit: bool = False, knockback: float = 0.0) -> None:
        self.health -= amount
        self.hit_cooldown = 0.18
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.dead_timer = 0.0
            self.set_anim("death", fps=6)
        else:
            self.set_anim("hurt", fps=10)
