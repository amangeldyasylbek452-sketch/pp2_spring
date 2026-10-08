"""
enemy.py - Base Enemy state machine (patrol -> chase -> attack -> death)
plus concrete enemy types: SkeletonWarrior, SkeletonArcher, Bat.
"""
import pygame
import random
import math
from sprites import make_skeleton_frame, make_bat_frame, make_ghost_frame

ANIM_SPEED = 0.18


class Projectile(pygame.sprite.Sprite):
    """A simple arrow fired by archers."""
    def __init__(self, x, y, direction, damage=10, speed=320, color=(200, 200, 210)):
        super().__init__()
        self.pos = pygame.Vector2(x, y)
        self.dir = direction.normalize() if direction.length_squared() else pygame.Vector2(1, 0)
        self.speed = speed
        self.damage = damage
        self.life = 2.5
        self.image = pygame.Surface((10, 4), pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, (0, 0, 10, 4))
        angle = math.degrees(math.atan2(-self.dir.y, self.dir.x))
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self, dt):
        self.pos += self.dir * self.speed * dt
        self.rect.center = self.pos
        self.life -= dt
        return self.life > 0


class Enemy(pygame.sprite.Sprite):
    """Base enemy with patrol / chase / attack / death state machine."""

    def __init__(self, x, y, hp=40, speed=70, patrol_range=120,
                 aggro_range=220, attack_range=42, damage=10, xp=10):
        super().__init__()
        self.pos = pygame.Vector2(x, y)
        self.spawn_x = x
        self.patrol_range = patrol_range
        self.hp = hp
        self.max_hp = hp
        self.speed = speed
        self.aggro_range = aggro_range
        self.attack_range = attack_range
        self.damage = damage
        self.xp = xp

        self.state = "patrol"
        self.facing = random.choice([-1, 1])
        self.frame_index = 0
        self.frame_timer = 0.0

        self.attack_cooldown = 0.0
        self.attack_windup = 0.0
        self.hurt_timer = 0.0
        self.death_timer = 0.0
        self.is_dead = False
        self.alive_for_loot = True

        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.hitbox = self.rect.inflate(-6, -4)

    # -- AI ---------------------------------------------------------------
    def update(self, dt, player, collision_rects, particle_system=None):
        if self.is_dead:
            self.death_timer -= dt
            self._advance_anim(dt)
            return

        self.hurt_timer = max(0.0, self.hurt_timer - dt)
        self.attack_cooldown = max(0.0, self.attack_cooldown - dt)

        to_player = pygame.Vector2(player.hitbox.center) - self.pos
        dist = to_player.length()

        if self.hurt_timer > 0:
            self.state = "hurt"
        elif dist <= self.attack_range and self.attack_cooldown <= 0:
            self.state = "attack"
            self._do_attack(player, particle_system)
        elif dist <= self.aggro_range:
            self.state = "chase"
            if dist > 2:
                move = to_player.normalize() * self.speed
                self._move(move, dt, collision_rects)
                self.facing = 1 if to_player.x > 0 else -1
        else:
            self.state = "patrol"
            self._patrol(dt, collision_rects)

        self._advance_anim(dt)

    def _patrol(self, dt, collision_rects):
        move = pygame.Vector2(self.facing * self.speed * 0.5, 0)
        self._move(move, dt, collision_rects)
        if abs(self.pos.x - self.spawn_x) > self.patrol_range:
            self.facing *= -1

    def _move(self, move, dt, collision_rects):
        self.pos.x += move.x * dt
        self.hitbox.centerx = round(self.pos.x)
        for r in collision_rects:
            if self.hitbox.colliderect(r):
                self.hitbox.centerx = round(self.pos.x - move.x * dt)
                self.pos.x = self.hitbox.centerx
                self.facing *= -1
                break
        self.pos.y += move.y * dt
        self.hitbox.centery = round(self.pos.y)
        for r in collision_rects:
            if self.hitbox.colliderect(r):
                self.hitbox.centery = round(self.pos.y - move.y * dt)
                self.pos.y = self.hitbox.centery
        self.rect.center = self.hitbox.center

    def _do_attack(self, player, particle_system):
        self.attack_cooldown = 1.1
        kb = pygame.Vector2(1 if player.pos.x > self.pos.x else -1, -0.2) * 260
        player.take_damage(self.damage, kb, particle_system)

    def take_damage(self, amount, particle_system=None):
        if self.is_dead:
            return
        self.hp -= amount
        self.hurt_timer = 0.2
        # Emit event for systems that care (UI, quests, audio)
        try:
            from event_bus import default_bus
            default_bus().emit('enemy_damaged', enemy=self, amount=amount)
        except Exception:
            pass
        if particle_system:
            particle_system.emit_hit_spark(self.pos.x, self.pos.y)
        if self.hp <= 0:
            self.hp = 0
            self.is_dead = True
            self.death_timer = 0.6
            self.state = "death"
            try:
                from event_bus import default_bus
                default_bus().emit('enemy_died', enemy=self)
            except Exception:
                pass
            if particle_system:
                particle_system.emit_death_burst(self.pos.x, self.pos.y, (200, 200, 190))

    def _advance_anim(self, dt):
        self.frame_timer += dt
        if self.frame_timer >= ANIM_SPEED:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % 2
        self.image = make_skeleton_frame(self.state, self.frame_index, self.facing)
        self.rect = self.image.get_rect(center=self.hitbox.center)

    def draw(self, surf, cam):
        if self.is_dead and self.death_timer <= 0:
            return
        alpha = 255
        if self.is_dead:
            alpha = max(0, int(255 * (self.death_timer / 0.6)))
        screen_rect = cam.apply(self.rect)
        img = self.image
        if alpha < 255:
            img = img.copy()
            img.set_alpha(alpha)
        surf.blit(img, screen_rect)
        if not self.is_dead and self.hp < self.max_hp:
            self._draw_hp_bar(surf, screen_rect)

    def _draw_hp_bar(self, surf, screen_rect):
        w = 30
        x = screen_rect.centerx - w // 2
        y = screen_rect.top - 8
        pygame.draw.rect(surf, (30, 10, 10), (x, y, w, 4))
        pct = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surf, (200, 40, 40), (x, y, int(w * pct), 4))


