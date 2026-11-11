"""Code-drawn 2D illustration kit in the channel style (no image model needed).

Stickman characters (big round white head, thick outline, thin black limbs,
one signature outfit) on painterly gradient backgrounds with glows.
Coordinates are in a 1080x1920 layout space; drawing happens at 2x and is
downsampled for clean anti-aliased lines.

    python -m studio.draw2d lighthouse      # writes assets/lighthouse/beat_NN.png
"""
from __future__ import annotations

import math
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import config

W, H, SS = 1080, 1920, 2
INK = (24, 22, 28)


class Canvas:
    def __init__(self, top=(40, 60, 110), bottom=(240, 150, 110)):
        self.img = gradient(top, bottom)
        self.d = ImageDraw.Draw(self.img)

    # coordinate helpers -----------------------------------------------------
    @staticmethod
    def p(*xy):
        return [v * SS for v in xy]

    def poly(self, pts, fill, outline=INK, width=7):
        pts = [(x * SS, y * SS) for x, y in pts]
        self.d.polygon(pts, fill=fill)
        if outline and width:
            self.d.line(pts + [pts[0]], fill=outline, width=int(width * SS), joint="curve")

    def rect(self, x0, y0, x1, y1, fill, outline=INK, width=7, r=0):
        self.d.rounded_rectangle(self.p(x0, y0, x1, y1), radius=r * SS, fill=fill,
                                 outline=outline if width else None, width=int(width * SS))

    def ellipse(self, cx, cy, rx, ry, fill, outline=INK, width=7):
        self.d.ellipse(self.p(cx - rx, cy - ry, cx + rx, cy + ry), fill=fill,
                       outline=outline if width else None, width=int(width * SS))

    def line(self, pts, fill=INK, width=7):
        self.d.line([(x * SS, y * SS) for x, y in pts], fill=fill, width=int(width * SS), joint="curve")
        for x, y in (pts[0], pts[-1]):
            r = width * SS / 2
            self.d.ellipse((x * SS - r, y * SS - r, x * SS + r, y * SS + r), fill=fill)

    def arc(self, cx, cy, r, a0, a1, fill=INK, width=6):
        self.d.arc(self.p(cx - r, cy - r, cx + r, cy + r), a0, a1, fill=fill, width=int(width * SS))

    def glow(self, cx, cy, r, color, strength=1.0):
        layer = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        ImageDraw.Draw(layer).ellipse(self.p(cx - r, cy - r, cx + r, cy + r), fill=color + (int(200 * strength),))
        layer = layer.filter(ImageFilter.GaussianBlur(r * SS * 0.45))
        self.img.alpha_composite(layer)

    def beam(self, x, y, angle_deg, length, spread_deg, color=(255, 240, 180), alpha=150):
        layer = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        a0, a1 = math.radians(angle_deg - spread_deg), math.radians(angle_deg + spread_deg)
        pts = [(x, y), (x + length * math.cos(a0), y + length * math.sin(a0)),
               (x + length * math.cos(a1), y + length * math.sin(a1))]
        ImageDraw.Draw(layer).polygon([(px * SS, py * SS) for px, py in pts], fill=color + (alpha,))
        layer = layer.filter(ImageFilter.GaussianBlur(14 * SS))
        self.img.alpha_composite(layer)

    def shade(self, alpha=90, color=(10, 10, 30)):
        """Full-frame tint, e.g. for night."""
        self.img.alpha_composite(Image.new("RGBA", self.img.size, color + (alpha,)))

    def vignette(self, strength=0.55):
        yy, xx = np.mgrid[0:H * SS:4, 0:W * SS:4]
        d = np.sqrt(((xx / (W * SS) - 0.5) * 1.4) ** 2 + ((yy / (H * SS) - 0.5) * 1.0) ** 2)
        a = np.clip((d - 0.35) * 1.6, 0, 1) * 255 * strength
        mask = Image.fromarray(a.astype(np.uint8)).resize(self.img.size, Image.BILINEAR)
        dark = Image.new("RGBA", self.img.size, (8, 6, 18, 255))
        dark.putalpha(mask)
        self.img.alpha_composite(dark)

    def save(self, path):
        self.vignette()
        self.img.convert("RGB").resize((W, H), Image.LANCZOS).save(path, quality=95)


