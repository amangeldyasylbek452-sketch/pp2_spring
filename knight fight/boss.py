"""
boss.py - Mini-boss (Skeleton Captain) with multiple attack phases.
Structured so Level 2's Ghost King and Level 3's Dragon King can subclass Boss.
"""
import pygame
import random
from sprites import make_captain_frame, make_dragon_frame

ANIM_SPEED = 0.15


class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, hp, name):
        super().__init__()
        self.name = name
        self.pos = pygame.Vector2(x, y)
        self.hp = hp
        self.max_hp = hp
        self.phase = 1
        self.state = "idle"
        self.facing = -1
        self.frame_index = 0
        self.frame_timer = 0.0
        self.attack_cooldown = 1.0
        self.hurt_timer = 0.0
        self.is_dead = False
        self.death_timer = 0.0
        self.intro_played = False

        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.hitbox = self.rect.inflate(-10, -6)

    def draw_bar_label(self):
        return f"{self.name}  (Phase {self.phase})"


class SkeletonCaptain(Boss):
    def __init__(self, x, y):
        super().__init__(x, y, hp=260, name="Skeleton Captain")
        self.speed = 90
        self.attack_range = 60
        self.charge_timer = 0.0
        self.is_charging = False
        self.charge_dir = pygame.Vector2(1, 0)

    def update(self, dt, player, collision_rects, particle_system=None):
        if self.is_dead:
            self.death_timer -= dt
            self._advance_anim(dt)
            return

        self.hurt_timer = max(0.0, self.hurt_timer - dt)
        self.attack_cooldown = max(0.0, self.attack_cooldown - dt)

        # Phase transitions based on HP thresholds
        if self.hp < self.max_hp * 0.33:
            self.phase = 3
            self.speed = 150
        elif self.hp < self.max_hp * 0.66:
            self.phase = 2
            self.speed = 115
        else:
            self.phase = 1
            self.speed = 90

        to_player = pygame.Vector2(player.hitbox.center) - self.pos
        dist = to_player.length()

        if self.hurt_timer > 0:
            self.state = "hurt"
        elif self.is_charging:
            self.state = "attack"
            self.pos += self.charge_dir * self.speed * 2.4 * dt
            self.charge_timer -= dt
            if self.charge_timer <= 0:
                self.is_charging = False
        elif dist <= self.attack_range and self.attack_cooldown <= 0:
            self.state = "attack"
            self._melee_attack(player, particle_system)
        elif dist <= 400:
            self.state = "chase"
            if dist > 6:
                move = to_player.normalize() * self.speed
                self.pos += move * dt
                self.facing = 1 if to_player.x > 0 else -1
            if self.phase >= 2 and self.attack_cooldown <= 0 and dist > self.attack_range and random.random() < 0.02:
                self._start_charge(player)
        else:
            self.state = "idle"

        self.hitbox.center = self.pos
        self.rect.center = self.hitbox.center
        self._advance_anim(dt)

    def _melee_attack(self, player, particle_system):
        self.attack_cooldown = 1.3 if self.phase < 3 else 0.8
        dmg = 16 if self.phase == 1 else (20 if self.phase == 2 else 26)
        dist = (pygame.Vector2(player.hitbox.center) - self.pos).length()
        if dist <= self.attack_range + 10:
            kb = pygame.Vector2(1 if player.pos.x > self.pos.x else -1, -0.3) * 340
            player.take_damage(dmg, kb, particle_system)

    def _start_charge(self, player):
        self.is_charging = True
        self.charge_timer = 0.4
        direction = pygame.Vector2(player.hitbox.center) - self.pos
        self.charge_dir = direction.normalize() if direction.length_squared() else pygame.Vector2(self.facing, 0)

    def take_damage(self, amount, particle_system=None):
        if self.is_dead:
            return
        self.hp -= amount
        self.hurt_timer = 0.15
        if particle_system:
            particle_system.emit_hit_spark(self.pos.x, self.pos.y, n=12, color=(255, 200, 120))
            particle_system.shake(4, 0.12)
        if self.hp <= 0:
            self.hp = 0
            self.is_dead = True
            self.death_timer = 1.2
            if particle_system:
                particle_system.emit_death_burst(self.pos.x, self.pos.y, (210, 60, 40))
                particle_system.shake(14, 0.5)

    def _advance_anim(self, dt):
        self.frame_timer += dt
        if self.frame_timer >= ANIM_SPEED:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % 2
        self.image = make_captain_frame(self.state, self.frame_index, self.facing)
        self.rect = self.image.get_rect(center=self.hitbox.center)

    def draw(self, surf, cam):
        if self.is_dead and self.death_timer <= 0:
            return
        img = self.image
        if self.is_dead:
            alpha = max(0, int(255 * (self.death_timer / 1.2)))
            img = img.copy()
            img.set_alpha(alpha)
        surf.blit(img, cam.apply(self.rect))


