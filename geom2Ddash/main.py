"""Playable entrypoint for the GeoCube Runner prototype with a main menu, worlds, skins, and JSON save data."""
import os
import sys

import pygame

import config
from audio import AudioEngine
from level import Camera, Level
from particles import ParticleSystem
from player import Player
from save_store import load_save_data, save_save_data
from skins import SKINS, SkinManager


def get_world_options():
    return config.WORLDS


def build_game(width=None, height=None, save_data=None, save_path=None):
    pygame.init()
    width = width or config.DEFAULT_WIDTH
    height = height or config.DEFAULT_HEIGHT
    try:
        screen = pygame.display.set_mode((width, height))
    except pygame.error:
        screen = pygame.Surface((width, height))
    try:
        pygame.display.set_caption(config.WINDOW_TITLE)
    except pygame.error:
        pass

    if save_data is None:
        save_data, save_path = load_save_data(save_path)
    skin_manager = SkinManager(save_data)

    world_id = save_data.get("last_world_id") or config.WORLDS[0]["id"]
    world = next((item for item in config.WORLDS if item["id"] == world_id), config.WORLDS[0])
    level = Level(world, width, height)
    particles = ParticleSystem()
    audio = AudioEngine()
    player = Player(140, level.ground_y, skin_manager)
    camera = Camera(width)

    return {
        "screen": screen,
        "clock": pygame.time.Clock(),
        "level": level,
        "player": player,
        "camera": camera,
        "particles": particles,
        "audio": audio,
        "world": world,
        "background_t": 0.0,
        "running": True,
        "paused": False,
        "state": "menu",
        "menu_selection": 0,
        "menu_message": "Select an option",
        "menu_buttons": [],
        "save_data": save_data,
        "save_path": save_path,
        "skin_manager": skin_manager,
        "world_index": next((idx for idx, item in enumerate(config.WORLDS) if item["id"] == world["id"]), 0),
    }


def reset_round(game):
    world = game["world"]
    screen = game["screen"]
    level = Level(world, screen.get_width(), screen.get_height())
    game["level"] = level
    game["player"].reset(140, level.ground_y)
    game["camera"] = Camera(screen.get_width())
    game["background_t"] = 0.0
    game["paused"] = False


def start_run(game):
    game["state"] = "playing"
    game["paused"] = False
    reset_round(game)


def activate_menu_selection(game):
    if game["menu_selection"] == 0:
        start_run(game)
    elif game["menu_selection"] == 1:
        select_world(game, 1)
    elif game["menu_selection"] == 2:
        game["state"] = "skin_menu"
        game["menu_message"] = "Choose a skin"
    elif game["menu_selection"] == 3:
        game["running"] = False


def handle_menu_click(game, pos):
    for idx, rect in enumerate(game.get("menu_buttons", [])):
        if rect.collidepoint(pos):
            game["menu_selection"] = idx
            activate_menu_selection(game)
            return True
    return False


def select_world(game, offset):
    world_options = get_world_options()
    game["world_index"] = (game["world_index"] + offset) % len(world_options)
    game["world"] = world_options[game["world_index"]]
    game["save_data"]["last_world_id"] = game["world"]["id"]
    save_save_data(game["save_data"], game["save_path"])


def cycle_skin(game, offset):
    skin_ids = [skin["id"] for skin in SKINS]
    current = game["save_data"].get("equipped_skin", "classic")
    index = skin_ids.index(current) if current in skin_ids else 0
    candidate = skin_ids[(index + offset) % len(skin_ids)]
    if candidate in game["save_data"].get("unlocked_skins", ["classic"]):
        game["save_data"]["equipped_skin"] = candidate
        save_save_data(game["save_data"], game["save_path"])
        game["menu_message"] = f"Equipped {candidate}"
    else:
        game["menu_message"] = f"Unlock {candidate} first"


def unlock_default_skins(save_data):
    if "classic" not in save_data.get("unlocked_skins", ["classic"]):
        save_data["unlocked_skins"] = ["classic"]
    if "ice" not in save_data["unlocked_skins"]:
        save_data["unlocked_skins"].append("ice")
    if "fire" not in save_data["unlocked_skins"]:
        save_data["unlocked_skins"].append("fire")


def draw_text(surface, text, x, y, color=(255, 255, 255), size=24):
    font = pygame.font.SysFont("consolas", size)
    rendered = font.render(text, True, color)
    surface.blit(rendered, (x, y))


def draw_menu(game):
    screen = game["screen"]
    screen.fill((8, 10, 22))
    draw_text(screen, "GeoCube Runner", 80, 70, (120, 220, 255), 40)
    draw_text(screen, "A faster, longer, and more custom adventure", 80, 120, (220, 220, 240), 20)

    options = ["Play", f"World: {game['world']['name']}", "Skins", "Quit"]
    buttons = []
    for idx, label in enumerate(options):
        color = (255, 220, 120) if idx == game["menu_selection"] else (230, 235, 245)
        y = 220 + idx * 58
        rect = pygame.Rect(70, y - 6, 340, 42)
        buttons.append(rect)
        pygame.draw.rect(screen, (26, 30, 42), rect, border_radius=10)
        draw_text(screen, label, 90, y, color, 24)

    draw_text(screen, f"Coins: {game['save_data'].get('coins', 0)}", 80, 420, (255, 205, 80), 24)
    draw_text(screen, f"Equipped: {game['save_data'].get('equipped_skin', 'classic')}", 80, 456, (140, 220, 255), 24)
    draw_text(screen, game["menu_message"], 80, 492, (210, 230, 255), 20)
    game["menu_buttons"] = buttons
    return buttons


