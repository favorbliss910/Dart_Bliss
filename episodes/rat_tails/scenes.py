"""Rat Tails (Hanoi, 1902): environments, post-process looks and the 87 shots.

    python3 scenes.py OUT_DIR --times 0.5,1.8,... --size 320x568
"""
import math
import os
import random
import sys

import cairo
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'drongo'))

import render as R  # noqa: E402  (engine: Frame, Cam, cam_path, easing, captions)
from render import (Frame, Cam, cam_path, ease, ease_io, ease_out, ease_in, back_out, seg, clamp, lerp,  # noqa: E402
                    blink_at, W, H)
from chars import C, INK, src, ellipse, stick, fill_stroke, soft_ellipse, form_shade, rim, clipped, grad_fill  # noqa: E402
from env import mix as cmix  # noqa: E402
from people import (person, rat, rat_front, rat_dangle, flea, heart, star, tail_prop, scissors, coin, sack,  # noqa: E402
                    rice_pile, bucket, cage, cart, shoulder_pole, shed, manhole, _shade, PINK)

PI = math.pi

# ============================================================== cast
HERO = dict(body=C('#2f6f73'), hat='conical', tunic=True, pants=C('#1f3b40'), hair='short', hair_col=C('#2a1d14'))
CATCH2 = dict(body=C('#8a5a32'), hat='turban', hair_col=C('#3a3a46'), tunic=True, pants=C('#5a3a20'))
CATCH3 = dict(body=C('#7a6a3a'), hair='messy', hair_col=C('#1a1a1a'), tunic=True, pants=C('#4a3a20'))
OFFICIAL = dict(coat=C('#f2efe6'), hat='pith', moustache='handlebar', hair_col=C('#6a4a2a'), pants=C('#e8e2d2'))
OFFICIAL2 = dict(coat=C('#f2efe6'), hat='pith', moustache='walrus', hair_col=C('#9a8a7a'), pants=C('#e8e2d2'),
                 glasses=True)
INSPECTOR = dict(body=C('#2a3550'), hat='kepi', moustache='walrus', hair_col=C('#3a2a20'), pants=C('#1c2438'))
TOWN = [dict(body=C('#b0563a'), hat='conical', tunic=True, pants=C('#5a2e20')),
        dict(body=C('#4a6b8a'), hair='short', hair_col=C('#1a1410'), tunic=True, pants=C('#2a3a4a')),
        dict(body=C('#8a3a5a'), hat='conical', tunic=True, pants=C('#3a2030')),
        dict(body=C('#5a7a4a'), hat='turban', hair_col=C('#2a2a2a'), tunic=True, pants=C('#33402a')),
        dict(body=C('#9a7a3a'), hair='bun', hair_col=C('#1a1410'), tunic=True, pants=C('#4a3a20')),
        dict(body=C('#3a5a6a'), hat='conical', tunic=True, pants=C('#22343e'))]
STONE = C('#8c8576')
GOLD = C('#e8b53a')


def aim(x, yh, z, fy=0.42, fx=0.5, rot=0.0):
    """Camera key that puts world point (x, yh) at screen fraction (fx, fy) at zoom z."""
    return (x - (fx * W - W / 2) / z, yh - (fy * H - H / 2) / z, z, rot)


def path(u, keys, fn=ease_io):
    keys = [(k[0], *((k[1].cx, k[1].cy, k[1].z, k[1].rot) if isinstance(k[1], Cam) else k[1])) for k in keys]
    return cam_path(u, keys, fn)


def head_y(y, s, hat=False):
    return y - s * 240


# ============================================================== shared helpers (from library/scenes.py)
def dust(F, t, n=40, seed=1, area=(0, 0, W, H), col=(1, 0.95, 0.8)):
    c = F.layer(screen=True)
    rnd = random.Random(seed)
    for i in range(n):
        x = area[0] + (rnd.uniform(0, area[2]) + 8 * math.sin(t * 0.7 + i)) % area[2]
        y = area[1] + (rnd.uniform(0, area[3]) - t * rnd.uniform(4, 14)) % area[3]
        r = rnd.uniform(1, 2.6)
        soft_ellipse(c, x, y, r * 2, r * 2, col, 0.5 * (0.5 + 0.5 * math.sin(t * 2 + i)))


def grade(F, tint=(0.0, 0.0, 0.0, 0.0), vig=0.45, warm_glow=None):
    c = F.layer(screen=True)
    if warm_glow:
        x, y, r, a = warm_glow
        soft_ellipse(c, x, y, r, r, C('#ffd98a'), a)
    if tint[3] > 0:
        c.rectangle(0, 0, W, H)
        src(c, tint)
        c.fill()
    g = cairo.RadialGradient(W / 2, H * 0.47, W * 0.28, W / 2, H * 0.47, H * 0.72)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0.02, 0.02, 0.05, vig)
    c.rectangle(0, 0, W, H)
    c.set_source(g)
    c.paint()


def speech_bubble(c, x, y, k, draw=None, w=1.0):
    if k <= 0:
        return
    c.save()
    c.translate(x, y)
    c.scale(k * w, k)
    c.move_to(-90, -40)
    c.curve_to(-90, -100, 90, -100, 90, -40)
    c.curve_to(90, 10, 10, 10, -10, 8)
    c.line_to(-50, 40)
    c.line_to(-40, 4)
    c.curve_to(-90, 0, -90, -20, -90, -40)
    fill_stroke(c, (1, 1, 1), 5)
    c.scale(1 / w, 1)
    if draw:
        draw(c)
    c.restore()


