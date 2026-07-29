"""
camera.py
---------
The Camera tracks the player upward with smooth interpolation, and supports
a screen-shake effect (used when the player touches lava / dies).
The world only ever needs to scroll up (the player is always climbing),
so the camera's target y only decreases, never increases back down,
which keeps platforms from "reappearing" behind the player.
"""

import random
from constants import SCREEN_HEIGHT, SCREEN_WIDTH


class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.target_y = 0.0
        self.smoothing = 6.0          # higher = snappier follow
        self.shake_time = 0.0
        self.shake_strength = 0.0
        self.shake_offset = (0, 0)

    def follow(self, player):
        # Keep the player roughly in the lower-middle third of the screen.
        # Only move the camera upward when the player climbs higher.
        desired_y = player.y - SCREEN_HEIGHT * 0.55
        self.target_y = min(self.target_y, desired_y)

    def update(self, dt):
        self.y += (self.target_y - self.y) * min(1.0, self.smoothing * dt)

        if self.shake_time > 0:
            self.shake_time -= dt
            mag = self.shake_strength * max(0.0, self.shake_time)
            self.shake_offset = (
                random.uniform(-mag, mag),
                random.uniform(-mag, mag),
            )
        else:
            self.shake_offset = (0, 0)

    def shake(self, strength=18.0, duration=0.45):
        self.shake_strength = max(self.shake_strength, strength)
        self.shake_time = max(self.shake_time, duration)

    @property
    def offset(self):
        """Returns the (x, y) to subtract from world coordinates to get
        screen coordinates, including any active shake."""
        return (
            self.x - self.shake_offset[0],
            self.y - self.shake_offset[1],
        )
