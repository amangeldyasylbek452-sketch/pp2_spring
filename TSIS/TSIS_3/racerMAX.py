import json
import os
import random
import pygame
import sys
import time

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.path.join(BASE_DIR, 'settings.json')
LEADERBOARD_PATH = os.path.join(BASE_DIR, 'leaderboard.json')

# Default settings
DEFAULT_SETTINGS = {
    'sound': True,
    'car_color': 'red',
    'difficulty': 'normal',
    'username': '',
}

# Difficulty parameters
DIFFICULTY_PARAMS = {
    'easy': {
        'traffic_rate': 0.012,
        'obstacle_rate': 0.007,
        'powerup_rate': 0.0014,
        'scroll_speed': 4,
    },
    'normal': {
        'traffic_rate': 0.018,
        'obstacle_rate': 0.01,
        'powerup_rate': 0.0011,
        'scroll_speed': 5,
    },
    'hard': {
        'traffic_rate': 0.026,
        'obstacle_rate': 0.013,
        'powerup_rate': 0.0009,
        'scroll_speed': 6,
    },
}

CAR_COLORS = {
    'red': (210, 35, 35),
    'blue': (35, 120, 210),
    'green': (35, 180, 70),
    'yellow': (220, 180, 25),
}

SCREEN_WIDTH = 820
SCREEN_HEIGHT = 640
ROAD_LEFT = 120
ROAD_WIDTH = 460
LANE_COUNT = 3
LANE_WIDTH = ROAD_WIDTH // LANE_COUNT
LANES = [ROAD_LEFT + LANE_WIDTH // 2 + i * LANE_WIDTH for i in range(LANE_COUNT)]
ROAD_END_DISTANCE = 4500

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Racer MAX')
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 24)
large_font = pygame.font.SysFont(None, 40)
score_font = pygame.font.SysFont(None, 28)

# Load settings and leaderboard

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception:
            return default.copy()
    return default.copy()


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2)

settings = load_json(SETTINGS_PATH, DEFAULT_SETTINGS)
leaderboard = load_json(LEADERBOARD_PATH, [])

if 'difficulty' not in settings:
    settings['difficulty'] = DEFAULT_SETTINGS['difficulty']
if 'sound' not in settings:
    settings['sound'] = DEFAULT_SETTINGS['sound']
if 'car_color' not in settings:
    settings['car_color'] = DEFAULT_SETTINGS['car_color']
if 'username' not in settings:
    settings['username'] = ''

save_json(SETTINGS_PATH, settings)

button_sound = None
try:
    button_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, 'click.wav'))
except Exception:
    button_sound = None


def play_sound(sound):
    if settings.get('sound', True) and sound is not None:
        sound.play()


def draw_text(text, x, y, color=(255, 255, 255), center=False, font_obj=None):
    font_obj = font_obj or font
    surface = font_obj.render(str(text), True, color)
    rect = surface.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surface, rect)
    return rect


def rect_button(text, rect, active=True):
    color = (230, 230, 230) if active else (130, 130, 130)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, (0, 0, 0), rect, 2)
    draw_text(text, rect.centerx, rect.centery, color=(0, 0, 0), center=True)


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def build_top_scores(entries):
    sorted_entries = sorted(entries, key=lambda item: item['score'], reverse=True)
    return sorted_entries[:10]


def update_leaderboard(name, score, distance):
    global leaderboard
    leaderboard.append({'name': name or 'Player', 'score': score, 'distance': int(distance)})
    leaderboard = build_top_scores(leaderboard)
    save_json(LEADERBOARD_PATH, leaderboard)


