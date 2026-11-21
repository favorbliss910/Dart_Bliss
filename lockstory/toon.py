"""Procedural toon drawing kit: Pen (supersampled outline drawing), animals, props.
Character space: origin = feet/perch point, y up is negative, d = +1 faces right."""
import math
from PIL import Image, ImageDraw, ImageFont

OUT = (28, 22, 36)
SS = 2
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"


def rotp(p, piv, a):
    r = math.radians(a); c, s = math.cos(r), math.sin(r)
    dx, dy = p[0] - piv[0], p[1] - piv[1]
    return (piv[0] + dx * c - dy * s, piv[1] + dx * s + dy * c)


class Pen:
    def __init__(self, w, h, ox, oy, scale, d=1):
        self.S = scale * SS; self.d = d; self.ox = ox; self.oy = oy
        self.w, self.h, self.scale = w, h, scale
        self.im = Image.new("RGBA", (int(w * self.S), int(h * self.S)), (0, 0, 0, 0))
        self.g = ImageDraw.Draw(self.im)

    def P(self, x, y):
        return ((self.ox + x * self.d) * self.S, (self.oy + y) * self.S)

    def poly(self, pts, col, ow=6):
        pp = [self.P(*p) for p in pts]
        if ow:
            self.g.line(pp + [pp[0]], fill=OUT, width=int(2 * ow * self.S), joint="curve")
            r = ow * self.S
            for p in pp: self.g.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=OUT)
        self.g.polygon(pp, fill=col)

    def ell(self, cx, cy, rx, ry, col, rot=0, ow=6, n=36):
        pts = [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]
        if rot: pts = [rotp(p, (cx, cy), rot) for p in pts]
        self.poly(pts, col, ow)

    def line(self, p, q, w, col, ow=6):
        a, b = self.P(*p), self.P(*q)
        for ww, cc in ((w + 2 * ow, OUT), (w, col)) if ow else ((w, col),):
            self.g.line([a, b], fill=cc, width=int(ww * self.S))
            r = ww * self.S / 2
            for c in (a, b): self.g.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=cc)

    def curve(self, pts, w, col, ow=6):          # thick poly-line
        for i in range(len(pts) - 1):
            self.line(pts[i], pts[i + 1], w, col, ow)

    def done(self):
        im = self.im.resize((int(self.w * self.scale), int(self.h * self.scale)), Image.LANCZOS)
        return im, (self.ox * self.scale, self.oy * self.scale)


def put(canvas, res, x, y):
    im, (ox, oy) = res[0], res[1]
    canvas.alpha_composite(im, (int(x - ox), int(y - oy)))


