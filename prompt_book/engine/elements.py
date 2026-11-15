# Vector props, character, HUD, diagrams.
import math
import numpy as np
import skia
from core import *
from assets import *

# ================================================================ generic shapes
def arrow(c, x0, y0, x1, y1, color, width=6, head=22, alpha=1.0, k=1.0, glow_=0.0):
    """Arrow drawn progressively (k 0..1)."""
    if k <= 0 or alpha <= 0:
        return
    x1k, y1k = lerp(x0, x1, k), lerp(y0, y1, k)
    ang = math.atan2(y1k - y0, x1k - x0)
    p = P(with_alpha(color, alpha), stroke=width, cap='round')
    hx, hy = x1k - math.cos(ang) * head * .6, y1k - math.sin(ang) * head * .6
    if glow_:
        c.drawLine(x0, y0, hx, hy, P(with_alpha(color, alpha * glow_ * .5), stroke=width * 3, blur=8))
    c.drawLine(x0, y0, hx, hy, p)
    pa = path_from([(x1k, y1k),
                    (x1k - math.cos(ang - .45) * head, y1k - math.sin(ang - .45) * head),
                    (x1k - math.cos(ang + .45) * head, y1k - math.sin(ang + .45) * head)], True)
    c.drawPath(pa, P(with_alpha(color, alpha)))

def draw_x(c, cx, cy, size, k, color=None, width=None, alpha=1.0):
    """Animated red cross (two strokes)."""
    color = hexc(PAL['danger']) if color is None else color
    width = size * .16 if width is None else width
    if k <= 0:
        return
    k1, k2 = clamp(k * 2), clamp(k * 2 - 1)
    p = P(with_alpha(color, alpha), stroke=width, cap='round')
    pg = P(with_alpha(color, alpha * .35), stroke=width * 2.2, cap='round', blur=6)
    s = size / 2
    for pp in (pg, p):
        c.drawLine(cx - s, cy - s, cx - s + 2 * s * k1, cy - s + 2 * s * k1, pp)
        if k2 > 0:
            c.drawLine(cx + s, cy - s, cx + s - 2 * s * k2, cy - s + 2 * s * k2, pp)

def draw_check(c, cx, cy, size, k, color=None, alpha=1.0):
    color = hexc(PAL['ok']) if color is None else color
    if k <= 0:
        return
    pts = [(cx - size * .5, cy), (cx - size * .15, cy + size * .35), (cx + size * .55, cy - size * .4)]
    L1 = math.dist(pts[0], pts[1]); L2 = math.dist(pts[1], pts[2]); d = (L1 + L2) * k
    pa = skia.Path(); pa.moveTo(*pts[0])
    if d <= L1:
        pa.lineTo(lerp(pts[0][0], pts[1][0], d / L1), lerp(pts[0][1], pts[1][1], d / L1))
    else:
        pa.lineTo(*pts[1]); u = (d - L1) / L2
        pa.lineTo(lerp(pts[1][0], pts[2][0], u), lerp(pts[1][1], pts[2][1], u))
    c.drawPath(pa, P(with_alpha(color, alpha * .4), stroke=size * .3, cap='round', join='round', blur=6))
    c.drawPath(pa, P(with_alpha(color, alpha), stroke=size * .14, cap='round', join='round'))

def dashed(c, pts, color, width=4, on=14, off=10, phase=0.0, alpha=1.0, k=1.0):
    pa = path_from(pts)
    if k < 1:
        meas = skia.PathMeasure(pa, False)
        L = meas.getLength()
        seg = skia.Path(); meas.getSegment(0, L * k, seg, True); pa = seg
    p = P(with_alpha(color, alpha), stroke=width, cap='round')
    p.setPathEffect(skia.DashPathEffect.Make([on, off], phase))
    c.drawPath(pa, p)

def stroke_path_k(c, pa, paint, k):
    if k >= 1:
        c.drawPath(pa, paint); return
    if k <= 0:
        return
    meas = skia.PathMeasure(pa, False)
    seg = skia.Path(); meas.getSegment(0, meas.getLength() * k, seg, True)
    c.drawPath(seg, paint)

# ================================================================ labels / tags / cards
TAG_STYLE = {
    'hist': ('#FFB347', '#2A1810'),   # historical reconstruction (amber)
    'fict': ('#6FD3FF', '#07152a'),   # fictional
    'model': ('#B79BFF', '#140d2e'),  # model-based illustration
    'concept': ('#9FE3FF', '#07152a'),
    'danger': ('#FF3B30', '#2a0806'),
}

def draw_tag(c, text, x, y, kind='hist', alpha=1.0, size=19, align='left'):
    if alpha <= 0:
        return
    fg, bg = TAG_STYLE[kind]
    f = mono(size, 'semi')
    tw_ = f.measureText(text)
    w, h = tw_ + 44, size * 1.85
    if align == 'center':
        x -= w / 2
    elif align == 'right':
        x -= w
    rrect(c, x, y, w, h, h / 2, P(hexc(bg, .78 * alpha)))
    rrect(c, x, y, w, h, h / 2, P(hexc(fg, .9 * alpha), stroke=1.6))
    c.drawCircle(x + 17, y + h / 2, 4.5, P(hexc(fg, alpha)))
    draw_text(c, text, x + 30, y + h * .5 + size * .36, f, hexc(fg), alpha=alpha)
    return w

