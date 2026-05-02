# Основная логика гонки.
import os
import random
import pygame

# Размер окна и количество кадров в секунду.
WIDTH = 400
HEIGHT = 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (70, 70, 70)
DARK_GRAY = (40, 40, 40)
YELLOW = (255, 215, 0)
ORANGE = (255, 140, 0)
RED = (220, 50, 50)
BLUE = (70, 140, 255)
GREEN = (50, 220, 90)
PURPLE = (170, 80, 255)
CYAN = (70, 230, 255)

BASE_DIR = os.path.dirname(__file__)
ASSET_DIR = os.path.join(BASE_DIR, "assets")
OLD_IMAGE_DIR = os.path.join(BASE_DIR, "images")

# Границы дороги и координаты полос.
ROAD_LEFT = 80
ROAD_RIGHT = WIDTH - 80
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT
LANES = [100, 175, 250]
FINISH_DISTANCE = 3000

# Настройки сложности.
DIFFICULTY_DATA = {
    "easy": {"enemy_spawn": 105, "obstacle_spawn": 145, "speed": 4},
    "normal": {"enemy_spawn": 80, "obstacle_spawn": 115, "speed": 5},
    "hard": {"enemy_spawn": 55, "obstacle_spawn": 85, "speed": 6}
}

# Цвета машины игрока.
CAR_TINTS = {
    "blue": BLUE,
    "red": RED,
    "green": GREEN
}


# Загружает картинку из assets или images.
def load_image(name, size, fallback_color):
    # Сначала ищем в TSIS3/assets, потом в старой папке images.
    for folder in (ASSET_DIR, OLD_IMAGE_DIR):
        path = os.path.join(folder, name)
        if os.path.exists(path):
            image = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(image, size)

    # Если картинки нет, рисуем обычный прямоугольник.
    image = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(image, fallback_color, image.get_rect(), border_radius=8)
    pygame.draw.rect(image, WHITE, image.get_rect(), 2, border_radius=8)
    return image


# Добавляет цветовой оттенок к картинке.
def tint_image(image, color):
    result = image.copy()
    tint = pygame.Surface(result.get_size(), pygame.SRCALPHA)
    tint.fill((*color, 70))
    result.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return result


# Машина игрока.
class Player(pygame.sprite.Sprite):
    def __init__(self, settings):
        super().__init__()
        # Загружаем картинку игрока.
        base_image = load_image("car.png", (50, 90), BLUE)
        color = CAR_TINTS.get(settings.get("car_color", "blue"), BLUE)
        self.image = tint_image(base_image, color)
        # Ставим машину внизу дороги.
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 100))
        self.speed = 6
        self.shield = False
        self.repair = 0

    # Двигает игрока влево и вправо.
    # Обновляет всю игру каждый кадр.
    def update(self):
        keys = pygame.key.get_pressed()#читаем клавиши

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed#движение
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed#враги падают вниз

        # Не даем машине выехать за дорогу.
        if self.rect.left < ROAD_LEFT:
            self.rect.left = ROAD_LEFT
        if self.rect.right > ROAD_RIGHT:
            self.rect.right = ROAD_RIGHT


# Вражеская машина.
class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = load_image("enemy.png", (50, 90), RED)
        self.rect = self.image.get_rect(midtop=(random.choice(LANES), -120))
        self.speed = speed + random.randint(0, 2)

    # Обновляет всю игру каждый кадр.
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


