"""
player.py - The player-controlled cube. Handles physics (gravity, coyote
time, jump buffering, variable jump height), rotation animation, skins,
trail particles and death animation.
"""
import math
import pygame
import config
from skins import TRAIL_EFFECTS


TRAIL_COLORS = {
    "classic": (90, 200, 255),
    "ice": (170, 230, 255),
    "fire": (255, 120, 40),
    "neon": (255, 60, 220),
    "pixel": (120, 220, 120),
    "sparkle": (255, 225, 120),
    "smoke": (120, 110, 130),
    "magic": (170, 110, 255),
    "lightning": (255, 240, 90),
    "rainbow": (255, 255, 255),
}


class Player:
    def __init__(self, x, ground_y, skin_manager):
        self.size = config.CUBE_SIZE
        self.x = x
        self.ground_y = ground_y
        self.y = ground_y - self.size
        self.vy = 0.0
        self.on_ground = True
        self.rotation = 0.0
        self.coyote_timer = 0.0
        self.jump_buffer_timer = 0.0
        self.has_double_jump = True
        self.used_double_jump = False
        self.alive = True
        self.death_timer = 0.0
        self.skin_manager = skin_manager
        self.gravity_flipped = False
        self.speed_multiplier = 1.0
        self.trail_accum = 0.0
        self.squash = 1.0
        self.jump_held = False

    @property
    def rect(self):
        pad = 5
        return pygame.Rect(int(self.x + pad), int(self.y + pad),
                            int(self.size - pad * 2), int(self.size - pad * 2))

    def reset(self, x, ground_y):
        self.x = x
        self.ground_y = ground_y
        self.y = ground_y - self.size
        self.vy = 0.0
        self.on_ground = True
        self.rotation = 0.0
        self.coyote_timer = 0.0
        self.jump_buffer_timer = 0.0
        self.used_double_jump = False
        self.alive = True
        self.death_timer = 0.0
        self.gravity_flipped = False
        self.speed_multiplier = 1.0
        self.squash = 1.0

    def request_jump(self):
        self.jump_buffer_timer = config.JUMP_BUFFER_TIME

    def release_jump(self):
        self.jump_held = False
        if self.vy < 0 and not self.gravity_flipped:
            # cut the jump short for variable height
            self.vy *= config.JUMP_CUT_MULTIPLIER
        elif self.vy > 0 and self.gravity_flipped:
            self.vy *= config.JUMP_CUT_MULTIPLIER

    def _do_jump(self, particles):
        g_sign = 1 if not self.gravity_flipped else -1
        self.vy = config.JUMP_VELOCITY * g_sign
        self.jump_buffer_timer = 0.0
        self.coyote_timer = 0.0
        self.on_ground = False
        self.jump_held = True
        particles.jump_burst(self.x + self.size / 2, self.y + self.size, self._trail_color())

    def _do_double_jump(self, particles):
        g_sign = 1 if not self.gravity_flipped else -1
        self.vy = config.DOUBLE_JUMP_VELOCITY * g_sign
        self.used_double_jump = True
        self.jump_buffer_timer = 0.0
        particles.jump_burst(self.x + self.size / 2, self.y + self.size / 2, self._trail_color())

    def _trail_color(self):
        skin = self.skin_manager.equipped
        return TRAIL_COLORS.get(skin["trail"], (255, 255, 255))

    def update(self, dt, particles, double_jump_enabled=True):
        if not self.alive:
            self.death_timer += dt
            return

        # timers
        if self.on_ground:
            self.coyote_timer = config.COYOTE_TIME
        else:
            self.coyote_timer = max(0.0, self.coyote_timer - dt)
        self.jump_buffer_timer = max(0.0, self.jump_buffer_timer - dt)

        # resolve buffered jump
        if self.jump_buffer_timer > 0:
            if self.on_ground or self.coyote_timer > 0:
                self._do_jump(particles)
            elif double_jump_enabled and not self.used_double_jump:
                self._do_double_jump(particles)

        # gravity
        g_sign = 1 if not self.gravity_flipped else -1
        self.vy += config.GRAVITY * g_sign * dt
        self.vy = max(-config.MAX_FALL_SPEED, min(config.MAX_FALL_SPEED, self.vy))
        self.y += self.vy * dt

        # ground collision (simple flat/segmented ground handled by level via set_ground)
        floor = self.ground_y - self.size if not self.gravity_flipped else self.ground_y
        if not self.gravity_flipped:
            if self.y >= floor:
                if not self.on_ground and self.vy > 200:
                    particles.land_burst(self.x + self.size / 2, self.y + self.size, self._trail_color())
                    self.squash = 0.6
                self.y = floor
                self.vy = 0
                self.on_ground = True
                self.used_double_jump = False
        else:
            if self.y <= floor:
                self.y = floor
                self.vy = 0
                self.on_ground = True
                self.used_double_jump = False

        was_ground = self.on_ground
        # rotation animation
        if not self.on_ground:
            direction = 1 if self.vy >= 0 else -1
            if self.gravity_flipped:
                direction *= -1
            self.rotation += config.ROTATION_SPEED * dt * direction
            self.rotation %= 360
        else:
            # snap to nearest 90 for a crisp landing
            nearest = round(self.rotation / 90) * 90
            self.rotation += (nearest - self.rotation) * min(1.0, dt * 18)

        # squash/stretch recovery
        self.squash += (1.0 - self.squash) * min(1.0, dt * 10)

        # trail particles while airborne / always for juice
        self.trail_accum += dt
        if self.trail_accum > 0.03:
            self.trail_accum = 0.0
            particles.trail(self.x + self.size / 2, self.y + self.size / 2,
                             self._trail_color(), kind="circle", size=5, life=0.3)

    def kill(self, particles, audio):
        if not self.alive:
            return
        self.alive = False
        self.death_timer = 0.0
        particles.death_burst(self.x + self.size / 2, self.y + self.size / 2, self._trail_color())
        audio.play("death")

    def draw(self, surf, cam_x):
        if not self.alive:
            return
        skin = self.skin_manager.equipped
        cx = self.x + self.size / 2 - cam_x
        cy = self.y + self.size / 2
        s = self.size * self.squash
        surf_size = int(self.size * 1.6)
        cube_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
        half = surf_size / 2
        rect = pygame.Rect(half - s / 2, half - (self.size / self.squash if False else s) / 2,
                            s, s)
        rect = pygame.Rect(int(half - s / 2), int(half - s / 2), int(s), int(s))
        primary = skin["primary"]
        secondary = skin["secondary"]
        pattern = skin["pattern"]

        pygame.draw.rect(cube_surf, primary, rect, border_radius=6)
        if pattern == "plain":
            inner = rect.inflate(-10, -10)
            pygame.draw.rect(cube_surf, secondary, inner, 3, border_radius=4)
        elif pattern == "facet":
            pygame.draw.polygon(cube_surf, secondary,
                                 [(rect.left, rect.top), (rect.centerx, rect.top + 6),
                                  (rect.left + 6, rect.centery)])
            pygame.draw.polygon(cube_surf, secondary,
                                 [(rect.right, rect.bottom), (rect.centerx, rect.bottom - 6),
                                  (rect.right - 6, rect.centery)])
        elif pattern == "stripes":
            for i in range(-1, 3):
                x0 = rect.left + i * 10
                pygame.draw.line(cube_surf, secondary, (x0, rect.bottom), (x0 + 14, rect.top), 4)
        elif pattern == "outline":
            pygame.draw.rect(cube_surf, secondary, rect, 3, border_radius=6)
            pygame.draw.rect(cube_surf, secondary, rect.inflate(-14, -14), 2, border_radius=4)
        elif pattern == "grid":
            step = rect.w // 3
            for i in range(1, 3):
                pygame.draw.line(cube_surf, secondary, (rect.left + i * step, rect.top),
                                  (rect.left + i * step, rect.bottom), 2)
                pygame.draw.line(cube_surf, secondary, (rect.left, rect.top + i * step),
                                  (rect.right, rect.top + i * step), 2)
        elif pattern == "diamond":
            pygame.draw.polygon(cube_surf, secondary,
                                 [(rect.centerx, rect.top + 4), (rect.right - 4, rect.centery),
                                  (rect.centerx, rect.bottom - 4), (rect.left + 4, rect.centery)], 2)
        elif pattern == "stars":
            import random as _r
            rng = _r.Random(7)
            for _ in range(6):
                sx = rect.left + rng.randint(4, rect.w - 4)
                sy = rect.top + rng.randint(4, rect.h - 4)
                pygame.draw.circle(cube_surf, secondary, (sx, sy), 1)

        pygame.draw.rect(cube_surf, (0, 0, 0, 90), rect, 2, border_radius=6)
        # eyes for personality
        eye_y = rect.top + rect.h * 0.4
        pygame.draw.circle(cube_surf, (20, 20, 25), (int(rect.left + rect.w * 0.35), int(eye_y)), 2)
        pygame.draw.circle(cube_surf, (20, 20, 25), (int(rect.left + rect.w * 0.65), int(eye_y)), 2)

        rotated = pygame.transform.rotate(cube_surf, -self.rotation)
        rr = rotated.get_rect(center=(cx, cy))
        surf.blit(rotated, rr.topleft)

    def draw_death(self, surf, cam_x):
        pass  # handled entirely via particle burst