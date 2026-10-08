"""
level.py - Level generation, camera, parallax backgrounds and per-frame
collision resolution between the player and the obstacle field.
Levels are procedurally assembled (seeded, so repeatable) from each world's
theme parameters defined in config.WORLDS, giving every world a unique
layout, obstacle mix and background while sharing the same engine.
"""
import random
import math
import pygame
import config
from obstacles import (Spike, MovingSpike, SpikeWheel, Block, JumpPad, BouncePad,
                        JumpRing, SpeedPad, Lava, Fire, SawBlade, LaserBeam,
                        FallingRock, Crusher, Coin)
from particles import WeatherSystem


class Camera:
    def __init__(self, screen_w, offset_ratio=0.30):
        self.x = 0.0
        self.screen_w = screen_w
        self.offset_ratio = offset_ratio
        self.shake_time = 0.0
        self.shake_mag = 0.0

    def follow(self, player_x):
        self.x = player_x - self.screen_w * self.offset_ratio

    def shake(self, magnitude, duration):
        self.shake_mag = max(self.shake_mag, magnitude)
        self.shake_time = max(self.shake_time, duration)

    def update(self, dt):
        if self.shake_time > 0:
            self.shake_time -= dt
        else:
            self.shake_mag = 0

    def get_shake_offset(self):
        if self.shake_time <= 0:
            return 0, 0
        return (random.uniform(-1, 1) * self.shake_mag,
                random.uniform(-1, 1) * self.shake_mag)


