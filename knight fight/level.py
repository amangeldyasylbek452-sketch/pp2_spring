"""
level.py - Level construction and rendering.

Level 1: The Haunted Mountains
A long side-scrolling stretch of cursed terrain: dead trees, broken statues,
ruined bridges, fog, rain, and a blue moon overhead. Ends at an abandoned
fortress guarded by the Skeleton Captain mini-boss; defeating him opens the
portal to the next realm.

Only Level 1 is fully built out in this codebase (see the module docstring
in main.py for why) but Level2/Level3 classes are stubbed with the same
interface so they can be filled in with the Cursed Kingdom streets and
Dragon's Castle without touching any other system.
"""
import random
import math
import pygame
from settings import (
    TILE, NIGHT_SKY_TOP, NIGHT_SKY_BOTTOM, MOON_COLOR, GROUND_DARK, GROUND_LIGHT,
    MOUNTAIN_FAR, MOUNTAIN_NEAR, TORCH_ORANGE,
)
from enemy import SkeletonWarrior, SkeletonArcher, Bat, Ghost, DarkKnight
from boss import SkeletonCaptain, GhostKing, DragonBoss


class Checkpoint:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 16, y - 60, 32, 60)
        self.activated = False


class Portal:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 30, y - 70, 60, 70)
        self.active = False
        self.pulse = 0.0


class Statue:
    def __init__(self, x, y, broken=True):
        self.rect = pygame.Rect(x - 14, y - 40, 28, 40)
        self.broken = broken


class Tree:
    def __init__(self, x, y, scale=1.0):
        self.x, self.y = x, y
        self.scale = scale
        self.sway_phase = random.uniform(0, math.tau)
        self.eyes_active = False
        self.eyes_timer = random.uniform(6, 20)