# =========================================================== MEERKAT
def meerkat(pose, d=1, scale=1.5):
    p = Pen(1100, 1040, 440, 960, scale, d)
    bob = pose.get("bob", 0); lean = pose.get("lean", 0); tilt = pose.get("tilt", 0)
    TAN, DK, CREAM = (200, 156, 104), (74, 48, 36), (238, 212, 168)
    hip = (0, -170 + bob)
    U = lambda x, y: rotp((x, y + bob), hip, lean)
    # tail
    p.curve([U(-60, -170), U(-170, -120), U(-250, -40)], 26, TAN, 6)
    p.ell(*U(-255, -36), 15, 15, DK, 0, 4)
    # legs
    for sx in (-1, 1):
        p.line((sx * 36, -150 + bob * 0.3), (sx * 40 + 6, -22), 44, (180, 136, 90))
        p.ell(sx * 40 + 28, -14, 46, 17, DK, 0, 5)
    # back arm
    a_b = pose.get("armB", pose.get("arm", 14)); a_f = pose.get("arm", 14)
    def arm(a, col):
        sh = U(30, -470); r = math.radians(a + lean)
        en = (sh[0] + math.sin(r) * 150, sh[1] + math.cos(r) * 150)
        p.line(sh, en, 38, col, 6); p.ell(en[0], en[1], 24, 22, DK, 0, 5)
    arm(a_b, (178, 134, 88))
    # body
    pts = [U(100 * math.cos(t) * 1.0, -330 + 215 * math.sin(t)) for t in [2 * math.pi * i / 40 for i in range(40)]]
    p.poly(pts, TAN, 7)
    pts = [U(30 + 62 * math.cos(t), -320 + 150 * math.sin(t)) for t in [2 * math.pi * i / 36 for i in range(36)]]
    p.poly(pts, CREAM, 0)
    for i in range(4):                                 # back stripes
        y = -430 + i * 70
        p.line(U(-92, y), U(-48, y + 14), 14, DK, 0)
    arm(a_f, TAN)
    # head
    neck = (10, -540)
    Hd = lambda x, y: U(*rotp((x, y), neck, tilt))
    p.line(U(10, -470), Hd(20, -580), 60, TAN, 6)
    p.ell(*Hd(-34, -700), 26, 26, DK, 0, 5)                       # ear
    p.ell(*Hd(22, -620), 92, 102, CREAM, tilt + lean, 7)           # head
    p.ell(*Hd(98, -588), 62, 44, CREAM, tilt + lean, 6)            # snout
    p.ell(*Hd(48, -628), 40, 50, DK, tilt + lean, 0)               # eye patch
    eyes = pose.get("eyes", "dot"); look = pose.get("look", (1, 0))
    ex, ey = Hd(52, -630)
    if eyes == "closed":
        p.line(Hd(34, -630), Hd(72, -630), 9, OUT, 0)
    else:
        rr = 27 if eyes == "wide" else 22
        p.ell(ex, ey, rr, rr, (255, 255, 255), 0, 5)
        p.ell(ex + look[0] * 8, ey + look[1] * 8, 9 if eyes != "wide" else 7, 9 if eyes != "wide" else 7, OUT, 0, 0)
        if eyes == "squint":
            p.poly([(ex - 34, ey - 34), (ex + 34, ey - 34), (ex + 34, ey - 3), (ex - 34, ey - 3)], DK, 0)
            p.line((ex - 30, ey - 3), (ex + 30, ey - 3), 8, OUT, 0)
    br = pose.get("brow", 0)
    p.line(Hd(28, -680 - br * 10), Hd(78, -672 + (pose.get("angry", 0)) * 22 - br * 10), 9, OUT, 0)
    nose = Hd(150, -592)
    p.ell(nose[0], nose[1], 16, 14, OUT, 0, 0)
    mo = pose.get("mouth", "smile"); op = pose.get("open", 0.6)
    if mo == "open":
        p.poly([Hd(86, -560), Hd(140, -566), Hd(128, -560 + 44 * op + 8), Hd(92, -560 + 44 * op + 8)], (120, 34, 44), 4)
    elif mo == "smile":
        p.curve([Hd(84, -568), Hd(112, -556), Hd(142, -568)], 6, OUT, 0)
    elif mo == "munch":
        k = 10 + 14 * abs(math.sin(pose.get("munch", 0)))
        p.poly([Hd(88, -562), Hd(138, -566), Hd(128, -562 + k), Hd(94, -562 + k)], (120, 34, 44), 4)
    if pose.get("shades"):
        p.poly([Hd(20, -655), Hd(90, -655), Hd(90, -615), Hd(20, -615)], (20, 20, 28), 3)
        p.line(Hd(20, -640), Hd(-30, -650), 6, OUT, 0)
    if pose.get("cap"):
        p.poly([Hd(-60, -690), Hd(100, -690), Hd(96, -760), Hd(-50, -760)], (40, 60, 120), 5)
        p.poly([Hd(60, -690), Hd(150, -684), Hd(100, -668), Hd(40, -672)], (28, 40, 90), 4)
        p.ell(*Hd(30, -725), 14, 14, (240, 200, 70), 0, 3)
    return p.done()