def label_line(c, x0, y0, x1, y1, text, color=None, alpha=1.0, k=1.0, size=26, sub=None, align=None):
    """Callout: dot at (x0,y0), line to (x1,y1), text beyond."""
    color = hexc('#FFF1D6') if color is None else color
    if alpha <= 0 or k <= 0:
        return
    c.drawCircle(x0, y0, 6, P(with_alpha(color, alpha)))
    c.drawCircle(x0, y0, 12, P(with_alpha(color, alpha * .5), stroke=2))
    kk = e_out(clamp(k * 1.5))
    xe, ye = lerp(x0, x1, kk), lerp(y0, y1, kk)
    c.drawLine(x0, y0, xe, ye, P(with_alpha(color, alpha * .9), stroke=2.5))
    ka = clamp(k * 1.5 - .5)
    if ka > 0:
        al = align or ('left' if x1 >= x0 else 'right')
        dx = 14 if al == 'left' else -14
        tw1 = font(size, 'bold').measureText(text)
        tw2 = font(size * .7, 'medium').measureText(sub) if sub else 0
        tw_ = max(tw1, tw2)
        tx = x1 + dx
        if al == 'left' and tx + tw_ > W - 40:
            tx = W - 40 - tw_
        if al == 'right' and tx - tw_ < 40:
            tx = 40 + tw_
        ty = y1 + size * .35
        if tx != x1 + dx:
            ty = y1 + size * 1.3 if y1 < H / 2 else y1 - size * 1.6
        draw_text(c, text, tx, ty, font(size, 'bold'), color, al, alpha * ka, shadow=1)
        if sub:
            draw_text(c, sub, tx, ty + size * 1.05, font(size * .7, 'medium'), with_alpha(color, .8), al, alpha * ka, shadow=1)

def card(c, x, y, w, h, alpha=1.0, color='#0b1330', border='#3D5A9E', r=22):
    if alpha <= 0:
        return
    rrect(c, x + 6, y + 10, w, h, r, P(rgba(0, 0, 0, .35 * alpha), blur=14))
    rrect(c, x, y, w, h, r, P(hexc(color, .86 * alpha)))
    rrect(c, x, y, w, h, r, P(hexc(border, .9 * alpha), stroke=2))

def big_number(c, text, x, y, size, color, t, t0, alpha=1.0, glow_=.5, unit=None, unit_color=None, weight='black'):
    """Big stat number with pop and optional unit."""
    if t < t0:
        return
    k = prog(t, t0, t0 + .4)
    sc = lerp(1.25, 1.0, e_out(k))
    c.save(); c.translate(x, y); c.scale(sc, sc)
    f = font(size, weight)
    w = f.measureText(text)
    uw = 0
    if unit:
        fu = font(size * .42, 'bold')
        uw = fu.measureText(unit) + size * .12
    x0 = -(w + uw) / 2
    draw_text(c, text, x0, 0, f, color, 'left', alpha * e_out(min(1, k * 2)), glow=glow_)
    if unit:
        draw_text(c, unit, x0 + w + size * .12, 0, fu, unit_color or color, 'left', alpha * e_out(min(1, k * 2)))
    c.restore()

def chapter_card(c, num, title, t, t0, t1):
    """Minimal chapter marker top-left."""
    a = fade_window(t, t0, t1, .5, .6)
    if a <= 0:
        return
    k = e_out(prog(t, t0, t0 + .7))
    x, y = 120, 160
    c.drawLine(x, y + 18, x + 220 * k, y + 18, P(hexc('#E3B47A', a), stroke=3))
    draw_text(c, f'CHAPTER {num:02d}', x, y, mono(22, 'semi'), hexc('#E3B47A'), alpha=a, spacing=3)
    draw_text(c, title, x, y + 78, font(58, 'black'), hexc('#FFF1D6'), alpha=a * k, shadow=1)

# ================================================================ HUD
HUDC = '#9FE3FF'

def hud_panel(c, x, y, w, h, title=None, alpha=1.0, color=HUDC, warn=False):
    if alpha <= 0:
        return
    col = PAL['danger'] if warn else color
    rrect(c, x, y, w, h, 14, P(hexc('#06101f', .62 * alpha)))
    rrect(c, x, y, w, h, 14, P(hexc(col, .55 * alpha), stroke=1.5))
    # corner brackets
    L = 16
    pc = P(hexc(col, alpha), stroke=3)
    for (cx_, cy_, sx, sy) in ((x, y, 1, 1), (x + w, y, -1, 1), (x, y + h, 1, -1), (x + w, y + h, -1, -1)):
        c.drawLine(cx_, cy_ + sy * 2, cx_ + sx * L, cy_ + sy * 2, pc)
        c.drawLine(cx_ + sx * 2, cy_, cx_ + sx * 2, cy_ + sy * L, pc)
    if title:
        draw_text(c, title, x + 18, y + 30, mono(17, 'semi'), hexc(col), alpha=alpha * .9, spacing=1.5)

def hud_readout(c, x, y, w, label, value, unit='', alpha=1.0, color=HUDC, warn=False, sub=None, size=44):
    """Panel with label + big value."""
    h = size * 2.05 + (24 if sub else 0)
    hud_panel(c, x, y, w, h, label, alpha, color, warn)
    col = hexc(PAL['danger']) if warn else hexc('#FFFFFF')
    f = mono(size, 'bold')
    draw_text(c, value, x + 18, y + 34 + size * .95, f, col, alpha=alpha)
    if unit:
        vw = f.measureText(value)
        draw_text(c, unit, x + 26 + vw, y + 34 + size * .95, mono(size * .45, 'semi'), hexc(color), alpha=alpha)
    if sub:
        draw_text(c, sub, x + 18, y + 34 + size * .95 + 30, mono(16, 'medium'), hexc(color), alpha=alpha * .8)
    return h

