"""
ui.py
-----
Everything visual that isn't part of the game world: the main menu,
instructions, high score screen, settings, difficulty select, pause menu,
game-over screen, the in-game HUD, and shared decorative background
elements (gradient sky, twinkling stars, drifting clouds).
"""

import math
import random
import pygame

from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SKY_TOP, SKY_BOTTOM, STAR_COLOR,
    CLOUD_COLOR, UI_TEXT, UI_ACCENT, BUTTON_BG, BUTTON_HOVER, BUTTON_BORDER,
    POWERUP_COLORS,
)


# ---------------------------------------------------------------------------
# Small reusable button widget
# ---------------------------------------------------------------------------
class Button:
    def __init__(self, x, y, w, h, label, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.font = font
        self.hovered = False

    def update_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def clicked(self, mouse_pos, mouse_click):
        return mouse_click and self.rect.collidepoint(mouse_pos)

    def draw(self, surface):
        bg = BUTTON_HOVER if self.hovered else BUTTON_BG
        pygame.draw.rect(surface, bg, self.rect, border_radius=10)
        pygame.draw.rect(surface, BUTTON_BORDER, self.rect, width=2, border_radius=10)
        text_surf = self.font.render(self.label, True, UI_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


# ---------------------------------------------------------------------------
# Background decoration (shared by menu + gameplay)
# ---------------------------------------------------------------------------
class Star:
    def __init__(self):
        self.x = random.uniform(0, SCREEN_WIDTH)
        self.y = random.uniform(0, SCREEN_HEIGHT)
        self.radius = random.uniform(1, 2.4)
        self.phase = random.uniform(0, 6.283)

    def draw(self, surface, t):
        twinkle = (math.sin(t * 2 + self.phase) + 1) / 2
        alpha = int(120 + 135 * twinkle)
        s = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(s, (*STAR_COLOR, alpha), (3, 3), max(1, int(self.radius)))
        surface.blit(s, (self.x - 3, self.y - 3))


class Cloud:
    def __init__(self, y=None):
        self.x = random.uniform(-100, SCREEN_WIDTH + 100)
        self.y = y if y is not None else random.uniform(20, SCREEN_HEIGHT * 0.6)
        self.speed = random.uniform(6, 18)
        self.scale = random.uniform(0.6, 1.4)

    def update(self, dt):
        self.x += self.speed * dt
        if self.x > SCREEN_WIDTH + 120:
            self.x = -120

    def draw(self, surface):
        s = self.scale
        alpha = 90
        cloud_surf = pygame.Surface((160 * s, 60 * s), pygame.SRCALPHA)
        color = (*CLOUD_COLOR, alpha)
        pygame.draw.ellipse(cloud_surf, color, (0, 20 * s, 70 * s, 35 * s))
        pygame.draw.ellipse(cloud_surf, color, (35 * s, 5 * s, 90 * s, 45 * s))
        pygame.draw.ellipse(cloud_surf, color, (80 * s, 20 * s, 70 * s, 35 * s))
        surface.blit(cloud_surf, (self.x, self.y))


def draw_gradient_background(surface, top_color=SKY_TOP, bottom_color=SKY_BOTTOM):
    for y in range(SCREEN_HEIGHT):
        t = y / SCREEN_HEIGHT
        color = (
            int(top_color[0] + (bottom_color[0] - top_color[0]) * t),
            int(top_color[1] + (bottom_color[1] - top_color[1]) * t),
            int(top_color[2] + (bottom_color[2] - top_color[2]) * t),
        )
        pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y))


