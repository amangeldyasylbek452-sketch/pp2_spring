"""
assets.py - Centralized asset manager with caching and graceful fallbacks.

This module provides a lightweight AssetManager to load and cache images, sounds
and fonts. It handles missing assets gracefully by returning placeholder surfaces
or None for sounds. The class is intentionally simple so it can be integrated
incrementally into the existing codebase.

Design goals:
- Single place to load/cache assets
- Graceful fallback on missing files (no crash at runtime)
- Small, well-documented API for future expansion (atlasing, async loading)
"""
from __future__ import annotations

import os
import typing as T
import pygame


class AssetManager:
    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = data_dir
        self._images: dict[str, pygame.Surface] = {}
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        self._fonts: dict[tuple[str, int], pygame.font.Font] = {}

    def _full_path(self, relative: str) -> str:
        return os.path.join(self.data_dir, relative)

    # Images
    def load_image(self, relative_path: str) -> pygame.Surface:
        """Load an image and return a Surface (convert_alpha used). Returns a
        placeholder surface if file is missing or loading fails."""
        if relative_path in self._images:
            return self._images[relative_path]
        full = self._full_path(relative_path)
        try:
            surf = pygame.image.load(full).convert_alpha()
        except Exception:
            surf = self._placeholder_image()
        self._images[relative_path] = surf
        return surf

    def _placeholder_image(self, w: int = 48, h: int = 48) -> pygame.Surface:
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        s.fill((120, 120, 140))
        pygame.draw.rect(s, (80, 80, 90), s.get_rect(), 2)
        return s

    # Sounds
    def load_sound(self, relative_path: str) -> T.Optional[pygame.mixer.Sound]:
        if relative_path in self._sounds:
            return self._sounds[relative_path]
        full = self._full_path(relative_path)
        try:
            snd = pygame.mixer.Sound(full)
        except Exception:
            snd = None
        self._sounds[relative_path] = snd
        return snd

    # Fonts
    def load_font(self, font_name: str, size: int) -> pygame.font.Font:
        key = (font_name, size)
        if key in self._fonts:
            return self._fonts[key]
        try:
            f = pygame.font.Font(os.path.join(self.data_dir, font_name), size)
        except Exception:
            try:
                f = pygame.font.SysFont(font_name, size)
            except Exception:
                f = pygame.font.SysFont("arial", size)
        self._fonts[key] = f
        return f


# Simple module-level convenience instance for quick integration
_default: T.Optional[AssetManager] = None


def get_default(data_dir: str = "data") -> AssetManager:
    global _default
    if _default is None:
        _default = AssetManager(data_dir)
    return _default
