"""
ui.py - Medieval-styled HUD: health/stamina bars, boss health bar,
quest tracker, minimap dot, FPS counter, and a typewriter dialogue box.
"""
import pygame
from settings import UI_GOLD, UI_BG, WHITE, BLACK, SCREEN_W, SCREEN_H


class UI:
    def __init__(self, font_small, font_med, font_big):
        self.font_small = font_small
        self.font_med = font_med
        self.font_big = font_big
        self.show_fps = True

        # dialogue state
        self.dialogue_active = False
        self.dialogue_speaker = ""
        self.dialogue_full_text = ""
        self.dialogue_shown_chars = 0
        self.dialogue_timer = 0.0
        self.dialogue_speed = 40  # chars/sec

    # -- dialogue -----------------------------------------------------
    def start_dialogue(self, speaker, text):
        self.dialogue_active = True
        self.dialogue_speaker = speaker
        self.dialogue_full_text = text
        self.dialogue_shown_chars = 0
        self.dialogue_timer = 0.0

    def advance_dialogue(self):
        if self.dialogue_shown_chars < len(self.dialogue_full_text):
            self.dialogue_shown_chars = len(self.dialogue_full_text)
        else:
            self.dialogue_active = False

    def update(self, dt):
        if self.dialogue_active and self.dialogue_shown_chars < len(self.dialogue_full_text):
            self.dialogue_timer += dt * self.dialogue_speed
            self.dialogue_shown_chars = min(len(self.dialogue_full_text), int(self.dialogue_timer))

    # -- draw helpers ---------------------------------------------------
    def _bar(self, surf, x, y, w, h, pct, fg, bg=(20, 18, 22), border=UI_GOLD):
        pygame.draw.rect(surf, bg, (x, y, w, h))
        pygame.draw.rect(surf, fg, (x, y, int(w * max(0, pct)), h))
        pygame.draw.rect(surf, border, (x, y, w, h), 2)

    def draw_hud(self, surf, player, quest_text=None, minimap_info=None, clock=None):
        # Health bar
        self._bar(surf, 24, 24, 260, 22, player.hp / player.max_hp, (170, 30, 40))
        label = self.font_small.render(f"HP {int(player.hp)}/{player.max_hp}", True, WHITE)
        surf.blit(label, (30, 27))

        # Stamina bar
        self._bar(surf, 24, 52, 200, 12, player.stamina / player.max_stamina, (60, 140, 200))

        # Inventory quick display (gold / potions)
        inv_text = f"Gold: {player.gold}   Potions: {player.inventory.get('potion', 0)}"
        surf.blit(self.font_small.render(inv_text, True, UI_GOLD), (24, 70))

        # Quest tracker (top-right)
        if quest_text:
            box = pygame.Surface((300, 70), pygame.SRCALPHA)
            box.fill((*UI_BG, 170))
            surf.blit(box, (SCREEN_W - 320, 20))
            pygame.draw.rect(surf, UI_GOLD, (SCREEN_W - 320, 20, 300, 70), 2)
            title = self.font_small.render("Quest", True, UI_GOLD)
            surf.blit(title, (SCREEN_W - 310, 26))
            body = self.font_small.render(quest_text, True, WHITE)
            surf.blit(body, (SCREEN_W - 310, 48))

        # Minimap (simple dot representation, bottom-right)
        if minimap_info:
            mm_rect = pygame.Rect(SCREEN_W - 170, SCREEN_H - 170, 150, 150)
            mm = pygame.Surface(mm_rect.size, pygame.SRCALPHA)
            mm.fill((*UI_BG, 160))
            level_w, level_h, px, py, poi = minimap_info
            dot_x = int(px / level_w * mm_rect.w)
            dot_y = int(py / level_h * mm_rect.h)
            pygame.draw.circle(mm, (90, 200, 255), (dot_x, dot_y), 4)
            for (poix, poiy, color) in poi:
                qx = int(poix / level_w * mm_rect.w)
                qy = int(poiy / level_h * mm_rect.h)
                pygame.draw.circle(mm, color, (qx, qy), 3)
            surf.blit(mm, mm_rect.topleft)
            pygame.draw.rect(surf, UI_GOLD, mm_rect, 2)

        # FPS
        if self.show_fps and clock:
            fps_text = self.font_small.render(f"FPS: {int(clock.get_fps())}", True, (120, 220, 120))
            surf.blit(fps_text, (SCREEN_W - 90, SCREEN_H - 24))

    def draw_boss_bar(self, surf, boss):
        w = 560
        x = SCREEN_W // 2 - w // 2
        y = 40
        self._bar(surf, x, y, w, 20, boss.hp / boss.max_hp, (150, 30, 30))
        label = self.font_med.render(boss.draw_bar_label(), True, WHITE)
        surf.blit(label, (x + w // 2 - label.get_width() // 2, y - 26))

    def draw_dialogue_box(self, surf):
        if not self.dialogue_active:
            return
        box_h = 140
        box = pygame.Surface((SCREEN_W - 120, box_h), pygame.SRCALPHA)
        box.fill((*UI_BG, 230))
        surf.blit(box, (60, SCREEN_H - box_h - 40))
        pygame.draw.rect(surf, UI_GOLD, (60, SCREEN_H - box_h - 40, SCREEN_W - 120, box_h), 3)

        name_tag = self.font_med.render(self.dialogue_speaker, True, UI_GOLD)
        surf.blit(name_tag, (84, SCREEN_H - box_h - 20))

        shown = self.dialogue_full_text[:self.dialogue_shown_chars]
        wrapped = self._wrap(shown, self.font_small, SCREEN_W - 200)
        for i, line in enumerate(wrapped):
            surf.blit(self.font_small.render(line, True, WHITE), (90, SCREEN_H - box_h + 20 + i * 26))

        hint = self.font_small.render("[E] Continue", True, (170, 170, 180))
        surf.blit(hint, (SCREEN_W - 200, SCREEN_H - 60))

    def _wrap(self, text, font, max_w):
        words = text.split(" ")
        lines, cur = [], ""
        for w in words:
            trial = (cur + " " + w).strip()
            if font.size(trial)[0] > max_w:
                lines.append(cur)
                cur = w
            else:
                cur = trial
        if cur:
            lines.append(cur)
        return lines

    def draw_center_text(self, surf, text, y_offset=0, color=UI_GOLD, big=True):
        font = self.font_big if big else self.font_med
        render = font.render(text, True, color)
        surf.blit(render, (SCREEN_W // 2 - render.get_width() // 2, SCREEN_H // 2 + y_offset))