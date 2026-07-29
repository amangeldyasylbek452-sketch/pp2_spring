import math
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
        if self.kind == "extra_life":
            player.add_life()
            return True
        if self.kind == "shield":
            player.activate_powerup(self.kind, 0.0)
        else:
            player.activate_powerup(self.kind, POWERUP_DURATION.get(self.kind, 5.0))
        return True
