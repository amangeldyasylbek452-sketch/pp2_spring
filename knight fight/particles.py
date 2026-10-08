"""
particles.py - Lightweight pixel-particle system + screen shake helper.

Rather than loading external particle images (no asset files ship with this
project), every particle is a tiny filled rect/circle drawn each frame. This
keeps the "pixel art" look while remaining fully self-contained.
"""
import random
import math
import pygame


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "color", "size", "kind", "gravity")

    def __init__(self, x, y, vx, vy, life, color, size=2, kind="dust", gravity=0.0):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size
        self.kind = kind
        self.gravity = gravity

    def update(self, dt):
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        return self.life > 0

    def draw(self, surf, cam):
        sx, sy = cam.apply_pos(self.x, self.y)
        if not (-10 <= sx <= surf.get_width() + 10 and -10 <= sy <= surf.get_height() + 10):
            return
        alpha_ratio = max(0.0, self.life / self.max_life)
        size = max(1, int(self.size * (0.5 + 0.5 * alpha_ratio)))
        color = self.color
        if self.kind == "spark":
            pygame.draw.rect(surf, color, (int(sx), int(sy), size, size))
        else:
            pygame.draw.rect(surf, color, (int(sx), int(sy), size, size))


class ParticleSystem:
    """Manages all world-space particles plus screen-space rain/fog overlays."""

    def __init__(self):
        self.particles = []
        self.shake_time = 0.0
        self.shake_mag = 0.0
        self.rain_drops = []
        self.fog_offset = 0.0

    # -- screen shake ----------------------------------------------------
    def shake(self, magnitude=8, duration=0.25):
        self.shake_time = max(self.shake_time, duration)
        self.shake_mag = max(self.shake_mag, magnitude)

    def get_shake_offset(self):
        if self.shake_time <= 0:
            return 0, 0
        m = self.shake_mag * (self.shake_time / max(0.25, self.shake_time))
        return random.uniform(-m, m), random.uniform(-m, m)

    # -- emitters ----------------------------------------------------------
    def emit_hit_spark(self, x, y, n=8, color=(255, 220, 140)):
        for _ in range(n):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(60, 220)
            self.particles.append(Particle(
                x, y, math.cos(ang) * spd, math.sin(ang) * spd,
                random.uniform(0.15, 0.35), color, size=2, kind="spark"))

    def emit_blood(self, x, y):
        for _ in range(5):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(20, 80)
            self.particles.append(Particle(
                x, y, math.cos(ang) * spd, math.sin(ang) * spd,
                random.uniform(0.3, 0.6), (90, 10, 10), size=2, gravity=250))

    def emit_dash_trail(self, x, y, color=(160, 200, 255)):
        self.particles.append(Particle(x, y, 0, 0, 0.25, color, size=4))

    def emit_fire(self, x, y):
        if random.random() < 0.6:
            self.particles.append(Particle(
                x + random.uniform(-6, 6), y, random.uniform(-8, 8), random.uniform(-60, -30),
                random.uniform(0.4, 0.9),
                random.choice([(255, 140, 40), (255, 90, 20), (255, 200, 80)]),
                size=random.randint(2, 4)))

    def emit_death_burst(self, x, y, color):
        for _ in range(20):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(40, 260)
            self.particles.append(Particle(
                x, y, math.cos(ang) * spd, math.sin(ang) * spd,
                random.uniform(0.3, 0.7), color, size=3, gravity=120))

    # -- update / draw -------------------------------------------------
    def update(self, dt):
        self.particles = [p for p in self.particles if p.update(dt)]
        if self.shake_time > 0:
            self.shake_time -= dt

    def draw_world(self, surf, cam):
        for p in self.particles:
            p.draw(surf, cam)

    def draw_rain(self, surf, count=140):
        w, h = surf.get_size()
        for _ in range(count):
            x = random.randint(0, w)
            y = random.randint(0, h)
            length = random.randint(8, 16)
            pygame.draw.line(surf, (150, 170, 200, 120), (x, y), (x - 3, y + length), 1)

    def draw_fog(self, surf, dt, intensity=90):
        w, h = surf.get_size()
        self.fog_offset = (self.fog_offset + dt * 8) % w
        fog = pygame.Surface((w, h), pygame.SRCALPHA)
        band_h = 90
        for i, y in enumerate(range(h - band_h * 3, h, band_h)):
            alpha = intensity - i * 20
            if alpha <= 0:
                continue
            offset = int(self.fog_offset * (i + 1) * 0.3) % w
            for xoff in (-w, 0, w):
                pygame.draw.ellipse(
                    fog, (180, 190, 210, max(0, alpha)),
                    (xoff + offset - w // 2, y, w * 2, band_h)
                )
        surf.blit(fog, (0, 0))