class GhostKing(Boss):
    def __init__(self, x, y):
        super().__init__(x, y, hp=420, name="Ghost King")
        self.speed = 95
        self.attack_range = 70

    def update(self, dt, player, collision_rects, particle_system=None):
        if self.is_dead:
            self.death_timer -= dt
            self._advance_anim(dt)
            return
        self.hurt_timer = max(0.0, self.hurt_timer - dt)
        self.attack_cooldown = max(0.0, self.attack_cooldown - dt)
        if self.hp < self.max_hp * 0.33:
            self.phase = 3
            self.speed = 125
        elif self.hp < self.max_hp * 0.66:
            self.phase = 2
            self.speed = 110
        else:
            self.phase = 1
            self.speed = 95

        to_player = pygame.Vector2(player.hitbox.center) - self.pos
        dist = to_player.length()
        if self.hurt_timer > 0:
            self.state = "hurt"
        elif dist <= self.attack_range and self.attack_cooldown <= 0:
            self.state = "attack"
            self._melee_attack(player, particle_system)
        elif dist <= 450:
            self.state = "chase"
            move = to_player.normalize() * self.speed
            self.pos += move * dt
            self.facing = 1 if to_player.x > 0 else -1
        else:
            self.state = "idle"

        self.hitbox.center = self.pos
        self.rect.center = self.hitbox.center
        self._advance_anim(dt)

    def _melee_attack(self, player, particle_system):
        self.attack_cooldown = 0.9 if self.phase < 3 else 0.6
        dmg = 18 if self.phase == 1 else (24 if self.phase == 2 else 30)
        if (pygame.Vector2(player.hitbox.center) - self.pos).length() <= self.attack_range + 10:
            kb = pygame.Vector2(1 if player.pos.x > self.pos.x else -1, -0.3) * 320
            player.take_damage(dmg, kb, particle_system)

    def take_damage(self, amount, particle_system=None):
        if self.is_dead:
            return
        self.hp -= amount
        self.hurt_timer = 0.16
        if particle_system:
            particle_system.emit_hit_spark(self.pos.x, self.pos.y, n=14, color=(140, 180, 220))
        if self.hp <= 0:
            self.hp = 0
            self.is_dead = True
            self.death_timer = 1.4
            if particle_system:
                particle_system.emit_death_burst(self.pos.x, self.pos.y, (130, 180, 220))
                particle_system.shake(10, 0.4)

    def _advance_anim(self, dt):
        self.frame_timer += dt
        if self.frame_timer >= ANIM_SPEED * 0.9:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % 2
        self.image = make_dragon_frame(self.phase, self.frame_index, self.facing)
        self.rect = self.image.get_rect(center=self.hitbox.center)

    def draw(self, surf, cam):
        if self.is_dead and self.death_timer <= 0:
            return
        img = self.image
        if self.is_dead:
            alpha = max(0, int(255 * (self.death_timer / 1.4)))
            img = img.copy()
            img.set_alpha(alpha)
        surf.blit(img, cam.apply(self.rect))


class DragonBoss(Boss):
    def __init__(self, x, y):
        super().__init__(x, y, hp=700, name="Dragon King")
        self.speed = 95
        self.attack_range = 90
        self.flight_timer = 0.0
        self.fire_timer = 0.0

    def update(self, dt, player, collision_rects, particle_system=None):
        if self.is_dead:
            self.death_timer -= dt
            self._advance_anim(dt)
            return
        self.hurt_timer = max(0.0, self.hurt_timer - dt)
        self.attack_cooldown = max(0.0, self.attack_cooldown - dt)
        self.flight_timer = max(0.0, self.flight_timer - dt)
        self.fire_timer = max(0.0, self.fire_timer - dt)
        if self.hp < self.max_hp * 0.33:
            self.phase = 3
            self.speed = 140
        elif self.hp < self.max_hp * 0.66:
            self.phase = 2
            self.speed = 120
        else:
            self.phase = 1
            self.speed = 95

        to_player = pygame.Vector2(player.hitbox.center) - self.pos
        dist = to_player.length()
        if self.hurt_timer > 0:
            self.state = "hurt"
        elif self.attack_cooldown <= 0 and dist <= self.attack_range + 40:
            self.state = "attack"
            self._do_attack(player, particle_system)
        elif dist <= 650:
            self.state = "chase"
            move = to_player.normalize() * self.speed
            self.pos += move * dt
            self.facing = 1 if to_player.x > 0 else -1
        else:
            self.state = "idle"

        self.hitbox.center = self.pos
        self.rect.center = self.hitbox.center
        self._advance_anim(dt)

    def _do_attack(self, player, particle_system):
        self.attack_cooldown = 1.3 if self.phase == 1 else (1.0 if self.phase == 2 else 0.7)
        dmg = 24 if self.phase == 1 else (30 if self.phase == 2 else 36)
        if (pygame.Vector2(player.hitbox.center) - self.pos).length() <= self.attack_range + 40:
            kb = pygame.Vector2(1 if player.pos.x > self.pos.x else -1, -0.4) * 360
            player.take_damage(dmg, kb, particle_system)
        if particle_system:
            particle_system.emit_fire(self.pos.x, self.pos.y)

    def take_damage(self, amount, particle_system=None):
        if self.is_dead:
            return
        self.hp -= amount
        self.hurt_timer = 0.12
        if particle_system:
            particle_system.emit_hit_spark(self.pos.x, self.pos.y, n=20, color=(255, 120, 40))
            particle_system.shake(8, 0.16)
        if self.hp <= 0:
            self.hp = 0
            self.is_dead = True
            self.death_timer = 1.8
            if particle_system:
                particle_system.emit_death_burst(self.pos.x, self.pos.y, (255, 80, 20))
                particle_system.shake(18, 0.6)

    def _advance_anim(self, dt):
        self.frame_timer += dt
        if self.frame_timer >= ANIM_SPEED * 0.8:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % 2
        self.image = make_dragon_frame(self.phase, self.frame_index, self.facing)
        self.rect = self.image.get_rect(center=self.hitbox.center)

    def draw(self, surf, cam):
        if self.is_dead and self.death_timer <= 0:
            return
        img = self.image
        if self.is_dead:
            alpha = max(0, int(255 * (self.death_timer / 1.8)))
            img = img.copy()
            img.set_alpha(alpha)
        surf.blit(img, cam.apply(self.rect))