"""
camera.py - Simple smoothed camera that follows a target within level bounds.
"""
from settings import SCREEN_W, SCREEN_H


class Camera:
    def __init__(self, level_w, level_h):
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.level_w = level_w
        self.level_h = level_h
        self.smoothing = 6.0  # higher = snappier

    def set_level_bounds(self, w, h):
        self.level_w = w
        self.level_h = h

    def update(self, target_rect, dt):
        target_x = target_rect.centerx - SCREEN_W / 2
        target_y = target_rect.centery - SCREEN_H / 2

        # Clamp to level bounds so we never show outside the map
        target_x = max(0, min(target_x, max(0, self.level_w - SCREEN_W)))
        target_y = max(0, min(target_y, max(0, self.level_h - SCREEN_H)))

        # Exponential smoothing towards target (frame-rate independent)
        lerp = 1 - pow(0.001, dt * self.smoothing)
        self.offset_x += (target_x - self.offset_x) * lerp
        self.offset_y += (target_y - self.offset_y) * lerp

    def apply(self, rect):
        """Return a screen-space rect for a world-space rect."""
        return rect.move(-int(self.offset_x), -int(self.offset_y))

    def apply_pos(self, x, y):
        return x - self.offset_x, y - self.offset_y