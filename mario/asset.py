"""Procedural asset generation for all game graphics and sounds."""
import pygame
import math
import random
from constants import *


# ── COLOUR PALETTES ──────────────────────────────────────────────
PALETTES = {
    "moon":     [(160,170,200),(120,130,170),(80,90,140),(200,210,230)],
    "crystal":  [(150,220,255),(100,180,240),(60,140,220),(200,240,255)],
    "station":  [(100,110,130),(70,80,100),(140,150,160),(60,65,80)],
    "asteroid": [(130,120,110),(100,95,85),(160,150,140),(80,75,70)],
    "nebula":   [(200,120,255),(160,80,220),(240,160,255),(120,60,180)],
    "blackhole":[(20,10,40),(40,20,80),(60,30,100),(10,5,20)],
    "volcanic": [(220,80,30),(180,60,20),(255,120,40),(140,40,10)],
    "void":     [(60,0,80),(40,0,60),(100,20,120),(20,0,40)],
}


def make_player_surf(frame: int = 0) -> pygame.Surface:
    """Animated player sprite – space explorer with jump boots."""
    s = pygame.Surface((40, 52), pygame.SRCALPHA)
    # Body – spacesuit
    body_col = (60, 100, 200)
    visor_col = (100, 220, 255, 200)
    suit_col  = (80, 120, 220)
    
    # legs
    leg_off = int(math.sin(frame * 0.4) * 4)
    pygame.draw.rect(s, (40, 70, 160), (8,  36+leg_off, 10, 16))
    pygame.draw.rect(s, (40, 70, 160), (22, 36-leg_off, 10, 16))
    # boots
    pygame.draw.rect(s, CRYSTAL,       (6,  50+leg_off, 14, 4))
    pygame.draw.rect(s, CRYSTAL,       (20, 50-leg_off, 14, 4))
    # boot glow
    pygame.draw.ellipse(s, (*CYAN, 120), (4, 52+leg_off, 16, 6))
    pygame.draw.ellipse(s, (*CYAN, 120), (20,52-leg_off, 16, 6))
    # torso
    pygame.draw.rect(s, suit_col, (6, 20, 28, 20))
    # arms
    arm_off = int(math.sin(frame * 0.4 + math.pi) * 3)
    pygame.draw.rect(s, body_col, (0,  22+arm_off, 8, 12))
    pygame.draw.rect(s, body_col, (32, 22-arm_off, 8, 12))
    # helmet
    pygame.draw.ellipse(s, body_col, (4, 4, 32, 20))
    # visor
    pygame.draw.ellipse(s, visor_col, (8, 7, 24, 14))
    # chest light
    pygame.draw.circle(s, PLASMA, (20, 28), 4)
    pygame.draw.circle(s, WHITE,  (20, 28), 2)
    # plasma blaster on right arm
    pygame.draw.rect(s, (40, 200, 140), (32, 24-arm_off, 12, 6))
    return s