def draw_gauge(c, cx, cy, r, frac, label, value_text, alpha=1.0, color=HUDC, warn_from=0.75, ticks=10, tick_labels=None, sub=None):
    if alpha <= 0:
        return
    a0, a1 = 135, 405
    c.drawCircle(cx, cy, r * 1.08, P(hexc('#06101f', .7 * alpha)))
    c.drawCircle(cx, cy, r * 1.08, P(hexc(color, .4 * alpha), stroke=2))
    rect = skia.Rect(cx - r, cy - r, cx + r, cy + r)
    c.drawArc(rect, a0, 270, False, P(hexc(color, .25 * alpha), stroke=r * .09))
    wa = a0 + 270 * warn_from
    c.drawArc(rect, wa, 270 * (1 - warn_from), False, P(hexc(PAL['danger'], .55 * alpha), stroke=r * .09))
    f = clamp(frac)
    col = hexc(PAL['danger']) if frac >= warn_from else hexc(color)
    c.drawArc(rect, a0, 270 * f, False, P(with_alpha(col, alpha), stroke=r * .09, cap='round'))
    for i in range(ticks + 1):
        ang = math.radians(a0 + 270 * i / ticks)
        c.drawLine(cx + math.cos(ang) * r * .8, cy + math.sin(ang) * r * .8, cx + math.cos(ang) * r * .9, cy + math.sin(ang) * r * .9,
                   P(hexc(color, .8 * alpha), stroke=2.5))
        if tick_labels and i < len(tick_labels) and tick_labels[i]:
            draw_text(c, tick_labels[i], cx + math.cos(ang) * r * .66, cy + math.sin(ang) * r * .66 + 7, mono(r * .11, 'medium'), hexc(color), 'center', alpha * .8)
    ang = math.radians(a0 + 270 * min(f, 1.04))
    c.drawLine(cx, cy, cx + math.cos(ang) * r * .78, cy + math.sin(ang) * r * .78, P(with_alpha(col, alpha), stroke=r * .045, cap='round'))
    c.drawCircle(cx, cy, r * .07, P(with_alpha(col, alpha)))
    draw_text(c, value_text, cx, cy + r * .48, mono(r * .26, 'bold'), hexc('#FFFFFF'), 'center', alpha)
    draw_text(c, label, cx, cy + r * .72, mono(r * .12, 'semi'), hexc(color), 'center', alpha * .9, spacing=1.5)
    if sub:
        draw_text(c, sub, cx, cy + r * 1.32, font(r * .15, 'semi'), hexc('#FFF1D6'), 'center', alpha * .9)

def draw_thermo(c, x, y, h, frac, value_text, alpha=1.0, cold='#6FD3FF', hot='#FF6A3D', marks=None):
    """Vertical thermometer. frac 0..1."""
    if alpha <= 0:
        return
    w = 34
    rrect(c, x - w / 2 - 6, y - 6, w + 12, h + 12, (w + 12) / 2, P(hexc('#06101f', .75 * alpha)))
    rrect(c, x - w / 2 - 6, y - 6, w + 12, h + 12, (w + 12) / 2, P(hexc(HUDC, .5 * alpha), stroke=2))
    f = clamp(frac)
    fill_h = max(w, h * f)
    col = mixc(cold, hot, f)
    rrect(c, x - w / 2, y + h - fill_h, w, fill_h, w / 2, P(with_alpha(col, alpha)))
    c.drawCircle(x, y + h + 18, 30, P(with_alpha(col, alpha)))
    c.drawCircle(x, y + h + 18, 34, P(hexc(HUDC, .5 * alpha), stroke=2))
    if marks:
        for fr, txt in marks:
            yy = y + h - h * fr
            c.drawLine(x + w / 2 + 6, yy, x + w / 2 + 22, yy, P(hexc(HUDC, .7 * alpha), stroke=2))
            draw_text(c, txt, x + w / 2 + 30, yy + 7, mono(18, 'medium'), hexc(HUDC), alpha=alpha * .8)
    draw_text(c, value_text, x, y - 26, mono(40, 'bold'), hexc('#FFFFFF'), 'center', alpha)

def signal_bars(c, x, y, level, alpha=1.0, n=5, color=None, lost=False):
    color = hexc(PAL['ok']) if color is None else color
    for i in range(n):
        h = 12 + i * 9
        on = level * n > i + .2
        col = hexc(PAL['danger'], .9) if lost else (color if on else hexc('#ffffff', .15))
        rrect(c, x + i * 16, y - h, 11, h, 3, P(with_alpha(col, alpha)))

