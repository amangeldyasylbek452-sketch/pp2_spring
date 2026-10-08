"""
particles.py - Lightweight, pooled particle system used for trails, impacts,
death bursts, coin sparkles, weather (rain/snow/ash) and explosions.
"""
import random
import math
import pygame


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "size", "color",
                 "gravity", "fade", "shrink", "kind", "alive", "angle",
                 "spin")

    def __init__(self):
        self.alive = False

    def spawn(self, x, y, vx, vy, life, size, color, gravity=0.0,
              fade=True, shrink=True, kind="circle", angle=0.0, spin=0.0):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.life = life
        self.max_life = life
        self.size = size
        self.color = color
        self.gravity = gravity
        self.fade = fade
        self.shrink = shrink
        self.kind = kind
        self.angle = angle
        self.spin = spin
        self.alive = True

    def update(self, dt):
        self.life -= dt
        if self.life <= 0:
            self.alive = False
            return
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.angle += self.spin * dt

    def draw(self, surf, cam_x):
        if not self.alive:
            return
        t = max(0.0, self.life / self.max_life)
        size = self.size * (t if self.shrink else 1.0)
        if size < 0.5:
            return
        alpha = int(255 * t) if self.fade else 255
        alpha = max(0, min(255, alpha))
        sx = int(self.x - cam_x)
        sy = int(self.y)
        if sx < -20 or sx > surf.get_width() + 20:
            return
        color = (*self.color, alpha)
        if self.kind == "circle":
            s = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (size + 1, size + 1), max(1, int(size)))
            surf.blit(s, (sx - size - 1, sy - size - 1))
        elif self.kind == "square":
            s = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
            rect = pygame.Rect(1, 1, size * 2, size * 2)
            pygame.draw.rect(s, color, rect)
            rotated = pygame.transform.rotate(s, self.angle)
            r = rotated.get_rect(center=(sx, sy))
            surf.blit(rotated, r.topleft)
        elif self.kind == "spark":
            s = pygame.Surface((size * 4 + 2, size * 4 + 2), pygame.SRCALPHA)
            c = (size * 2 + 1, size * 2 + 1)
            dx = math.cos(math.radians(self.angle)) * size * 2
            dy = math.sin(math.radians(self.angle)) * size * 2
            pygame.draw.line(s, color, (c[0] - dx, c[1] - dy), (c[0] + dx, c[1] + dy),
                              max(1, int(size / 2)))
            surf.blit(s, (sx - c[0], sy - c[1]))


