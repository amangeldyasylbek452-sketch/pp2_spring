"""
systems/assetgen.py

Procedural pixel-art generator. Every sprite, tile, particle and UI
element used by the game is synthesized at startup onto small Surfaces
(drawn pixel-by-pixel with pygame.draw primitives) and then scaled up
with nearest-neighbour scaling so it reads as crisp pixel art.

This keeps the project fully self-contained (no external binary asset
files to ship) while still producing a consistent hand-authored look,
since every shape/palette/animation frame is defined in code.

All surfaces are cached by AssetManager so generation only happens once.
"""
from __future__ import annotations
import math
import random
import pygame
from core.settings import PIXEL_SCALE


def scale_up(surf: pygame.Surface, factor: int = PIXEL_SCALE) -> pygame.Surface:
    w, h = surf.get_size()
    return pygame.transform.scale(surf, (w * factor, h * factor))


class AssetManager:
    """Generates and caches every pixel-art surface used in the game."""

    def __init__(self) -> None:
        self._cache: dict[str, pygame.Surface] = {}
        self._rand = random.Random(1337)

    # ------------------------------------------------------------ generic
    def get(self, key: str, factory):
        if key not in self._cache:
            self._cache[key] = factory()
        return self._cache[key]

    # ------------------------------------------------------------ tiles
    def tile(self, kind: str) -> pygame.Surface:
        return self.get(f"tile_{kind}", lambda: self._make_tile(kind))

    def _make_tile(self, kind: str) -> pygame.Surface:
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        r = self._rand
        if kind == "ground":
            base = (54, 46, 40)
            s.fill(base)
            for _ in range(10):
                x, y = r.randrange(16), r.randrange(16)
                shade = (base[0] + r.randint(-10, 14), base[1] + r.randint(-8, 12), base[2] + r.randint(-8, 10))
                s.set_at((x, y), shade)
            pygame.draw.line(s, (30, 24, 20), (0, 0), (15, 0), 1)
        elif kind == "stone":
            base = (72, 70, 78)
            s.fill(base)
            for _ in range(14):
                x, y = r.randrange(16), r.randrange(16)
                s.set_at((x, y), (base[0] + r.randint(-16, 18),) * 3)
            pygame.draw.rect(s, (40, 38, 44), (0, 0, 16, 16), 1)
        elif kind == "cliff":
            s.fill((44, 40, 50))
            for i in range(0, 16, 4):
                pygame.draw.line(s, (30, 28, 36), (0, i), (16, i), 1)
            for _ in range(8):
                s.set_at((r.randrange(16), r.randrange(16)), (60, 56, 66))
        elif kind == "path":
            s.fill((80, 68, 52))
            for _ in range(8):
                s.set_at((r.randrange(16), r.randrange(16)), (94, 80, 60))
        elif kind == "grass_top":
            s.fill((54, 46, 40))
            for x in range(0, 16, 2):
                h = r.randint(2, 5)
                pygame.draw.line(s, (58, 90, 46), (x, 6 - h), (x, 6), 1)
        return s

    # ------------------------------------------------------------ parallax backgrounds
    def parallax_layer(self, index: int, w: int, h: int) -> pygame.Surface:
        return self.get(f"parallax_{index}_{w}_{h}", lambda: self._make_parallax(index, w, h))

    def _make_parallax(self, index: int, w: int, h: int) -> pygame.Surface:
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        r = random.Random(90 + index)
        # sky gradient
        top = (18, 18, 40) if index == 0 else (0, 0, 0, 0)
        if index == 0:
            for y in range(h):
                t = y / h
                col = (
                    int(14 + t * 10),
                    int(14 + t * 14),
                    int(38 + t * 30),
                )
                pygame.draw.line(s, col, (0, y), (w, y))
            # moon
            pygame.draw.circle(s, (210, 216, 235), (int(w * 0.78), int(h * 0.18)), 34)
            pygame.draw.circle(s, (170, 178, 205), (int(w * 0.78) - 10, int(h * 0.18) - 6), 30)
            # stars
            for _ in range(140):
                x, y = r.randrange(w), r.randrange(int(h * 0.6))
                b = r.randint(120, 230)
                s.set_at((x, y), (b, b, b))
        elif index == 1:
            # far mountains silhouette
            base_y = int(h * 0.62)
            pts = [(0, h)]
            x = 0
            while x <= w:
                base_y2 = base_y + int(40 * math.sin(x / 220.0) + r.randint(-6, 6))
                pts.append((x, base_y2))
                x += 40
            pts.append((w, h))
            pygame.draw.polygon(s, (26, 22, 44), pts)
        elif index == 2:
            base_y = int(h * 0.74)
            pts = [(0, h)]
            x = 0
            while x <= w:
                base_y2 = base_y + int(26 * math.sin(x / 140.0 + 1.5) + r.randint(-8, 8))
                pts.append((x, base_y2))
                x += 30
            pts.append((w, h))
            pygame.draw.polygon(s, (18, 14, 30), pts)
            # dead trees silhouette
            for _ in range(int(w / 90)):
                tx = r.randrange(w)
                ty = base_y + 10
                pygame.draw.line(s, (14, 12, 22), (tx, ty), (tx + r.randint(-6, 6), ty - r.randint(18, 34)), 2)
        return s

    # ------------------------------------------------------------ humanoid sprite helper
    def _draw_humanoid(self, size, palette, pose: dict) -> pygame.Surface:
        """Draws a simple articulated pixel humanoid onto a small surface.
        pose keys: leg_swing(-1..1), arm_swing(-1..1), arm_raise(0..1),
        crouch(0..1), lean(-1..1), flash(bool)
        """
        w, h = size
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        body, trim, skin, dark = palette["body"], palette["trim"], palette["skin"], palette["dark"]
        if pose.get("flash"):
            body, trim, skin, dark = (255, 255, 255), (255, 255, 255), (255, 240, 220), (230, 230, 230)

        crouch = int(pose.get("crouch", 0) * 3)
        lean = pose.get("lean", 0)
        cx = w // 2 + int(lean * 2)
        top = 2 + crouch

        # legs
        leg_swing = pose.get("leg_swing", 0)
        lx1 = cx - 3 + int(leg_swing * 3)
        lx2 = cx + 1 - int(leg_swing * 3)
        leg_y = h - 6 + crouch
        pygame.draw.rect(s, dark, (lx1, leg_y, 3, 6 - crouch))
        pygame.draw.rect(s, dark, (lx2, leg_y, 3, 6 - crouch))

        # torso
        torso_h = 10 - crouch
        pygame.draw.rect(s, body, (cx - 4, top + 4, 8, torso_h))
        pygame.draw.rect(s, trim, (cx - 4, top + 4, 8, 2))

        # arm (weapon arm)
        arm_swing = pose.get("arm_swing", 0)
        raise_ = pose.get("arm_raise", 0)
        ax = cx + 4
        ay = top + 6 - int(raise_ * 6)
        pygame.draw.rect(s, skin, (ax, ay, 2, 5 + int(arm_swing * 2)))
        # off arm
        pygame.draw.rect(s, skin, (cx - 6, top + 6, 2, 5))

        # head
        pygame.draw.rect(s, skin, (cx - 3, top, 6, 5))
        pygame.draw.rect(s, dark, (cx - 3, top, 6, 2))  # helmet band

        # weapon (sword) when arm raised / attacking
        if pose.get("weapon", True):
            wx = ax + 2
            wy = ay - int(raise_ * 10) - int(arm_swing * 4)
            pygame.draw.line(s, (200, 200, 210), (wx, wy), (wx + 6, wy - 6), 2)
            pygame.draw.line(s, (150, 110, 40), (wx, wy), (wx - 2, wy + 3), 2)

        if pose.get("shield"):
            pygame.draw.rect(s, trim, (cx - 8, top + 5, 3, 7))
            pygame.draw.rect(s, dark, (cx - 8, top + 5, 3, 1))

        return s

    def player_frame(self, action: str, index: int) -> pygame.Surface:
        key = f"player_{action}_{index}"
        return self.get(key, lambda: self._make_player_frame(action, index))

    def _make_player_frame(self, action: str, index: int) -> pygame.Surface:
        palette = {"body": (70, 90, 130), "trim": (200, 175, 90), "skin": (216, 178, 140), "dark": (40, 44, 60)}
        pose = {"weapon": True, "shield": action in ("idle", "walk", "run", "block")}
        t = index / 6.0
        if action == "idle":
            pose["leg_swing"] = 0
            pose["arm_swing"] = math.sin(t * math.pi * 2) * 0.15
        elif action in ("walk", "run", "sprint"):
            pose["leg_swing"] = math.sin(t * math.pi * 2)
            pose["arm_swing"] = math.sin(t * math.pi * 2 + math.pi)
        elif action == "attack1":
            pose["arm_raise"] = min(1.0, index * 0.5)
            pose["shield"] = False
        elif action == "attack2":
            pose["arm_raise"] = 1.0
            pose["lean"] = 1
            pose["shield"] = False
        elif action == "attack3":
            pose["arm_raise"] = 1.0
            pose["lean"] = -1
            pose["shield"] = False
        elif action == "roll":
            pose["crouch"] = 1
            pose["leg_swing"] = 1 if index % 2 == 0 else -1
        elif action == "block":
            pose["shield"] = True
            pose["crouch"] = 0.3
        elif action == "hurt":
            pose["lean"] = -1
            pose["flash"] = index == 0
        elif action == "death":
            pose["crouch"] = min(1.0, index * 0.4)
        surf = self._draw_humanoid((16, 22), palette, pose)
        return scale_up(surf)

    def enemy_frame(self, kind: str, action: str, index: int) -> pygame.Surface:
        key = f"enemy_{kind}_{action}_{index}"
        return self.get(key, lambda: self._make_enemy_frame(kind, action, index))

    def _make_enemy_frame(self, kind: str, action: str, index: int) -> pygame.Surface:
        palettes = {
            "skeleton": {"body": (210, 205, 190), "trim": (120, 30, 30), "skin": (210, 205, 190), "dark": (150, 145, 132)},
            "archer": {"body": (200, 196, 182), "trim": (40, 90, 60), "skin": (200, 196, 182), "dark": (140, 136, 122)},
            "captain": {"body": (225, 215, 190), "trim": (170, 30, 30), "skin": (225, 215, 190), "dark": (120, 40, 40)},
        }
        palette = palettes.get(kind, palettes["skeleton"])
        pose = {"weapon": True, "shield": kind == "captain" and action in ("idle", "walk")}
        t = index / 6.0
        size = (18, 26) if kind == "captain" else (14, 20)
        if action == "idle":
            pose["arm_swing"] = math.sin(t * math.pi * 2) * 0.1
        elif action == "walk":
            pose["leg_swing"] = math.sin(t * math.pi * 2)
        elif action == "attack":
            pose["arm_raise"] = 1.0
            pose["lean"] = 1
        elif action == "hurt":
            pose["flash"] = index == 0
            pose["lean"] = -1
        elif action == "death":
            pose["crouch"] = min(1.0, index * 0.4)
        surf = self._draw_humanoid(size, palette, pose)
        return scale_up(surf)

    def bat_frame(self, index: int) -> pygame.Surface:
        key = f"bat_{index}"
        return self.get(key, lambda: self._make_bat_frame(index))

    def _make_bat_frame(self, index: int) -> pygame.Surface:
        s = pygame.Surface((16, 12), pygame.SRCALPHA)
        flap = math.sin(index / 4.0 * math.pi * 2)
        wing_y = 5 - int(flap * 3)
        pygame.draw.polygon(s, (30, 26, 40), [(8, 6), (0, wing_y), (5, 7)])
        pygame.draw.polygon(s, (30, 26, 40), [(8, 6), (16, wing_y), (11, 7)])
        pygame.draw.ellipse(s, (44, 38, 54), (6, 4, 5, 5))
        return scale_up(s)

    # ------------------------------------------------------------ particles
    def particle(self, kind: str) -> pygame.Surface:
        return self.get(f"particle_{kind}", lambda: self._make_particle(kind))

    def _make_particle(self, kind: str) -> pygame.Surface:
        s = pygame.Surface((4, 4), pygame.SRCALPHA)
        if kind == "spark":
            pygame.draw.circle(s, (255, 230, 140), (2, 2), 2)
        elif kind == "dust":
            pygame.draw.circle(s, (150, 140, 120, 180), (2, 2), 2)
        elif kind == "rain":
            s = pygame.Surface((2, 10), pygame.SRCALPHA)
            pygame.draw.line(s, (150, 170, 210, 160), (1, 0), (1, 10), 1)
        elif kind == "ember":
            pygame.draw.circle(s, (255, 140, 40), (2, 2), 2)
        elif kind == "leaf":
            pygame.draw.circle(s, (90, 100, 50), (2, 2), 2)
        elif kind == "ghost":
            pygame.draw.circle(s, (140, 220, 190, 140), (2, 2), 2)
        elif kind == "magic":
            pygame.draw.circle(s, (170, 110, 220), (2, 2), 2)
        return scale_up(s, 2)

    # ------------------------------------------------------------ icons / props
    def relic_icon(self) -> pygame.Surface:
        return self.get("relic_icon", self._make_relic_icon)

    def _make_relic_icon(self) -> pygame.Surface:
        s = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.polygon(s, (170, 110, 220), [(6, 0), (11, 6), (6, 11), (1, 6)])
        pygame.draw.polygon(s, (220, 180, 250), [(6, 2), (9, 6), (6, 9), (3, 6)])
        return scale_up(s, 4)

    def potion_icon(self) -> pygame.Surface:
        return self.get("potion_icon", self._make_potion_icon)

    def _make_potion_icon(self) -> pygame.Surface:
        s = pygame.Surface((10, 12), pygame.SRCALPHA)
        pygame.draw.rect(s, (120, 200, 100), (2, 4, 6, 7))
        pygame.draw.rect(s, (80, 60, 50), (4, 0, 2, 4))
        return scale_up(s, 4)

    def gold_icon(self) -> pygame.Surface:
        return self.get("gold_icon", self._make_gold_icon)

    def _make_gold_icon(self) -> pygame.Surface:
        s = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(s, (212, 175, 55), (5, 5), 4)
        pygame.draw.circle(s, (240, 210, 110), (4, 4), 2)
        return scale_up(s, 4)

    # ------------------------------------------------------------ NPC portrait
    def portrait(self, name: str, palette_seed: int) -> pygame.Surface:
        return self.get(f"portrait_{name}", lambda: self._make_portrait(palette_seed))

    def _make_portrait(self, seed: int) -> pygame.Surface:
        r = random.Random(seed)
        s = pygame.Surface((24, 24), pygame.SRCALPHA)
        skin = (216, 178 + r.randint(-10, 10), 140)
        hair = r.choice([(60, 40, 30), (30, 30, 34), (150, 140, 120), (90, 60, 40)])
        s.fill((0, 0, 0, 0))
        pygame.draw.rect(s, skin, (6, 6, 12, 14))
        pygame.draw.rect(s, hair, (5, 3, 14, 5))
        pygame.draw.rect(s, (40, 40, 44), (8, 12, 2, 2))
        pygame.draw.rect(s, (40, 40, 44), (14, 12, 2, 2))
        cloak = r.choice([(90, 40, 40), (40, 70, 90), (70, 60, 40), (60, 40, 80)])
        pygame.draw.rect(s, cloak, (4, 18, 16, 6))
        return scale_up(s, 4)