# ================================================================ spacecraft
def draw_galileo_entry(c, x, y, s=1.0, ang=0.0, heat=0.0, t=0.0, alpha=1.0):
    """Galileo entry probe aeroshell, side view. Nose points along +x before rotation `ang` (deg)."""
    if alpha <= 0:
        return
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(s, s)
    if heat > 0:
        # shock layer glow in front of nose
        glow(c, 70, 0, 260 * (0.6 + heat), hexc('#ff7a2a'), alpha * heat * .9)
        glow(c, 50, 0, 150 * (0.6 + heat), hexc('#fff0c8'), alpha * heat)
    # afterbody (conical back cover) - gold thermal blanket
    back = path_from([(-10, -78), (-10, 78), (-92, 34), (-92, -34)], True)
    c.drawPath(back, P(shader=lin((0, -78), (0, 78), [hexc('#f2cf72', alpha), hexc('#b8862d', alpha), hexc('#6b4a17', alpha)])))
    c.drawPath(back, P(hexc('#3a2a10', alpha * .8), stroke=2))
    for i in range(4):
        xx = -22 - i * 18
        c.drawLine(xx, -70 + i * 9.5, xx, 70 - i * 9.5, P(hexc('#fff3c4', .25 * alpha), stroke=1.5))
    # forebody heat shield: blunt cone (nose to +x)
    shield = skia.Path()
    shield.moveTo(-10, -82); shield.lineTo(36, -24)
    shield.quadTo(52, 0, 36, 24)
    shield.lineTo(-10, 82); shield.close()
    hc = mixc('#3b2a22', '#ff9a3c', heat * .9)
    c.drawPath(shield, P(shader=lin((-10, 0), (52, 0), [hexc('#1c1412', alpha), with_alpha(hc, alpha)])))
    c.drawPath(shield, P(hexc('#0b0806', alpha), stroke=2))
    if heat > 0.05:
        c.drawPath(shield, P(hexc('#ffd28a', alpha * heat * .8), stroke=4 + 6 * heat, blur=4))
    c.restore()

def draw_parachute(c, x, y, s, openk, sway=0.0, alpha=1.0, color='#f4f1ea', stripe='#e0583a'):
    if openk <= 0 or alpha <= 0:
        return
    c.save(); c.translate(x, y); c.rotate(sway); c.scale(s, s)
    w = lerp(20, 190, e_back(clamp(openk), 1.4)); h = lerp(120, 95, clamp(openk))
    top = -260
    # lines
    for fx in (-1, -.5, 0, .5, 1):
        c.drawLine(0, 0, fx * w * .92, top + h * .55, P(hexc('#d8d2c4', .7 * alpha), stroke=1.4))
    can = skia.Path()
    can.moveTo(-w, top + h * .55)
    can.cubicTo(-w * 1.02, top - h * .45, w * 1.02, top - h * .45, w, top + h * .55)
    for i in range(6):
        x0 = w - i * (2 * w / 6); x1 = w - (i + 1) * (2 * w / 6)
        can.quadTo((x0 + x1) / 2, top + h * .38, x1, top + h * .55)
    can.close()
    c.drawPath(can, P(shader=lin((-w, 0), (w, 0), [hexc(color, alpha), hexc('#bdb6a8', alpha)])))
    # stripes
    c.save(); c.clipPath(can, doAntiAlias=True)
    for i in (-1, 1):
        c.drawRect(skia.Rect(i * w * .33 - w * .12, top - h, i * w * .33 + w * .12, top + h), P(hexc(stripe, .85 * alpha)))
    c.restore()
    c.drawPath(can, P(hexc('#6d665a', .6 * alpha), stroke=2))
    c.restore()

def draw_galileo_descent(c, x, y, s=1.0, chute=1.0, sway=0.0, alpha=1.0, t=0.0, transmit=0.0, heat=0.0):
    """Galileo descent module hanging under parachute. (x,y) = module center."""
    if alpha <= 0:
        return
    c.save(); c.translate(x, y); c.rotate(sway)
    draw_parachute(c, 0, -40 * s, s, chute, 0, alpha)
    c.scale(s, s)
    # module: squat cylinder with domed top
    body = skia.Rect(-46, -38, 46, 30)
    c.drawRRect(skia.RRect.MakeRectXY(body, 10, 10), P(shader=lin((-46, 0), (46, 0), [hexc('#e9e3d2', alpha), hexc('#a9a291', alpha), hexc('#6c665a', alpha)])))
    c.drawOval(skia.Rect(-46, -50, 46, -26), P(shader=lin((-46, 0), (46, 0), [hexc('#f4c56a', alpha), hexc('#9b7428', alpha)])))
    c.drawRect(skia.Rect(-46, -6, 46, 2), P(hexc('#c99a3b', alpha)))
    for i in range(-3, 4):
        c.drawCircle(i * 12, 16, 3, P(hexc('#3b3a36', alpha)))
    c.drawLine(0, -50, 0, -40 * 1 - 18, P(hexc('#cfc8b6', alpha), stroke=3))
    if heat > 0:
        glow(c, 0, 0, 120, hexc('#ff6a2a'), heat * alpha * .7)
    c.restore()
    if transmit > 0:
        for i in range(4):
            ph = (t * 1.1 + i * .25) % 1.0
            rr = (40 + ph * 260) * s
            c.drawArc(skia.Rect(x - rr, y - 330 * s - rr, x + rr, y - 330 * s + rr), 235, 70, False,
                      P(hexc('#9FE3FF', alpha * transmit * (1 - ph) * .9), stroke=3.5 * s))

