import os
import json
import random
import math
import pygame

from settings import SCREEN_W, SCREEN_H, FPS, TITLE, KEY_ATTACK, KEY_DASH, KEY_INTERACT, KEY_PAUSE
from player import Player
from level import Level1, Level2, Level3
from camera import Camera
from particles import ParticleSystem
from ui import UI
from save import load_game, save_game, has_save
from quest_system import QuestSystem
from dialogue_system import DialogueSystem
from inventory import Inventory
from audio import AudioManager
from event_bus import EventBus


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0.0
        self.time = 0.0
        self.state = "menu"
        self.current_level_index = 0
        self.levels = [Level1(), Level2(), Level3()]
        self.level = self.levels[0]
        self.event_bus = EventBus()
        self.player = Player(180, 520, event_bus=self.event_bus)
        self.camera = Camera(self.level.width, self.level.height)
        self.particles = ParticleSystem()
        # Asset manager for images, sounds and fonts (graceful fallback)
        from assets import AssetManager
        self.assets = AssetManager("data")
        # UI and font resources loaded through AssetManager (falls back to system fonts)
        self.ui = UI(self.assets.load_font("arial", 18), self.assets.load_font("arial", 24), self.assets.load_font("arial", 42))
        self.font = self.assets.load_font("arial", 20)
        self.quest_system = QuestSystem("data/quests.json")
        self.dialogue_system = DialogueSystem("data/dialogue.json")
        self.inventory = Inventory("data/items.json")
        self.audio = AudioManager()
        self.inventory.add("potion", 3)
        self.inventory.add("sword")
        self.inventory.add("shield")
        self.menu_options = ["New Game", "Continue", "Settings", "Credits", "Quit"]
        self.menu_index = 0
        self.paused = False
        self.show_inventory = False
        self.show_quests = False
        self.dialogue_queue = []
        self.dialogue_index = 0
        self._load_or_init_save()
        self._seed_ambient_events()
        # Load and play background music via AssetManager (graceful if missing)
        music = self.assets.load_sound("soundtrack.wav")
        if music:
            self.audio.play_music(music)

    def _seed_ambient_events(self):
        self.ambient_timer = random.uniform(4, 10)
        self.screamer_timer = random.uniform(12, 25)

    def _load_or_init_save(self):
        self.save_slot = "manual"
        self.save_data = load_game(self.save_slot) or {}

    def run(self):
        while self.running:
            # Tick once per frame to cap FPS and compute delta-time
            self.dt = min(self.clock.tick(FPS) / 1000.0, 0.03)
            self.time += self.dt
            self.handle_events()
            self.update()
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "game":
                        self.paused = not self.paused
                    elif self.state == "menu":
                        self.running = False
                elif self.state == "menu":
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.menu_index = (self.menu_index - 1) % len(self.menu_options)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.menu_index = (self.menu_index + 1) % len(self.menu_options)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self._handle_menu_action(self.menu_options[self.menu_index])
                elif self.state == "game":
                    if event.key == KEY_ATTACK:
                        self.player.try_attack()
                    elif event.key == KEY_DASH:
                        self.player.try_dash(pygame.Vector2(1 if self.player.facing > 0 else -1, 0), self.particles)
                    elif event.key == KEY_INTERACT:
                        self._try_interact()
                    elif event.key == KEY_PAUSE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_i:
                        self.show_inventory = not self.show_inventory
                    elif event.key == pygame.K_q:
                        self.show_quests = not self.show_quests
                    elif event.key == pygame.K_l:
                        save_game(self.player, self.level.name, self.level.quest_state, self.save_slot)
                    elif event.key == pygame.K_t:
                        self.ui.start_dialogue("Queen", "The curse is breaking. Rise, knight.")

    def _handle_menu_action(self, option):
        if option == "New Game":
            self._start_new_game()
        elif option == "Continue":
            self._continue_game()
        elif option == "Settings":
            self.state = "menu"
        elif option == "Credits":
            self.state = "menu"
        elif option == "Quit":
            self.running = False

    def _start_new_game(self):
        self.player = Player(180, 520, event_bus=self.event_bus)
        self.levels = [Level1(), Level2(), Level3()]
        self.level = self.levels[0]
        self.current_level_index = 0
        self.camera = Camera(self.level.width, self.level.height)
        self.state = "game"
        self.paused = False
        self.show_inventory = False
        self.show_quests = False
        self.ui.start_dialogue("Queen", self.dialogue_system.get_text("queen", "intro"))
        self.quest_system = QuestSystem("data/quests.json")

    def _continue_game(self):
        data = load_game(self.save_slot)
        if data:
            self.player = Player(data["position"][0], data["position"][1], event_bus=self.event_bus)
            self.player.hp = data["hp"]
            self.player.max_hp = data.get("max_hp", 100)
            self.player.gold = data.get("gold", 0)
            self.player.inventory = data.get("inventory", self.player.inventory)
            self.level = self._level_for_name(data.get("level", "The Haunted Mountains"))
            self.quest_system = QuestSystem("data/quests.json")
            self.dialogue_system = DialogueSystem("data/dialogue.json")
            self.inventory = Inventory("data/items.json")
            self.current_level_index = self._level_index_for_name(self.level.name)
            self.camera = Camera(self.level.width, self.level.height)
            self.state = "game"
            self.paused = False
        else:
            self._start_new_game()

    def _level_for_name(self, level_name):
        for level in self.levels:
            if level.name == level_name:
                return level
        return self.levels[0]

    def _level_index_for_name(self, level_name):
        for idx, level in enumerate(self.levels):
            if level.name == level_name:
                return idx
        return 0

    def update(self):
        # dt and time are updated once per frame in run()
        if self.state != "game":
            return
        if self.paused:
            return

        keys = pygame.key.get_pressed()
        self.player.handle_input(keys, self.dt, self.particles)
        self.level.update(self.dt, self.player, self.particles)
        self.player.update(self.dt, self.level.collision_rects())
        self.particles.update(self.dt)
        self.ui.update(self.dt)
        self.camera.update(self.player.rect, self.dt)
        self._handle_level_progression()
        self._update_ambient_events()

    def _handle_level_progression(self):
        if self.level.check_portal_reached(self.player):
            self.current_level_index += 1
            if self.current_level_index < len(self.levels):
                self.level = self.levels[self.current_level_index]
                self.player.pos.x = 120
                self.player.pos.y = self.level.ground_y - 40
                self.player.hitbox.center = self.player.pos
                self.player.rect.center = self.player.hitbox.center
                self.camera = Camera(self.level.width, self.level.height)
                self.ui.start_dialogue("Queen", self.dialogue_system.get_text("queen", "mid"))
            else:
                self.state = "victory"

    def _update_ambient_events(self):
        self.ambient_timer -= self.dt
        self.screamer_timer -= self.dt
        if self.ambient_timer <= 0:
            self.ambient_timer = random.uniform(5, 12)
            self.particles.shake(2, 0.08)
        if self.screamer_timer <= 0:
            self.screamer_timer = random.uniform(18, 35)
            if random.random() < 0.4:
                self.particles.shake(8, 0.14)

    def draw(self):
        self.screen.fill((8, 8, 16))
        if self.state == "menu":
            self._draw_menu()
        elif self.state == "game":
            self._draw_game()
        elif self.state == "victory":
            self._draw_victory()
        pygame.display.flip()

    def _draw_menu(self):
        self.screen.fill((8, 10, 20))
        self._draw_text("THE CURSED KINGDOM", 42, 120, (220, 180, 120))
        self._draw_text("A pixel-art gothic action adventure", 24, 180, (185, 185, 190))
        y = 280
        for idx, option in enumerate(self.menu_options):
            color = (255, 220, 140) if idx == self.menu_index else (190, 190, 190)
            self._draw_text(f"> {option}", 28, y + idx * 48, color)
        if has_save():
            info = "A save file is available."
            self._draw_text(info, 20, 520, (120, 220, 120))

    def _draw_game(self):
        self.level.draw_background(self.screen, self.camera, self.time)
        self.particles.draw_world(self.screen, self.camera)
        self.level.draw_world(self.screen, self.camera, self.time)
        self.player.draw(self.screen, self.camera)
        self.ui.draw_hud(self.screen, self.player, self.level.current_quest_text(), (self.level.width, self.level.height, self.player.pos.x, self.player.pos.y, []))
        self._draw_quest_panel()
        self._draw_inventory_panel()
        if self.paused:
            self._draw_overlay("Paused", "Press ESC to resume")
        elif self.show_inventory:
            self._draw_overlay("Inventory", "Sword, Shield, Potion, Crystal")
        elif self.show_quests:
            self._draw_overlay("Quests", self.level.current_quest_text())
        self.ui.draw_dialogue_box(self.screen)

    def _draw_victory(self):
        self.screen.fill((10, 14, 20))
        self._draw_text("The Queen is rescued", 40, 220, (220, 180, 120))
        self._draw_text("The curse is broken. Morning rises over the kingdom.", 24, 280, (190, 190, 190))
        self._draw_text("Press ESC to quit", 22, 360, (140, 220, 140))

    def _draw_overlay(self, title, body):
        overlay = pygame.Surface((640, 300), pygame.SRCALPHA)
        overlay.fill((20, 20, 24, 220))
        pygame.draw.rect(overlay, (212, 175, 55), (0, 0, 640, 300), 3)
        self.screen.blit(overlay, (320, 210))
        self._draw_text(title, 30, 240, (212, 175, 55))
        self._draw_text(body, 24, 300, (230, 230, 230))

    def _draw_quest_panel(self):
        if not self.show_quests:
            return
        panel = pygame.Surface((360, 220), pygame.SRCALPHA)
        panel.fill((20, 20, 24, 220))
        pygame.draw.rect(panel, (212, 175, 55), (0, 0, 360, 220), 2)
        self.screen.blit(panel, (80, 120))
        self._draw_text("Quests", 24, 132, (212, 175, 55))
        for idx, quest in enumerate(self.quest_system.quests):
            label = f"- {quest['title']}"
            self._draw_text(label, 20, 168 + idx * 24, (235, 235, 240))

    def _draw_inventory_panel(self):
        if not self.show_inventory:
            return
        panel = pygame.Surface((360, 220), pygame.SRCALPHA)
        panel.fill((20, 20, 24, 220))
        pygame.draw.rect(panel, (212, 175, 55), (0, 0, 360, 220), 2)
        self.screen.blit(panel, (840, 120))
        self._draw_text("Inventory", 24, 132, (212, 175, 55))
        for idx, item in enumerate(self.inventory.get_items()):
            label = f"- {item['id']} x{item.get('count', 1)}"
            self._draw_text(label, 20, 168 + idx * 24, (235, 235, 240))

    def _draw_text(self, text, size, y, color):
        font = pygame.font.SysFont("arial", size)
        surf = font.render(text, True, color)
        self.screen.blit(surf, (SCREEN_W // 2 - surf.get_width() // 2, y))

    def _try_interact(self):
        self.ui.start_dialogue("Priest", self.dialogue_system.get_text("priest", "intro"))
        self.quest_system.complete("intro")
