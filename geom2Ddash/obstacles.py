"""
obstacles.py - All obstacle / hazard types. Every obstacle exposes:
    rect            -> pygame.Rect in world space for broad-phase collision
    is_hazard        -> bool, True if touching it kills the player
    check_collision(player_rect) -> bool precise hit test
    update(dt)       -> for animated / moving obstacles
    draw(surf, cam_x)
Drawing uses only primitives (polygons, circles, lines, gradients).
"""
import math
import pygame


class Obstacle:
    kind = "base"
    is_hazard = False
    is_solid = False

    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), int(self.w), int(self.h))

    def update(self, dt):
        pass

    def check_collision(self, prect):
        return self.rect.colliderect(prect)

    def on_screen(self, cam_x, screen_w):
        return self.x + self.w > cam_x - 40 and self.x < cam_x + screen_w + 40

    def draw(self, surf, cam_x):
        pass


# ---------------------------------------------------------------------------
# Spikes
# ---------------------------------------------------------------------------
class Spike(Obstacle):
    """Triangular spike sitting on the ground. Size controls scale."""
    kind = "spike"
    is_hazard = True

    def __init__(self, x, ground_y, size="small", count=1, ceiling=False):
        sizes = {"small": (34, 34), "large": (48, 52)}
        w, h = sizes.get(size, (34, 34))
        self.count = count
        self.ceiling = ceiling
        total_w = w * count
        if ceiling:
            super().__init__(x, ground_y, total_w, h)
        else:
            super().__init__(x, ground_y - h, total_w, h)
        self.unit_w = w
        self.unit_h = h
        self.color = (230, 230, 240)
        self.dark = (150, 155, 170)

    def check_collision(self, prect):
        # Narrower hitbox than the bounding box for fairness (triangle shape)
        cx = self.rect.centerx
        inset = self.rect.inflate(-int(self.w * 0.25), -int(self.h * 0.18))
        return inset.colliderect(prect)

    def draw(self, surf, cam_x):
        base_y = self.y + self.h if not self.ceiling else self.y
        for i in range(self.count):
            x0 = self.x + i * self.unit_w - cam_x
            if self.ceiling:
                pts = [(x0, self.y), (x0 + self.unit_w, self.y),
                       (x0 + self.unit_w / 2, self.y + self.h)]
            else:
                pts = [(x0, self.y + self.h), (x0 + self.unit_w, self.y + self.h),
                       (x0 + self.unit_w / 2, self.y)]
            pygame.draw.polygon(surf, self.color, pts)
            pygame.draw.polygon(surf, self.dark, pts, 2)


class MovingSpike(Spike):
    """Spike that slides back and forth or up/down."""
    kind = "moving_spike"

    def __init__(self, x, ground_y, size="small", axis="x", amplitude=60, speed=1.6):
        super().__init__(x, ground_y, size, 1, ceiling=False)
        self.origin_x = self.x
        self.origin_y = self.y
        self.axis = axis
        self.amplitude = amplitude
        self.speed = speed
        self.t = 0.0

    def update(self, dt):
        self.t += dt
        offset = math.sin(self.t * self.speed) * self.amplitude
        if self.axis == "x":
            self.x = self.origin_x + offset
        else:
            self.y = self.origin_y + offset


class SpikeWheel(Obstacle):
    """Rotating wheel of spikes, hazardous around its rim."""
    kind = "spike_wheel"
    is_hazard = True

    def __init__(self, x, y, radius=44, spikes=8, spin_speed=140):
        super().__init__(x - radius, y - radius, radius * 2, radius * 2)
        self.cx = x
        self.cy = y
        self.radius = radius
        self.spikes = spikes
        self.angle = 0
        self.spin_speed = spin_speed

    def update(self, dt):
        self.angle += self.spin_speed * dt

    def check_collision(self, prect):
        # Approximate as circle-rect collision against the rim.
        closest_x = max(prect.left, min(self.cx, prect.right))
        closest_y = max(prect.top, min(self.cy, prect.bottom))
        dx, dy = self.cx - closest_x, self.cy - closest_y
        return (dx * dx + dy * dy) <= (self.radius * 0.85) ** 2

    def draw(self, surf, cam_x):
        cx, cy = self.cx - cam_x, self.cy
        pygame.draw.circle(surf, (70, 70, 85), (int(cx), int(cy)), self.radius - 8)
        pygame.draw.circle(surf, (120, 120, 140), (int(cx), int(cy)), self.radius - 8, 3)
        for i in range(self.spikes):
            a = math.radians(self.angle + i * (360 / self.spikes))
            x1 = cx + math.cos(a) * (self.radius - 10)
            y1 = cy + math.sin(a) * (self.radius - 10)
            x2 = cx + math.cos(a) * self.radius
            y2 = cy + math.sin(a) * self.radius
            perp = a + math.pi / 2
            wx = math.cos(perp) * 6
            wy = math.sin(perp) * 6
            pygame.draw.polygon(surf, (220, 225, 235),
                                 [(x1 - wx, y1 - wy), (x1 + wx, y1 + wy), (x2, y2)])