# =========================================================== DRONGO
def drongo(pose, d=1, scale=1.5):
    p = Pen(1100, 760, 550, 560, scale, d)
    sp = pose.get("sp", "drongo")
    BK, SH = {"drongo": ((24, 26, 38), (62, 86, 140)), "cuckoo": ((126, 130, 148), (176, 182, 198)),
              "magpie": ((24, 26, 38), (50, 150, 140)), "crow": ((30, 30, 40), (70, 70, 96))}[sp]
    BELLY = {"cuckoo": (236, 226, 204), "magpie": (248, 248, 252)}.get(sp)
    EYE = {"drongo": (210, 36, 40), "cuckoo": (240, 160, 40), "magpie": (250, 250, 250), "crow": (250, 250, 250)}[sp]
    bob = pose.get("bob", 0); rot = pose.get("rot", 0)          # body rotation (flight)
    wing = pose.get("wing", None)                               # None = folded
    fly = wing is not None
    pv = (0, -170 + bob)
    T = lambda x, y: rotp((x, y + bob), pv, rot)
    tw = pose.get("tail", 0)
    # feet
    if not fly:
        for fx in (-14, 28):
            p.line((fx, -110 + bob), (fx + 4, 0), 12, (80, 70, 80), 5)
            p.curve([(fx + 4, 0), (fx + 30, -4)], 10, (80, 70, 80), 5)
    else:
        for fx in (-10, 30):
            p.line(T(fx, -100), T(fx + 30, -60), 12, (80, 70, 80), 5)
    # forked tail
    base = T(-100, -150)
    if sp in ("cuckoo", "magpie"):
        p.poly([base, T(-470, -120 + tw), T(-480, -150 + tw), T(-120, -200)], BK, 6)
        p.poly([T(-300, -150), T(-460, -128 + tw), T(-470, -146 + tw), T(-300, -176)], SH, 0)
    elif sp == "crow":
        p.poly([base, T(-260, -110 + tw), T(-250, -190 + tw), T(-110, -190)], BK, 6)
    else:
        p.poly([base, T(-380, -60 + tw), T(-330, -110 + tw * 0.5), T(-300, -140), T(-390, -230 + tw), T(-110, -190)], BK, 6)
        p.poly([T(-325, -105 + tw), T(-372, -66 + tw), T(-338, -96)], SH, 0)
    # back wing in flight
    def wingshape(sign, a, col):
        sh = T(-10, -215); r = math.radians(a)
        ln = 330
        tip = (sh[0] + math.sin(r) * 0 - 0, sh[1])
        pts = []
        for k in range(5):
            f = k / 4
            ang = r + math.radians(-14 + f * 34 * sign)
            L = ln * (0.7 + 0.3 * math.sin(f * math.pi))
            pts.append((sh[0] - math.sin(ang) * L * 0.55 - 60 * (1 - f), sh[1] - math.cos(ang) * L))
        poly = [sh] + pts + [(sh[0] - 120, sh[1] - 20)]
        p.poly(poly, col, 6)
    if fly:
        wingshape(1, 55 - wing, (14, 16, 26))
    # body
    p.ell(*T(-10, -170), 128, 80, BK, rot - 22, 7)
    p.ell(*T(-34, -198), 70, 26, SH, rot - 22, 0)
    if BELLY:
        p.ell(*T(18, -140), 92, 40, BELLY, rot - 12, 0)
        if sp == "cuckoo":
            for k in range(5): p.line(T(-40 + k * 26, -158), T(-30 + k * 26, -118), 7, (150, 140, 128), 0)
    if not fly:
        p.ell(*T(-40, -180), 72, 38, (14, 16, 26), rot - 30, 4)    # folded wing
    # head
    tilt = pose.get("tilt", 0)
    neck = T(70, -220)
    Hd = lambda x, y: rotp(T(x, y), neck, tilt)
    hc = Hd(100, -262)
    p.ell(hc[0], hc[1], 66, 64, BK, 0, 7)
    if sp == "cuckoo": p.poly([Hd(60, -300), Hd(110, -360), Hd(130, -300)], BK, 5)
    if sp == "magpie": p.ell(*Hd(80, -240), 40, 30, BELLY, 0, 0)
    # beak
    op = pose.get("open", 0)
    bt = Hd(160, -268); bb = Hd(160, -238)
    p.poly([bb, Hd(250, -226 + op * 38), Hd(165, -240 + 6 + op * 10)], (14, 14, 20), 5)        # lower
    p.poly([bt, Hd(262, -246), Hd(250, -256 - op * 10), Hd(165, -292)], (20, 20, 28), 5)       # upper
    if op > 0.2:
        p.poly([Hd(168, -246), Hd(242, -246 + 0), Hd(238, -230 + op * 34), Hd(168, -242 + op * 6)], (150, 40, 52), 0)
    ex, ey = Hd(122, -280)
    eyes = pose.get("eyes", "dot")
    if eyes == "closed":
        p.line((ex - 20, ey), (ex + 20, ey), 8, (255, 255, 255), 0)
    else:
        rr = 24 if eyes != "wide" else 30
        p.ell(ex, ey, rr, rr, EYE, 0, 4)
        p.ell(ex + 3, ey, 11, 11, OUT, 0, 0)
        p.ell(ex - 3, ey - 7, 4, 4, (255, 255, 255), 0, 0)
        if eyes == "squint":
            p.poly([(ex - 32, ey - 32), (ex + 32, ey - 32), (ex + 32, ey - 2), (ex - 32, ey - 2)], BK, 0)
    br = pose.get("brow", 0)
    p.line(Hd(100, -322 - br * 6), Hd(150, -306 + pose.get("angry", 0) * 18 - br * 6), 9, OUT, 0)
    if pose.get("cap"):
        p.poly([Hd(60, -318), Hd(160, -318), Hd(150, -378), Hd(70, -378)], (40, 60, 120), 5)
        p.poly([Hd(120, -318), Hd(210, -312), Hd(160, -298), Hd(110, -300)], (28, 40, 90), 4)
        p.ell(*Hd(112, -348), 12, 12, (240, 200, 70), 0, 3)
    if fly:
        wingshape(-1, -(55 - wing), BK)
        pass
    return p.done()