def make_enemy_surf(kind: str, frame: int = 0) -> pygame.Surface:
    s = pygame.Surface((40, 40), pygame.SRCALPHA)
    t = frame * 0.15
    
    if kind == "drone":
        # Robotic drone
        pygame.draw.rect(s, (80, 90, 110), (8, 12, 24, 16))
        pygame.draw.rect(s, (120, 130, 150), (12, 8, 16, 8))
        # rotor blades
        for angle in [t, t+math.pi/2, t+math.pi, t+3*math.pi/2]:
            x = 20 + int(math.cos(angle)*14)
            y = 10 + int(math.sin(angle)*4)
            pygame.draw.line(s, (180,190,200), (20,10), (x,y), 2)
        pygame.draw.circle(s, RED, (20, 28), 5)
        pygame.draw.circle(s, (255,100,100), (20, 28), 2)
        
    elif kind == "jellyfish":
        # Plasma jellyfish
        bob = int(math.sin(t*2)*4)
        col = (100+int(math.sin(t)*50), 80, 200+int(math.cos(t)*55))
        pygame.draw.ellipse(s, col, (6, 4+bob, 28, 18))
        pygame.draw.ellipse(s, (*col[:2], col[2], 180), (10, 6+bob, 20, 14))
        for i in range(5):
            tx = t + i*0.6
            x0 = 10 + i*5
            pygame.draw.line(s, (*PURPLE, 200), (x0, 22+bob),
                             (x0+int(math.sin(tx)*4), 38), 2)
            
    elif kind == "spider":
        # Crystal spider
        pygame.draw.ellipse(s, (80, 180, 220), (10, 14, 20, 14))
        pygame.draw.ellipse(s, (120, 210, 240), (13, 10, 14, 12))
        for i in range(4):
            angle_l = math.pi*0.3 + i*0.35 + math.sin(t)*0.2
            angle_r = math.pi*0.7 - i*0.35 - math.sin(t)*0.2
            lx = 14 + int(math.cos(math.pi-angle_l)*16)
            ly = 20 + int(math.sin(math.pi-angle_l)*12)
            rx = 26 + int(math.cos(angle_r)*16)
            ry = 20 + int(math.sin(angle_r)*12)
            pygame.draw.line(s, (60,150,200), (14,20), (lx,ly), 2)
            pygame.draw.line(s, (60,150,200), (26,20), (rx,ry), 2)
        pygame.draw.circle(s, RED, (20, 16), 3)
        
    elif kind == "turret":
        pygame.draw.rect(s, (100,110,120), (10, 20, 20, 16))
        pygame.draw.rect(s, (130,140,150), (12, 18, 16, 6))
        barrel_x = 20 + int(math.cos(t)*10)
        barrel_y = 20 + int(math.sin(t)*6)
        pygame.draw.line(s, (200,50,50), (20,20), (barrel_x,barrel_y), 4)
        
    elif kind == "slime":
        # Gravity slime
        squish = int(math.sin(t*2)*3)
        pygame.draw.ellipse(s, (80,200,100), (6, 10+squish, 28, 22-squish))
        pygame.draw.ellipse(s, (120,230,140), (10, 12+squish, 20, 14-squish))
        pygame.draw.circle(s, BLACK, (15, 18+squish), 3)
        pygame.draw.circle(s, BLACK, (25, 18+squish), 3)
        
    elif kind == "bat":
        # Cosmic bat
        wing_flap = math.sin(t*3) * 0.4
        pygame.draw.polygon(s, (120,40,160), [
            (20,18), (4, 12+int(wing_flap*8)), (2,24), (14,22)])
        pygame.draw.polygon(s, (120,40,160), [
            (20,18), (36,12+int(-wing_flap*8)), (38,24), (26,22)])
        pygame.draw.ellipse(s, (150,60,180), (13,14,14,12))
        pygame.draw.circle(s, (255,100,50), (16,18), 2)
        pygame.draw.circle(s, (255,100,50), (24,18), 2)
        
    elif kind == "ghost":
        # Energy ghost
        alpha = 180 + int(math.sin(t*2)*60)
        col = (150, 180, 255, alpha)
        surf2 = pygame.Surface((40,40), pygame.SRCALPHA)
        bob = int(math.sin(t)*4)
        pygame.draw.ellipse(surf2, col, (6, 4+bob, 28, 26))
        for i in range(3):
            pygame.draw.ellipse(surf2, col,
                (6+i*8, 26+bob+int(math.sin(t+i)*3), 10, 8))
        s.blit(surf2, (0,0))
        pygame.draw.circle(s, WHITE, (15, 16+bob), 4)
        pygame.draw.circle(s, WHITE, (25, 16+bob), 4)
        pygame.draw.circle(s, BLACK, (15, 16+bob), 2)
        pygame.draw.circle(s, BLACK, (25, 16+bob), 2)
        
    elif kind == "pirate":
        # Space pirate
        pygame.draw.rect(s, (100,60,120), (8, 16, 24, 22))
        pygame.draw.ellipse(s, (140,100,160), (6, 8, 28, 18))
        pygame.draw.rect(s, (60,40,80), (8,34,8,8))
        pygame.draw.rect(s, (60,40,80), (24,34,8,8))
        pygame.draw.rect(s, (200,160,50), (16,14,8,6))  # belt
        pygame.draw.circle(s, (255,80,80), (20,14), 3)  # gem
        
    return s


