"""
sound_manager.py
----------------
Simple sound manager with optional file playback and fallback mute behavior.
"""
import os
import pygame

from constants import SOUND_DIR

class SoundManager:
    def __init__(self):
        self.sfx_volume = 0.8
        self.enabled = False
        self.sounds = {}
        try:
            pygame.mixer.init()
            self.enabled = True
        except pygame.error:
            self.enabled = False
        for name in ('jump', 'coin', 'powerup', 'death'):
            self.sounds[name] = self._load_sound(name)

    def _load_sound(self, name):
        if not self.enabled:
            return None
        path = os.path.join(SOUND_DIR, f'{name}.wav')
        if os.path.isfile(path):
            try:
                sound = pygame.mixer.Sound(path)
                sound.set_volume(self.sfx_volume)
                return sound
            except pygame.error:
                return None
        return None

    def play(self, name):
        sound = self.sounds.get(name)
        if self.enabled and sound is not None:
            try:
                sound.play()
            except pygame.error:
                pass

    def set_volume(self, volume):
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            if sound is not None:
                sound.set_volume(self.sfx_volume)
