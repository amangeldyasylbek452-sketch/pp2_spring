"""
audio.py - Fully procedural audio. No external sound or music files are used;
every effect and music loop is synthesized at runtime with numpy and played
back through pygame's mixer via sndarray.
"""
import numpy as np
import pygame
import math

SAMPLE_RATE = 44100


def _env(n, attack=0.02, release=0.3):
    """Simple attack/release envelope of length n samples."""
    a = max(1, int(attack * SAMPLE_RATE))
    r = max(1, int(release * SAMPLE_RATE))
    env = np.ones(n)
    a = min(a, n)
    r = min(r, n)
    env[:a] = np.linspace(0, 1, a)
    env[n - r:] = np.linspace(1, 0, r)
    return env


def _tone(freq, duration, wave="sine", volume=0.5, attack=0.01, release=0.1,
          vibrato=0.0, sweep_to=None):
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    if sweep_to is not None:
        freq_arr = np.linspace(freq, sweep_to, n)
    else:
        freq_arr = np.full(n, freq)
    if vibrato:
        freq_arr = freq_arr + np.sin(2 * np.pi * 6 * t) * vibrato
    phase = 2 * np.pi * np.cumsum(freq_arr) / SAMPLE_RATE
    if wave == "sine":
        wav = np.sin(phase)
    elif wave == "square":
        wav = np.sign(np.sin(phase))
    elif wave == "saw":
        wav = 2 * (phase / (2 * np.pi) % 1) - 1
    elif wave == "triangle":
        wav = 2 * np.abs(2 * (phase / (2 * np.pi) % 1) - 1) - 1
    elif wave == "noise":
        wav = np.random.uniform(-1, 1, n)
    else:
        wav = np.sin(phase)
    wav *= _env(n, attack, release) * volume
    return wav


def _mix(*waves):
    n = max(len(w) for w in waves)
    out = np.zeros(n)
    for w in waves:
        out[:len(w)] += w
    peak = np.max(np.abs(out)) if out.size else 1.0
    if peak > 1.0:
        out /= peak
    return out


def _to_sound(wav):
    stereo = np.column_stack([wav, wav])
    arr = np.ascontiguousarray((stereo * 32767).astype(np.int16))
    return pygame.sndarray.make_sound(arr)


class AudioEngine:
    """Generates and caches all SFX; plays procedural background music loops."""

    def __init__(self):
        self.enabled = True
        try:
            pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2)
            self.available = True
        except pygame.error:
            self.available = False
        self.sfx_volume = 0.7
        self.music_volume = 0.5
        self._cache = {}
        self.music_channel = None
        if self.available:
            self._build_sfx()

    # -- SFX ---------------------------------------------------------------
    def _build_sfx(self):
        self._cache["jump"] = _to_sound(_tone(520, 0.14, "square", 0.35,
                                               sweep_to=780, release=0.1))
        self._cache["double_jump"] = _to_sound(_tone(680, 0.16, "square", 0.35,
                                                      sweep_to=980, release=0.12))
        self._cache["coin"] = _to_sound(_mix(
            _tone(880, 0.09, "sine", 0.3, release=0.06),
            _tone(1320, 0.12, "sine", 0.25, attack=0.03, release=0.09)))
        self._cache["death"] = _to_sound(_tone(300, 0.4, "saw", 0.35,
                                                sweep_to=60, release=0.35))
        self._cache["click"] = _to_sound(_tone(440, 0.06, "square", 0.2, release=0.04))
        self._cache["explosion"] = _to_sound(_mix(
            _tone(90, 0.35, "noise", 0.4, release=0.3),
            _tone(70, 0.4, "sine", 0.3, sweep_to=30, release=0.35)))
        self._cache["finish"] = _to_sound(_mix(
            _tone(523, 0.12, "sine", 0.3, release=0.08),
            _tone(659, 0.12, "sine", 0.3, attack=0.06, release=0.1),
            _tone(784, 0.2, "sine", 0.3, attack=0.12, release=0.15)))
        self._cache["land"] = _to_sound(_tone(150, 0.08, "sine", 0.2, release=0.06))

    def play(self, name):
        if not self.available or not self.enabled:
            return
        snd = self._cache.get(name)
        if snd:
            snd.set_volume(self.sfx_volume)
            snd.play()

    # -- Music ---------------------------------------------------------------
    def _scale_for_world(self, world_id):
        scales = {
            "green_hills": [261.6, 293.7, 329.6, 392.0, 440.0],
            "crystal_cave": [220.0, 246.9, 261.6, 329.6, 392.0],
            "volcano": [196.0, 233.1, 261.6, 293.7, 349.2],
            "ice_kingdom": [246.9, 277.2, 329.6, 369.9, 415.3],
            "ancient_temple": [220.0, 261.6, 293.7, 349.2, 392.0],
            "cyber_city": [233.1, 277.2, 311.1, 370.0, 466.2],
            "space_station": [196.0, 220.0, 261.6, 311.1, 349.2],
        }
        return scales.get(world_id, scales["green_hills"])

    def build_music_loop(self, world_id, tempo=140):
        """Synthesize a short seamless background loop for a world."""
        import random as _r
        rng = _r.Random(hash(world_id) & 0xffff)
        scale = self._scale_for_world(world_id)
        beat = 60.0 / tempo
        notes = []
        for _ in range(16):
            notes.append(rng.choice(scale) / 2)
        waves = []
        t_cursor = 0
        for i, freq in enumerate(notes):
            dur = beat * rng.choice([0.5, 0.5, 1.0])
            wav = _tone(freq, dur, "triangle", 0.18, attack=0.01, release=dur * 0.5)
            bass = _tone(freq / 2, dur, "sine", 0.12, attack=0.01, release=dur * 0.6)
            waves.append(_mix(wav, bass))
        full = np.concatenate(waves)
        return _to_sound(full)

    def play_music(self, world_id, tempo=140):
        if not self.available or not self.enabled:
            return
        snd = self._cache.get(f"music_{world_id}")
        if snd is None:
            snd = self.build_music_loop(world_id, tempo)
            self._cache[f"music_{world_id}"] = snd
        if self.music_channel is None:
            self.music_channel = pygame.mixer.Channel(7)
        snd.set_volume(self.music_volume)
        self.music_channel.play(snd, loops=-1)

    def stop_music(self):
        if self.music_channel:
            self.music_channel.stop()

    def set_sfx_volume(self, v):
        self.sfx_volume = max(0.0, min(1.0, v))

    def set_music_volume(self, v):
        self.music_volume = max(0.0, min(1.0, v))
        if self.music_channel:
            self.music_channel.set_volume(self.music_volume)