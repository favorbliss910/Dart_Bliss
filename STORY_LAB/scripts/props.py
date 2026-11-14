"""Sets and props for the three stories (warm toon 2.5D: front faces lit from upper-left,
side faces darker, soft violet contact shadows, ink outlines)."""
import math, random
import cairo
from engine import (W, H, INK, GOLD, rgb, shade, mix, fill, stroke, fs, ellipse, poly, rrect, soft_shadow,
                    glow, vgrad, clamp, lerp, wob, ease, label, chalk_text, _font)

# ----------------------------------------------------------------------------- sky / land
def sky(f, top, bot, mid=None):
    c = f.ctx
    f.screen()
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *rgb(top))
    if mid:
        g.add_color_stop_rgb(0.55, *rgb(mid))
    g.add_color_stop_rgb(1, *rgb(bot))
    c.rectangle(0, 0, W, H)
    c.set_source(g)
    c.fill()


def stars(c, x0, y0, w, h, n=80, t=0, seed=3):
    rnd = random.Random(seed)
    for _ in range(n):
        x, y = x0 + rnd.random() * w, y0 + rnd.random() * h
        r = rnd.random() * 2.5 + 1
        a = 0.5 + 0.5 * math.sin(t * 2 + rnd.random() * 6)
        c.arc(x, y, r, 0, 2 * math.pi)
        fill(c, (1, 1, 0.9), 0.4 + 0.5 * a)


def sun(c, x, y, r, col="#FFE38A"):
    glow(c, x, y, r * 3, col, 0.5)
    c.arc(x, y, r, 0, 2 * math.pi)
    fs(c, col, 6)


def moon(c, x, y, r):
    glow(c, x, y, r * 3.2, (0.8, 0.85, 1.0), 0.35)
    c.arc(x, y, r, 0, 2 * math.pi)
    fs(c, (0.97, 0.95, 0.85), 6)
    for dx, dy, rr in ((-0.3, -0.2, 0.18), (0.25, 0.25, 0.12), (0.2, -0.35, 0.09)):
        c.arc(x + dx * r, y + dy * r, rr * r, 0, 2 * math.pi)
        fill(c, (0.85, 0.82, 0.72))


def cloud(c, x, y, s=1.0, col=(1, 1, 1), a=1.0):
    def b(c):
        for dx, dy, r in ((0, 0, 60), (60, 10, 48), (-60, 12, 44), (25, -35, 50), (-30, -25, 40)):
            c.new_sub_path()
            c.arc(x + dx * s, y + dy * s, r * s, 0, 2 * math.pi)
    b(c)
    stroke(c, 14, INK, a)
    b(c)
    fill(c, col, a)
    for dx, dy, r in ((60, 22, 40), (0, 18, 50)):
        c.arc(x + dx * s, y + dy * s, r * s, 0, math.pi)
        fill(c, shade(col, 0.88), a)


def hills(c, y, col, seed=1, x0=-1200, x1=2400, amp=90, n=7):
    rnd = random.Random(seed)
    c.move_to(x0, y + 2000)
    c.line_to(x0, y)
    xs = [x0 + (x1 - x0) * k / n for k in range(n + 1)]
    for k in range(n):
        xa, xb = xs[k], xs[k + 1]
        h = amp * (0.6 + rnd.random() * 0.8)
        c.curve_to(xa + (xb - xa) * 0.3, y - h, xa + (xb - xa) * 0.7, y - h, xb, y)
    c.line_to(x1, y + 2000)
    c.close_path()
    fs(c, col, 7)


def ground(c, y, col, x0=-2000, x1=3200, depth=3000):
    g = cairo.LinearGradient(0, y, 0, y + 900)
    g.add_color_stop_rgb(0, *shade(col, 1.08))
    g.add_color_stop_rgb(1, *shade(col, 0.82))
    c.rectangle(x0, y, x1 - x0, depth)
    c.set_source(g)
    c.fill()
    c.move_to(x0, y)
    c.line_to(x1, y)
    stroke(c, 7)


def tree(c, x, y, s=1.0, col=(0.35, 0.65, 0.3)):
    soft_shadow(c, x + 20 * s, y, 70 * s, 14 * s, 0.3)
    rrect(c, x - 14 * s, y - 120 * s, 28 * s, 120 * s, 8 * s)
    fs(c, (0.5, 0.33, 0.2), 6)
    def blob(c):
        for dx, dy, r in ((0, -190, 75), (-55, -140, 55), (55, -140, 58), (0, -250, 50)):
            c.new_sub_path()
            c.arc(x + dx * s, y + dy * s, r * s, 0, 2 * math.pi)
    blob(c)
    stroke(c, 12)
    blob(c)
    fill(c, col)
    c.arc(x + 30 * s, y - 160 * s, 50 * s, -0.3, math.pi * 0.8)
    fill(c, shade(col, 0.8))
    c.arc(x - 25 * s, y - 220 * s, 28 * s, 0, 2 * math.pi)
    fill(c, shade(col, 1.25))


def box3d(c, x, y, w, h, d, col, ink=6):
    """front face (x..x+w, y-h..y), side face extruded to the right/up by d."""
    poly(c, [(x + w, y), (x + w + d, y - d * 0.6), (x + w + d, y - h - d * 0.6), (x + w, y - h)])
    fs(c, shade(col, 0.72), ink)
    poly(c, [(x, y - h), (x + d, y - h - d * 0.6), (x + w + d, y - h - d * 0.6), (x + w, y - h)])
    fs(c, shade(col, 1.15), ink)
    c.rectangle(x, y - h, w, h)
    fs(c, col, ink)


def house(c, x, y, w=220, h=170, wall=(0.95, 0.85, 0.65), roof=(0.8, 0.35, 0.25), lit=False, d=40):
    soft_shadow(c, x + w * 0.6, y + 4, w * 0.75, 18, 0.35)
    box3d(c, x, y, w, h, d, wall)
    # roof: front gable + side slope
    poly(c, [(x + w, y - h), (x + w + d, y - h - d * 0.6), (x + w / 2 + d, y - h - 110 - d * 0.6), (x + w / 2, y - h - 110)])
    fs(c, shade(roof, 0.75), 6)
    poly(c, [(x - 16, y - h + 8), (x + w / 2, y - h - 110), (x + w + 16, y - h + 8)])
    fs(c, roof, 6)
    rrect(c, x + w * 0.38, y - 90, w * 0.24, 90, 10)
    fs(c, (0.55, 0.35, 0.22), 5)
    win = (1.0, 0.85, 0.45) if lit else (0.55, 0.75, 0.9)
    for wx in (x + w * 0.1, x + w * 0.7):
        c.rectangle(wx, y - h + 40, w * 0.2, 50)
        fs(c, win, 5)
        if lit:
            glow(c, wx + w * 0.1, y - h + 65, 80, (1, 0.8, 0.4), 0.35)