def draw_juno(c, x, y, s=1.0, rot=0.0, alpha=1.0, t=0.0):
    if alpha <= 0:
        return
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    for k in range(3):
        c.save(); c.rotate(k * 120 + 90)
        # solar array: 4 segments (one array shorter with magnetometer boom)
        n = 4 if k else 3
        for i in range(n):
            r = skia.Rect(40 + i * 62, -26, 98 + i * 62, 26)
            c.drawRect(r, P(shader=lin((0, -26), (0, 26), [hexc('#3d6bd6', alpha), hexc('#1b2f6a', alpha)])))
            c.drawRect(r, P(hexc('#a9c3ff', .55 * alpha), stroke=1.5))
            c.drawLine(r.centerX(), -26, r.centerX(), 26, P(hexc('#a9c3ff', .35 * alpha), stroke=1))
        if not k:
            c.drawLine(225, 0, 290, 0, P(hexc('#d9d4c6', alpha), stroke=3))
            c.drawRect(skia.Rect(282, -8, 298, 8), P(hexc('#d9d4c6', alpha)))
        c.restore()
    # hex body
    hexp = path_from([(math.cos(math.radians(60 * i)) * 44, math.sin(math.radians(60 * i)) * 44) for i in range(6)], True)
    c.drawPath(hexp, P(shader=lin((-44, -44), (44, 44), [hexc('#e7e1cf', alpha), hexc('#8b8574', alpha)])))
    c.drawCircle(0, 0, 30, P(shader=rad(-8, -8, 34, [hexc('#ffffff', alpha), hexc('#bdb7a6', alpha)])))
    c.drawCircle(0, 0, 30, P(hexc('#6f6a5d', alpha), stroke=2))
    c.restore()

# ================================================================ explorer + capsule
SKIN = '#B87A56'; SKIN_D = '#8E5A3E'; SUIT = '#ECE8DF'; SUIT_D = '#B9B3A6'; ACC = '#E39A3B'

def draw_explorer_face(c, cx, cy, s, look=(0, 0), blink=0.0, brow=0.0, mouth='neutral', alpha=1.0,
                       visor_tint=0.32, light='#ffd6a0', light_amt=0.4, helmet=True, sweat=0.0):
    """Explorer head inside helmet. s = helmet radius. brow: +1 raised (awe), -1 worried."""
    if alpha <= 0:
        return
    c.save(); c.translate(cx, cy)
    if helmet:
        c.drawCircle(0, 0, s, P(shader=rad(-s * .35, -s * .4, s * 1.5, [hexc('#ffffff', alpha), hexc(SUIT, alpha), hexc('#8d877a', alpha)], [0, .5, 1])))
        c.drawCircle(0, 0, s, P(hexc('#5a554b', alpha * .9), stroke=s * .025))
        # helmet lamp
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-s * .16, -s * .98, s * .16, -s * .86), 6, 6), P(hexc('#56504a', alpha)))
        c.drawCircle(0, -s * .92, s * .045, P(hexc('#bff3ff', alpha)))
    # visor opening
    vis = skia.RRect.MakeRectXY(skia.Rect(-s * .74, -s * .62, s * .74, s * .66), s * .5, s * .5)
    c.save(); c.clipRRect(vis, doAntiAlias=True)
    c.drawRRect(vis, P(hexc('#1a1410', alpha)))
    # face
    face = skia.Rect(-s * .5, -s * .5, s * .5, s * .7)
    c.drawOval(face, P(shader=rad(-s * .15, -s * .2, s * .8, [hexc('#c98c66', alpha), hexc(SKIN, alpha), hexc(SKIN_D, alpha)], [0, .55, 1])))
    # hair line under helmet
    hair = skia.Path(); hair.moveTo(-s * .52, -s * .1); hair.cubicTo(-s * .5, -s * .62, s * .5, -s * .62, s * .52, -s * .1)
    hair.cubicTo(s * .3, -s * .34, -s * .2, -s * .4, -s * .52, -s * .1); hair.close()
    c.drawPath(hair, P(hexc('#2a1c15', alpha)))
    # eyes
    lx, ly = look
    eo = clamp(1 - blink)
    for side in (-1, 1):
        ex, ey = side * s * .21, s * .02
        ew, eh = s * .135, s * .16 * max(eo, .06)
        if brow < 0:  # fear: eyes wider
            eh *= 1 + (-brow) * .18; ew *= 1 + (-brow) * .08
        c.drawOval(skia.Rect(ex - ew, ey - eh, ex + ew, ey + eh), P(hexc('#fbf7f0', alpha)))
        if eo > .15:
            c.save(); c.clipRect(skia.Rect(ex - ew, ey - eh, ex + ew, ey + eh))
            px, py = ex + lx * ew * .5, ey + ly * eh * .45
            pr = s * .075 * (0.85 if brow < -.5 else 1.0)
            c.drawCircle(px, py, pr, P(hexc('#3a2418', alpha)))
            c.drawCircle(px, py, pr * .55, P(hexc('#120b07', alpha)))
            c.drawCircle(px - pr * .35, py - pr * .4, pr * .3, P(hexc('#ffffff', alpha)))
            c.restore()
        # eyelid line
        c.drawArc(skia.Rect(ex - ew, ey - eh, ex + ew, ey + eh), 200, 140, False, P(hexc('#4a2a1a', alpha * .8), stroke=s * .022))
        # brows
        by = ey - s * .2 - brow * s * .06
        inner = -brow * s * .05 if brow < 0 else 0
        c.drawLine(ex - side * s * .02 - side * s * 0 , by - inner * (1 if side else 0), ex + side * s * .14, by + (s * .02 if brow >= 0 else inner * .4),
                   P(hexc('#2a1c15', alpha), stroke=s * .045, cap='round'))
    # nose
    c.drawArc(skia.Rect(-s * .05, s * .14, s * .05, s * .24), 20, 140, False, P(hexc(SKIN_D, alpha), stroke=s * .025, cap='round'))
    # mouth
    my = s * .38
    mp = P(hexc('#5a2a1e', alpha), stroke=s * .03, cap='round')
    if mouth == 'smile':
        c.drawArc(skia.Rect(-s * .14, my - s * .1, s * .14, my + s * .06), 20, 140, False, mp)
    elif mouth == 'o':
        c.drawOval(skia.Rect(-s * .05, my - s * .05, s * .05, my + s * .07), P(hexc('#4a1e16', alpha)))
    elif mouth == 'grit':
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-s * .12, my - s * .03, s * .12, my + s * .04), 4, 4), P(hexc('#f3eee6', alpha)))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-s * .12, my - s * .03, s * .12, my + s * .04), 4, 4), P(hexc('#5a2a1e', alpha), stroke=s * .02))
    elif mouth == 'frown':
        c.drawArc(skia.Rect(-s * .12, my, s * .12, my + s * .14), 200, 140, False, mp)
    else:
        c.drawLine(-s * .09, my, s * .09, my, mp)
    if sweat > 0:
        c.drawOval(skia.Rect(s * .36, -s * .1, s * .42, s * .0), P(hexc('#cfefff', alpha * sweat)))
    c.restore()  # visor clip
    # visor glass tint + reflections
    c.drawRRect(vis, P(hexc('#0d2440', visor_tint * alpha)))
    c.drawRRect(vis, P(shader=lin((-s * .7, -s * .6), (s * .7, s * .6), [hexc(light, light_amt * .35 * alpha), hexc(light, 0)])))
    hl = skia.Path(); hl.addArc(skia.Rect(-s * .66, -s * .56, s * .66, s * .6), 200, 50)
    c.drawPath(hl, P(hexc('#ffffff', .5 * alpha), stroke=s * .04, cap='round'))
    c.drawRRect(vis, P(hexc('#3c3a36', alpha), stroke=s * .05))
    c.restore()

