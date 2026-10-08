"""examples/game.py — Minimal playable game manager for the examples package."""
from __future__ import annotations
import pygame
from core.settings import SCREEN_W, SCREEN_H, TILE, WHITE, UI_GOLD, UI_BG, UI_BORDER, BLACK

try:
    from .assetgen import AssetManager
except ImportError:
    from assetgen import AssetManager

try:
    from .ai import Camera
except ImportError:
    from ai import Camera

try:
    from .entities.player import Player
except ImportError:
    from entities.player import Player

try:
    from .npc import ParticleSystem
except ImportError:
    from npc import ParticleSystem


class Inventory:
    def __init__(self) -> None:
        self.upgrades: dict[str, int | float] = {}


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("The Cursed Kingdom")
        self.clock = pygame.time.Clock()
        self.assets = AssetManager()
        self.camera = Camera(2400, 1200)
        self.inventory = Inventory()
        self.particles = ParticleSystem(self.assets)
        self.player = Player(self, 180.0, 520.0)
        self.hit_stop_timer = 0.0
        self.running = True
        self.font = pygame.font.SysFont("consolas", 18)
        self.platforms = [
            pygame.Rect(0, 560, 2400, 160),
            pygame.Rect(400, 460, 240, 24),
            pygame.Rect(940, 360, 240, 24),
        ]

    def on_perfect_parry(self, player) -> None:
        pass

    def hit_stop(self, duration: float) -> None:
        self.hit_stop_timer = max(self.hit_stop_timer, duration)

    def spawn_projectile(self, x: float, y: float, direction: int, owner: str, damage: int, kind: str = "arrow"):
        pass

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            if self.hit_stop_timer > 0:
                self.hit_stop_timer = max(0.0, self.hit_stop_timer - dt)
                dt = 0.0
            self._handle_events()
            self._update(dt)
            self._draw()
        pygame.quit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.player.jump()
                elif event.key == pygame.K_j:
                    self.player.try_attack()
                elif event.key in (pygame.K_LCTRL, pygame.K_RCTRL):
                    self.player.try_roll()
                elif event.key == pygame.K_k:
                    self.player.start_block()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_k:
                    self.player.stop_block()

    def _update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        controls = {
            "left": keys[pygame.K_a] or keys[pygame.K_LEFT],
            "right": keys[pygame.K_d] or keys[pygame.K_RIGHT],
        }
        sprint = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        self.player.handle_input(dt, controls, sprint)
        self.player.update(dt, self.platforms)
        self.particles.update(dt)
        self.camera.update(dt, (self.player.pos.x, self.player.pos.y - 20), self.player.facing, self.player.vel.x)

    def _draw(self) -> None:
        self.screen.fill((24, 20, 32))
        for platform in self.platforms:
            rect = pygame.Rect(
                platform.x - self.camera.x,
                platform.y - self.camera.y,
                platform.w,
                platform.h,
            )
            pygame.draw.rect(self.screen, (72, 64, 52), rect)
            pygame.draw.rect(self.screen, (125, 110, 90), rect, 2)

        frame = self.player.current_frame(self.assets)
        player_rect = frame.get_rect(center=(self.player.pos.x - self.camera.x, self.player.pos.y - self.camera.y))
        self.screen.blit(frame, player_rect)

        self.particles.draw(self.screen, self.camera)

        self._draw_hud()
        pygame.display.flip()

    def _draw_hud(self) -> None:
        text_lines = [
            "The Cursed Kingdom (minimal playable demo)",
            "Move: A/D or ←/→  Jump: Space  Attack: J  Roll: Ctrl  Block: K  Quit: Esc",
            f"Health: {self.player.health}/{self.player.max_health}",
        ]
        y = 12
        for line in text_lines:
            surf = self.font.render(line, True, WHITE)
            self.screen.blit(surf, (18, y))
            y += surf.get_height() + 8

        bar_back = pygame.Rect(18, y, 320, 22)
        pygame.draw.rect(self.screen, UI_BG, bar_back)
        pygame.draw.rect(self.screen, UI_BORDER, bar_back, 2)
        health_ratio = max(0.0, min(1.0, self.player.health / self.player.max_health))
        bar_fill = pygame.Rect(20, y + 2, int((bar_back.w - 4) * health_ratio), 18)
        pygame.draw.rect(self.screen, UI_GOLD, bar_fill)


def main() -> None:
    Game().run()


if __name__ == "__main__":
    main()
