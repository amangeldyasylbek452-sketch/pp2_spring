"""entities/player.py

The knight. Implements: acceleration-based movement with walk/run/sprint,
3-hit sword combo with timing windows, heavy charged attack, shield block,
perfect-parry window, dodge roll with i-frames, stamina economy, hit-stop
and damage/heal/death handling.
"""
from __future__ import annotations
import pygame
from .entity import Entity
from core import settings as S


class Player(Entity):
    def __init__(self, game, x, y) -> None:
        super().__init__(game, x, y, 42, 66)
        self.max_health = S.PLAYER_MAX_HEALTH
        self.health = self.max_health
        self.max_stamina = S.PLAYER_MAX_STAMINA
        self.stamina = self.max_stamina
        self.max_mana = S.PLAYER_MAX_MANA
        self.mana = self.max_mana

        self.state = "idle"  # idle, move, attack, roll, block, hurt, dead
        self.combo_index = 0
        self.combo_timer = 0.0
        self.attack_active_timer = 0.0
        self.attack_hit_done = False
        self.roll_timer = 0.0
        self.iframe_timer = 0.0
        self.stamina_regen_delay = 0.0
        self.heavy_charge = 0.0
        self.is_charging_heavy = False
        self.hurt_timer = 0.0
        self.parry_window_timer = 0.0
        self.just_parried_timer = 0.0
        self.blocking = False
        self.dead_timer = 0.0

        self.relics = 0
        self.on_damage_callbacks = []

    def effective_max_health(self) -> int:
        return self.max_health + self.game.inventory.upgrades.get("max_health", 0)

    def effective_max_stamina(self) -> int:
        return self.max_stamina + self.game.inventory.upgrades.get("max_stamina", 0)

    def combo_damage(self, i: int) -> float:
        base = list(S.COMBO_DAMAGE)[i]
        return base + self.game.inventory.upgrades.get("sword_damage", 0)

    def try_attack(self) -> None:
        if self.state in ("attack",) and self.combo_timer > 0:
            self._queued_next = True
            return
        if self.state in ("roll", "hurt", "dead"):
            return
        if self.stamina < S.PLAYER_ATTACK_STAMINA_COST:
            return
        self._start_attack(0)

    def _start_attack(self, index: int) -> None:
        self.state = "attack"
        self.combo_index = index
        self.attack_active_timer = 0.18
        self.attack_hit_done = False
        self.combo_timer = S.COMBO_WINDOW
        self.stamina -= S.PLAYER_ATTACK_STAMINA_COST
        self.stamina_regen_delay = S.STAMINA_REGEN_DELAY
        self.set_anim(f"attack{index + 1}", fps=14)
        self._queued_next = False

    def try_roll(self) -> None:
        if self.state in ("roll", "hurt", "dead"):
            return
        if self.stamina < S.PLAYER_ROLL_STAMINA_COST:
            return
        self.state = "roll"
        self.roll_timer = S.PLAYER_ROLL_TIME
        self.iframe_timer = S.PLAYER_IFRAME_ON_ROLL
        self.stamina -= S.PLAYER_ROLL_STAMINA_COST
        self.stamina_regen_delay = S.STAMINA_REGEN_DELAY
        self.vel.x = S.PLAYER_ROLL_SPEED * self.facing
        self.set_anim("roll", fps=12)

    def start_block(self) -> None:
        if self.state in ("attack", "roll", "hurt", "dead"):
            return
        self.blocking = True
        if self.parry_window_timer <= 0:
            self.parry_window_timer = S.PLAYER_PARRY_WINDOW
        self.state = "block"
        self.set_anim("block", fps=6)

    def stop_block(self) -> None:
        self.blocking = False
        if self.state == "block":
            self.state = "idle"

    def take_damage(self, amount: float, source_x: float | None = None, crit: bool = False) -> bool:
        if self.iframe_timer > 0 or self.state == "dead":
            return False
        if self.blocking:
            if self.parry_window_timer > 0:
                self.just_parried_timer = 0.35
                self.game.on_perfect_parry(self)
                return False
            reduced = amount * 0.15
            self.stamina -= S.PLAYER_BLOCK_STAMINA_DRAIN * 0.4
            if self.stamina <= 0:
                self.stamina = 0
                self.blocking = False
            self.health -= reduced
            self.game.camera.shake(2)
            return True
        defense = self.game.inventory.upgrades.get("defense", 0)
        dmg = max(1.0, amount - defense)
        self.health -= dmg
        self.state = "hurt"
        self.hurt_timer = 0.35
        self.iframe_timer = 0.5
        self.set_anim("hurt", fps=10)
        if source_x is not None:
            self.vel.x = (90 if self.pos.x > source_x else -90)
        self.game.camera.shake(6 if crit else 3)
        self.game.hit_stop(0.05 if not crit else 0.12)
        for cb in self.on_damage_callbacks:
            cb(dmg)
        if self.health <= 0:
            self.health = 0
            self.state = "dead"
            self.dead_timer = 0.0
            self.set_anim("death", fps=8)
        return True

    def heal(self, amount: float) -> None:
        self.health = min(self.effective_max_health(), self.health + amount)

    def handle_input(self, dt: float, keys, sprint_held: bool) -> None:
        if self.state in ("hurt", "dead", "roll"):
            return
        move = 0
        if keys.get("left"):
            move -= 1
        if keys.get("right"):
            move += 1
        if move != 0:
            self.facing = move
            speed = S.PLAYER_SPRINT_SPEED if (sprint_held and self.stamina > 0) else S.PLAYER_RUN_SPEED
            self.vel.x += move * S.PLAYER_ACCEL * dt
            self.vel.x = max(-speed, min(speed, self.vel.x))
            if sprint_held and self.stamina > 0 and self.state not in ("attack", "block"):
                self.stamina -= 14 * dt
                self.stamina_regen_delay = S.STAMINA_REGEN_DELAY
            if self.state not in ("attack", "block"):
                self.state = "move"
        else:
            if self.state == "move":
                self.state = "idle"

    def jump(self) -> None:
        if self.on_ground and self.state not in ("attack", "roll", "hurt", "dead"):
            self.vel.y = -1260

    def update(self, dt: float, solids: list[pygame.Rect]) -> None:
        self.combo_timer = max(0.0, self.combo_timer - dt)
        self.iframe_timer = max(0.0, self.iframe_timer - dt)
        self.parry_window_timer = max(0.0, self.parry_window_timer - dt)
        self.just_parried_timer = max(0.0, self.just_parried_timer - dt)
        self.stamina_regen_delay = max(0.0, self.stamina_regen_delay - dt)

        if self.state == "attack":
            self.attack_active_timer -= dt
            if self.attack_active_timer <= 0 and self.combo_timer <= 0.02:
                self.state = "idle"
        elif self.state == "roll":
            self.roll_timer -= dt
            if self.roll_timer <= 0:
                self.state = "idle"
        elif self.state == "hurt":
            self.hurt_timer -= dt
            if self.hurt_timer <= 0:
                self.state = "idle"
        elif self.state == "dead":
            self.dead_timer += dt

        if self.stamina_regen_delay <= 0 and self.stamina < self.effective_max_stamina():
            self.stamina = min(self.effective_max_stamina(), self.stamina + S.STAMINA_REGEN * dt)
        if self.mana < self.max_mana:
            self.mana = min(self.max_mana, self.mana + S.MANA_REGEN * dt)

        self.apply_gravity(dt)
        if self.state not in ("roll",):
            self.apply_friction()
        self.move_and_collide(dt, solids)

        if self.state == "idle":
            self.set_anim("idle", fps=6)
        elif self.state == "move":
            fast = abs(self.vel.x) > S.PLAYER_RUN_SPEED * 0.9
            self.set_anim("run" if fast else "walk", fps=12 if fast else 9)
        self.tick_anim(dt, 6)

    def get_attack_hitbox(self) -> pygame.Rect | None:
        if self.state != "attack":
            return None
        if self.attack_active_timer <= 0:
            return None
        w, h = 70, 46
        x = self.pos.x + (28 * self.facing)
        y = self.pos.y - self.h * 0.6
        return pygame.Rect(int(x - w / 2), int(y - h / 2), w, h)

    def current_frame(self, assets):
        return assets.player_frame(self.anim_action, self.anim_frame)