def draw_explorer_bust(c, cx, cy, s, alpha=1.0, **face):
    """Helmet head at (cx,cy) radius s plus shoulders below."""
    if alpha <= 0:
        return
    # shoulders / torso
    tor = skia.Path()
    tor.moveTo(-s * 1.75, s * 2.6); tor.cubicTo(-s * 1.8, s * 1.15, -s * 1.2, s * .8, 0, s * .8)
    tor.cubicTo(s * 1.2, s * .8, s * 1.8, s * 1.15, s * 1.75, s * 2.6); tor.close()
    c.save(); c.translate(cx, cy)
    c.drawPath(tor, P(shader=lin((-s * 1.6, 0), (s * 1.6, 0), [hexc('#ffffff', alpha), hexc(SUIT, alpha), hexc(SUIT_D, alpha)])))
    c.drawPath(tor, P(hexc('#6a655a', alpha), stroke=s * .025))
    # accent stripes and chest panel
    c.drawLine(-s * 1.45, s * 1.35, -s * .7, s * 1.05, P(hexc(ACC, alpha), stroke=s * .09, cap='round'))
    c.drawLine(s * 1.45, s * 1.35, s * .7, s * 1.05, P(hexc(ACC, alpha), stroke=s * .09, cap='round'))
    rrect(c, -s * .42, s * 1.3, s * .84, s * .55, s * .08, P(hexc('#2d3440', alpha)))
    for i, col in enumerate(('#58E08A', '#FFB347', '#6FD3FF')):
        c.drawCircle(-s * .22 + i * s * .22, s * 1.48, s * .055, P(hexc(col, alpha)))
    c.drawRect(skia.Rect(-s * .3, s * 1.62, s * .3, s * 1.7), P(hexc('#6FD3FF', .6 * alpha)))
    # collar ring
    c.drawOval(skia.Rect(-s * .78, s * .62, s * .78, s * 1.02), P(hexc('#8d877a', alpha)))
    c.drawOval(skia.Rect(-s * .7, s * .66, s * .7, s * .96), P(hexc('#56504a', alpha)))
    c.restore()
    draw_explorer_face(c, cx, cy, s, alpha=alpha, **face)

def capsule_path(s):
    p = skia.Path()
    p.moveTo(0, -150 * s)
    p.cubicTo(95 * s, -150 * s, 120 * s, -40 * s, 112 * s, 40 * s)
    p.cubicTo(105 * s, 110 * s, 60 * s, 150 * s, 0, 160 * s)
    p.cubicTo(-60 * s, 150 * s, -105 * s, 110 * s, -112 * s, 40 * s)
    p.cubicTo(-120 * s, -40 * s, -95 * s, -150 * s, 0, -150 * s)
    p.close()
    return p