# =========================================================== HAWK
def hawk(pose, d=1, scale=1.6):
    p = Pen(1500, 940, 750, 520, scale, d)
    BR, WH = (138, 92, 56), (240, 226, 200)
    wing = pose.get("wing", 0); rot = pose.get("rot", 0)
    pv = (0, 0)
    T = lambda x, y: rotp((x, y), pv, rot)
    def wingp(sign, col):
        sh = T(-20, -40)
        pts = []
        for k in range(7):
            f = k / 6
            a = math.radians(wing * sign * (0.4 + f * 0.8))
            L = 520 * (0.5 + f * 0.5)
            pts.append((sh[0] - 60 * f - 140 * f * f + (0), sh[1] - math.sin(a) * L * 0.9 - 0))
        pts = [(sh[0] - 40 - k * 70, sh[1] - (260 - k * 10) * math.sin(math.radians(wing * 0.9 + 20)) * (1 - k * 0.12)) for k in range(7)]
        poly = [sh, (sh[0] + 60, sh[1] - 30)] + [(x, y) for x, y in pts] + [(sh[0] - 400, sh[1] + 20), (sh[0] - 120, sh[1] + 40)]
        p.poly(poly, col, 7)
        for k in range(1, 6):
            p.line(pts[k], (pts[k][0] + 20, pts[k][1] + 70), 7, (90, 56, 34), 0)
    wingp(1, (120, 80, 48))
    # tail fan
    p.poly([T(-150, -10), T(-420, -70), T(-440, 10), T(-420, 80), T(-150, 40)], (176, 112, 64), 7)
    p.ell(*T(0, 0), 190, 80, BR, rot, 8)
    p.ell(*T(30, 24), 130, 42, WH, rot, 0)
    # head
    hc = T(200, -34)
    p.ell(hc[0], hc[1], 72, 66, BR, 0, 7)
    p.poly([T(250, -52), T(332, -36), T(300, 4), T(256, -8)], (240, 190, 50), 6)                 # beak
    p.poly([T(300, -14), T(332, -34), T(318, 20)], (40, 30, 24), 3)
    ex, ey = T(228, -62)
    p.ell(ex, ey, 21, 21, (250, 220, 70), 0, 4); p.ell(ex + 4, ey, 9, 9, OUT, 0, 0)
    p.line((ex - 36, ey - 26), (ex + 26, ey - 6), 12, OUT, 0)           # angry brow
    if pose.get("claws", 0):
        c = pose["claws"]
        for fx in (30, 80):
            a = T(fx, 60); b = (a[0] + 14, a[1] + 70 * c)
            p.line(a, b, 14, (240, 190, 50), 5)
            p.curve([b, (b[0] + 36, b[1] + 22 * c), (b[0] + 10, b[1] + 50 * c)], 9, (40, 30, 24), 3)
    wingp(-1, BR)
    return p.done()