def gradient(top, bottom, mid=None):
    t = np.linspace(0, 1, H * SS)[:, None]
    if mid is not None:
        c = np.where(t < 0.5, np.array(top) * (1 - t * 2) + np.array(mid) * t * 2,
                     np.array(mid) * (1 - (t - 0.5) * 2) + np.array(bottom) * (t - 0.5) * 2)
    else:
        c = np.array(top) * (1 - t) + np.array(bottom) * t
    arr = np.repeat(c[:, None, :], W * SS, axis=1).astype(np.uint8)
    img = Image.fromarray(arr, "RGB").convert("RGBA")
    return img


# --------------------------------------------------------------------------- characters
def stickman(c: Canvas, x, y, h=520, coat=(250, 205, 40), hat="beanie", hat_color=(30, 30, 36),
             face="neutral", arms=((-30, 60), (210, 60)), legs=((-8, 0), (8, 0)), scarf=(215, 50, 50),
             look=0.0, sweat=False, item=None):
    """Draw a stickman standing with feet at (x, y). h = total height.
    arms: ((angle_deg, bend_deg), ...) angle 0 = right, 90 = down. legs: (dx_foot, lift)."""
    head_r = h * 0.2
    hy = y - h + head_r
    body_top, body_bot = hy + head_r * 0.85, y - h * 0.34
    bw = head_r * 0.82
    lw = max(5, h * 0.016)
    # legs
    for (dx, lift) in legs:
        hip = (x + (dx * 0.4), body_bot - 4)
        foot = (x + dx * 6, y - lift)
        c.line([hip, ((hip[0] + foot[0]) / 2 + dx * 0.8, (hip[1] + foot[1]) / 2), foot], width=lw)
        c.ellipse(foot[0] + (8 if dx >= 0 else -8), y - lift, lw * 1.7, lw * 0.9, INK, width=0)
    # body (coat) capsule
    c.rect(x - bw, body_top, x + bw, body_bot, coat, r=bw * 0.9, width=lw)
    c.line([(x, body_top + 30), (x, body_bot - 20)], fill=tuple(int(v * 0.75) for v in coat), width=lw * 0.6)
    # arms
    sh = (x, body_top + head_r * 0.35)
    for (ang, bend) in arms:
        a = math.radians(ang)
        L = h * 0.2
        elbow = (sh[0] + L * math.cos(a), sh[1] + L * math.sin(a))
        b = math.radians(ang + bend)
        hand = (elbow[0] + L * math.cos(b), elbow[1] + L * math.sin(b))
        c.line([sh, elbow, hand], width=lw)
        c.ellipse(hand[0], hand[1], lw * 1.1, lw * 1.1, INK, width=0)
    if item:
        item(c, sh, h)
    if scarf:
        c.rect(x - bw * 0.95, body_top - 6, x + bw * 0.95, body_top + head_r * 0.28, scarf, r=12, width=lw * 0.8)
    # head
    c.ellipse(x, hy, head_r, head_r, (252, 252, 250), width=lw * 1.15)
    ex = x + look * head_r * 0.35
    _face(c, ex, hy, head_r, face, lw)
    if hat == "beanie":
        c.d.chord(Canvas.p(x - head_r * 1.02, hy - head_r * 1.05, x + head_r * 1.02, hy + head_r * 0.55),
                  180, 360, fill=hat_color, outline=INK, width=int(lw * SS))
        c.rect(x - head_r * 1.05, hy - head_r * 0.32, x + head_r * 1.05, hy - head_r * 0.08, hat_color, r=8, width=lw * 0.9)
    if sweat:
        sx, sy = x + head_r * 0.85, hy - head_r * 0.25
        c.poly([(sx, sy - 34), (sx - 16, sy), (sx + 16, sy)], (140, 200, 255), width=lw * 0.6)
        c.ellipse(sx, sy + 2, 16, 16, (140, 200, 255), width=lw * 0.6)