def draw_capsule(c, x, y, s=1.0, ang=0.0, alpha=1.0, t=0.0, heat=0.0, shield=0.0, face=None, lamp=True,
                 hull_light='#fff1d6', ambient='#E3B47A'):
    """Fictional explorer capsule (graphite pod, amber band, big round window). Nose (heat shield) at bottom."""
    if alpha <= 0:
        return
    c.save(); c.translate(x, y); c.rotate(ang)
    if shield > 0:
        for i in range(3):
            rr = 210 * s + i * 14 * s + math.sin(t * 3 + i) * 4 * s
            c.drawOval(skia.Rect(-rr * .82, -rr, rr * .82, rr), P(hexc('#8fd8ff', alpha * shield * (.35 - i * .09)), stroke=3 * s))
        glow(c, 0, 0, 300 * s, hexc('#4c8dff'), alpha * shield * .35)
    if heat > 0:
        glow(c, 0, 170 * s, 300 * s * (0.6 + heat), hexc('#ff7a2a'), alpha * heat)
        glow(c, 0, 150 * s, 160 * s * (0.6 + heat), hexc('#fff0c8'), alpha * heat)
    body = capsule_path(s)
    c.drawPath(body, P(shader=lin((-112 * s, -60 * s), (112 * s, 60 * s), [hexc('#5d6470', alpha), hexc('#3a3f49', alpha), hexc('#1d2027', alpha)], [0, .45, 1])))
    # ambient bounce from the environment (bottom/right)
    c.save(); c.clipPath(body, doAntiAlias=True)
    c.drawPaint(P(shader=lin((0, -150 * s), (0, 160 * s), [hexc(ambient, 0), hexc(ambient, .22 * alpha)])))
    # heat shield nose
    c.drawOval(skia.Rect(-130 * s, 95 * s, 130 * s, 230 * s), P(shader=lin((0, 95 * s), (0, 170 * s), [hexc('#2a201b', alpha), with_alpha(mixc('#3b2a22', '#ff9a3c', heat), alpha)])))
    # panel lines
    for yy in (-95, 70):
        c.drawLine(-130 * s, yy * s, 130 * s, yy * s, P(hexc('#0e1014', .6 * alpha), stroke=2 * s))
    # amber band
    c.drawRect(skia.Rect(-130 * s, -20 * s, 130 * s, -2 * s), P(hexc(ACC, alpha)))
    # rim light
    c.restore()
    c.drawPath(body, P(hexc(hull_light, .35 * alpha), stroke=3 * s))
    c.drawPath(body, P(hexc('#0b0c10', .8 * alpha), stroke=1.5 * s))
    # fins
    for side in (-1, 1):
        fin = path_from([(side * 98 * s, 70 * s), (side * 140 * s, 120 * s), (side * 128 * s, 140 * s), (side * 86 * s, 112 * s)], True)
        c.drawPath(fin, P(hexc('#2a2e36', alpha)))
        c.drawPath(fin, P(hexc(ACC, .8 * alpha), stroke=2 * s))
    # window
    wx, wy, wr = -8 * s, -62 * s, 62 * s
    c.drawCircle(wx, wy, wr + 12 * s, P(hexc('#22262e', alpha)))
    c.drawCircle(wx, wy, wr + 12 * s, P(hexc('#8b919c', alpha), stroke=3 * s))
    for i in range(8):
        a_ = i * math.pi / 4
        c.drawCircle(wx + math.cos(a_) * (wr + 6 * s), wy + math.sin(a_) * (wr + 6 * s), 2.6 * s, P(hexc('#aab0ba', alpha)))
    c.save(); c.clipPath(skia.Path().addCircle(wx, wy, wr), doAntiAlias=True)
    c.drawCircle(wx, wy, wr, P(hexc('#0e1a26', alpha)))
    c.drawCircle(wx, wy, wr, P(shader=rad(wx, wy + 40 * s, wr * 1.3, [hexc('#2b4a66', alpha * .9), hexc('#0e1a26', alpha)])))
    if face is not None:
        f = dict(face); f.setdefault('alpha', alpha)
        draw_explorer_bust(c, wx + 2 * s, wy + 2 * s, 40 * s, **f)
    # glass reflection
    c.drawArc(skia.Rect(wx - wr * .8, wy - wr * .8, wx + wr * .8, wy + wr * .8), 200, 60, False, P(hexc('#ffffff', .45 * alpha), stroke=5 * s, cap='round'))
    c.drawCircle(wx, wy, wr, P(hexc('#6FD3FF', .12 * alpha)))
    c.restore()
    # top lamp / antenna
    c.drawLine(0, -150 * s, 0, -182 * s, P(hexc('#9aa0aa', alpha), stroke=3 * s))
    if lamp:
        bl = .5 + .5 * math.sin(t * 5.0)
        c.drawCircle(0, -184 * s, 5 * s, P(hexc('#ff5a4a', alpha * (.4 + .6 * bl))))
        glow(c, 0, -184 * s, 26 * s, hexc('#ff5a4a'), alpha * bl * .7)
    c.restore()

