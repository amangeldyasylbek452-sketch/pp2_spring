import random

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, POWERUP_COLORS
from collectables import Coin, PowerUp
from platforms import MovingPlatform, Platform


class LevelGenerator:
    def __init__(self):
        self.platforms = []
        self.coins = []
        self.powerups = []
        self._generate_initial_layout()

    def _generate_initial_layout(self):
        floor = Platform(
            SCREEN_WIDTH * 0.12,
            SCREEN_HEIGHT - 50,
            SCREEN_WIDTH * 0.76,
            bouncy=False,
            disappearing=False,
        )
        self.platforms.append(floor)

        current_y = SCREEN_HEIGHT - 170
        for index in range(28):
            width = random.randint(140, 260)
            x = random.randint(40, SCREEN_WIDTH - width - 40)
            current_y -= random.randint(120, 165)
            bouncy = (index % 7 == 0)
            disappearing = (index % 6 == 0)

            if index % 5 == 0:
                platform = MovingPlatform(
                    x, current_y, width, range_px=120, speed=1.1,
                    bouncy=bouncy, disappearing=disappearing,
                )
            else:
                platform = Platform(x, current_y, width,
                                    bouncy=bouncy, disappearing=disappearing)

            self.platforms.append(platform)
            self._spawn_coin(platform)
            self._spawn_powerup(platform)

        self.highest_platform_y = min(p.y for p in self.platforms)

    def update(self, player_y):
        """Generate more platforms above the player as they climb."""
        while player_y < self.highest_platform_y + SCREEN_HEIGHT * 0.75:
            self._spawn_extra_platforms()

    def _spawn_extra_platforms(self):
        self.highest_platform_y -= random.randint(120, 165)
        layers = random.randint(2, 4)
        for i in range(layers):
            width = random.randint(140, 260)
            x = random.randint(40, SCREEN_WIDTH - width - 40)
            self.highest_platform_y -= random.randint(105, 145)
            bouncy = random.random() < 0.12
            disappearing = random.random() < 0.13
            if random.random() < 0.22:
                platform = MovingPlatform(
                    x, self.highest_platform_y, width, range_px=110, speed=1.0,
                    bouncy=bouncy, disappearing=disappearing,
                )
            else:
                platform = Platform(
                    x, self.highest_platform_y, width,
                    bouncy=bouncy, disappearing=disappearing,
                )
            self.platforms.append(platform)
            self._spawn_coin(platform)
            self._spawn_powerup(platform)

    def _spawn_coin(self, platform):
        if random.random() < 0.64:
            coin_x = platform.x + platform.width * 0.5
            coin_y = platform.y - 30
            self.coins.append(Coin(coin_x, coin_y))

    def _spawn_powerup(self, platform):
        if random.random() < 0.14:
            kinds = list(POWERUP_COLORS.keys())
            if random.random() < 0.15:
                kind = "extra_life"
            else:
                kinds.remove("extra_life")
                kind = random.choice(kinds)
            powerup_x = min(SCREEN_WIDTH - 40, max(40, platform.x + platform.width * 0.5))
            powerup_y = platform.y - 42
            self.powerups.append(PowerUp(powerup_x, powerup_y, kind))