def _face(c, x, y, r, face, lw):
    if face in ("shock", "scared"):
        for s in (-1, 1):
            c.ellipse(x + s * r * 0.36, y - r * 0.05, r * 0.24, r * 0.27, (255, 255, 255), width=lw * 0.7)
            c.ellipse(x + s * r * 0.36, y - r * 0.02, r * 0.08, r * 0.08, INK, width=0)
        if face == "shock":
            c.ellipse(x, y + r * 0.48, r * 0.16, r * 0.2, INK, width=0)
        else:
            pts = [(x - r * 0.3 + i * r * 0.12, y + r * 0.5 + (8 if i % 2 else -8)) for i in range(6)]
            c.line(pts, width=lw * 0.7)
        c.line([(x - r * 0.6, y - r * 0.45), (x - r * 0.2, y - r * 0.55)], width=lw * 0.7)
        c.line([(x + r * 0.2, y - r * 0.55), (x + r * 0.6, y - r * 0.45)], width=lw * 0.7)
    elif face == "squint":
        for s in (-1, 1):
            c.line([(x + s * r * 0.5, y - r * 0.12), (x + s * r * 0.2, y - r * 0.02), (x + s * r * 0.5, y + r * 0.06)], width=lw * 0.8)
        c.line([(x - r * 0.2, y + r * 0.45), (x + r * 0.2, y + r * 0.45)], width=lw * 0.8)
    elif face == "determined":
        for s in (-1, 1):
            c.ellipse(x + s * r * 0.33, y, r * 0.09, r * 0.12, INK, width=0)
            c.line([(x + s * r * 0.58, y - r * 0.3), (x + s * r * 0.15, y - r * 0.2)], width=lw * 0.8)
        c.arc(x, y + r * 0.62, r * 0.3, 220, 320, width=lw * 0.7)
    else:  # neutral / curious
        for s in (-1, 1):
            c.ellipse(x + s * r * 0.33, y, r * 0.09, r * 0.12, INK, width=0)
            c.line([(x + s * r * 0.55, y - r * 0.32), (x + s * r * 0.15, y - r * 0.36)], width=lw * 0.7)
        c.arc(x, y + r * 0.2, r * 0.3, 50, 130, width=lw * 0.7)


def lantern(c, sh, h):
    x, y = sh[0] + h * 0.33, sh[1] + h * 0.12
    c.glow(x, y + 40, 120, (255, 200, 90), 0.9)
    c.line([(x, y - 10), (x, y + 10)], width=5)
    c.rect(x - 22, y + 10, x + 22, y + 70, (255, 214, 120), r=8, width=5)


# --------------------------------------------------------------------------- props
def sea(c, top_y, color=(30, 90, 120), dark=(10, 40, 70), waves=True, seed=1):
    rnd = random.Random(seed)
    t = np.linspace(0, 1, int((H - top_y) * SS))[:, None]
    arr = (np.array(color) * (1 - t) + np.array(dark) * t)
    arr = np.repeat(arr[:, None, :], W * SS, axis=1).astype(np.uint8)
    c.img.paste(Image.fromarray(arr, "RGB").convert("RGBA"), (0, int(top_y * SS)))
    if waves:
        for _ in range(70):
            wx, wy = rnd.uniform(0, W), rnd.uniform(top_y + 20, H)
            s = 14 + (wy - top_y) / 18
            col = tuple(min(255, int(v * 1.5 + 40)) for v in color)
            c.arc(wx, wy, s, 200, 340, fill=col, width=max(3, s / 6))


