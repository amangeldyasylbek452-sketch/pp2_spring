import pygame
import random
import sys

SCREEN_WIDTH = 480
SCREEN_HEIGHT = 680
ROAD_LEFT = 90
ROAD_RIGHT = SCREEN_WIDTH - 90
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT
LANE_COUNT = 3
LANE_WIDTH = ROAD_WIDTH // LANE_COUNT
FPS = 30

FINISH_DISTANCE = 5000000.0
PLAYER_SPEED = 80.0
INITIAL_ENEMY_SPEED = 70.0
MAX_ENEMY_SPEED = 75.0
ENEMY_ACCELERATION = 2.5
COINS_TO_ACCELERATE = 6

COIN_TYPES = [
    {'weight': 1, 'color': (179, 115, 50)},
    {'weight': 2, 'color': (192, 192, 192)},
    {'weight': 3, 'color': (255, 215, 0)},
]
COIN_FALL_SPEED = 200.0
COIN_SPAWN_INTERVAL = 800
OBSTACLE_SPAWN_INTERVAL = 1200

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
DARK_GRAY = (25, 25, 25)
GREEN = (50, 205, 50)
RED = (220, 20, 60)
BLUE = (45, 135, 245)


def draw_text(surface, text, size, x, y, color=WHITE):
    font = pygame.font.SysFont(None, size)
    img = font.render(text, True, color)
    rect = img.get_rect(center=(x, y))
    surface.blit(img, rect)


class Player:
    def __init__(self):
        self.lane = 1
        self.width = 48
        self.height = 80
        self.y = SCREEN_HEIGHT - self.height - 40
        self.cooldown = 0
        self.update_pos()

    def update_pos(self):
        self.x = ROAD_LEFT + self.lane * LANE_WIDTH + LANE_WIDTH // 2

    @property
    def rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y, self.width, self.height)

    def move_left(self):
        self.lane = max(0, self.lane - 1)
        self.update_pos()

    def move_right(self):
        self.lane = min(LANE_COUNT - 1, self.lane + 1)
        self.update_pos()

    def draw(self, surface):
        pygame.draw.rect(surface, BLUE, self.rect)


class Coin:
    def __init__(self):
        t = random.choice(COIN_TYPES)
        self.weight = t['weight']
        self.color = t['color']
        self.lane = random.randrange(LANE_COUNT)
        self.x = ROAD_LEFT + self.lane * LANE_WIDTH + LANE_WIDTH // 2
        self.y = -20
        self.r = 12

    @property
    def rect(self):
        return pygame.Rect(self.x - self.r, self.y - self.r, self.r * 2, self.r * 2)

    def update(self, dt):
        self.y += COIN_FALL_SPEED * dt

    def draw(self, s):
        pygame.draw.circle(s, self.color, (int(self.x), int(self.y)), self.r)


class Obstacle:
    def __init__(self):
        self.lane = random.randrange(LANE_COUNT)
        self.x = ROAD_LEFT + self.lane * LANE_WIDTH + LANE_WIDTH // 2
        self.y = -80
        self.w = 50
        self.h = 80
        self.speed = 250

    @property
    def rect(self):
        return pygame.Rect(self.x - self.w // 2, self.y, self.w, self.h)

    def update(self, dt):
        self.y += self.speed * dt

    def draw(self, s):
        pygame.draw.rect(s, RED, self.rect)


def draw_road(s):
    s.fill(DARK_GRAY)
    pygame.draw.rect(s, GRAY, (ROAD_LEFT, 0, ROAD_WIDTH, SCREEN_HEIGHT))
    for i in range(1, LANE_COUNT):
        x = ROAD_LEFT + i * LANE_WIDTH
        pygame.draw.line(s, WHITE, (x, 0), (x, SCREEN_HEIGHT), 3)


def run():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    while True:
        player = Player()
        coins = []
        obstacles = []

        coin_timer = 0
        obs_timer = 0

        enemy_speed = INITIAL_ENEMY_SPEED
        next_threshold = COINS_TO_ACCELERATE

        score = 0
        coins_collected = 0
        boost = 0

        player_dist = 0
        enemy_dist = 0

        game_over = False

        while True:
            dt = clock.tick(FPS) / 900

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if e.type == pygame.KEYDOWN and game_over:
                    if e.key == pygame.K_r:
                        break

            if game_over:
                break

            keys = pygame.key.get_pressed()

            player.cooldown -= dt

            if keys[pygame.K_LEFT] and player.cooldown <= 0:
                player.move_left()
                player.cooldown = 0.15

            if keys[pygame.K_RIGHT] and player.cooldown <= 0:
                player.move_right()
                player.cooldown = 0.15

            coin_timer += dt * 1000
            if coin_timer >= COIN_SPAWN_INTERVAL:
                coin_timer = 0
                coins.append(Coin())

            obs_timer += dt * 1000
            if obs_timer >= OBSTACLE_SPAWN_INTERVAL:
                obs_timer = 0
                obstacles.append(Obstacle())

            for c in coins[:]:
                c.update(dt)
                if c.y > SCREEN_HEIGHT:
                    coins.remove(c)
                elif player.rect.colliderect(c.rect):
                    coins_collected += c.weight
                    score += c.weight * 10
                    boost += c.weight * 2
                    coins.remove(c)

                    if coins_collected >= next_threshold:
                        enemy_speed = min(MAX_ENEMY_SPEED, enemy_speed + ENEMY_ACCELERATION)
                        next_threshold += COINS_TO_ACCELERATE

            for o in obstacles[:]:
                o.update(dt)
                if o.y > SCREEN_HEIGHT:
                    obstacles.remove(o)
                elif player.rect.colliderect(o.rect):
                    game_over = True

            player_dist += (PLAYER_SPEED + boost) * dt
            enemy_dist += enemy_speed * dt
            boost *= 0.95

            if player_dist >= FINISH_DISTANCE or enemy_dist >= FINISH_DISTANCE:
                game_over = True

            draw_road(screen)

            for c in coins:
                c.draw(screen)

            for o in obstacles:
                o.draw(screen)

            player.draw(screen)

            draw_text(screen, f"Score: {score}", 30, 240, 40, GREEN)

            pygame.display.flip()

        # Game over screen
        while game_over:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_r:
                        game_over = False
                    if e.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            screen.fill(BLACK)
            draw_text(screen, "GAME OVER", 50, 240, 300, RED)
            draw_text(screen, "Press R to Restart", 30, 240, 360, WHITE)
            pygame.display.flip()


if __name__ == '__main__':
    run()