def palace(c, x, y, s=1.0, lit=False, t=0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    wall = (0.96, 0.9, 0.78)
    soft_shadow(c, 40, 6, 420, 30, 0.35)
    box3d(c, -300, 0, 600, 330, 60, wall)
    for tx in (-360, 300):
        box3d(c, tx, 0, 90, 470, 30, shade(wall, 0.97))
        poly(c, [(tx - 12, -470), (tx + 45 + 15, -600), (tx + 102 + 15, -470)])
        fs(c, (0.35, 0.4, 0.75), 6)
        c.move_to(tx + 60, -600)
        c.line_to(tx + 60, -680)
        stroke(c, 5)
        fl = wob(t, 1.3, 8)
        poly(c, [(tx + 60, -680), (tx + 120, -665 + fl), (tx + 60, -645)])
        fs(c, (0.85, 0.2, 0.25), 4)
    # dome
    c.arc(0, -330, 130, math.pi, 2 * math.pi)
    c.close_path()
    g = cairo.LinearGradient(-130, -460, 130, -330)
    g.add_color_stop_rgb(0, 1.0, 0.92, 0.55)
    g.add_color_stop_rgb(1, 0.8, 0.55, 0.12)
    c.set_source(g)
    c.fill_preserve()
    stroke(c, 7)
    # crenellations
    for k in range(-5, 6):
        c.rectangle(k * 52 - 18, -360, 36, 30)
        fs(c, shade(wall, 1.05), 5)
    # gate
    c.move_to(-70, 0)
    c.line_to(-70, -130)
    c.arc(0, -130, 70, math.pi, 2 * math.pi)
    c.line_to(70, 0)
    c.close_path()
    fs(c, (0.45, 0.28, 0.18), 6)
    winc = (1.0, 0.82, 0.4) if lit else (0.45, 0.6, 0.85)
    for wx in (-230, -150, 110, 190):
        c.move_to(wx, -180)
        c.line_to(wx, -240)
        c.arc(wx + 20, -240, 20, math.pi, 2 * math.pi)
        c.line_to(wx + 40, -180)
        c.close_path()
        fs(c, winc, 5)
    # balcony
    rrect(c, -110, -275, 220, 26, 8)
    fs(c, shade(wall, 0.85), 5)
    c.restore()


def fence(c, x0, x1, y, s=1.0, col=(0.72, 0.5, 0.3)):
    n = int((x1 - x0) / (60 * s)) + 1
    for k in range(n):
        px = x0 + k * 60 * s
        poly(c, [(px - 9 * s, y), (px - 9 * s, y - 80 * s), (px, y - 95 * s), (px + 9 * s, y - 80 * s), (px + 9 * s, y)])
        fs(c, col, 4)
    for yy in (y - 62 * s, y - 30 * s):
        rrect(c, x0 - 20, yy - 7 * s, x1 - x0 + 40, 14 * s, 4)
        fs(c, shade(col, 0.9), 4)


def potato(c, x, y, s=1.0, rot=0.0, gold=False, a=1.0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    c.move_to(-40, -4)
    c.curve_to(-42, -30, 10, -34, 34, -18)
    c.curve_to(52, -6, 44, 26, 12, 26)
    c.curve_to(-20, 28, -40, 20, -40, -4)
    c.close_path()
    if gold:
        g = cairo.LinearGradient(-40, -30, 40, 30)
        g.add_color_stop_rgba(0, 1.0, 0.95, 0.6, a)
        g.add_color_stop_rgba(0.5, 1.0, 0.78, 0.2, a)
        g.add_color_stop_rgba(1, 0.75, 0.48, 0.08, a)
        c.set_source(g)
    else:
        c.set_source_rgba(0.80, 0.6, 0.36, a)
    c.fill_preserve()
    stroke(c, 5, INK, a)
    c.move_to(-40, -4)
    c.curve_to(-42, -30, 10, -34, 34, -18)
    c.curve_to(52, -6, 44, 26, 12, 26)
    c.curve_to(-20, 28, -40, 20, -40, -4)
    c.save()
    c.clip()
    ellipse(c, 14, 18, 40, 14)
    fill(c, (0.4, 0.25, 0.1), 0.25 * a)
    ellipse(c, -14, -16, 16, 7)
    fill(c, (1, 1, 1), 0.35 * a)
    c.restore()
    for ex, ey in ((-18, 2), (8, -10), (22, 10)):
        c.arc(ex, ey, 2.6, 0, 2 * math.pi)
        fill(c, (0.45, 0.3, 0.15), a)
    c.restore()


def potato_plant(c, x, y, s=1.0, t=0.0, grow=1.0):
    if grow <= 0:
        return
    s *= grow
    sway = wob(t, 0.5, 0.06, x * 0.01)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    soft_shadow(c, 8, 4, 50, 10, 0.3)
    for k, ang in enumerate((-1.0, -0.45, 0.1, 0.6, 1.05)):
        c.save()
        c.rotate(ang * 0.8 + sway)
        ellipse(c, 0, -46, 16, 40)
        fs(c, shade((0.35, 0.68, 0.3), 0.85 + 0.1 * (k % 2)), 4)
        c.move_to(0, -8)
        c.line_to(0, -76)
        stroke(c, 2, shade((0.35, 0.68, 0.3), 0.6))
        c.restore()
    c.arc(-8, -70, 6, 0, 2 * math.pi)
    fs(c, (1, 1, 1), 3)
    c.arc(-8, -70, 2.5, 0, 2 * math.pi)
    fill(c, (1, 0.85, 0.2))
    c.restore()


def field(c, x0, x1, y0, y1, t=0.0, rows=5, grow=1.0, soil=(0.55, 0.38, 0.24)):
    poly(c, [(x0 + 40, y0), (x1 - 40, y0), (x1, y1), (x0, y1)])
    fs(c, soil, 6)
    for r in range(rows):
        yy = lerp(y0 + 30, y1 - 30, r / max(rows - 1, 1))
        sc = lerp(0.7, 1.15, r / max(rows - 1, 1))
        ellipse(c, (x0 + x1) / 2, yy + 6, (x1 - x0) / 2 - 30, 10 * sc)
        fill(c, shade(soil, 0.8))
        n = int((x1 - x0) / (90 * sc))
        for k in range(n):
            potato_plant(c, x0 + 50 + k * (x1 - x0 - 100) / max(n - 1, 1), yy, sc, t, grow)


def torch(c, x, y, s=1.0, t=0.0, lit=True):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rrect(c, -6, -10, 12, 90, 4)
    fs(c, (0.45, 0.28, 0.16), 4)
    poly(c, [(-14, -10), (14, -10), (9, 10), (-9, 10)])
    fs(c, (0.35, 0.35, 0.4), 4)
    if lit:
        glow(c, 0, -40, 140, (1.0, 0.65, 0.2), 0.45)
        fl = 1 + 0.12 * math.sin(t * 17) + 0.08 * math.sin(t * 29)
        c.move_to(-14, -12)
        c.curve_to(-22, -40 * fl, 0, -50 * fl, 2, -78 * fl)
        c.curve_to(10, -50 * fl, 22, -36 * fl, 14, -12)
        c.close_path()
        fs(c, (1.0, 0.6, 0.15), 4)
        c.move_to(-7, -12)
        c.curve_to(-9, -30 * fl, 0, -38 * fl, 1, -52 * fl)
        c.curve_to(6, -32 * fl, 10, -26 * fl, 7, -12)
        c.close_path()
        fill(c, (1.0, 0.92, 0.45))
    c.restore()


def sack(c, x, y, s=1.0, full=1.0, col=(0.82, 0.68, 0.45)):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    w = 40 + 14 * full
    c.move_to(-14, -60)
    c.curve_to(-w, -40, -w - 6, 10, -w + 6, 28)
    c.curve_to(-20, 40, 20, 40, w - 6, 28)
    c.curve_to(w + 6, 10, w, -40, 14, -60)
    c.close_path()
    fs(c, col, 6)
    c.move_to(-16, -58)
    c.line_to(16, -58)
    stroke(c, 8, (0.55, 0.35, 0.2))
    poly(c, [(-12, -60), (-26, -80), (0, -68), (26, -82), (12, -60)])
    fs(c, col, 5)
    c.move_to(10, -30)
    c.curve_to(30, -10, 30, 15, 22, 28)
    stroke(c, 3, shade(col, 0.7))
    c.restore()


def trough(c, x, y, s=1.0, n_pot=0, t=0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    soft_shadow(c, 10, 6, 150, 16, 0.3)
    for k in range(n_pot):
        potato(c, -90 + k * 45, -60 + (k % 2) * 8, 0.6, k * 0.7)
    poly(c, [(-140, -60), (140, -60), (115, 0), (-115, 0)])
    fs(c, (0.62, 0.42, 0.26), 6)
    for xx in (-60, 0, 60):
        c.move_to(xx * 1.1, -60)
        c.line_to(xx, 0)
        stroke(c, 3, (0.45, 0.3, 0.18))
    c.restore()


def basket(c, x, y, s=1.0, full=0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    for k in range(full):
        potato(c, -30 + (k % 3) * 30, -52 - (k // 3) * 16, 0.5, k)
    poly(c, [(-60, -50), (60, -50), (45, 0), (-45, 0)])
    fs(c, (0.82, 0.62, 0.35), 5)
    for yy in (-36, -20):
        c.move_to(-56, yy)
        c.line_to(56, yy)
        stroke(c, 2.5, (0.55, 0.38, 0.2))
    c.restore()


def board(c, x, y, w, h, lines, s=1.0, col=(0.85, 0.65, 0.4)):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    for px in (-w / 2 + 20, w / 2 - 20):
        rrect(c, px - 9, -h - 30, 18, h + 120, 4)
        fs(c, (0.5, 0.32, 0.2), 5)
    rrect(c, -w / 2, -h - 40, w, h, 10)
    fs(c, col, 7)
    rrect(c, -w / 2 + 30, -h - 15, w - 60, h - 50, 4)
    fs(c, (0.98, 0.95, 0.85), 4)
    for k, ln in enumerate(lines):
        label(c, ln, 0, -h + 25 + k * 52, 40, INK, "Lilita One", cairo.FONT_WEIGHT_NORMAL)
    c.restore()


def cushion(c, x, y, s=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    soft_shadow(c, 10, 30, 190, 30, 0.35)
    c.move_to(-170, 0)
    c.curve_to(-120, -60, 120, -60, 170, 0)
    c.curve_to(120, 50, -120, 50, -170, 0)
    c.close_path()
    g = cairo.LinearGradient(0, -50, 0, 50)
    g.add_color_stop_rgb(0, 0.85, 0.18, 0.3)
    g.add_color_stop_rgb(1, 0.5, 0.06, 0.16)
    c.set_source(g)
    c.fill_preserve()
    stroke(c, 7)
    for tx in (-170, 170):
        c.arc(tx, 0, 12, 0, 2 * math.pi)
        fs(c, GOLD, 4)
    c.restore()


def bunting(c, x0, x1, y, t=0, sag=50):
    c.move_to(x0, y)
    c.curve_to(lerp(x0, x1, 0.3), y + sag, lerp(x0, x1, 0.7), y + sag, x1, y)
    stroke(c, 4)
    cols = [(0.95, 0.3, 0.3), (1, 0.8, 0.2), (0.3, 0.6, 0.95), (0.4, 0.8, 0.4)]
    n = int((x1 - x0) / 70)
    for k in range(1, n):
        u = k / n
        px = lerp(x0, x1, u)
        py = y + sag * 4 * u * (1 - u) * 0.75
        sw = wob(t, 1.2, 4, u)
        poly(c, [(px - 22, py), (px + 22, py), (px + sw, py + 48)])
        fs(c, cols[k % 4], 4)


def snow(f, t, n=140, seed=5, a=1.0):
    c = f.ctx
    f.screen()
    rnd = random.Random(seed)
    for _ in range(n):
        x0, sp, r, ph = rnd.random() * W, 60 + rnd.random() * 120, 3 + rnd.random() * 7, rnd.random() * 10
        y = (rnd.random() * H + t * sp) % (H + 40) - 20
        x = x0 + math.sin(t * 1.3 + ph) * 30
        c.arc(x, y, r, 0, 2 * math.pi)
        fill(c, (1, 1, 1), 0.85 * a)


def snow_ground(c, y, x0=-2000, x1=3200):
    c.move_to(x0, y + 10)
    for k in range(40):
        xx = lerp(x0, x1, k / 39)
        c.line_to(xx, y - 8 - 10 * math.sin(k * 1.7))
    c.line_to(x1, y + 3000)
    c.line_to(x0, y + 3000)
    c.close_path()
    fs(c, (0.96, 0.97, 1.0), 6)


def stall(c, x, y, s=1.0, cols=((0.9, 0.3, 0.3), (1, 1, 1)), goods=None, empty=False):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    soft_shadow(c, 20, 4, 180, 18, 0.3)
    for px in (-140, 140):
        rrect(c, px - 8, -260, 16, 260, 4)
        fs(c, (0.55, 0.36, 0.22), 5)
    box3d(c, -160, 0, 320, 110, 30, (0.75, 0.52, 0.32))
    # awning stripes
    n = 6
    for k in range(n):
        x0 = -175 + k * 350 / n
        poly(c, [(x0, -300), (x0 + 350 / n, -300), (x0 + 350 / n, -250), (x0, -250)])
        fs(c, cols[k % 2], 5)
        c.arc(x0 + 350 / n / 2, -250, 350 / n / 2, 0, math.pi)
        fs(c, cols[k % 2], 5)
    if not empty:
        for k in range(5):
            gc = goods[k % len(goods)] if goods else (0.9, 0.5, 0.2)
            c.arc(-110 + k * 55, -125, 22, 0, 2 * math.pi)
            fs(c, gc, 4)
    else:
        basket(c, -60, -110, 0.7, 0)
        basket(c, 70, -110, 0.7, 0)
    c.restore()


# ----------------------------------------------------------------------------- coins story
SILVER = (0.80, 0.82, 0.86)


def coin(c, x, y, r, ridged=True, squash=1.0, clipped=0.0, col=SILVER, face="crown", a=1.0, rot=0.0, smooth_glint=False):
    """front-facing coin; squash<1 tilts it (ellipse). clipped: 0..1 how much the rim is shaved."""
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(1, squash)
    th = r * 0.12 * (1 - squash) * 3 + 2
    # rim thickness (for tilt)
    if squash < 0.98:
        c.save()
        c.translate(0, th / squash)
        _coin_outline(c, r, clipped)
        fs(c, shade(col, 0.6), 4)
        c.restore()
    _coin_outline(c, r, clipped)
    g = cairo.RadialGradient(-r * 0.4, -r * 0.4, 0, 0, 0, r * 1.2)
    g.add_color_stop_rgba(0, *shade(col, 1.35), a)
    g.add_color_stop_rgba(0.6, *rgb(col), a)
    g.add_color_stop_rgba(1, *shade(col, 0.7), a)
    c.set_source(g)
    c.fill_preserve()
    stroke(c, max(3, r * 0.05), INK, a)
    rr = r * (1 - 0.12 * clipped)
    if ridged:
        n = 64
        for k in range(n):
            an = k * 2 * math.pi / n
            c.move_to(math.cos(an) * rr * 0.86, math.sin(an) * rr * 0.86)
            c.line_to(math.cos(an) * rr * 0.98, math.sin(an) * rr * 0.98)
        stroke(c, max(1.5, r * 0.025), shade(col, 0.55), a)
    c.arc(0, 0, rr * 0.8, 0, 2 * math.pi)
    stroke(c, max(2, r * 0.025), shade(col, 0.65), a)
    if face == "crown":
        s = rr / 100
        poly(c, [(-38 * s, 20 * s), (-44 * s, -26 * s), (-20 * s, -2 * s), (0, -36 * s), (20 * s, -2 * s), (44 * s, -26 * s), (38 * s, 20 * s)])
        c.set_source_rgba(*shade(col, 0.7), a)
        c.fill()
        c.rectangle(-38 * s, 24 * s, 76 * s, 12 * s)
        fill(c, shade(col, 0.7), a)
    elif face == "head":
        s = rr / 100
        c.arc(0, -6 * s, 34 * s, 0, 2 * math.pi)
        fill(c, shade(col, 0.72), a)
        c.rectangle(-30 * s, 26 * s, 60 * s, 22 * s)
        fill(c, shade(col, 0.72), a)
    c.arc(-r * 0.4, -r * 0.45, r * 0.15, 0, 2 * math.pi)
    fill(c, (1, 1, 1), 0.5 * a)
    c.restore()


def _coin_outline(c, r, clipped):
    if clipped <= 0:
        c.arc(0, 0, r, 0, 2 * math.pi)
        return
    rnd = random.Random(7)
    n = 40
    for k in range(n + 1):
        an = k * 2 * math.pi / n
        rr = r * (1 - clipped * (0.06 + 0.12 * rnd.random()))
        if k == 0:
            c.move_to(math.cos(an) * rr, math.sin(an) * rr)
        else:
            c.line_to(math.cos(an) * rr, math.sin(an) * rr)
    c.close_path()


def coin_edge(c, x, y, r, h, t, ridged=True, col=SILVER):
    """the coin's rim seen side-on (a band) with scrolling ridges = rotating coin macro."""
    c.save()
    c.translate(x, y)
    rrect(c, -r, -h / 2, 2 * r, h, h * 0.2)
    g = cairo.LinearGradient(0, -h / 2, 0, h / 2)
    g.add_color_stop_rgb(0, *shade(col, 1.3))
    g.add_color_stop_rgb(0.4, *rgb(col))
    g.add_color_stop_rgb(1, *shade(col, 0.55))
    c.set_source(g)
    c.fill_preserve()
    c.save()
    c.clip_preserve()
    stroke(c, 8)
    if ridged:
        n = 46
        off = (t * 120) % (2 * r / n * 2)
        for k in range(-2, n + 2):
            u = (-r + k * 2 * r / n * 1.0 + off)
            # compress toward the sides like a cylinder
            xn = math.sin(clamp((u) / r, -1, 1) * math.pi / 2) * r
            wv = max(1.5, 7 * math.cos(clamp(u / r, -1, 1) * math.pi / 2))
            c.move_to(xn, -h / 2 + 6)
            c.line_to(xn, h / 2 - 6)
            stroke(c, wv, shade(col, 0.45))
            c.move_to(xn + wv * 0.8, -h / 2 + 6)
            c.line_to(xn + wv * 0.8, h / 2 - 6)
            stroke(c, wv * 0.5, shade(col, 1.35), 0.7)
    c.restore()
    c.new_path()
    c.restore()


def scissors(c, x, y, s=1.0, open_=0.3, rot=0.0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    for sg in (-1, 1):
        c.save()
        c.rotate(sg * open_ * 0.5)
        poly(c, [(0, -6 * sg), (150, -2 * sg), (150, 2 * sg), (0, 10 * sg)])
        c.move_to(0, -8 * sg)
        c.curve_to(60, -14 * sg, 120, -6 * sg, 160, 0)
        c.curve_to(110, 4 * sg, 50, 10 * sg, 0, 8 * sg)
        c.close_path()
        fs(c, (0.85, 0.87, 0.92), 5)
        c.restore()
        c.save()
        c.rotate(-sg * open_ * 0.5)
        ellipse(c, -55, 0 + sg * 22, 34, 22)
        c.set_source_rgb(0.85, 0.2, 0.25)
        c.fill_preserve()
        stroke(c, 6)
        ellipse(c, -55, sg * 22, 18, 10)
        fill(c, (0.98, 0.92, 0.82))
        c.restore()
    c.arc(0, 0, 9, 0, 2 * math.pi)
    fs(c, GOLD, 4)
    c.restore()


def candle(c, x, y, s=1.0, t=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    glow(c, 0, -110, 380, (1, 0.7, 0.3), 0.4)
    ellipse(c, 0, 0, 46, 14)
    fs(c, GOLD, 5)
    rrect(c, -18, -90, 36, 90, 6)
    fs(c, (0.98, 0.95, 0.85), 5)
    fl = 1 + 0.1 * math.sin(t * 13) + 0.06 * math.sin(t * 31)
    c.move_to(-9, -92)
    c.curve_to(-14, -110 * fl, 0, -125 * fl, 1, -140 * fl)
    c.curve_to(6, -122 * fl, 14, -110 * fl, 9, -92)
    c.close_path()
    fs(c, (1, 0.75, 0.25), 3)
    c.restore()


def scales(c, x, y, s=1.0, tilt=0.0, left=None, right=None):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    soft_shadow(c, 10, 4, 120, 14, 0.3)
    poly(c, [(-60, 0), (60, 0), (30, -24), (-30, -24)])
    fs(c, GOLD, 5)
    rrect(c, -8, -260, 16, 240, 4)
    fs(c, shade(GOLD, 0.9), 5)
    c.save()
    c.translate(0, -250)
    c.rotate(tilt)
    rrect(c, -170, -7, 340, 14, 5)
    fs(c, GOLD, 5)
    for sx, item in ((-1, left), (1, right)):
        px = sx * 160
        c.save()
        c.translate(px, 0)
        c.rotate(-tilt)
        for dx in (-50, 50):
            c.move_to(0, 0)
            c.line_to(dx, 110)
            stroke(c, 3)
        if item:
            item(c, 0, 100)
        c.arc(0, 100, 62, 0, math.pi)
        c.close_path()
        fs(c, GOLD, 5)
        c.restore()
    c.restore()
    c.arc(0, -250, 14, 0, 2 * math.pi)
    fs(c, GOLD, 4)
    c.restore()


def silver_bar(c, x, y, s=1.0, a=1.0, hot=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    if hot > 0:
        glow(c, 0, -30, 220, (1, 0.6, 0.2), 0.6 * hot)
    col = mix(SILVER, (1.0, 0.65, 0.25), hot)
    poly(c, [(-110, 0), (110, 0), (85, -55), (-85, -55)])
    fs(c, col, 6)
    poly(c, [(-85, -55), (85, -55), (70, -70), (-70, -70)])
    fs(c, shade(col, 1.25), 5)
    poly(c, [(-60, -40), (-20, -40), (-30, -50), (-55, -50)])
    fill(c, (1, 1, 1), 0.5)
    c.restore()


def crucible(c, x, y, s=1.0, glowa=1.0, t=0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    glow(c, 0, -80, 260, (1, 0.5, 0.15), 0.6 * glowa)
    for k in range(5):
        fx = -60 + k * 30
        fl = 30 + 15 * math.sin(t * 9 + k)
        poly(c, [(fx - 18, 0), (fx + 18, 0), (fx, -fl)])
        fill(c, (1, 0.55 + 0.1 * (k % 2), 0.15))
    poly(c, [(-90, -150), (90, -150), (65, -20), (-65, -20)])
    fs(c, (0.3, 0.28, 0.3), 6)
    ellipse(c, 0, -150, 90, 22)
    fs(c, (0.25, 0.22, 0.25), 5)
    ellipse(c, 0, -150, 72, 15)
    fill(c, mix((0.85, 0.85, 0.9), (1, 0.65, 0.2), glowa))
    c.restore()


def coin_press(c, x, y, s=1.0, press=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    soft_shadow(c, 20, 6, 260, 24, 0.35)
    box3d(c, -220, 0, 440, 120, 40, (0.5, 0.38, 0.28))
    for px in (-200, 140):
        box3d(c, px, -120, 60, 520, 20, (0.45, 0.35, 0.28))
    box3d(c, -220, -640, 440, 80, 30, (0.42, 0.33, 0.27))
    # screw + ram
    ry = -560 + press * 300
    c.rectangle(-14, -640, 28, ry + 640)
    fs(c, (0.6, 0.6, 0.65), 4)
    box3d(c, -70, ry + 90, 140, 90, 20, (0.6, 0.6, 0.66))
    # cross bar
    rrect(c, -230, -680, 460, 22, 8)
    fs(c, (0.35, 0.35, 0.4), 5)
    for bx in (-230, 230):
        c.arc(bx, -669, 22, 0, 2 * math.pi)
        fs(c, (0.55, 0.55, 0.6), 5)
    c.restore()


def apple(c, x, y, s=1.0, rot=0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    c.move_to(0, -30)
    c.curve_to(30, -50, 60, -10, 34, 30)
    c.curve_to(20, 50, -20, 50, -34, 30)
    c.curve_to(-60, -10, -30, -50, 0, -30)
    c.close_path()
    fs(c, (0.9, 0.2, 0.2), 5)
    c.move_to(0, -30)
    c.line_to(4, -52)
    stroke(c, 5, (0.4, 0.25, 0.1))
    ellipse(c, 18, -46, 14, 7)
    fs(c, (0.35, 0.7, 0.3), 3)
    ellipse(c, -16, -12, 9, 6)
    fill(c, (1, 1, 1), 0.6)
    c.restore()


def red_x(c, x, y, s=1.0, t=1.0):
    k = clamp(t)
    c.save()
    c.translate(x, y)
    c.scale(s * (0.5 + 0.5 * k), s * (0.5 + 0.5 * k))
    for a in (1, -1):
        c.move_to(-90, -90 * a)
        c.line_to(90, 90 * a)
    stroke(c, 46, INK)
    for a in (1, -1):
        c.move_to(-90, -90 * a)
        c.line_to(90, 90 * a)
    stroke(c, 30, (0.92, 0.15, 0.2))
    c.restore()


def check(c, x, y, s=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.move_to(-80, 0)
    c.line_to(-20, 60)
    c.line_to(90, -70)
    stroke(c, 46, INK)
    c.move_to(-80, 0)
    c.line_to(-20, 60)
    c.line_to(90, -70)
    stroke(c, 30, (0.2, 0.75, 0.3))
    c.restore()


def interior(c, wall=(0.55, 0.38, 0.25), floor=(0.42, 0.28, 0.2), fy=1300, planks=True):
    c.rectangle(-1500, -1500, 4200, fy + 1500)
    g = vgrad(c, 0, fy, [(0, shade(wall, 0.7)), (1, wall)])
    c.set_source(g)
    c.fill()
    if planks:
        for k in range(-20, 50):
            c.move_to(k * 90, -1500)
            c.line_to(k * 90, fy)
            stroke(c, 3, shade(wall, 0.75))
    c.rectangle(-1500, fy, 4200, 2000)
    g = vgrad(c, fy, fy + 700, [(0, floor), (1, shade(floor, 0.7))])
    c.set_source(g)
    c.fill()
    for k in range(-10, 30):
        c.move_to(k * 160, fy)
        c.line_to(k * 160 + (k * 160 - 540) * 0.8, fy + 700)
        stroke(c, 3, shade(floor, 0.7))
    c.move_to(-1500, fy)
    c.line_to(2700, fy)
    stroke(c, 7)


def window_night(c, x, y, w, h, t=0, moon_=True):
    rrect(c, x - 14, y - 14, w + 28, h + 28, 10)
    fs(c, (0.4, 0.26, 0.16), 6)
    c.rectangle(x, y, w, h)
    g = vgrad(c, y, y + h, [(0, (0.08, 0.1, 0.3)), (1, (0.25, 0.2, 0.45))])
    c.set_source(g)
    c.fill_preserve()
    c.save()
    c.clip()
    stars(c, x, y, w, h, 15, t)
    if moon_:
        moon(c, x + w * 0.7, y + h * 0.3, 30)
    c.restore()
    c.move_to(x + w / 2, y)
    c.line_to(x + w / 2, y + h)
    c.move_to(x, y + h / 2)
    c.line_to(x + w, y + h / 2)
    stroke(c, 10, (0.4, 0.26, 0.16))
    c.rectangle(x, y, w, h)
    stroke(c, 6)


def table(c, x, y, w=500, h=160, col=(0.6, 0.4, 0.25), d=30):
    soft_shadow(c, x + w / 2 + 20, y + 4, w * 0.6, 20, 0.3)
    for lx in (x + 20, x + w - 40):
        c.rectangle(lx, y - h, 20, h)
        fs(c, shade(col, 0.8), 5)
    poly(c, [(x - 20, y - h), (x + w + 20, y - h), (x + w + 20 + d, y - h - d * 0.8), (x - 20 + d, y - h - d * 0.8)])
    fs(c, shade(col, 1.15), 6)
    c.rectangle(x - 20, y - h, w + 40, 26)
    fs(c, col, 6)


def barrel(c, x, y, s=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    soft_shadow(c, 10, 4, 70, 12, 0.3)
    c.move_to(-55, 0)
    c.curve_to(-75, -60, -75, -100, -55, -160)
    c.line_to(55, -160)
    c.curve_to(75, -100, 75, -60, 55, 0)
    c.close_path()
    fs(c, (0.62, 0.4, 0.22), 6)
    for yy in (-30, -130):
        c.move_to(-66, yy)
        c.line_to(66, yy)
        stroke(c, 8, (0.35, 0.35, 0.4))
    ellipse(c, 0, -160, 55, 14)
    fs(c, (0.7, 0.48, 0.28), 5)
    c.restore()


def mug(c, x, y, s=1.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.arc(30, -40, 18, -1.4, 1.4)
    stroke(c, 8)
    rrect(c, -26, -80, 56, 80, 8)
    fs(c, (0.75, 0.55, 0.3), 5)
    ellipse(c, 2, -80, 30, 12)
    fs(c, (1, 0.97, 0.9), 4)
    c.restore()


def lamp(c, x, y, s=1.0, t=0, col=(1, 0.75, 0.35)):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.move_to(0, -200)
    c.line_to(0, -40)
    stroke(c, 4)
    glow(c, 0, 0, 260, col, 0.4 + 0.05 * math.sin(t * 7))
    poly(c, [(-30, -40), (30, -40), (24, 30), (-24, 30)])
    fs(c, (1.0, 0.85, 0.5), 5)
    rrect(c, -36, -50, 72, 14, 5)
    fs(c, (0.25, 0.22, 0.25), 4)
    c.restore()


# ----------------------------------------------------------------------------- ships story
def ocean(c, y, t, x0=-1500, x1=2600, storm=0.0, col=(0.2, 0.45, 0.75), layers=4, depth=1800):
    for L in range(layers):
        yy = y + L * 70
        amp = 14 + 26 * storm + L * 4
        k = 0.012 - L * 0.001
        sp = (1.2 + storm * 2) * (1 if L % 2 else -1)
        cc = shade(col, 1.15 - L * 0.12)
        c.move_to(x0, yy + depth)
        n = 70
        for i in range(n + 1):
            xx = lerp(x0, x1, i / n)
            c.line_to(xx, yy + math.sin(xx * k + t * sp + L) * amp + math.sin(xx * k * 2.3 - t * sp * 0.7) * amp * 0.4)
        c.line_to(x1, yy + depth)
        c.close_path()
        fs(c, cc, 6)
        # foam caps
        for i in range(0, n, 5):
            xx = lerp(x0, x1, i / n) + (t * 30 * sp) % 50
            wy = yy + math.sin(xx * k + t * sp + L) * amp + math.sin(xx * k * 2.3 - t * sp * 0.7) * amp * 0.4
            ellipse(c, xx, wy + 4, 14, 5)
            fill(c, (1, 1, 1), 0.5)


def ship(c, x, y, s=1.0, t=0.0, roll=0.04, sails=True, flag=(0.85, 0.15, 0.2), lanterns=0, lit=None, people=None, sunny=False):
    c.save()
    c.translate(x, y + math.sin(t * 1.6) * 8 * s)
    c.rotate(math.sin(t * 1.3) * roll)
    c.scale(s, s)
    # masts
    for mx, mh in ((-150, 520), (40, 600), (210, 430)):
        rrect(c, mx - 10, -mh - 60, 20, mh, 5)
        fs(c, (0.45, 0.3, 0.18), 5)
        if sails:
            sw = 0.14 * math.sin(t * 1.1 + mx)
            for k, (sy, sh_, w) in enumerate(((-mh - 20, 150, 170), (-mh + 160, 160, 210))):
                if sy + sh_ > -80:
                    continue
                c.move_to(mx - w / 2, sy)
                c.line_to(mx + w / 2, sy)
                c.curve_to(mx + w / 2 + 30 + sw * 100, sy + sh_ * 0.5, mx + w / 2 + 20, sy + sh_, mx + w / 2, sy + sh_)
                c.line_to(mx - w / 2, sy + sh_)
                c.curve_to(mx - w / 2 + 20 + sw * 100, sy + sh_ * 0.5, mx - w / 2 + 10, sy + sh_ * 0.4, mx - w / 2, sy)
                c.close_path()
                fs(c, (0.97, 0.94, 0.86), 5)
                c.move_to(mx - w / 2 + 10, sy + sh_ * 0.5)
                c.line_to(mx + w / 2 + 5, sy + sh_ * 0.5)
                stroke(c, 3, (0.8, 0.75, 0.65))
    fx = 40
    fy = -660
    poly(c, [(fx, fy), (fx + 80, fy + 14 + wob(t, 2, 6)), (fx, fy + 30)])
    fs(c, flag, 4)
    if people:
        people(c)
    # hull
    c.move_to(-360, -80)
    c.line_to(380, -80)
    c.line_to(420, -130)
    c.curve_to(360, 40, 220, 70, 0, 70)
    c.curve_to(-220, 70, -330, 40, -360, -80)
    c.close_path()
    g = cairo.LinearGradient(0, -130, 0, 70)
    g.add_color_stop_rgb(0, 0.62, 0.4, 0.24)
    g.add_color_stop_rgb(1, 0.38, 0.23, 0.14)
    c.set_source(g)
    c.fill_preserve()
    stroke(c, 7)
    c.move_to(-350, -50)
    c.line_to(395, -50)
    stroke(c, 10, (0.85, 0.7, 0.3))
    c.move_to(-350, -50)
    c.line_to(395, -50)
    stroke(c, 3)
    for k in range(6):
        px = -250 + k * 100
        c.arc(px, -10, 14, 0, 2 * math.pi)
        fs(c, (0.15, 0.1, 0.1), 4)
    for k in range(lanterns):
        lx = -260 + k * 170
        on = lit[k] if lit else 1.0
        c.move_to(lx, -80)
        c.line_to(lx, -150)
        stroke(c, 4)
        if on > 0:
            glow(c, lx, -165, 120, (1, 0.75, 0.3), 0.6 * on)
        rrect(c, lx - 16, -190, 32, 44, 6)
        fs(c, mix((0.3, 0.3, 0.35), (1.0, 0.85, 0.45), on), 4)
    c.restore()


def hold_cutaway(c, x, y, s=1.0, t=0, crowd=None, light=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.move_to(-480, -520)
    c.line_to(480, -520)
    c.curve_to(470, 0, 300, 160, 0, 170)
    c.curve_to(-300, 160, -470, 0, -480, -520)
    c.close_path()
    fs(c, (0.45, 0.28, 0.16), 10)
    c.move_to(-430, -470)
    c.line_to(430, -470)
    c.curve_to(420, -10, 270, 120, 0, 125)
    c.curve_to(-270, 120, -420, -10, -430, -470)
    c.close_path()
    c.save()
    c.clip_preserve()
    dark = mix((0.12, 0.08, 0.1), (0.95, 0.85, 0.6), light)
    fill(c, dark)
    for k in range(-6, 7):
        c.move_to(k * 70, -470)
        c.line_to(k * 70, 200)
        stroke(c, 3, shade(dark, 1.4 if light < 0.5 else 0.9))
    for dy in (-260,):
        c.rectangle(-440, dy, 880, 20)
        fs(c, (0.4, 0.26, 0.15), 5)
    if crowd:
        crowd(c)
    c.restore()
    c.restore()


def dock(c, y, t=0, x0=-1500, x1=2600):
    ocean(c, y + 120, t, x0, x1, layers=2)
    c.rectangle(x0, y - 10, x1 - x0, 60)
    fs(c, (0.62, 0.43, 0.27), 7)
    for k in range(int((x1 - x0) / 80)):
        c.move_to(x0 + k * 80, y - 10)
        c.line_to(x0 + k * 80, y + 50)
        stroke(c, 3, (0.42, 0.28, 0.18))
    for k in range(int((x1 - x0) / 300)):
        px = x0 + 100 + k * 300
        rrect(c, px - 18, y - 60, 36, 260, 6)
        fs(c, (0.5, 0.34, 0.2), 6)


def map_table(c, x, y, s=1.0, route=0.0, ship_draw=None):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    rrect(c, -480, -330, 960, 660, 20)
    fs(c, (0.45, 0.28, 0.16), 9)
    c.move_to(-430, -290)
    for k in range(9):
        c.line_to(-430 + k * 108, -290 + (8 if k % 2 else -4))
    c.line_to(430, 290)
    c.line_to(-430, 290)
    c.close_path()
    fs(c, (0.96, 0.88, 0.68), 6)
    # sea tint
    # Britain (top-left), Africa (mid), Australia (bottom-right)
    land = (0.72, 0.8, 0.5)
    for pts in ([(-370, -240), (-330, -270), (-300, -220), (-320, -170), (-360, -180)],
                [(-260, -140), (-140, -150), (-100, -40), (-150, 120), (-210, 160), (-230, 40), (-280, -60)],
                [(200, 120), (330, 90), (400, 150), (390, 240), (280, 260), (210, 210)]):
        poly(c, pts)
        fs(c, land, 5)
    label(c, "BRITAIN", -330, -205 - 50, 28, (0.35, 0.2, 0.1), "Lilita One", cairo.FONT_WEIGHT_NORMAL)
    label(c, "AUSTRALIA", 300, 285 - 20, 28, (0.35, 0.2, 0.1), "Lilita One", cairo.FONT_WEIGHT_NORMAL)
    path = [(-320, -170), (-330, -60), (-300, 100), (-180, 230), (0, 250), (150, 200), (230, 170)]
    # sample along path
    pts = []
    for i in range(len(path) - 1):
        for k in range(20):
            u = k / 20
            pts.append((lerp(path[i][0], path[i + 1][0], u), lerp(path[i][1], path[i + 1][1], u)))
    pts.append(path[-1])
    nshow = int(len(pts) * clamp(route))
    for i in range(0, nshow, 4):
        c.arc(pts[i][0], pts[i][1], 6, 0, 2 * math.pi)
        fill(c, (0.75, 0.15, 0.15))
    if ship_draw and nshow > 0:
        px, py = pts[min(nshow, len(pts) - 1)]
        ship_draw(c, px, py)
    c.restore()


def chalkboard(c, x, y, w, h):
    rrect(c, x - w / 2 - 24, y - h / 2 - 24, w + 48, h + 48, 16)
    fs(c, (0.55, 0.36, 0.2), 8)
    c.rectangle(x - w / 2, y - h / 2, w, h)
    g = cairo.RadialGradient(x - w * 0.2, y - h * 0.2, 0, x, y, w * 0.8)
    g.add_color_stop_rgb(0, 0.22, 0.38, 0.3)
    g.add_color_stop_rgb(1, 0.13, 0.24, 0.19)
    c.set_source(g)
    c.fill_preserve()
    stroke(c, 6)


def contract(c, x, y, s=1.0, strike=0.0, stamp=0.0, t=0, title="CONTRACT", line1="PAID PER PRISONER", line2="ON the ship", line3="OFF the ship ALIVE"):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    soft_shadow(c, 20, 330, 330, 30, 0.3)
    c.move_to(-300, -380)
    c.line_to(300, -380)
    c.line_to(300, 380)
    c.line_to(-300, 380)
    c.close_path()
    fs(c, (0.97, 0.92, 0.78), 7)
    label(c, title, 0, -300, 64, (0.35, 0.2, 0.1), "Lilita One", cairo.FONT_WEIGHT_NORMAL)
    for k in range(3):
        c.move_to(-240, -210 + k * 40)
        c.line_to(240 - (k % 2) * 80, -210 + k * 40)
        stroke(c, 5, (0.6, 0.5, 0.4))
    label(c, line1, 0, -40, 42, INK, "Lilita One", cairo.FONT_WEIGHT_NORMAL)
    label(c, line2, 0, 40, 54, (0.15, 0.15, 0.35), "Lilita One", cairo.FONT_WEIGHT_NORMAL)
    if strike > 0:
        _font(c, 54, "Lilita One")
        wd = c.text_extents(line2).x_advance
        c.move_to(-wd / 2 - 20, 40)
        c.line_to(-wd / 2 - 20 + (wd + 40) * clamp(strike), 34)
        stroke(c, 12, (0.85, 0.12, 0.15))
    for k in range(2):
        c.move_to(-240, 170 + k * 40)
        c.line_to(200, 170 + k * 40)
        stroke(c, 5, (0.6, 0.5, 0.4))
    if stamp > 0:
        k = 2.2 - 1.2 * clamp(stamp * 3)
        c.save()
        c.translate(0, 110)
        c.rotate(-0.12)
        c.scale(k, k)
        rrect(c, -230, -50, 460, 100, 12)
        fill(c, (0.2, 0.6, 0.25), 0.15 * clamp(stamp * 3))
        rrect(c, -230, -50, 460, 100, 12)
        stroke(c, 10, (0.2, 0.6, 0.25), clamp(stamp * 3))
        label(c, line3, 0, 0, 52, (0.2, 0.6, 0.25), "Lilita One", cairo.FONT_WEIGHT_NORMAL, a=clamp(stamp * 3))
        c.restore()
    c.restore()


def quill(c, x, y, s=1.0, rot=-0.6):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    c.move_to(0, 0)
    c.curve_to(30, -80, 40, -220, 10, -320)
    c.curve_to(-30, -220, -20, -80, 0, 0)
    c.close_path()
    fs(c, (0.98, 0.98, 0.96), 5)
    c.move_to(0, 10)
    c.line_to(8, -300)
    stroke(c, 3, (0.6, 0.6, 0.6))
    poly(c, [(-5, 0), (5, 0), (0, 30)])
    fs(c, INK, 3)
    c.restore()


def crate(c, x, y, s=1.0, fruit=(1.0, 0.6, 0.1)):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    for k in range(6):
        c.arc(-60 + (k % 3) * 60, -110 - (k // 3) * 25, 28, 0, 2 * math.pi)
        fs(c, fruit if k % 2 else (0.9, 0.2, 0.2), 4)
    box3d(c, -100, 0, 200, 110, 26, (0.78, 0.6, 0.38))
    for yy in (-75, -35):
        c.move_to(-100, yy)
        c.line_to(100, yy)
        stroke(c, 3, (0.5, 0.36, 0.2))
    c.restore()
