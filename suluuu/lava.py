import math
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