# ---------------------------------------------------------------------------
# Main UI manager
# ---------------------------------------------------------------------------
class UI:
    def __init__(self):
        pygame.font.init()
        self.font_huge = pygame.font.SysFont("arial", 72, bold=True)
        self.font_title = pygame.font.SysFont("arial", 48, bold=True)
        self.font_large = pygame.font.SysFont("arial", 32, bold=True)
        self.font_medium = pygame.font.SysFont("arial", 24)
        self.font_small = pygame.font.SysFont("arial", 18)

        self.stars = [Star() for _ in range(90)]
        self.clouds = [Cloud() for _ in range(6)]
        self.time = 0.0

    def update_background(self, dt):
        self.time += dt
        for cloud in self.clouds:
            cloud.update(dt)

    def draw_background(self, surface):
        draw_gradient_background(surface)
        for star in self.stars:
            star.draw(surface, self.time)
        for cloud in self.clouds:
            cloud.draw(surface)

    # ------------------------------------------------------------------
    def draw_panel(self, surface, rect, alpha=200):
        panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (20, 20, 35, alpha), panel.get_rect(), border_radius=16)
        pygame.draw.rect(panel, UI_ACCENT, panel.get_rect(), width=2, border_radius=16)
        surface.blit(panel, rect.topleft)

    def center_text(self, surface, text, font, color, y, x=None):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(x if x is not None else SCREEN_WIDTH // 2, y))
        surface.blit(surf, rect)
        return rect

    # ------------------------------------------------------------------
    # HUD (during gameplay)
    # ------------------------------------------------------------------
    def draw_hud(self, surface, height, time_survived, coins, high_score, combo, player):
        panel_rect = pygame.Rect(10, 10, 250, 150)
        self.draw_panel(surface, panel_rect, alpha=150)

        lines = [
            f"Height: {int(height)}m",
            f"Time: {time_survived:0.1f}s",
            f"Coins: {coins}",
            f"High Score: {high_score}",
        ]
        for i, line in enumerate(lines):
            surf = self.font_small.render(line, True, UI_TEXT)
            surface.blit(surf, (24, 20 + i * 26))

        if combo > 1:
            combo_surf = self.font_medium.render(f"x{combo} combo!", True, UI_ACCENT)
            surface.blit(combo_surf, (SCREEN_WIDTH - combo_surf.get_width() - 24, 20))

        # active power-up icons, top-right
        active = [(k, v) for k, v in player.powerups.items() if (v > 0 if k != "shield" else v > 0)]
        for i, (kind, value) in enumerate(active):
            x = SCREEN_WIDTH - 46 - i * 50
            y = 60
            color = POWERUP_COLORS.get(kind, (255, 255, 255))
            pygame.draw.circle(surface, color, (x, y), 18)
            pygame.draw.circle(surface, (255, 255, 255), (x, y), 18, 2)
            label = kind.replace("_", " ")
            if kind == "shield":
                text = str(int(value))
            else:
                text = f"{value:0.0f}"
            t_surf = self.font_small.render(text, True, (20, 20, 20))
            surface.blit(t_surf, t_surf.get_rect(center=(x, y)))

    def draw_toast(self, surface, achievement):
        if achievement is None:
            return
        w, h = 340, 60
        rect = pygame.Rect(SCREEN_WIDTH // 2 - w // 2, 20, w, h)
        self.draw_panel(surface, rect, alpha=220)
        title = self.font_small.render("Achievement Unlocked!", True, UI_ACCENT)
        name = self.font_medium.render(achievement.title, True, UI_TEXT)
        surface.blit(title, (rect.x + 16, rect.y + 8))
        surface.blit(name, (rect.x + 16, rect.y + 26))

    # ------------------------------------------------------------------
    # Main menu
    # ------------------------------------------------------------------
    def draw_main_menu(self, surface):
        bob = math.sin(self.time * 2) * 8
        self.center_text(surface, "RISING LAVA BALL", self.font_huge, UI_ACCENT,
                          int(150 + bob), )
        self.center_text(surface, "Climb. Survive. Don't look down.",
                          self.font_medium, UI_TEXT, 215)

        buttons = {}
        labels = ["Play", "High Scores", "Instructions", "Settings", "Quit"]
        start_y = 300
        for i, label in enumerate(labels):
            btn = Button(SCREEN_WIDTH // 2 - 140, start_y + i * 65, 280, 50, label, self.font_large)
            buttons[label] = btn
        return buttons

    def draw_difficulty_menu(self, surface, current):
        self.center_text(surface, "Select Difficulty", self.font_title, UI_ACCENT, 180)
        buttons = {}
        labels = ["Easy", "Normal", "Hard", "Back"]
        start_y = 280
        for i, label in enumerate(labels):
            btn = Button(SCREEN_WIDTH // 2 - 140, start_y + i * 65, 280, 50,
                         label + ("  [selected]" if label == current else ""),
                         self.font_large)
            buttons[label] = btn
        return buttons

    def draw_instructions(self, surface):
        self.center_text(surface, "How To Play", self.font_title, UI_ACCENT, 100)
        lines = [
            "A / Left Arrow  -  Move Left",
            "D / Right Arrow -  Move Right",
            "SPACE           -  Jump (only while on a platform)",
            "",
            "Climb as high as you can while the lava rises below you.",
            "Some platforms move, some vanish after 2 seconds standing on them,",
            "and green ones will bounce you higher!",
            "",
            "Collect coins for score, and grab power-ups:",
            "Double Jump, Slow Lava, High Jump, Shield, Magnet.",
            "",
            "Falling into the lava ends the run - unless a shield saves you!",
            "",
            "P = Pause     F11 = Fullscreen",
        ]
        for i, line in enumerate(lines):
            self.center_text(surface, line, self.font_small, UI_TEXT, 170 + i * 30)

        btn = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 90, 200, 50, "Back", self.font_large)
        return {"Back": btn}

    def draw_highscore_screen(self, surface, high_score, achievements):
        self.center_text(surface, "High Score", self.font_title, UI_ACCENT, 100)
        self.center_text(surface, str(high_score), self.font_huge, UI_TEXT, 180)

        self.center_text(surface, "Achievements", self.font_large, UI_ACCENT, 260)
        y = 300
        for ach in achievements.achievements:
            color = UI_TEXT if ach.unlocked else (110, 110, 120)
            mark = "\u2713" if ach.unlocked else "\u2022"
            text = f"{mark} {ach.title} - {ach.description}"
            self.center_text(surface, text, self.font_small, color, y)
            y += 28

        btn = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 70, 200, 50, "Back", self.font_large)
        return {"Back": btn}

    def draw_settings_menu(self, surface, sfx_volume, fullscreen):
        self.center_text(surface, "Settings", self.font_title, UI_ACCENT, 150)
        self.center_text(surface, f"SFX Volume: {int(sfx_volume * 100)}%", self.font_medium, UI_TEXT, 240)
        self.center_text(surface, f"Fullscreen (F11): {'On' if fullscreen else 'Off'}",
                          self.font_medium, UI_TEXT, 280)

        buttons = {}
        vol_down = Button(SCREEN_WIDTH // 2 - 160, 320, 60, 44, "-", self.font_large)
        vol_up = Button(SCREEN_WIDTH // 2 + 100, 320, 60, 44, "+", self.font_large)
        back = Button(SCREEN_WIDTH // 2 - 100, 420, 200, 50, "Back", self.font_large)
        buttons["vol_down"] = vol_down
        buttons["vol_up"] = vol_up
        buttons["Back"] = back
        return buttons

    # ------------------------------------------------------------------
    # Pause / Game over
    # ------------------------------------------------------------------
    def draw_pause_menu(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        surface.blit(overlay, (0, 0))

        self.center_text(surface, "PAUSED", self.font_title, UI_ACCENT, 220)
        buttons = {}
        labels = ["Resume", "Main Menu", "Quit"]
        for i, label in enumerate(labels):
            btn = Button(SCREEN_WIDTH // 2 - 140, 300 + i * 65, 280, 50, label, self.font_large)
            buttons[label] = btn
        return buttons

    def draw_game_over(self, surface, height, time_survived, coins, score, high_score, is_new_high):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((30, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        self.center_text(surface, "GAME OVER", self.font_huge, (255, 90, 60), 100)
        if is_new_high:
            self.center_text(surface, "NEW HIGH SCORE!", self.font_large, UI_ACCENT, 160)

        stats = [
            f"Height Reached: {int(height)}m",
            f"Time Survived: {time_survived:0.1f}s",
            f"Coins Collected: {coins}",
            f"Score: {score}",
            f"High Score: {high_score}",
        ]
        for i, line in enumerate(stats):
            self.center_text(surface, line, self.font_medium, UI_TEXT, 220 + i * 34)

        buttons = {}
        labels = ["Play Again", "Main Menu", "Quit"]
        start_y = 420
        for i, label in enumerate(labels):
            btn = Button(SCREEN_WIDTH // 2 - 140, start_y + i * 65, 280, 50, label, self.font_large)
            buttons[label] = btn
        return buttons