def draw_main_menu():
    screen.fill((28, 60, 30))
    draw_text('RACER MAX', SCREEN_WIDTH // 2, 80, color=(255, 230, 80), center=True, font_obj=large_font)
    draw_text('Choose an option', SCREEN_WIDTH // 2, 130, center=True)
    buttons = []
    labels = ['Play', 'Leaderboard', 'Settings', 'Quit']
    for idx, label in enumerate(labels):
        rect = pygame.Rect(SCREEN_WIDTH // 2 - 120, 180 + idx * 80, 240, 55)
        rect_button(label, rect)
        buttons.append((label.lower(), rect))
    return buttons


def draw_leaderboard_screen():
    screen.fill((15, 20, 60))
    draw_text('Leaderboard', SCREEN_WIDTH // 2, 45, color=(255, 255, 200), center=True, font_obj=large_font)
    y = 110
    draw_text('Rank', 160, y, color=(255, 255, 255))
    draw_text('Name', 260, y, color=(255, 255, 255))
    draw_text('Score', 520, y, color=(255, 255, 255))
    draw_text('Distance', 650, y, color=(255, 255, 255))
    y += 35
    for idx, entry in enumerate(leaderboard[:10], start=1):
        draw_text(f'{idx}', 160, y)
        draw_text(entry['name'], 260, y)
        draw_text(entry['score'], 520, y)
        draw_text(entry['distance'], 650, y)
        y += 32
    back_rect = pygame.Rect(320, 540, 180, 45)
    rect_button('Back', back_rect)
    return back_rect


def draw_settings_screen(selected_index):
    screen.fill((25, 25, 40))
    draw_text('Settings', SCREEN_WIDTH // 2, 40, color=(255, 220, 220), center=True, font_obj=large_font)
    sound_text = f"Sound: {'On' if settings['sound'] else 'Off'}"
    draw_text(sound_text, 180, 140)
    sound_rect = pygame.Rect(100, 130, 260, 45)
    rect_button(sound_text, sound_rect)

    color_text = f"Car color: {settings['car_color'].capitalize()}"
    color_rect = pygame.Rect(100, 200, 260, 45)
    rect_button(color_text, color_rect)

    difficulty_text = f"Difficulty: {settings['difficulty'].capitalize()}"
    difficulty_rect = pygame.Rect(100, 270, 260, 45)
    rect_button(difficulty_text, difficulty_rect)

    name_text = f"Player name: {settings.get('username', '') or 'Enter name'}"
    name_rect = pygame.Rect(100, 340, 260, 45)
    rect_button(name_text, name_rect)

    back_rect = pygame.Rect(320, 540, 180, 45)
    rect_button('Back', back_rect)
    return [('sound', sound_rect), ('color', color_rect), ('difficulty', difficulty_rect), ('name', name_rect), ('back', back_rect)]


def draw_game_over_screen(score, distance, coins, winner):
    screen.fill((60, 10, 10))
    draw_text('Game Over', SCREEN_WIDTH // 2, 70, color=(255, 220, 220), center=True, font_obj=large_font)
    draw_text(f'Score: {score}', SCREEN_WIDTH // 2, 150, center=True)
    draw_text(f'Distance: {int(distance)} m', SCREEN_WIDTH // 2, 190, center=True)
    draw_text(f'Coins: {coins}', SCREEN_WIDTH // 2, 230, center=True)
    if winner:
        draw_text('Finish line reached!', SCREEN_WIDTH // 2, 270, center=True, color=(255, 235, 120))
    retry_rect = pygame.Rect(160, 520, 180, 55)
    menu_rect = pygame.Rect(470, 520, 180, 55)
    rect_button('Retry', retry_rect)
    rect_button('Main Menu', menu_rect)
    return retry_rect, menu_rect


def draw_game_screen(game_state):
    screen.fill((20, 35, 20))
    pygame.draw.rect(screen, (55, 55, 55), (ROAD_LEFT, 0, ROAD_WIDTH, SCREEN_HEIGHT))
    for i in range(12):
        line_x = ROAD_LEFT + LANE_WIDTH * (i % LANE_COUNT) + LANE_WIDTH // 2
        pygame.draw.line(screen, (100, 100, 100), (line_x, 0), (line_x, SCREEN_HEIGHT), 2)

    offset = int(game_state['scroll_offset'])
    for i in range(-2, SCREEN_HEIGHT // 40 + 4):
        y = (i * 40 + offset) % SCREEN_HEIGHT
        pygame.draw.rect(screen, (220, 220, 220), (SCREEN_WIDTH // 2 - 4, y, 8, 30))

    draw_text(f"Distance: {int(game_state['distance'])} / {ROAD_END_DISTANCE} m", 30, 10)
    draw_text(f"Remaining: {max(0, ROAD_END_DISTANCE - int(game_state['distance']))} m", 30, 34)
    draw_text(f"Score: {game_state['score']}", 30, 58)
    draw_text(f"Coins: {game_state['coins']}", 30, 82)
    active_text = 'None'
    if game_state['active_powerup']:
        active_text = f"{game_state['active_powerup'].capitalize()} ({int(game_state['powerup_timer'])}s)"
    draw_text(f"Power-up: {active_text}", 30, 106)
    draw_text(f"Player: {settings.get('username', '') or 'Guest'}", 30, 130)

    color = CAR_COLORS.get(settings['car_color'], (255, 0, 0))
    pygame.draw.rect(screen, color, (*game_state['player_pos'], 40, 60), border_radius=10)
    pygame.draw.polygon(screen, (220, 220, 220), [(game_state['player_pos'][0] + 10, game_state['player_pos'][1] + 20), (game_state['player_pos'][0] + 30, game_state['player_pos'][1] + 20), (game_state['player_pos'][0] + 40, game_state['player_pos'][1] + 40), (game_state['player_pos'][0], game_state['player_pos'][1] + 40)])

    for traffic in game_state['traffic']:
        pygame.draw.rect(screen, (180, 20, 20), (*traffic['pos'], 40, 60), border_radius=8)
    for obstacle in game_state['obstacles']:
        if obstacle['type'] == 'oil':
            pygame.draw.circle(screen, (30, 30, 30), obstacle['pos'], 22)
        elif obstacle['type'] == 'barrier':
            pygame.draw.rect(screen, (140, 70, 30), (*obstacle['pos'], 40, 40))
        elif obstacle['type'] == 'pothole':
            pygame.draw.circle(screen, (80, 80, 80), obstacle['pos'], 18)
    for powerup in game_state['powerups']:
        color_map = {'nitro': (255, 120, 20), 'shield': (40, 180, 240), 'repair': (190, 255, 120)}
        pygame.draw.circle(screen, color_map.get(powerup['type'], (255, 255, 255)), powerup['pos'], 15)
        draw_text(powerup['type'][0].upper(), powerup['pos'][0] - 5, powerup['pos'][1] - 10, color=(0, 0, 0))

    if game_state['event_strips']:
        for strip in game_state['event_strips']:
            pygame.draw.rect(screen, (255, 120, 120), (*strip['pos'], strip['width'], 12))

    if game_state['event_effect']:
        draw_text(f"Event: {game_state['event_effect'].capitalize()}", SCREEN_WIDTH - 140, 10)
    elif settings['sound']:
        draw_text('Sound: On', SCREEN_WIDTH - 140, 10)
    else:
        draw_text('Sound: Off', SCREEN_WIDTH - 140, 10)


def spawn_traffic(game_state):
    lane = random.randrange(LANE_COUNT)
    x = LANES[lane] - 20
    y = -80
    if abs(game_state['player_pos'][1] - y) < 120:
        return
    if game_state['player_lane'] == lane and random.random() < 0.4:
        return
    game_state['traffic'].append({'pos': [x, y], 'lane': lane})


def spawn_obstacle(game_state):
    lane = random.randrange(LANE_COUNT)
    x = LANES[lane] - 20
    y = -60
    if abs(game_state['player_pos'][1] - y) < 100:
        return
    obstacle_type = random.choice(['oil', 'barrier', 'pothole'])
    game_state['obstacles'].append({'pos': [x, y], 'type': obstacle_type, 'lane': lane})


def spawn_powerup(game_state):
    lane = random.randrange(LANE_COUNT)
    x = LANES[lane]
    y = -50
    if any(abs(x - p['pos'][0]) < 10 and abs(y - p['pos'][1]) < 80 for p in game_state['powerups']):
        return
    ptype = random.choice(['nitro', 'shield', 'repair'])
    game_state['powerups'].append({'pos': [x, y], 'type': ptype, 'lane': lane, 'spawn_time': time.time()})


def spawn_event_strip(game_state):
    lane = random.randrange(LANE_COUNT)
    x = LANES[lane] - 40
    y = -12
    game_state['event_strips'].append({'pos': [x, y], 'width': 80, 'type': random.choice(['boost', 'bump'])})


def reset_game():
    return {
        'player_lane': 1,
        'player_pos': [LANES[1] - 20, SCREEN_HEIGHT - 120],
        'speed': DIFFICULTY_PARAMS[settings['difficulty']]['scroll_speed'],
        'base_speed': DIFFICULTY_PARAMS[settings['difficulty']]['scroll_speed'],
        'scroll_offset': 0,
        'traffic': [],
        'obstacles': [],
        'powerups': [],
        'event_strips': [],
        'coins': 0,
        'score': 0,
        'distance': 0,
        'active_powerup': None,
        'powerup_timer': 0,
        'powerup_bonus': 0,
        'event_effect': None,
        'event_timer': 0,
        'crash_protected': False,
        'timer': 0,
        'last_spawn': 0,
        'last_obstacle': 0,
        'last_powerup': 0,
        'last_event': 0,
        'safe_path': [],
    }


def handle_collision(game_state):
    player_rect = pygame.Rect(*game_state['player_pos'], 40, 60)
    for traffic in list(game_state['traffic']):
        traffic_rect = pygame.Rect(*traffic['pos'], 40, 60)
        if player_rect.colliderect(traffic_rect):
            if game_state['active_powerup'] == 'shield':
                game_state['active_powerup'] = None
                game_state['powerup_timer'] = 0
                game_state['traffic'].remove(traffic)
                game_state['score'] += 50
            else:
                return True
    for obstacle in list(game_state['obstacles']):
        ox, oy = obstacle['pos']
        obstacle_rect = pygame.Rect(ox - 20, oy - 20, 40, 40) if obstacle['type'] != 'oil' else pygame.Rect(ox - 22, oy - 22, 44, 44)
        if player_rect.colliderect(obstacle_rect):
            if game_state['active_powerup'] == 'shield':
                game_state['active_powerup'] = None
                game_state['powerup_timer'] = 0
                game_state['obstacles'].remove(obstacle)
                game_state['score'] += 40
            else:
                if obstacle['type'] == 'oil':
                    game_state['speed'] = max(2, game_state['speed'] - 3)
                    game_state['obstacles'].remove(obstacle)
                elif obstacle['type'] == 'bump':
                    game_state['speed'] = max(2, game_state['speed'] - 2)
                    game_state['obstacles'].remove(obstacle)
                elif obstacle['type'] == 'pothole':
                    return True
                else:
                    return True
    for strip in list(game_state['event_strips']):
        strip_rect = pygame.Rect(*strip['pos'], strip['width'], 12)
        if player_rect.colliderect(strip_rect):
            if strip['type'] == 'boost':
                game_state['event_effect'] = 'boost'
                game_state['event_timer'] = 3.0
                game_state['speed'] = game_state['base_speed'] + 5
                game_state['score'] += 25
            elif strip['type'] == 'bump':
                game_state['event_effect'] = 'bump'
                game_state['event_timer'] = 1.5
                game_state['speed'] = max(2, game_state['speed'] - 2)
            game_state['event_strips'].remove(strip)
    return False


def update_powerups(game_state, dt):
    now = time.time()
    for powerup in list(game_state['powerups']):
        if now - powerup['spawn_time'] > 8:
            game_state['powerups'].remove(powerup)

    if game_state['active_powerup']:
        game_state['powerup_timer'] -= dt
        if game_state['powerup_timer'] <= 0:
            if game_state['active_powerup'] == 'nitro':
                game_state['speed'] = game_state['base_speed']
            game_state['active_powerup'] = None
            game_state['powerup_timer'] = 0

    if game_state['event_effect']:
        game_state['event_timer'] -= dt
        if game_state['event_timer'] <= 0:
            if game_state['event_effect'] == 'boost':
                game_state['speed'] = game_state['base_speed']
            elif game_state['event_effect'] == 'bump':
                game_state['speed'] = max(2, game_state['base_speed'])
            game_state['event_effect'] = None
            game_state['event_timer'] = 0


def collect_powerups(game_state):
    player_rect = pygame.Rect(*game_state['player_pos'], 40, 60)
    for powerup in list(game_state['powerups']):
        p_rect = pygame.Rect(powerup['pos'][0] - 15, powerup['pos'][1] - 15, 30, 30)
        if player_rect.colliderect(p_rect):
            if game_state['active_powerup'] is None:
                game_state['active_powerup'] = powerup['type']
                if powerup['type'] == 'nitro':
                    game_state['speed'] = game_state['base_speed'] + 4
                    game_state['powerup_timer'] = random.randint(3, 5)
                elif powerup['type'] == 'shield':
                    game_state['powerup_timer'] = 999
                elif powerup['type'] == 'repair':
                    game_state['score'] += 80
                    game_state['powerup_timer'] = 0
                game_state['powerups'].remove(powerup)
                play_sound(button_sound)
            else:
                game_state['powerups'].remove(powerup)
            break


def update_game(game_state, dt):
    params = DIFFICULTY_PARAMS[settings['difficulty']]
    game_state['scroll_offset'] += game_state['speed']
    game_state['distance'] += game_state['speed']
    if game_state['distance'] >= ROAD_END_DISTANCE:
        return 'finish'

    game_state['score'] = int(game_state['distance'] * 0.12 + game_state['coins'] * 50 + game_state['powerup_bonus'])
    now = time.time()
    pace = 1.0 + min(game_state['distance'] / 1200.0, 1.5)
    traffic_rate = min(0.08, params['traffic_rate'] * pace)
    obstacle_rate = min(0.06, params['obstacle_rate'] * pace)
    powerup_rate = min(0.032, params['powerup_rate'] * (1.0 + game_state['distance'] / 10000.0))
    event_rate = min(0.02, 0.007 * pace)

    if random.random() < traffic_rate and now - game_state['last_spawn'] > 0.4:
        spawn_traffic(game_state)
        game_state['last_spawn'] = now
    if random.random() < obstacle_rate and now - game_state['last_obstacle'] > 0.8:
        spawn_obstacle(game_state)
        game_state['last_obstacle'] = now
    if random.random() < powerup_rate and now - game_state['last_powerup'] > 3.0:
        spawn_powerup(game_state)
        game_state['last_powerup'] = now
    if random.random() < event_rate and now - game_state['last_event'] > 4.0:
        spawn_event_strip(game_state)
        game_state['last_event'] = now

    for traffic in list(game_state['traffic']):
        traffic['pos'][1] += game_state['speed'] + 1
        if traffic['pos'][1] > SCREEN_HEIGHT + 80:
            game_state['traffic'].remove(traffic)
    for obstacle in list(game_state['obstacles']):
        obstacle['pos'][1] += game_state['speed'] * 0.7
        if obstacle['pos'][1] > SCREEN_HEIGHT + 60:
            game_state['obstacles'].remove(obstacle)
    for powerup in list(game_state['powerups']):
        powerup['pos'][1] += game_state['speed'] * 0.8
        if powerup['pos'][1] > SCREEN_HEIGHT + 40:
            game_state['powerups'].remove(powerup)
    for strip in list(game_state['event_strips']):
        strip['pos'][1] += game_state['speed'] * 0.6
        if strip['pos'][1] > SCREEN_HEIGHT + 20:
            game_state['event_strips'].remove(strip)

    collect_powerups(game_state)
    update_powerups(game_state, dt)

    if handle_collision(game_state):
        return 'crash'
    return 'running'


def move_player(game_state, direction):
    if direction == 'left':
        game_state['player_lane'] = clamp(game_state['player_lane'] - 1, 0, LANE_COUNT - 1)
    elif direction == 'right':
        game_state['player_lane'] = clamp(game_state['player_lane'] + 1, 0, LANE_COUNT - 1)
    game_state['player_pos'][0] = LANES[game_state['player_lane']] - 20


def main():
    screen_state = 'menu'
    running = True
    selected_setting = 0
    game_state = reset_game()
    username_input = settings.get('username', '')
    name_active = False
    username_message = ''
    play_name_prompt = False

    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if screen_state == 'menu':
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    buttons = draw_main_menu()
                    for label, rect in buttons:
                        if rect.collidepoint(event.pos):
                            play_sound(button_sound)
                            if label == 'play':
                                if not settings.get('username'):
                                    play_name_prompt = True
                                    screen_state = 'name'
                                else:
                                    game_state = reset_game()
                                    screen_state = 'playing'
                            elif label == 'leaderboard':
                                screen_state = 'leaderboard'
                            elif label == 'settings':
                                screen_state = 'settings'
                            elif label == 'quit':
                                running = False

            elif screen_state == 'leaderboard':
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    back_rect = draw_leaderboard_screen()
                    if back_rect.collidepoint(event.pos):
                        play_sound(button_sound)
                        screen_state = 'menu'

            elif screen_state == 'settings':
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    items = draw_settings_screen(selected_setting)
                    for key, rect in items:
                        if rect.collidepoint(event.pos):
                            play_sound(button_sound)
                            if key == 'sound':
                                settings['sound'] = not settings['sound']
                            elif key == 'color':
                                choices = list(CAR_COLORS.keys())
                                index = choices.index(settings['car_color'])
                                settings['car_color'] = choices[(index + 1) % len(choices)]
                            elif key == 'difficulty':
                                choices = list(DIFFICULTY_PARAMS.keys())
                                index = choices.index(settings['difficulty'])
                                settings['difficulty'] = choices[(index + 1) % len(choices)]
                            elif key == 'name':
                                name_active = True
                            elif key == 'back':
                                screen_state = 'menu'
                            save_json(SETTINGS_PATH, settings)

                if event.type == pygame.KEYDOWN and name_active:
                    if event.key == pygame.K_RETURN:
                        settings['username'] = username_input.strip()[:12]
                        name_active = False
                        save_json(SETTINGS_PATH, settings)
                    elif event.key == pygame.K_BACKSPACE:
                        username_input = username_input[:-1]
                    elif event.unicode and len(username_input) < 12:
                        username_input += event.unicode

            elif screen_state == 'name':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        settings['username'] = username_input.strip()[:12] or 'Player'
                        save_json(SETTINGS_PATH, settings)
                        game_state = reset_game()
                        screen_state = 'playing'
                    elif event.key == pygame.K_ESCAPE:
                        screen_state = 'menu'
                    elif event.key == pygame.K_BACKSPACE:
                        username_input = username_input[:-1]
                    elif event.unicode and len(username_input) < 12:
                        username_input += event.unicode

            elif screen_state == 'playing':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        move_player(game_state, 'left')
                    elif event.key == pygame.K_RIGHT:
                        move_player(game_state, 'right')
                    elif event.key == pygame.K_ESCAPE:
                        screen_state = 'menu'

            elif screen_state == 'gameover':
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    retry_rect, menu_rect = draw_game_over_screen(game_state['score'], game_state['distance'], game_state['coins'], game_state.get('winner', False))
                    if retry_rect.collidepoint(event.pos):
                        play_sound(button_sound)
                        game_state = reset_game()
                        screen_state = 'playing'
                    elif menu_rect.collidepoint(event.pos):
                        play_sound(button_sound)
                        screen_state = 'menu'

        if screen_state == 'menu':
            buttons = draw_main_menu()
        elif screen_state == 'leaderboard':
            draw_leaderboard_screen()
        elif screen_state == 'settings':
            draw_settings_screen(selected_setting)
            if name_active:
                draw_text('Enter name: ' + username_input, 420, 340, color=(255, 255, 255))
        elif screen_state == 'name':
            screen.fill((20, 35, 20))
            draw_text('Enter your name:', SCREEN_WIDTH // 2, 220, center=True, font_obj=large_font)
            draw_text(username_input + '|', SCREEN_WIDTH // 2, 300, center=True)
            draw_text('Press Enter to start or Esc to cancel', SCREEN_WIDTH // 2, 360, center=True)
        elif screen_state == 'playing':
            result = update_game(game_state, dt)
            draw_game_screen(game_state)
            if result in ('crash', 'finish'):
                game_state['winner'] = result == 'finish'
                update_leaderboard(settings.get('username', 'Player'), game_state['score'], game_state['distance'])
                screen_state = 'gameover'
        elif screen_state == 'gameover':
            game_state['score'] = int(game_state['distance'] * 0.12 + game_state['coins'] * 50 + game_state['powerup_bonus'])
            draw_game_over_screen(game_state['score'], game_state['distance'], game_state['coins'], game_state.get('winner', False))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