# =========================================================== PROPS
def prop(kind, scale=1.0, rot=0, **kw):
    p = Pen(520, 420, 260, 240, scale)
    if kind == "beetle":
        p.ell(0, 0, 70, 52, (60, 40, 120), 0, 6); p.line((0, -50), (0, 50), 5, OUT, 0)
        for k in (-1, 1):
            for j in (-30, 0, 30): p.line((k * 40, j), (k * 100, j + 20), 8, OUT, 0)
        p.ell(80, 0, 26, 24, (40, 28, 80), 0, 5)
    elif kind == "scorpion":
        p.ell(0, 0, 84, 50, (150, 90, 40), 0, 6)
        p.curve([(-70, -10), (-120, -70), (-90, -140), (-20, -130)], 22, (150, 90, 40), 5)
        p.poly([(-20, -130), (30, -120), (-8, -98)], (220, 60, 40), 4)
        for j in (-30, 0, 30): p.line((10, j), (70, j + 36), 9, (110, 66, 30), 4)
        p.curve([(70, -20), (140, -50), (150, -10)], 20, (150, 90, 40), 5); p.curve([(70, 20), (140, 50), (150, 10)], 20, (150, 90, 40), 5)
        p.ell(40, -10, 10, 10, OUT, 0, 0)
    elif kind == "lizard":
        p.curve([(-170, 20), (-80, 0), (0, 10), (90, -4)], 40, (110, 170, 70), 6)
        p.ell(120, -4, 52, 40, (120, 184, 78), 0, 6); p.ell(132, -14, 11, 11, (255, 255, 255), 0, 4); p.ell(136, -14, 5, 5, OUT, 0, 0)
        p.curve([(-170, 20), (-230, 50)], 14, (110, 170, 70), 5)
        for x in (-40, 40): p.line((x, 10), (x + 14, 56), 14, (100, 156, 64), 5)
    elif kind == "grub":
        for i in range(5):
            p.ell(-90 + i * 45, math.sin(i * 1.3) * 8, 52, 44, (255, 220, 110) if i % 2 else (255, 236, 150), 0, 6)
        p.ell(110, -4, 40, 36, (250, 190, 70), 0, 6); p.ell(122, -12, 8, 8, OUT, 0, 0)
    elif kind == "lunch":
        p.poly([(-70, -40), (70, -40), (70, 50), (-70, 50)], (220, 60, 60), 6)
        p.curve([(-36, -40), (-36, -80), (36, -80), (36, -40)], 12, (200, 200, 210), 5)
        p.line((-70, 0), (70, 0), 8, (240, 240, 240), 0)
    p.im = p.im.rotate(-rot, resample=Image.BICUBIC, center=(260 * p.S, 240 * p.S)) if rot else p.im
    return p.done()


