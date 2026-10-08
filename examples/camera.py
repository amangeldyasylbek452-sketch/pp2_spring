"""world/level.py — The Haunted Mountains: the game's first full level.

Builds a hand-authored tilemap (as a simple ASCII layout, in the spirit of
classic level-design tooling), converts it into collision geometry and
tile rendering data, and populates the level with enemies, an NPC, a
relic pickup, a checkpoint, and a boss arena gate.
"""
from __future__ import annotations
import pygame
from core.settings import TILE

try:
    from .enemy import SkeletonWarrior, SkeletonArcher, Bat
except ImportError:
    from enemy import SkeletonWarrior, SkeletonArcher, Bat

try:
    from .boss import SkeletonCaptain
except ImportError:
    from boss import SkeletonCaptain

try:
    from .npc import NPC
except ImportError:
    from npc import NPC

try:
    from .dialogue import DialogueTree, DialogueLine
except ImportError:
    from dialogue import DialogueTree, DialogueLine

# Legend:
# '#' stone ground   'G' grass-topped ground   '.' empty
# '^' cliff wall      'P' player spawn          'E' skeleton
# 'A' archer           'B' bat                   'N' npc survivor
# 'R' relic pickup     'C' checkpoint            'X' boss trigger gate
LAYOUT = [
    "..........................................................................",
    "..........................................................................",
    "..........................................B.............................",
    "..........................................................................",
    "..............A............................................E.............",
    "..............^^....................................^^^^^^^^^^...........",
    "..P...G........................N.........G........................X......",
    "GGGGGGG^^^^^GGGGGGGGGGGGGGRGGGGGGGGGGGGGCGGGGGGGGGGGGGGG^^^^GGGGGGGGGGGGGGG",
    "########################################################################",
    "########################################################################",
]


def build_survivor_dialogue() -> DialogueTree:
    nodes = {
        "start": DialogueLine(
            "Old Hunter Corran",
            "Stranger... you wear the crest of the Queen's Guard. I thought them all dead.",
            choices=[("Ask about the mountains", "mountains"), ("Ask about the Dragon King", "dragon"), ("Leave", "end")],
        ),
        "mountains": DialogueLine(
            "Old Hunter Corran",
            "These peaks were green once. Now the mist eats the light and the bones walk at night.",
            choices=[("Ask about the Dragon King", "dragon"), ("Leave", "end")],
        ),
        "dragon": DialogueLine(
            "Old Hunter Corran",
            "Beyond the ruined watchtower, a captain of bone guards the old pass. Slay him, and the road opens.",
            on_enter="quest_captain_hint",
            choices=[("Leave", "end")],
        ),
        "end": DialogueLine("Old Hunter Corran", "Go well, knight. The kingdom remembers you, even if you don't remember it.", next_id=None),
    }
    return DialogueTree(nodes, start="start")


class Level:
    name = "The Haunted Mountains"
    weather = "rain"

    def __init__(self, game) -> None:
        self.game = game
        self.solids: list[pygame.Rect] = []
        self.decor_tiles: list[tuple[int, int, str]] = []
        self.enemies = []
        self.npcs = []
        self.projectiles = []
        self.relic_pos = None
        self.relic_taken = False
        self.checkpoint_pos = None
        self.boss_gate_x = None
        self.boss_spawned = False
        self.boss = None
        self.player_spawn = (100, 300)
        self.width = len(LAYOUT[0]) * TILE
        self.height = len(LAYOUT) * TILE
        self._parse_layout()

    def _parse_layout(self) -> None:
        for row, line in enumerate(LAYOUT):
            for col, ch in enumerate(line):
                x, y = col * TILE, row * TILE
                if ch in "#":
                    self.solids.append(pygame.Rect(x, y, TILE, TILE))
                    self.decor_tiles.append((x, y, "stone"))
                elif ch == "G":
                    self.solids.append(pygame.Rect(x, y, TILE, TILE))
                    self.decor_tiles.append((x, y, "ground"))
                elif ch == "^":
                    self.solids.append(pygame.Rect(x, y, TILE, TILE))
                    self.decor_tiles.append((x, y, "cliff"))
                elif ch == "P":
                    self.player_spawn = (x, y + TILE)
                elif ch == "E":
                    self.enemies.append(SkeletonWarrior(self.game, x, y))
                elif ch == "A":
                    self.enemies.append(SkeletonArcher(self.game, x, y))
                elif ch == "B":
                    self.enemies.append(Bat(self.game, x, y))
                elif ch == "N":
                    self.npcs.append(NPC(self.game, x, y + TILE, "Old Hunter Corran",
                                          build_survivor_dialogue(), portrait_seed=42))
                elif ch == "R":
                    self.relic_pos = (x, y + TILE)
                elif ch == "C":
                    self.checkpoint_pos = (x, y + TILE)
                elif ch == "X":
                    self.boss_gate_x = x

    def spawn_boss_if_needed(self, player_x: float) -> None:
        if not self.boss_spawned and self.boss_gate_x and player_x > self.boss_gate_x - 40:
            self.boss_spawned = True
            self.boss = SkeletonCaptain(self.game, self.boss_gate_x + 60, 100)
            self.enemies.append(self.boss)
            self.game.on_boss_encounter(self.boss)

    def update(self, dt: float) -> None:
        self.spawn_boss_if_needed(self.game.player.pos.x)
        for e in list(self.enemies):
            e.update(dt, self.solids)
        for n in self.npcs:
            n.update(dt, self.solids)

    def draw_tiles(self, surf: pygame.Surface, assets, cam) -> None:
        cam_x, cam_y = cam.offset()
        for x, y, kind in self.decor_tiles:
            sx, sy = x - cam_x, y - cam_y
            if -TILE < sx < surf.get_width() and -TILE < sy < surf.get_height():
                surf.blit(assets.tile(kind), (sx, sy))
