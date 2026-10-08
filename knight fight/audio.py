import pygame


class AudioManager:
    def __init__(self):
        self.enabled = True
        self.music = None

    def play_music(self, src):
        """Play looping music. Accepts either a filepath or a preloaded pygame.mixer.Sound.
        Gracefully ignores errors (e.g., missing audio device or file)."""
        if not self.enabled:
            return
        try:
            if isinstance(src, pygame.mixer.Sound):
                self.music = src
            else:
                self.music = pygame.mixer.Sound(src)
            self.music.play(-1)
        except Exception:
            self.music = None

    def stop_music(self):
        if self.music:
            self.music.stop()
            self.music = None

    def play_sfx(self, src):
        if not self.enabled:
            return
        try:
            if isinstance(src, pygame.mixer.Sound):
                sound = src
            else:
                sound = pygame.mixer.Sound(src)
            sound.play()
        except Exception:
            return