# ================================================================ Jupiter interior cross-section
def draw_cross_section(c, cx, cy, R, alpha=1.0, wedge=(-90, 90), t=0.0, core_fuzz=1.0, core_alpha=1.0,
                       metal_glow=0.6, show_metal=1.0, rot=1.2, sphere=True, dark_unknown=0.0, highlight=None):
    """Planet drawn as textured sphere with a pie-slice cutaway (angles in deg, 0=right, clockwise).
    Layer radii (fraction of R) are illustrative, model-based:
      clouds/atmosphere skin ~1.0, molecular H2 fluid to ~0.83, metallic H to ~0.3-0.5, dilute core."""
    if alpha <= 0:
        return
    if sphere:
        draw_jupiter(c, cx, cy, R, rot, alpha)
    a0, a1 = wedge
    sweep = a1 - a0
    if sweep <= 0.1:
        return
    pie = skia.Path(); pie.moveTo(cx, cy); pie.arcTo(skia.Rect(cx - R, cy - R, cx + R, cy + R), a0, sweep, False); pie.close()
    c.save(); c.clipPath(pie, doAntiAlias=True)
    # molecular hydrogen envelope: amber -> deep brown-red with depth
    c.drawCircle(cx, cy, R, P(shader=rad(cx, cy, R, [hexc('#5a1f12', alpha), hexc('#8a3b1f', alpha), hexc('#c7783c', alpha), hexc('#e8b27a', alpha)], [0, .7, .93, 1.0])))
    # metallic hydrogen region
    if show_metal > 0:
        mr = R * 0.80
        c.drawCircle(cx, cy, mr, P(shader=rad(cx, cy, mr, [hexc('#24205e', alpha * show_metal), hexc('#2d2a7a', alpha * show_metal), hexc('#3b3f9e', alpha * show_metal), hexc('#3b3f9e', 0)], [0, .6, .97, 1.0])))
        if metal_glow > 0:
            # shimmering conductive glow
            for i in range(14):
                aa = math.radians(a0 + sweep * ((i * .37 + t * .03) % 1.0))
                rr = mr * (.45 + .45 * ((i * .61) % 1.0))
                glow(c, cx + math.cos(aa) * rr, cy + math.sin(aa) * rr, R * .16, hexc('#7f8cff'), alpha * show_metal * metal_glow * (.35 + .25 * math.sin(t * 2 + i)))
    # core: compact (fuzz=0) or dilute (fuzz=1)
    if core_alpha > 0:
        cr_compact = R * .16; cr_fuzzy = R * .52
        cr = lerp(cr_compact, cr_fuzzy, core_fuzz)
        edge = lerp(.94, .0, core_fuzz)
        cols = [hexc('#f2d29a', alpha * core_alpha), hexc('#c98a4a', alpha * core_alpha), hexc('#9a5a3a', alpha * core_alpha * lerp(1, .55, core_fuzz)), hexc('#7a4a5a', 0)]
        c.drawCircle(cx, cy, cr, P(shader=rad(cx, cy, cr, cols, [0, lerp(.45, .2, core_fuzz), lerp(.97, .6, core_fuzz), 1.0])))
        if core_fuzz < .5:
            c.drawCircle(cx, cy, cr, P(hexc('#fff1d6', alpha * core_alpha * (1 - core_fuzz * 2) * .8), stroke=3))
        if core_fuzz > 0.05:
            rng = np.random.default_rng(4)
            for i in range(160):
                aa = math.radians(a0 + sweep * rng.random())
                rr = cr_fuzzy * (rng.random() ** 0.8) * lerp(.3, 1.05, core_fuzz)
                c.drawCircle(cx + math.cos(aa) * rr, cy + math.sin(aa) * rr, 2.2 + rng.random() * 2.5,
                             P(hexc('#ffe2b0', alpha * core_alpha * core_fuzz * .55)))
    if dark_unknown > 0:
        c.drawCircle(cx, cy, R * .97, P(shader=rad(cx, cy, R * .97, [rgba(4, 4, 10, dark_unknown * alpha), rgba(4, 4, 10, dark_unknown * alpha * .92), rgba(4, 4, 10, 0)], [0, .85, 1.0])))
    # cloud layer skin
    c.drawCircle(cx, cy, R * .985, P(hexc('#ffe7c2', .7 * alpha), stroke=max(2, R * .012)))
    c.restore()
    # cut edges
    for a_ in (a0, a1):
        ar = math.radians(a_)
        c.drawLine(cx, cy, cx + math.cos(ar) * R, cy + math.sin(ar) * R, P(hexc('#fff1d6', .5 * alpha), stroke=2))
    if highlight is not None:
        r_in, r_out, col = highlight
        hp = skia.Path(); hp.addArc(skia.Rect(cx - r_out * R, cy - r_out * R, cx + r_out * R, cy + r_out * R), a0, sweep)
        hp.arcTo(skia.Rect(cx - r_in * R, cy - r_in * R, cx + r_in * R, cy + r_in * R), a1, -sweep, False); hp.close()
        c.drawPath(hp, P(hexc(col, .9 * alpha), stroke=3.5))

# ================================================================ field lines, molecules
def dipole_lines(c, cx, cy, R, alpha=1.0, k=1.0, t=0.0, Ls=(1.6, 2.2, 3.0, 4.2, 5.8), color='#6FD3FF', tilt=-10, width=3):
    if alpha <= 0 or k <= 0:
        return
    c.save(); c.translate(cx, cy); c.rotate(tilt)
    for L in Ls:
        for side in (-1, 1):
            pts = []
            th0 = math.asin(min(1, math.sqrt(1 / L)))
            n = 80
            for i in range(n + 1):
                th = th0 + (math.pi - 2 * th0) * i / n
                r = L * R * math.sin(th) ** 2
                pts.append((side * r * math.sin(th), -r * math.cos(th)))
            pa = path_from(pts)
            pp = P(hexc(color, alpha * .55), stroke=width)
            pp.setPathEffect(skia.DashPathEffect.Make([18, 12], -t * 40))
            stroke_path_k(c, pa, pp, k)
            stroke_path_k(c, pa, P(hexc(color, alpha * .18), stroke=width * 3.5, blur=6), k)
    c.restore()

def h2_molecule(c, x, y, r, ang, alpha=1.0, color='#FFF1D6', bond=1.0):
    dx, dy = math.cos(ang) * r * .75 * bond, math.sin(ang) * r * .75 * bond
    c.drawLine(x - dx, y - dy, x + dx, y + dy, P(hexc(color, alpha * .7), stroke=r * .35))
    for sgn in (-1, 1):
        c.drawCircle(x + sgn * dx, y + sgn * dy, r * .62, P(shader=rad(x + sgn * dx - r * .2, y + sgn * dy - r * .2, r * .9, [hexc('#ffffff', alpha), hexc(color, alpha)])))