def make_boss_surf(kind: str, phase: int = 0, frame: int = 0) -> pygame.Surface:
    t = frame * 0.1
    
    if kind == "spider":
        s = pygame.Surface((200, 160), pygame.SRCALPHA)
        col = (60+phase*30, 20, 100+phase*40)
        pygame.draw.ellipse(s, col, (50, 50, 100, 70))
        pygame.draw.ellipse(s, (col[0]+40,col[1]+20,col[2]+40), (60,56,80,58))
        for i in range(4):
            a_l = math.pi*0.2 + i*0.4 + math.sin(t+i)*0.3
            a_r = math.pi*0.8 - i*0.4 - math.sin(t+i)*0.3
            ex_l = 60 + int(math.cos(math.pi-a_l)*70)
            ey_l = 85 + int(math.sin(math.pi-a_l)*50)
            ex_r = 140 + int(math.cos(a_r)*70)
            ey_r = 85 + int(math.sin(a_r)*50)
            pygame.draw.line(s, (80,30,120), (60,85),(ex_l,ey_l),4)
            pygame.draw.line(s, (80,30,120),(140,85),(ex_r,ey_r),4)
        for i in range(6):
            pygame.draw.circle(s, RED, (60+i*16, 62+int(math.sin(t+i)*4)), 5)
        pygame.draw.polygon(s, (200,100,50), [(90,50),(100,36),(110,50)])
        return s
        
    elif kind == "robot":
        s = pygame.Surface((160, 200), pygame.SRCALPHA)
        col = (80,90,110)
        pygame.draw.rect(s, col, (30,60,100,100))
        pygame.draw.rect(s, (110,120,140),(40,20,80,50))
        arm_off = int(math.sin(t)*10)
        pygame.draw.rect(s, col, (0, 70+arm_off, 32, 60))
        pygame.draw.rect(s, col, (128,70-arm_off,32,60))
        pygame.draw.rect(s, col, (40,158,30,44))
        pygame.draw.rect(s, col, (90,158,30,44))
        pygame.draw.rect(s, (200,50,50), (50,30,60,30))
        pygame.draw.rect(s, (255,100,100),(58,36,44,18))
        pygame.draw.circle(s, CYAN, (80,44), 10)
        pygame.draw.circle(s, WHITE,(80,44), 5)
        return s
        
    elif kind == "dragon":
        s = pygame.Surface((240, 180), pygame.SRCALPHA)
        col = (180,80,20) if phase==0 else (120,20,160)
        wing_a = math.sin(t) * 0.3
        pygame.draw.polygon(s, (col[0]//2,col[1]//2,col[2]//2), [
            (120,80),(40,20+int(wing_a*40)),(20,100),(80,110)])
        pygame.draw.polygon(s, (col[0]//2,col[1]//2,col[2]//2), [
            (120,80),(200,20+int(-wing_a*40)),(220,100),(160,110)])
        pygame.draw.ellipse(s, col, (60,70,120,80))
        pygame.draw.ellipse(s, col, (30,60,70,50))
        pygame.draw.circle(s, (255,220,50), (32,68), 8)
        pygame.draw.circle(s, BLACK, (32,68), 4)
        for i in range(6):
            spike_x = 66+i*18
            pygame.draw.polygon(s, (col[0]+40,col[1],col[2]),
                [(spike_x,70),(spike_x+8,56),(spike_x+16,70)])
        return s
        
    elif kind == "gravitas":
        s = pygame.Surface((180, 180), pygame.SRCALPHA)
        for r in range(80, 0, -10):
            alpha = max(0, 255 - r*2)
            col = (20+r, 0, 40+r*2, alpha)
            pygame.draw.circle(s, col, (90,90), r)
        # accretion disk
        for i in range(60):
            a = i/60*math.tau + t
            r_inner, r_outer = 70, 90
            col_d = (200+int(math.sin(a*3)*55), 100+int(math.cos(a*2)*50), 50)
            pygame.draw.circle(s, col_d,
                (90+int(math.cos(a)*r_inner), 90+int(math.sin(a)*r_inner//3)), 3)
        pygame.draw.circle(s, BLACK, (90,90), 36)
        return s
        
    elif kind == "emperor":
        s = pygame.Surface((200, 240), pygame.SRCALPHA)
        col = (60,0,80) if phase<2 else (120,0,20)
        # robe
        pygame.draw.polygon(s, col,[(40,80),(160,80),(180,240),(20,240)])
        # torso/armor
        pygame.draw.rect(s, (col[0]+40,col[1]+20,col[2]+40),(60,50,80,50))
        # head
        pygame.draw.ellipse(s, (col[0]+60,col[1]+30,col[2]+60),(60,10,80,50))
        # crown
        for i in range(5):
            pygame.draw.polygon(s, GOLD,
                [(72+i*14,10),(76+i*14,0),(80+i*14,10)])
        # eyes
        eye_glow = int(math.sin(t*3)*50)
        pygame.draw.circle(s, (255,100+eye_glow,50), (80,34), 8)
        pygame.draw.circle(s, (255,100+eye_glow,50),(120,34), 8)
        pygame.draw.circle(s, (255,200,50),(80,34),4)
        pygame.draw.circle(s, (255,200,50),(120,34),4)
        # staff
        pygame.draw.rect(s, GOLD, (155,40,6,180))
        pygame.draw.circle(s, PURPLE, (158,40), 14)
        pygame.draw.circle(s, WHITE, (158,40), 6)
        # cape
        pygame.draw.polygon(s, (40,0,60),
            [(40,80),(0,200),(20,240),(40,200),(60,80)])
        return s
    
    return pygame.Surface((80,80), pygame.SRCALPHA)


def make_tile_surf(kind: int, palette: str = "moon") -> pygame.Surface:
    s = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    cols = PALETTES.get(palette, PALETTES["moon"])
    
    if kind == TILE_SOLID:
        s.fill(cols[0])
        pygame.draw.rect(s, cols[1], (0,0,TILE,TILE), 2)
        # detail lines
        pygame.draw.line(s, cols[2], (4,4), (TILE-4, 4), 1)
        pygame.draw.line(s, cols[3], (4,8), (TILE-4, 8), 1)
        pygame.draw.rect(s, cols[3], (2,2,TILE-4,TILE-4), 1)
        
    elif kind == TILE_PLATFORM:
        pygame.draw.rect(s, cols[0], (0,0,TILE,12))
        pygame.draw.rect(s, cols[1], (0,0,TILE,12), 2)
        pygame.draw.line(s, cols[3], (0,2), (TILE,2), 1)
        
    elif kind == TILE_SPIKE:
        for i in range(3):
            x = 8 + i*16
            pygame.draw.polygon(s, (220,80,80),
                [(x,TILE),(x+8,TILE-20),(x+16,TILE)])
            
    elif kind == TILE_BOUNCE:
        s.fill((80,200,120))
        pygame.draw.rect(s, (120,255,160), (0,0,TILE,TILE), 3)
        for i in range(3):
            pygame.draw.line(s, WHITE, (8+i*16,12), (8+i*16,TILE-8), 2)
            
    elif kind == TILE_ICE:
        s.fill((160,220,255))
        pygame.draw.rect(s, (200,240,255), (0,0,TILE,TILE), 2)
        pygame.draw.line(s, WHITE, (4,4), (20,20), 1)
        pygame.draw.line(s, WHITE, (TILE-4,4), (TILE-20,20), 1)
        
    elif kind in (TILE_CONVEYOR_R, TILE_CONVEYOR_L):
        s.fill((160,140,80))
        pygame.draw.rect(s, (200,180,100), (0,0,TILE,TILE), 2)
        arrow = "→" if kind==TILE_CONVEYOR_R else "←"
        font = pygame.font.SysFont(None, 28)
        surf = font.render(arrow, True, WHITE)
        s.blit(surf, (TILE//2 - surf.get_width()//2, TILE//2 - surf.get_height()//2))
        
    elif kind == TILE_LAVA:
        s.fill((200,60,20))
        pygame.draw.rect(s, (255,120,40), (0,0,TILE,TILE), 2)
        
    elif kind == TILE_CHECKPOINT:
        s.fill((0,0,0,0))
        pygame.draw.rect(s, (80,200,255), (TILE//2-4,0,8,TILE), 3)
        pygame.draw.polygon(s, (80,200,255),
            [(TILE//2-4,4),(TILE//2+12,12),(TILE//2-4,20)])
        
    elif kind == TILE_GOAL:
        s.fill((0,0,0,0))
        pygame.draw.circle(s, GOLD, (TILE//2,TILE//2), TILE//2-4, 3)
        pygame.draw.circle(s, CRYSTAL, (TILE//2,TILE//2), TILE//4)
        
    return s


def make_bg_stars(w: int, h: int, count: int = 300) -> list:
    """Return a list of star dicts for the parallax background."""
    stars = []
    for _ in range(count):
        brightness = random.randint(100, 255)
        size = random.choices([1,2,3], weights=[60,30,10])[0]
        stars.append({
            "x": random.uniform(0, w),
            "y": random.uniform(0, h),
            "size": size,
            "brightness": brightness,
            "twinkle_offset": random.uniform(0, math.tau),
            "twinkle_speed": random.uniform(0.02, 0.08),
            "layer": random.choice([0.1, 0.2, 0.4]),  # parallax factor
        })
    return stars


def make_nebula_surf(w: int, h: int, palette: str = "moon") -> pygame.Surface:
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    cols = [
        (100, 50, 200, 25),
        (50, 150, 200, 20),
        (200, 80, 150, 18),
        (80, 200, 150, 15),
    ]
    palette_map = {
        "moon":     [(100,120,200,20),(80,100,180,18)],
        "crystal":  [(80,200,255,22),(60,160,240,18)],
        "nebula":   [(200,100,255,28),(160,60,220,22),(255,120,200,20)],
        "volcanic": [(220,80,30,25),(200,120,20,20)],
        "void":     [(80,0,120,20),(40,0,80,18)],
        "blackhole":[(20,10,40,15),(60,30,80,12)],
    }
    use_cols = palette_map.get(palette, cols)
    
    rng = random.Random(abs(hash(palette)))
    for col in use_cols:
        for _ in range(5):
            cx = rng.randint(0, w)
            cy = rng.randint(0, h)
            rw = rng.randint(w//5, w//2)
            rh = rng.randint(h//5, h//2)
            blob = pygame.Surface((rw*2, rh*2), pygame.SRCALPHA)
            pygame.draw.ellipse(blob, col, (0,0,rw*2,rh*2))
            # feather
            for r in range(3):
                fc = (*col[:3], col[3]//(r+2))
                pygame.draw.ellipse(blob, fc,
                    (-r*10,-r*10,rw*2+r*20,rh*2+r*20))
            s.blit(blob, (cx-rw, cy-rh), special_flags=pygame.BLEND_ALPHA_SDL2)
    return s


def make_planet_surf(radius: int, col: tuple, ring: bool = False) -> pygame.Surface:
    size = radius*2 + 10
    s = pygame.Surface((size + (80 if ring else 0), size + 20), pygame.SRCALPHA)
    cx, cy = size//2 + (40 if ring else 0), size//2 + 10

    # planet body
    pygame.draw.circle(s, col, (cx,cy), radius)
    # highlight
    hl = (min(col[0]+80,255), min(col[1]+80,255), min(col[2]+80,255), 120)
    pygame.draw.ellipse(s, hl, (cx-radius//2, cy-radius//2, radius//2, radius//3))
    # surface details
    rng = random.Random(radius + col[0])
    for _ in range(4):
        dx = rng.randint(-radius//2, radius//2)
        dy = rng.randint(-radius//2, radius//2)
        dr = rng.randint(radius//8, radius//4)
        dc = (max(0,col[0]-30), max(0,col[1]-30), max(0,col[2]-30), 100)
        pygame.draw.circle(s, dc, (cx+dx, cy+dy), dr)
    
    if ring:
        ring_col = (*col[:3], 80)
        pygame.draw.ellipse(s, ring_col, (cx-radius-30, cy-10, (radius+30)*2, 20), 4)
    return s


def make_item_surf(kind: str) -> pygame.Surface:
    s = pygame.Surface((28, 28), pygame.SRCALPHA)
    if kind == "crystal":
        points = [(14,2),(20,10),(14,26),(8,10)]
        pygame.draw.polygon(s, CRYSTAL, points)
        pygame.draw.polygon(s, WHITE, points, 1)
        pygame.draw.polygon(s, (*CYAN,150), [(14,6),(18,12),(14,22),(10,12)])
    elif kind == "health":
        pygame.draw.rect(s, RED, (8,2,12,24))
        pygame.draw.rect(s, RED, (2,8,24,12))
        pygame.draw.rect(s, (255,120,120), (10,4,8,20))
        pygame.draw.rect(s, (255,120,120), (4,10,20,8))
    elif kind == "shield":
        pygame.draw.polygon(s, SHIELD_BLU, [(14,2),(26,8),(26,18),(14,26),(2,18),(2,8)])
        pygame.draw.polygon(s, WHITE, [(14,2),(26,8),(26,18),(14,26),(2,18),(2,8)], 2)
    elif kind == "energy":
        pygame.draw.polygon(s, ENERGY_GRN, [(16,2),(20,14),(14,14),(12,26),(8,14),(14,14)])
        pygame.draw.polygon(s, WHITE, [(16,2),(20,14),(14,14),(12,26),(8,14),(14,14)], 1)
    elif kind == "life":
        pygame.draw.polygon(s, (220,50,50),
            [(14,6),(18,2),(24,4),(26,10),(14,26),(2,10),(4,4),(10,2)])
        pygame.draw.polygon(s, (255,120,120),
            [(14,8),(17,4),(22,6),(24,10),(14,22),(4,10),(6,6),(11,4)])
    elif kind == "upgrade":
        pygame.draw.circle(s, GOLD, (14,14), 12)
        pygame.draw.circle(s, (255,240,100), (14,14), 8)
        pygame.draw.polygon(s, WHITE, [(14,6),(16,12),(22,14),(16,16),(14,22),(12,16),(6,14),(12,12)])
    return s


def make_bullet_surf(owner: str = "player") -> pygame.Surface:
    s = pygame.Surface((16, 8), pygame.SRCALPHA)
    if owner == "player":
        pygame.draw.ellipse(s, PLASMA, (0,1,14,6))
        pygame.draw.ellipse(s, WHITE,  (8,2,6,4))
    else:
        pygame.draw.ellipse(s, (255,80,80),(0,1,14,6))
        pygame.draw.ellipse(s, (255,200,200),(8,2,6,4))
    return s


# ── SOUND SYNTHESIS ──────────────────────────────────────────────
def make_sound(kind: str) -> pygame.mixer.Sound:
    """Generate a sound effect procedurally using numpy if available."""
    try:
        import numpy as np
        rate = 44100
        
        sounds = {
            "jump":   _synth_jump(rate),
            "land":   _synth_land(rate),
            "shoot":  _synth_shoot(rate),
            "hit":    _synth_hit(rate),
            "die":    _synth_die(rate),
            "coin":   _synth_coin(rate),
            "power":  _synth_power(rate),
            "explode":_synth_explode(rate),
            "checkpoint": _synth_checkpoint(rate),
            "boss_hit": _synth_boss_hit(rate),
        }
        data = sounds.get(kind, np.zeros(rate//10, dtype=np.int16))
        return pygame.sndarray.make_sound(
            np.column_stack([data, data]).astype(np.int16))
    except Exception:
        # fallback: silent
        buf = bytes(100)
        return pygame.mixer.Sound(buffer=buf)


def _wave(rate, freq, dur, shape="sine", decay=1.0):
    import numpy as np
    t = np.linspace(0, dur, int(rate*dur))
    if shape == "sine":   w = np.sin(2*np.pi*freq*t)
    elif shape == "square": w = np.sign(np.sin(2*np.pi*freq*t))
    elif shape == "saw":  w = 2*(t*freq - np.floor(t*freq+0.5))
    elif shape == "noise": w = np.random.uniform(-1,1,len(t))
    else: w = np.sin(2*np.pi*freq*t)
    env = np.exp(-decay*t/dur)
    return (w * env * 28000).astype(np.int16)

def _synth_jump(rate):
    import numpy as np
    t = np.linspace(0,0.2,int(rate*0.2))
    freq = 300 + 400*t/0.2
    w = np.sin(2*np.pi*np.cumsum(freq)/rate)
    env = np.exp(-8*t)
    return (w*env*26000).astype(np.int16)

def _synth_land(rate):
    import numpy as np
    t = np.linspace(0,0.1,int(rate*0.1))
    w = np.random.uniform(-1,1,len(t))
    env = np.exp(-20*t)
    return (w*env*20000).astype(np.int16)

def _synth_shoot(rate):
    import numpy as np
    t = np.linspace(0,0.15,int(rate*0.15))
    freq = 600 - 200*t/0.15
    w = np.sin(2*np.pi*np.cumsum(freq)/rate)
    env = np.exp(-12*t)
    return (w*env*24000).astype(np.int16)

def _synth_hit(rate):
    import numpy as np
    t = np.linspace(0,0.12,int(rate*0.12))
    w = np.random.uniform(-1,1,len(t)) * 0.5 + np.sin(2*np.pi*180*t)*0.5
    env = np.exp(-15*t)
    return (w*env*26000).astype(np.int16)

def _synth_die(rate):
    import numpy as np
    t = np.linspace(0,0.6,int(rate*0.6))
    freq = 500 - 400*t/0.6
    w = np.sin(2*np.pi*np.cumsum(freq)/rate)
    env = np.exp(-4*t)
    return (w*env*26000).astype(np.int16)

def _synth_coin(rate):
    import numpy as np
    t = np.linspace(0,0.18,int(rate*0.18))
    w = np.sin(2*np.pi*880*t)*0.5 + np.sin(2*np.pi*1320*t)*0.5
    env = np.exp(-10*t)
    return (w*env*26000).astype(np.int16)

def _synth_power(rate):
    import numpy as np
    t = np.linspace(0,0.5,int(rate*0.5))
    freq = 200 + 600*t/0.5
    w = np.sin(2*np.pi*np.cumsum(freq)/rate)
    env = np.exp(-3*t)
    return (w*env*26000).astype(np.int16)

def _synth_explode(rate):
    import numpy as np
    t = np.linspace(0,0.5,int(rate*0.5))
    w = np.random.uniform(-1,1,len(t))
    env = np.exp(-5*t)
    return (w*env*30000).astype(np.int16)

def _synth_checkpoint(rate):
    import numpy as np
    t = np.linspace(0,0.4,int(rate*0.4))
    w = (np.sin(2*np.pi*523*t) + np.sin(2*np.pi*659*t) + np.sin(2*np.pi*784*t)) / 3
    env = np.exp(-5*t)
    return (w*env*26000).astype(np.int16)

def _synth_boss_hit(rate):
    import numpy as np
    t = np.linspace(0,0.25,int(rate*0.25))
    w = np.random.uniform(-1,1,len(t))*0.4 + np.sin(2*np.pi*120*t)*0.6
    env = np.exp(-8*t)
    return (w*env*30000).astype(np.int16)


# ── MUSIC SYNTHESIS ──────────────────────────────────────────────
def make_music_track(theme: str) -> pygame.mixer.Sound:
    """Generate a simple looping music track for the given theme."""
    try:
        import numpy as np
        rate = 44100
        bpm = 120 if theme not in ("boss","blackhole","void") else 140
        beat = rate * 60 // bpm
        
        theme_notes = {
            "menu":      [261,330,392,523,659,784],
            "moon":      [220,277,330,415,523,415,330,277],
            "crystal":   [293,369,440,587,733,587,440,369],
            "station":   [196,247,294,370,440,370,294,247],
            "asteroid":  [164,207,246,311,392,311,246,207],
            "nebula":    [261,329,392,523,659,523,392,329],
            "blackhole": [123,155,185,233,311,233,185,155],
            "volcanic":  [174,220,261,349,440,349,261,220],
            "void":      [130,164,196,261,329,261,196,164],
            "boss":      [195,245,292,390,490,390,292,245],
            "gameover":  [196,185,175,164,155,146,138,130],
            "win":       [523,659,784,1046,1318,1046,784,659],
        }
        
        notes = theme_notes.get(theme, theme_notes["moon"])
        bars = 4
        total = beat * len(notes) * bars
        track = np.zeros(total, dtype=np.float64)
        
        t_full = np.arange(total) / rate
        
        for bar in range(bars):
            for i, note in enumerate(notes):
                start = (bar * len(notes) + i) * beat
                end   = start + beat
                if end > total: break
                t_seg = np.arange(beat) / rate
                
                # layered synth
                osc  = np.sin(2*np.pi*note*t_seg)
                osc += np.sin(2*np.pi*note*2*t_seg) * 0.3
                osc += np.sin(2*np.pi*note*0.5*t_seg) * 0.5
                
                env_a = np.minimum(np.arange(beat)/(beat*0.05), 1.0)
                env_r = np.exp(-3*t_seg)
                env   = env_a * env_r * 0.4
                
                track[start:end] += osc * env
        
        # bass line
        bass_notes = [n//2 for n in notes]
        for bar in range(bars):
            for i, note in enumerate(bass_notes[::2]):
                start = (bar * len(bass_notes)//2 + i) * beat * 2
                end   = start + beat*2
                if end > total: break
                t_seg = np.arange(beat*2) / rate
                osc = np.sin(2*np.pi*note*t_seg) * 0.3
                env = np.exp(-1.5*t_seg)
                track[start:end] += osc * env
        
        # normalize
        mx = np.max(np.abs(track))
        if mx > 0:
            track = track / mx * 20000
        
        data = track.astype(np.int16)
        stereo = np.column_stack([data, data])
        return pygame.sndarray.make_sound(stereo)
    except Exception:
        buf = bytes(100)
        return pygame.mixer.Sound(buffer=buf)