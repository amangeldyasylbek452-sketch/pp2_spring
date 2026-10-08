"""Particle system for all visual effects."""
import pygame
import random
import math
from constants import *


class Particle:
    __slots__ = ('x','y','vx','vy','life','max_life','size','color','gravity',
                 'fade','shape','spin','spin_speed')
    
    def __init__(self, x, y, vx, vy, life, size, color,
                 gravity=0.1, fade=True, shape="circle", spin=0.0):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = float(vx), float(vy)
        self.life = self.max_life = float(life)
        self.size = float(size)
        self.color = color
        self.gravity = gravity
        self.fade = fade
        self.shape = shape
        self.spin = spin
        self.spin_speed = random.uniform(-0.2, 0.2)
    
    def update(self) -> bool:
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.vx *= 0.98
        self.life -= 1
        self.spin += self.spin_speed
        return self.life > 0
    
    def draw(self, surf: pygame.Surface, cam_x: float, cam_y: float):
        ratio = self.life / self.max_life
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)
        size = max(1, int(self.size * ratio))
        
        if self.fade:
            alpha = int(255 * ratio)
            col = (*self.color[:3], alpha) if len(self.color)==4 else (*self.color, alpha)
        else:
            col = self.color
        
        if size <= 0:
            return
        
        if self.shape == "circle":
            _draw_alpha_circle(surf, col, (sx, sy), size)
        elif self.shape == "square":
            _draw_alpha_rect(surf, col, (sx-size//2, sy-size//2, size, size))
        elif self.shape == "star":
            _draw_star(surf, col, (sx, sy), size, self.spin)
        elif self.shape == "spark":
            ex = sx + int(math.cos(self.spin)*size*2)
            ey = sy + int(math.sin(self.spin)*size*2)
            if 0<=sx<surf.get_width() and 0<=sy<surf.get_height():
                pygame.draw.line(surf, self.color[:3], (sx,sy), (ex,ey),
                                 max(1, size//2))


def _draw_alpha_circle(surf, col, pos, radius):
    if radius < 1: return
    try:
        tmp = pygame.Surface((radius*2+2, radius*2+2), pygame.SRCALPHA)
        pygame.draw.circle(tmp, col, (radius+1, radius+1), radius)
        surf.blit(tmp, (pos[0]-radius-1, pos[1]-radius-1),
                  special_flags=pygame.BLEND_ALPHA_SDL2)
    except Exception:
        pygame.draw.circle(surf, col[:3], pos, radius)


def _draw_alpha_rect(surf, col, rect):
    try:
        tmp = pygame.Surface((max(1,rect[2]), max(1,rect[3])), pygame.SRCALPHA)
        tmp.fill(col)
        surf.blit(tmp, (rect[0], rect[1]),
                  special_flags=pygame.BLEND_ALPHA_SDL2)
    except Exception:
        pygame.draw.rect(surf, col[:3], rect)


def _draw_star(surf, col, pos, size, angle):
    pts = []
    for i in range(10):
        r = size if i%2==0 else size//2
        a = angle + i * math.pi / 5
        pts.append((pos[0]+int(math.cos(a)*r),
                    pos[1]+int(math.sin(a)*r)))
    if len(pts) >= 3:
        try:
            pygame.draw.polygon(surf, col[:3], pts)
        except Exception:
            pass


class ParticleSystem:
    def __init__(self):
        self.particles: list[Particle] = []
    
    def clear(self):
        self.particles.clear()
    
    def update(self):
        self.particles = [p for p in self.particles if p.update()]
    
    def draw(self, surf: pygame.Surface, cam_x: float, cam_y: float):
        for p in self.particles:
            p.draw(surf, cam_x, cam_y)
    
    # ── Emitter helpers ──────────────────────────────────────────
    def burst(self, x, y, color, count=12, speed=4, size=6, gravity=0.2,
              shape="circle", life=30):
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            spd   = random.uniform(speed*0.3, speed)
            self.particles.append(Particle(
                x, y,
                math.cos(angle)*spd, math.sin(angle)*spd,
                random.randint(life//2, life),
                random.uniform(size*0.5, size),
                color, gravity=gravity, shape=shape,
            ))
    
    def dust(self, x, y, dir_x=0):
        for _ in range(4):
            self.particles.append(Particle(
                x + random.uniform(-8,8),
                y,
                dir_x*random.uniform(0.5,1.5) + random.uniform(-1,1),
                random.uniform(-2, -0.5),
                random.randint(12,22),
                random.uniform(3,7),
                (180,180,220),
                gravity=0.05,
            ))
    
    def trail(self, x, y, color, size=4):
        self.particles.append(Particle(
            x + random.uniform(-4,4),
            y + random.uniform(-4,4),
            random.uniform(-0.5,0.5),
            random.uniform(-0.5,0.5),
            random.randint(8,16),
            size,
            color,
            gravity=0.0,
        ))
    
    def sparks(self, x, y, color=(255,220,80), count=8):
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            spd   = random.uniform(2, 6)
            p = Particle(
                x, y,
                math.cos(angle)*spd, math.sin(angle)*spd,
                random.randint(10,20),
                random.uniform(2,4),
                color,
                gravity=0.3,
                shape="spark",
            )
            p.spin = angle
            self.particles.append(p)
    
    def explosion(self, x, y, color=(255,120,40), scale=1.0):
        # Core
        self.burst(x, y, color, count=int(20*scale), speed=int(6*scale),
                   size=int(8*scale), gravity=0.15, life=40)
        # Smoke
        self.burst(x, y, (80,80,100,180), count=int(8*scale),
                   speed=int(3*scale), size=int(14*scale), gravity=-0.05, life=50)
        # Sparks
        self.sparks(x, y, (255,240,80), count=int(12*scale))
        # Shockwave ring
        for i in range(16):
            a = i/16*math.tau
            self.particles.append(Particle(
                x, y,
                math.cos(a)*8*scale, math.sin(a)*8*scale,
                10, 5*scale, (255,200,100), gravity=0.0,
            ))
    
    def stomp_effect(self, x, y):
        self.burst(x, y, (200,220,255), count=8, speed=3,
                   size=5, gravity=0.1, life=20)
        for _ in range(6):
            self.particles.append(Particle(
                x+random.uniform(-12,12), y,
                random.uniform(-2,2), random.uniform(-3,-1),
                15, random.uniform(3,6), (180,200,255), gravity=0.05,
            ))
    
    def crystal_pickup(self, x, y):
        for i in range(20):
            a = i/20*math.tau
            self.particles.append(Particle(
                x, y,
                math.cos(a)*3, math.sin(a)*3,
                25, 5, CRYSTAL, gravity=-0.05,
                shape="star", spin=a,
            ))
    
    def boss_death(self, x, y, w=200, h=200):
        for _ in range(80):
            px = x + random.uniform(-w//2, w//2)
            py = y + random.uniform(-h//2, h//2)
            self.explosion(px, py, scale=0.5)
    
    def portal_particles(self, x, y, color):
        a = random.uniform(0, math.tau)
        r = random.uniform(10, 30)
        self.particles.append(Particle(
            x+math.cos(a)*r, y+math.sin(a)*r,
            -math.cos(a)*1.5, -math.sin(a)*1.5,
            random.randint(20,35),
            random.uniform(2,5),
            color, gravity=0.0,
        ))
    
    def shield_hit(self, x, y):
        for i in range(14):
            a = i/14*math.tau
            self.particles.append(Particle(
                x, y,
                math.cos(a)*5, math.sin(a)*5,
                15, 4, SHIELD_BLU, gravity=0.0,
            ))
    
    def gravity_distortion(self, x, y, radius=60):
        for _ in range(4):
            a = random.uniform(0, math.tau)
            r = random.uniform(radius*0.5, radius)
            self.particles.append(Particle(
                x+math.cos(a)*r, y+math.sin(a)*r,
                -math.cos(a)*2, -math.sin(a)*2,
                random.randint(20,35),
                random.uniform(2,5),
                (150,50,255,180), gravity=0.0,
            ))
    
    def star_fragment_idle(self, x, y):
        """Gentle glow particles around collectibles."""
        if random.random() < 0.3:
            self.particles.append(Particle(
                x+random.uniform(-10,10),
                y+random.uniform(-10,10),
                random.uniform(-0.3,0.3),
                random.uniform(-1,-0.2),
                random.randint(20,35),
                random.uniform(2,4),
                GOLD, gravity=0.0,
            ))