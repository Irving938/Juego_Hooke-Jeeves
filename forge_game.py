import pygame
import math
import sys
import random
import csv
from datetime import datetime
from hooke_jeeves import HookeJeeves, FUNCTIONS

# =====================================================
# CONFIGURACIÓN INICIAL
# =====================================================
pygame.init()
BASE_W, BASE_H = 1200, 800
W, H = BASE_W, BASE_H
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("The Perfect Blade - Hooke-Jeeves Forge")
clock = pygame.time.Clock()

scale_x, scale_y = 1.0, 1.0
uniform_scale = 1.0

def get_fonts():
    return {
        'FONT': pygame.font.SysFont("arial", int(22 * scale_y)),
        'BIG_FONT': pygame.font.SysFont("arial", int(34 * scale_y), bold=True),
        'TITLE_FONT': pygame.font.SysFont("arial", int(50 * scale_y), bold=True),
        'SMALL_FONT': pygame.font.SysFont("arial", int(18 * scale_y)),
    }

fonts = get_fonts()

# Colores
C = {
    'WHITE': (245,245,245), 'BLACK': (20,20,20), 'GRAY': (80,80,80),
    'LIGHT_GRAY': (180,180,180), 'RED': (210,70,70), 'GREEN': (60,180,90),
    'BLUE': (60,120,220), 'ORANGE': (255,140,0), 'YELLOW': (255,220,50),
    'BROWN': (139,69,19), 'DARK_BROWN': (101,67,33), 'BACKGROUND': (40,40,45),
    'GOLD': (212,175,55), 'ANVIL_GRAY': (100,100,100), 'LAVA_RED': (255,60,0),
    'WATER_BLUE': (30,144,255), 'STONE': (125,125,125), 'DARK_STONE': (80,80,80),
    'MORTAR': (60,60,60), 'WALL_DARK': (40,40,45)
}

# =====================================================
# POSICIONES FIJAS (del layout exportado)
# =====================================================
HORNO             = (121, 223, 240, 240)   # x, y, w, h
PANEL_CLIENTE     = (483, 60, 245, 195)
PANEL_ALGORITMO   = (455, 342, 300, 210)
PANEL_MENSAJE     = (97, 66, 310, 50)
PANEL_BOTONES     = None  # los botones están sueltos, no dentro de un panel
PANEL_EXPLORACION = (771, 594, 420, 140)
BARRA_CALIDAD     = (92, 683, 300, 25)
YUNQUE            = (278, 624)
TEXTO_Z           = (591, 791)

# Botones (independientes, según el layout)
BTN_TEMP_PLUS  = (813, 158, 165, 60)
BTN_TEMP_MINUS = (990, 160, 165, 60)
BTN_COOL_PLUS  = (813, 257, 165, 60)
BTN_COOL_MINUS = (990, 257, 165, 60)
BTN_PATTERN    = (815, 58, 335, 65)
BTN_REDUCE     = (815, 358, 335, 65)
BTN_FINISH     = (815, 456, 335, 65)

# Martillo
HAMMER_HEAD   = (50, 50, 90, 52)
HAMMER_HANDLE = (87, 94, 14, 65)

# =====================================================
# FUNCIONES DE DIBUJO
# =====================================================
def draw_panel(x, y, w, h, alpha=180):
    panel = pygame.Surface((int(w), int(h)), pygame.SRCALPHA)
    panel.fill((20, 20, 25, alpha))
    screen.blit(panel, (int(x), int(y)))
    pygame.draw.rect(screen, C['DARK_STONE'], (int(x), int(y), int(w), int(h)), 2)

def text(txt, font, color, x, y, center=False):
    img = font.render(txt, True, color)
    r = img.get_rect(center=(int(x), int(y))) if center else img.get_rect(topleft=(int(x), int(y)))
    screen.blit(img, r)

def button(rect, txt, color, font):
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, C['WHITE'], rect, 2, border_radius=8)
    text(txt, font, C['WHITE'], rect.centerx, rect.centery, center=True)

