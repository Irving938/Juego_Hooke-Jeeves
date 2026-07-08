import pygame
import math
import sys
import random
import csv
import os
from datetime import datetime
from hooke_jeeves import (HookeJeeves, FUNCTIONS, FUNCTION_INFO,
                          START_RANGE, MAP_DOMAIN, KNOWN_MINIMA)

# =====================================================
# CONFIGURACION INICIAL
# =====================================================
pygame.init()
BASE_W, BASE_H = 1200, 800
W, H = BASE_W, BASE_H
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("The Perfect Blade - Hooke-Jeeves Forge")
clock = pygame.time.Clock()

scale_x, scale_y = 1.0, 1.0
uniform_scale = 1.0

HISTORIAL_CSV = "historial.csv"


def get_fonts():
    return {
        'FONT':       pygame.font.SysFont("arial", int(21 * uniform_scale)),
        'BIG_FONT':   pygame.font.SysFont("arial", int(32 * uniform_scale), bold=True),
        'TITLE_FONT': pygame.font.SysFont("arial", int(52 * uniform_scale), bold=True),
        'HUGE_FONT':  pygame.font.SysFont("arial", int(78 * uniform_scale), bold=True),
        'SMALL_FONT': pygame.font.SysFont("arial", int(16 * uniform_scale)),
        'MONO_FONT':  pygame.font.SysFont("consolas", int(19 * uniform_scale)),
    }

fonts = get_fonts()

# Colores
C = {
    'WHITE': (245, 245, 245), 'BLACK': (18, 16, 20), 'GRAY': (90, 88, 95),
    'LIGHT_GRAY': (185, 182, 190), 'RED': (205, 75, 70), 'GREEN': (70, 185, 100),
    'BLUE': (75, 130, 215), 'ORANGE': (255, 145, 40), 'YELLOW': (255, 215, 70),
    'BROWN': (150, 92, 45), 'DARK_BROWN': (96, 62, 32),
    'GOLD': (222, 182, 70), 'ANVIL_GRAY': (105, 105, 112),
    'LAVA_RED': (255, 70, 10), 'WATER_BLUE': (60, 160, 245),
    'STONE': (66, 62, 70), 'DARK_STONE': (44, 41, 48), 'MORTAR': (32, 30, 36),
    'WALL_DARK': (28, 26, 32), 'PANEL': (24, 22, 30), 'PANEL_BORDER': (105, 92, 72),
    'CYAN': (120, 220, 255), 'DIM': (140, 135, 145),
}


# =====================================================
# SONIDO SINTETIZADO (opcional, requiere numpy)
# =====================================================
class SFX:
    def __init__(self):
        self.ok = False
        self.s = {}
        try:
            import numpy as np
            self.np = np
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.s['hit']    = self._tone([(105, 0.12)], noise=0.55, vol=0.45)
            self.s['sizzle'] = self._tone([(90, 0.28)],  noise=0.9,  vol=0.30)
            self.s['splash'] = self._tone([(240, 0.22)], noise=0.75, vol=0.30)
            self.s['good']   = self._tone([(620, 0.07), (830, 0.10)], vol=0.30)
            self.s['bad']    = self._tone([(220, 0.14)], vol=0.28)
            self.s['sell']   = self._tone([(523, 0.09), (659, 0.09), (784, 0.16)], vol=0.35)
            self.s['fail']   = self._tone([(300, 0.14), (196, 0.26)], vol=0.35)
            self.s['click']  = self._tone([(880, 0.04)], vol=0.20)
            self.ok = True
        except Exception:
            self.ok = False

    def _tone(self, notes, noise=0.0, vol=0.5):
        np = self.np
        sr = 22050
        parts = []
        for f, dur in notes:
            n = max(1, int(sr * dur))
            t = np.arange(n) / sr
            env = np.exp(-t * 14.0)
            w = np.sin(2 * np.pi * f * t)
            if noise > 0:
                w = (1 - noise) * w + noise * (np.random.rand(n) * 2 - 1)
            parts.append(w * env)
        w = np.concatenate(parts)
        a = (w * vol * 32767).astype(np.int16)
        stereo = np.ascontiguousarray(np.column_stack((a, a)))
        return pygame.sndarray.make_sound(stereo)

    def play(self, name):
        if self.ok and name in self.s:
            try:
                self.s[name].play()
            except Exception:
                pass

sfx = SFX()


# =====================================================
# UTILIDADES DE DIBUJO
# =====================================================
def R(x, y, w, h):
    """Rect en coordenadas base escaladas a la ventana actual."""
    return pygame.Rect(int(x * scale_x), int(y * scale_y),
                       int(w * scale_x), int(h * scale_y))


def text(txt, font, color, x, y, center=False):
    img = font.render(txt, True, color)
    r = img.get_rect(center=(int(x), int(y))) if center else img.get_rect(topleft=(int(x), int(y)))
    screen.blit(img, r)
    return r