class Level:
    """Represents one playable level built from a world definition."""

    def __init__(self, world, screen_w, screen_h):
        self.world = world
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.ground_y = int(screen_h * config.GROUND_Y_RATIO)
        self.length = world["length"] * (1.0 + (world["difficulty"] - 1) * 0.15)
        self.difficulty = world["difficulty"]
        self.scroll_speed = (config.BASE_SCROLL_SPEED +
                              config.SPEED_PER_DIFFICULTY * world["difficulty"])
        self.rng = random.Random(world["seed"])
        self.obstacles = []
        self.coins = []
        self.decor_seed_objects = []
        self._generate()
        self.weather = self._make_weather()
        self.finished = False
        self.finish_x = self.length

    # -- Generation ----------------------------------------------------
    def _make_weather(self):
        decor = self.world["decor"]
        mapping = {
            "green_hills": ("float", 20),
            "crystal_cave": ("float", 30),
            "volcano": ("ash", 50),
            "ice_kingdom": ("snow", 60),
            "ancient_temple": ("float", 15),
            "cyber_city": ("float", 25),
            "space_station": ("stars", 90),
        }
        kind, density = mapping.get(self.world["id"], ("float", 20))
        return WeatherSystem(kind, self.screen_w, self.screen_h, density)

    def _generate(self):
        rng = self.rng
        x = 500
        min_gap = 260 - self.difficulty * 12  # tighter reaction windows at higher difficulty
        min_gap = max(150, min_gap)
        patterns = self._pattern_pool()
        safe_zone_end = 420
        while x < self.length - 500:
            gap = min_gap + rng.uniform(0, 140)
            pattern_fn = rng.choice(patterns)
            consumed = pattern_fn(x)
            x += max(consumed, min_gap) + gap
        # scatter coins - three clusters, occasionally requiring a jump to reach
        for i in range(3):
            cx = 700 + i * (self.length - 1400) / 2 + rng.uniform(-100, 100)
            cy = self.ground_y - rng.choice([70, 110, 160])
            for j in range(5):
                self.coins.append(Coin(cx + j * 26, cy))

    def _add(self, obs):
        self.obstacles.append(obs)

    def _pattern_pool(self):
        gy = self.ground_y
        d = self.difficulty

        def p_single_small_spike(x):
            self._add(Spike(x, gy, "small"))
            return 40

        def p_triple_spike(x):
            self._add(Spike(x, gy, "small", count=3))
            return 34 * 3

        def p_large_spike(x):
            self._add(Spike(x, gy, "large"))
            return 50

        def p_ceiling_spike(x):
            self._add(Spike(x, gy - 230, "small", count=2, ceiling=True))
            self._add(Block(x - 10, gy - 40, 90, 40, color=self.world["ground_dark"]))
            return 100

        def p_moving_spike(x):
            axis = self.rng.choice(["x", "y"])
            self._add(MovingSpike(x, gy, "small", axis=axis, amplitude=50, speed=1.6))
            return 40

        def p_spike_wheel(x):
            self._add(SpikeWheel(x, gy - 60, radius=42, spikes=8, spin_speed=120 + d * 20))
            return 90

        def p_floating_block(x):
            h = self.rng.choice([90, 140, 180])
            self._add(Block(x, gy - h, 80, 26, color=self.world["ground"], floating=True))
            return 90

        def p_block_gauntlet(x):
            n = self.rng.randint(2, 3)
            for i in range(n):
                self._add(Block(x + i * 70, gy - self.rng.choice([90, 130]), 55, 22,
                                 color=self.world["ground"], floating=True))
            return n * 70

        def p_jump_pad(x):
            self._add(JumpPad(x, gy, strength=980))
            self._add(Block(x + 90, gy - 150, 60, 22, color=self.world["ground"], floating=True))
            return 160

        def p_bounce_pad(x):
            self._add(BouncePad(x, gy))
            return 60

        def p_jump_ring(x):
            self._add(JumpRing(x, gy - 130))
            self._add(Spike(x + 60, gy, "small", count=2))
            return 140

        def p_speed_pad(x):
            mult = self.rng.choice([1.35, 0.75])
            self._add(SpeedPad(x, gy, multiplier=mult))
            return 60

        def p_lava_pit(x):
            w = self.rng.choice([70, 100, 130])
            self._add(Lava(x, gy, w))
            self._add(JumpPad(x - 70, gy))
            return w

        def p_fire(x):
            self._add(Fire(x, gy))
            return 40

        def p_saw_static(x):
            self._add(SawBlade(x, gy - 40))
            return 60

        def p_saw_moving(x):
            path = self.rng.choice(["vertical", "horizontal"])
            self._add(SawBlade(x, gy - 80, path=path, amplitude=60, speed=1.3))
            return 90

        def p_laser(x):
            self._add(LaserBeam(x, gy, 230, cycle=2.2, on_time=0.5, warn_time=0.5))
            return 40

        def p_falling_rock(x):
            self._add(FallingRock(x, gy - 220, gy))
            return 40

        def p_crusher(x):
            self._add(Crusher(x, gy - 260, gy))
            return 70

        pool = [p_single_small_spike, p_triple_spike, p_large_spike, p_moving_spike,
                p_floating_block, p_bounce_pad, p_speed_pad]
        if d >= 2:
            pool += [p_ceiling_spike, p_spike_wheel, p_block_gauntlet, p_jump_pad,
                     p_jump_ring, p_saw_static]
        if d >= 3:
            pool += [p_lava_pit, p_fire, p_saw_moving, p_falling_rock]
        if d >= 4:
            pool += [p_laser, p_crusher]
        if d >= 5:
            pool += [p_laser, p_crusher, p_spike_wheel, p_saw_moving]
        return pool

    # -- Update / collision ---------------------------------------------
    def update(self, dt, player, particles, audio, double_jump_enabled=True):
        if not player.alive:
            for obs in self.obstacles:
                if abs(obs.x - player.x) < 900:
                    obs.update(dt)
            return "playing"

        prev_bottom = player.y + player.size
        prev_x = player.x

        effective_speed = self.scroll_speed * player.speed_multiplier
        player.x += effective_speed * dt

        player.ground_y = self.ground_y
        player.update(dt, particles, double_jump_enabled=double_jump_enabled)

        result = "playing"
        prect = player.rect

        for obs in self.obstacles:
            if not obs.on_screen(player.x - self.screen_w * 0.4, self.screen_w * 1.8):
                continue
            obs.update(dt)

            if isinstance(obs, FallingRock):
                if 0 < obs.x - player.x < 160:
                    obs.trigger()

            if obs.is_solid:
                if obs.rect.colliderect(prect):
                    landed = (player.vy >= 0 and prev_bottom <= obs.rect.top + 12)
                    if landed:
                        player.y = obs.rect.top - player.size
                        player.vy = 0
                        player.on_ground = True
                        player.used_double_jump = True
                        player.coyote_timer = config.COYOTE_TIME
                    else:
                        player.kill(particles, audio)
                        result = "dead"
                continue

            if isinstance(obs, JumpPad):
                if obs.check_collision(prect) and player.vy >= 0:
                    player.vy = -obs.strength
                    player.on_ground = False
                    player.used_double_jump = False
                    particles.jump_burst(obs.x + obs.w / 2, obs.y, (120, 255, 170))
                    audio.play("jump")
                continue
            if isinstance(obs, BouncePad):
                if obs.check_collision(prect) and player.vy >= 0:
                    player.vy = -obs.strength
                    player.used_double_jump = False
                    obs.squish = 1.0
                    particles.jump_burst(obs.x + obs.w / 2, obs.y, (255, 160, 90))
                    audio.play("jump")
                continue
            if isinstance(obs, JumpRing):
                if not obs.used and obs.check_collision(prect):
                    player.vy = -obs.strength
                    player.used_double_jump = False
                    obs.used = True
                    particles.jump_burst(obs.x + obs.w / 2, obs.y + obs.h / 2, (150, 220, 255))
                    audio.play("double_jump")
                elif obs.used and not obs.check_collision(prect):
                    obs.used = False
                continue
            if isinstance(obs, SpeedPad):
                if obs.check_collision(prect):
                    player.speed_multiplier = obs.multiplier
                continue
            if isinstance(obs, Coin):
                if obs.check_collision(prect):
                    obs.collected = True
                    particles.coin_burst(obs.x, obs.y)
                    audio.play("coin")
                    result = "coin"
                continue

            if obs.is_hazard and obs.check_collision(prect):
                player.kill(particles, audio)
                result = "dead"

        if player.alive and player.x >= self.finish_x:
            self.finished = True
            result = "finished"

        return result

    def percent_complete(self, player_x):
        return max(0.0, min(100.0, (player_x / self.finish_x) * 100.0))

    # -- Drawing ---------------------------------------------------------
    def draw_background(self, surf, cam_x, t):
        w, h = self.screen_w, self.screen_h
        top = self.world["sky_top"]
        bottom = self.world["sky_bottom"]
        steps = 40
        for i in range(steps):
            ratio = i / steps
            color = tuple(int(top[c] + (bottom[c] - top[c]) * ratio) for c in range(3))
            pygame.draw.rect(surf, color, (0, int(h * ratio), w, int(h / steps) + 1))

        decor = self.world["decor"]
        parallax_layers = {
            "hills": self._draw_hills, "crystals": self._draw_crystals,
            "volcano": self._draw_volcano, "ice": self._draw_ice,
            "temple": self._draw_temple, "cyber": self._draw_cyber,
            "space": self._draw_space,
        }
        fn = parallax_layers.get(decor)
        if fn:
            fn(surf, cam_x, t)

        self.weather.draw(surf, self.world["accent"])

    def _seeded_positions(self, count, seed_add, spread=None):
        rng = random.Random(self.world["seed"] + seed_add)
        spread = spread or self.length
        return [rng.uniform(0, spread) for _ in range(count)]

    def _draw_hills(self, surf, cam_x, t):
        w, h = self.screen_w, self.screen_h
        factor = 0.25
        for i, bx in enumerate(self._seeded_positions(10, 1)):
            x = (bx - cam_x * factor) % (w + 300) - 150
            pygame.draw.circle(surf, (255, 255, 255), (int(x), int(60 + (i % 3) * 22)), 26)
            pygame.draw.circle(surf, (255, 255, 255), (int(x) + 24, int(70 + (i % 3) * 22)), 20)
        factor2 = 0.5
        for i, bx in enumerate(self._seeded_positions(8, 2)):
            x = (bx - cam_x * factor2) % (w + 400) - 200
            pygame.draw.polygon(surf, (110, 170, 120),
                                 [(x, self.ground_y), (x + 120, self.ground_y - 90), (x + 240, self.ground_y)])

    def _draw_crystals(self, surf, cam_x, t):
        w, h = self.screen_w, self.screen_h
        factor = 0.4
        for i, bx in enumerate(self._seeded_positions(14, 3)):
            x = (bx - cam_x * factor) % (w + 300) - 150
            glow = int(60 + 40 * math.sin(t * 2 + i))
            col = (60, 120 + glow // 3, 200)
            pygame.draw.polygon(surf, col,
                                 [(x, self.ground_y), (x + 18, self.ground_y - 70 - (i % 4) * 12),
                                  (x + 36, self.ground_y)])

    def _draw_volcano(self, surf, cam_x, t):
        w, h = self.screen_w, self.screen_h
        factor = 0.3
        for i, bx in enumerate(self._seeded_positions(4, 4)):
            x = (bx - cam_x * factor) % (w + 500) - 250
            pygame.draw.polygon(surf, (60, 35, 30),
                                 [(x, self.ground_y), (x + 150, self.ground_y - 160), (x + 300, self.ground_y)])
            glow = int(150 + 80 * math.sin(t * 3 + i))
            pygame.draw.circle(surf, (255, min(255, glow), 40), (int(x + 150), int(self.ground_y - 155)), 10)

    def _draw_ice(self, surf, cam_x, t):
        w, h = self.screen_w, self.screen_h
        factor = 0.35
        for i, bx in enumerate(self._seeded_positions(10, 5)):
            x = (bx - cam_x * factor) % (w + 300) - 150
            pygame.draw.polygon(surf, (225, 240, 250),
                                 [(x, self.ground_y), (x + 20, self.ground_y - 60), (x + 40, self.ground_y)])
        # aurora
        for band in range(3):
            pts = []
            for i in range(0, w + 40, 40):
                y = 60 + band * 26 + 14 * math.sin(t * 0.6 + i * 0.02 + band)
                pts.append((i, y))
            if len(pts) > 1:
                pygame.draw.lines(surf, (150 + band * 20, 255 - band * 20, 220), False, pts, 3)

    def _draw_temple(self, surf, cam_x, t):
        w, h = self.screen_w, self.screen_h
        factor = 0.3
        for i, bx in enumerate(self._seeded_positions(6, 6)):
            x = (bx - cam_x * factor) % (w + 350) - 175
            pygame.draw.rect(surf, (110, 90, 60), (x, self.ground_y - 140, 26, 140))
            flick = int(180 + 60 * math.sin(t * 8 + i))
            pygame.draw.circle(surf, (255, min(255, flick), 60), (int(x + 13), int(self.ground_y - 150)), 6)

    def _draw_cyber(self, surf, cam_x, t):
        w, h = self.screen_w, self.screen_h
        factor = 0.25
        for i, bx in enumerate(self._seeded_positions(8, 7)):
            x = (bx - cam_x * factor) % (w + 300) - 150
            hgt = 80 + (i % 4) * 40
            pygame.draw.rect(surf, (30, 26, 50), (x, self.ground_y - hgt, 50, hgt))
            for wy in range(int(self.ground_y - hgt + 10), int(self.ground_y - 6), 16):
                if (wy + i) % 32 < 16:
                    pygame.draw.rect(surf, self.world["accent"], (x + 8, wy, 8, 8))

    def _draw_space(self, surf, cam_x, t):
        w, h = self.screen_w, self.screen_h
        factor = 0.15
        for i, bx in enumerate(self._seeded_positions(3, 8)):
            x = (bx - cam_x * factor) % (w + 500) - 250
            pygame.draw.circle(surf, (120, 100, 160), (int(x), 100 + i * 40), 40 - i * 6)

    def draw_ground(self, surf, cam_x):
        w, h = self.screen_w, self.screen_h
        r = pygame.Rect(0, self.ground_y, w, h - self.ground_y)
        pygame.draw.rect(surf, self.world["ground"], r)
        pygame.draw.rect(surf, self.world["ground_dark"], (0, self.ground_y, w, 6))
        offset = int(-cam_x) % 40
        for x in range(offset - 40, w + 40, 40):
            pygame.draw.line(surf, self.world["ground_dark"], (x, self.ground_y + 6),
                              (x, h), 1)

    def draw_obstacles(self, surf, cam_x):
        for obs in self.obstacles:
            if obs.on_screen(cam_x, self.screen_w):
                obs.draw(surf, cam_x)
        for coin in self.coins:
            if coin.on_screen(cam_x, self.screen_w):
                coin.draw(surf, cam_x)

    def draw_finish(self, surf, cam_x):
        x = self.finish_x - cam_x
        if -50 < x < self.screen_w + 50:
            pygame.draw.rect(surf, (255, 255, 255), (x, 0, 6, self.ground_y))
            for i in range(0, self.ground_y, 24):
                col = (20, 20, 20) if (i // 24) % 2 == 0 else (255, 255, 255)
                pygame.draw.rect(surf, col, (x - 10, i, 26, 24))