def text(c, s, x, y, size, col=(1, 1, 1), outline=INK, lw=None, align='c', k=1.0, rot=0.0):
    """Bold Poppins label with an ink outline (pops in with k)."""
    if k <= 0:
        return
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(k, k)
    c.select_font_face('Poppins', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(size)
    e = c.text_extents(s)
    dx = {'c': -e.x_advance / 2, 'l': 0, 'r': -e.x_advance}[align]
    c.move_to(dx, size * 0.35)
    c.text_path(s)
    if outline is not None:
        c.set_line_width(lw or size * 0.16)
        src(c, outline)
        c.stroke_preserve()
    src(c, col)
    c.fill()
    c.restore()


def pop_in(t, t0, dur=0.22, k=2.0):
    return back_out(seg(t, t0, t0 + dur), k)


def qmark(c, x, y, k, s='?', size=90, col=(1, 1, 1)):
    text(c, s, x, y, size, col, INK, 7, k=k)


def lamp_light(c, x, y, r=320, k=1.0, col=C('#ffd98a')):
    soft_ellipse(c, x, y, r, r * 0.8, col, 0.28 * k, core=0.3)


def stink(c, x, y, t, n=3, k=1.0, col=C('#9acd5a')):
    for i in range(n):
        p = (t * 0.8 + i / n) % 1
        c.save()
        c.translate(x + (i - n / 2) * 34, y - p * 140)
        c.move_to(0, 0)
        for j in range(6):
            c.line_to(12 * math.sin(j * 1.4 + t * 5 + i), -j * 14)
        c.set_line_width(7)
        src(c, (*col[:3], k * (1 - p) * 0.9))
        c.stroke()
        c.restore()


def fly(c, x, y, t, seed=0):
    rnd = random.Random(seed)
    a = t * 6 + rnd.uniform(0, 6)
    fx, fy = x + 40 * math.cos(a) + 10 * math.sin(a * 3), y + 26 * math.sin(a * 1.3)
    ellipse(c, fx, fy, 6, 5)
    src(c, INK)
    c.fill()
    for sd in (-1, 1):
        ellipse(c, fx + sd * 5, fy - 6 - 2 * math.sin(t * 60), 5, 3, sd * 0.5)
        fill_stroke(c, (1, 1, 1, 0.8), 1.4)


def burst(c, x, y, r, k, col=(1, 1, 1), n=10, lw=4):
    """Comic action lines radiating out (the 'snip!' / impact burst)."""
    if k <= 0:
        return
    for i in range(n):
        a = i * 2 * PI / n + 0.2
        stick(c, [(x + math.cos(a) * r * 0.55 * k, y + math.sin(a) * r * 0.55 * k),
                  (x + math.cos(a) * r * k, y + math.sin(a) * r * k)], lw, (*col[:3], 1 - 0.5 * k))


def calendar_page(c, x, y, s, top, big, rot=0.0, col=C('#d6332f')):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    c.rectangle(-60, -70, 120, 140)
    fill_stroke(c, (1, 1, 1), 4)
    c.rectangle(-60, -70, 120, 36)
    fill_stroke(c, col, 4)
    text(c, top, 0, -52, 20, (1, 1, 1), None)
    text(c, big, 0, 18, 54, INK, None)
    c.restore()


def counter(c, x, y, val, size=80, k=1.0, col=GOLD, prefix='', suffix=''):
    text(c, f'{prefix}{int(val):,}{suffix}', x, y, size, col, INK, size * 0.14, k=k)


def tail_bundle(c, x, y, s=1.0, n=7, seed=0, rot=0.0):
    rnd = random.Random(seed)
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    for i in range(n):
        tail_prop(c, rnd.uniform(-10, 10), rnd.uniform(-14, 14), s * rnd.uniform(0.85, 1.1), rnd.uniform(-0.25, 0.25),
                  rnd.uniform(-0.3, 0.6))
    c.rectangle(-14 * s, -22 * s, 22 * s, 44 * s)
    fill_stroke(c, C('#c9a24a'), 3)
    c.restore()


def tail_heap(c, x, y, w, h, seed=0, n=None):
    """A mound of loose tails."""
    rnd = random.Random(seed)
    n = n or int(w * h / 700)
    for i in range(n):
        u = rnd.uniform(-0.5, 0.5)
        yy = -rnd.uniform(0, h * (1 - (2 * u) ** 2)) * (i / n) ** 0.4
        tail_prop(c, x + u * w, y + yy, rnd.uniform(0.35, 0.6), rnd.uniform(-PI, PI), rnd.uniform(-0.6, 0.6))


# ============================================================== post looks
def to_rgb(img):
    return img[..., [2, 1, 0]]


def from_rgb(img, rgb):
    img[..., 0], img[..., 1], img[..., 2] = rgb[..., 2], rgb[..., 1], rgb[..., 0]
    return img


def _vig(h, w, k):
    yy, xx = np.mgrid[0:h, 0:w]
    d = ((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2
    return (1 - k * np.clip(d, 0, 1.4))[..., None]


def vintage_post(amount=1.0, scratches=True):
    """Old silent-film look: sepia, gate flicker, dust specks and vertical scratches."""
    def post(img, T):
        rgb = to_rgb(img) / 255.0
        lum = rgb @ np.array([0.3, 0.59, 0.11], np.float32)
        a = amount(T) if callable(amount) else amount
        sep = np.stack([0.12 + lum * 0.95, 0.07 + lum * 0.80, 0.03 + lum * 0.58], -1)
        out = rgb * (1 - a) + sep * a
        h, w = lum.shape
        rng = np.random.default_rng(int(T * 24))
        out *= 1 + a * 0.06 * (rng.random() - 0.5)
        out *= _vig(h, w, 0.55 * a + 0.1)
        out = np.clip(out * 255, 0, 255)
        if scratches and a > 0.3:
            for _ in range(rng.integers(1, 4)):
                x = rng.integers(0, w)
                out[:, x:x + max(1, int(R.SS)), :] *= 0.55
            for _ in range(rng.integers(3, 9)):
                y, x = rng.integers(0, h - 8), rng.integers(0, w - 8)
                r = int(rng.integers(1, 4) * R.SS)
                out[y:y + r, x:x + r, :] = 30 if rng.random() < 0.6 else 230
        return from_rgb(img, out)
    return post


def isolate_red(keep=1.0, tint=(0.62, 0.68, 0.8)):
    """Everything grey (cool) except saturated reds."""
    def post(img, T):
        rgb = to_rgb(img) / 255.0
        lum = rgb @ np.array([0.3, 0.59, 0.11], np.float32)
        grey = lum[..., None] * np.array(tint, np.float32) + 0.04
        r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
        m = np.clip((r - np.maximum(g, b) - 0.15) * 4, 0, 1)[..., None]
        k = keep(T) if callable(keep) else keep
        out = rgb * (1 - k) + (grey * (1 - m) + rgb * m) * k
        return from_rgb(img, np.clip(out * 255, 0, 255))
    return post


# ============================================================== environments
SKIES = {
    'day': (C('#7fb6d6'), C('#bfdbe3'), C('#f6e2b0')),
    'dusk': (C('#3a3f72'), C('#c46a63'), C('#f5b46a')),
    'night': (C('#060b1e'), C('#13234a'), C('#2c4266')),
    'sepia': (C('#9fb8c6'), C('#d5dcd2'), C('#f0e2c0')),
}


def sky(F, tone='day', t=0.0, moon=False, sun=None):
    c = F.layer(screen=True)
    top, mid, hor = SKIES[tone]
    hy = F.horizon_y()
    g = cairo.LinearGradient(0, hy - 1300, 0, hy)
    g.add_color_stop_rgb(0, *top)
    g.add_color_stop_rgb(0.6, *mid)
    g.add_color_stop_rgb(1, *hor)
    c.rectangle(0, 0, W, H)
    c.set_source(g)
    c.fill()
    c = F.layer(p=0.05)
    if tone == 'night':
        rnd = random.Random(3)
        for i in range(110):
            x, y = rnd.uniform(-900, 900), rnd.uniform(-1500, -150)
            r = rnd.uniform(0.6, 1.9)
            ellipse(c, x, y, r, r)
            src(c, (1, 1, 1, 0.6 + 0.3 * math.sin(t * 2 + i)))
            c.fill()
    if moon:
        soft_ellipse(c, 150, -760, 170, 170, C('#cfe0ff'), 0.25)
        ellipse(c, 150, -760, 50, 50)
        fill_stroke(c, C('#f3f1e0'), 3)
        ellipse(c, 132, -770, 10, 8)
        src(c, C('#d9d6c0'))
        c.fill()
    if sun:
        soft_ellipse(c, sun[0], sun[1], 240, 240, C('#ffd98a'), 0.4)
        ellipse(c, sun[0], sun[1], 54, 54)
        fill_stroke(c, C('#fff0c0'), 0, C('#fff0c0'))
    if tone in ('day', 'dusk', 'sepia'):  # soft clouds
        for (x, y, s) in ((-300, -720, 1.0), (260, -880, 0.8), (520, -640, 0.7)):
            for dx, dy, r in ((0, 0, 60), (55, 10, 45), (-55, 12, 42), (25, -28, 40)):
                soft_ellipse(c, x + dx * s, y + dy * s, r * s * 1.2, r * s, (1, 1, 1), 0.5 if tone != 'dusk' else 0.25)


def tree_round(c, x, y, s, col, trunk=C('#4a3626')):
    stick(c, [(x, y), (x + 4 * s, y - 90 * s)], 14 * s, trunk)
    for dx, dy, r in ((0, -150, 80), (-60, -120, 60), (60, -118, 62), (-30, -190, 55), (36, -186, 56)):
        ellipse(c, x + dx * s, y + dy * s, r * s, r * s * 0.85)
        src(c, col)
        c.fill()


def far_city(F, tone='day', blur=2.5, pagoda=True):
    """Distant Hanoi skyline: tiled roofs, tamarind trees, a cathedral spire pair."""
    c = F.layer(p=0.18, blur=blur)
    base = {'day': C('#8aa0a8'), 'dusk': C('#6a5a78'), 'night': C('#1a2440'), 'sepia': C('#a8a89a')}[tone]
    rnd = random.Random(9)
    x = -1400
    while x < 1400:
        w = rnd.uniform(60, 130)
        h = rnd.uniform(60, 160)
        c.move_to(x, 0)
        c.line_to(x, -h)
        c.line_to(x + w * 0.5, -h - 26)
        c.line_to(x + w, -h)
        c.line_to(x + w, 0)
        c.close_path()
        src(c, base)
        c.fill()
        x += w - 6
    if pagoda:  # two square cathedral towers on the far right, a tiered pagoda roof on the left
        for tx in (360, 450):
            c.rectangle(tx, -330, 60, 330)
            src(c, cmix(base, (0, 0, 0), 0.08))
            c.fill()
            c.move_to(tx - 6, -330)
            c.line_to(tx + 30, -380)
            c.line_to(tx + 66, -330)
            c.close_path()
            c.fill()
        for k in range(3):
            yy = -150 - k * 60
            ww = 150 - k * 34
            c.move_to(-520 - ww, yy + 14)
            c.curve_to(-520 - ww * 0.4, yy, -520 + ww * 0.4, yy, -520 + ww, yy + 14)
            c.line_to(-520 + ww * 0.6, yy - 26)
            c.line_to(-520 - ww * 0.6, yy - 26)
            c.close_path()
            src(c, cmix(base, (0, 0, 0), 0.12))
            c.fill()
        c.rectangle(-560, -150, 80, 150)
        c.fill()
    tcol = cmix(base, C('#3a6a3a'), 0.35)
    for i in range(9):
        tree_round(c, -1200 + i * 300 + rnd.uniform(-60, 60), 10, rnd.uniform(0.5, 0.8), tcol, cmix(base, (0, 0, 0), 0.2))


def tube_house(c, x, y, w, h, seed, tone='day', lit=0.0):
    """Old Quarter shophouse: narrow facade, curved terracotta roof, wooden shutters, a lantern."""
    rnd = random.Random(seed)
    night = tone == 'night'
    wall = rnd.choice([C('#e6cf9a'), C('#d9b07a'), C('#cfc0a0'), C('#e2c08a')])
    if night:
        wall = cmix(wall, C('#1a2448'), 0.65)
    c.rectangle(x, y - h, w, h)
    form_shade(c, lambda: c.rectangle(x, y - h, w, h), wall, _shade(wall, 1.12), _shade(wall, 0.72), (x, y - h, x + w, y))
    c.rectangle(x, y - h, w, h)
    c.set_line_width(4)
    src(c, INK)
    c.stroke()
    roof = C('#b4553a') if not night else C('#4a2a34')
    c.move_to(x - 16, y - h + 6)
    c.curve_to(x + w * 0.3, y - h - 8, x + w * 0.7, y - h - 8, x + w + 16, y - h + 6)
    c.line_to(x + w + 4, y - h - 40)
    c.line_to(x - 4, y - h - 40)
    c.close_path()
    fill_stroke(c, roof, 4)
    for k in range(1, 7):
        stick(c, [(x - 4 + k * (w + 8) / 7, y - h - 38), (x - 6 + k * (w + 8) / 7, y - h + 2)], 1.6, _shade(roof, 0.6))
    # shutters / shop opening
    c.rectangle(x + w * 0.14, y - h * 0.5, w * 0.72, h * 0.5)
    shop = C('#3a2416') if not lit else C('#ffd98a')
    if night and not lit:
        shop = C('#120c10')
    fill_stroke(c, shop, 3.6)
    for k in range(1, 4):
        stick(c, [(x + w * 0.14 + k * w * 0.18, y - h * 0.5), (x + w * 0.14 + k * w * 0.18, y)], 2.4,
              C('#6a4426') if not night else C('#2a1a20'))
    c.rectangle(x + w * 0.25, y - h * 0.86, w * 0.5, h * 0.22)
    fill_stroke(c, C('#4a6a5a') if not night else C('#1a2a2a'), 3.4)
    if rnd.random() < 0.6:  # red paper lantern
        lx = x + w * rnd.uniform(0.25, 0.75)
        stick(c, [(lx, y - h * 0.56), (lx, y - h * 0.5)], 2)
        if night:
            soft_ellipse(c, lx, y - h * 0.48 + 12, 60, 60, C('#ff8a4a'), 0.4)
        ellipse(c, lx, y - h * 0.48 + 12, 14, 18)
        fill_stroke(c, C('#d6332f'), 3)


def villa(c, x, y, w, h, seed, tone='day', lit=0.0):
    """French Quarter villa: ochre stucco, tall green-shuttered windows, balcony, cornice."""
    rnd = random.Random(seed)
    night = tone == 'night'
    wall = rnd.choice([C('#e8c65a'), C('#f0d27a'), C('#e6d3a8'), C('#efe2c4')])
    if night:
        wall = cmix(wall, C('#1a2448'), 0.68)
    c.rectangle(x, y - h, w, h)
    form_shade(c, lambda: c.rectangle(x, y - h, w, h), wall, _shade(wall, 1.1), _shade(wall, 0.72), (x, y - h, x + w, y))
    c.rectangle(x, y - h, w, h)
    c.set_line_width(4)
    src(c, INK)
    c.stroke()
    c.rectangle(x - 10, y - h - 22, w + 20, 24)
    fill_stroke(c, _shade(wall, 1.15), 4)
    c.move_to(x - 4, y - h - 22)
    c.line_to(x + w / 2, y - h - 70)
    c.line_to(x + w + 4, y - h - 22)
    c.close_path()
    fill_stroke(c, C('#a84a34') if not night else C('#3a2430'), 4)
    cols = max(2, int(w / 90))
    for row in range(2):
        for k in range(cols):
            wx = x + (k + 0.5) * w / cols - 24
            wy = y - h + 40 + row * h * 0.46
            c.rectangle(wx, wy, 48, h * 0.3)
            lit_k = lit and rnd.random() < 0.6
            fill_stroke(c, C('#ffd98a') if lit_k else (C('#2a3a3a') if not night else C('#0c1418')), 3.4)
            if lit_k:
                soft_ellipse(c, wx + 24, wy + h * 0.15, 60, 70, C('#ffd98a'), 0.35)
            for sd in (-1, 1):  # open green shutters
                c.rectangle(wx + (48 if sd > 0 else -22), wy, 22, h * 0.3)
                fill_stroke(c, C('#3f7a5a') if not night else C('#1a3028'), 3)
                for j in range(1, 6):
                    stick(c, [(wx + (48 if sd > 0 else -22) + 3, wy + j * h * 0.05),
                              (wx + (48 if sd > 0 else -22) + 19, wy + j * h * 0.05)], 1.4, INK)
        if row == 0:  # wrought-iron balcony
            stick(c, [(x + 10, y - h + 40 + h * 0.3 + 6), (x + w - 10, y - h + 40 + h * 0.3 + 6)], 4)
            for j in range(int(w / 14)):
                stick(c, [(x + 12 + j * 14, y - h + 40 + h * 0.3 + 6), (x + 12 + j * 14, y - h + 40 + h * 0.3 - 24)], 1.6)
            stick(c, [(x + 10, y - h + 40 + h * 0.3 - 24), (x + w - 10, y - h + 40 + h * 0.3 - 24)], 3)


def gas_lamp(c, x, y, s=1.0, on=False):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    stick(c, [(0, 0), (0, -330)], 9)
    stick(c, [(-14, -40), (14, -40)], 6)
    if on:
        soft_ellipse(c, 0, -340, 150, 150, C('#ffd98a'), 0.45)
        soft_ellipse(c, 0, 0, 150, 30, C('#ffd98a'), 0.35)
    c.move_to(-20, -330)
    c.line_to(-26, -380)
    c.line_to(26, -380)
    c.line_to(20, -330)
    c.close_path()
    fill_stroke(c, C('#fff1c0') if on else C('#cfd8d0'), 4)
    c.move_to(-32, -380)
    c.line_to(0, -402)
    c.line_to(32, -380)
    c.close_path()
    fill_stroke(c, C('#2a2a2a'), 4)
    c.restore()


def street(F, t, tone='day', quarter='old', blur_bg=3.0, lit=False, x0=-1500, x1=1500, seed=0, ground_blur=0.0,
           far=True):
    """A Hanoi street: sky, distant skyline, a row of facades at y=-40 and the road at y=0."""
    sky(F, tone, t, moon=(tone == 'night'))
    if far:
        far_city(F, tone, blur=blur_bg + 1.5)
    c = F.layer(p=0.55, blur=blur_bg)
    x = x0
    k = 0
    rnd = random.Random(seed)
    while x < x1:
        if quarter == 'old':
            w = rnd.uniform(110, 150)
            tube_house(c, x, -30, w, rnd.uniform(260, 340), seed * 100 + k, tone, lit=lit and rnd.random() < 0.5)
        else:
            w = rnd.uniform(230, 300)
            villa(c, x, -30, w, rnd.uniform(330, 400), seed * 100 + k, tone, lit=lit)
        x += w + (6 if quarter == 'old' else 60)
        if quarter != 'old':
            tree_round(c, x - 30, -26, 0.9, C('#3f6f3a') if tone != 'night' else C('#14222a'),
                       C('#4a3626') if tone != 'night' else C('#14141c'))
        k += 1
    c = F.layer(p=1.0, blur=ground_blur)
    road = {'day': C('#c9a878'), 'dusk': C('#a07a64'), 'night': C('#2a2c3a'), 'sepia': C('#c9b898')}[tone]
    g = cairo.LinearGradient(0, -40, 0, 700)
    g.add_color_stop_rgb(0, *_shade(road, 0.82))
    g.add_color_stop_rgb(1, *_shade(road, 1.08))
    c.rectangle(-4000, -40, 8000, 3000)
    c.set_source(g)
    c.fill()
    stick(c, [(-4000, -36), (4000, -36)], 10, _shade(road, 0.7))
    rnd = random.Random(seed + 5)
    for i in range(70):
        y = (i / 70) ** 1.5 * 700
        xx = rnd.uniform(-1600, 1600)
        stick(c, [(xx, y), (xx + lerp(20, 120, y / 700), y + 2)], lerp(1.5, 4, y / 700), (*_shade(road, 0.75), 0.6))
    return c


def tunnel(F, t, light=1.0, clean=1.0, water=True, blur_far=2.0, vp=(0, -260), rats=None, sparkle=0.0, dark=0.0):
    """One-point-perspective stone sewer tunnel. rats: list of (depth 0..1, side -1/1, kw)."""
    c = F.layer(screen=True)
    src(c, C('#120f0c'))
    c.paint()
    c = F.layer(p=1.0)
    vx, vy = vp
    N = 9
    stone = cmix(STONE, C('#4a4a3a'), 1 - clean)
    for k in range(N, 0, -1):  # far -> near arch rings
        d0 = 1.0 / (0.6 + k * 0.55)
        d1 = 1.0 / (0.6 + (k - 1) * 0.55)
        R0, R1 = 900 * d0, 900 * d1
        lite = clamp(1.2 * d1) * light
        col = cmix(C('#1a1612'), stone, lite)

        def ring(Rr):
            c.move_to(vx - Rr, vy + Rr * 0.9)
            c.line_to(vx - Rr, vy)
            c.arc(vx, vy, Rr, PI, 2 * PI)
            c.line_to(vx + Rr, vy + Rr * 0.9)
        ring(R1)
        c.line_to(vx + R0, vy + R0 * 0.9)
        c.line_to(vx + R0, vy)
        c.arc_negative(vx, vy, R0, 2 * PI, PI)
        c.line_to(vx - R0, vy + R0 * 0.9)
        c.close_path()
        src(c, col)
        c.fill()
        # stone joints on this band
        for j in range(14):
            a = PI + j * PI / 13
            stick(c, [(vx + math.cos(a) * R0, vy + math.sin(a) * R0), (vx + math.cos(a) * R1, vy + math.sin(a) * R1)],
                  2.2 * d1, (0, 0, 0, 0.35))
        ring(R1)
        c.set_line_width(4 * d1 + 1)
        src(c, (0, 0, 0, 0.55))
        c.stroke()
        if clean > 0.5 and sparkle > 0 and k % 2 == 0:
            star(c, vx - R1 * 0.7, vy - R1 * 0.55, 10 * d1 * sparkle * (0.6 + 0.4 * math.sin(t * 6 + k)), (1, 1, 1), 0)
    # far opening glow
    soft_ellipse(c, vx, vy + 20, 90, 70, C('#ffe9b0') if light > 0.5 else C('#3a3a4a'), 0.5 * light)
    if water:  # channel down the middle
        c.move_to(vx - 40, vy + 70)
        c.line_to(vx + 40, vy + 70)
        c.line_to(vx + 520, vy + 1200)
        c.line_to(vx - 520, vy + 1200)
        c.close_path()
        g = cairo.LinearGradient(0, vy + 70, 0, vy + 1200)
        wc = cmix(C('#3a5a5a'), C('#4a4a2a'), 1 - clean)
        g.add_color_stop_rgb(0, *cmix(wc, C('#000000'), 0.5))
        g.add_color_stop_rgb(1, *wc)
        c.set_source(g)
        c.fill()
        for j in range(16):
            yy = vy + 80 + ((j / 16 + t * 0.15) % 1) ** 1.6 * 1100
            ww = (yy - vy) * 0.3
            stick(c, [(vx - ww, yy), (vx + ww * 0.3, yy + 3)], 1 + (yy - vy) / 300, (1, 1, 1, 0.12 + 0.1 * clean))
    if rats:
        for (dep, side, kw) in rats:
            Rr = 900 / (0.6 + dep * 0.55 * N)
            s = Rr / 900 * 1.6
            rat(c, vx + side * (Rr * 0.72), vy + Rr * 0.86, s, flip=side > 0, **kw)
    if dark > 0:
        c2 = F.layer(screen=True)
        c2.rectangle(0, 0, W, H)
        src(c2, (0, 0, 0, dark))
        c2.fill()
    return c


def soil_cutaway(c, x0=-1400, x1=1400, y0=0, depth=1200, tone='day'):
    """Underground cross-section below a street line at y0."""
    c.rectangle(x0, y0, x1 - x0, depth)
    g = cairo.LinearGradient(0, y0, 0, y0 + depth)
    g.add_color_stop_rgb(0, *C('#7a5a3a'))
    g.add_color_stop_rgb(1, *C('#3a2618'))
    c.set_source(g)
    c.fill()
    rnd = random.Random(4)
    for i in range(90):
        ellipse(c, rnd.uniform(x0, x1), y0 + rnd.uniform(20, depth), rnd.uniform(4, 12), rnd.uniform(3, 8))
        src(c, (0, 0, 0, 0.18))
        c.fill()
    stick(c, [(x0, y0), (x1, y0)], 6)


def tunnel_section(c, x, y, r, t=0.0, rats=0, seed=0, glow=0.0, full=0.0):
    """Circular sewer in cross-section (stone ring, water at the bottom, optional rats)."""
    if glow > 0:
        soft_ellipse(c, x, y, r * 1.6, r * 1.4, C('#ffd98a'), 0.35 * glow)
    ellipse(c, x, y, r + 22, r + 22)
    fill_stroke(c, STONE, 5)
    for j in range(16):
        a = j * PI / 8
        stick(c, [(x + math.cos(a) * r, y + math.sin(a) * r), (x + math.cos(a) * (r + 22), y + math.sin(a) * (r + 22))], 2.4)
    ellipse(c, x, y, r, r)
    src(c, C('#1e1a16'))
    c.fill()
    clipped(c, lambda: ellipse(c, x, y, r, r), lambda: (c.rectangle(x - r, y + r * 0.45, 2 * r, r),
                                                          src(c, C('#3a5a5a')), c.fill()))
    rnd = random.Random(seed)
    for k in range(rats):
        u = rnd.uniform(-0.6, 0.6) if full <= 0 else (k / max(1, rats - 1) - 0.5) * 1.3
        yy = y + r * 0.45 - (k % 3) * r * 0.22 * full
        rat(c, x + u * r, yy, r / 300 * rnd.uniform(0.8, 1.1), flip=rnd.random() < 0.5, step=t * 12 + k,
            blink=blink_at(t, 2.3, k), shadow=False, tail_wave=t * 4 + k)
    ellipse(c, x, y, r, r)
    c.set_line_width(5)
    src(c, INK)
    c.stroke()


def office(F, t, blur=4.0, window=True, fan=True, wall=C('#c9d3b8')):
    """Colonial health office: two-tone wall, shuttered window with light shafts, ceiling fan."""
    c = F.layer(p=0.5, blur=blur)
    c.rectangle(-3000, -3000, 6000, 3000)
    g = cairo.LinearGradient(0, -1200, 0, 0)
    g.add_color_stop_rgb(0, *_shade(wall, 0.8))
    g.add_color_stop_rgb(1, *wall)
    c.set_source(g)
    c.fill()
    c.rectangle(-3000, -260, 6000, 260)
    src(c, C('#5a3e2a'))
    c.fill()
    stick(c, [(-3000, -262), (3000, -262)], 8, C('#3a2618'))
    if window:
        for wx in (-430, 330):
            c.rectangle(wx, -820, 170, 380)
            fill_stroke(c, C('#f8f0d0'), 6)
            for sd in (-1, 1):
                c.rectangle(wx + (170 if sd > 0 else -80), -820, 80, 380)
                fill_stroke(c, C('#3f7a5a'), 5)
                for j in range(1, 12):
                    stick(c, [(wx + (170 if sd > 0 else -80) + 6, -820 + j * 32), (wx + (170 if sd > 0 else -80) + 74, -820 + j * 32)],
                          2, INK)
            stick(c, [(wx + 85, -820), (wx + 85, -440)], 5)
        # plaque
        c.rectangle(-120, -760, 240, 70)
        fill_stroke(c, C('#e8dcc0'), 5)
        text(c, 'HYGIÈNE', 0, -726, 34, C('#3a2a1a'), None)
    if fan:
        c2 = F.layer(p=0.6, blur=blur * 0.5)
        stick(c2, [(0, -1400), (0, -980)], 6)
        for k in range(4):
            a = t * 9 + k * PI / 2
            ellipse(c2, 110 * math.cos(a), -970 + 10 * math.sin(a), 110, 16, 0)
            fill_stroke(c2, C('#5a3e2a'), 3)
    c3 = F.layer(screen=True)
    if window:
        for i in range(3):  # light shafts
            c3.move_to(W * (0.05 + i * 0.07), 0)
            c3.line_to(W * (0.25 + i * 0.1), 0)
            c3.line_to(W * (0.7 + i * 0.1), H)
            c3.line_to(W * (0.4 + i * 0.1), H)
            c3.close_path()
            src(c3, (1, 0.95, 0.8, 0.06))
            c3.fill()
    c = F.layer(p=1.0)
    c.rectangle(-3000, 0, 6000, 3000)
    g = cairo.LinearGradient(0, 0, 0, 800)
    g.add_color_stop_rgb(0, *C('#8a6a4a'))
    g.add_color_stop_rgb(1, *C('#5a4030'))
    c.set_source(g)
    c.fill()
    for i in range(-20, 21):
        stick(c, [(i * 90, 0), (i * 200, 800)], 2, (0, 0, 0, 0.18))
    return c


def desk(c, x, y, w=520, h=230, col=C('#6a4426')):
    c.rectangle(x - w / 2, y, w, h)
    form_shade(c, lambda: c.rectangle(x - w / 2, y, w, h), col, _shade(col, 1.35), _shade(col, 0.55),
               (x - w / 2, y, x + w / 2, y + h))
    c.rectangle(x - w / 2, y, w, h)
    c.set_line_width(5)
    src(c, INK)
    c.stroke()
    c.rectangle(x - w / 2 - 14, y - 16, w + 28, 22)
    fill_stroke(c, _shade(col, 1.2), 5)


def ledger(c, x, y, s=1.0, rows=6, ticks=0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.rectangle(-120, -70, 240, 140)
    fill_stroke(c, C('#f4ecd4'), 4)
    stick(c, [(0, -70), (0, 70)], 3)
    for i in range(rows):
        stick(c, [(-108, -50 + i * 20), (-14, -50 + i * 20)], 1.6, C('#7a8aa0'))
        stick(c, [(14, -50 + i * 20), (108, -50 + i * 20)], 1.6, C('#7a8aa0'))
    for i in range(ticks):
        xx = 20 + (i % 5) * 14
        stick(c, [(xx, -46 + (i // 5) * 20), (xx + 4, -34 + (i // 5) * 20)], 2.6, C('#3a2a6a'))
    c.restore()


def fields(F, t, tone='day', blur_far=3.0, dike=True, path_k=1.0, palms=True):
    """Red River delta rice paddies: flooded terraces reflecting the sky, a raised dike path."""
    sky(F, tone, t, moon=(tone == 'night'), sun=(-260, -520) if tone == 'dusk' else None)
    night = tone == 'night'
    c = F.layer(p=0.15, blur=blur_far + 2)
    hill = {'day': C('#7a9a9a'), 'dusk': C('#6a4e6e'), 'night': C('#16223a'), 'sepia': C('#a8a890')}[tone]
    rnd = random.Random(2)
    for k in range(7):  # distant limestone hills
        x = -1300 + k * 420 + rnd.uniform(-80, 80)
        hh = rnd.uniform(160, 300)
        c.move_to(x - 200, 0)
        c.curve_to(x - 150, -hh, x + 150, -hh, x + 200, 0)
        c.close_path()
        src(c, hill)
        c.fill()
    c = F.layer(p=0.35, blur=blur_far)
    tcol = C('#3a6a3a') if not night else C('#0e1a1e')
    if palms:
        for k in range(10):  # bamboo clumps + areca palms on the horizon
            x = -1500 + k * 330 + rnd.uniform(-60, 60)
            for j in range(5):
                stick(c, [(x + j * 8, 0), (x + j * 8 + (j - 2) * 14, -160 - j * 10)], 4, tcol)
                for q in range(4):
                    yy = -60 - q * 30 - j * 4
                    stick(c, [(x + j * 8 + (j - 2) * 4 * q / 2, yy), (x + j * 8 + (j - 2) * 6 + 30 * (1 if j % 2 else -1), yy - 10)], 3,
                          tcol)
    c = F.layer(p=1.0)
    water = {'day': C('#9ec9d6'), 'dusk': C('#e2a07a'), 'night': C('#1c2c4a'), 'sepia': C('#d8d0b8')}[tone]
    green = C('#6fae4a') if not night else C('#1e3a2a')
    c.rectangle(-4000, -10, 8000, 4000)
    src(c, cmix(green, (0, 0, 0), 0.15))
    c.fill()
    for i in range(16):  # paddies: rows of flooded plots, perspective stripes
        y0 = (i / 16) ** 1.7 * 1100
        y1 = ((i + 1) / 16) ** 1.7 * 1100
        c.rectangle(-4000, y0 + 2, 8000, max(2, (y1 - y0) - 6))
        g = cairo.LinearGradient(0, y0, 0, y1)
        g.add_color_stop_rgb(0, *cmix(water, (1, 1, 1), 0.15))
        g.add_color_stop_rgb(1, *water)
        c.set_source(g)
        c.fill()
        # rows of seedlings
        sp = lerp(14, 60, i / 16)
        n = int(5000 / sp)
        for j in range(0, n, 2):
            xx = -2500 + j * sp + (i % 2) * sp / 2
            hh = lerp(4, 22, i / 16)
            stick(c, [(xx, y1 - 4), (xx - hh * 0.2, y1 - 4 - hh)], lerp(1, 3, i / 16), green)
    if dike:  # raised earth path running from the foreground to the shed on the horizon
        c.move_to(-60 * path_k, -6)
        c.line_to(60 * path_k, -6)
        c.line_to(700, 1400)
        c.line_to(-260, 1400)
        c.close_path()
        dc = C('#b48a5a') if not night else C('#3a3040')
        g = cairo.LinearGradient(0, 0, 0, 1200)
        g.add_color_stop_rgb(0, *_shade(dc, 0.85))
        g.add_color_stop_rgb(1, *dc)
        c.set_source(g)
        c.fill_preserve()
        c.set_line_width(4)
        src(c, INK)
        c.stroke()
    return c


def shed_interior(F, t, light=1.0, blur=0.0):
    c = F.layer(p=0.6, blur=blur)
    c.rectangle(-3000, -3000, 6000, 3000)
    g = cairo.LinearGradient(0, -1200, 0, 0)
    g.add_color_stop_rgb(0, *C('#2a1a10'))
    g.add_color_stop_rgb(1, *C('#5a3a22'))
    c.set_source(g)
    c.fill()
    for i in range(-20, 21):
        stick(c, [(i * 70, -3000), (i * 70, 0)], 3, (0, 0, 0, 0.35))
    c = F.layer(p=1.0)
    c.rectangle(-3000, 0, 6000, 3000)
    src(c, C('#3a2a1a'))
    c.fill()
    for i in range(12):
        ellipse(c, random.Random(i).uniform(-600, 600), random.Random(i + 9).uniform(20, 400), 6, 3)
        src(c, C('#efe6cf'))
        c.fill()
    return c


def cage_wall(c, x0, y0, cols, rows, t, cw=150, ch=112, seed=0, look=(0, 0)):
    rnd = random.Random(seed)
    for r in range(rows):
        for k in range(cols):
            cage(c, x0 + k * (cw + 6), y0 - r * (ch + 8), cw, ch, rats=rnd.choice((1, 2, 2, 3)), t=t, seed=seed + r * 50 + k,
                 look=look)
        c.rectangle(x0 - 10, y0 - r * (ch + 8) - 2, cols * (cw + 6) + 14, 10)
        fill_stroke(c, C('#7a5432'), 3)


def paper_bg(F, col=C('#efe4c8'), lines=True):
    c = F.layer(screen=True)
    src(c, col)
    c.paint()
    rnd = random.Random(1)
    for i in range(160):
        soft_ellipse(c, rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(10, 60), rnd.uniform(10, 60), C('#c9b48a'), 0.08)
    if lines:
        for i in range(30):
            stick(c, [(0, 40 + i * 40), (W, 40 + i * 40)], 1.2, C('#9fb4cc', 0.5))


def chalkboard(F, t):
    c = F.layer(p=0.6, blur=1.5)
    c.rectangle(-3000, -3000, 6000, 6000)
    src(c, C('#c9d3b8'))
    c.fill()
    c.rectangle(-420, -900, 840, 620)
    fill_stroke(c, C('#6a4426'), 10)
    c.rectangle(-396, -876, 792, 572)
    g = cairo.LinearGradient(-400, -880, 400, -300)
    g.add_color_stop_rgb(0, *C('#2f4a3a'))
    g.add_color_stop_rgb(1, *C('#1e3228'))
    c.set_source(g)
    c.fill()
    return c


def chalk(c, s, x, y, size, k=1.0, col=(0.95, 0.95, 0.9)):
    """Chalk handwriting: text revealed left-to-right by k."""
    if k <= 0:
        return
    c.save()
    c.select_font_face('Poppins', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(size)
    e = c.text_extents(s)
    c.rectangle(x - 4, y - size, (e.x_advance + 8) * k, size * 1.5)
    c.clip()
    c.move_to(x, y)
    c.text_path(s)
    src(c, (*col[:3], 0.9))
    c.fill()
    c.restore()


def market(F, t, blur=3.0):
    street(F, t, 'day', 'old', blur_bg=blur, seed=3)
    c = F.layer(p=0.8, blur=blur * 0.6)
    # awning over a rice stall
    c.move_to(-420, -560)
    c.line_to(420, -560)
    c.line_to(460, -470)
    c.line_to(-460, -470)
    c.close_path()
    fill_stroke(c, C('#c0453c'), 5)
    for k in range(9):
        c.move_to(-460 + k * 102, -470)
        c.line_to(-460 + k * 102 + 51, -470)
        c.line_to(-420 + k * 93 + 46, -560)
        c.line_to(-420 + k * 93, -560)
        c.close_path()
        src(c, C('#f0e6d0'))
        c.fill()
    stick(c, [(-430, -470), (-430, 0)], 8, C('#6a4426'))
    stick(c, [(430, -470), (430, 0)], 8, C('#6a4426'))
    return c


def basket(c, x, y, w=160, fill_rice=True):
    if fill_rice:
        rice_pile(c, x, y - 60, w * 0.9, 70, int(x))
    c.move_to(x - w / 2, y - 64)
    c.line_to(x + w / 2, y - 64)
    c.line_to(x + w * 0.4, y)
    c.line_to(x - w * 0.4, y)
    c.close_path()
    fill_stroke(c, C('#c49a5a'), 4.4)
    for k in range(4):
        stick(c, [(x - w * 0.48 + k * 2, y - 52 + k * 14), (x + w * 0.48 - k * 2, y - 52 + k * 14)], 1.8, C('#8a6a3a'))


def garden(F, t, tone='day'):
    sky(F, tone, t)
    c = F.layer(p=0.3, blur=4)
    for k in range(8):
        tree_round(c, -1100 + k * 320, 0, 0.9, C('#5a8a4a'))
    c = F.layer(p=1.0)
    c.rectangle(-3000, 0, 6000, 3000)
    g = cairo.LinearGradient(0, 0, 0, 900)
    g.add_color_stop_rgb(0, *C('#6a4a2e'))
    g.add_color_stop_rgb(1, *C('#4a3020'))
    c.set_source(g)
    c.fill()
    stick(c, [(-3000, 2), (3000, 2)], 8, C('#5a8a3a'))
    return c


def weed(c, x, y, s=1.0, up=0.0, roots=True, sprout=1.0, face=True, t=0.0):
    """A cartoon weed with a smug face; up lifts it out of the soil (roots stay when roots=True)."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    if roots:
        for a in (-0.8, -0.3, 0.2, 0.7):
            c.move_to(0, 0)
            c.curve_to(40 * a, 40, 80 * a, 70, 110 * a, 120 + 20 * abs(a))
            c.set_line_width(5)
            src(c, C('#e8d6a8'))
            c.stroke()
    c.translate(0, -up * 160)
    k = sprout
    stick(c, [(0, 0), (0, -100 * k)], 7, C('#3f8a3a'))
    for sd in (-1, 1):
        c.move_to(0, -50 * k)
        c.curve_to(sd * 50 * k, -90 * k, sd * 80 * k, -60 * k, sd * 70 * k, -30 * k)
        c.curve_to(sd * 40 * k, -40 * k, sd * 20 * k, -40 * k, 0, -50 * k)
        fill_stroke(c, C('#5fae4a'), 3.6)
    if face and k > 0.6:
        ellipse(c, 0, -120 * k, 26 * k, 24 * k)
        fill_stroke(c, C('#8fd06a'), 3.6)
        for sx in (-8, 8):
            ellipse(c, sx * k, -124 * k, 6 * k, 6 * k)
            fill_stroke(c, (1, 1, 1), 2)
            ellipse(c, sx * k + 1, -124 * k, 2.4 * k, 2.4 * k)
            src(c, INK)
            c.fill()
        c.new_path()
        c.arc(0, -114 * k, 7 * k, 0.2 * PI, 0.8 * PI)
        c.set_line_width(2.4)
        src(c, INK)
        c.stroke()
    if up > 0 and not roots:
        for a in (-0.5, 0, 0.5):
            stick(c, [(0, 0), (30 * a, 30)], 3, C('#e8d6a8'))
    c.restore()


def vault(c, x, y, s=1.0, open_k=0.0, t=0.0):
    """Round bank-vault door with spokes; open_k swings it aside to reveal gold."""
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    ellipse(c, 0, 0, 300, 300)
    fill_stroke(c, C('#3a3d45'), 8)
    ellipse(c, 0, 0, 260, 260)
    src(c, C('#1a1208'))
    c.fill()
    if open_k > 0:
        soft_ellipse(c, 0, 40, 300, 240, C('#ffd23f'), 0.55 * open_k)
        for k in range(14):
            rnd = random.Random(k)
            coin(c, rnd.uniform(-180, 180), rnd.uniform(40, 200), 30, 0, '', edge=rnd.uniform(0.3, 1))
    c.save()
    c.translate(-520 * ease_io(open_k), 0)
    c.scale(1 - 0.55 * open_k, 1)
    ellipse(c, 0, 0, 262, 262)
    form_shade(c, lambda: ellipse(c, 0, 0, 262, 262), C('#9aa0aa'), C('#d8dde4'), C('#5a5f68'), (-262, -262, 262, 262))
    ellipse(c, 0, 0, 262, 262)
    c.set_line_width(8)
    src(c, INK)
    c.stroke()
    for k in range(10):
        a = k * PI / 5
        ellipse(c, 220 * math.cos(a), 220 * math.sin(a), 14, 14)
        fill_stroke(c, C('#c0c4cc'), 4)
    for k in range(3):
        a = k * PI / 3 + t * 0.6
        stick(c, [(-110 * math.cos(a), -110 * math.sin(a)), (110 * math.cos(a), 110 * math.sin(a))], 14)
        stick(c, [(-110 * math.cos(a), -110 * math.sin(a)), (110 * math.cos(a), 110 * math.sin(a))], 8, C('#c9a24a'))
    ellipse(c, 0, 0, 40, 40)
    fill_stroke(c, C('#c9a24a'), 6)
    c.restore()
    c.restore()


# ============================================================== shots
WORDS = []
SHOT_T0 = {}


def wl(key, i):
    """Local time of word i inside shot `key` (so gags land on the exact word)."""
    return WORDS[i]['t0'] - SHOT_T0[key]


def board_bg(F, col=C('#6a4430'), col2=C('#3a2416')):
    c = F.layer(p=1.0)
    c.rectangle(-1500, -1500, 3000, 3000)
    g = cairo.LinearGradient(-600, -600, 600, 600)
    g.add_color_stop_rgb(0, *col)
    g.add_color_stop_rgb(1, *col2)
    c.set_source(g)
    c.fill()
    for i in range(-12, 13):
        stick(c, [(-1500, i * 110), (1500, i * 110 + 20)], 2, (0, 0, 0, 0.18))
    return c


def snip_closeup(F, t, tsnip, fat=0.0, cut_col=(1, 1, 1)):
    """Shared framing for the two snip shots (s02 and its callback s29)."""
    c = F.layer(p=1.0)
    k = seg(t, tsnip - 0.05, tsnip + 0.05)
    after = t > tsnip
    fly_u = ease_out(seg(t, tsnip, tsnip + 0.6))
    # the rat (body), tail still attached until the snip
    rat(c, -10 if fat else 40, 60, 1.3 if fat else 1.6, fat=fat, tail=0.0 if after else 1.0, look=(-0.7, 0.2) if not after else (0.2, -0.3),
        eyes='wide' if t > tsnip - 0.35 else None, mouth='o' if after else 'smile',
        blink=blink_at(t, 1.7, 0.3), bandage=None, tail_wave=t * 3)
    if after:  # the loose tail flips away
        tail_prop(c, lerp(-250, -330, fly_u), lerp(-20, -160, fly_u) + 120 * fly_u ** 2, 1.6, -0.4 + 3 * fly_u, 0.3)
    # scissors close on the tail root
    op = 1 - k if t < tsnip + 0.05 else lerp(0, 0.6, seg(t, tsnip + 0.1, tsnip + 0.4))
    scissors(c, lerp(-300, -170, ease_out(seg(t, 0, tsnip - 0.1))), -38 * 1.6 + 30, 1.5, op, -0.15)
    burst(c, -110, -40, 120, ease_out(seg(t, tsnip, tsnip + 0.25)) * (1 - seg(t, tsnip + 0.25, tsnip + 0.45)), cut_col)
    text(c, 'SNIP!', -120, -250, 70, (1, 1, 1), INK, 10, k=pop_in(t, tsnip, 0.18) * (1 - seg(t, tsnip + 0.7, tsnip + 0.9)),
         rot=-0.12)
    return c


def s01_hook(t, d):
    u = t / d
    cam = path(u, [(0, aim(0, -820, 0.95, 0.5)), (0.5, aim(10, -250, 1.6)), (1, aim(10, -250, 1.8))], ease_io)
    F = Frame(cam)
    street(F, t, 'day', 'old', blur_bg=2.0, seed=1)
    c = F.layer(p=1.0)
    person(c, 0, 0, 1.0, arms='hold_up', look=(0.6, -0.5), mouth='smile', blink=blink_at(t, 2.1, 0.4),
           hand=lambda cc, x, y: rat_dangle(cc, x, y, 0.5, 0.35 * math.sin(t * 5), eyes='wide', mouth='o',
                                            blink=blink_at(t, 1.3)), **HERO)
    for i, x in enumerate((-260, 250, 380)):  # passers-by
        person(c, x + 20 * t * (1 if i else -1), 10 + i * 4, 0.82, step=t * 7 + i, look=(-0.6 if x > 0 else 0.6, 0),
               blink=blink_at(t, 2.4, i), **TOWN[i])
    grade(F, vig=0.42, warm_glow=(W * 0.2, H * 0.1, 320, 0.15))
    return F


def s02_snip(t, d):
    u = t / d
    F = Frame(Cam(-70, -60, lerp(0.92, 1.04, ease(u)), lerp(-0.04, 0.02, ease(u))))
    board_bg(F)
    c = F.layer(p=1.0)
    lamp_light(c, 0, -100, 600, 1.2)
    snip_closeup(F, t, wl('s02', 10))
    grade(F, vig=0.5)
    return F


def s03_let_go(t, d):
    u = t / d
    rx = lerp(-60, 420, ease_in(seg(t, 0.12, d)))
    cam = path(u, [(0, aim(-80, -200, 1.45)), (1, aim(160, -180, 1.6))], ease_io)
    F = Frame(cam)
    street(F, t, 'day', 'old', blur_bg=3.0, seed=1)
    c = F.layer(p=1.0)
    person(c, -200, 0, 1.0, arms='wag' if t > 0.3 else 'down', look=(1, 0.3), mouth='smile', **HERO)
    rat(c, rx, 6, 0.75, tail=0.0, bandage=True, step=t * 26, look=(1, 0), mouth='grin', tail_wave=0)
    for k in range(3):  # dust puffs behind the runner
        p = (t * 3 + k / 3) % 1
        soft_ellipse(c, rx - 80 - p * 90, -4 - p * 20, 22 + 20 * p, 14 + 10 * p, C('#e6d2a8'), 0.6 * (1 - p))
    grade(F, vig=0.42)
    return F


def bounty_window(F, t, blur=3.0):
    """The bounty counter: office wall, a wooden counter at y=0 with a window frame."""
    office(F, t, blur=blur, window=False, fan=False)
    c = F.layer(p=1.0)
    c.rectangle(-700, -760, 1400, 60)
    fill_stroke(c, C('#6a4426'), 5)
    text(c, 'PRIMES', 0, -730, 34, C('#f3e2b8'), None)
    return c


def counter_top(c, w=1400, y=0):
    c.rectangle(-w / 2, y, w, 600)
    form_shade(c, lambda: c.rectangle(-w / 2, y, w, 600), C('#7a5030'), C('#a87448'), C('#4a2e18'), (-w / 2, y, w / 2, y + 600))
    c.rectangle(-w / 2, y, w, 600)
    c.set_line_width(5)
    src(c, INK)
    c.stroke()
    c.rectangle(-w / 2 - 10, y - 18, w + 20, 24)
    fill_stroke(c, C('#9a6a3e'), 5)


def s04_paid(t, d):
    u = t / d
    cam = path(u, [(0, aim(0, -130, 1.3)), (1, aim(0, -130, 1.5))])
    F = Frame(cam)
    bounty_window(F, t)
    c = F.layer(p=1.0)
    tp = wl('s04', 20)
    person(c, -150, 120, 1.0, arms='give' if t < tp + 0.6 else 'down', look=(1, 0.2), mouth='flat', blink=blink_at(t, 2.2),
           **OFFICIAL)
    person(c, 150, 120, 1.0, flip=True, look=(1, 0.2), mouth='grin' if t > tp else 'smile', arms='give' if t > tp - 0.1 else 'down',
           **HERO)
    counter_top(c, y=10)
    tail_prop(c, 40, -16, 0.8, 0.1)
    cx = lerp(-80, 120, ease_io(seg(t, tp - 0.25, tp + 0.25)))
    coin(c, cx, -80, 26, glint=pop_in(t, tp, 0.25), label='1')
    grade(F, vig=0.45)
    return F


def s05_rewind(t, d):
    u = t / d
    F = Frame(Cam(0, 0, lerp(1.0, 1.15, ease(u)), 0.15 * math.sin(u * PI)))
    paper_bg(F, C('#e9dcc0'), lines=False)
    c = F.layer(p=1.0)
    # clock spinning backwards
    ellipse(c, 0, -200, 190, 190)
    fill_stroke(c, C('#fbf6e9'), 8)
    for k in range(12):
        a = k * PI / 6
        stick(c, [(150 * math.cos(a), -200 + 150 * math.sin(a)), (172 * math.cos(a), -200 + 172 * math.sin(a))], 5)
    a = -t * 9
    stick(c, [(0, -200), (110 * math.sin(a), -200 - 110 * math.cos(a))], 9)
    stick(c, [(0, -200), (70 * math.sin(a / 12), -200 - 70 * math.cos(a / 12))], 12)
    # calendar pages flying back: 1902 -> 1897
    yr = 1902 - int(clamp(u * 1.15) * 5)
    for k in range(4):
        p = (u * 4 + k / 4) % 1
        calendar_page(c, lerp(-60, -520, p) + k * 30, lerp(160, -200, p), 0.9, 'ANNÉE', str(yr + (k % 2)), rot=-p * 3)
    calendar_page(c, 0, 220, 1.6, 'ANNÉE', str(yr))
    F.post = vintage_post(lambda T: ease(clamp((T - SHOT_T0['s05']) / 0.6)))
    return F


def official_group(c, x, y, t, s=1.0, proud=0.0, flip=False, look=(0.2, 0)):
    for i, (dx, kw) in enumerate(((-150, OFFICIAL), (0, OFFICIAL2), (150, OFFICIAL))):
        person(c, x + dx * s, y + (i % 2) * 6, s * (1.0 + 0.04 * proud), arms='hips' if proud > 0.5 else 'down',
               look=look, mouth='smile' if proud > 0.3 else 'flat', lid=0.35 * proud, lean=-0.08 * proud,
               blink=blink_at(t, 2.3, i * 0.6), flip=flip, **kw)


def s06_french(t, d):
    u = t / d
    cam = path(u, [(0, aim(-160, -250, 1.5)), (1, aim(120, -250, 1.55))], lambda v: v)
    F = Frame(cam)
    street(F, t, 'sepia', 'french', blur_bg=2.5, seed=6)
    c = F.layer(p=0.8, blur=1.5)
    stick(c, [(420, -40), (420, -760)], 8)  # flagpole
    for k, col in enumerate((C('#2b4a9a'), C('#f4f4f2'), C('#c0302a'))):
        c.rectangle(424 + k * 50, -760 + 6 * math.sin(t * 4 + k), 50, 100)
        fill_stroke(c, col, 3)
    c = F.layer(p=1.0)
    official_group(c, 0, 0, t, 1.0, proud=ease(seg(t, 0.3, 0.8)))
    F.post = vintage_post(1.0)
    return F


def s07_proud(t, d):
    u = t / d
    tp = wl('s07', 41)
    cam = path(u, [(0, aim(0, -230, 1.3)), (1, aim(0, -230, 1.55))])
    F = Frame(cam)
    street(F, t, 'sepia', 'french', blur_bg=3, seed=7)
    c = F.layer(p=1.0)
    rk = ease_out(seg(t, 0.4, 0.8))  # ribbon cut
    manhole(c, 0, 120, 1.2, shine=pop_in(t, 0.6, 0.3))
    if rk < 1:
        stick(c, [(-500, 60), (-500 * rk - 10, 70)], 9, C('#c0302a'))
        stick(c, [(500, 60), (500 * rk + 10, 70)], 9, C('#c0302a'))
    else:
        stick(c, [(-500, 60), (-420, 150)], 9, C('#c0302a'))
        stick(c, [(500, 60), (420, 150)], 9, C('#c0302a'))
    proud = ease(seg(t, tp - 0.3, tp + 0.2))
    official_group(c, 0, 20, t, 0.95, proud=proud, look=(0, 0.6) if proud < 0.5 else (0, -0.2))
    for k in range(5):  # little proud sparkles
        star(c, -300 + k * 150, -380 - 30 * math.sin(t * 3 + k), 16 * proud, C('#ffe9a0'), 2.4, t + k)
    F.post = vintage_post(1.0)
    return F


def s08_sewer_new(t, d):
    u = t / d
    lift = ease_out(seg(t, 0.15, 0.6))
    cam = path(u, [(0, aim(0, 60, 1.4, 0.5)), (0.55, aim(0, 60, 2.4, 0.5)), (1, aim(0, 110, 5.0, 0.5))], ease_in)
    F = Frame(cam)
    street(F, t, 'sepia', 'french', blur_bg=4, seed=8)
    c = F.layer(p=1.0)
    manhole(c, 0, 110, 1.3, lift=lift, shine=lift)
    text(c, 'NEUF!', 170, -60, 56, C('#fff1c0'), INK, 8, k=pop_in(t, wl('s08', 45), 0.25), rot=0.15)
    burst(c, 0, 80, 200, lift * (1 - seg(t, 0.6, 0.9)))
    F.post = vintage_post(1.0)
    return F


def s09_tunnels(t, d):
    u = t / d
    F = Frame(Cam(0, -240, lerp(1.0, 1.55, ease_io(u))))
    tunnel(F, t, light=1.0, clean=1.0, sparkle=1.0)
    text(F.layer(screen=True), '', 0, 0, 1)
    F.post = vintage_post(1.0)
    return F


def villa_row(c, t, tone='day', lit=False, seed=11, y=0):
    x = -900
    k = 0
    rnd = random.Random(seed)
    while x < 900:
        w = rnd.uniform(220, 280)
        villa(c, x, y, w, rnd.uniform(300, 360), seed * 10 + k, tone, lit=lit)
        x += w + 40
        k += 1


def s10_under_french(t, d):
    u = t / d
    cam = path(u, [(0, aim(0, 330, 1.25, 0.5)), (1, aim(0, -230, 1.2, 0.5))])
    F = Frame(cam)
    sky(F, 'sepia', t)
    c = F.layer(p=1.0)
    villa_row(c, t, 'day', seed=11, y=-10)
    for i, x in enumerate((-180, 200)):  # fancy residents with parasols
        person(c, x, -10, 0.6, coat=C('#f2efe6'), hat='pith', moustache='handlebar', hair_col=C('#6a4a2a'), look=(0, 0),
               mouth='smile', lid=0.4, flip=i == 1, pants=C('#e8e2d2'))
    soil_cutaway(c, y0=0, depth=1300)
    for x in (-360, 0, 360):
        tunnel_section(c, x, 380, 110, t)
        stick(c, [(x, 270), (x, 0)], 22, STONE)
        stick(c, [(x - 11, 270), (x - 11, 0)], 3)
        stick(c, [(x + 11, 270), (x + 11, 0)], 3)
    stick(c, [(-250, 380), (-110, 380)], 40, STONE)
    stick(c, [(110, 380), (250, 380)], 40, STONE)
    F.post = vintage_post(1.0)
    return F


def s11_rats_love(t, d):
    u = t / d
    tl = wl('s11', 62)
    F = Frame(Cam(0, -200, lerp(1.25, 1.4, ease(u))))
    tunnel(F, t, light=0.9, clean=0.8)
    c = F.layer(p=1.0)
    for i, (x, y, s, t0) in enumerate(((-210, 160, 0.95, 0.05), (210, 170, 0.95, 0.25), (0, 240, 1.15, 0.45),
                                      (-90, 60, 0.6, 0.65), (110, 70, 0.6, 0.8))):
        k = back_out(seg(t, t0, t0 + 0.3))
        if k <= 0:
            continue
        rat_front(c, x, y + (1 - k) * 160, s, look=(0, 0.2), hearts=back_out(seg(t, tl + i * 0.06, tl + 0.25 + i * 0.06)),
                  blink=blink_at(t, 2.2, i))
    for i in range(6):  # floating hearts
        p = seg(t, tl + i * 0.1, tl + 1.1 + i * 0.1)
        if 0 < p < 1:
            heart(c, -250 + i * 100 + 20 * math.sin(t * 4 + i), 40 - p * 360, 26 * (1 - 0.4 * p))
    grade(F, vig=0.5)
    return F


def s12_dark_warm(t, d):
    u = t / d
    tw = wl('s12', 70)
    F = Frame(Cam(0, 40, lerp(1.6, 1.85, ease(u))))
    dark = ease(seg(t, 0.15, 0.45)) * (1 - 0.65 * ease(seg(t, tw - 0.1, tw + 0.3)))
    tunnel(F, t, light=0.7, clean=0.7)
    c = F.layer(p=1.0)
    warm = ease(seg(t, tw - 0.1, tw + 0.3))
    soft_ellipse(c, 0, 60, 380, 240, C('#ff9a4a'), 0.55 * warm)
    rat(c, -20, 160, 1.0, pose='sleep', blink=1.0, mouth='smile', tail_wave=0.5, look=(0, 0))
    for k in range(3):
        p = (t * 0.7 + k / 3) % 1
        text(c, 'z', 110 + k * 26 + p * 40, 20 - p * 130, 34 + k * 8, (1, 1, 1), INK, 5, k=(1 - p) * warm + 0.001)
    c2 = F.layer(screen=True)
    c2.rectangle(0, 0, W, H)
    src(c2, (0.02, 0.02, 0.05, 0.7 * dark))
    c2.fill()
    grade(F, vig=0.6, tint=(0.25, 0.1, 0.0, 0.12 * warm))
    return F


def kitchen(c, t, x=0, y=0, cook=True, pot_steam=True):
    """A cramped kitchen above ground: tiled wall, clay stove with a pot, a floor drain."""
    c.rectangle(x - 700, y - 700, 1400, 700)
    src(c, C('#e8d6b0'))
    c.fill()
    for i in range(14):
        for j in range(8):
            c.rectangle(x - 700 + i * 100, y - 700 + j * 90, 100, 90)
            c.set_line_width(1.5)
            src(c, (0, 0, 0, 0.1))
            c.stroke()
    c.rectangle(x - 160, y - 200, 320, 200)
    fill_stroke(c, C('#a8583a'), 5)
    soft_ellipse(c, x, y - 120, 80, 40, C('#ff8a3a'), 0.6)
    c.move_to(x - 120, y - 260)
    c.curve_to(x - 130, y - 190, x + 130, y - 190, x + 120, y - 260)
    c.close_path()
    fill_stroke(c, C('#3a3a3a'), 5)
    if pot_steam:
        for k in range(3):
            p = (t * 0.6 + k / 3) % 1
            c.move_to(x - 40 + k * 40, y - 270 - p * 150)
            c.curve_to(x - 60 + k * 40, y - 300 - p * 150, x - 20 + k * 40, y - 330 - p * 150, x - 40 + k * 40, y - 360 - p * 150)
            c.set_line_width(8)
            src(c, (1, 1, 1, 0.5 * (1 - p)))
            c.stroke()
    if cook:
        person(c, x - 220, y, 1.0, look=(0.8, 0.3), mouth='flat', blink=blink_at(t, 2.0), arms='scoop',
               body=C('#b0563a'), hair='bun', hair_col=C('#1a1410'), tunic=True, pants=C('#5a2e20'))
    c.rectangle(x - 3000, y, 6000, 30)
    src(c, C('#5a4030'))
    c.fill()


def s13_kitchen(t, d):
    u = t / d
    tk = wl('s13', 78)
    cam = path(u, [(0, Cam(60, 200, 0.95)), (1, Cam(60, 60, 1.08))])
    F = Frame(cam)
    c = F.layer(p=1.0)
    kitchen(c, t, 0, 0)
    soil_cutaway(c, y0=30, depth=1000)
    tunnel_section(c, 200, 520, 150, t)
    stick(c, [(200, 370), (200, 30)], 34, C('#6a6f78'))  # pipe up to the floor drain
    stick(c, [(183, 370), (183, 30)], 3)
    stick(c, [(217, 370), (217, 30)], 3)
    ry = lerp(560, 0, ease_io(seg(t, 0.1, tk - 0.05)))
    if ry > 30:
        rat(c, 200, ry, 0.45, rot=-PI / 2, shadow=False, step=t * 20)
    else:  # pops out of the drain next to the stove
        k = pop_in(t, tk - 0.05, 0.3)
        rat_front(c, 200, 10, 0.55 * k, look=(-0.6, -0.4), mouth='smile', blink=blink_at(t, 1.5))
        star(c, 280, -120, 24 * k, GOLD, 3, t)
    ellipse(c, 200, 30, 40, 10)
    fill_stroke(c, C('#2a2a2a'), 3)
    grade(F, vig=0.45)
    return F


def sponge_bed(c, x, y):
    c.rectangle(x - 150, y - 50, 300, 50)
    fill_stroke(c, C('#f2d24a'), 4)
    for k in range(12):
        ellipse(c, x - 130 + k * 22, y - 25 + (k % 2) * 10, 5, 4)
        src(c, C('#c9a22a'))
        c.fill()
    ellipse(c, x - 110, y - 64, 54, 24)
    fill_stroke(c, C('#f4f0f8'), 4)


def s14_hotel(t, d):
    u = t / d
    tf = wl('s14', 81)
    trs = wl('s14', 85)
    F = Frame(Cam(0, 40, lerp(1.4, 1.6, ease(u))))
    tunnel(F, t, light=0.85, clean=0.7, vp=(0, -120))
    c = F.layer(p=1.0)
    lamp_light(c, 0, 80, 360, 1.0)
    sponge_bed(c, -80, 210)
    rat(c, -70, 170, 0.95, pose='sit', look=(0.4, -0.3), mouth='smile', blink=blink_at(t, 2.6), tail_wave=t,
        shadow=False)
    for k in range(5):
        star(c, -200 + k * 100, -150, 34 * pop_in(t, tf + k * 0.09, 0.2), GOLD, 3.6, 0.1 * math.sin(t * 4 + k))
    wx = lerp(480, 170, ease_out(seg(t, trs - 0.35, trs + 0.2)))
    rat(c, wx, 220, 0.8, flip=True, look=(-1, 0), step=t * 18 if t < trs + 0.2 else None, mouth='smile', tail_wave=t * 2)
    # tray held high by the waiter rat, with a noodle crumb under a cloche
    c.save()
    c.translate(wx - 50, 60)
    ellipse(c, 0, 0, 70, 12)
    fill_stroke(c, C('#d9dde4'), 4)
    c.move_to(-46, -2)
    c.curve_to(-46, -64, 46, -64, 46, -2)
    c.close_path()
    fill_stroke(c, C('#e6e9ee'), 4)
    ellipse(c, 0, -52, 8, 6)
    fill_stroke(c, C('#c0c4cc'), 3)
    c.restore()
    stick(c, [(wx - 60, 150), (wx - 50, 70)], 4)
    grade(F, vig=0.5, warm_glow=(W * 0.45, H * 0.55, 260, 0.12))
    return F


def s15_fleas(t, d):
    u = t / d
    tf = wl('s15', 90)
    F = Frame(Cam(0, -10, lerp(1.9, 2.15, ease(u))))
    tunnel(F, t, light=0.6, clean=0.5, blur_far=4, vp=(0, -60))
    c = F.layer(p=1.0)
    rat_front(c, 0, 40, 1.05, look=(0, -0.7), mouth='o' if t > tf else 'smile', blink=blink_at(t, 1.6))
    for k in range(6):
        p = pop_in(t, tf + k * 0.06, 0.2)
        if p > 0:
            flea(c, -90 + k * 36, -150 - (k % 2) * 30, 1.2 * p, hop=t * 9 + k)
    grade(F, vig=0.5)
    return F


def s16_plague(t, d):
    u = t / d
    tp = wl('s16', 94)
    F = Frame(Cam(0, -200, lerp(1.2, 1.45, ease(u))))
    sky(F, 'dusk', t)
    far_city(F, 'dusk', blur=1.0)
    c = F.layer(p=0.6)
    for k in range(3):  # toxic green miasma rolling over the town
        x = lerp(-900, 300, ease(seg(t, tp - 0.4, d))) + k * 260
        for j in range(6):
            soft_ellipse(c, x + j * 90, -60 - (j % 3) * 50 - k * 40, 160, 110, C('#7fbf3a'), 0.35 * seg(t, tp - 0.3, tp + 0.3))
    c = F.layer(p=1.0)
    flea(c, 0, -160, 5.2, hop=t * 5, look=(-0.6, 0.2))
    # skull-and-crossbones label on a tiny satchel the flea carries
    sk = max(1e-3, pop_in(t, tp, 0.25))
    c.save()
    c.translate(70, -200)
    c.scale(sk, sk)
    ellipse(c, 0, 0, 34, 30)
    fill_stroke(c, C('#e8f0d0'), 4)
    for sx in (-12, 12):
        ellipse(c, sx, -4, 7, 8)
        src(c, INK)
        c.fill()
    stick(c, [(-36, 30), (36, 60)], 6)
    stick(c, [(36, 30), (-36, 60)], 6)
    c.restore()
    grade(F, vig=0.6, tint=(0.2, 0.45, 0.05, 0.22 * seg(t, tp - 0.2, tp + 0.4)))
    return F


def poster(c, x, y, s=1.0, k=1.0, cross=0.0, tail_word=0.0):
    """WANTED-style bounty notice: a rat silhouette = 1 cent."""
    if k <= 0:
        return
    c.save()
    c.translate(x, y)
    c.scale(s * k, s * k)
    c.rotate(0.03)
    c.rectangle(-170, -220, 340, 440)
    fill_stroke(c, C('#f1e4c2'), 5)
    text(c, 'AVIS', 0, -175, 50, C('#7a2e2e'), None)
    rat(c, -20, -20, 0.9, col=C('#3a3236'), look=(0, 0), shadow=False)
    if cross > 0:
        stick(c, [(-150, -110), (-150 + 300 * cross, -20)], 10, C('#d6332f'))
    if tail_word > 0:
        tail_prop(c, 0, -60, 1.4 * tail_word, 0.0)
    text(c, '= 1 CENT', 0, 140, 48, INK, None)
    c.restore()


def s17_offer(t, d):
    u = t / d
    cam = path(u, [(0, aim(-20, -240, 1.0)), (1, aim(0, -250, 1.15))])
    F = Frame(cam)
    street(F, t, 'day', 'french', blur_bg=4, seed=17)
    c = F.layer(p=1.0)
    c.rectangle(-700, -700, 1400, 680)
    fill_stroke(c, C('#d9c8a0'), 5)
    for i in range(10):
        stick(c, [(-700, -700 + i * 70), (700, -700 + i * 70)], 2, (0, 0, 0, 0.12))
    k = pop_in(t, 0.35, 0.3)
    poster(c, 120, -330, 0.75, k)
    hammer = math.sin(clamp((t - 0.2) * 3) * PI * 3) * (t < 0.55)
    person(c, -190, 0, 1.0, arms='give', look=(1, -0.4), mouth='smile', blink=blink_at(t, 2.0), lean=0.05 * hammer,
           **OFFICIAL)
    grade(F, vig=0.42)
    return F


def s18_one_cent(t, d):
    u = t / d
    td = wl('s18', 104)
    tc = wl('s18', 110)
    cam = path(u, [(0, aim(0, -130, 1.3)), (0.6, aim(0, -130, 1.45)), (1, aim(-80, -150, 1.9, 0.4))])
    F = Frame(cam)
    bounty_window(F, t)
    c = F.layer(p=1.0)
    person(c, -160, 120, 1.0, arms='hold_up' if t > tc - 0.1 else 'down', look=(0.6, -0.4) if t > tc else (0.6, 0.4),
           mouth='smile', blink=blink_at(t, 2.4),
           hand=(lambda cc, x, y: coin(cc, x + 6, y - 30, 30, glint=pop_in(t, tc, 0.3), label='1')) if t > tc - 0.1 else None,
           **OFFICIAL)
    counter_top(c, y=10)
    k = ease_in(seg(t, td - 0.25, td))
    rat(c, 130, lerp(-500, -4, k), 0.85, dead=True, shadow=k >= 1, rot=0.0)
    if k >= 1:
        burst(c, 130, -10, 140, ease_out(seg(t, td, td + 0.25)) * (1 - seg(t, td + 0.25, td + 0.4)))
    grade(F, vig=0.45)
    return F


def s19_buckets(t, d):
    u = t / d
    cam = path(u, [(0, aim(-380, -260, 1.3)), (1, aim(160, -260, 1.35))], lambda v: v)
    F = Frame(cam)
    street(F, t, 'day', 'old', blur_bg=3, seed=19)
    c = F.layer(p=1.0)
    for i in range(7):
        x = -760 + i * 230 + t * 60
        kw = TOWN[i % len(TOWN)]
        person(c, x, 6 + (i % 2) * 8, 0.95, step=t * 8 + i, look=(1, 0.1), mouth='flat', blink=blink_at(t, 2.0, i),
               arms='give', hand=lambda cc, hx, hy, i=i: bucket(cc, hx + 40, hy + 110, 0.75, 3, i), **kw)
    grade(F, vig=0.42)
    return F


def s20_cart(t, d):
    u = t / d
    x = -260 + t * 140
    cam = path(u, [(0, aim(x - 60, -230, 1.05)), (1, aim(x - 40, -230, 1.15))], lambda v: v)
    F = Frame(cam)
    street(F, t, 'day', 'old', blur_bg=3, seed=20)
    c = F.layer(p=1.0)
    cart(c, x + 140, 30, 1.0, load=1.0, seed=3, t=t * 2)
    person(c, x - 250, 26, 1.0, step=t * 7, look=(1, 0.2), mouth='frown', brows='worried', sweat=1, arms='give',
           lean=0.15, **TOWN[2])
    for k in range(2):  # a rat tumbling off the top
        p = (t * 0.8 + k * 0.5) % 1
        c.save()
        c.translate(x + 60 + 160 * p, -230 + 260 * p ** 2)
        c.rotate(p * 6)
        rat(c, 0, 0, 0.45, dead=True, shadow=False)
        c.restore()
    grade(F, vig=0.42)
    return F


def s21_buried(t, d):
    u = t / d
    pile = ease_io(seg(t, 0.1, d - 0.2))
    cam = path(u, [(0, aim(0, -130, 1.2)), (1, aim(0, -60, 1.4))])
    F = Frame(cam)
    office(F, t)
    c = F.layer(p=1.0)
    person(c, 0, 120 + 120 * pile, 1.0, arms='up' if pile > 0.5 else 'down', look=(0, -0.9) if pile > 0.4 else (0.5, 0.4),
           mouth='scream' if pile > 0.55 else 'o', eyes='wide', brows='shock', sweat=2 if pile > 0.4 else 0,
           **OFFICIAL)
    desk(c, 0, 20, 520)
    rnd = random.Random(21)
    top = lerp(240, -100, pile)
    for i in range(110):  # the rising heap of dead rats
        yy = rnd.uniform(top, 240)
        xx = rnd.uniform(-600, 600) * (0.6 + 0.4 * (yy - top) / max(1, 240 - top))
        c.save()
        c.translate(xx, yy)
        c.rotate(rnd.uniform(-PI, PI))
        rat(c, 0, 0, rnd.uniform(0.45, 0.6), dead=True, shadow=False, tail=rnd.uniform(0.4, 1))
        c.restore()
    grade(F, vig=0.45)
    return F


def s22_smell(t, d):
    u = t / d
    cam = path(u, [(0, aim(0, -230, 2.0)), (1, aim(0, -230, 2.35))])
    F = Frame(cam)
    office(F, t, blur=6)
    c = F.layer(p=1.0)
    rnd = random.Random(22)
    for i in range(40):
        c.save()
        c.translate(rnd.uniform(-400, 400), rnd.uniform(-60, 200))
        c.rotate(rnd.uniform(-PI, PI))
        rat(c, 0, 0, 0.55, dead=True, shadow=False)
        c.restore()
    person(c, 0, 50, 1.0, arms='pinch', look=(0.2, -0.2), eyes='wide', mouth='wobble', brows='worried',
           tears=0.3 + 0.2 * math.sin(t * 5), blink=blink_at(t, 1.4), **OFFICIAL)
    stink(c, -150, -120, t, 3, ease(seg(t, 0.0, 0.3)))
    stink(c, 170, -150, t + 0.3, 3, ease(seg(t, 0.1, 0.4)))
    fly(c, 90, -330, t, 1)
    fly(c, -110, -300, t + 1.3, 2)
    grade(F, vig=0.5, tint=(0.3, 0.45, 0.05, 0.14))
    return F


def s23_rule(t, d):
    u = t / d
    tt = wl('s23', 147)
    F = Frame(Cam(0, -120, lerp(1.2, 1.5, ease_io(u))))
    board_bg(F, C('#6a4a32'), C('#3a2618'))
    c = F.layer(p=1.0)
    lamp_light(c, 0, -80, 500, 1.2)
    poster(c, 0, -150, 1.0, 1.0, cross=ease_out(seg(t, tt, tt + 0.35)), tail_word=pop_in(t, tt + 0.4, 0.3))
    # the official's pen
    px = lerp(-150, 150, ease_out(seg(t, tt, tt + 0.35)))
    c.save()
    c.translate(px + 40, -220)
    c.rotate(-0.6)
    c.rectangle(0, -12, 180, 24)
    fill_stroke(c, C('#2a2a3a'), 4)
    c.move_to(0, -12)
    c.line_to(-36, 0)
    c.line_to(0, 12)
    c.close_path()
    fill_stroke(c, C('#c9a24a'), 3)
    c.restore()
    grade(F, vig=0.55)
    return F


def s24_no_rat(t, d):
    u = t / d
    cam = path(u, [(0, aim(0, -130, 1.3)), (1, aim(-20, -130, 1.45))])
    F = Frame(cam)
    bounty_window(F, t)
    c = F.layer(p=1.0)
    wag = math.sin(t * 14) * 0.15
    person(c, -170, 120, 1.0, arms='wag', look=(0.5, 0), mouth='frown', brows='angry', lean=wag * 0.3, **OFFICIAL)
    counter_top(c, y=10)
    rat(c, 120, -4, 0.9, dead=True)
    k = pop_in(t, wl('s24', 153) - 0.1, 0.25)
    if k > 0:
        c.save()
        c.translate(150, -60)
        c.scale(k, k)
        ellipse(c, 0, 0, 130, 130)
        c.set_line_width(18)
        src(c, C('#d6332f'))
        c.stroke()
        stick(c, [(-92, 92), (92, -92)], 18, C('#d6332f'))
        c.restore()
    grade(F, vig=0.45)
    return F


def s25_tail(t, d):
    u = t / d
    tt = wl('s25', 157)
    F = Frame(Cam(0, 40, lerp(1.6, 1.9, ease(u))))
    c = F.layer(screen=True)
    src(c, C('#1a1210'))
    c.paint()
    c = F.layer(p=1.0)
    soft_ellipse(c, 0, -20, 330, 420, C('#fff1c0'), 0.35 * pop_in(t, 0.1, 0.3))
    ellipse(c, 0, 60, 230, 60)  # velvet cushion
    fill_stroke(c, C('#8a1f3a'), 5)
    for sx in (-200, 200):
        ellipse(c, sx, 70, 18, 12)
        fill_stroke(c, C('#e8b53a'), 3)
    tail_prop(c, 0, 20 - 14 * math.sin(t * 3), 1.6, 0.0, 0.3 * math.sin(t * 2))
    for k in range(6):
        a = k * PI / 3 + t
        star(c, 210 * math.cos(a), -40 + 120 * math.sin(a), 20 * pop_in(t, tt + k * 0.05, 0.2), (1, 1, 1), 0, t)
    grade(F, vig=0.6)
    return F


def s26_hero(t, d):
    u = t / d
    ts = wl('s26', 167)
    cam = path(u, [(0, aim(0, -240, 1.35)), (1, aim(0, -240, 1.85))])
    F = Frame(cam)
    street(F, t, 'dusk', 'french', blur_bg=4, seed=26)
    c = F.layer(p=1.0)
    manhole(c, 210, 40, 0.9)
    person(c, 0, 0, 1.0, arms='wag', look=(0, 0), mouth='smirk', lid=0.35 * ease(seg(t, ts - 0.2, ts + 0.2)),
           blink=blink_at(t, 2.4, 0.5),
           hand=lambda cc, x, y: scissors(cc, x + 10, y - 20, 0.55, 0.5 + 0.5 * math.sin(t * 6), -1.3 + 0.2 * math.sin(t * 3)),
           **HERO)
    grade(F, vig=0.5, warm_glow=(W * 0.3, H * 0.3, 300, 0.12))
    return F


def s27_climb(t, d):
    u = t / d
    cam = path(u, [(0, aim(0, -250, 1.4)), (1, aim(0, 260, 1.4))])
    F = Frame(cam)
    street(F, t, 'dusk', 'french', blur_bg=4, seed=26)
    c = F.layer(p=1.0)
    soil_cutaway(c, y0=0, depth=1600)
    c.rectangle(-70, 0, 140, 420)  # the shaft
    src(c, C('#1a1612'))
    c.fill()
    tunnel_section(c, 0, 600, 200, t)
    for sx in (-40, 40):
        stick(c, [(sx, -10), (sx, 470)], 6, C('#8a8f98'))
    for k in range(12):
        stick(c, [(-40, k * 38), (40, k * 38)], 5, C('#8a8f98'))
    yy = lerp(0, 470, ease_io(seg(t, 0.05, d - 0.1)))
    person(c, 0, yy, 0.85, arms='up', look=(0, 0.8), mouth='flat', step=t * 10, blink=blink_at(t, 2.0), **HERO)
    manhole(c, 170, 0, 0.8, lift=1.0)
    grade(F, vig=0.5)
    return F


def s28_fattest(t, d):
    u = t / d
    tf = wl('s28', 179)
    F = Frame(Cam(0, 110, lerp(1.3, 1.45, ease(u))))
    tunnel(F, t, light=0.8, clean=0.6, vp=(0, -80))
    c = F.layer(p=1.0)
    grab = ease_out(seg(t, tf + 0.15, tf + 0.6))
    rat(c, -230, 220, 0.5, look=(0.6, -0.4), blink=blink_at(t, 2.0), step=None)
    rat(c, -60, 220, 0.65, look=(0.6, -0.5), blink=blink_at(t, 2.2, 0.4))
    fx, fy = 120, 230 - 200 * grab
    if grab > 0:
        stick(c, [(330, -600), (260, -250), (fx - 30, fy - 120)], 8)
        ellipse(c, fx - 30, fy - 120, 12, 12)
        src(c, INK)
        c.fill()
    rat(c, fx, fy, 0.85, fat=1.0, look=(-0.5, -0.4) if grab else (0, 0), eyes='wide' if grab > 0 else None,
        mouth='o' if grab > 0 else 'smile', shadow=grab <= 0, tail_wave=t * 5)
    text(c, '!', fx + 80, fy - 180, 70, (1, 1, 1), INK, 8, k=pop_in(t, tf + 0.2, 0.2))
    grade(F, vig=0.5)
    return F


def s29_snip_again(t, d):
    u = t / d
    F = Frame(Cam(-70, -60, lerp(0.92, 1.06, ease(u)), lerp(0.04, -0.02, ease(u))))
    tunnel(F, t, light=0.6, clean=0.5, blur_far=5)
    snip_closeup(F, t, wl('s29', 187) - 0.05, fat=1.0)
    grade(F, vig=0.5)
    return F


def s30_free(t, d):
    u = t / d
    tf = wl('s30', 191)
    cam = path(u, [(0, aim(-80, -230, 1.45)), (1, aim(0, -230, 1.6))])
    F = Frame(cam)
    tunnel(F, t, light=0.75, clean=0.6, vp=(0, -330))
    c = F.layer(p=1.0)
    lamp_light(c, -80, -100, 380, 0.9)
    go = ease_in(seg(t, tf - 0.2, d))
    person(c, -150, 130, 1.0, arms='give' if t < tf else 'wag', look=(1, 0.4), mouth='smile', lid=0.2,
           blink=blink_at(t, 2.0, 0.3), **HERO)
    rat(c, lerp(40, 520, go), 140, 0.85, fat=1.0, tail=0.0, bandage=True, step=t * 20 if go > 0 else None,
        look=(1, 0) if go > 0 else (-0.6, -0.3), mouth='grin', eyes=None)
    heart(c, -100, -230 - 20 * seg(t, tf, d), 36 * pop_in(t, tf, 0.3))
    grade(F, vig=0.5, warm_glow=(W * 0.35, H * 0.45, 260, 0.12))
    return F


def s31_lost_it(t, d):
    u = t / d
    cam = path(u, [(0, aim(-60, -240, 1.4)), (1, aim(-20, -240, 1.55))])
    F = Frame(cam)
    street(F, t, 'day', 'old', blur_bg=3, seed=31)
    c = F.layer(p=0.85, blur=2.5)
    person(c, 380, 10, 0.75, step=t * 6, look=(1, 0), mouth='smile', **HERO)
    c = F.layer(p=1.0)
    person(c, -170, 30, 1.0, arms='twirl', look=(1, -0.1), mouth='smirk', lid=0.3, blink=blink_at(t, 2.0), **CATCH2)
    person(c, 70, 30, 1.0, arms='hips', look=(1, 0), mouth='o', brows='raised', eyes='wide', **CATCH3)
    for k in range(3):  # cuckoo spirals by the temple
        a = t * 6 + k * 2
        c.new_path()
        c.arc(-110 + 10 * k, -330 - 14 * k, 10 + 6 * k, a, a + 4)
        c.set_line_width(3)
        src(c, (1, 1, 1, 0.9))
        c.stroke()
    grade(F, vig=0.42)
    return F


def s32_kill_it(t, d):
    u = t / d
    tk = wl('s32', 207)
    cam = path(u, [(0, aim(-40, -250, 1.7)), (1, aim(-40, -250, 1.95))])
    F = Frame(cam)
    street(F, t, 'day', 'old', blur_bg=5, seed=31)
    c = F.layer(p=1.0)
    person(c, -60, 30, 1.0, arms='wag', look=(1, 0), mouth='shout', brows='angry', blink=blink_at(t, 2.2), **CATCH3)
    k = pop_in(t, tk - 0.15, 0.25)
    speech_bubble(c, 150, -360, k * 1.05, lambda cc: rat(cc, 0, -14, 0.5, dead=True, shadow=False))
    grade(F, vig=0.42)
    return F


def s33_haircut(t, d):
    u = t / d
    F = Frame(Cam(0, -40, lerp(1.5, 1.7, ease(u))))
    c = F.layer(screen=True)
    src(c, C('#d8e4dc'))
    c.paint()
    c = F.layer(p=0.6, blur=2)
    for i in range(-6, 7):
        c.rectangle(i * 120, -1400, 60, 1400)
        src(c, C('#c6d6cc'))
        c.fill()
    c.rectangle(-170, -420, 340, 200)  # mirror
    fill_stroke(c, C('#bcd6e4'), 8)
    stick(c, [(-120, -390), (-70, -270)], 6, (1, 1, 1, 0.6))
    for k in range(5):  # barber pole stripes
        c.rectangle(280, -420 + k * 50, 50, 50)
        src(c, C('#d6332f') if k % 2 == 0 else (1, 1, 1))
        c.fill()
    c = F.layer(p=1.0)
    c.rectangle(-3000, 160, 6000, 3000)
    src(c, C('#e8e2d2'))
    c.fill()
    c.rectangle(-120, 40, 240, 120)  # chair seat + base
    fill_stroke(c, C('#c0302a'), 5)
    stick(c, [(0, 160), (0, 260)], 18, C('#9aa0aa'))
    rat(c, -30, 50, 1.0, pose='sit', look=(0.3, -0.3), mouth='smile', shadow=False, tail_wave=t * 3)
    for k in range(3):  # fur clippings falling
        p = (t * 1.2 + k / 3) % 1
        stick(c, [(40 + k * 20, -120 + p * 180), (46 + k * 20, -110 + p * 180)], 3, RAT_GREY)
    scissors(c, 90, -120, 0.55, 0.5 + 0.5 * math.sin(t * 22), -2.4)
    grade(F, vig=0.4)
    return F


RAT_GREY = C('#8a8790')


def s34_pocket(t, d):
    u = t / d
    tp = wl('s34', 218)
    cam = path(u, [(0, aim(0, -240, 1.8)), (1, aim(0, -230, 2.05))])
    F = Frame(cam)
    street(F, t, 'day', 'old', blur_bg=6, seed=34)
    c = F.layer(p=1.0)
    k = ease_io(seg(t, tp - 0.2, tp + 0.35))
    person(c, 0, 30, 1.0, arms='pocket' if k > 0.5 else 'give', look=(0.5, 0.4) if k < 0.5 else (0, 0), mouth='smile',
           cheeks=0.6, blink=blink_at(t, 2.1, 0.2),
           hand=(lambda cc, x, y: tail_prop(cc, x + 30, y, 0.5, 0.4 + 0.2 * math.sin(t * 6))) if k <= 0.5 else None, **HERO)
    if k > 0.5:  # tail tip peeking out of the pocket
        c.save()
        c.translate(30, 30 - 92 - 30)
        stick(c, [(0, 0), (12, -26), (4, -44)], 5, PINK)
        c.restore()
    star(c, 70, -140, 22 * pop_in(t, tp + 0.3, 0.25), GOLD, 3, t)
    grade(F, vig=0.45)
    return F


def s35_hundred(t, d):
    u = t / d
    th = wl('s35', 228)
    cam = path(u, [(0, aim(20, -140, 1.2)), (1, aim(20, -150, 1.35))])
    F = Frame(cam)
    bounty_window(F, t)
    c = F.layer(p=1.0)
    person(c, -170, 120, 1.0, arms='down', look=(1, 0.4), mouth='o', brows='raised', blink=blink_at(t, 2.3), **OFFICIAL)
    person(c, 170, 120, 1.0, flip=True, arms='give', look=(1, 0.4), mouth='grin', **HERO)
    counter_top(c, y=10)
    tail_bundle(c, 30, -20, 1.0, 9, 1)
    calendar_page(c, 200, -420, 0.8, 'SEMAINE', '1', rot=0.08)
    counter(c, -60, -420, 100 * ease_out(seg(t, th - 0.6, th)), 96, k=pop_in(t, 0.1, 0.25))
    grade(F, vig=0.45)
    return F


def s36_thousand(t, d):
    u = t / d
    tt = wl('s36', 237)
    cam = path(u, [(0, aim(20, -140, 1.25)), (1, aim(20, -160, 1.4))])
    F = Frame(cam)
    bounty_window(F, t)
    c = F.layer(p=1.0)
    person(c, -180, 120, 1.0, arms='down', look=(1, 0.2), mouth='o', eyes='wide', brows='shock', **OFFICIAL)
    counter_top(c, y=10)
    tail_heap(c, 80, 10, 520, lerp(60, 260, ease_out(seg(t, 0.1, tt))), seed=36, n=70)
    flip = seg(t, 0.2, 0.6)
    calendar_page(c, 200, -420, 0.8, 'MOIS', '30' if flip > 0.5 else '1', rot=0.08 - flip * 0.2)
    counter(c, -70, -420, lerp(100, 1000, ease_out(seg(t, 0.2, tt))), 96)
    grade(F, vig=0.45)
    return F


def confetti(c, t, n=50, seed=0, area=(-500, -1000, 1000, 1100)):
    rnd = random.Random(seed)
    cols = [C('#e0413a'), C('#2f6fd6'), C('#f2d24a'), C('#5fae4a'), (1, 1, 1)]
    for i in range(n):
        x = area[0] + rnd.uniform(0, area[2]) + 30 * math.sin(t * 2 + i)
        y = area[1] + (rnd.uniform(0, area[3]) + t * rnd.uniform(200, 400)) % area[3]
        c.save()
        c.translate(x, y)
        c.rotate(t * 5 + i)
        c.rectangle(-8, -4, 16, 8)
        src(c, rnd.choice(cols))
        c.fill()
        c.restore()


def s37_thrilled(t, d):
    u = t / d
    cam = path(u, [(0, aim(0, -240, 1.35)), (1, aim(0, -230, 1.5))])
    F = Frame(cam)
    street(F, t, 'day', 'french', blur_bg=3, seed=37)
    c = F.layer(p=1.0)
    for i, (dx, kw) in enumerate(((-170, OFFICIAL), (0, OFFICIAL2), (170, OFFICIAL))):
        hop = abs(math.sin(t * 7 + i)) * 30
        person(c, dx, 10 - hop, 1.0, arms='up', look=(0, -0.4), mouth='grin', eyes='wide', cheeks=0.6, step=0,
               shadow=False, **kw)
    confetti(c, t, 60, 37)
    grade(F, vig=0.4)
    return F


def s38_june(t, d):
    u = t / d
    F = Frame(Cam(0, -40, lerp(1.2, 1.45, ease(u))))
    sky(F, 'day', t, sun=(140, -420))
    c = F.layer(p=1.0)
    k = pop_in(t, 0.0, 0.3)
    calendar_page(c, 0, -20, 2.4 * max(k, 0.01), 'JUIN', '21', rot=-0.05 + 0.03 * math.sin(t * 3))
    grade(F, vig=0.35, warm_glow=(W * 0.7, H * 0.15, 360, 0.3))
    return F


def s39_twenty_k(t, d):
    u = t / d
    tn = wl('s39', 254)
    cam = path(u, [(0, aim(-120, -230, 1.0)), (1, aim(80, -330, 1.1))])
    F = Frame(cam)
    street(F, t, 'day', 'french', blur_bg=3, seed=39)
    c = F.layer(p=1.0)
    tail_heap(c, 320, 40, 620, lerp(120, 520, ease_out(seg(t, 0.2, tn + 0.3))), seed=39, n=200)
    for i in range(12):  # the queue snaking to the heap
        x = -900 + i * 110 + 20 * math.sin(t * 2 + i)
        person(c, x, 30 + (i % 3) * 22, 0.75, step=t * 6 + i, look=(1, 0), mouth='smile' if i % 2 else 'flat',
               arms='give', hand=lambda cc, hx, hy, i=i: tail_bundle(cc, hx + 20, hy, 0.7, 5, i), blink=blink_at(t, 2, i),
               **TOWN[i % len(TOWN)])
    counter(c, 80, -600, 20000 * ease_out(seg(t, tn - 0.9, tn + 0.15)), 110, k=pop_in(t, 0.05, 0.25))
    grade(F, vig=0.42)
    return F


def s40_math(t, d):
    u = t / d
    cam = path(u, [(0, aim(0, -590, 0.72, 0.3)), (1, aim(0, -590, 0.8, 0.3))])
    F = Frame(cam)
    chalkboard(F, t)
    c = F.layer(p=0.6, blur=1.5)
    chalk(c, '20 000 / jour', -340, -760, 64, seg(t, 0.0, 0.5))
    chalk(c, 'x 180 jours', -340, -660, 64, seg(t, 0.3, 0.8))
    chalk(c, '= 0 rats', -340, -540, 76, seg(t, 0.6, 1.0), C('#f2d24a'))
    c = F.layer(p=1.0)
    person(c, -270, 60, 1.0, arms='wag', look=(0.6, -0.8), mouth='flat', lid=0.3, blink=blink_at(t, 1.9), **OFFICIAL2)
    grade(F, vig=0.45)
    return F


def xmas_tree(c, x, y, s, k=1.0):
    if k <= 0:
        return
    c.save()
    c.translate(x, y)
    c.scale(s * k, s * k)
    for j in range(3):
        c.move_to(-120 + j * 26, -j * 90)
        c.line_to(0, -150 - j * 90)
        c.line_to(120 - j * 26, -j * 90)
        c.close_path()
        fill_stroke(c, C('#3f8a3a'), 5)
    c.rectangle(-20, 0, 40, 40)
    fill_stroke(c, C('#6a4426'), 4)
    star(c, 0, -330, 34, GOLD, 4)
    for k2, (bx, by) in enumerate(((-50, -30), (40, -60), (-20, -130), (30, -170), (-10, -230))):
        ellipse(c, bx, by, 10, 10)
        fill_stroke(c, (C('#e0413a'), C('#2f6fd6'))[k2 % 2], 3)
    c.restore()


def s41_christmas(t, d):
    u = t / d
    tx = wl('s41', 269)
    cam = path(u, [(0, aim(0, -590, 0.75, 0.3)), (1, aim(0, -560, 0.82, 0.3))])
    F = Frame(cam)
    chalkboard(F, t)
    c = F.layer(p=0.6, blur=1.5)
    # chart: rat count line falling to zero
    stick(c, [(-340, -820), (-340, -380), (340, -380)], 6, (0.95, 0.95, 0.9))
    k = ease_io(seg(t, 0.1, tx))
    pts = [(-330 + i * 6.6, -800 + 400 * (i / 100) ** 0.7) for i in range(int(100 * k) + 1)]
    if len(pts) > 1:
        c.move_to(*pts[0])
        for p in pts[1:]:
            c.line_to(*p)
        c.set_line_width(8)
        src(c, C('#f2d24a'))
        c.stroke()
    c = F.layer(p=1.0)
    xmas_tree(c, 230, -120, 0.9, pop_in(t, tx, 0.3))
    person(c, -270, 60, 1.0, arms='hips', look=(1, -0.6), mouth='smile', lid=0.4, blink=blink_at(t, 2.0), **OFFICIAL2)
    grade(F, vig=0.45)
    return F


def s42_weird(t, d):
    u = t / d
    cam = path(u, [(0, aim(-60, -240, 1.4)), (1, aim(0, -245, 2.0))])
    F = Frame(cam)
    street(F, t, 'night', 'old', blur_bg=5, seed=42)
    c = F.layer(p=1.0)
    turn = ease(seg(u, 0.3, 0.8))
    lamp_light(c, 0, -260, 320, 0.6, C('#9fb4ff'))
    person(c, 0, 0, 1.0, look=(-0.9 + 0.9 * turn, 0.1), lid=0.45, mouth='smirk' if turn > 0.6 else 'flat',
           blink=0, **HERO)
    if turn > 0.7:
        star(c, 30, -250, 14 * seg(u, 0.7, 0.85) * (1 - seg(u, 0.85, 1)), (1, 1, 1), 0)
    grade(F, vig=0.68, tint=(0.05, 0.08, 0.22, 0.25))
    return F


def s43_buying(t, d):
    u = t / d
    tb = wl('s43', 279)
    tr = wl('s43', 280)
    cam = path(u, [(0, aim(-10, -190, 1.08)), (1, aim(10, -190, 1.2))])
    F = Frame(cam)
    market(F, t)
    c = F.layer(p=1.0)
    basket(c, 60, 120, 200)
    basket(c, -140, 140, 170)
    person(c, -200, 60, 1.0, arms='give', look=(1, 0.2), mouth='smile', blink=blink_at(t, 2.4), body=C('#8a3a5a'),
           hat='conical', tunic=True, pants=C('#3a2030'))
    person(c, 200, 60, 1.0, flip=True, arms='give', look=(1, 0.2), mouth='smile', **HERO)
    cx = lerp(170, -80, ease_io(seg(t, tb - 0.1, tb + 0.35)))
    coin(c, cx, -150, 22, glint=0.5)
    k = ease_io(seg(t, tr - 0.15, tr + 0.35))
    sack(c, lerp(-140, 150, k), lerp(-60, 20, k) + 0, 0.6)
    grade(F, vig=0.42)
    return F


def s44_sacks(t, d):
    u = t / d
    F = Frame(Cam(0, -260, lerp(1.25, 1.4, ease(u))))
    market(F, t, blur=5)
    c = F.layer(p=1.0)
    spots = [(-160, 120), (0, 120), (160, 120), (-80, -40), (80, -40), (0, -200)]
    for i, (x, y) in enumerate(spots):
        k = ease_in(seg(t, 0.05 + i * 0.12, 0.2 + i * 0.12))
        if k > 0:
            sack(c, x, lerp(-1100, y, k), 0.8)
            if k >= 1:
                burst(c, x, y, 110, ease_out(seg(t, 0.2 + i * 0.12, 0.4 + i * 0.12)) * (1 - seg(t, 0.4 + i * 0.12, 0.5 + i * 0.12)))
    grade(F, vig=0.42)
    return F


def s45_family(t, d):
    u = t / d
    ty = wl('s45', 294)
    cam = path(u, [(0, aim(-170, -200, 1.15)), (0.55, aim(-150, -200, 1.2)), (1, aim(60, -600, 0.9))])
    F = Frame(cam)
    street(F, t, 'day', 'old', blur_bg=4, seed=45)
    c = F.layer(p=1.0)
    rnd = random.Random(45)
    for r in range(7):  # towering stack of sacks
        for k in range(4 - r % 2):
            sack(c, 120 + k * 120 + (r % 2) * 60, 20 - r * 140, 0.75, label=rnd.random() < 0.5)
    fam = [(-380, 1.0, dict(body=C('#8a3a5a'), hair='bun', hair_col=C('#1a1410'), tunic=True, pants=C('#3a2030'))),
           (-240, 0.62, dict(body=C('#e0a03a'), hair='short', hair_col=C('#1a1410'), tunic=True, pants=C('#6a4a20'))),
           (-130, 0.55, dict(body=C('#5fae9a'), hair='bun', hair_col=C('#1a1410'), tunic=True, pants=C('#2a4a40'))),
           (-30, 0.85, dict(body=C('#6a5a8a'), hair='grey', hair_col=C('#bbbbbb'), tunic=True, pants=C('#3a3050')))]
    look_up = ease(seg(t, 0.4, 1.0))
    for i, (x, s, kw) in enumerate(fam):
        person(c, x, 20, s, look=(0.5, -0.9 * look_up), mouth='o' if look_up > 0.5 else 'smile', eyes='wide' if look_up > 0.5 else 'normal',
               brows='raised' if look_up > 0.5 else None, blink=blink_at(t, 2.1, i), **kw)
    calendar_page(c, -260, -620, 1.0, 'UN AN', '365', rot=-0.1, col=C('#3f8a3a'))
    burst(c, -260, -620, 140, pop_in(t, ty, 0.3) * (1 - seg(t, ty + 0.3, ty + 0.5)))
    grade(F, vig=0.42)
    return F


def s46_carry(t, d):
    u = t / d
    cam = path(u, [(0, aim(-240, -230, 1.3)), (1, aim(160, -220, 1.35))], lambda v: v)
    F = Frame(cam)
    fields(F, t, 'dusk', dike=False)
    c = F.layer(p=1.0)
    c.rectangle(-4000, -14, 8000, 40)  # dike running across the frame
    fill_stroke(c, C('#b48a5a'), 4)
    x = lerp(-420, 300, u)
    person(c, x, 0, 1.0, arms='carry', step=t * 7, look=(1, 0), mouth='smile', blink=blink_at(t, 2.2),
           hold=shoulder_pole(True, 0.42), **HERO)
    grade(F, vig=0.45, warm_glow=(W * 0.2, H * 0.3, 360, 0.2))
    return F


def s47_shed(t, d):
    u = t / d
    cam = path(u, [(0, aim(0, -170, 1.0, 0.45)), (1, aim(0, -200, 1.2, 0.45))])
    F = Frame(cam)
    fields(F, t, 'dusk', dike=True, path_k=1.5)
    c = F.layer(p=1.0)
    shed(c, 0, 0, 0.6)
    person(c, 120, 40, 0.42, arms='carry', step=t * 6, look=(-1, 0), hold=shoulder_pole(True, 0.42), flip=True, **HERO)
    grade(F, vig=0.5, warm_glow=(W * 0.2, H * 0.3, 360, 0.2))
    return F


def s48_wait(t, d):
    u = t / d
    cam = path(u, [(0, aim(0, -200, 1.2, 0.45)), (0.25, aim(0, -170, 2.4, 0.45)), (1, aim(0, -170, 2.55, 0.45))], ease_out)
    F = Frame(cam)
    fields(F, t, 'dusk', dike=True, path_k=1.5)
    c = F.layer(p=1.0)
    shed(c, 0, 0, 0.6)
    k = pop_in(t, 0.15, 0.25)
    text(c, '?!', 70, -320, 90, (1, 1, 1), INK, 9, k=k, rot=0.1)
    grade(F, vig=0.55, warm_glow=(W * 0.2, H * 0.3, 360, 0.2))
    return F


def s49_feeding(t, d):
    u = t / d
    F = Frame(Cam(0, -120, lerp(1.6, 1.85, ease(u))))
    shed_interior(F, t)
    c = F.layer(p=1.0)
    lamp_light(c, -40, -40, 300, 1.2)
    rnd = random.Random(49)
    for i in range(28):  # glowing eyes in the dark
        x, y = rnd.uniform(-420, 420), rnd.uniform(-420, 260)
        if abs(x + 60) < 170 and y > -260:
            continue
        b = blink_at(t, 2.0, i * 0.3)
        for sx in (-8, 8):
            ellipse(c, x + sx, y, 6, 6 * (1 - b) + 0.5)
            src(c, C('#fff3a0'))
            c.fill()
    person(c, -60, 160, 1.0, arms='scoop', look=(0.6, 0.6), mouth='smile', blink=blink_at(t, 2.2), **HERO)
    for k in range(12):  # rice pouring from his hands
        p = (t * 1.4 + k / 12) % 1
        ellipse(c, -20 + 30 * math.sin(k), 0 + p * 150, 3, 5)
        src(c, (1, 1, 1))
        c.fill()
    rice_pile(c, -20, 170, 140, 40)
    c2 = F.layer(screen=True)  # seen through a gap in the planks
    c2.rectangle(0, 0, W, H)
    c2.rectangle(W * 0.18, H * 0.02, W * 0.64, H * 0.96)
    c2.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    src(c2, C('#1a120c'))
    c2.fill()
    grade(F, vig=0.6)
    return F


def gossip(c, t, n=4, x0=-360, y=40, s=0.85, seed=0, tstart=0.0):
    for i in range(n):
        kw = [CATCH2, TOWN[0], CATCH3, TOWN[4], TOWN[1]][(i + seed) % 5]
        x = x0 + i * 240 * s
        active = int(clamp((t - tstart) * 3, 0, n - 1))
        person(c, x, y, s, flip=False, arms='whisper' if i == active else 'down', look=(1, 0) if i <= active else (0, 0),
               mouth='whisper' if i == active else ('o' if i == active + 1 else 'flat'),
               eyes='wide' if i == active + 1 else 'normal', blink=blink_at(t, 2.3, i), lean=0.12 if i == active else 0, **kw)
        if i == active:
            for k in range(3):
                p = (t * 3 + k / 3) % 1
                c.new_path()
                c.arc(x + 70 * s + p * 60, y - 240 * s, 10 + 20 * p, -0.7, 0.7)
                c.set_line_width(3)
                src(c, (1, 1, 1, 1 - p))
                c.stroke()


def s50_word(t, d):
    u = t / d
    cam = path(u, [(0, aim(-220, -220, 1.35)), (1, aim(220, -220, 1.35))], lambda v: v)
    F = Frame(cam)
    street(F, t, 'day', 'old', blur_bg=4, seed=50)
    c = F.layer(p=1.0)
    gossip(c, t, 4, -380, 30, 0.95)
    grade(F, vig=0.42)
    return F


def s51_soft(t, d):
    u = t / d
    ts = wl('s51', 324)
    cam = path(u, [(0, aim(0, -240, 1.3)), (1, aim(0, -280, 1.45))])
    F = Frame(cam)
    street(F, t, 'day', 'old', blur_bg=4, seed=51)
    c = F.layer(p=1.0)
    laugh = abs(math.sin(t * 9))
    person(c, -150, 30, 1.0, arms='hips', look=(0.4, -0.1), mouth='grin', blink=0.9 if laugh > 0.5 else 0, lean=-0.06 * laugh,
           **CATCH2)
    person(c, 150, 30, 1.0, arms='cheeks', look=(-0.4, -0.1), mouth='grin', blink=0.9, lean=0.06 * laugh, flip=True, **CATCH3)
    k = pop_in(t, ts - 0.4, 0.3)

    def thought(cc):  # the hero hugging a rat, hearts everywhere
        person(cc, 0, 40, 0.42, arms='hug', mouth='smile', blink=1, cheeks=1,
               hold=lambda c3, bh: rat_front(c3, 0, -bh * 0.4, 0.5), **HERO)
        heart(cc, -60, -60, 16)
        heart(cc, 60, -80, 14)
    speech_bubble(c, 0, -460, k * 1.25, thought, w=1.15)
    grade(F, vig=0.42)
    return F


def s52_rat_hotel(t, d):
    u = t / d
    th = wl('s52', 333)
    cam = path(u, [(0, aim(0, -220, 1.0, 0.45)), (1, aim(0, -280, 1.35, 0.45))])
    F = Frame(cam)
    fields(F, t, 'day', dike=True, path_k=1.5)
    c = F.layer(p=1.0)
    k = pop_in(t, th - 0.1, 0.35)
    shed(c, 0, 0, 0.75, sign='RAT HOTEL', sign_k=k, t=t)
    for i, (x, kw) in enumerate(((-230, CATCH2), (230, CATCH3))):
        person(c, x, 40, 0.62, arms='twirl' if i == 0 else 'hips', look=(-0.8 if x > 0 else 0.8, -0.3), mouth='grin',
               blink=blink_at(t, 2.0, i), flip=x > 0, **kw)
    grade(F, vig=0.42)
    return F


def s53_stop(t, d):
    u = t / d
    cam = path(u, [(0, aim(-10, -240, 1.05)), (1, aim(0, -240, 1.18))])
    F = Frame(cam)
    street(F, t, 'day', 'french', blur_bg=4, seed=53)
    c = F.layer(p=1.0)
    stop = ease_out(seg(t, 0.2, 0.6))
    person(c, lerp(-430, -170, stop), 20, 1.05, arms='give' if stop > 0.6 else 'down', step=t * 8 * (1 - stop),
           look=(1, 0.1), mouth='frown', brows='angry', blink=blink_at(t, 2.2), **OFFICIAL)
    hx = lerp(240, 200, stop)
    person(c, hx, 20, 1.0, flip=True, arms='carry', look=(1, -0.1), mouth='o', eyes='wide', step=t * 8 * (1 - stop),
           hold=shoulder_pole(True, 0.42), **HERO)
    grade(F, vig=0.45)
    return F


def s54_enemy(t, d):
    u = t / d
    te = wl('s54', 349)
    cam = path(u, [(0, aim(-40, -240, 2.0)), (1, aim(-40, -240, 2.3))])
    F = Frame(cam)
    street(F, t, 'day', 'french', blur_bg=7, seed=53)
    c = F.layer(p=1.0)
    person(c, -40, 20, 1.0, arms='wag', look=(0.3, 0), mouth='shout' if int(t * 6) % 2 else 'frown', brows='angry',
           lean=0.04 * math.sin(t * 12), **OFFICIAL)
    k = pop_in(t, te - 0.1, 0.25)
    speech_bubble(c, 160, -400, k, lambda cc: flea(cc, 0, -40, 2.2, hop=t * 8))
    grade(F, vig=0.45)
    return F


def s55_friends(t, d):
    u = t / d
    tf = wl('s55', 353)
    cam = path(u, [(0, aim(0, -240, 1.9)), (1, aim(0, -230, 2.15))])
    F = Frame(cam)
    street(F, t, 'day', 'french', blur_bg=7, seed=53)
    c = F.layer(p=1.0)
    person(c, 0, 20, 1.0, arms='carry', look=(-0.3, 0), mouth='smile', lid=0.3, cheeks=0.5,
           hold=shoulder_pole(True, 0.42), blink=blink_at(t, 2.4), **HERO)
    for i, sx in enumerate((-140, 140)):  # rats peeking from the sacks
        k = pop_in(t, tf + i * 0.12, 0.25)
        if k > 0:
            c.save()
            clipped(c, lambda: c.rectangle(sx - 120, -260, 240, 120), lambda: rat_front(c, sx, -150 + 60 * (1 - k), 0.32,
                                                                                       look=(-0.4 * (1 if sx > 0 else -1), 0)))
            c.restore()
    grade(F, vig=0.45)
    return F


def chute(c, x, y, t, flow=1.0, seed=0):
    c.move_to(x - 70, y - 900)
    c.line_to(x + 70, y - 900)
    c.line_to(x + 40, y - 520)
    c.line_to(x - 40, y - 520)
    c.close_path()
    fill_stroke(c, C('#9aa0aa'), 5)
    rnd = random.Random(seed)
    for i in range(int(18 * flow)):
        p = (t * 1.6 + i / 18) % 1
        tail_prop(c, x + rnd.uniform(-30, 30), y - 520 + p * 420, 0.45, rnd.uniform(-1, 1) + p * 4)


def s56_pouring(t, d):
    u = t / d
    cam = path(u, [(0, aim(0, -140, 1.1)), (1, aim(0, -150, 1.22))])
    F = Frame(cam)
    office(F, t)
    c = F.layer(p=1.0)
    chute(c, 150, 0, t, 1.0, 56)
    tail_heap(c, 120, 140, 700, lerp(160, 300, u), seed=56, n=130)
    person(c, -190, 100, 1.0, arms='up', look=(1, -0.6), mouth='o', eyes='wide', brows='shock', sweat=1, **OFFICIAL2)
    grade(F, vig=0.45)
    return F


def s57_thirty(t, d):
    u = t / d
    F = Frame(Cam(60, -180, lerp(1.25, 1.45, ease(u))))
    office(F, t, blur=6)
    c = F.layer(p=1.0)
    chute(c, 120, 0, t, 1.0, 57)
    tail_heap(c, 120, 140, 800, 360, seed=57, n=160)
    counter(c, 60, -430, lerp(20000, 30000, ease_out(seg(t, 0.0, 0.35))), 120, k=pop_in(t, 0.0, 0.25))
    grade(F, vig=0.5)
    return F


def s58_forty(t, d):
    u = t / d
    F = Frame(Cam(60, -220, lerp(1.1, 1.3, ease(u))))
    office(F, t, blur=6)
    c = F.layer(p=1.0)
    chute(c, 120, 0, t, 1.0, 58)
    tail_heap(c, 120, 140, 950, 520, seed=58, n=210)
    person(c, -260, 120, 0.9, arms='up', look=(0.6, -0.8), mouth='scream', eyes='wide', brows='shock', sweat=2, **OFFICIAL2)
    counter(c, 60, -470, lerp(30000, 40000, ease_out(seg(t, 0.0, 0.35))), 130, k=pop_in(t, 0.0, 0.25))
    grade(F, vig=0.5)
    return F


def s59_full(t, d):
    u = t / d
    tf = wl('s59', 370)
    cam = path(u, [(0, aim(0, -300, 1.15, 0.5)), (1, aim(0, 420, 1.15, 0.5))])
    F = Frame(cam)
    sky(F, 'dusk', t)
    c = F.layer(p=1.0)
    villa_row(c, t, 'dusk', seed=59, y=-10)
    soil_cutaway(c, y0=0, depth=1500)
    for i, x in enumerate((-330, 0, 330)):
        tunnel_section(c, x, 440, 150, t, rats=9, seed=59 + i, full=1.0)
    for i in range(4):
        rat_front(c, -300 + i * 200, 280 + 30 * math.sin(t * 3 + i), 0.3 * pop_in(t, tf + i * 0.08, 0.25),
                  look=(0, -0.4), mouth='smile')
    grade(F, vig=0.45)
    return F


def s60_night(t, d):
    u = t / d
    cam = path(u, [(0, aim(100, -900, 1.0, 0.5)), (1, aim(60, -520, 1.15, 0.45))])
    F = Frame(cam)
    street(F, t, 'night', 'french', blur_bg=2, lit=True, seed=60)
    c = F.layer(p=1.0)
    for x in (-300, 300):
        gas_lamp(c, x, 10, 1.0, on=True)
    grade(F, vig=0.6, tint=(0.02, 0.05, 0.18, 0.18))
    return F


def s61_inspector(t, d):
    u = t / d
    cam = path(u, [(0, aim(-200, -240, 1.35)), (1, aim(100, -240, 1.4))], lambda v: v)
    F = Frame(cam)
    street(F, t, 'night', 'french', blur_bg=3, lit=True, seed=61)
    c = F.layer(p=1.0)
    for x in (-500, 0, 500):
        gas_lamp(c, x, -10, 1.0, on=True)
    x = lerp(-240, 120, u)
    lamp_light(c, x + 60, -120, 220, 0.9)
    person(c, x, 20, 1.0, arms='lantern', step=t * 6, look=(1, 0), mouth='flat', blink=blink_at(t, 2.1),
           hand=lambda cc, hx, hy: (stick(cc, [(hx, hy), (hx, hy + 20)], 2.5),
                                   soft_ellipse(cc, hx, hy + 44, 60, 60, C('#ffd98a'), 0.5),
                                   ellipse(cc, hx, hy + 44, 14, 20), fill_stroke(cc, C('#ffe9a8'), 3)), **INSPECTOR)
    grade(F, vig=0.6, tint=(0.02, 0.05, 0.18, 0.15))
    return F


def shoe(c, x, y, s=1.0, lift=0.0):
    c.save()
    c.translate(x, y - lift * 60)
    c.scale(s, s)
    c.rectangle(-30, -260, 60, 200)
    fill_stroke(c, C('#1c2438'), 5)
    c.move_to(-50, -60)
    c.curve_to(-60, 0, 140, 10, 150, -20)
    c.curve_to(150, -60, 60, -70, 30, -80)
    c.line_to(-40, -80)
    c.close_path()
    form_shade(c, lambda: (c.move_to(-50, -60), c.curve_to(-60, 0, 140, 10, 150, -20), c.curve_to(150, -60, 60, -70, 30, -80),
                           c.line_to(-40, -80), c.close_path()), C('#2a2020'), C('#5a4a40'), C('#100c0c'), (-60, -80, 150, 0))
    c.move_to(-50, -60)
    c.curve_to(-60, 0, 140, 10, 150, -20)
    c.curve_to(150, -60, 60, -70, 30, -80)
    c.line_to(-40, -80)
    c.close_path()
    c.set_line_width(5)
    src(c, INK)
    c.stroke()
    stick(c, [(90, -48), (120, -36)], 2.5, (1, 1, 1, 0.5))
    c.restore()


def s62_shoe(t, d):
    u = t / d
    tr = wl('s62', 387)
    F = Frame(Cam(0, -60, lerp(1.7, 1.9, ease(u))))
    street(F, t, 'night', 'french', blur_bg=7, lit=True, seed=61, ground_blur=0)
    c = F.layer(p=1.0)
    lift = abs(math.sin(clamp((t - tr - 0.1) * 4) * PI)) if t > tr + 0.1 else 0
    shoe(c, -40, 60, 1.2, lift)
    p = seg(t, tr - 0.1, tr + 0.35)
    if 0 < p < 1:  # the blur streak of a running rat
        x = lerp(-600, 600, p)
        rat(c, x, 50, 0.7, tail=0.0, bandage=True, step=t * 40, shadow=False)
        for k in range(5):
            stick(c, [(x - 120 - k * 40, 20 + k * 6), (x - 300 - k * 40, 20 + k * 6)], 4, (1, 1, 1, 0.5 - k * 0.08))
    text(c, '!', 60, -260, 110, (1, 1, 1), INK, 10, k=pop_in(t, tr + 0.15, 0.2))
    grade(F, vig=0.6, tint=(0.02, 0.05, 0.18, 0.15))
    return F


def spot_rat(F, t, **kw):
    street(F, t, 'night', 'french', blur_bg=8, lit=True, seed=61)
    c = F.layer(p=1.0)
    soft_ellipse(c, 0, 20, 360, 120, C('#ffe9a8'), 0.55)
    soft_ellipse(c, 0, -160, 300, 300, C('#ffe9a8'), 0.18)
    rat(c, -30, 40, 1.4, look=(0.2, 0.1), blink=blink_at(t, 1.8, 0.3), **kw)
    return c


def s63_a_rat(t, d):
    u = t / d
    F = Frame(Cam(0, -110, lerp(1.7, 1.9, ease(u))))
    spot_rat(F, t, tail=0.0, mouth='smile')
    grade(F, vig=0.65, tint=(0.02, 0.05, 0.18, 0.12))
    return F


def s64_fat(t, d):
    u = t / d
    F = Frame(Cam(0, -120, lerp(1.9, 1.7, ease_out(u))))
    fk = back_out(seg(t, 0.0, 0.35), 2.5)
    spot_rat(F, t, tail=0.0, fat=fk, mouth='grin', cheeks=0.3 * fk)
    grade(F, vig=0.65, tint=(0.02, 0.05, 0.18, 0.12))
    return F


def s65_healthy(t, d):
    u = t / d
    F = Frame(Cam(0, -130, lerp(1.7, 1.85, ease(u))))
    c = spot_rat(F, t, tail=0.0, fat=1.0, pose='flex', mouth='grin', eyes='wide')
    for k in range(5):
        a = k * 1.3 + t * 2
        star(c, 120 * math.cos(a) + 40, -120 + 70 * math.sin(a), 18 * pop_in(t, 0.05 + k * 0.06, 0.2), (1, 1, 1), 0, t)
    grade(F, vig=0.65, tint=(0.02, 0.05, 0.18, 0.12))
    return F


def s66_no_tail(t, d):
    u = t / d
    tn = wl('s66', 396)
    cam = path(u, [(0, aim(-20, -100, 1.8, 0.5)), (0.3, aim(-140, -60, 2.6, 0.5)), (1, aim(-150, -60, 2.8, 0.5))], ease_io)
    F = Frame(cam)
    street(F, t, 'night', 'french', blur_bg=8, lit=True, seed=61)
    c = F.layer(p=1.0)
    soft_ellipse(c, 0, 20, 360, 120, C('#ffe9a8'), 0.55)
    rat(c, -30, 40, 1.4, tail=0.0, fat=1.0, bandage=True, look=(-1, 0), mouth='o', blink=blink_at(t, 1.8))
    text(c, '!', -160, -200, 70, (1, 1, 1), INK, 8, k=pop_in(t, tn, 0.2))
    F.post = isolate_red(lambda T: ease(clamp((T - SHOT_T0['s66'] - tn + 0.15) / 0.3)))
    return F


def s67_another(t, d):
    u = t / d
    cam = path(u, [(0, aim(0, -240, 1.5)), (1, aim(0, -240, 1.7))])
    F = Frame(cam)
    street(F, t, 'night', 'french', blur_bg=5, lit=True, seed=61)
    c = F.layer(p=1.0)
    person(c, 0, 20, 1.0, arms='lantern', look=(-0.8, 0.8), eyes='wide', mouth='o', brows='raised', **INSPECTOR)
    x = lerp(600, -600, seg(t, 0.05, 0.6))
    rat(c, x, 40, 0.6, tail=0.0, bandage=True, flip=True, step=t * 40, look=(-1, 0), mouth='grin')
    grade(F, vig=0.6, tint=(0.02, 0.05, 0.18, 0.15))
    return F


def s68_ten_more(t, d):
    u = t / d
    cam = path(u, [(0, aim(0, -240, 1.35)), (1, aim(0, -260, 1.5))])
    F = Frame(cam)
    street(F, t, 'night', 'french', blur_bg=5, lit=True, seed=61)
    c = F.layer(p=1.0)
    jump = abs(math.sin(clamp(t * 2.2) * PI)) * 70
    person(c, 0, 20 - jump, 1.0, arms='up', look=(0, 0.9), eyes='huge', mouth='scream', brows='shock', sweat=2,
           shadow=False, **INSPECTOR)
    rnd = random.Random(68)
    for i in range(10):
        p = seg(t, 0.1 + i * 0.05, 0.9 + i * 0.05)
        if 0 < p < 1:
            rat(c, lerp(700, -700, p) + rnd.uniform(-40, 40), 50 + rnd.uniform(0, 140), rnd.uniform(0.5, 0.65), tail=0.0,
                bandage=True, flip=True, step=t * 40 + i, look=(-1, 0), mouth='grin')
    grade(F, vig=0.6, tint=(0.02, 0.05, 0.18, 0.15))
    return F


def paw_trail(c, x0, y0, x1, y1, n=16, k=1.0):
    for i in range(int(n * k)):
        p = i / n
        x, y = lerp(x0, x1, p), lerp(y0, y1, p)
        for sd in (-1, 1):
            ellipse(c, x + sd * 10 + (i % 2) * 6, y + sd * 6, 6, 4)
            src(c, (0.85, 0.9, 1, 0.75))
            c.fill()


def s69_follow(t, d):
    u = t / d
    cam = path(u, [(0, aim(-200, -230, 1.3)), (1, aim(180, -230, 1.35))], lambda v: v)
    F = Frame(cam)
    street(F, t, 'night', 'old', blur_bg=4, seed=69)
    c = F.layer(p=1.0)
    paw_trail(c, -900, 120, 900, 80, 40)
    for i, dx in enumerate((-160, 40)):
        x = lerp(-300, 220, u) + dx
        person(c, x, 30, 0.95, arms='lantern', step=t * 7 + i, look=(0.6, 0.8), mouth='flat', brows='raised',
               hand=lambda cc, hx, hy: (soft_ellipse(cc, hx, hy + 44, 70, 70, C('#ffd98a'), 0.5),
                                       ellipse(cc, hx, hy + 44, 14, 20), fill_stroke(cc, C('#ffe9a8'), 3)), **INSPECTOR)
    grade(F, vig=0.6, tint=(0.02, 0.05, 0.18, 0.15))
    return F


def s70_shed_night(t, d):
    """The reveal reuses the s47 framing: same path, same shed, now at night with a light inside."""
    u = t / d
    cam = path(u, [(0, aim(0, -170, 1.0, 0.45)), (1, aim(0, -200, 1.2, 0.45))])
    F = Frame(cam)
    fields(F, t, 'night', dike=True, path_k=1.5)
    c = F.layer(p=1.0)
    shed(c, 0, 0, 0.6, night=True, light=0.0)
    soft_ellipse(c, 0, -60, 60, 80, C('#ffd98a'), 0.25 + 0.1 * math.sin(t * 7))
    for i, dx in enumerate((-90, 90)):
        y = lerp(500, 120, ease_out(u))
        person(c, dx * lerp(1.6, 0.8, u), y, lerp(0.7, 0.45, u), arms='lantern', look=(0, -1), step=t * 6 + i, mouth='flat',
               hand=lambda cc, hx, hy: (soft_ellipse(cc, hx, hy + 44, 70, 70, C('#ffd98a'), 0.5),
                                       ellipse(cc, hx, hy + 44, 14, 20), fill_stroke(cc, C('#ffe9a8'), 3)), **INSPECTOR)
    grade(F, vig=0.6, tint=(0.02, 0.05, 0.18, 0.12))
    return F


def s71_door(t, d):
    u = t / d
    F = Frame(Cam(0, -160, lerp(1.6, 1.9, ease(u))))
    fields(F, t, 'night', dike=True, path_k=1.5, blur_far=6)
    c = F.layer(p=1.0)
    dk = ease_io(seg(t, 0.15, 0.9))
    shed(c, 0, 40, 1.0, door=dk, light=dk, night=True)
    grade(F, vig=0.6, tint=(0.02, 0.05, 0.18, 0.1))
    return F


def s72_cages(t, d):
    u = t / d
    F = Frame(Cam(0, -180, lerp(1.8, 1.45, ease_out(u))))
    shed_interior(F, t)
    c = F.layer(p=1.0)
    lamp_light(c, 0, -200, 500, 1.3)
    cage_wall(c, -480, 200, 6, 4, t, seed=72)
    burst(c, 0, -160, 500, ease_out(seg(t, 0.0, 0.3)) * (1 - seg(t, 0.3, 0.5)))
    grade(F, vig=0.55)
    return F


def s73_stacked(t, d):
    u = t / d
    cam = path(u, [(0, aim(0, 60, 1.25, 0.5)), (1, aim(0, -900, 1.05, 0.5))])
    F = Frame(cam)
    shed_interior(F, t)
    c = F.layer(p=1.0)
    lamp_light(c, 0, -300, 700, 1.3)
    cage_wall(c, -560, 220, 7, 10, t, seed=73)
    c.rectangle(-3000, -1260, 6000, 100)  # the ceiling beam
    fill_stroke(c, C('#4a2e18'), 6)
    for k in range(2):
        person(c, -200 + k * 400, 400, 1.1, look=(0, -1), mouth='o', eyes='wide', arms='lantern', **INSPECTOR)
    grade(F, vig=0.55)
    return F


def s74_chewing(t, d):
    u = t / d
    F = Frame(Cam(0, -120, lerp(1.25, 1.4, ease(u))))
    shed_interior(F, t, blur=4)
    c = F.layer(p=1.0)
    lamp_light(c, 0, -160, 400, 1.3)
    cage(c, -260, 0, 520, 340, rats=3, t=t, seed=74)
    grade(F, vig=0.5)
    return F


def arrow(c, x0, y0, x1, y1, col=INK, lw=8, k=1.0):
    if k <= 0:
        return
    x1, y1 = lerp(x0, x1, k), lerp(y0, y1, k)
    stick(c, [(x0, y0), (x1, y1)], lw, col)
    a = math.atan2(y1 - y0, x1 - x0)
    c.move_to(x1 + math.cos(a) * 20, y1 + math.sin(a) * 20)
    c.line_to(x1 + math.cos(a + 2.4) * 28, y1 + math.sin(a + 2.4) * 28)
    c.line_to(x1 + math.cos(a - 2.4) * 28, y1 + math.sin(a - 2.4) * 28)
    c.close_path()
    src(c, col)
    c.fill()


def s75_never_paid(t, d):
    u = t / d
    tn = wl('s75', 442)
    F = Frame(Cam(0, -120, lerp(1.2, 1.35, ease(u))))
    paper_bg(F)
    c = F.layer(p=1.0)
    coin(c, -170, -260, 70, glint=0.4, label='1')
    rat(c, 100, 60, 1.2, dead=True)
    arrow(c, -120, -180, 30, -40, INK, 9, ease_out(seg(t, 0.1, 0.6)))
    k = pop_in(t, tn, 0.25)
    if k > 0:
        c.save()
        c.translate(-45, -110)
        c.scale(k, k)
        stick(c, [(-70, -70), (70, 70)], 18, C('#d6332f'))
        stick(c, [(70, -70), (-70, 70)], 18, C('#d6332f'))
        c.restore()
    return F


def s76_paid_tails(t, d):
    u = t / d
    F = Frame(Cam(0, -120, lerp(1.25, 1.4, ease(u))))
    paper_bg(F)
    c = F.layer(p=1.0)
    coin(c, -170, -260, 70, glint=0.6 + 0.4 * math.sin(t * 6), label='1')
    tail_prop(c, 110, 40, 1.8, 0.0, 0.3 * math.sin(t * 3))
    soft_ellipse(c, 110, 40, 220, 90, C('#ffd23f'), 0.3 * pop_in(t, 0.3, 0.3))
    arrow(c, -120, -180, 40, -40, C('#3f8a3a'), 9, ease_out(seg(t, 0.05, 0.45)))
    return F


def s77_still_rat(t, d):
    u = t / d
    ts = wl('s77', 458)
    F = Frame(Cam(0, -120, lerp(1.25, 1.35, ease(u))))
    paper_bg(F)
    c = F.layer(p=1.0)
    rat(c, -60, -160, 1.0, tail=0.0, bandage=True, look=(0.3, 0), mouth='smile', blink=blink_at(t, 2.0))
    text(c, '=', 0, 0, 110, INK, None, k=pop_in(t, ts - 0.1, 0.25))
    k = pop_in(t, ts + 0.1, 0.25)
    if k > 0:
        c.save()
        c.translate(0, 230)
        c.scale(k, k)
        rat(c, 30, 0, 1.0, tail=1.0, look=(0.3, 0), mouth='smile', blink=blink_at(t, 2.4), tail_wave=t * 3)
        c.restore()
    return F


def s78_babies(t, d):
    u = t / d
    tb = wl('s78', 467)
    F = Frame(Cam(0, 60, lerp(1.3, 1.45, ease(u))))
    tunnel(F, t, light=0.8, clean=0.6, blur_far=4, vp=(0, -100))
    c = F.layer(p=1.0)
    lamp_light(c, 0, 80, 380, 1.0)
    rat(c, -40, 140, 1.0, fat=0.6, tail=0.0, bandage=True, look=(0.2, 0.4), mouth='smile', blink=blink_at(t, 2.2))
    rnd = random.Random(78)
    for i in range(14):
        k = pop_in(t, tb - 0.3 + i * 0.06, 0.2)
        if k > 0:
            rat(c, rnd.uniform(-330, 330), 170 + rnd.uniform(0, 110), 0.38 * k, baby=True, tail=0.0, flip=rnd.random() < 0.5,
                look=(rnd.uniform(-1, 1), 0), blink=blink_at(t, 1.8, i), shadow=False)
    grade(F, vig=0.5)
    return F


def s79_new_tails(t, d):
    u = t / d
    tt = wl('s79', 480)
    F = Frame(Cam(0, -60, lerp(1.25, 1.4, ease(u))))
    tunnel(F, t, light=0.8, clean=0.6, blur_far=4)
    c = F.layer(p=1.0)
    rnd = random.Random(79)
    grow = ease_out(seg(t, tt - 1.0, tt + 0.1))
    for i in range(8):
        x, y = -200 + (i % 3) * 210 + rnd.uniform(-20, 20) + 40 * (i // 3 == 1), -120 + (i // 3) * 200
        rat(c, x, y, 0.62, baby=True, tail=grow, flip=False, look=(-0.6, -0.3), blink=blink_at(t, 1.8, i), shadow=False,
            tail_wave=t * 3 + i)
        coin(c, x - 130, y - 70, 20, glint=pop_in(t, tt + i * 0.03, 0.2), label='1', edge=pop_in(t, tt + i * 0.03, 0.2))
    grade(F, vig=0.5)
    return F


def s80_not_mistake(t, d):
    """Callback to the s30 framing: the release, now read as a plan."""
    u = t / d
    tm = wl('s80', 489)
    cam = path(u, [(0, aim(-80, -230, 1.45)), (1, aim(-110, -230, 1.75))])
    F = Frame(cam)
    tunnel(F, t, light=0.75, clean=0.6, vp=(0, -330))
    c = F.layer(p=1.0)
    lamp_light(c, -80, -100, 380, 0.9)
    go = ease_in(seg(t, 0.2, 1.4))
    person(c, -150, 130, 1.0, arms='wag', look=(1, 0.4) if t < tm else (-0.2, 0), mouth='smirk', lid=0.35,
           blink=blink_at(t, 2.6), **HERO)
    rat(c, lerp(40, 520, go), 140, 0.85, fat=1.0, tail=0.0, bandage=True, step=t * 20, look=(1, 0), mouth='grin')
    k = pop_in(t, tm, 0.3)
    if k > 0:  # wink
        star(c, -110, -300, 24 * k, GOLD, 3, t)
    grade(F, vig=0.5, warm_glow=(W * 0.35, H * 0.45, 260, 0.12))
    return F


def s81_investment(t, d):
    u = t / d
    ti = wl('s81', 493)
    F = Frame(Cam(0, -260, lerp(0.9, 1.0, ease(u))))
    paper_bg(F)
    c = F.layer(p=1.0)
    c.translate(0, -150)
    stick(c, [(-300, -600), (-300, 100), (320, 100)], 7)
    k = ease_in(seg(t, 0.0, ti + 0.4))
    pts = [(-300 + i * 6.2, 100 - 650 * (i / 100) ** 2.4) for i in range(int(100 * k) + 1)]
    if len(pts) > 1:
        c.move_to(*pts[0])
        for p in pts[1:]:
            c.line_to(*p)
        c.set_line_width(12)
        src(c, C('#3f8a3a'))
        c.stroke()
        rat(c, pts[-1][0] - 10, pts[-1][1] - 10, 0.45, tail=0.0, bandage=True, look=(0.5, -0.5), mouth='grin', shadow=False,
            rot=-0.6 * k)
    for i in range(5):  # coin stacks under the curve
        n = int(lerp(1, 9, i / 4) * k)
        for j in range(n):
            coin(c, -200 + i * 110, 80 - j * 18, 34, label='', edge=1.0)
    return F


def s82_gardener(t, d):
    u = t / d
    tw = wl('s82', 501)
    tp = wl('s82', 503)
    cam = path(u, [(0, aim(-60, -230, 1.35)), (1, aim(-20, -230, 1.5))])
    F = Frame(cam)
    garden(F, t)
    c = F.layer(p=1.0)
    up = ease_out(seg(t, tw - 0.1, tw + 0.4))
    weed(c, 130, 10, 1.0, up=up, roots=False, t=t)
    weed(c, 330, 10, 0.8, t=t)
    person(c, -60, 0, 1.0, arms='give', look=(1, 0.5), mouth='grin', blink=blink_at(t, 2.2), body=C('#5a7a4a'), hat='conical',
           tunic=True, pants=C('#33402a'), lean=-0.1 * up)
    coin(c, 130, -360, 36, glint=pop_in(t, tp, 0.25), label='1', edge=pop_in(t, tp, 0.25))
    grade(F, vig=0.4)
    return F


def s83_roots(t, d):
    u = t / d
    tr = wl('s83', 509)
    cam = path(u, [(0, aim(0, -240, 1.25, 0.4)), (1, aim(0, -60, 1.3, 0.45))])
    F = Frame(cam)
    garden(F, t)
    c = F.layer(p=1.0)
    soil_cutaway(c, y0=10, depth=900)
    weed(c, 130, 10, 1.0, up=0, roots=True, sprout=pop_in(t, tr, 0.4), face=True, t=t)
    person(c, -140, 10, 1.0, arms='hips', look=(-0.2, 0), mouth='smirk', lid=0.6 * seg(t, tr - 0.2, tr), body=C('#5a7a4a'),
           hat='conical', tunic=True, pants=C('#33402a'))
    glow = 0.5 + 0.5 * math.sin(t * 5)
    soft_ellipse(c, 130, 90, 140, 80, C('#ffe9a8'), 0.25 * glow)
    grade(F, vig=0.4)
    return F


def s84_real_life(t, d):
    u = t / d
    tb = wl('s84', 515)
    ts = wl('s84', 520)
    F = Frame(Cam(0, -240, lerp(1.25, 1.45, ease(u))))
    street(F, t, 'sepia', 'french', blur_bg=5, seed=84)
    c = F.layer(p=1.0)
    c.rectangle(-700, -700, 1400, 680)
    fill_stroke(c, C('#d9c8a0'), 5)
    poster(c, 0, -330, 1.0, 1.0)
    pk = seg(t, tb, tb + 0.6)
    if 0 < pk < 1:  # the backfire: a sooty puff blows out of the notice
        for k in range(6):
            soft_ellipse(c, 40 * math.cos(k) * (1 + 3 * pk), -330 + 40 * math.sin(k * 1.7) * (1 + 3 * pk), 90 * pk + 20, 80 * pk + 20,
                         C('#3a3430'), 0.6 * (1 - pk))
        burst(c, 0, -330, 320, ease_out(pk))
    sk = ease_in(seg(t, ts - 0.12, ts))
    if sk > 0:
        c.save()
        c.translate(0, -330)
        c.rotate(-0.25)
        c.scale(lerp(2.5, 1.0, sk), lerp(2.5, 1.0, sk))
        c.rectangle(-180, -60, 360, 120)
        c.set_line_width(12)
        src(c, (0.75, 0.12, 0.1, sk))
        c.stroke()
        text(c, 'FERMÉ', 0, 0, 84, (0.75, 0.12, 0.1, sk), None)
        c.restore()
    F.post = vintage_post(1.0)
    return F


def s85_never_wanted(t, d):
    u = t / d
    cam = path(u, [(0, aim(-40, -230, 1.3)), (1, aim(-40, -230, 1.55))])
    F = Frame(cam)
    fields(F, t, 'dusk', dike=False, blur_far=4)
    c = F.layer(p=1.0)
    c.rectangle(-4000, -14, 8000, 40)
    fill_stroke(c, C('#b48a5a'), 4)
    shed(c, 330, 20, 0.8, door=1.0, light=0.7, sign='RAT HOTEL', t=t)
    person(c, -60, 30, 1.0, arms='hug', look=(0.2, 0.3), mouth='smile', blink=blink_at(t, 2.4), cheeks=0.6,
           hold=lambda cc, bh: rat_front(cc, 0, -bh * 0.38, 0.45, mouth='smile'), **HERO)
    for i in range(4):
        rat(c, -260 + i * 120 + (i > 1) * 200, 70 + (i % 2) * 20, 0.4, tail=0.0, bandage=True, step=t * 10 + i,
            flip=i % 2 == 0, look=(0, -0.5), mouth='smile', blink=blink_at(t, 2, i))
    grade(F, vig=0.45, warm_glow=(W * 0.2, H * 0.3, 360, 0.25))
    return F


def s86_money(t, d):
    u = t / d
    tm = wl('s86', 538)
    F = Frame(Cam(0, -120, lerp(1.4, 1.6, ease(u))))
    paper_bg(F, C('#efe4c8'), lines=False)
    c = F.layer(p=1.0)
    m = ease_io(seg(t, tm - 0.25, tm + 0.15))
    if m < 0.5:
        tail_prop(c, 0, -100, 2.0 * (1 - m * 2), m * 6, 0.3 * math.sin(t * 3))
    else:
        coin(c, 0, -100, 110 * (m - 0.5) * 2, glint=pop_in(t, tm + 0.05, 0.3), label='1')
    burst(c, 0, -100, 260, ease_out(seg(t, tm - 0.05, tm + 0.25)) * (1 - seg(t, tm + 0.25, tm + 0.45)))
    return F


def s87_bank(t, d):
    u = t / d
    tb = wl('s87', 544)
    cam = path(u, [(0, aim(0, -200, 0.95, 0.45)), (0.55, aim(0, -200, 1.15, 0.45)), (1, aim(0, -150, 1.6, 0.45))])
    F = Frame(cam)
    c = F.layer(screen=True)
    src(c, C('#2a2620'))
    c.paint()
    c = F.layer(p=1.0)
    c.rectangle(-1500, -1500, 3000, 1500)
    src(c, C('#4a4a50'))
    c.fill()
    for i in range(-8, 9):
        stick(c, [(i * 120, -1500), (i * 120, 0)], 2, (0, 0, 0, 0.2))
    c.rectangle(-1500, 0, 3000, 1500)
    src(c, C('#2a2a30'))
    c.fill()
    ok = ease_io(seg(t, 0.0, tb + 0.1))
    vault(c, 0, -200, 0.9, open_k=ok, t=t)
    if ok > 0.4:  # the fat tailless rat lounging on the gold
        k = pop_in(t, tb - 0.05, 0.3)
        rat(c, -20, -60, 0.95 * k + 0.001, fat=1.0, tail=0.0, bandage=True, pose='sit', look=(0, 0.1), mouth='grin',
            blink=blink_at(t, 1.6, 0.4), shadow=False)
    for k in range(4):
        star(c, -240 + k * 160, -540, 22 * pop_in(t, tb + 0.2 + k * 0.07, 0.2), GOLD, 3, t)
    grade(F, vig=0.55, warm_glow=(W * 0.5, H * 0.45, 300, 0.2 * ok))
    return F


# shot list: (first word index, fn)
SHOTS = [
    (0, s01_hook), (7, s02_snip), (13, s03_let_go), (17, s04_paid), (23, s05_rewind), (30, s06_french),
    (36, s07_proud), (43, s08_sewer_new), (47, s09_tunnels), (52, s10_under_french), (59, s11_rats_love),
    (65, s12_dark_warm), (71, s13_kitchen), (79, s14_hotel), (87, s15_fleas), (91, s16_plague), (95, s17_offer),
    (101, s18_one_cent), (112, s19_buckets), (121, s20_cart), (126, s21_buried), (135, s22_smell), (142, s23_rule),
    (149, s24_no_rat), (154, s25_tail), (158, s26_hero), (171, s27_climb), (177, s28_fattest), (184, s29_snip_again),
    (188, s30_free), (193, s31_lost_it), (200, s32_kill_it), (209, s33_haircut), (214, s34_pocket), (221, s35_hundred),
    (230, s36_thousand), (238, s37_thrilled), (242, s38_june), (247, s39_twenty_k), (256, s40_math), (261, s41_christmas),
    (270, s42_weird), (275, s43_buying), (281, s44_sacks), (284, s45_family), (295, s46_carry), (305, s47_shed),
    (310, s48_wait), (312, s49_feeding), (316, s50_word), (319, s51_soft), (325, s52_rat_hotel), (335, s53_stop),
    (345, s54_enemy), (351, s55_friends), (355, s56_pouring), (361, s57_thirty), (362, s58_forty), (363, s59_full),
    (373, s60_night), (376, s61_inspector), (386, s62_shoe), (391, s63_a_rat), (393, s64_fat), (394, s65_healthy),
    (395, s66_no_tail), (398, s67_another), (400, s68_ten_more), (403, s69_follow), (412, s70_shed_night),
    (421, s71_door), (425, s72_cages), (426, s73_stacked), (433, s74_chewing), (438, s75_never_paid),
    (447, s76_paid_tails), (451, s77_still_rat), (461, s78_babies), (470, s79_new_tails), (481, s80_not_mistake),
    (490, s81_investment), (494, s82_gardener), (504, s83_roots), (510, s84_real_life), (523, s85_never_wanted),
    (532, s86_money), (539, s87_bank),
]


def install(words, total):
    R.SHOTS = SHOTS
    WORDS[:] = words
    b = R.shot_bounds(words, total)
    for (t0, _), (_, fn) in zip(b, SHOTS):
        SHOT_T0[fn.__name__.split('_')[0]] = t0
    return b


if __name__ == '__main__':
    import json
    args = sys.argv[1:]
    wpath = os.path.join(HERE, 'words.json')
    meta = json.load(open(wpath))
    install(meta['words'], meta['duration'])
    R.main(args + ['--words', wpath])