# ---------------------------------------------------------------------------
# Blocks
# ---------------------------------------------------------------------------
class Block(Obstacle):
    kind = "block"
    is_solid = True

    def __init__(self, x, y, w, h, color=(90, 100, 130), floating=False):
        super().__init__(x, y, w, h)
        self.color = color
        self.floating = floating

    def draw(self, surf, cam_x):
        r = pygame.Rect(int(self.x - cam_x), int(self.y), int(self.w), int(self.h))
        pygame.draw.rect(surf, self.color, r, border_radius=4)
        top = pygame.Rect(r.x, r.y, r.w, max(4, r.h // 6))
        lighter = tuple(min(255, c + 35) for c in self.color)
        pygame.draw.rect(surf, lighter, top, border_radius=4)
        pygame.draw.rect(surf, tuple(max(0, c - 40) for c in self.color), r, 2, border_radius=4)


# ---------------------------------------------------------------------------
# Pads
# ---------------------------------------------------------------------------
class JumpPad(Obstacle):
    """Instantly launches the player upward with a fixed strong velocity."""
    kind = "jump_pad"

    def __init__(self, x, ground_y, strength=980):
        super().__init__(x, ground_y - 14, 40, 14)
        self.strength = strength
        self.pulse = 0.0

    def update(self, dt):
        self.pulse = (self.pulse + dt * 4) % (2 * math.pi)

    def draw(self, surf, cam_x):
        x = self.x - cam_x
        glow = int(6 + 4 * math.sin(self.pulse))
        pygame.draw.polygon(surf, (120, 255, 170),
                             [(x, self.y + self.h), (x + self.w, self.y + self.h),
                              (x + self.w / 2, self.y - glow)])
        pygame.draw.polygon(surf, (30, 150, 90),
                             [(x, self.y + self.h), (x + self.w, self.y + self.h),
                              (x + self.w / 2, self.y - glow)], 2)


class BouncePad(JumpPad):
    """A softer pad that gives a medium bounce, drawn as a rounded pad."""
    kind = "bounce_pad"

    def __init__(self, x, ground_y, strength=650):
        Obstacle.__init__(self, x, ground_y - 10, 44, 10)
        self.strength = strength
        self.squish = 0.0

    def update(self, dt):
        self.squish = max(0.0, self.squish - dt * 4)

    def draw(self, surf, cam_x):
        x = self.x - cam_x
        h = self.h * (1 - self.squish * 0.4)
        r = pygame.Rect(int(x), int(self.y + (self.h - h)), int(self.w), int(h))
        pygame.draw.ellipse(surf, (255, 160, 90), r)
        pygame.draw.ellipse(surf, (180, 90, 40), r, 2)


class JumpRing(Obstacle):
    """Floating ring that grants a mid-air jump/dash when touched."""
    kind = "jump_ring"

    def __init__(self, x, y, strength=760):
        super().__init__(x, y, 40, 40)
        self.strength = strength
        self.t = 0.0
        self.used = False

    def update(self, dt):
        self.t += dt

    def check_collision(self, prect):
        cx, cy = self.x + self.w / 2, self.y + self.h / 2
        closest_x = max(prect.left, min(cx, prect.right))
        closest_y = max(prect.top, min(cy, prect.bottom))
        dx, dy = cx - closest_x, cy - closest_y
        return (dx * dx + dy * dy) <= (self.w / 2) ** 2

    def draw(self, surf, cam_x):
        cx, cy = self.x + self.w / 2 - cam_x, self.y + self.h / 2
        pulse = 3 * math.sin(self.t * 5)
        color = (150, 220, 255) if not self.used else (90, 100, 110)
        pygame.draw.circle(surf, color, (int(cx), int(cy)), int(self.w / 2 + pulse), 4)
        pygame.draw.circle(surf, (255, 255, 255), (int(cx), int(cy)), int(self.w / 2 - 6), 1)


class SpeedPad(Obstacle):
    """Temporarily changes the player's scroll speed multiplier."""
    kind = "speed_pad"

    def __init__(self, x, ground_y, multiplier=1.4):
        super().__init__(x, ground_y - 8, 50, 8)
        self.multiplier = multiplier

    def draw(self, surf, cam_x):
        x = self.x - cam_x
        col = (255, 220, 60) if self.multiplier > 1 else (140, 160, 255)
        for i in range(3):
            xi = x + i * 16
            pygame.draw.polygon(surf, col, [(xi, self.y), (xi + 10, self.y + self.h / 2),
                                             (xi, self.y + self.h)])


# ---------------------------------------------------------------------------
# Hazards
# ---------------------------------------------------------------------------
class Lava(Obstacle):
    kind = "lava"
    is_hazard = True

    def __init__(self, x, ground_y, w, h=26):
        super().__init__(x, ground_y - h + 8, w, h)
        self.t = 0.0

    def update(self, dt):
        self.t += dt * 3

    def draw(self, surf, cam_x):
        x = self.x - cam_x
        r = pygame.Rect(int(x), int(self.y), int(self.w), int(self.h))
        pygame.draw.rect(surf, (140, 30, 10), r)
        wave_h = 6
        pts = [(x, self.y + wave_h)]
        steps = max(2, int(self.w / 10))
        for i in range(steps + 1):
            wx = x + i * (self.w / steps)
            wy = self.y + wave_h + math.sin(self.t + i * 0.9) * 4
            pts.append((wx, wy))
        pts.append((x + self.w, self.y))
        pts.append((x, self.y))
        pygame.draw.polygon(surf, (255, 120, 30), pts)


class Fire(Obstacle):
    kind = "fire"
    is_hazard = True

    def __init__(self, x, ground_y, h=40):
        super().__init__(x, ground_y - h, 22, h)
        self.t = 0.0

    def update(self, dt):
        self.t += dt * 6

    def check_collision(self, prect):
        inset = self.rect.inflate(-8, -6)
        return inset.colliderect(prect)

    def draw(self, surf, cam_x):
        x = self.x - cam_x + self.w / 2
        wob = math.sin(self.t) * 4
        pts = [(x - 10, self.y + self.h), (x + 10, self.y + self.h),
               (x + wob, self.y)]
        pygame.draw.polygon(surf, (255, 140, 30), pts)
        pts2 = [(x - 5, self.y + self.h), (x + 5, self.y + self.h),
                (x + wob * 0.6, self.y + self.h * 0.35)]
        pygame.draw.polygon(surf, (255, 220, 90), pts2)


class SawBlade(Obstacle):
    kind = "saw"
    is_hazard = True

    def __init__(self, x, y, radius=26, path="static", amplitude=80, speed=1.4):
        super().__init__(x - radius, y - radius, radius * 2, radius * 2)
        self.cx, self.cy = x, y
        self.origin_x, self.origin_y = x, y
        self.radius = radius
        self.angle = 0
        self.path = path
        self.amplitude = amplitude
        self.speed = speed
        self.t = 0.0

    def update(self, dt):
        self.angle += 420 * dt
        self.t += dt
        if self.path == "vertical":
            self.cy = self.origin_y + math.sin(self.t * self.speed) * self.amplitude
        elif self.path == "horizontal":
            self.cx = self.origin_x + math.sin(self.t * self.speed) * self.amplitude
        self.x, self.y = self.cx - self.radius, self.cy - self.radius

    def check_collision(self, prect):
        closest_x = max(prect.left, min(self.cx, prect.right))
        closest_y = max(prect.top, min(self.cy, prect.bottom))
        dx, dy = self.cx - closest_x, self.cy - closest_y
        return (dx * dx + dy * dy) <= (self.radius * 0.8) ** 2

    def draw(self, surf, cam_x):
        cx, cy = self.cx - cam_x, self.cy
        pygame.draw.circle(surf, (170, 175, 185), (int(cx), int(cy)), self.radius)
        teeth = 10
        for i in range(teeth):
            a = math.radians(self.angle + i * (360 / teeth))
            x1 = cx + math.cos(a) * self.radius
            y1 = cy + math.sin(a) * self.radius
            x2 = cx + math.cos(a) * (self.radius + 9)
            y2 = cy + math.sin(a) * (self.radius + 9)
            pygame.draw.line(surf, (210, 215, 225), (x1, y1), (x2, y2), 4)
        pygame.draw.circle(surf, (90, 92, 100), (int(cx), int(cy)), int(self.radius * 0.35))


class LaserBeam(Obstacle):
    """Telegraphs, then fires for a short window, on a repeating cycle."""
    kind = "laser"

    def __init__(self, x, ground_y, height, cycle=2.2, on_time=0.55, warn_time=0.5):
        super().__init__(x, ground_y - height, 10, height)
        self.cycle = cycle
        self.on_time = on_time
        self.warn_time = warn_time
        self.t = 0.0

    @property
    def is_hazard(self):
        phase = self.t % self.cycle
        return phase >= self.cycle - self.on_time

    def update(self, dt):
        self.t += dt

    def check_collision(self, prect):
        if not self.is_hazard:
            return False
        return self.rect.colliderect(prect)

    def draw(self, surf, cam_x):
        x = self.x - cam_x
        phase = self.t % self.cycle
        warning = self.cycle - self.on_time - self.warn_time <= phase < self.cycle - self.on_time
        firing = phase >= self.cycle - self.on_time
        if firing:
            pygame.draw.rect(surf, (255, 60, 70), (x, self.y, self.w, self.h))
            pygame.draw.rect(surf, (255, 200, 200), (x + 3, self.y, self.w - 6, self.h))
        elif warning:
            alpha_line = pygame.Surface((2, self.h), pygame.SRCALPHA)
            alpha_line.fill((255, 80, 80, 140))
            surf.blit(alpha_line, (x + self.w / 2 - 1, self.y))


class FallingRock(Obstacle):
    """Rock that drops when the player approaches, then respawns."""
    kind = "falling_rock"
    is_hazard = True

    def __init__(self, x, trigger_y, ground_y, size=30):
        super().__init__(x, trigger_y - size, size, size)
        self.start_y = self.y
        self.ground_y = ground_y
        self.size = size
        self.state = "idle"  # idle, falling, settled, respawning
        self.vy = 0.0
        self.timer = 0.0

    def trigger(self):
        if self.state == "idle":
            self.state = "falling"
            self.vy = 0

    def update(self, dt):
        if self.state == "falling":
            self.vy += 1800 * dt
            self.y += self.vy * dt
            if self.y + self.size >= self.ground_y:
                self.y = self.ground_y - self.size
                self.state = "settled"
                self.timer = 1.2
        elif self.state == "settled":
            self.timer -= dt
            if self.timer <= 0:
                self.state = "respawning"
                self.timer = 1.0
        elif self.state == "respawning":
            self.timer -= dt
            if self.timer <= 0:
                self.state = "idle"
                self.y = self.start_y

    def check_collision(self, prect):
        if self.state in ("idle", "respawning"):
            return False
        return self.rect.colliderect(prect)

    def draw(self, surf, cam_x):
        if self.state == "respawning":
            return
        x = self.x - cam_x
        col = (110, 100, 95) if self.state != "idle" else (150, 140, 130)
        pygame.draw.rect(surf, col, (x, self.y, self.size, self.size), border_radius=6)
        pygame.draw.rect(surf, (60, 55, 52), (x, self.y, self.size, self.size), 2, border_radius=6)


class Crusher(Obstacle):
    """Ceiling-mounted block that slams down periodically."""
    kind = "crusher"
    is_hazard = True

    def __init__(self, x, ceiling_y, ground_y, width=54, cycle=2.4):
        self.ceiling_y = ceiling_y
        self.ground_y = ground_y
        self.rest_h = 46
        super().__init__(x, ceiling_y, width, self.rest_h)
        self.cycle = cycle
        self.t = 0.0

    def update(self, dt):
        self.t = (self.t + dt) % self.cycle
        phase = self.t / self.cycle
        if phase < 0.45:
            self.h = self.rest_h
        elif phase < 0.55:
            k = (phase - 0.45) / 0.10
            self.h = self.rest_h + k * ((self.ground_y - self.ceiling_y) - self.rest_h)
        elif phase < 0.75:
            self.h = self.ground_y - self.ceiling_y
        else:
            k = (phase - 0.75) / 0.25
            self.h = (self.ground_y - self.ceiling_y) - k * ((self.ground_y - self.ceiling_y) - self.rest_h)

    def draw(self, surf, cam_x):
        x = self.x - cam_x
        r = pygame.Rect(int(x), int(self.ceiling_y), int(self.w), int(self.h))
        pygame.draw.rect(surf, (120, 60, 60), r)
        pygame.draw.rect(surf, (80, 30, 30), r, 3)
        spike_y = r.bottom
        pygame.draw.polygon(surf, (200, 190, 190),
                             [(x, spike_y), (x + self.w, spike_y), (x + self.w / 2, spike_y + 14)])


# ---------------------------------------------------------------------------
# Decorative / collectible
# ---------------------------------------------------------------------------
class Coin(Obstacle):
    kind = "coin"

    def __init__(self, x, y):
        super().__init__(x, y, 22, 22)
        self.collected = False
        self.t = 0.0

    def update(self, dt):
        self.t += dt * 4

    def check_collision(self, prect):
        if self.collected:
            return False
        return self.rect.colliderect(prect)

    def draw(self, surf, cam_x):
        if self.collected:
            return
        x = self.x - cam_x + self.w / 2
        y = self.y + self.h / 2
        squish = abs(math.sin(self.t))
        rw = max(2, int(self.w / 2 * (0.3 + 0.7 * squish)))
        pygame.draw.ellipse(surf, (255, 215, 90), (x - rw, y - self.h / 2, rw * 2, self.h))
        pygame.draw.ellipse(surf, (200, 150, 40), (x - rw, y - self.h / 2, rw * 2, self.h), 2)