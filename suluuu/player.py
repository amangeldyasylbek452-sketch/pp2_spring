"""
player.py
---------
Player physics, jumping, power-ups, collisions.
"""

import math
import pygame
from constants import (
    BALL_RADIUS, BALL_COLOR, BALL_OUTLINE, GRAVITY, MOVE_ACCEL,
    MAX_MOVE_SPEED, FRICTION, AIR_FRICTION, JUMP_VELOCITY,
    DOUBLE_JUMP_VELOCITY, HIGH_JUMP_MULTIPLIER, MAX_FALL_SPEED,
    COYOTE_TIME, BOUNCE_PLATFORM_MULTIPLIER, MAGNET_RADIUS, SCREEN_WIDTH,
    MAX_LIVES,
)


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = BALL_RADIUS
        self.alive = True
        self.on_ground = False
        self.can_double_jump = False
        self.jump_buffer = 0.0
        self.coyote_timer = 0.0
        self.max_height_y = y
        self.lives = 3
        self.powerups = {
            'double_jump': 0.0,
            'slow_lava': 0.0,
            'high_jump': 0.0,
            'shield': 0,
            'magnet': 0.0,
        }
        self.contact_platform = None

    def handle_input(self, keys, dt):
        accel = MOVE_ACCEL
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vx -= accel * dt
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vx += accel * dt
        if not (keys[pygame.K_a] or keys[pygame.K_LEFT] or keys[pygame.K_d] or keys[pygame.K_RIGHT]):
            friction = FRICTION if self.on_ground else AIR_FRICTION
            if self.vx > 0:
                self.vx = max(0.0, self.vx - friction * dt)
            elif self.vx < 0:
                self.vx = min(0.0, self.vx + friction * dt)
        self.vx = max(-MAX_MOVE_SPEED, min(MAX_MOVE_SPEED, self.vx))

    def update_timers(self, dt):
        if self.coyote_timer > 0:
            self.coyote_timer = max(0.0, self.coyote_timer - dt)
        for key in ('double_jump', 'slow_lava', 'high_jump', 'magnet'):
            self.powerups[key] = max(0.0, self.powerups[key] - dt)
        if self.powerups['double_jump'] > 0:
            self.can_double_jump = True

    def apply_physics(self, dt):
        self.vy += GRAVITY * dt
        self.vy = min(self.vy, MAX_FALL_SPEED)
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.max_height_y = min(self.max_height_y, self.y)
        if self.x < self.radius:
            self.x = self.radius
            self.vx = 0
        elif self.x > SCREEN_WIDTH - self.radius:
            self.x = SCREEN_WIDTH - self.radius
            self.vx = 0

    def try_jump(self, sound, particles):
        can_jump = self.on_ground or self.coyote_timer > 0 or self.powerups['double_jump'] > 0
        if not can_jump:
            return
        jump_velocity = JUMP_VELOCITY
        if self.powerups['high_jump'] > 0:
            jump_velocity *= HIGH_JUMP_MULTIPLIER
        if not self.on_ground and self.coyote_timer <= 0:
            self.powerups['double_jump'] = 0.0
            self.can_double_jump = False
        self.vy = jump_velocity
        self.on_ground = False
        self.coyote_timer = 0.0
        if sound:
            sound.play('jump')
        if particles:
            particles.powerup_burst(self.x, self.y, (255, 255, 255))

    def activate_powerup(self, kind, duration):
        if kind == 'shield':
            self.powerups['shield'] += 1
        else:
            self.powerups[kind] = max(self.powerups[kind], duration)
        if kind == 'double_jump':
            self.can_double_jump = True

    def consume_shield(self):
        if self.powerups['shield'] > 0:
            self.powerups['shield'] -= 1
            return True
        return False

    def add_life(self):
        self.lives = min(MAX_LIVES, self.lives + 1)

    def apply_magnet(self, coins, dt):
        if self.powerups['magnet'] <= 0:
            return
        for coin in coins:
            if coin.collected:
                continue
            dx = self.x - coin.x
            dy = self.y - coin.y
            dist = math.hypot(dx, dy)
            if dist < MAGNET_RADIUS and dist > 0:
                strength = (MAGNET_RADIUS - dist) / MAGNET_RADIUS
                coin.x += dx / dist * 180 * dt * strength
                coin.y += dy / dist * 180 * dt * strength

    def resolve_platform_collisions(self, platforms, particles, sound):
        landed = None
        self.on_ground = False
        self.coyote_timer = max(0.0, self.coyote_timer)
        player_rect = pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            int(self.radius * 2),
            int(self.radius * 2),
        )
        for platform in platforms:
            if platform.is_gone:
                continue
            rect = pygame.Rect(platform.x, platform.y, platform.width, platform.height)
            if not player_rect.colliderect(rect):
                continue

            vertical_overlap = min(player_rect.bottom, rect.bottom) - max(player_rect.top, rect.top)
            horizontal_overlap = min(player_rect.right, rect.right) - max(player_rect.left, rect.left)

            if self.vy > 0 and self.y + self.radius <= platform.y + 12:
                self.y = platform.y - self.radius
                self.vy = 0.0
                self.on_ground = True
                self.coyote_timer = COYOTE_TIME
                landed = platform
                if platform.bouncy:
                    self.vy = JUMP_VELOCITY * BOUNCE_PLATFORM_MULTIPLIER
                    if sound:
                        sound.play('jump')
                break
            if self.vy < 0 and self.y - self.radius >= platform.y + platform.height - 12:
                self.y = platform.y + platform.height + self.radius
                self.vy = 0.0
                break
            if horizontal_overlap < vertical_overlap:
                if player_rect.centerx < rect.centerx:
                    self.x = platform.x - self.radius
                else:
                    self.x = platform.x + platform.width + self.radius
                self.vx = 0
                player_rect.x = int(self.x - self.radius)
                continue

            if self.vy >= 0:
                self.y = platform.y - self.radius
                self.vy = 0.0
                self.on_ground = True
                self.coyote_timer = COYOTE_TIME
                landed = platform
                if platform.bouncy:
                    self.vy = JUMP_VELOCITY * BOUNCE_PLATFORM_MULTIPLIER
                    if sound:
                        sound.play('jump')
                break
        return landed, self.on_ground

    def draw(self, surface, cam_x, cam_y):
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        pygame.draw.circle(surface, BALL_COLOR, (sx, sy), self.radius)
        pygame.draw.circle(surface, BALL_OUTLINE, (sx, sy), self.radius, 3)