class Level1:
    """The Haunted Mountains"""
    name = "The Haunted Mountains"

    def __init__(self):
        self.width = 4800
        self.height = 720
        self.ground_y = 560

        # Solid collision geometry: ground + a few floating ruin platforms/bridges
        self.solids = [
            pygame.Rect(0, self.ground_y, self.width, 200),
        ]
        # Bridge gaps -> represented by removing collision in chasms (visual only here,
        # kept simple/robust: one continuous ground so the level always feels fair)

        self.trees = [Tree(x, self.ground_y, random.uniform(0.8, 1.3))
                      for x in range(100, self.width - 200, random.randint(140, 220))]
        self.statues = [Statue(x, self.ground_y) for x in range(600, self.width - 400, 900)]
        self.torches_x = list(range(300, self.width - 300, 500))

        self.checkpoints = [Checkpoint(x, self.ground_y) for x in (400, 1800, 3200)]
        self.portal = Portal(self.width - 200, self.ground_y)

        self.enemies = pygame.sprite.Group()
        self._spawn_enemies()

        self.boss = None
        self.boss_spawn_x = self.width - 500
        self.boss_triggered = False

        self.quest_state = {"reach_fortress": False, "captain_defeated": False, "portal_open": False}

    def _spawn_enemies(self):
        layout = [
            (SkeletonWarrior, 900), (SkeletonWarrior, 1400),
            (SkeletonArcher, 1650), (Bat, 2000), (Bat, 2100),
            (SkeletonWarrior, 2500), (SkeletonArcher, 2750),
            (SkeletonWarrior, 3000), (Bat, 3400), (SkeletonArcher, 3600),
            (SkeletonWarrior, 3900), (SkeletonWarrior, 4000),
        ]
        for cls, x in layout:
            self.enemies.add(cls(x, self.ground_y - 20))

    def collision_rects(self):
        return self.solids

    def current_quest_text(self):
        if not self.quest_state["reach_fortress"]:
            return "Journey through the Haunted Mountains"
        if not self.quest_state["captain_defeated"]:
            return "Defeat the Skeleton Captain"
        if not self.quest_state["portal_open"]:
            return "Enter the portal"
        return "Level complete!"

    def update(self, dt, player, particle_system):
        for t in self.trees:
            t.eyes_timer -= dt
            if t.eyes_timer <= 0:
                t.eyes_active = random.random() < 0.15
                t.eyes_timer = random.uniform(8, 25)

        for cp in self.checkpoints:
            if not cp.activated and player.hitbox.colliderect(cp.rect.inflate(20, 20)):
                cp.activated = True

        if player.pos.x > self.boss_spawn_x - 400 and self.boss is None and not self.boss_triggered:
            self.boss_triggered = True
            self.boss = SkeletonCaptain(self.boss_spawn_x, self.ground_y - 30)
            self.quest_state["reach_fortress"] = True

        if self.boss is not None:
            self.boss.update(dt, player, self.solids, particle_system)
            if self.boss.is_dead and self.boss.death_timer <= 0 and not self.quest_state["captain_defeated"]:
                self.quest_state["captain_defeated"] = True
                self.portal.active = True

        if self.portal.active:
            self.quest_state["portal_open"] = True
            self.portal.pulse += dt

        for e in list(self.enemies):
            e.update(dt, player, self.solids, particle_system)

    def check_portal_reached(self, player):
        return self.portal.active and player.hitbox.colliderect(self.portal.rect)

    # -- rendering ---------------------------------------------------------
    def draw_background(self, surf, cam, t):
        w, h = surf.get_size()
        for y in range(h):
            ratio = y / h
            color = tuple(int(NIGHT_SKY_TOP[i] + (NIGHT_SKY_BOTTOM[i] - NIGHT_SKY_TOP[i]) * ratio) for i in range(3))
            pygame.draw.line(surf, color, (0, y), (w, y))

        moon_x = w * 0.78
        moon_y = h * 0.18
        glow = pygame.Surface((260, 260), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*MOON_COLOR, 40), (130, 130), 130)
        pygame.draw.circle(glow, (*MOON_COLOR, 70), (130, 130), 80)
        surf.blit(glow, (moon_x - 130, moon_y - 130))
        pygame.draw.circle(surf, MOON_COLOR, (int(moon_x), int(moon_y)), 46)

        # parallax mountains
        far_off = (cam.offset_x * 0.15) % w
        near_off = (cam.offset_x * 0.35) % w
        self._draw_mountain_row(surf, far_off, h * 0.6, MOUNTAIN_FAR, 90, w)
        self._draw_mountain_row(surf, near_off, h * 0.68, MOUNTAIN_NEAR, 70, w)

    def _draw_mountain_row(self, surf, offset, base_y, color, amp, w):
        for xoff in (-w, 0, w):
            points = [(xoff - offset, base_y + amp)]
            for i in range(0, w + 100, 100):
                peak = base_y + amp - (amp * 0.6 if (i // 100) % 2 == 0 else amp * 0.3)
                points.append((xoff - offset + i, peak))
            points.append((xoff - offset + w + 100, base_y + amp))
            pygame.draw.polygon(surf, color, points)

    def draw_world(self, surf, cam, t):
        # ground
        ground_rect = cam.apply(pygame.Rect(0, self.ground_y, self.width, self.height))
        pygame.draw.rect(surf, GROUND_DARK, ground_rect)
        for x in range(0, self.width, 40):
            sx, sy = cam.apply_pos(x, self.ground_y)
            if -40 < sx < surf.get_width():
                shade = GROUND_LIGHT if (x // 40) % 3 == 0 else GROUND_DARK
                pygame.draw.rect(surf, shade, (sx, sy, 40, 8))

        for statue in self.statues:
            r = cam.apply(statue.rect)
            if -50 < r.x < surf.get_width():
                pygame.draw.rect(surf, (60, 60, 70), r)
                pygame.draw.rect(surf, (40, 40, 50), (r.x, r.y, r.width, 10))

        for tx in self.torches_x:
            sx, sy = cam.apply_pos(tx, self.ground_y - 50)
            if -20 < sx < surf.get_width():
                flick = 3 + int(2 * math.sin(t * 10 + tx))
                pygame.draw.rect(surf, (70, 50, 30), (sx - 2, sy, 4, 50))
                pygame.draw.circle(surf, TORCH_ORANGE, (int(sx), int(sy - flick)), 6)
                glow = pygame.Surface((60, 60), pygame.SRCALPHA)
                pygame.draw.circle(glow, (*TORCH_ORANGE, 40), (30, 30), 28)
                surf.blit(glow, (sx - 30, sy - 30 - flick))

        for tree in self.trees:
            self._draw_tree(surf, cam, tree, t)

        for cp in self.checkpoints:
            r = cam.apply(cp.rect)
            if -40 < r.x < surf.get_width():
                color = (120, 200, 255) if cp.activated else (90, 90, 100)
                pygame.draw.rect(surf, color, r, border_radius=4)

        self._draw_portal(surf, cam, t)

        if self.boss is not None:
            self.boss.draw(surf, cam)
        for e in self.enemies:
            e.draw(surf, cam)

    def _draw_tree(self, surf, cam, tree, t):
        sx, sy = cam.apply_pos(tree.x, tree.y)
        if not (-60 < sx < surf.get_width() + 60):
            return
        sway = math.sin(t * 1.2 + tree.sway_phase) * 4
        h = int(90 * tree.scale)
        pygame.draw.rect(surf, (35, 28, 24), (sx - 4, sy - h, 8, h))
        for i in range(3):
            branch_y = sy - h + i * 20
            pygame.draw.line(surf, (35, 28, 24), (sx, branch_y), (sx + sway * (i + 1) - 10, branch_y - 20), 3)
            pygame.draw.line(surf, (35, 28, 24), (sx, branch_y), (sx - sway * (i + 1) + 10, branch_y - 20), 3)
        if tree.eyes_active:
            pygame.draw.circle(surf, (255, 40, 40), (int(sx - 4), int(sy - h + 15)), 2)
            pygame.draw.circle(surf, (255, 40, 40), (int(sx + 4), int(sy - h + 15)), 2)

    def _draw_portal(self, surf, cam, t):
        r = cam.apply(self.portal.rect)
        if not (-80 < r.x < surf.get_width()):
            return
        if self.portal.active:
            pulse = 0.5 + 0.5 * math.sin(self.portal.pulse * 4)
            color = (int(120 + 100 * pulse), int(80 + 60 * pulse), 220)
        else:
            color = (50, 45, 60)
        pygame.draw.ellipse(surf, color, r)
        pygame.draw.ellipse(surf, (20, 15, 30), r, 4)


class Level2:
    """The Cursed Kingdom - ruined streets, church, cemetery, and the Ghost King."""
    name = "The Cursed Kingdom"

    def __init__(self):
        self.width = 4800
        self.height = 720
        self.ground_y = 560
        self.solids = [pygame.Rect(0, self.ground_y, self.width, 200)]
        self.checkpoints = [Checkpoint(x, self.ground_y) for x in (500, 1900, 3400)]
        self.portal = Portal(self.width - 220, self.ground_y)
        self.enemies = pygame.sprite.Group()
        self._spawn_enemies()
        self.boss = None
        self.boss_spawn_x = self.width - 500
        self.boss_triggered = False
        self.quest_state = {"souls_saved": False, "relics_collected": False, "boss_defeated": False, "portal_open": False}

    def _spawn_enemies(self):
        layout = [(Ghost, 900), (Ghost, 1300), (DarkKnight, 1700), (Ghost, 2200), (Ghost, 2600), (DarkKnight, 3100), (Ghost, 3500)]
        for cls, x in layout:
            self.enemies.add(cls(x, self.ground_y - 20))

    def collision_rects(self):
        return self.solids

    def current_quest_text(self):
        if not self.quest_state["souls_saved"]:
            return "Free the trapped souls"
        if not self.quest_state["boss_defeated"]:
            return "Defeat the Ghost King"
        return "Open the castle gate"

    def update(self, dt, player, particle_system):
        for cp in self.checkpoints:
            if not cp.activated and player.hitbox.colliderect(cp.rect.inflate(20, 20)):
                cp.activated = True

        if player.pos.x > self.boss_spawn_x - 400 and self.boss is None and not self.boss_triggered:
            self.boss_triggered = True
            self.boss = GhostKing(self.boss_spawn_x, self.ground_y - 40)

        if self.boss is not None:
            self.boss.update(dt, player, self.solids, particle_system)
            if self.boss.is_dead and self.boss.death_timer <= 0 and not self.quest_state["boss_defeated"]:
                self.quest_state["boss_defeated"] = True
                self.portal.active = True

        if self.portal.active:
            self.quest_state["portal_open"] = True

        for e in list(self.enemies):
            e.update(dt, player, self.solids, particle_system)

    def check_portal_reached(self, player):
        return self.portal.active and player.hitbox.colliderect(self.portal.rect)

    def draw_background(self, surf, cam, t):
        w, h = surf.get_size()
        for y in range(h):
            ratio = y / h
            color = tuple(int(12 + (24 - 12) * ratio) for _ in range(3))
            pygame.draw.line(surf, color, (0, y), (w, y))

    def draw_world(self, surf, cam, t):
        ground_rect = cam.apply(pygame.Rect(0, self.ground_y, self.width, self.height))
        pygame.draw.rect(surf, (22, 24, 30), ground_rect)
        for x in range(0, self.width, 40):
            sx, sy = cam.apply_pos(x, self.ground_y)
            pygame.draw.rect(surf, (38, 42, 54), (sx, sy, 40, 10))

        for cp in self.checkpoints:
            r = cam.apply(cp.rect)
            pygame.draw.rect(surf, (130, 180, 220) if cp.activated else (90, 90, 110), r, border_radius=4)

        for x in range(200, self.width, 700):
            rx, ry = cam.apply_pos(x, self.ground_y - 30)
            pygame.draw.rect(surf, (55, 60, 74), (rx, ry, 24, 70))
            pygame.draw.rect(surf, (35, 38, 44), (rx + 6, ry - 12, 12, 20))

        self._draw_portal(surf, cam, t)
        if self.boss is not None:
            self.boss.draw(surf, cam)
        for e in self.enemies:
            e.draw(surf, cam)

    def _draw_portal(self, surf, cam, t):
        r = cam.apply(self.portal.rect)
        if self.portal.active:
            pulse = 0.5 + 0.5 * math.sin(t * 4)
            color = (int(100 + 80 * pulse), int(140 + 40 * pulse), 220)
        else:
            color = (70, 70, 90)
        pygame.draw.ellipse(surf, color, r)
        pygame.draw.ellipse(surf, (18, 18, 24), r, 4)


class Level3:
    """Dragon's Castle - lava rivers, chains, and the Dragon King boss."""
    name = "Dragon's Castle"

    def __init__(self):
        self.width = 4800
        self.height = 720
        self.ground_y = 560
        self.solids = [pygame.Rect(0, self.ground_y, self.width, 200)]
        self.checkpoints = [Checkpoint(x, self.ground_y) for x in (500, 1900, 3400)]
        self.portal = Portal(self.width - 220, self.ground_y)
        self.enemies = pygame.sprite.Group()
        self.boss = None
        self.boss_spawn_x = self.width - 500
        self.boss_triggered = False
        self.quest_state = {"dragon_defeated": False, "portal_open": False}

    def collision_rects(self):
        return self.solids

    def current_quest_text(self):
        if not self.quest_state["dragon_defeated"]:
            return "Defeat the Dragon King"
        return "Escape the castle"

    def update(self, dt, player, particle_system):
        for cp in self.checkpoints:
            if not cp.activated and player.hitbox.colliderect(cp.rect.inflate(20, 20)):
                cp.activated = True

        if player.pos.x > self.boss_spawn_x - 350 and self.boss is None and not self.boss_triggered:
            self.boss_triggered = True
            self.boss = DragonBoss(self.boss_spawn_x, self.ground_y - 50)

        if self.boss is not None:
            self.boss.update(dt, player, self.solids, particle_system)
            if self.boss.is_dead and self.boss.death_timer <= 0 and not self.quest_state["dragon_defeated"]:
                self.quest_state["dragon_defeated"] = True
                self.portal.active = True

        if self.portal.active:
            self.quest_state["portal_open"] = True

    def check_portal_reached(self, player):
        return self.portal.active and player.hitbox.colliderect(self.portal.rect)

    def draw_background(self, surf, cam, t):
        w, h = surf.get_size()
        for y in range(h):
            ratio = y / h
            color = tuple(int(35 + (95 - 35) * ratio) for _ in range(3))
            pygame.draw.line(surf, color, (0, y), (w, y))

    def draw_world(self, surf, cam, t):
        ground_rect = cam.apply(pygame.Rect(0, self.ground_y, self.width, self.height))
        pygame.draw.rect(surf, (48, 24, 22), ground_rect)
        for x in range(0, self.width, 80):
            sx, sy = cam.apply_pos(x, self.ground_y)
            pygame.draw.rect(surf, (70, 34, 24), (sx, sy, 80, 14))

        for x in range(200, self.width, 800):
            rx, ry = cam.apply_pos(x, self.ground_y - 120)
            pygame.draw.rect(surf, (90, 80, 90), (rx, ry, 40, 120))
            pygame.draw.rect(surf, (45, 38, 50), (rx + 12, ry - 20, 16, 30))
            pygame.draw.line(surf, (255, 120, 30), (rx + 20, ry + 120), (rx + 20, ry + 180), 3)

        self._draw_portal(surf, cam, t)
        if self.boss is not None:
            self.boss.draw(surf, cam)

    def _draw_portal(self, surf, cam, t):
        r = cam.apply(self.portal.rect)
        if self.portal.active:
            pulse = 0.5 + 0.5 * math.sin(t * 4)
            color = (int(180 + 60 * pulse), int(80 + 40 * pulse), 40)
        else:
            color = (70, 40, 30)
        pygame.draw.ellipse(surf, color, r)
        pygame.draw.ellipse(surf, (24, 12, 8), r, 4)