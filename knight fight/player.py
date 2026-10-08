"""
player.py - The knight. Full state machine: idle/walk/run/attack/hurt/death/dash.
"""
import pygame
import math
from settings import (
    KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_ATTACK, KEY_DASH,
    PLAYER_MAX_HP, PLAYER_WALK_SPEED, PLAYER_RUN_SPEED, PLAYER_DASH_SPEED,
    PLAYER_DASH_TIME, PLAYER_DASH_COOLDOWN, PLAYER_IFRAME_TIME,
    PLAYER_ATTACK_COOLDOWN, PLAYER_COMBO_WINDOW, PLAYER_STAMINA_MAX,
    PLAYER_STAMINA_REGEN, DASH_STAMINA_COST, ATTACK_STAMINA_COST, TILE
)
from sprites import make_knight_frame

ANIM_SPEED = 0.12  # seconds per frame


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, event_bus=None):
        super().__init__()
        # Event bus (injected by Game or default)
        from event_bus import default_bus
        self.event_bus = event_bus or default_bus()
        self.state = "idle"
        self.facing = 1
        self.frame_index = 0
        self.frame_timer = 0.0

        self.image = make_knight_frame("idle", 0, 1)
        self.rect = self.image.get_rect(center=(x, y))
        self.hitbox = self.rect.inflate(-20, -10)

        self.pos = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)

        self.hp = PLAYER_MAX_HP
        self.max_hp = PLAYER_MAX_HP
        self.stamina = PLAYER_STAMINA_MAX
        self.max_stamina = PLAYER_STAMINA_MAX

        self.combo_index = 0
        self.combo_timer = 0.0
        self.attack_cooldown_timer = 0.0
        self.attack_active_timer = 0.0
        self.current_attack_hits = set()

        self.dash_timer = 0.0
        self.dash_cooldown_timer = 0.0
        self.dash_dir = pygame.Vector2(1, 0)

        self.iframe_timer = 0.0
        self.hurt_timer = 0.0
        self.is_dead = False
        self.death_timer = 0.0

        self.gold = 0
        self.keys_held = 0
        self.inventory = {"potion": 3, "magic_crystal": 0, "quest_items": []}

        self.attack_range = 46
        self.attack_damage = [14, 16, 24]  # 3-hit combo damage

    # -- input -------------------------------------------------------------
    def handle_input(self, keys, dt, particle_system):
        if self.is_dead:
            return
        if self.hurt_timer > 0 or self.attack_active_timer > 0:
            # locked during hurt/attack recovery (but attack allows movement cancel window)
            if self.hurt_timer > 0:
                return

        move = pygame.Vector2(0, 0)
        if keys[KEY_UP]:
            move.y -= 1
        if keys[KEY_DOWN]:
            move.y += 1
        if keys[KEY_LEFT]:
            move.x -= 1
        if keys[KEY_RIGHT]:
            move.x += 1

        running = keys[pygame.K_LSHIFT] is False and (keys[KEY_UP] or keys[KEY_DOWN] or keys[KEY_LEFT] or keys[KEY_RIGHT])

        if move.length_squared() > 0:
            move = move.normalize()
            if move.x != 0:
                self.facing = 1 if move.x > 0 else -1

        # Dash trigger handled in Game (key down event) - see try_dash()
        if self.dash_timer > 0:
            self.velocity = self.dash_dir * PLAYER_DASH_SPEED
            if particle_system:
                particle_system.emit_dash_trail(self.pos.x, self.pos.y)
        elif self.attack_active_timer > 0:
            self.velocity *= 0.8  # slow during attack
        else:
            speed = PLAYER_RUN_SPEED if (keys[pygame.K_LSHIFT] and move.length_squared() > 0) else PLAYER_WALK_SPEED
            self.velocity = move * speed

    def try_attack(self):
        if self.is_dead or self.dash_timer > 0 or self.hurt_timer > 0:
            return False
        if self.attack_cooldown_timer > 0:
            return False
        if self.stamina < ATTACK_STAMINA_COST:
            return False
        self.stamina -= ATTACK_STAMINA_COST
        if self.combo_timer > 0:
            self.combo_index = (self.combo_index + 1) % 3
        else:
            self.combo_index = 0
        self.combo_timer = PLAYER_COMBO_WINDOW
        self.attack_cooldown_timer = PLAYER_ATTACK_COOLDOWN
        self.attack_active_timer = 0.22
        self.current_attack_hits.clear()
        self.state = "attack"
        self.frame_index = 0
        self.frame_timer = 0
        return True

    def try_dash(self, move_dir, particle_system=None):
        if self.is_dead or self.dash_cooldown_timer > 0 or self.stamina < DASH_STAMINA_COST:
            return False
        if move_dir.length_squared() == 0:
            move_dir = pygame.Vector2(self.facing, 0)
        self.dash_dir = move_dir.normalize()
        self.dash_timer = PLAYER_DASH_TIME
        self.dash_cooldown_timer = PLAYER_DASH_COOLDOWN
        self.stamina -= DASH_STAMINA_COST
        self.iframe_timer = max(self.iframe_timer, PLAYER_DASH_TIME + 0.1)
        self.state = "dash"
        return True

    def take_damage(self, amount, knockback=pygame.Vector2(0, 0), particle_system=None):
        if self.iframe_timer > 0 or self.is_dead:
            return
        self.hp = max(0, self.hp - amount)
        self.iframe_timer = PLAYER_IFRAME_TIME
        self.hurt_timer = 0.28
        self.velocity = knockback
        self.state = "hurt"
        # Emit an event so UI, quests, audio can react without tight coupling
        try:
            self.event_bus.emit('player_damaged', amount=amount, hp=self.hp)
        except Exception:
            pass
        if particle_system:
            particle_system.emit_blood(self.pos.x, self.pos.y)
            particle_system.shake(6, 0.2)
        if self.hp <= 0:
            self.die()

    def die(self):
        self.is_dead = True
        self.state = "death"
        self.death_timer = 1.4
        self.velocity = pygame.Vector2(0, 0)
        try:
            self.event_bus.emit('player_died')
        except Exception:
            pass

    def get_attack_hitbox(self):
        w, h = self.attack_range, 40
        if self.facing == 1:
            rect = pygame.Rect(self.hitbox.centerx, self.hitbox.centery - h // 2, w, h)
        else:
            rect = pygame.Rect(self.hitbox.centerx - w, self.hitbox.centery - h // 2, w, h)
        return rect

    def get_attack_damage(self):
        return self.attack_damage[min(self.combo_index, 2)]

    # -- update --------------------------------------------------------
    def update(self, dt, collision_rects):
        # timers
        for attr in ("attack_cooldown_timer", "combo_timer", "dash_cooldown_timer",
                     "iframe_timer", "hurt_timer", "attack_active_timer"):
            v = getattr(self, attr) - dt
            setattr(self, attr, max(0.0, v))

        if self.dash_timer > 0:
            self.dash_timer = max(0.0, self.dash_timer - dt)

        if self.is_dead:
            self.death_timer -= dt
            self._advance_anim(dt, loop=False)
            return

        self.stamina = min(self.max_stamina, self.stamina + PLAYER_STAMINA_REGEN * dt)

        # integrate movement with simple AABB collision
        self.pos.x += self.velocity.x * dt
        self.hitbox.centerx = round(self.pos.x)
        for r in collision_rects:
            if self.hitbox.colliderect(r):
                if self.velocity.x > 0:
                    self.hitbox.right = r.left
                elif self.velocity.x < 0:
                    self.hitbox.left = r.right
                self.pos.x = self.hitbox.centerx

        self.pos.y += self.velocity.y * dt
        self.hitbox.centery = round(self.pos.y)
        for r in collision_rects:
            if self.hitbox.colliderect(r):
                if self.velocity.y > 0:
                    self.hitbox.bottom = r.top
                elif self.velocity.y < 0:
                    self.hitbox.top = r.bottom
                self.pos.y = self.hitbox.centery

        self.rect.center = self.hitbox.center

        # state resolution (priority: death > hurt > dash > attack > move)
        if self.hurt_timer > 0:
            self.state = "hurt"
        elif self.dash_timer > 0:
            self.state = "dash"
        elif self.attack_active_timer > 0:
            self.state = "attack"
        else:
            speed = self.velocity.length()
            if speed > PLAYER_RUN_SPEED - 10:
                self.state = "run"
            elif speed > 5:
                self.state = "walk"
            else:
                self.state = "idle"

        self._advance_anim(dt, loop=True)

    def _advance_anim(self, dt, loop=True):
        self.frame_timer += dt
        frames_by_state = {"idle": 4, "walk": 4, "run": 4, "attack": 3, "hurt": 1, "dash": 1, "death": 1}
        n = frames_by_state.get(self.state, 4)
        if self.frame_timer >= ANIM_SPEED:
            self.frame_timer = 0
            self.frame_index += 1
            if self.frame_index >= n:
                self.frame_index = n - 1 if not loop else 0
        self.image = make_knight_frame(self.state, self.frame_index, self.facing)
        self.rect = self.image.get_rect(center=self.hitbox.center)

    def draw(self, surf, cam):
        screen_rect = cam.apply(self.rect)
        # flash white briefly during i-frames for readability
        if self.iframe_timer > 0 and int(self.iframe_timer * 20) % 2 == 0:
            tint = self.image.copy()
            tint.fill((255, 255, 255, 90), special_flags=pygame.BLEND_RGBA_ADD)
            surf.blit(tint, screen_rect)
        else:
            surf.blit(self.image, screen_rect)