def sparkle(canvas, x, y, r, a=255):
    g = ImageDraw.Draw(canvas)
    pts = []
    for i in range(8):
        rr = r if i % 2 == 0 else r * 0.28
        ang = math.pi / 4 * i - math.pi / 2
        pts.append((x + rr * math.cos(ang), y + rr * math.sin(ang)))
    g.polygon(pts, fill=(255, 245, 160, a), outline=(255, 255, 255, a))


def rings(canvas, x, y, t, n=3, col=(255, 255, 255), d=1, spread=70, maxr=520):
    """Concentric sound arcs travelling outward; t in seconds since start."""
    lay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    g = ImageDraw.Draw(lay)
    for i in range(n):
        u = (t * 1.6 - i * 0.28) % 1.0
        if t * 1.6 - i * 0.28 < 0: continue
        r = 60 + u * maxr
        a = int(255 * (1 - u))
        box = [x - r, y - r, x + r, y + r]
        s, e = (-50, 50) if d > 0 else (130, 230)
        g.arc(box, s, e, fill=col + (a,), width=16)
    canvas.alpha_composite(lay)


def dust(canvas, x, y, t, n=9, seed=1):
    import random
    rnd = random.Random(seed)
    lay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    g = ImageDraw.Draw(lay)
    for i in range(n):
        a = rnd.uniform(-math.pi, 0); sp = rnd.uniform(80, 280)
        r = 30 + 90 * t * rnd.uniform(0.6, 1.2)
        px, py = x + math.cos(a) * sp * t, y + math.sin(a) * sp * t * 0.7
        g.ellipse([px - r, py - r, px + r, py + r], fill=(222, 190, 140, int(200 * max(0, 1 - t))))
    canvas.alpha_composite(lay)


def bubble(canvas, text, x, y, size=84, tail=(0, 120), scale=1.0, col=(255, 255, 255), tcol=(30, 24, 40)):
    if scale < 0.3: return
    f = ImageFont.truetype(FONT, int(size * scale))
    g = ImageDraw.Draw(canvas)
    bb = g.textbbox((0, 0), text, font=f)
    w, h = bb[2] - bb[0] + 70 * scale, bb[3] - bb[1] + 56 * scale
    x0, y0 = x - w / 2, y - h / 2
    g.rounded_rectangle([x0 - 8, y0 - 8, x0 + w + 8, y0 + h + 8], int(h / 2), fill=OUT)
    g.rounded_rectangle([x0, y0, x0 + w, y0 + h], int(h / 2) - 6, fill=col)
    tx, ty = x + tail[0], y + h / 2 + tail[1] * scale
    g.polygon([(x - 28 * scale, y + h / 2 - 6), (x + 28 * scale, y + h / 2 - 6), (tx, ty)], fill=OUT)
    g.polygon([(x - 18 * scale, y + h / 2 - 12), (x + 18 * scale, y + h / 2 - 12), (tx, ty - 14 * scale)], fill=col)
    g.text((x0 + 35 * scale - bb[0], y0 + 28 * scale - bb[1]), text, font=f, fill=tcol)


def label(canvas, text, x, y, size=96, col=(255, 255, 255), stroke=12):
    if size < 8: return
    f = ImageFont.truetype(FONT, size)
    g = ImageDraw.Draw(canvas)
    bb = g.textbbox((0, 0), text, font=f, stroke_width=stroke)
    g.text((x - (bb[2] - bb[0]) / 2 - bb[0], y - (bb[3] - bb[1]) / 2 - bb[1]), text, font=f, fill=col,
           stroke_width=stroke, stroke_fill=OUT)
