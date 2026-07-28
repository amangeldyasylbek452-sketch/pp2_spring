"""
platforms.py
------------
Platform + MovingPlatform classes. A single Platform can also be flagged as
"bouncy" or "disappearing" - those are behavioural flags rather than
separate subclasses, since they can combine (e.g. a moving+bouncy platform).
MovingPlatform overrides update() to add horizontal oscillation.
"""

import math
import pygame
from constants import (
    PLATFORM_COLOR, PLATFORM_EDGE, MOVING_PLATFORM_COLOR,
    BOUNCY_PLATFORM_COLOR, DISAPPEARING_PLATFORM_COLOR, DISAPPEAR_TIME,
    PLATFORM_HEIGHT,
)


class Platform:
    """A static platform the ball can stand on."""

    def __init__(self, x, y, width, height=PLATFORM_HEIGHT,
                 bouncy=False, disappearing=False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.bouncy = bouncy
        self.disappearing = disappearing

        self.standing_timer = 0.0     # counts up while player stands on it
        self.is_gone = False          # once True, remove from world
        self.shake_amount = 0.0       # visual warning wobble before vanish

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), int(self.width), int(self.height))

    def update(self, dt, player_on_it):
        if self.disappearing and player_on_it and not self.is_gone:
            self.standing_timer += dt
            # start visibly shaking during the last 40% of its life
            warn_start = DISAPPEAR_TIME * 0.6
            if self.standing_timer > warn_start:
                progress = (self.standing_timer - warn_start) / (DISAPPEAR_TIME - warn_start)
                self.shake_amount = progress * 4
            if self.standing_timer >= DISAPPEAR_TIME:
                self.is_gone = True

    def color(self):
        if self.is_gone:
            return PLATFORM_COLOR
        if self.disappearing:
            return DISAPPEARING_PLATFORM_COLOR
        if self.bouncy:
            return BOUNCY_PLATFORM_COLOR
        return PLATFORM_COLOR

    def draw(self, surface, cam_x, cam_y):
        if self.is_gone:
            return
        import random
        wobble_x = random.uniform(-self.shake_amount, self.shake_amount) if self.shake_amount else 0
        rect = pygame.Rect(
            int(self.x - cam_x + wobble_x), int(self.y - cam_y),
            int(self.width), int(self.height),
        )
        pygame.draw.rect(surface, self.color(), rect, border_radius=6)
        pygame.draw.rect(surface, PLATFORM_EDGE, rect, width=2, border_radius=6)

        if self.bouncy:
            # draw a little spring hint arrow on top
            cx = rect.centerx
            top = rect.top
            pygame.draw.polygon(
                surface, (255, 255, 255),
                [(cx - 6, top + 3), (cx + 6, top + 3), (cx, top - 5)],
            )


class MovingPlatform(Platform):
    """A platform that oscillates left / right between two x bounds."""

    def __init__(self, x, y, width, range_px, speed, height=PLATFORM_HEIGHT,
                 bouncy=False, disappearing=False):
        super().__init__(x, y, width, height, bouncy, disappearing)
        self.origin_x = x
        self.range_px = range_px
        self.speed = speed
        self.phase = 0.0
        self.prev_x = x
        self.delta_x = 0.0   # movement this frame, used to carry the player

    def update(self, dt, player_on_it):
        super().update(dt, player_on_it)
        self.prev_x = self.x
        self.phase += dt * self.speed
        self.x = self.origin_x + math.sin(self.phase) * self.range_px
        self.delta_x = self.x - self.prev_x

    def color(self):
        base = super().color()
        if base == PLATFORM_COLOR:
            return MOVING_PLATFORM_COLOR
        return base