def quality_bar(q, x, y, w=300, h=25):
    w, h = int(w), int(h)
    pygame.draw.rect(screen, C['GRAY'], (int(x), int(y), w, h))
    fill = int(w * q / 100)
    col = C['GREEN'] if q >= 80 else C['YELLOW'] if q >= 50 else C['RED']
    pygame.draw.rect(screen, col, (int(x), int(y), fill, h))
    pygame.draw.rect(screen, C['WHITE'], (int(x), int(y), w, h), 2)

def draw_brick_background():
    screen.fill(C['WALL_DARK'])
    brick_w = int(60 * scale_x)
    brick_h = int(30 * scale_y)
    for row in range(0, H, brick_h):
        offset = 0 if (row // brick_h) % 2 == 0 else brick_w // 2
        for col in range(-brick_w, W + brick_w, brick_w):
            rect = pygame.Rect(col + offset, row, brick_w - 2, brick_h - 2)
            pygame.draw.rect(screen, C['STONE'], rect)
            pygame.draw.rect(screen, C['MORTAR'], rect, 1)

def furnace_outline(x, y, w, h, tick):
    size = min(w, h)
    sc = size / 120.0
    border = pygame.Rect(int(x), int(y), int(size), int(size))
    pygame.draw.rect(screen, C['DARK_STONE'], border, int(4 * sc))
    mouth_w = int(80 * sc)
    mouth_h = int(55 * sc)
    mouth_x = int(x + 20 * sc)
    mouth_y = int(y + 55 * sc)
    mouth_rect = pygame.Rect(mouth_x, mouth_y, mouth_w, mouth_h)
    pygame.draw.rect(screen, C['BLACK'], mouth_rect)
    pygame.draw.rect(screen, C['DARK_STONE'], mouth_rect, int(3 * sc))
    fcol = [C['ORANGE'], C['YELLOW'], (255, 100, 0)]
    bfh = int(35 * sc)
    heights = [
        bfh + (tick * 3) % int(6 * sc),
        bfh + ((tick + 2) * 3) % int(8 * sc),
        bfh + ((tick + 4) * 3) % int(5 * sc)
    ]
    flame_xs = [mouth_x + mouth_w//4, mouth_x + mouth_w//2, mouth_x + 3*mouth_w//4]
    for i, fx in enumerate(flame_xs):
        fh = heights[i]
        pygame.draw.ellipse(screen, fcol[i % 3],
                            (fx - int(12*sc), mouth_rect.y - fh//2, int(24*sc), fh))
        pygame.draw.ellipse(screen, C['YELLOW'],
                            (fx - int(8*sc), mouth_rect.y - fh//3, int(16*sc), fh//1.5))
        for _ in range(int(3 * sc)):
            px = fx + random.randint(-int(8*sc), int(8*sc))
            py = mouth_rect.y - random.randint(int(10*sc), fh + int(5*sc))
            pygame.draw.rect(screen, random.choice(fcol), (px, py, int(4*sc), int(4*sc)))
    chim_w = int(40 * sc)
    chim_h = int(30 * sc)
    chim_rect = pygame.Rect(int(x + (size - chim_w)/2), int(y - chim_h), chim_w, chim_h)
    pygame.draw.rect(screen, C['DARK_STONE'], chim_rect)
    pygame.draw.rect(screen, C['MORTAR'], chim_rect, 2)
    if tick % 2 == 0:
        for s in range(3):
            pygame.draw.circle(screen, (180,180,180),
                               (chim_rect.centerx + (s-1)*int(15*sc), chim_rect.y - tick*2),
                               int(8*sc))

# =====================================================
# CLASE DEL JUEGO 
# =====================================================
class ForgeGame:
    def __init__(self, func_name="sphere"):
        self.opt = HookeJeeves(func_name=func_name)
        self.gold = 0
        self.lingotes = 0
        self.d_upgrade = 0
        self.level = 1
        self.base_lingote_cost = 50
        self.forge_res = None
        self.fmsg = ""
        self.req, self.reward = 0, 0
        self.shake = 0
        self.hammer_anim = 0
        self.lava_anim = 0
        self.water_anim = 0
        self.max_h, self.max_b = 20, 30
        self.game_over = False
        self.next_customer()

    def next_customer(self):
        cost = self.base_lingote_cost + (self.level - 1) * 30
        if self.level > 1 and self.gold < cost:
            self.forge_res = "sin_oro"
            self.fmsg = f"Necesitas {cost} oro para reponer lingotes."
            self.game_over = True
            return
        if self.level > 1:
            self.gold -= cost
        x0 = random.uniform(-8, 8)
        y0 = random.uniform(-8, 8)
        delta = 2.0 + self.d_upgrade * 0.5
        self.opt = HookeJeeves(x0, y0, delta, func_name=self.opt.func_name)
        self.lingotes = 20
        self.req = 60 + self.level * 10 + random.randint(-5, 5)
        self.reward = 100 + self.level * 50 + random.randint(-20, 20)
        self.forge_res = "forjando"
        self.opt.message = f"Nivel {self.level}: ¡Forja la espada!"
        self.level += 1

    def use_lingote(self):
        if self.lingotes > 0:
            self.lingotes -= 1
            return True
        return False

    def explore(self, dx, dy):
        if self.game_over: return
        if not self.use_lingote():
            self.opt.message = "¡Sin lingotes!"
            return
        if dx != 0: self.hammer_anim = self.max_h
        elif dy > 0: self.water_anim = self.max_b
        else: self.lava_anim = self.max_b
        improved = self.opt.explore_direction(dx, dy)
        if improved: self.shake = 5

    def pattern(self):
        if self.game_over: return
        if not self.opt.all_explored():
            self.opt.message = "Explora las 4 direcciones primero."
            return
        if not self.opt.exploration_success:
            self.opt.message = "Ninguna dirección mejoró. Reduce Δ."
            return
        if not self.use_lingote():
            self.opt.message = "¡Sin lingotes!"
            return
        self.hammer_anim = self.max_h
        improved = self.opt.pattern_move()
        if improved: self.shake = 5

    def reduce_delta(self):
        if self.game_over: return False
        stopped = self.opt.reduce_delta()
        if stopped:
            self.finish_forge()
        return stopped

    def finish_forge(self):
        q = self.opt.quality(self.opt.best_value)
        if q >= self.req:
            self.forge_res = "exito"
            self.gold += self.reward
            self.fmsg = f"¡Vendida por {self.reward} monedas!"
        else:
            self.forge_res = "fracaso"
            self.fmsg = f"Calidad insuficiente. Necesitaba {self.req}."

    def save_progress(self):
        with open("historial.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                self.level - 1,
                self.gold,
                self.req,
                self.reward,
                self.d_upgrade
            ])

    def show_history(self):
        try:
            with open("historial.csv", "r") as f:
                return [line.strip().split(",") for line in f.readlines()]
        except FileNotFoundError:
            return []

    def update_anim(self):
        if self.hammer_anim > 0: self.hammer_anim -= 1
        if self.lava_anim > 0: self.lava_anim -= 1
        if self.water_anim > 0: self.water_anim -= 1
        if self.shake > 0: self.shake -= 1

# =====================================================
# DIBUJOS DE OBJETOS 
# =====================================================
def anvil(x, y):
    w = int(180 * scale_x)
    h = int(25 * scale_y)
    pygame.draw.rect(screen, C['ANVIL_GRAY'], (int(x - 90*scale_x), int(y + 20*scale_y), w, h), border_radius=8)
    puntos = [(int(x - 60*scale_x), int(y + 20*scale_y)),
              (int(x + 60*scale_x), int(y + 20*scale_y)),
              (int(x + 30*scale_x), int(y - 20*scale_y)),
              (int(x - 30*scale_x), int(y - 20*scale_y))]
    pygame.draw.polygon(screen, C['ANVIL_GRAY'], puntos)
    pygame.draw.rect(screen, C['DARK_BROWN'], (int(x - 70*scale_x), int(y - 25*scale_y),
                                               int(140*scale_x), int(15*scale_y)), border_radius=4)

def sword(q, gx, gy, shake=0):
    gx += random.randint(-shake, shake)
    gy += random.randint(-shake, shake)
    if q < 30: bc, gl = (128,128,128), 0
    elif q < 50: bc, gl = (100,100,255), 50
    elif q < 70: bc, gl = (50,200,50), 100
    elif q < 90: bc, gl = (255,255,0), 180
    else: bc, gl = (255,255,255), 255
    if gl:
        s = pygame.Surface((int(200*scale_x), int(100*scale_y)), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (*bc, min(gl,80)), (int(10*scale_x), int(20*scale_y),
                                                   int(180*scale_x), int(40*scale_y)))
        screen.blit(s, (gx + int(10*scale_x), gy - int(30*scale_y)))
    tip = gx + int(190*scale_x)
    pts = [(gx, gy - int(9*scale_y)),
           (tip - int(20*scale_x), gy - int(13*scale_y)),
           (tip, gy),
           (tip - int(20*scale_x), gy + int(13*scale_y)),
           (gx, gy + int(9*scale_y))]
    pygame.draw.polygon(screen, bc, pts)
    pygame.draw.polygon(screen, C['BLACK'], pts, 2)
    pygame.draw.line(screen, C['BLACK'], (gx, gy), (tip - int(25*scale_x), gy), 2)
    gr = pygame.Rect(gx - int(4*scale_x), gy - int(15*scale_y), int(8*scale_x), int(30*scale_y))
    pygame.draw.rect(screen, C['YELLOW'], gr, border_radius=3)
    pygame.draw.rect(screen, C['BLACK'], gr, 2, border_radius=3)
    hr = pygame.Rect(gx - int(90*scale_x), gy - int(6*scale_y), int(90*scale_x), int(12*scale_y))
    pygame.draw.rect(screen, C['BROWN'], hr, border_radius=4)
    pygame.draw.rect(screen, C['BLACK'], hr, 2, border_radius=4)
    pygame.draw.circle(screen, C['GOLD'], (int(gx - 98*scale_x), int(gy)), int(12*scale_y))
    pygame.draw.circle(screen, C['BLACK'], (int(gx - 98*scale_x), int(gy)), int(12*scale_y), 2)

def hammer_swing(frame, maxf, ix, iy):
    if frame <= 0: return
    p = frame / maxf
    px, py = ix - 80*scale_x, iy - 120*scale_y
    al = 110*scale_x
    if p < 0.3: ang = -math.pi/4 * (p/0.3)
    elif p < 0.7: t = (p-0.3)/0.4; ang = -math.pi/4*(1-t) + math.pi/6*t
    else: t = (p-0.7)/0.3; ang = math.pi/6*(1-t)
    hx = px + al*math.cos(ang); hy = py + al*math.sin(ang)
    head_w = int(HAMMER_HEAD[2] * scale_x)
    head_h = int(HAMMER_HEAD[3] * scale_y)
    hs = pygame.Surface((head_w, head_h), pygame.SRCALPHA)
    pygame.draw.rect(hs, C['GRAY'], (0,0,head_w,head_h), border_radius=6)
    pygame.draw.rect(hs, C['BLACK'], (0,0,head_w,head_h), 3, border_radius=6)
    pygame.draw.rect(hs, C['DARK_BROWN'], (int(6*scale_x),int(4*scale_y),
                                           int(head_w-12*scale_x),int(6*scale_y)), border_radius=3)
    rh = pygame.transform.rotate(hs, math.degrees(-ang))
    screen.blit(rh, rh.get_rect(center=(hx, hy)))
    dx, dy = hx-px, hy-py
    d = math.hypot(dx, dy)
    ad = math.degrees(math.atan2(dy,dx))
    handle_w = int(HAMMER_HANDLE[2] * scale_x)
    handle_l = int(HAMMER_HANDLE[3] * scale_y)
    hl = d - head_h/2 - 4
    if hl > 10:
        hnd = pygame.Surface((handle_w, int(hl)), pygame.SRCALPHA)
        pygame.draw.rect(hnd, C['BROWN'], (0,0,handle_w,int(hl)), border_radius=5)
        pygame.draw.rect(hnd, C['BLACK'], (0,0,handle_w,int(hl)), 2, border_radius=5)
        rhn = pygame.transform.rotate(hnd, -ad+90)
        mx = px + (dx*(hl/2+head_h/2))/d; my = py + (dy*(hl/2+head_h/2))/d
        screen.blit(rhn, rhn.get_rect(center=(mx,my)))
    if 0.45 < p < 0.75:
        for _ in range(20):
            sx = ix + random.randint(-20,20)
            sy = iy + random.randint(-8,8)
            pygame.draw.circle(screen, random.choice([C['YELLOW'],C['ORANGE'],C['WHITE']]),
                               (int(sx), int(sy)), random.randint(2,5))

def bucket(frame, maxf, px, py, is_lava):
    if frame <= 0: return
    p = frame/maxf; tilt = 30*(1-p)
    bs = pygame.Surface((int(40*scale_x),int(30*scale_y)), pygame.SRCALPHA)
    col = C['GRAY'] if is_lava else C['LIGHT_GRAY']
    pygame.draw.rect(bs, col, (0,0,int(40*scale_x),int(30*scale_y)))
    pygame.draw.rect(bs, C['BLACK'], (0,0,int(40*scale_x),int(30*scale_y)), 2)
    pygame.draw.arc(bs, C['BLACK'], (int(10*scale_x),int(-15*scale_y),int(20*scale_x),int(20*scale_y)),
                    math.pi, 2*math.pi, 3)
    rb = pygame.transform.rotate(bs, -tilt)
    screen.blit(rb, (px - int(15*scale_x), py - int(50*scale_y)))
    if p > 0.1:
        sl = int(30*scale_y + 10*p)
        lc = C['LAVA_RED'] if is_lava else C['WATER_BLUE']
        dc = C['ORANGE'] if is_lava else C['BLUE']
        for i in range(3):
            sx = px - int(8*scale_x) + i*int(8*scale_x); sy = py - int(20*scale_y)
            pygame.draw.line(screen, lc, (sx, sy), (sx + random.randint(-4,4), sy + sl), 4)
        for _ in range(5):
            dx = px + random.randint(-15,15); dy = py + random.randint(0,20)
            pygame.draw.circle(screen, dc, (int(dx), int(dy)), 3)

# =====================================================
# ESCENAS
# =====================================================
def draw_menu():
    draw_brick_background()
    text("THE PERFECT BLADE", fonts['TITLE_FONT'], C['YELLOW'], W//2, H*0.25, center=True)
    text("Algoritmo Hooke-Jeeves en acción", fonts['FONT'], C['WHITE'], W//2, H*0.35, center=True)
    text("Haz clic para empezar", fonts['FONT'], C['GREEN'], W//2, H*0.6, center=True)

def draw_forge(g):
    draw_brick_background()

    # --- Horno ---
    ho_x, ho_y, ho_w, ho_h = HORNO
    ho_x *= scale_x; ho_y *= scale_y
    ho_w *= uniform_scale; ho_h *= uniform_scale
    furnace_size = min(ho_w, ho_h)
    glow = pygame.Surface((int(furnace_size*1.5), int(furnace_size*1.5)), pygame.SRCALPHA)
    for r in range(int(furnace_size*0.6), 0, -int(furnace_size*0.06)):
        alpha = max(0, 30 - r//5)
        pygame.draw.circle(glow, (255, 100, 0, alpha),
                           (int(furnace_size*0.75), int(furnace_size*0.75)), r)
    screen.blit(glow, (ho_x - int(furnace_size*0.25), ho_y - int(furnace_size*0.25)))
    furnace_outline(ho_x, ho_y, ho_w, ho_h, pygame.time.get_ticks()//150)

    # --- Panel cliente ---
    pc_x, pc_y, pc_w, pc_h = PANEL_CLIENTE
    pc_x *= scale_x; pc_y *= scale_y; pc_w *= scale_x; pc_h *= scale_y
    draw_panel(pc_x, pc_y, pc_w, pc_h, alpha=160)
    text(f"Nivel {g.level-1}", fonts['BIG_FONT'], C['YELLOW'], pc_x + 20*scale_x, pc_y + 30*scale_y)
    text(f"Requerida: {g.req}", fonts['FONT'], C['WHITE'], pc_x + 20*scale_x, pc_y + 70*scale_y)
    text(f"Recompensa: {g.reward} oro", fonts['FONT'], C['WHITE'], pc_x + 20*scale_x, pc_y + 100*scale_y)

    # --- Panel algoritmo ---
    pa_x, pa_y, pa_w, pa_h = PANEL_ALGORITMO
    pa_x *= scale_x; pa_y *= scale_y; pa_w *= scale_x; pa_h *= scale_y
    draw_panel(pa_x, pa_y, pa_w, pa_h, alpha=160)
    text("Estado del algoritmo", fonts['FONT'], C['ORANGE'], pa_x + 20*scale_x, pa_y + 20*scale_y)
    text(f"Temp (x): {g.opt.bx:.2f}", fonts['FONT'], C['WHITE'], pa_x + 20*scale_x, pa_y + 50*scale_y)
    text(f"Enfr (y): {g.opt.by:.2f}", fonts['FONT'], C['WHITE'], pa_x + 20*scale_x, pa_y + 75*scale_y)
    text(f"f(x): {g.opt.best_value:.4f}", fonts['FONT'], C['WHITE'], pa_x + 20*scale_x, pa_y + 100*scale_y)
    text(f"Δ = {g.opt.delta:.2f}", fonts['FONT'], C['WHITE'], pa_x + 20*scale_x, pa_y + 125*scale_y)
    text(f"Lingotes: {g.lingotes}", fonts['FONT'], C['WHITE'], pa_x + 20*scale_x, pa_y + 160*scale_y)
    text(f"Oro: {g.gold}", fonts['FONT'], C['YELLOW'], pa_x + 180*scale_x, pa_y + 160*scale_y)

    # --- Panel mensaje ---
    pm_x, pm_y, pm_w, pm_h = PANEL_MENSAJE
    pm_x *= scale_x; pm_y *= scale_y; pm_w *= scale_x; pm_h *= scale_y
    draw_panel(pm_x, pm_y, pm_w, pm_h, alpha=180)
    text(g.opt.message, fonts['FONT'], C['ORANGE'], pm_x + 20*scale_x, pm_y + 20*scale_y)

    # --- Botones de acción (sueltos) ---
    btn_defs = [
        (BTN_TEMP_PLUS,  'Temp +',         C['BLUE']),
        (BTN_TEMP_MINUS, 'Temp -',         C['BLUE']),
        (BTN_COOL_PLUS,  'Enfriar +',      C['BLUE']),
        (BTN_COOL_MINUS, 'Enfriar -',      C['BLUE']),
        (BTN_PATTERN,    'Repetir técnica',C['GREEN']),
        (BTN_REDUCE,     'Reducir Δ',      C['RED']),
        (BTN_FINISH,     'Terminar',       C['BROWN']),
    ]
    for (rx, ry, rw, rh), label, col in btn_defs:
        rect = pygame.Rect(rx*scale_x, ry*scale_y, rw*scale_x, rh*scale_y)
        button(rect, label, col, fonts['FONT'])

    # --- Yunque y espada ---
    ay_x, ay_y = YUNQUE
    anvil_x = ay_x * scale_x
    anvil_y = ay_y * scale_y
    anvil(anvil_x, anvil_y)
    guard_x = anvil_x - 100*scale_x
    sword_y = anvil_y - 20*scale_y
    q = g.opt.quality(g.opt.best_value)
    sword(q, guard_x, sword_y, 2 if g.shake>0 else 0)
    impact_x = guard_x + 90*scale_x
    impact_y = sword_y
    if g.lava_anim > 0: bucket(g.lava_anim, g.max_b, impact_x, impact_y, True)
    elif g.water_anim > 0: bucket(g.water_anim, g.max_b, impact_x, impact_y, False)
    elif g.hammer_anim > 0: hammer_swing(g.hammer_anim, g.max_h, impact_x, impact_y)

    # --- Panel exploración ---
    pe_x, pe_y, pe_w, pe_h = PANEL_EXPLORACION
    pe_x *= scale_x; pe_y *= scale_y; pe_w *= scale_x; pe_h *= scale_y
    draw_panel(pe_x, pe_y, pe_w, pe_h, alpha=160)
    text("Exploración:", fonts['SMALL_FONT'], C['LIGHT_GRAY'], pe_x + 20*scale_x, pe_y + 10*scale_y)
    y_off = pe_y + 30*scale_y
    for i, (key, explored) in enumerate(g.opt.explored.items()):
        col = C['GREEN'] if explored else C['RED']
        text(f"{key}: {'V' if explored else 'X'}", fonts['FONT'], col, pe_x + 20*scale_x, y_off + i*25*scale_y)
    if g.opt.delta < g.opt.epsilon:
        text("¡Precisión máxima!", fonts['FONT'], C['GREEN'], pe_x + 20*scale_x, y_off + 80*scale_y)

    # --- Barra calidad ---
    bc_x, bc_y, bc_w, bc_h = BARRA_CALIDAD
    bc_x *= scale_x; bc_y *= scale_y; bc_w *= scale_x; bc_h *= scale_y
    quality_bar(q, bc_x, bc_y, bc_w, bc_h)
    text(f"Calidad: {q:.1f}", fonts['FONT'], C['GREEN'], bc_x + bc_w + 20*scale_x, bc_y + bc_h/2)

    # --- Texto Z ---
    tz_x, tz_y = TEXTO_Z
    text("Presiona Z para terminar y guardar", fonts['FONT'], C['GRAY'], tz_x*scale_x, tz_y*scale_y, center=True)

def draw_shop(g):
    draw_brick_background()
    draw_panel(300*scale_x, 200*scale_y, 600*scale_x, 350*scale_y, alpha=180)
    text("TIENDA DEL HERRERO", fonts['TITLE_FONT'], C['YELLOW'], W//2, 240*scale_y, center=True)
    text(f"Oro: {g.gold}", fonts['BIG_FONT'], C['WHITE'], W//2, 290*scale_y, center=True)
    buy_rect = pygame.Rect(400*scale_x, 300*scale_y, 400*scale_x, 50*scale_y)
    delta_rect = pygame.Rect(400*scale_x, 380*scale_y, 400*scale_x, 50*scale_y)
    back_rect = pygame.Rect(500*scale_x, 500*scale_y, 200*scale_x, 50*scale_y)
    button(buy_rect, "Comprar 5 lingotes (50 oro)", C['GREEN'], fonts['FONT'])
    button(delta_rect, "Mejorar martillo (+0.5 Δ inicial) - 100 oro", C['BLUE'], fonts['FONT'])
    button(back_rect, "Volver a la forja", C['GRAY'], fonts['FONT'])
    text(f"Lingotes actuales: {g.lingotes}", fonts['FONT'], C['WHITE'], 450*scale_x, 460*scale_y)
    text(f"Martillo nivel: {g.d_upgrade}", fonts['FONT'], C['WHITE'], 450*scale_x, 485*scale_y)

def draw_result(g):
    draw_brick_background()
    draw_panel(300*scale_x, 200*scale_y, 600*scale_x, 300*scale_y, alpha=200)
    if g.forge_res == "exito":
        text("¡ESPADA VENDIDA!", fonts['BIG_FONT'], C['GREEN'], W//2, 270*scale_y, center=True)
        text(g.fmsg, fonts['FONT'], C['WHITE'], W//2, 320*scale_y, center=True)
    elif g.forge_res == "fracaso":
        text("ESPADA RECHAZADA", fonts['BIG_FONT'], C['RED'], W//2, 270*scale_y, center=True)
        text(g.fmsg, fonts['FONT'], C['WHITE'], W//2, 320*scale_y, center=True)
    elif g.forge_res == "sin_oro":
        text("¡QUEBRADO!", fonts['BIG_FONT'], C['RED'], W//2, 270*scale_y, center=True)
        text(g.fmsg, fonts['FONT'], C['WHITE'], W//2, 320*scale_y, center=True)
    text("Haz clic para continuar", fonts['FONT'], C['GRAY'], W//2, 380*scale_y, center=True)

def draw_history(history_data):
    draw_brick_background()
    draw_panel(100*scale_x, 80*scale_y, 1000*scale_x, 600*scale_y, alpha=200)
    text("HISTORIAL DE PARTIDAS", fonts['TITLE_FONT'], C['YELLOW'], W//2, 120*scale_y, center=True)
    y = 160*scale_y
    for row in history_data[-10:]:
        text(" | ".join(row), fonts['FONT'], C['WHITE'], 150*scale_x, y)
        y += 30*scale_y
    text("Presiona cualquier tecla para salir", fonts['FONT'], C['GRAY'], W//2, H-60*scale_y, center=True)

# =====================================================
# BUCLE PRINCIPAL
# =====================================================
def main():
    global W, H, screen, scale_x, scale_y, uniform_scale, fonts
    game = ForgeGame(func_name="sphere")
    scene = "menu"
    fullscreen = False
    running = True
    while running:
        clock.tick(60)
        if scene in ("forge",):
            game.update_anim()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
                        W, H = screen.get_width(), screen.get_height()
                    else:
                        W, H = BASE_W, BASE_H
                        screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
                    scale_x = W / BASE_W
                    scale_y = H / BASE_H
                    uniform_scale = min(scale_x, scale_y)
                    fonts = get_fonts()
                elif e.key == pygame.K_z and scene == "forge":
                    game.save_progress()
                    scene = "history"
                elif e.key == pygame.K_ESCAPE and scene == "history":
                    running = False
            if e.type == pygame.VIDEORESIZE and not fullscreen:
                W, H = e.size
                screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
                scale_x = W / BASE_W
                scale_y = H / BASE_H
                uniform_scale = min(scale_x, scale_y)
                fonts = get_fonts()
            if e.type == pygame.MOUSEBUTTONDOWN:
                m = pygame.mouse.get_pos()
                if scene == "menu":
                    if e.button == 1:
                        scene = "forge"
                elif scene == "forge":
                    if e.button == 3:
                        scene = "shop"
                        continue
                    if e.button == 1:
                        btn_defs = [
                            (BTN_TEMP_PLUS,  'temp_plus'),
                            (BTN_TEMP_MINUS, 'temp_minus'),
                            (BTN_COOL_PLUS,  'cool_plus'),
                            (BTN_COOL_MINUS, 'cool_minus'),
                            (BTN_PATTERN,    'pattern'),
                            (BTN_REDUCE,     'reduce'),
                            (BTN_FINISH,     'finish'),
                        ]
                        for (rx, ry, rw, rh), action in btn_defs:
                            rect = pygame.Rect(rx*scale_x, ry*scale_y, rw*scale_x, rh*scale_y)
                            if rect.collidepoint(m):
                                if action == 'temp_plus': game.explore(game.opt.delta, 0)
                                elif action == 'temp_minus': game.explore(-game.opt.delta, 0)
                                elif action == 'cool_plus': game.explore(0, game.opt.delta)
                                elif action == 'cool_minus': game.explore(0, -game.opt.delta)
                                elif action == 'pattern': game.pattern()
                                elif action == 'reduce':
                                    if game.reduce_delta():
                                        game.save_progress()
                                        scene = "result"
                                elif action == 'finish':
                                    game.finish_forge()
                                    game.save_progress()
                                    scene = "result"
                                break
                elif scene == "shop":
                    buy_rect = pygame.Rect(400*scale_x, 300*scale_y, 400*scale_x, 50*scale_y)
                    delta_rect = pygame.Rect(400*scale_x, 380*scale_y, 400*scale_x, 50*scale_y)
                    back_rect = pygame.Rect(500*scale_x, 500*scale_y, 200*scale_x, 50*scale_y)
                    if buy_rect.collidepoint(m) and game.gold >= 50:
                        game.gold -= 50
                        game.lingotes += 5
                    elif delta_rect.collidepoint(m) and game.gold >= 100:
                        game.gold -= 100
                        game.d_upgrade += 1
                    elif back_rect.collidepoint(m):
                        scene = "forge"
                elif scene == "result":
                    if game.forge_res == "sin_oro":
                        running = False
                    else:
                        game.next_customer()
                        if game.game_over:
                            game.save_progress()
                            scene = "history"
                        else:
                            scene = "forge"
                elif scene == "history":
                    running = False

        if scene == "menu": draw_menu()
        elif scene == "forge": draw_forge(game)
        elif scene == "shop": draw_shop(game)
        elif scene == "result": draw_result(game)
        elif scene == "history": draw_history(game.show_history())
        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()