def draw_panel(rect, alpha=185, title=None, title_color=None):
    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(panel, (*C['PANEL'], alpha), panel.get_rect(), border_radius=10)
    pygame.draw.rect(panel, (255, 255, 255, 14), (2, 2, rect.w - 4, max(3, rect.h // 12)),
                     border_radius=8)
    screen.blit(panel, rect.topleft)
    pygame.draw.rect(screen, C['PANEL_BORDER'], rect, 2, border_radius=10)
    if title:
        text(title, fonts['SMALL_FONT'], title_color or C['GOLD'],
             rect.x + int(14 * scale_x), rect.y + int(8 * scale_y))


def button(rect, txt, color, font, mouse=None, enabled=True):
    hover = enabled and mouse is not None and rect.collidepoint(mouse)
    base = color if enabled else C['GRAY']
    if hover:
        base = tuple(min(255, c + 30) for c in base)
    shadow = rect.move(0, int(3 * scale_y))
    pygame.draw.rect(screen, (10, 10, 14), shadow, border_radius=10)
    pygame.draw.rect(screen, base, rect, border_radius=10)
    pygame.draw.rect(screen, C['WHITE'] if hover else (210, 205, 200),
                     rect, 2, border_radius=10)
    text(txt, font, C['WHITE'] if enabled else (200, 198, 205),
         rect.centerx, rect.centery, center=True)
    return rect


def quality_bar(q, rect, req=None):
    pygame.draw.rect(screen, (48, 46, 54), rect, border_radius=6)
    fill = int(rect.w * max(0, min(100, q)) / 100)
    col = C['GREEN'] if q >= 80 else C['YELLOW'] if q >= 50 else C['RED']
    if fill > 0:
        pygame.draw.rect(screen, col, (rect.x, rect.y, fill, rect.h), border_radius=6)
    if req is not None:
        rx = rect.x + int(rect.w * req / 100)
        pygame.draw.line(screen, C['WHITE'], (rx, rect.y - 4), (rx, rect.bottom + 4), 3)
    pygame.draw.rect(screen, C['WHITE'], rect, 2, border_radius=6)


def draw_brick_background():
    screen.fill(C['WALL_DARK'])
    brick_w = int(64 * scale_x)
    brick_h = int(32 * scale_y)
    for row in range(0, H, brick_h):
        offset = 0 if (row // brick_h) % 2 == 0 else brick_w // 2
        shade = 0.85 + 0.3 * (row / max(1, H))   # se "calienta" hacia abajo
        col = tuple(min(255, int(c * shade)) for c in C['STONE'])
        for colx in range(-brick_w, W + brick_w, brick_w):
            rect = pygame.Rect(colx + offset, row, brick_w - 2, brick_h - 2)
            pygame.draw.rect(screen, col, rect)
            pygame.draw.rect(screen, C['MORTAR'], rect, 1)
    # resplandor calido en la parte baja (como si el horno iluminara el taller)
    glow = pygame.Surface((W, H // 3), pygame.SRCALPHA)
    for i in range(glow.get_height()):
        a = int(38 * i / glow.get_height())
        pygame.draw.line(glow, (255, 110, 20, a), (0, i), (W, i))
    screen.blit(glow, (0, H - glow.get_height()))


# =====================================================
# PARTICULAS
# =====================================================
sparks = []   # chispas del yunque
embers = []   # brasas ambientales


def spawn_sparks(x, y, n=18, colors=None):
    colors = colors or [C['YELLOW'], C['ORANGE'], C['WHITE']]
    for _ in range(n):
        ang = random.uniform(-math.pi, 0)
        spd = random.uniform(2, 7) * uniform_scale
        sparks.append({
            'x': x, 'y': y,
            'vx': math.cos(ang) * spd, 'vy': math.sin(ang) * spd,
            'life': random.randint(15, 32),
            'col': random.choice(colors),
        })


def update_sparks():
    for p in sparks[:]:
        p['x'] += p['vx']
        p['y'] += p['vy']
        p['vy'] += 0.3 * uniform_scale
        p['life'] -= 1
        if p['life'] <= 0:
            sparks.remove(p)
        else:
            r = max(1, int(p['life'] / 10))
            pygame.draw.circle(screen, p['col'], (int(p['x']), int(p['y'])), r)


def update_embers():
    if len(embers) < 40 and random.random() < 0.35:
        embers.append({
            'x': random.uniform(0, W), 'y': H + 10,
            'vy': -random.uniform(0.5, 1.6) * uniform_scale,
            'drift': random.uniform(-0.4, 0.4),
            'col': random.choice([C['ORANGE'], C['LAVA_RED'], C['YELLOW']]),
            'r': random.randint(1, 3),
        })
    for p in embers[:]:
        p['y'] += p['vy']
        p['x'] += p['drift'] + math.sin(p['y'] * 0.02) * 0.5
        if p['y'] < -10:
            embers.remove(p)
        else:
            pygame.draw.circle(screen, p['col'], (int(p['x']), int(p['y'])), p['r'])


# =====================================================
# MAPA DE CONTORNO DE LA FUNCION
# =====================================================
_contour_cache = {}

_PALETTE = [
    (0.00, (255, 236, 150)),   # cerca del minimo: brillo dorado
    (0.25, (238, 148, 60)),
    (0.55, (150, 62, 92)),
    (0.80, (62, 44, 84)),
    (1.00, (22, 22, 40)),      # valores altos: oscuro
]


def _palette(t):
    t = max(0.0, min(1.0, t))
    for i in range(len(_PALETTE) - 1):
        t0, c0 = _PALETTE[i]
        t1, c1 = _PALETTE[i + 1]
        if t <= t1:
            k = (t - t0) / (t1 - t0 + 1e-9)
            return tuple(int(c0[j] + (c1[j] - c0[j]) * k) for j in range(3))
    return _PALETTE[-1][1]


def get_contour(func_name, size):
    key = (func_name, size)
    if key in _contour_cache:
        return _contour_cache[key]
    func = FUNCTIONS[func_name]
    d = MAP_DOMAIN[func_name]
    n = 90
    vals = []
    vmin, vmax = float('inf'), float('-inf')
    for j in range(n):
        row = []
        y = d - 2 * d * j / (n - 1)
        for i in range(n):
            x = -d + 2 * d * i / (n - 1)
            v = math.log1p(max(0.0, func(x, y)))
            row.append(v)
            vmin, vmax = min(vmin, v), max(vmax, v)
        vals.append(row)
    small = pygame.Surface((n, n))
    for j in range(n):
        for i in range(n):
            t = (vals[j][i] - vmin) / (vmax - vmin + 1e-9)
            small.set_at((i, j), _palette(t))
    surf = pygame.transform.smoothscale(small, (size, size))
    _contour_cache[key] = surf
    return surf


def _w2m(x, y, rect, d):
    """Convierte coordenadas del mundo (x,y) a pixeles del mapa (clampeado)."""
    px = rect.x + (x + d) / (2 * d) * rect.w
    py = rect.y + (d - y) / (2 * d) * rect.h
    px = max(rect.x + 2, min(rect.right - 2, px))
    py = max(rect.y + 2, min(rect.bottom - 2, py))
    return int(px), int(py)


def draw_map(g, rect, tick):
    d = MAP_DOMAIN[g.func_name]
    size = min(rect.w, rect.h)
    rect = pygame.Rect(rect.x, rect.y, size, size)
    screen.blit(get_contour(g.func_name, size), rect.topleft)

    # Ejes x=0, y=0
    ax = pygame.Surface(rect.size, pygame.SRCALPHA)
    cx, cy = rect.w // 2, rect.h // 2
    pygame.draw.line(ax, (255, 255, 255, 45), (cx, 0), (cx, rect.h))
    pygame.draw.line(ax, (255, 255, 255, 45), (0, cy), (rect.w, cy))
    screen.blit(ax, rect.topleft)

    # Minimos conocidos
    for mx, my in KNOWN_MINIMA[g.func_name]:
        px, py = _w2m(mx, my, rect, d)
        s = int(5 * uniform_scale)
        pygame.draw.line(screen, (30, 30, 30), (px - s, py), (px + s, py), 2)
        pygame.draw.line(screen, (30, 30, 30), (px, py - s), (px, py + s), 2)

    opt = g.opt
    # Trayectoria de puntos aceptados
    pts = [_w2m(x, y, rect, d) for (x, y, _) in opt.history]
    if len(pts) > 1:
        pygame.draw.lines(screen, C['CYAN'], False, pts, 2)
    for p in pts[:-1]:
        pygame.draw.circle(screen, C['CYAN'], p, max(2, int(3 * uniform_scale)))
    # Punto inicial
    pygame.draw.circle(screen, C['WHITE'], pts[0], max(3, int(4 * uniform_scale)), 2)

    # Cuadrado de exploracion (alcance de delta) y candidatos
    bx, by = opt.bx, opt.by
    half = opt.delta / (2 * d) * rect.w
    bpx, bpy = _w2m(bx, by, rect, d)
    box = pygame.Surface((int(half * 2) + 4, int(half * 2) + 4), pygame.SRCALPHA)
    pygame.draw.rect(box, (255, 255, 255, 70), box.get_rect(), 1)
    screen.blit(box, (bpx - half - 2, bpy - half - 2))

    dirs = {"temp+": (opt.delta, 0), "temp-": (-opt.delta, 0),
            "cool+": (0, opt.delta), "cool-": (0, -opt.delta)}
    for key, (dx, dy) in dirs.items():
        px, py = _w2m(bx + dx, by + dy, rect, d)
        if opt.explored[key]:
            pygame.draw.circle(screen, (150, 150, 160), (px, py), max(2, int(3 * uniform_scale)))
        else:
            r = max(3, int(4 * uniform_scale)) + (1 if tick % 20 < 10 else 0)
            pygame.draw.circle(screen, C['YELLOW'], (px, py), r, 2)

    # Mejor punto actual (pulsante)
    pulse = 2 + int(2 * abs(math.sin(tick * 0.15)))
    pygame.draw.circle(screen, C['WHITE'], (bpx, bpy), max(4, int(5 * uniform_scale)))
    pygame.draw.circle(screen, C['GREEN'], (bpx, bpy),
                       max(6, int(7 * uniform_scale)) + pulse, 2)

    pygame.draw.rect(screen, C['PANEL_BORDER'], rect, 2, border_radius=2)
    text(f"dominio [{-d:g}, {d:g}]  |  + = minimo conocido",
         fonts['SMALL_FONT'], C['DIM'], rect.x, rect.bottom + int(6 * scale_y))
    return rect


# =====================================================
# OBJETOS DE LA FORJA (horno, yunque, espada, martillo)
# =====================================================
def furnace(rect, tick):
    size = min(rect.w, rect.h)
    x, y = rect.x, rect.y
    sc = size / 120.0
    # resplandor
    glow = pygame.Surface((int(size * 1.6), int(size * 1.6)), pygame.SRCALPHA)
    for r in range(int(size * 0.7), 0, -max(2, int(size * 0.06))):
        alpha = max(0, 32 - r // 5)
        pygame.draw.circle(glow, (255, 100, 0, alpha),
                           (int(size * 0.8), int(size * 0.8)), r)
    screen.blit(glow, (x - int(size * 0.3), y - int(size * 0.3)))

    border = pygame.Rect(int(x), int(y), int(size), int(size))
    pygame.draw.rect(screen, C['DARK_STONE'], border, max(2, int(4 * sc)))
    mouth = pygame.Rect(int(x + 20 * sc), int(y + 55 * sc), int(80 * sc), int(55 * sc))
    pygame.draw.rect(screen, C['BLACK'], mouth)
    pygame.draw.rect(screen, C['DARK_STONE'], mouth, max(2, int(3 * sc)))
    fcol = [C['ORANGE'], C['YELLOW'], (255, 100, 0)]
    bfh = int(35 * sc)
    heights = [bfh + (tick * 3) % max(2, int(6 * sc)),
               bfh + ((tick + 2) * 3) % max(2, int(8 * sc)),
               bfh + ((tick + 4) * 3) % max(2, int(5 * sc))]
    flame_xs = [mouth.x + mouth.w // 4, mouth.x + mouth.w // 2, mouth.x + 3 * mouth.w // 4]
    for i, fx in enumerate(flame_xs):
        fh = heights[i]
        pygame.draw.ellipse(screen, fcol[i % 3],
                            (fx - int(12 * sc), mouth.y - fh // 2, int(24 * sc), fh))
        pygame.draw.ellipse(screen, C['YELLOW'],
                            (fx - int(8 * sc), mouth.y - fh // 3, int(16 * sc), int(fh / 1.5)))
        for _ in range(max(1, int(3 * sc))):
            px = fx + random.randint(-int(8 * sc), int(8 * sc))
            py = mouth.y - random.randint(int(10 * sc), fh + int(5 * sc))
            pygame.draw.rect(screen, random.choice(fcol), (px, py, int(4 * sc), int(4 * sc)))
    chim = pygame.Rect(int(x + (size - 40 * sc) / 2), int(y - 30 * sc),
                       int(40 * sc), int(30 * sc))
    pygame.draw.rect(screen, C['DARK_STONE'], chim)
    pygame.draw.rect(screen, C['MORTAR'], chim, 2)
    if tick % 2 == 0:
        for s in range(3):
            pygame.draw.circle(screen, (140, 138, 145, 90),
                               (chim.centerx + (s - 1) * int(15 * sc), chim.y - (tick % 30) * 2),
                               int(7 * sc))


def anvil(x, y):
    pygame.draw.rect(screen, C['ANVIL_GRAY'],
                     (int(x - 90 * uniform_scale), int(y + 20 * uniform_scale),
                      int(180 * uniform_scale), int(25 * uniform_scale)), border_radius=8)
    pts = [(int(x - 60 * uniform_scale), int(y + 20 * uniform_scale)),
           (int(x + 60 * uniform_scale), int(y + 20 * uniform_scale)),
           (int(x + 30 * uniform_scale), int(y - 20 * uniform_scale)),
           (int(x - 30 * uniform_scale), int(y - 20 * uniform_scale))]
    pygame.draw.polygon(screen, C['ANVIL_GRAY'], pts)
    pygame.draw.rect(screen, C['DARK_BROWN'],
                     (int(x - 70 * uniform_scale), int(y - 25 * uniform_scale),
                      int(140 * uniform_scale), int(15 * uniform_scale)), border_radius=4)


def sword(q, gx, gy, shake=0):
    u = uniform_scale
    gx += random.randint(-shake, shake)
    gy += random.randint(-shake, shake)
    if q < 30:   bc, gl = (128, 128, 128), 0
    elif q < 50: bc, gl = (100, 100, 255), 50
    elif q < 70: bc, gl = (50, 200, 50), 100
    elif q < 90: bc, gl = (255, 255, 0), 180
    else:        bc, gl = (255, 255, 255), 255
    if gl:
        s = pygame.Surface((int(200 * u), int(100 * u)), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (*bc, min(gl, 80)),
                            (int(10 * u), int(20 * u), int(180 * u), int(40 * u)))
        screen.blit(s, (gx + int(10 * u), gy - int(30 * u)))
    tip = gx + int(190 * u)
    pts = [(gx, gy - int(9 * u)), (tip - int(20 * u), gy - int(13 * u)), (tip, gy),
           (tip - int(20 * u), gy + int(13 * u)), (gx, gy + int(9 * u))]
    pygame.draw.polygon(screen, bc, pts)
    pygame.draw.polygon(screen, C['BLACK'], pts, 2)
    pygame.draw.line(screen, C['BLACK'], (gx, gy), (tip - int(25 * u), gy), 2)
    gr = pygame.Rect(gx - int(4 * u), gy - int(15 * u), int(8 * u), int(30 * u))
    pygame.draw.rect(screen, C['YELLOW'], gr, border_radius=3)
    pygame.draw.rect(screen, C['BLACK'], gr, 2, border_radius=3)
    hr = pygame.Rect(gx - int(90 * u), gy - int(6 * u), int(90 * u), int(12 * u))
    pygame.draw.rect(screen, C['BROWN'], hr, border_radius=4)
    pygame.draw.rect(screen, C['BLACK'], hr, 2, border_radius=4)
    pygame.draw.circle(screen, C['GOLD'], (int(gx - 98 * u), int(gy)), int(12 * u))
    pygame.draw.circle(screen, C['BLACK'], (int(gx - 98 * u), int(gy)), int(12 * u), 2)


def hammer_swing(frame, maxf, ix, iy):
    if frame <= 0:
        return
    u = uniform_scale
    p = frame / maxf
    px, py = ix - 80 * u, iy - 120 * u
    al = 110 * u
    if p < 0.3:
        ang = -math.pi / 4 * (p / 0.3)
    elif p < 0.7:
        t = (p - 0.3) / 0.4
        ang = -math.pi / 4 * (1 - t) + math.pi / 6 * t
    else:
        t = (p - 0.7) / 0.3
        ang = math.pi / 6 * (1 - t)
    hx = px + al * math.cos(ang)
    hy = py + al * math.sin(ang)
    head_w, head_h = int(90 * u), int(52 * u)
    hs = pygame.Surface((head_w, head_h), pygame.SRCALPHA)
    pygame.draw.rect(hs, C['GRAY'], (0, 0, head_w, head_h), border_radius=6)
    pygame.draw.rect(hs, C['BLACK'], (0, 0, head_w, head_h), 3, border_radius=6)
    pygame.draw.rect(hs, C['DARK_BROWN'],
                     (int(6 * u), int(4 * u), int(head_w - 12 * u), int(6 * u)), border_radius=3)
    rh = pygame.transform.rotate(hs, math.degrees(-ang))
    screen.blit(rh, rh.get_rect(center=(hx, hy)))
    dx, dy = hx - px, hy - py
    dist = math.hypot(dx, dy)
    ad = math.degrees(math.atan2(dy, dx))
    handle_w = int(14 * u)
    hl = dist - head_h / 2 - 4
    if hl > 10:
        hnd = pygame.Surface((handle_w, int(hl)), pygame.SRCALPHA)
        pygame.draw.rect(hnd, C['BROWN'], (0, 0, handle_w, int(hl)), border_radius=5)
        pygame.draw.rect(hnd, C['BLACK'], (0, 0, handle_w, int(hl)), 2, border_radius=5)
        rhn = pygame.transform.rotate(hnd, -ad + 90)
        mx = px + (dx * (hl / 2 + head_h / 2)) / dist
        my = py + (dy * (hl / 2 + head_h / 2)) / dist
        screen.blit(rhn, rhn.get_rect(center=(mx, my)))
    if 0.45 < p < 0.75:
        for _ in range(14):
            sx = ix + random.randint(-20, 20)
            sy = iy + random.randint(-8, 8)
            pygame.draw.circle(screen, random.choice([C['YELLOW'], C['ORANGE'], C['WHITE']]),
                               (int(sx), int(sy)), random.randint(2, 5))


def bucket(frame, maxf, px, py, is_lava):
    if frame <= 0:
        return
    u = uniform_scale
    p = frame / maxf
    tilt = 30 * (1 - p)
    bs = pygame.Surface((int(40 * u), int(30 * u)), pygame.SRCALPHA)
    col = C['GRAY'] if is_lava else C['LIGHT_GRAY']
    pygame.draw.rect(bs, col, (0, 0, int(40 * u), int(30 * u)))
    pygame.draw.rect(bs, C['BLACK'], (0, 0, int(40 * u), int(30 * u)), 2)
    pygame.draw.arc(bs, C['BLACK'],
                    (int(10 * u), int(-15 * u), int(20 * u), int(20 * u)),
                    math.pi, 2 * math.pi, 3)
    rb = pygame.transform.rotate(bs, -tilt)
    screen.blit(rb, (px - int(15 * u), py - int(50 * u)))
    if p > 0.1:
        sl = int(30 * u + 10 * p)
        lc = C['LAVA_RED'] if is_lava else C['WATER_BLUE']
        dc = C['ORANGE'] if is_lava else C['BLUE']
        for i in range(3):
            sx = px - int(8 * u) + i * int(8 * u)
            sy = py - int(20 * u)
            pygame.draw.line(screen, lc, (sx, sy), (sx + random.randint(-4, 4), sy + sl), 4)
        for _ in range(5):
            dx = px + random.randint(-15, 15)
            dy = py + random.randint(0, 20)
            pygame.draw.circle(screen, dc, (int(dx), int(dy)), 3)


# =====================================================
# LOGICA DEL JUEGO
# =====================================================
IMPACT_BASE = (250, 655)   # punto de impacto sobre el yunque (coords base)


def impact_pos():
    return int(IMPACT_BASE[0] * scale_x), int(IMPACT_BASE[1] * scale_y)


class ForgeGame:
    def __init__(self, func_name="sphere"):
        self.func_name = func_name
        self.gold = 0
        self.lingotes = 20
        self.lingote_price = 5
        self.lingote_price_inc = 2
        self.d_upgrade = 0
        self.level = 1
        self.total_vendidas = 0
        self.forge_res = None
        self.fmsg = ""
        self.req, self.reward = 0, 0
        self.shake = 0
        self.hammer_anim = 0
        self.lava_anim = 0
        self.water_anim = 0
        self.max_h, self.max_b = 20, 30
        self.lingotes_gastados = 0
        self.next_customer()

    def next_customer(self):
        r = START_RANGE[self.func_name]
        delta = 2.0 + self.d_upgrade * 0.5
        self.req = min(95, 55 + self.level * 7 + random.randint(-4, 4))
        # Resamplear el punto inicial si ya nace casi cumpliendo el pedido
        for _ in range(60):
            x0 = random.uniform(-r, r)
            y0 = random.uniform(-r, r)
            self.opt = HookeJeeves(x0, y0, delta, func_name=self.func_name)
            if self.opt.quality(self.opt.best_value) < self.req - 20:
                break
        self.reward = 90 + self.level * 45 + random.randint(-15, 15)
        self.lingotes_gastados = 0
        self.forge_res = "forjando"
        self.opt.message = f"Nivel {self.level}: forja la espada!"
        self.level += 1

    # ------------- economia -------------
    def auto_buy_lingotes(self):
        if self.lingotes >= 20:
            return True
        max_comprar = 20 - self.lingotes
        cantidad = self.gold // self.lingote_price
        if cantidad == 0:
            return False
        cantidad = min(cantidad, max_comprar)
        costo = cantidad * self.lingote_price
        self.gold -= costo
        self.lingotes += cantidad
        self.lingote_price += self.lingote_price_inc
        self.opt.message = f"Compraste {cantidad} lingote(s) por {costo} oro."
        return True

    def buy_lingotes(self, n=5):
        costo = n * self.lingote_price
        if self.gold >= costo:
            self.gold -= costo
            self.lingotes += n
            self.lingote_price += self.lingote_price_inc
            sfx.play('sell')
            return True
        sfx.play('bad')
        return False

    def use_lingote(self):
        if self.lingotes > 0:
            self.lingotes -= 1
            self.lingotes_gastados += 1
            return True
        return False

    def check_game_over(self):
        if self.lingotes == 0 and self.gold < self.lingote_price:
            self.forge_res = "game_over"
            self.fmsg = "Sin lingotes ni oro para comprarlos."
            self.save_row("GAME OVER")
            sfx.play('fail')
            return True
        return False

    # ------------- acciones del algoritmo -------------
    def explore(self, dx, dy):
        if self.forge_res == "game_over":
            return
        if self.lingotes == 0 and not self.auto_buy_lingotes():
            self.check_game_over()
            return
        if not self.use_lingote():
            self.opt.message = "Sin lingotes!"
            return
        if dx != 0:
            self.hammer_anim = self.max_h
            sfx.play('hit')
        elif dy > 0:
            self.water_anim = self.max_b
            sfx.play('splash')
        else:
            self.lava_anim = self.max_b
            sfx.play('sizzle')
        improved = self.opt.explore_direction(dx, dy)
        if improved:
            self.shake = 5
            sfx.play('good')
            spawn_sparks(*impact_pos(), n=22)

    def pattern(self):
        if self.forge_res == "game_over":
            return
        if not self.opt.all_explored():
            self.opt.message = "Explora las 4 direcciones primero."
            sfx.play('bad')
            return
        if not self.opt.exploration_success:
            self.opt.message = "Ninguna direccion mejoro. Reduce delta."
            sfx.play('bad')
            return
        if self.lingotes == 0 and not self.auto_buy_lingotes():
            self.check_game_over()
            return
        if not self.use_lingote():
            self.opt.message = "Sin lingotes!"
            return
        self.hammer_anim = self.max_h
        sfx.play('hit')
        improved = self.opt.pattern_move()
        if improved:
            self.shake = 5
            sfx.play('good')
            spawn_sparks(*impact_pos(), n=30)

    def reduce_delta(self):
        if self.forge_res == "game_over":
            return False
        sfx.play('click')
        stopped = self.opt.reduce_delta()
        if stopped:
            self.finish_forge()
        return stopped

    def finish_forge(self):
        q = self.opt.quality(self.opt.best_value)
        if q >= self.req:
            self.forge_res = "exito"
            self.gold += self.reward
            self.lingotes += 3   # el cliente regala material extra
            self.total_vendidas += 1
            self.fmsg = f"Vendida por {self.reward} monedas (+3 lingotes de regalo)."
            self.save_row("VENDIDA")
            sfx.play('sell')
        else:
            self.forge_res = "fracaso"
            self.fmsg = f"Calidad {q:.1f}, se necesitaba {self.req}."
            self.save_row("RECHAZADA")
            sfx.play('fail')

    # ------------- persistencia -------------
    def save_row(self, resultado):
        nueva = not os.path.exists(HISTORIAL_CSV)
        with open(HISTORIAL_CSV, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if nueva:
                w.writerow(["fecha", "funcion", "nivel", "resultado",
                            "f_final", "calidad", "oro", "evaluaciones"])
            w.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                self.func_name,
                self.level - 1,
                resultado,
                f"{self.opt.best_value:.4f}",
                f"{self.opt.quality(self.opt.best_value):.1f}",
                self.gold,
                self.opt.evaluations,
            ])

    def show_history(self):
        try:
            with open(HISTORIAL_CSV, "r", encoding="utf-8") as f:
                rows = [line.strip().split(",") for line in f if line.strip()]
            if rows and rows[0] and rows[0][0] == "fecha":
                rows = rows[1:]
            return rows
        except FileNotFoundError:
            return []

    def update_anim(self):
        if self.hammer_anim > 0: self.hammer_anim -= 1
        if self.lava_anim > 0:   self.lava_anim -= 1
        if self.water_anim > 0:  self.water_anim -= 1
        if self.shake > 0:       self.shake -= 1


# =====================================================
# LAYOUTS (rects compartidos entre dibujo y clics)
# =====================================================
def forge_rects():
    return {
        'header':   R(20, 12, 1160, 52),
        'furnace':  R(30, 85, 260, 250),
        'cliente':  R(25, 355, 270, 145),
        'map':      R(320, 85, 380, 380),
        'estado':   R(320, 495, 380, 140),
        'bar':      R(320, 668, 380, 26),
        'temp+':    R(730, 85, 218, 54),
        'temp-':    R(962, 85, 218, 54),
        'cool+':    R(730, 152, 218, 54),
        'cool-':    R(962, 152, 218, 54),
        'pattern':  R(730, 219, 450, 54),
        'reduce':   R(730, 286, 450, 54),
        'finish':   R(730, 353, 450, 54),
        'shop':     R(730, 420, 450, 44),
        'explor':   R(730, 478, 450, 128),
        'recursos': R(730, 620, 450, 96),
    }


def menu_rects():
    cards = {}
    names = list(FUNCTIONS.keys())
    for i, name in enumerate(names):
        cards[name] = R(70 + i * 272, 300, 250, 190)
    return {
        'cards':    cards,
        'play':     R(BASE_W / 2 - 160, 550, 320, 62),
        'tutorial': R(BASE_W / 2 - 160, 632, 320, 50),
    }


def shop_rects():
    return {
        'panel':   R(280, 170, 640, 420),
        'hammer':  R(340, 320, 520, 56),
        'lingote': R(340, 396, 520, 56),
        'back':    R(480, 500, 240, 54),
    }


def result_rects(game_over=False):
    if game_over:
        return {'panel': R(100, 50, 1000, 700),
                'retry': R(380, 690, 200, 50),
                'quit':  R(620, 690, 200, 50)}
    return {'panel': R(300, 200, 600, 340),
            'next':  R(450, 460, 300, 56)}


# =====================================================
# ESCENAS
# =====================================================
def draw_menu(selected, mouse, tick):
    draw_brick_background()
    update_embers()
    rects = menu_rects()

    # Titulo con sombra y brillo pulsante
    tx, ty = W // 2, int(H * 0.14)
    off = int(4 * uniform_scale)
    text("THE PERFECT BLADE", fonts['HUGE_FONT'], (0, 0, 0), tx + off, ty + off, center=True)
    glow = 200 + int(55 * abs(math.sin(tick * 0.04)))
    text("THE PERFECT BLADE", fonts['HUGE_FONT'], (glow, int(glow * 0.82), 60), tx, ty, center=True)
    text("Forja la espada perfecta con el algoritmo de Hooke-Jeeves",
         fonts['BIG_FONT'], C['LIGHT_GRAY'], tx, int(H * 0.24), center=True)
    text("Elige la funcion objetivo:", fonts['FONT'], C['WHITE'],
         tx, int(H * 0.33), center=True)

    for name, rect in rects['cards'].items():
        sel = (name == selected)
        hover = rect.collidepoint(mouse)
        draw_panel(rect, alpha=210)
        prev_size = int(rect.w * 0.62)
        prev = get_contour(name, prev_size)
        px = rect.centerx - prev_size // 2
        py = rect.y + int(12 * scale_y)
        screen.blit(prev, (px, py))
        pygame.draw.rect(screen, C['PANEL_BORDER'], (px, py, prev_size, prev_size), 1)
        nice, diff = FUNCTION_INFO[name]
        text(nice, fonts['FONT'], C['WHITE'], rect.centerx,
             py + prev_size + int(16 * scale_y), center=True)
        dcol = {'Facil': C['GREEN'], 'Media': C['YELLOW'],
                'Dificil': C['ORANGE'], 'Experto': C['RED']}[diff]
        text(diff, fonts['SMALL_FONT'], dcol, rect.centerx,
             py + prev_size + int(38 * scale_y), center=True)
        border = C['GOLD'] if sel else (C['WHITE'] if hover else C['PANEL_BORDER'])
        pygame.draw.rect(screen, border, rect, 3 if sel else 2, border_radius=10)

    button(rects['play'], "JUGAR", C['GREEN'], fonts['BIG_FONT'], mouse)
    button(rects['tutorial'], "Tutorial", C['BLUE'], fonts['FONT'], mouse)
    text("F11: pantalla completa", fonts['SMALL_FONT'], C['DIM'],
         W // 2, H - int(24 * scale_y), center=True)
    return rects


def draw_tutorial(mouse):
    draw_brick_background()
    text("TUTORIAL", fonts['TITLE_FONT'], C['YELLOW'], W // 2, int(H * 0.07), center=True)

    lines = [
        "Hooke-Jeeves es un metodo de optimizacion directa (sin derivadas).",
        "Busca el minimo de f(x, y) alternando dos fases:",
        "",
        "1) EXPLORACION: prueba los 4 vecinos del punto base a distancia delta.",
        "   Temp +/- mueve en x (martillazo)  |  Enfriar +/- mueve en y (lava/agua).",
        "2) PATRON ('Repetir tecnica'): si la exploracion mejoro, repite el ultimo",
        "   movimiento exitoso para avanzar mas rapido. Luego se explora de nuevo.",
        "3) REDUCIR DELTA: si nada mejora, el paso se corta a la mitad.",
        "   Cuando delta < epsilon el algoritmo termina y la espada se entrega.",
        "",
        "El MAPA muestra el paisaje de la funcion: las zonas doradas son valores",
        "bajos (buena calidad). La linea celeste es tu trayectoria, el cuadrado",
        "blanco es el alcance de delta y las cruces son los minimos conocidos.",
        "",
        "ECONOMIA: cada accion consume 1 lingote. Sin lingotes, se compran solos",
        "con tu oro (el precio sube en cada compra). Sin oro ni lingotes: Game Over.",
        "Vende espadas con calidad >= requerida para ganar oro y lingotes extra.",
        "En la TIENDA (T o clic derecho) mejoras el martillo (delta inicial mayor).",
        "",
        "ATAJOS: flechas = explorar | ESPACIO = patron | R = reducir delta |",
        "ENTER = terminar | T = tienda | F11 = pantalla completa",
    ]

    panel = R(90, 105, 1020, 590)
    draw_panel(panel, alpha=215)
    y = panel.y + int(22 * scale_y)
    for line in lines:
        if line == "":
            y += int(10 * scale_y)
            continue
        text(line, fonts['FONT'], C['WHITE'], panel.x + int(24 * scale_x), y)
        y += int(25 * scale_y)

    back = R(BASE_W / 2 - 110, 720, 220, 52)
    button(back, "Volver", C['GRAY'], fonts['FONT'], mouse)
    return back


def draw_forge(g, mouse, tick):
    draw_brick_background()
    rects = forge_rects()

    # Header
    draw_panel(rects['header'], alpha=200)
    text("THE PERFECT BLADE", fonts['FONT'], C['GOLD'],
         rects['header'].x + int(16 * scale_x), rects['header'].centery - int(11 * scale_y))
    nice, _ = FUNCTION_INFO[g.func_name]
    text(f"[{nice}]", fonts['SMALL_FONT'], C['DIM'],
         rects['header'].x + int(16 * scale_x), rects['header'].centery + int(11 * scale_y))
    text(g.opt.message, fonts['FONT'], C['ORANGE'],
         rects['header'].centerx + int(40 * scale_x), rects['header'].centery, center=True)

    # Horno
    furnace(rects['furnace'], tick)

    # Panel cliente
    draw_panel(rects['cliente'], title="PEDIDO DEL CLIENTE")
    cx = rects['cliente'].x + int(16 * scale_x)
    cy = rects['cliente'].y + int(34 * scale_y)
    text(f"Nivel {g.level - 1}", fonts['BIG_FONT'], C['YELLOW'], cx, cy)
    text(f"Calidad requerida: {g.req}", fonts['FONT'], C['WHITE'], cx, cy + int(42 * scale_y))
    text(f"Recompensa: {g.reward} oro", fonts['FONT'], C['GOLD'], cx, cy + int(68 * scale_y))

    # Mapa
    map_rect = draw_map(g, rects['map'], tick)
    text("MAPA DE LA FUNCION", fonts['SMALL_FONT'], C['GOLD'],
         map_rect.x, map_rect.y - int(22 * scale_y))

    # Estado del algoritmo
    draw_panel(rects['estado'], title="ESTADO DEL ALGORITMO")
    ex = rects['estado'].x + int(16 * scale_x)
    ey = rects['estado'].y + int(32 * scale_y)
    lh = int(25 * scale_y)
    text(f"x = {g.opt.bx: .4f}   y = {g.opt.by: .4f}", fonts['MONO_FONT'], C['WHITE'], ex, ey)
    text(f"f(x,y) = {g.opt.best_value: .5f}", fonts['MONO_FONT'], C['CYAN'], ex, ey + lh)
    text(f"delta  = {g.opt.delta: .4f}   (epsilon = {g.opt.epsilon:.2f})",
         fonts['MONO_FONT'], C['WHITE'], ex, ey + 2 * lh)
    text(f"evaluaciones de f: {g.opt.evaluations}", fonts['MONO_FONT'], C['DIM'], ex, ey + 3 * lh)

    # Barra de calidad
    q = g.opt.quality(g.opt.best_value)
    text(f"CALIDAD: {q:.1f} / requerida {g.req}", fonts['FONT'],
         C['GREEN'] if q >= g.req else C['WHITE'],
         rects['bar'].x, rects['bar'].y - int(26 * scale_y))
    quality_bar(q, rects['bar'], req=g.req)

    # Botones
    hj = g.opt
    pattern_on = hj.all_explored() and hj.exploration_success
    button(rects['temp+'], "Temp +  (→)", C['BLUE'], fonts['FONT'], mouse,
           enabled=not hj.explored['temp+'])
    button(rects['temp-'], "Temp -  (←)", C['BLUE'], fonts['FONT'], mouse,
           enabled=not hj.explored['temp-'])
    button(rects['cool+'], "Enfriar +  (↑)", C['WATER_BLUE'], fonts['FONT'], mouse,
           enabled=not hj.explored['cool+'])
    button(rects['cool-'], "Enfriar -  (↓)", C['WATER_BLUE'], fonts['FONT'], mouse,
           enabled=not hj.explored['cool-'])
    button(rects['pattern'], "Repetir tecnica (ESPACIO)", C['GREEN'], fonts['FONT'],
           mouse, enabled=pattern_on)
    button(rects['reduce'], "Reducir delta (R)", C['RED'], fonts['FONT'], mouse)
    button(rects['finish'], "Terminar y entregar (ENTER)", C['BROWN'], fonts['FONT'], mouse)
    button(rects['shop'], "Tienda del herrero (T)", C['GRAY'], fonts['SMALL_FONT'], mouse)

    # Exploracion
    draw_panel(rects['explor'], title="EXPLORACION DE ESTA RONDA")
    labels = [("temp+", "Temp +"), ("temp-", "Temp -"),
              ("cool+", "Enfriar +"), ("cool-", "Enfriar -")]
    for i, (key, label) in enumerate(labels):
        col = i % 2
        row = i // 2
        px = rects['explor'].x + int(24 * scale_x) + col * int(215 * scale_x)
        py = rects['explor'].y + int(38 * scale_y) + row * int(30 * scale_y)
        done = hj.explored[key]
        pygame.draw.circle(screen, C['GREEN'] if done else C['RED'],
                           (px, py + int(9 * scale_y)), int(6 * uniform_scale))
        text(label, fonts['FONT'], C['WHITE'] if done else C['LIGHT_GRAY'],
             px + int(16 * scale_x), py)
    status = ("Exploracion completa: " +
              ("hubo mejora, puedes hacer patron." if hj.exploration_success
               else "sin mejora, reduce delta.")) if hj.all_explored() else \
             "Prueba las 4 direcciones para decidir."
    text(status, fonts['SMALL_FONT'], C['ORANGE'],
         rects['explor'].x + int(24 * scale_x),
         rects['explor'].bottom - int(26 * scale_y))

    # Recursos
    draw_panel(rects['recursos'], title="RECURSOS")
    rx = rects['recursos'].x + int(24 * scale_x)
    ry = rects['recursos'].y + int(36 * scale_y)
    text(f"Lingotes: {g.lingotes}", fonts['FONT'],
         C['RED'] if g.lingotes <= 3 else C['WHITE'], rx, ry)
    text(f"Oro: {g.gold}", fonts['FONT'], C['GOLD'], rx + int(160 * scale_x), ry)
    text(f"Precio lingote: {g.lingote_price}", fonts['FONT'], C['ORANGE'],
         rx + int(280 * scale_x), ry)
    text("Cada accion (explorar / patron) consume 1 lingote.",
         fonts['SMALL_FONT'], C['DIM'], rx, ry + int(28 * scale_y))

    # Yunque y espada
    ax, ay = int(160 * scale_x), int(690 * scale_y)
    anvil(ax, ay)
    guard_x = ax - int(100 * uniform_scale)
    sword_y = ay - int(20 * uniform_scale)
    sword(q, guard_x, sword_y, 2 if g.shake > 0 else 0)
    ix, iy = impact_pos()
    if g.lava_anim > 0:
        bucket(g.lava_anim, g.max_b, ix, iy, True)
    elif g.water_anim > 0:
        bucket(g.water_anim, g.max_b, ix, iy, False)
    elif g.hammer_anim > 0:
        hammer_swing(g.hammer_anim, g.max_h, ix, iy)

    update_sparks()
    return rects


def draw_shop(g, mouse):
    draw_brick_background()
    rects = shop_rects()
    draw_panel(rects['panel'], alpha=215)
    text("TIENDA DEL HERRERO", fonts['TITLE_FONT'], C['YELLOW'],
         W // 2, rects['panel'].y + int(55 * scale_y), center=True)
    text(f"Oro: {g.gold}    Lingotes: {g.lingotes}", fonts['BIG_FONT'], C['WHITE'],
         W // 2, rects['panel'].y + int(115 * scale_y), center=True)
    hammer_cost = 100 + 60 * g.d_upgrade
    text(f"Martillo nivel {g.d_upgrade}  (delta inicial: {2.0 + g.d_upgrade * 0.5:.1f})",
         fonts['FONT'], C['LIGHT_GRAY'], W // 2, rects['panel'].y + int(148 * scale_y),
         center=True)
    button(rects['hammer'], f"Mejorar martillo (+0.5 delta inicial) - {hammer_cost} oro",
           C['BLUE'], fonts['FONT'], mouse, enabled=g.gold >= hammer_cost)
    lingote_cost = 5 * g.lingote_price
    button(rects['lingote'], f"Comprar 5 lingotes - {lingote_cost} oro",
           C['ORANGE'], fonts['FONT'], mouse, enabled=g.gold >= lingote_cost)
    button(rects['back'], "Volver a la forja", C['GRAY'], fonts['FONT'], mouse)
    return rects


def draw_result(g, mouse, tick):
    draw_brick_background()
    update_embers()
    if g.forge_res in ("exito", "fracaso"):
        rects = result_rects(False)
        draw_panel(rects['panel'], alpha=215)
        py = rects['panel'].y
        if g.forge_res == "exito":
            text("ESPADA VENDIDA!", fonts['TITLE_FONT'], C['GREEN'],
                 W // 2, py + int(55 * scale_y), center=True)
        else:
            text("ESPADA RECHAZADA", fonts['TITLE_FONT'], C['RED'],
                 W // 2, py + int(55 * scale_y), center=True)
        text(g.fmsg, fonts['FONT'], C['WHITE'], W // 2, py + int(110 * scale_y), center=True)
        q = g.opt.quality(g.opt.best_value)
        stats = [
            f"f final = {g.opt.best_value:.5f}   |   calidad {q:.1f} / {g.req}",
            f"Evaluaciones de f: {g.opt.evaluations}   |   Lingotes usados: {g.lingotes_gastados}",
            f"Oro total: {g.gold}   |   Espadas vendidas: {g.total_vendidas}",
        ]
        for i, s in enumerate(stats):
            text(s, fonts['FONT'], C['LIGHT_GRAY'], W // 2,
                 py + int((155 + i * 30) * scale_y), center=True)
        button(rects['next'], "Siguiente cliente", C['GREEN'], fonts['FONT'], mouse)
        return rects
    else:  # game_over
        rects = result_rects(True)
        draw_panel(rects['panel'], alpha=225)
        py = rects['panel'].y
        text("GAME OVER", fonts['HUGE_FONT'], C['RED'], W // 2,
             py + int(60 * scale_y), center=True)
        text(g.fmsg or "Te quedaste sin recursos.", fonts['BIG_FONT'], C['WHITE'],
             W // 2, py + int(125 * scale_y), center=True)
        text(f"Llegaste al nivel {g.level - 1} con {g.total_vendidas} espada(s) vendida(s).",
             fonts['FONT'], C['LIGHT_GRAY'], W // 2, py + int(165 * scale_y), center=True)

        history = g.show_history()
        if history:
            text("Historial reciente:", fonts['BIG_FONT'], C['YELLOW'],
                 W // 2, py + int(215 * scale_y), center=True)
            headers = ["Fecha", "Funcion", "Nivel", "Resultado", "f final", "Calidad", "Oro"]
            widths = [170, 120, 70, 120, 110, 90, 70]
            widths = [int(w * scale_x) for w in widths]
            start_x = (W - sum(widths)) / 2
            y = py + int(255 * scale_y)
            x = start_x
            for i, h in enumerate(headers):
                text(h, fonts['SMALL_FONT'], C['ORANGE'], x + widths[i] / 2, y, center=True)
                x += widths[i]
            y += int(28 * scale_y)
            for row in history[-8:]:
                row = (row + [""] * 7)[:7]
                x = start_x
                for i, val in enumerate(row):
                    col = C['GREEN'] if val == "VENDIDA" else \
                          C['RED'] if val in ("RECHAZADA", "GAME OVER") else C['WHITE']
                    text(val, fonts['SMALL_FONT'], col, x + widths[i] / 2, y, center=True)
                    x += widths[i]
                y += int(24 * scale_y)

        button(rects['retry'], "Reintentar", C['GREEN'], fonts['FONT'], mouse)
        button(rects['quit'], "Salir", C['RED'], fonts['FONT'], mouse)
        return rects


# =====================================================
# BUCLE PRINCIPAL
# =====================================================
def apply_resize(w, h, fullscreen=False):
    global W, H, screen, scale_x, scale_y, uniform_scale, fonts, _contour_cache
    if fullscreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        W, H = screen.get_width(), screen.get_height()
    else:
        W, H = max(900, w), max(600, h)
        screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
    scale_x = W / BASE_W
    scale_y = H / BASE_H
    uniform_scale = min(scale_x, scale_y)
    fonts = get_fonts()
    _contour_cache = {}


def main():
    game = None
    selected_func = "sphere"
    scene = "menu"
    fullscreen = False
    tick = 0
    running = True

    while running:
        clock.tick(60)
        tick += 1
        mouse = pygame.mouse.get_pos()
        if scene == "forge" and game:
            game.update_anim()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    apply_resize(BASE_W, BASE_H, fullscreen)
                elif scene == "forge" and game:
                    if e.key == pygame.K_RIGHT:
                        game.explore(game.opt.delta, 0)
                    elif e.key == pygame.K_LEFT:
                        game.explore(-game.opt.delta, 0)
                    elif e.key == pygame.K_UP:
                        game.explore(0, game.opt.delta)
                    elif e.key == pygame.K_DOWN:
                        game.explore(0, -game.opt.delta)
                    elif e.key == pygame.K_SPACE:
                        game.pattern()
                    elif e.key == pygame.K_r:
                        if game.reduce_delta():
                            scene = "result"
                    elif e.key == pygame.K_RETURN:
                        game.finish_forge()
                        scene = "result"
                    elif e.key == pygame.K_t:
                        scene = "shop"
                    if game.forge_res == "game_over":
                        scene = "result"
                elif scene == "tutorial" and e.key == pygame.K_ESCAPE:
                    scene = "menu"
                elif scene == "shop" and e.key in (pygame.K_ESCAPE, pygame.K_t):
                    scene = "forge"

            elif e.type == pygame.VIDEORESIZE and not fullscreen:
                apply_resize(e.w, e.h)

            elif e.type == pygame.MOUSEBUTTONDOWN:
                m = e.pos
                if scene == "menu":
                    rects = menu_rects()
                    for name, rect in rects['cards'].items():
                        if rect.collidepoint(m):
                            selected_func = name
                            sfx.play('click')
                    if rects['play'].collidepoint(m):
                        game = ForgeGame(func_name=selected_func)
                        scene = "forge"
                        sfx.play('sell')
                    elif rects['tutorial'].collidepoint(m):
                        scene = "tutorial"
                        sfx.play('click')

                elif scene == "tutorial":
                    back = R(BASE_W / 2 - 110, 720, 220, 52)
                    if back.collidepoint(m):
                        scene = "menu"
                        sfx.play('click')

                elif scene == "forge" and game:
                    if e.button == 3:
                        scene = "shop"
                        sfx.play('click')
                        continue
                    if e.button == 1:
                        rects = forge_rects()
                        if rects['temp+'].collidepoint(m):
                            game.explore(game.opt.delta, 0)
                        elif rects['temp-'].collidepoint(m):
                            game.explore(-game.opt.delta, 0)
                        elif rects['cool+'].collidepoint(m):
                            game.explore(0, game.opt.delta)
                        elif rects['cool-'].collidepoint(m):
                            game.explore(0, -game.opt.delta)
                        elif rects['pattern'].collidepoint(m):
                            game.pattern()
                        elif rects['reduce'].collidepoint(m):
                            if game.reduce_delta():
                                scene = "result"
                        elif rects['finish'].collidepoint(m):
                            game.finish_forge()
                            scene = "result"
                        elif rects['shop'].collidepoint(m):
                            scene = "shop"
                        if game.forge_res == "game_over":
                            scene = "result"

                elif scene == "shop" and game:
                    rects = shop_rects()
                    hammer_cost = 100 + 60 * game.d_upgrade
                    if rects['hammer'].collidepoint(m) and game.gold >= hammer_cost:
                        game.gold -= hammer_cost
                        game.d_upgrade += 1
                        sfx.play('sell')
                    elif rects['lingote'].collidepoint(m):
                        game.buy_lingotes(5)
                    elif rects['back'].collidepoint(m):
                        scene = "forge"
                        sfx.play('click')

                elif scene == "result" and game:
                    if game.forge_res == "game_over":
                        rects = result_rects(True)
                        if rects['retry'].collidepoint(m):
                            game = ForgeGame(func_name=selected_func)
                            scene = "forge"
                            sfx.play('sell')
                        elif rects['quit'].collidepoint(m):
                            running = False
                    else:
                        rects = result_rects(False)
                        if rects['next'].collidepoint(m) or rects['panel'].collidepoint(m):
                            game.next_customer()
                            scene = "forge"
                            sfx.play('click')

        # ------- dibujar escena actual -------
        if scene == "menu":
            draw_menu(selected_func, mouse, tick)
        elif scene == "tutorial":
            draw_tutorial(mouse)
        elif scene == "forge" and game:
            draw_forge(game, mouse, tick)
        elif scene == "shop" and game:
            draw_shop(game, mouse)
        elif scene == "result" and game:
            draw_result(game, mouse, tick)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()