def draw_skin_menu(game):
    screen = game["screen"]
    screen.fill((8, 10, 22))
    draw_text(screen, "Skin Selection", 80, 70, (120, 220, 255), 36)
    draw_text(screen, "Left/Right to switch, Enter to equip", 80, 118, (220, 220, 240), 20)

    unlocked = set(game["save_data"].get("unlocked_skins", ["classic"]))
    current = game["save_data"].get("equipped_skin", "classic")
    for idx, skin in enumerate(SKINS):
        label = f"{skin['name']}"
        if skin["id"] in unlocked:
            label += " [unlocked]"
        else:
            label += f" [cost {skin['cost']}]"
        if skin["id"] == current:
            label += " <- equipped"
        color = (255, 220, 120) if skin["id"] == current else (230, 235, 245)
        y = 190 + idx * 32
        draw_text(screen, label, 90, y, color, 20)

    draw_text(screen, "Esc to return", 80, 500, (180, 200, 220), 20)


def run():
    if os.name == "nt" and os.environ.get("SDL_VIDEODRIVER") is None:
        os.environ.setdefault("SDL_AUDIODRIVER", "directsound")

    save_data, save_path = load_save_data()
    unlock_default_skins(save_data)
    save_save_data(save_data, save_path)
    game = build_game(save_data=save_data, save_path=save_path)
    screen = game["screen"]
    clock = game["clock"]

    while game["running"]:
        dt = min(clock.tick(config.FPS) / 1000.0, 0.033)
        game["background_t"] += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game["running"] = False
            elif event.type == pygame.KEYDOWN:
                if game["state"] == "menu":
                    if event.key in (pygame.K_UP, pygame.K_w):
                        game["menu_selection"] = (game["menu_selection"] - 1) % 4
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        game["menu_selection"] = (game["menu_selection"] + 1) % 4
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        activate_menu_selection(game)
                    elif event.key == pygame.K_LEFT:
                        if game["menu_selection"] == 1:
                            select_world(game, -1)
                    elif event.key == pygame.K_RIGHT:
                        if game["menu_selection"] == 1:
                            select_world(game, 1)
                elif game["state"] == "skin_menu":
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        cycle_skin(game, -1)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        cycle_skin(game, 1)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        game["state"] = "menu"
                    elif event.key == pygame.K_ESCAPE:
                        game["state"] = "menu"
                else:
                    if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                        game["player"].request_jump()
                    elif event.key == pygame.K_r:
                        reset_round(game)
                    elif event.key == pygame.K_ESCAPE:
                        game["paused"] = not game["paused"]
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if game["state"] == "menu":
                        handle_menu_click(game, event.pos)
                    elif game["state"] == "skin_menu":
                        game["state"] = "menu"
            elif event.type == pygame.KEYUP:
                if game["state"] == "playing":
                    if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                        game["player"].release_jump()

        if game["state"] == "playing":
            player = game["player"]
            level = game["level"]
            particles = game["particles"]
            audio = game["audio"]
            camera = game["camera"]

            if not game["paused"]:
                if pygame.key.get_pressed()[pygame.K_SPACE] or pygame.key.get_pressed()[pygame.K_UP] or pygame.key.get_pressed()[pygame.K_w]:
                    player.request_jump()

                result = level.update(dt, player, particles, audio, double_jump_enabled=True)
                particles.update(dt)
                camera.follow(player.x)
                camera.update(dt)

                if result == "coin":
                    game["save_data"]["coins"] = game["save_data"].get("coins", 0) + 1
                    save_save_data(game["save_data"], game["save_path"])
                    game["menu_message"] = "+1 coin"
                elif result == "finished":
                    game["save_data"]["coins"] = game["save_data"].get("coins", 0) + 5
                    save_save_data(game["save_data"], game["save_path"])
                    game["menu_message"] = "World cleared! +5 coins"
                    reset_round(game)
                elif result == "dead":
                    game["menu_message"] = "Try again!"
                    reset_round(game)

            screen.fill((12, 14, 24))
            level.draw_background(screen, camera.x, game["background_t"])
            level.draw_ground(screen, camera.x)
            level.draw_obstacles(screen, camera.x)
            level.draw_finish(screen, camera.x)
            particles.draw(screen, camera.x)
            player.draw(screen, camera.x)

            pygame.draw.rect(screen, (20, 24, 32), pygame.Rect(16, 16, 260, 92), border_radius=10)
            draw_text(screen, "SPACE/JUMP  R=restart  ESC=pause", 28, 30, (235, 238, 245), 20)
            draw_text(screen, f"World: {level.world['name']}  Progress: {int(level.percent_complete(player.x))}%", 28, 56, (140, 220, 255), 20)
            draw_text(screen, f"Coins: {game['save_data'].get('coins', 0)}", 28, 82, (255, 205, 80), 20)
        elif game["state"] == "skin_menu":
            draw_skin_menu(game)
        else:
            buttons = draw_menu(game)

        pygame.display.flip()

    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(run())