class SkeletonWarrior(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, hp=40, speed=80, aggro_range=200, attack_range=40, damage=10, xp=15)


class SkeletonArcher(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, hp=28, speed=50, aggro_range=320, attack_range=260, damage=8, xp=15)
        self.projectiles = pygame.sprite.Group()

    def _do_attack(self, player, particle_system):
        self.attack_cooldown = 1.6
        direction = pygame.Vector2(player.hitbox.center) - self.pos
        self.projectiles.add(Projectile(self.pos.x, self.pos.y, direction, damage=self.damage))

    def update(self, dt, player, collision_rects, particle_system=None):
        super().update(dt, player, collision_rects, particle_system)
        for p in list(self.projectiles):
            if not p.update(dt):
                self.projectiles.remove(p)

    def draw(self, surf, cam):
        super().draw(surf, cam)
        for p in self.projectiles:
            surf.blit(p.image, cam.apply(p.rect))


class Bat(Enemy):
    """Erratic flyer that darts toward the player."""
    def __init__(self, x, y):
        super().__init__(x, y, hp=15, speed=140, aggro_range=250, attack_range=28, damage=6, xp=8)
        self.wander_timer = 0.0
        self.wander_dir = pygame.Vector2(1, 0)

    def update(self, dt, player, collision_rects, particle_system=None):
        if self.is_dead:
            self.death_timer -= dt
            self._advance_anim(dt)
            return
        self.hurt_timer = max(0.0, self.hurt_timer - dt)
        self.attack_cooldown = max(0.0, self.attack_cooldown - dt)
        to_player = pygame.Vector2(player.hitbox.center) - self.pos
        dist = to_player.length()

        if self.hurt_timer > 0:
            self.state = "hurt"
        elif dist <= self.attack_range and self.attack_cooldown <= 0:
            self.state = "attack"
            self._do_attack(player, particle_system)
        elif dist <= self.aggro_range:
            self.state = "chase"
            self.pos += to_player.normalize() * self.speed * dt
            self.facing = 1 if to_player.x > 0 else -1
        else:
            self.state = "patrol"
            self.wander_timer -= dt
            if self.wander_timer <= 0:
                self.wander_timer = random.uniform(0.5, 1.5)
                self.wander_dir = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
                if self.wander_dir.length_squared() > 0:
                    self.wander_dir.normalize_ip()
            self.pos += self.wander_dir * self.speed * 0.4 * dt

        self.hitbox.center = self.pos
        self.rect.center = self.hitbox.center
        self.frame_timer += dt
        if self.frame_timer >= 0.1:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % 2
        self.image = make_bat_frame(self.frame_index)
        self.rect = self.image.get_rect(center=self.hitbox.center)


class Ghost(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, hp=34, speed=110, aggro_range=260, attack_range=36, damage=9, xp=18)

    def _advance_anim(self, dt):
        self.frame_timer += dt
        if self.frame_timer >= ANIM_SPEED * 0.9:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % 2
        self.image = make_ghost_frame(self.frame_index)
        self.rect = self.image.get_rect(center=self.hitbox.center)


class DarkKnight(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, hp=70, speed=85, aggro_range=220, attack_range=46, damage=14, xp=28)