def rocks(c, cx, y, w, color=(70, 72, 84)):
    pts = [(cx - w, y + 30), (cx - w * 0.8, y - 40), (cx - w * 0.45, y - 75), (cx - w * 0.1, y - 60),
           (cx + w * 0.3, y - 85), (cx + w * 0.7, y - 45), (cx + w, y + 30)]
    c.poly(pts, color, width=8)
    c.line([(cx - w * 0.45, y - 75), (cx - w * 0.3, y - 10)], fill=(50, 52, 62), width=6)
    c.line([(cx + w * 0.3, y - 85), (cx + w * 0.4, y - 20)], fill=(50, 52, 62), width=6)


def lighthouse(c, cx, base_y, h=900, lit=False, door=True):
    bw, tw = h * 0.16, h * 0.105
    top_y = base_y - h
    # tower with stripes
    pts = [(cx - bw, base_y), (cx - tw, top_y + h * 0.18), (cx + tw, top_y + h * 0.18), (cx + bw, base_y)]
    c.poly(pts, (245, 242, 235), width=9)
    for k in range(3):
        y0 = base_y - h * (0.12 + k * 0.25)
        y1 = y0 - h * 0.11
        f0 = (base_y - y0) / (base_y - (top_y + h * 0.18))
        f1 = (base_y - y1) / (base_y - (top_y + h * 0.18))
        w0, w1 = bw - (bw - tw) * f0, bw - (bw - tw) * f1
        c.poly([(cx - w0, y0), (cx - w1, y1), (cx + w1, y1), (cx + w0, y0)], (205, 50, 50), width=6)
    # gallery + lamp room + roof
    gy = top_y + h * 0.18
    c.rect(cx - tw * 1.45, gy - 22, cx + tw * 1.45, gy + 6, (60, 60, 70), r=6, width=7)
    c.rect(cx - tw * 0.9, gy - h * 0.1, cx + tw * 0.9, gy - 22, (255, 230, 150) if lit else (70, 90, 120), r=6, width=8)
    c.poly([(cx - tw * 1.15, gy - h * 0.1), (cx, top_y), (cx + tw * 1.15, gy - h * 0.1)], (180, 40, 45), width=8)
    if lit:
        c.glow(cx, gy - h * 0.06, h * 0.22, (255, 235, 160), 1.0)
    if door:
        c.rect(cx - bw * 0.28, base_y - h * 0.14, cx + bw * 0.28, base_y, (70, 110, 140), r=18, width=7)
    for k in range(2):
        wy = base_y - h * (0.38 + k * 0.25)
        c.rect(cx - 16, wy, cx + 16, wy + 44, (40, 50, 70), r=10, width=5)


def ship(c, x, y, s=1.0, color=(60, 60, 75)):
    c.poly([(x - 90 * s, y), (x + 90 * s, y), (x + 65 * s, y + 35 * s), (x - 65 * s, y + 35 * s)], color, width=5)
    c.rect(x - 40 * s, y - 40 * s, x + 25 * s, y, (220, 220, 225), width=5)
    c.rect(x - 5 * s, y - 75 * s, x + 12 * s, y - 40 * s, (200, 60, 60), width=5)


def gull(c, x, y, s=1.0):
    c.line([(x - 30 * s, y), (x - 12 * s, y - 14 * s), (x, y)], width=5)
    c.line([(x, y), (x + 12 * s, y - 14 * s), (x + 30 * s, y)], width=5)


def stars(c, n=80, seed=3, max_y=900):
    rnd = random.Random(seed)
    for _ in range(n):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, max_y), rnd.uniform(2, 5)
        c.ellipse(x, y, r, r, (255, 250, 220), width=0)


def tally_marks(c, x0, y0, x1, y1, n_groups, color=(70, 45, 30), fresh=0, seed=5, size=60):
    rnd = random.Random(seed)
    gx, gy = x0, y0
    groups = []
    while gy < y1 and len(groups) < n_groups:
        groups.append((gx, gy))
        gx += size * 1.6
        if gx > x1:
            gx, gy = x0 + rnd.uniform(-10, 30), gy + size * 1.5
    for i, (gx, gy) in enumerate(groups):
        col = (235, 205, 160) if i >= len(groups) - fresh else color
        jit = lambda: rnd.uniform(-4, 4)
        for k in range(4):
            c.line([(gx + k * size * 0.22 + jit(), gy + jit()), (gx + k * size * 0.22 + jit(), gy + size + jit())], fill=col, width=max(4, size / 10))
        c.line([(gx - 8, gy + size * 0.8), (gx + size * 0.8, gy + size * 0.15)], fill=col, width=max(4, size / 10))