class ParticleSystem:
    """Object-pooled particle system to avoid per-frame allocations."""

    def __init__(self, pool_size=600):
        self.pool = [Particle() for _ in range(pool_size)]
        self.cursor = 0

    def _next(self):
        for _ in range(len(self.pool)):
            p = self.pool[self.cursor]
            self.cursor = (self.cursor + 1) % len(self.pool)
            if not p.alive:
                return p
        return self.pool[self.cursor]

    def emit(self, x, y, count, **kwargs):
        for _ in range(count):
            p = self._next()
            jitter_vx = kwargs.get("vx", 0) + random.uniform(-kwargs.get("spread", 60),
                                                               kwargs.get("spread", 60))
            jitter_vy = kwargs.get("vy", 0) + random.uniform(-kwargs.get("spread_y", 60),
                                                               kwargs.get("spread_y", 60))
            life = kwargs.get("life", 0.6) * random.uniform(0.7, 1.3)
            size = kwargs.get("size", 4) * random.uniform(0.6, 1.3)
            p.spawn(x, y, jitter_vx, jitter_vy, life, size,
                    kwargs.get("color", (255, 255, 255)),
                    gravity=kwargs.get("gravity", 0),
                    fade=kwargs.get("fade", True),
                    shrink=kwargs.get("shrink", True),
                    kind=kwargs.get("kind", "circle"),
                    angle=random.uniform(0, 360),
                    spin=random.uniform(-180, 180))

    def jump_burst(self, x, y, color):
        self.emit(x, y, 8, vx=0, vy=40, spread=90, spread_y=30, life=0.35,
                   size=4, color=color, gravity=400, kind="circle")

    def land_burst(self, x, y, color):
        self.emit(x, y, 6, vx=0, vy=-20, spread=110, spread_y=20, life=0.3,
                   size=3, color=color, gravity=500, kind="square")

    def death_burst(self, x, y, color):
        self.emit(x, y, 40, vx=0, vy=-60, spread=260, spread_y=260, life=0.9,
                   size=6, color=color, gravity=650, kind="square")
        self.emit(x, y, 20, vx=0, vy=0, spread=320, spread_y=320, life=0.5,
                   size=2, color=(255, 255, 255), gravity=300, kind="spark")

    def coin_burst(self, x, y):
        self.emit(x, y, 14, vx=0, vy=-80, spread=140, spread_y=60, life=0.5,
                   size=3, color=(255, 210, 80), gravity=500, kind="circle")

    def trail(self, x, y, color, kind="circle", size=5, life=0.35):
        self.emit(x, y, 1, vx=-40, vy=0, spread=15, spread_y=15, life=life,
                   size=size, color=color, gravity=40, kind=kind)

    def explosion(self, x, y, color=(255, 150, 60)):
        self.emit(x, y, 34, vx=0, vy=0, spread=350, spread_y=350, life=0.7,
                   size=7, color=color, gravity=250, kind="circle")

    def update(self, dt):
        for p in self.pool:
            if p.alive:
                p.update(dt)

    def draw(self, surf, cam_x):
        for p in self.pool:
            if p.alive:
                p.draw(surf, cam_x)


class WeatherSystem:
    """Ambient background particles: rain, snow, ash, floating motes, stars."""

    def __init__(self, kind, width, height, density=60):
        self.kind = kind
        self.width = width
        self.height = height
        self.items = []
        for _ in range(density):
            self.items.append(self._make_item())

    def _make_item(self):
        x = random.uniform(0, self.width)
        y = random.uniform(0, self.height)
        if self.kind == "rain":
            return [x, y, random.uniform(500, 800), 0]
        if self.kind == "snow":
            return [x, y, random.uniform(30, 90), random.uniform(0, 6.28)]
        if self.kind == "ash":
            return [x, y, random.uniform(20, 60), random.uniform(0, 6.28)]
        if self.kind == "stars":
            return [x, y, random.uniform(0, 6.28), random.uniform(0.5, 2.5)]
        return [x, y, random.uniform(10, 40), random.uniform(0, 6.28)]

    def update(self, dt):
        for item in self.items:
            if self.kind == "rain":
                item[1] += item[2] * dt
                item[0] -= 60 * dt
                if item[1] > self.height:
                    item[1] = -10
                    item[0] = random.uniform(0, self.width)
            elif self.kind in ("snow", "ash", "float"):
                item[3] += dt
                item[1] += item[2] * dt * 0.3
                item[0] += math.sin(item[3]) * 20 * dt
                if item[1] > self.height:
                    item[1] = -10
                    item[0] = random.uniform(0, self.width)
            elif self.kind == "stars":
                item[2] += dt * item[3]

    def draw(self, surf, color=(255, 255, 255)):
        if self.kind == "rain":
            for x, y, spd, _ in self.items:
                pygame.draw.line(surf, (170, 200, 255), (x, y), (x - 4, y - 14), 1)
        elif self.kind == "snow":
            for x, y, spd, phase in self.items:
                pygame.draw.circle(surf, (255, 255, 255), (int(x), int(y)), 2)
        elif self.kind == "ash":
            for x, y, spd, phase in self.items:
                pygame.draw.circle(surf, (120, 110, 100), (int(x), int(y)), 2)
        elif self.kind == "stars":
            for x, y, phase, spd in self.items:
                b = int(150 + 100 * math.sin(phase))
                pygame.draw.circle(surf, (b, b, min(255, b + 30)), (int(x), int(y)), 1)
        elif self.kind == "float":
            for x, y, spd, phase in self.items:
                pygame.draw.circle(surf, color, (int(x), int(y)), 2)