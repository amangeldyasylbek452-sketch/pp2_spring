"""entities/boss.py — The Skeleton Captain, first mini-boss."""
from __future__ import annotations
import math
import random
import pygame
from .enemy import Enemy


class SkeletonCaptain(Enemy):
    kind = "captain"
    max_health = 260
    move_speed = 190
    sight_range = 500
    attack_range = 56
    attack_damage = 18
    stagger_duration = 0.25
    gold_reward = (40, 60)

    def __init__(self, game, x, y) -> None:
        super().__init__(game, x, y, w=54, h=78)
        self.health = self.max_health
        self.phase = 1
        self.action_cooldown = 1.5
        self.current_action = None
        self.action_timer = 0.0
        self.leap_target_x = None
        self.is_boss = True
        self.name = "Skeleton Captain"
        self.introduced = False
        self.enraged = False

    def update(self, dt, solids):
        if self.health < self.max_health * 0.45 and not self.enraged:
            self.enraged = True
            self.move_speed *= 1.3
            self.game.on_boss_phase_change(self, 2)

        self.action_cooldown -= dt
        if self.alive:
            self._boss_ai(dt)
            self.apply_gravity(dt)
            self.apply_friction()
            self.move_and_collide(dt, solids)
        else:
            self.dead_timer += dt
            self.apply_gravity(dt)
            self.move_and_collide(dt, solids)
        self.hit_cooldown = max(0.0, self.hit_cooldown - dt)
        self.stagger_flash = max(0.0, self.stagger_flash - dt)
        self.tick_anim(dt, 6)

    def _boss_ai(self, dt):
        player = self.game.player
        dist = math.hypot(player.pos.x - self.pos.x, player.pos.y - self.pos.y)

        if self.current_action:
            self._run_action(dt, dist)
            return

        if self.fsm.state == "stagger":
            self.fsm.update(dt)
            return

        if dist > self.sight_range:
            self.move_patrol(dt)
            return

        self.facing = 1 if player.pos.x > self.pos.x else -1

        if self.action_cooldown <= 0:
            choices = ["combo", "shield_charge"]
            if dist > 90:
                choices.append("bone_toss")
            if self.enraged:
                choices.append("leap_slam")
            self.current_action = random.choice(choices)
            self.action_timer = 0.0
            self.set_anim("attack", fps=8)
            self.action_cooldown = random.uniform(1.4, 2.2)
            return

        if dist > self.attack_range:
            self.vel.x = self.facing * self.move_speed
        else:
            self.vel.x *= 0.4

    def _run_action(self, dt, dist):
        self.action_timer += dt
        act = self.current_action
        if act == "combo":
            self.vel.x = self.facing * self.move_speed * 0.6
            if 0.3 < self.action_timer < 0.36 and dist < self.attack_range + 10:
                self.game.player.take_damage(self.attack_damage, source_x=self.pos.x)
                self.game.camera.shake(4)
            if self.action_timer > 0.75:
                self.current_action = None
        elif act == "shield_charge":
            self.vel.x = self.facing * self.move_speed * 2.4
            if dist < self.attack_range and self.action_timer > 0.15:
                self.game.player.take_damage(self.attack_damage * 0.8, source_x=self.pos.x)
                self.game.camera.shake(5)
                self.current_action = None
            if self.action_timer > 0.6:
                self.current_action = None
        elif act == "bone_toss":
            self.vel.x *= 0.5
            if abs(self.action_timer - 0.3) < 0.02:
                self.game.spawn_projectile(self.pos.x, self.pos.y - self.h * 0.6,
                                            self.facing, owner="enemy", damage=14, kind="bone")
            if self.action_timer > 0.7:
                self.current_action = None
        elif act == "leap_slam":
            if self.action_timer < 0.4:
                self.vel.y = -960
                self.vel.x = self.facing * 480
            elif self.on_ground and self.action_timer > 0.4:
                if abs(self.action_timer - 0.42) < 0.05:
                    self.game.camera.shake(10)
                    self.game.particles.spawn(self.pos.x, self.pos.y, "dust", count=20, speed=120)
                    if dist < 50:
                        self.game.player.take_damage(self.attack_damage * 1.4, source_x=self.pos.x)
                if self.action_timer > 1.0:
                    self.current_action = None

    def take_damage(self, amount, crit=False, knockback=90):
        super().take_damage(amount, crit, knockback=knockback * 0.4)
        if self.alive:
            self.current_action = None