def floorboards(c, y0=0, color=(150, 105, 70)):
    for k in range(0, W, 135):
        shade = tuple(int(v * (0.9 + 0.1 * ((k // 135) % 2))) for v in color)
        c.rect(k, y0, k + 135, H, shade, width=5)


def chair(c, x, y, s=1.0, color=(140, 90, 55)):
    c.rect(x - 90 * s, y - 330 * s, x + 90 * s, y - 300 * s, color, r=8, width=7)      # top rail
    c.rect(x - 90 * s, y - 330 * s, x - 65 * s, y, color, r=6, width=7)              # back legs
    c.rect(x + 65 * s, y - 330 * s, x + 90 * s, y, color, r=6, width=7)
    c.rect(x - 90 * s, y - 230 * s, x + 90 * s, y - 210 * s, color, r=6, width=6)
    c.rect(x - 105 * s, y - 150 * s, x + 105 * s, y - 120 * s, color, r=8, width=7)    # seat
    c.rect(x - 105 * s, y - 120 * s, x - 82 * s, y + 10 * s, color, r=6, width=7)
    c.rect(x + 82 * s, y - 120 * s, x + 105 * s, y + 10 * s, color, r=6, width=7)


# --------------------------------------------------------------------------- lighthouse story
def lighthouse_scenes():
    S = []

    def b1():  # lonely lighthouse at dusk, ships safe
        c = Canvas((38, 44, 92), (250, 150, 95))
        c.glow(780, 820, 260, (255, 190, 120), 0.6)
        sea(c, 1080, (40, 100, 130), (12, 40, 70))
        ship(c, 200, 1150, 0.7)
        ship(c, 930, 1210, 0.5)
        lighthouse(c, 560, 1250, 820)
        rocks(c, 560, 1290, 330)
        for gx, gy in ((300, 360), (380, 420), (820, 300)):
            gull(c, gx, gy, 1.2)
        return c

    def b2():  # waves crash, ship sails by untouched
        c = Canvas((80, 120, 170), (200, 220, 230))
        sea(c, 980, (50, 120, 150), (15, 50, 80), seed=4)
        lighthouse(c, 360, 1180, 760)
        rocks(c, 360, 1220, 300)
        for k in range(5):
            c.ellipse(170 + k * 90, 1230 - (k % 2) * 30, 70, 45, (235, 245, 250), width=6)
        ship(c, 820, 1100, 1.1)
        return c

    def b3():  # close-up door, gull on railing
        c = Canvas((230, 225, 215), (205, 195, 180))
        c.rect(0, 0, W, H, (238, 234, 226), width=0)
        for k in range(0, H, 160):
            c.line([(0, k), (W, k)], fill=(215, 210, 200), width=4)
        c.rect(230, 520, 850, 1520, (80, 120, 150), r=200, width=12)
        c.rect(280, 600, 800, 1470, (95, 140, 172), r=160, width=6)
        c.ellipse(720, 1050, 28, 28, (200, 170, 70), width=6)
        c.rect(0, 1480, W, 1540, (70, 70, 80), width=8)
        for k in range(60, W, 140):
            c.rect(k, 1540, k + 18, 1900, (70, 70, 80), width=6)
        gx, gy = 880, 1440
        c.ellipse(gx, gy, 70, 42, (245, 245, 245), width=7)
        c.ellipse(gx - 60, gy - 40, 34, 32, (245, 245, 245), width=7)
        c.ellipse(gx - 68, gy - 46, 6, 6, INK, width=0)
        c.poly([(gx - 94, gy - 40), (gx - 125, gy - 32), (gx - 94, gy - 28)], (250, 180, 40), width=5)
        return c

    def b4():  # empty dock, 1987 sign
        c = Canvas((120, 140, 160), (210, 200, 185))
        sea(c, 900, (70, 110, 130), (30, 60, 80), seed=7)
        for k in range(6):
            x = 140 + k * 150
            c.rect(x, 1000 + k * 40, x + 28, 1500 + k * 40, (110, 80, 55), width=6)
        c.poly([(80, 1060), (1000, 1210), (1000, 1290), (80, 1140)], (150, 110, 75), width=8)
        c.line([(560, 1180), (620, 1250), (640, 1360)], fill=(220, 200, 150), width=8)
        c.rect(640, 640, 980, 860, (190, 160, 110), r=10, width=9)
        c.rect(790, 860, 830, 1180, (110, 80, 55), width=7)
        from PIL import ImageFont
        f = ImageFont.truetype(str(config.FONTS / "Inter-Black.otf"), 120 * SS)
        c.d.text((810 * SS, 750 * SS), "1987", font=f, fill=(70, 45, 30), anchor="mm")
        return c

    def b5():  # night: beam blazes on, townspeople pointing
        c = Canvas((8, 12, 40), (30, 40, 90))
        stars(c, 90)
        sea(c, 1000, (20, 40, 80), (5, 15, 35), seed=9)
        lighthouse(c, 760, 1060, 620, lit=True)
        rocks(c, 760, 1090, 220, (40, 42, 55))
        c.beam(760, 520, 180, 1100, 9, alpha=170)
        c.beam(760, 520, 0, 700, 7, alpha=130)
        c.rect(0, 1500, W, H, (25, 28, 40), width=0)
        for i, x in enumerate((140, 330, 520)):
            stickman(c, x, 1860, 380, coat=[(90, 120, 200), (200, 90, 90), (90, 170, 120)][i], hat=None,
                     scarf=None, face="shock", arms=((-40, -10), (120, 30)), look=0.6)
        return c

    def b6():  # Theo rows toward glowing lighthouse
        c = Canvas((12, 18, 50), (40, 50, 100))
        stars(c, 70, seed=5)
        sea(c, 900, (25, 50, 90), (6, 18, 40), seed=11)
        lighthouse(c, 300, 960, 460, lit=True)
        c.beam(300, 640, 20, 900, 6, alpha=110)
        c.poly([(380, 1520), (980, 1520), (900, 1660), (460, 1660)], (200, 60, 50), width=9)
        stickman(c, 680, 1560, 420, face="determined", arms=((150, -40), (200, -60)), legs=((-6, 0), (6, 0)), look=-0.6)
        c.line([(560, 1450), (330, 1700)], fill=(140, 100, 60), width=12)
        return c

    def b7():  # spiral staircase looking up
        c = Canvas((30, 28, 40), (70, 60, 70))
        cx, cy = 540, 960
        for k in range(26, 0, -1):
            r = 60 + k * 32
            col = tuple(int(v * (0.35 + 0.025 * k)) for v in (200, 170, 130))
            c.ellipse(cx, cy, r, r, col, width=5)
        for k in range(48):
            a = k * 0.42
            r0, r1 = 80 + k * 17, 130 + k * 17
            c.line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))],
                   fill=(230, 210, 170), width=9)
        c.glow(cx, cy, 80, (255, 245, 210), 0.8)
        stickman(c, 540, 1800, 360, face="shock", look=0.0, item=lantern, arms=((-100, 10), (40, 50)))
        return c

    def b8():  # lamp room, glowing lamp, Theo squinting
        c = Canvas((40, 30, 30), (90, 60, 40))
        c.rect(0, 1400, W, H, (110, 75, 50), width=0)
        c.glow(560, 760, 420, (255, 220, 140), 1.0)
        c.rect(380, 520, 740, 1080, (255, 225, 140), r=60, width=12)
        for k in range(5):
            c.line([(400 + k * 80, 540), (400 + k * 80, 1060)], fill=(230, 180, 90), width=6)
        c.glow(560, 790, 200, (255, 255, 230), 1.0)
        c.rect(420, 1080, 700, 1180, (150, 110, 60), width=9)
        stickman(c, 830, 1820, 470, face="squint", arms=((-120, -40), (100, 20)), look=-0.5)
        return c

    def b9():  # chair facing window and dark sea
        c = Canvas((30, 26, 34), (60, 45, 40))
        c.rect(170, 260, 910, 1180, (12, 22, 46), r=30, width=14)
        stars(c, 25, seed=12, max_y=700)
        for k in range(8):
            c.arc(540 + (k - 4) * 90, 1000 + (k % 3) * 40, 30, 200, 340, fill=(70, 100, 150), width=5)
        c.line([(540, 260), (540, 1180)], width=10)
        c.line([(170, 720), (910, 720)], width=10)
        c.rect(0, 1300, W, H, (95, 65, 45), width=0)
        c.glow(540, 700, 300, (120, 160, 255), 0.35)
        chair(c, 540, 1660, 1.5)
        return c

    def b10():  # floor covered in tally marks, boots at edge
        c = Canvas((150, 105, 70), (120, 80, 55))
        floorboards(c, 0)
        tally_marks(c, 60, 80, 1020, 1600, 90, seed=7, size=70)
        for x in (360, 720):
            c.ellipse(x, 1820, 120, 70, (40, 35, 35), width=7)
        c.glow(540, 300, 400, (255, 210, 140), 0.25)
        return c

    def b11():  # extreme close-up tally marks, fresh ones
        c = Canvas((160, 112, 75), (130, 90, 60))
        floorboards(c, 0, (160, 112, 75))
        tally_marks(c, 80, 320, 1000, 1450, 14, fresh=4, seed=9, size=190)
        return c

    def b12():  # Theo kneeling, terrified
        c = Canvas((45, 35, 35), (110, 75, 50))
        floorboards(c, 1250, (130, 90, 60))
        tally_marks(c, 60, 1500, 1020, 1900, 12, fresh=1, seed=3, size=60)
        c.glow(700, 1600, 70, (255, 230, 170), 0.7)
        stickman(c, 470, 1640, 760, face="scared", sweat=True, arms=((40, 30), (120, 10)), legs=((-14, 0), (10, 90)), look=0.4)
        return c

    def b13():  # looking down dark stairs, shadow climbing
        c = Canvas((20, 18, 26), (5, 5, 10))
        cx, cy = 560, 1250
        for k in range(18, 0, -1):
            r = 40 + k * 30
            col = tuple(int(v * (0.1 + 0.03 * (18 - k))) for v in (200, 170, 130))
            c.ellipse(cx, cy, r, r * 0.9, col, width=4)
        layer = Image.new("RGBA", c.img.size, (0, 0, 0, 0))
        ImageDraw.Draw(layer).ellipse(Canvas.p(cx - 30, cy - 260, cx + 70, cy + 40), fill=(0, 0, 0, 230))
        ImageDraw.Draw(layer).ellipse(Canvas.p(cx - 10, cy - 360, cx + 70, cy - 270), fill=(0, 0, 0, 230))
        c.img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(8 * SS)))
        c.glow(260, 1500, 160, (255, 190, 90), 0.6)
        stickman(c, 240, 1950, 900, face="scared", sweat=True, item=lantern, arms=((-60, 40), (60, 50)), look=0.7)
        return c

    return [b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11, b12, b13]


SCENES = {"lighthouse": lighthouse_scenes}


def main(argv=None):
    name = (argv or sys.argv[1:] or ["lighthouse"])[0]
    out = config.ASSETS / name
    out.mkdir(parents=True, exist_ok=True)
    for i, fn in enumerate(SCENES[name](), 1):
        fn().save(out / f"beat_{i:02d}.png")
        print("drew", out / f"beat_{i:02d}.png")


if __name__ == "__main__":
    sys.exit(main())