# Монета для очков.
class Coin(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        # Чем больше weight, тем больше очков.
        self.weight = random.randint(1, 3)
        self.value = self.weight #дают очки
        self.image = load_image("coin.png", (32, 32), YELLOW)

        if self.weight == 2:
            self.image = tint_image(self.image, ORANGE)
        elif self.weight == 3:
            self.image = tint_image(self.image, RED)

        self.rect = self.image.get_rect(center=(random.choice(LANES), -40))
        self.speed = speed
        self.life = FPS * 6

    # Обновляет всю игру каждый кадр.
    def update(self):
        self.rect.y += self.speed
        self.life -= 1
        if self.rect.top > HEIGHT or self.life <= 0:
            self.kill()


# Препятствия на дороге.
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        # Случайно выбираем тип препятствия.
        self.kind = random.choice(["barrier", "oil", "pothole", "speed_bump"])
        self.speed = speed
        self.image = pygame.Surface((55, 35), pygame.SRCALPHA)

        if self.kind == "barrier":
            pygame.draw.rect(self.image, ORANGE, self.image.get_rect(), border_radius=5)
            pygame.draw.line(self.image, WHITE, (5, 5), (50, 30), 4)
        elif self.kind == "oil":
            pygame.draw.ellipse(self.image, BLACK, self.image.get_rect())
            pygame.draw.ellipse(self.image, DARK_GRAY, (8, 7, 35, 20))
        elif self.kind == "pothole":
            pygame.draw.ellipse(self.image, DARK_GRAY, self.image.get_rect())
            pygame.draw.ellipse(self.image, BLACK, (8, 6, 35, 22))
        else:
            pygame.draw.rect(self.image, YELLOW, self.image.get_rect(), border_radius=5)
            pygame.draw.line(self.image, BLACK, (0, 15), (55, 15), 3)

        self.rect = self.image.get_rect(center=(random.choice(LANES), -50))

    # Обновляет всю игру каждый кадр.
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


# Усиления: nitro, shield, repair.
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        # Выбираем случайный power-up.
        self.kind = random.choice(["nitro", "shield", "repair"])
        self.image = pygame.Surface((36, 36), pygame.SRCALPHA)

        if self.kind == "nitro":
            color = CYAN
            letter = "N"
        elif self.kind == "shield":
            color = PURPLE
            letter = "S"
        else:
            color = GREEN
            letter = "R"

        pygame.draw.circle(self.image, color, (18, 18), 18)
        pygame.draw.circle(self.image, WHITE, (18, 18), 18, 2)
        font = pygame.font.SysFont("Verdana", 20, bold=True)
        text = font.render(letter, True, WHITE)
        self.image.blit(text, text.get_rect(center=(18, 18)))

        self.rect = self.image.get_rect(center=(random.choice(LANES), -45))
        self.speed = speed
        self.life = FPS * 5

    # Обновляет всю игру каждый кадр.
    def update(self):
        self.rect.y += self.speed
        self.life -= 1
        if self.rect.top > HEIGHT or self.life <= 0:
            self.kill()


# Двигающееся препятствие.
class MovingBarrier(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.Surface((70, 30), pygame.SRCALPHA)
        pygame.draw.rect(self.image, RED, self.image.get_rect(), border_radius=6)
        pygame.draw.line(self.image, WHITE, (5, 6), (65, 24), 4)
        self.rect = self.image.get_rect(center=(WIDTH // 2, -70))
        self.speed = speed
        self.dx = random.choice([-2, 2])

    # Обновляет всю игру каждый кадр.
    def update(self):
        self.rect.y += self.speed
        self.rect.x += self.dx

        if self.rect.left < ROAD_LEFT or self.rect.right > ROAD_RIGHT:
            self.dx *= -1

        if self.rect.top > HEIGHT:
            self.kill()


# Главный класс игры.
class RacerGame:
    def __init__(self, screen, clock, username, settings):
        self.screen = screen
        self.clock = clock
        self.username = username
        self.settings = settings
        self.font = pygame.font.SysFont("Verdana", 18)
        self.big_font = pygame.font.SysFont("Verdana", 32, bold=True)
        self.road_img = self.load_road()
        self.reset()

    # Загружает фон дороги.
    def load_road(self):
        for folder in (ASSET_DIR, OLD_IMAGE_DIR):
            path = os.path.join(folder, "road.png")
            if os.path.exists(path):
                image = pygame.image.load(path).convert()
                return pygame.transform.scale(image, (WIDTH, HEIGHT))
        return None

    # Сбрасывает игру перед новым запуском.
    def reset(self):
        self.player = Player(self.settings)
        self.player_group = pygame.sprite.GroupSingle(self.player)
        self.enemies = pygame.sprite.Group()
        self.coins_group = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.events = pygame.sprite.Group()

        self.coins = 0
        self.score = 0
        self.distance = 0
        self.game_over = False
        self.finished = False
        self.saved = False

        self.enemy_timer = 0
        self.coin_timer = 0
        self.obstacle_timer = 0
        self.powerup_timer = 0
        self.event_timer = 0

        self.active_power = None
        self.power_time = 0
        self.nitro_bonus = 0

    # Возвращает настройки выбранной сложности.
    def difficulty(self):
        return DIFFICULTY_DATA.get(self.settings.get("difficulty", "normal"), DIFFICULTY_DATA["normal"])

    # Считает текущую скорость игры.
    def current_speed(self):
        level_bonus = int(self.distance // 700)
        return self.difficulty()["speed"] + level_bonus + self.nitro_bonus

    # Проверяет, можно ли создавать объект рядом с игроком.
    def safe_to_spawn(self, x):
        return abs(self.player.rect.centerx - x) > 45 or self.player.rect.y < HEIGHT - 180

    # Создает врага.
    def spawn_enemy(self):
        speed = self.current_speed()
        enemy = Enemy(speed)
        if self.safe_to_spawn(enemy.rect.centerx):
            self.enemies.add(enemy)

    # Создает препятствие.
    def spawn_obstacle(self):
        obstacle = Obstacle(self.current_speed())
        if self.safe_to_spawn(obstacle.rect.centerx):
            self.obstacles.add(obstacle)

    # Таймеры отвечают за появление объектов.
    def update_timers(self):
        speed = self.current_speed()
        difficulty = self.difficulty()
        progress_bonus = int(self.distance // 600) * 4

        self.enemy_timer += 1
        if self.enemy_timer >= max(25, difficulty["enemy_spawn"] - progress_bonus):
            self.enemy_timer = 0
            self.spawn_enemy()

        self.coin_timer += 1
        if self.coin_timer >= 70:
            self.coin_timer = 0
            self.coins_group.add(Coin(speed))

        self.obstacle_timer += 1
        if self.obstacle_timer >= max(35, difficulty["obstacle_spawn"] - progress_bonus):
            self.obstacle_timer = 0
            self.spawn_obstacle()

        self.powerup_timer += 1
        if self.powerup_timer >= 360:
            self.powerup_timer = 0
            if len(self.powerups) == 0 and self.active_power is None:
                self.powerups.add(PowerUp(speed))

        self.event_timer += 1
        if self.event_timer >= 500:
            self.event_timer = 0
            self.events.add(MovingBarrier(speed))

    # Проверяет сбор монет и power-ups.
    def collect_items(self):
        coins = pygame.sprite.spritecollide(self.player, self.coins_group, True)
        for coin in coins:
            self.coins += coin.value
            self.score += coin.value * 10

        powerups = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for powerup in powerups:
            # Новый power-up включается, если другого нет.
            if self.active_power is None:
                self.active_power = powerup.kind

                if powerup.kind == "nitro":
                    self.power_time = FPS * 4
                    self.nitro_bonus = 4
                    self.score += 30
                elif powerup.kind == "shield":
                    self.player.shield = True
                    self.power_time = 0
                    self.score += 20
                elif powerup.kind == "repair":
                    self.player.repair += 1
                    self.active_power = None
                    self.score += 15
                    if len(self.obstacles) > 0:
                        self.obstacles.sprites()[0].kill()

    # Отсчитывает время действия nitro.
    def handle_power_timer(self):
        if self.active_power == "nitro":
            self.power_time -= 1
            if self.power_time <= 0:
                self.active_power = None
                self.nitro_bonus = 0

    # Проверяет столкновения с объектами.
    def handle_collision_group(self, group):
        hit = pygame.sprite.spritecollideany(self.player, group)
        if not hit:
            return

        # Щит защищает от одного удара.
        if self.player.shield:
            hit.kill()
            self.player.shield = False
            self.active_power = None
            return

        # Repair убирает одно столкновение.
        if self.player.repair > 0:
            hit.kill()
            self.player.repair -= 1
            return

        self.game_over = True

    # Обновляет всю игру каждый кадр.
    def update(self):
        if self.game_over or self.finished:
            return

        self.player_group.update()
        self.enemies.update()
        self.coins_group.update()
        self.obstacles.update()
        self.powerups.update()
        self.events.update()
        self.update_timers()
        self.collect_items()
        self.handle_power_timer()

        # Проверяем столкновения с машинами и препятствиями.
        self.handle_collision_group(self.enemies)
        self.handle_collision_group(self.obstacles)
        self.handle_collision_group(self.events)

        self.distance += self.current_speed() / 5
        self.score += 1

        # Если дошли до финиша, игра закончена победой.
        if self.distance >= FINISH_DISTANCE:
            self.finished = True
            self.score += 500

    # Рисует дорогу.
    def draw_road(self):
        if self.road_img:
            self.screen.blit(self.road_img, (0, 0))
        else:
            self.screen.fill((45, 45, 45))
            pygame.draw.rect(self.screen, (35, 35, 35), (ROAD_LEFT, 0, ROAD_WIDTH, HEIGHT))
            pygame.draw.line(self.screen, WHITE, (ROAD_LEFT, 0), (ROAD_LEFT, HEIGHT), 3)
            pygame.draw.line(self.screen, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, HEIGHT), 3)
            for y in range(0, HEIGHT, 80):
                pygame.draw.line(self.screen, WHITE, (WIDTH // 2, y), (WIDTH // 2, y + 40), 3)

    # Рисует score, coins, distance и power-up.
    def draw_hud(self):
        remaining = max(0, int(FINISH_DISTANCE - self.distance))
        texts = [
            f"Score: {self.score}",
            f"Coins: {self.coins}",
            f"Distance: {int(self.distance)}m",
            f"Finish: {remaining}m"
        ]

        y = 10
        for text in texts:
            surface = self.font.render(text, True, WHITE)
            self.screen.blit(surface, (10, y))
            y += 24

        power_text = "Power: none"
        if self.active_power == "nitro":
            power_text = f"Power: nitro {self.power_time // FPS + 1}s"
        elif self.player.shield:
            power_text = "Power: shield"
        elif self.player.repair > 0:
            power_text = f"Repair: {self.player.repair}"

        surface = self.font.render(power_text, True, YELLOW)
        self.screen.blit(surface, (10, y))

    # Рисует все объекты на экране.
    def draw(self):
        self.draw_road()
        self.coins_group.draw(self.screen)
        self.powerups.draw(self.screen)
        self.obstacles.draw(self.screen)
        self.events.draw(self.screen)
        self.enemies.draw(self.screen)
        self.player_group.draw(self.screen)
        self.draw_hud()

        # Щит защищает от одного удара.
        if self.player.shield:
            pygame.draw.circle(self.screen, CYAN, self.player.rect.center, 55, 3)

        pygame.display.flip()

    # Основной игровой цикл.
    def run(self):
        while True:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return "menu"

            self.update()
            self.draw()

            if self.game_over:
                return "game_over"
            if self.finished:
                return "finished"