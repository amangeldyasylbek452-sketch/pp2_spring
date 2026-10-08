"""
sprites.py - Procedural pixel-art sprite generation.

This project ships with no external art files. Instead, every character is
built out of small filled rectangles on a low-res Surface which is then
scaled up with NEAREST-neighbour scaling, producing a genuine "pixel art"
look entirely in code. This keeps the game runnable with zero missing
assets while still matching the requested visual style.
"""
import pygame
from settings import (SKIN, STEEL, STEEL_DARK, CLOAK_RED, BONE, GHOST_BLUE, WHITE)

PIXEL_SCALE = 4  # low-res canvas scaled up 4x for a chunky pixel look


def _canvas(w, h):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    return surf


def _scale(surf):
    w, h = surf.get_size()
    return pygame.transform.scale(surf, (w * PIXEL_SCALE, h * PIXEL_SCALE))


def make_knight_frame(pose="idle", frame=0, facing=1):
    """Builds one low-res frame of the knight and returns it pixel-scaled."""
    c = _canvas(16, 20)
    bob = 0
    leg_off = 0
    arm_ang = 0

    if pose == "walk":
        bob = 1 if frame % 2 == 0 else 0
        leg_off = 2 if frame % 2 == 0 else -2
    elif pose == "run":
        bob = 1 if frame % 2 == 0 else -1
        leg_off = 3 if frame % 2 == 0 else -3
    elif pose == "attack":
        arm_ang = [4, 7, 2][frame % 3]
    elif pose == "dash":
        bob = -1
    elif pose == "hurt":
        bob = 1
    elif pose == "death":
        bob = 3

    # legs
    pygame.draw.rect(c, STEEL_DARK, (5, 14 + bob, 2, 5 - (bob if pose == "death" else 0)))
    pygame.draw.rect(c, STEEL_DARK, (9, 14 + bob - leg_off // 2, 2, 5))
    # torso / armor
    pygame.draw.rect(c, STEEL, (4, 8 + bob, 8, 7))
    pygame.draw.rect(c, STEEL_DARK, (4, 8 + bob, 8, 2))
    # cloak
    pygame.draw.rect(c, CLOAK_RED, (3, 9 + bob, 2, 6))
    # head
    pygame.draw.rect(c, SKIN, (6, 4 + bob, 4, 4))
    pygame.draw.rect(c, STEEL, (5, 3 + bob, 6, 3))  # helmet
    # sword arm
    sx = 12 if facing == 1 else 2
    pygame.draw.rect(c, STEEL_DARK, (sx, 7 + bob - arm_ang, 2, 8))
    pygame.draw.rect(c, (200, 205, 215), (sx, 2 + bob - arm_ang, 2, 6))  # blade
    if facing == -1:
        c = pygame.transform.flip(c, True, False)
    return _scale(c)


def make_skeleton_frame(pose="idle", frame=0, facing=1, archer=False):
    c = _canvas(14, 18)
    bob = 1 if (pose in ("walk", "chase") and frame % 2 == 0) else 0
    pygame.draw.rect(c, BONE, (5, 12 + bob, 2, 5))
    pygame.draw.rect(c, BONE, (8, 12 + bob, 2, 5))
    pygame.draw.rect(c, (210, 205, 185), (4, 7 + bob, 7, 6))  # ribcage block
    for ry in range(8 + bob, 12 + bob, 2):
        pygame.draw.line(c, (150, 145, 130), (4, ry), (10, ry), 1)
    pygame.draw.rect(c, BONE, (5, 3 + bob, 4, 4))  # skull
    pygame.draw.rect(c, (20, 15, 15), (6, 4 + bob, 1, 1))  # eye socket
    pygame.draw.rect(c, (20, 15, 15), (8, 4 + bob, 1, 1))
    if archer:
        pygame.draw.line(c, (120, 90, 60), (10, 6 + bob), (10, 12 + bob), 1)  # bow
    else:
        pygame.draw.rect(c, (170, 170, 175), (10, 6 + bob, 1, 7))  # rusty sword
    if facing == -1:
        c = pygame.transform.flip(c, True, False)
    return _scale(c)


def make_bat_frame(frame=0):
    c = _canvas(12, 8)
    wing = 2 if frame % 2 == 0 else -1
    pygame.draw.polygon(c, (40, 35, 55), [(0, 4 - wing), (5, 3), (5, 5)])
    pygame.draw.polygon(c, (40, 35, 55), [(12, 4 - wing), (7, 3), (7, 5)])
    pygame.draw.ellipse(c, (55, 48, 70), (4, 2, 4, 4))
    pygame.draw.rect(c, (255, 60, 60), (5, 3, 1, 1))
    return _scale(c)


def make_captain_frame(pose="idle", frame=0, facing=1):
    """Bigger, tougher skeleton captain mini-boss."""
    c = _canvas(20, 26)
    bob = 1 if frame % 2 == 0 and pose != "idle" else 0
    pygame.draw.rect(c, BONE, (7, 18 + bob, 3, 7))
    pygame.draw.rect(c, BONE, (11, 18 + bob, 3, 7))
    pygame.draw.rect(c, (60, 20, 25), (5, 9 + bob, 11, 9))  # dark armor chest
    pygame.draw.rect(c, (90, 30, 35), (5, 9 + bob, 11, 2))
    pygame.draw.rect(c, BONE, (8, 4 + bob, 5, 5))  # skull
    pygame.draw.rect(c, (255, 40, 40), (9, 6 + bob, 1, 1))
    pygame.draw.rect(c, (255, 40, 40), (12, 6 + bob, 1, 1))
    pygame.draw.rect(c, (40, 30, 20), (16, 2 + bob, 2, 3))  # horned helm spikes
    sx = 16 if facing == 1 else 1
    pygame.draw.rect(c, (80, 80, 90), (sx, 4 + bob, 3, 14))  # huge blade
    if facing == -1:
        c = pygame.transform.flip(c, True, False)
    return _scale(c)


def make_ghost_frame(frame=0):
    c = _canvas(12, 14)
    wob = 1 if frame % 2 == 0 else 0
    s = pygame.Surface((12, 14), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (*GHOST_BLUE, 160), (2, 2 + wob, 8, 9))
    pygame.draw.rect(s, (*GHOST_BLUE, 160), (2, 8 + wob, 8, 4))
    pygame.draw.rect(s, (20, 30, 50, 200), (4, 5 + wob, 1, 2))
    pygame.draw.rect(s, (20, 30, 50, 200), (7, 5 + wob, 1, 2))
    return _scale(s)


def make_dragon_frame(phase=1, frame=0, facing=1):
    c = _canvas(32, 24)
    body = (120, 35, 25)
    wing = (70, 25, 20)
    eye = (255, 120, 80)
    pygame.draw.rect(c, body, (8, 8, 16, 10))
    pygame.draw.rect(c, body, (14, 4, 8, 6))
    pygame.draw.rect(c, wing, (2, 8, 6, 8))
    pygame.draw.rect(c, wing, (24, 8, 6, 8))
    pygame.draw.rect(c, eye, (12, 7, 2, 2))
    pygame.draw.rect(c, eye, (18, 7, 2, 2))
    pygame.draw.rect(c, (220, 30, 30), (12, 2, 2, 4))
    pygame.draw.rect(c, (220, 30, 30), (18, 2, 2, 4))
    if phase >= 2:
        pygame.draw.rect(c, (255, 140, 40), (2, 4, 4, 8))
    if phase >= 3:
        pygame.draw.rect(c, (255, 80, 20), (26, 4, 4, 8))
    if facing == -1:
        c = pygame.transform.flip(c, True, False)
    return _scale(c)