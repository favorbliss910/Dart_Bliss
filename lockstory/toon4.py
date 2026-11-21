"""Pseudo-3D toolkit: perspective road canyon, first-person cockpit, aerial city, glow, depth-of-field.
All procedural. Cars are REAR-VIEW sprites scaled by depth, so near cars are huge (not toys)."""
import math, random
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFilter
from toon import Pen, OUT, put, FONT

DW, DH = 1440, 2560


# ---------------------------------------------------------------- generic fx
def soft(im, r):
    """Fast blur (depth of field): blur at reduced resolution."""
    s = max(1, int(r / 3))
    w, h = im.size
    sm = im.resize((max(1, w // s), max(1, h // s)), Image.BILINEAR).filter(ImageFilter.GaussianBlur(r / s))
    return sm.resize((w, h), Image.BILINEAR)


@lru_cache(maxsize=64)
def _radial(r, col):
    n = int(r * 2)
    lay = Image.new("RGBA", (n, n), (0, 0, 0, 0)); g = ImageDraw.Draw(lay)
    for k in range(24, 0, -1):
        rr = r * k / 24
        g.ellipse([r - rr, r - rr, r + rr, r + rr], fill=col + (int(255 * (1 - k / 24) ** 2 * 0.55),))
    return lay


def glow(cv, x, y, r, col=(255, 230, 160), a=1.0):
    lay = _radial(int(r), col)
    if a < 1: lay = lay.copy(); lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    cv.alpha_composite(lay, (int(x - r), int(y - r))) if (-r < x < cv.width + r and -r < y < cv.height + r) else None


def rays(cv, x, y, t, n=9, length=2600, col=(255, 240, 200), a=34):
    lay = Image.new("RGBA", cv.size, (0, 0, 0, 0)); g = ImageDraw.Draw(lay)
    for i in range(n):
        ang = math.radians(20 + i * (140 / n) + 6 * math.sin(t * 0.5 + i))
        w = 0.05 + 0.03 * math.sin(i * 2.1)
        g.polygon([(x, y), (x + math.cos(ang - w) * length, y + math.sin(ang - w) * length), (x + math.cos(ang + w) * length, y + math.sin(ang + w) * length)], fill=col + (a,))
    cv.alpha_composite(soft(lay, 40))


def smoke(cv, x, y, t, n=6, seed=0, col=(200, 200, 205)):
    rnd = random.Random(seed); g = ImageDraw.Draw(cv, "RGBA")
    for i in range(n):
        ph = (t * 0.9 + rnd.random()) % 1.0
        px = x + rnd.uniform(-30, 30) - 130 * ph; py = y - 220 * ph; r = 24 + 80 * ph
        g.ellipse([px - r, py - r, px + r, py + r], fill=col + (int(130 * (1 - ph)),))


# ---------------------------------------------------------------- rear-view cars
@lru_cache(maxsize=128)
def car_rear(kind="car", color=(220, 60, 60)):
    p = Pen(440, 330, 220, 300, 1.0)
    body = (250, 250, 252) if kind == "amb" else color
    dk = tuple(int(c * 0.72) for c in body)
    if kind == "bus":
        p.poly([(-190, -20), (190, -20), (190, -270), (-190, -270)], body, 9)
        for r in range(2):
            for c in range(4): p.poly([(-160 + c * 82, -240 + r * 90), (-100 + c * 82, -240 + r * 90), (-100 + c * 82, -190 + r * 90), (-160 + c * 82, -190 + r * 90)], (150, 200, 240), 4)
        p.poly([(-190, -50), (190, -50), (190, -20), (-190, -20)], dk, 6)
        for sx in (-150, 150): p.poly([(sx - 26, -120), (sx + 26, -120), (sx + 26, -76), (sx - 26, -76)], (230, 40, 50), 5)
        p.poly([(-30, -60), (30, -60), (30, -36), (-30, -36)], (250, 250, 250), 3)
        return p.done()
    p.poly([(-190, -110), (190, -110), (196, -26), (-196, -26)], body, 9)                      # lower body
    p.poly([(-150, -112), (-118, -214), (118, -214), (150, -112)], dk if kind != "amb" else (240, 240, 244), 9)  # cabin
    p.poly([(-128, -122), (-104, -200), (104, -200), (128, -122)], (46, 66, 98), 5)               # rear glass
    p.line((-90, -190), (-40, -130), 10, (130, 160, 210), 0)
    if kind == "amb":
        p.line((-196, -80), (196, -80), 26, (222, 44, 52), 0)
        p.poly([(-110, -214), (110, -214), (110, -250), (-110, -250)], (60, 60, 70), 5)
        p.poly([(-100, -220), (-10, -220), (-10, -244), (-100, -244)], (230, 50, 60), 3); p.poly([(10, -220), (100, -220), (100, -244), (10, -244)], (60, 110, 230), 3)
        p.line((0, -170), (0, -126), 14, (222, 44, 52), 0); p.line((-22, -148), (22, -148), 14, (222, 44, 52), 0)
    for sx in (-1, 1):                                                                       # tail lights
        p.poly([(sx * 118, -96), (sx * 184, -96), (sx * 186, -58), (sx * 120, -58)], (236, 40, 52), 6)
        p.poly([(sx * 130, -88), (sx * 172, -88), (sx * 172, -68), (sx * 130, -68)], (255, 190, 190), 0)
    p.poly([(-196, -46), (196, -46), (196, -22), (-196, -22)], (50, 52, 64), 6)             # bumper
    p.poly([(-34, -64), (34, -64), (34, -42), (-34, -42)], (250, 250, 240), 3)               # plate
    for sx in (-150, 150): p.ell(sx, -10, 36, 22, (24, 24, 32), 0, 5)                        # tyres
    return p.done()


def car_at(cv, x, ground_y, width_px, kind="car", color=(220, 60, 60), brake=True, flip=1):
    im = car_rear(kind, color)[0]
    sc = width_px / 392.0
    if sc < 0.03: return
    w, h = max(2, int(im.width * sc)), max(2, int(im.height * sc))
    sp = im.resize((w, h), Image.BILINEAR if sc < 1 else Image.BICUBIC)
    ox, oy = 220 * sc, 300 * sc
    sh = Image.new("RGBA", (int(width_px * 1.3), int(width_px * 0.22)), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([0, 0, sh.width, sh.height], fill=(0, 0, 0, 90))
    cv.alpha_composite(sh, (int(x - sh.width / 2), int(ground_y - sh.height / 2)))
    cv.alpha_composite(sp, (int(x - ox), int(ground_y - oy)))
    if brake:
        for sx in (-1, 1): glow(cv, x + sx * 152 * sc, ground_y - 77 * sc, width_px * 0.22, (255, 50, 50), 0.9)


# ---------------------------------------------------------------- perspective road
def _P(vp, f, h, x, y, z):
    return (vp[0] + x * f / z, vp[1] + (h - y) * f / z)


def road_view(cv, t, vp=(720, 980), f=1000.0, h=3.2, lanes=4, lane_w=3.8, speed=0.0, cars=(), night=False,
              sky=((110, 175, 240), (255, 232, 190)), buildings=True, seed=1, cam_x=0.0, crowd=False):
    g = ImageDraw.Draw(cv, "RGBA")
    W, H = cv.size
    top, bot = sky
    if night: top, bot = (24, 22, 60), (210, 110, 100)
    for y in range(0, int(vp[1]) + 40, 4):
        g.rectangle([0, y, W, y + 4], fill=tuple(int(top[i] + (bot[i] - top[i]) * min(1, y / max(1, vp[1]))) for i in range(3)))
    half = lanes * lane_w / 2
    rnd = random.Random(seed)
    # far skyline silhouette
    for k in range(18):
        x = k * 90 - 40; bh = 140 + rnd.randint(0, 340)
        g.rectangle([x, vp[1] - bh, x + 86, vp[1] + 6], fill=(120 - 30 * night, 140 - 30 * night, 180 - 40 * night))
    # ground: sidewalks + road
    g.rectangle([0, vp[1], W, H], fill=(150, 154, 164))
    zfar, znear = 160.0, 1.6
    def quad(x0, x1, z0, z1, col, y=0):
        pts = [_P(vp, f, h, x0 - cam_x, y, z0), _P(vp, f, h, x1 - cam_x, y, z0), _P(vp, f, h, x1 - cam_x, y, z1), _P(vp, f, h, x0 - cam_x, y, z1)]
        g.polygon(pts, fill=col)
    quad(-half, half, znear, zfar, (62, 64, 78))
    quad(-half - 0.5, -half, znear, zfar, (210, 210, 216)); quad(half, half + 0.5, znear, zfar, (210, 210, 216))
    # lane dashes
    ph = (speed * t) % 9.0
    for i in range(1, lanes):
        x = -half + i * lane_w
        z = -ph
        while z < zfar:
            z0, z1 = max(znear, z), z + 3.2
            if z1 > znear: quad(x - 0.09, x + 0.09, max(z0, znear), z1, (250, 240, 200, 235))
            z += 9.0
    # buildings canyon (far -> near)
    if buildings:
        for side in (-1, 1):
            xs = side * (half + 4.0)
            zz = zfar
            blds = []
            z = 8.0
            r2 = random.Random(seed * 7 + side)
            while z < 120:
                dz = r2.uniform(9, 15); bh = r2.uniform(14, 52); blds.append((z, z + dz, bh, r2.choice([(176, 120, 96), (150, 140, 176), (190, 170, 120), (120, 150, 170), (170, 100, 120)]))); z += dz + r2.uniform(0, 2)
            for z0, z1, bh, col in reversed(blds):
                shade = max(0.45, 1 - z0 / 150)
                c = tuple(int(v * shade + 150 * (1 - shade) * 0.3) for v in col)
                pts = [_P(vp, f, h, xs - cam_x, 0, z0), _P(vp, f, h, xs - cam_x, bh, z0), _P(vp, f, h, xs - cam_x, bh, z1), _P(vp, f, h, xs - cam_x, 0, z1)]
                g.polygon(pts, fill=c, outline=(30, 24, 40, 255))
                for wy in range(3, int(bh), 4):
                    for wz in range(int(z0) + 1, int(z1) - 1, 3):
                        if r2.random() < (0.7 if night else 0.35):
                            wp = [_P(vp, f, h, xs - cam_x, wy, wz), _P(vp, f, h, xs - cam_x, wy + 2, wz), _P(vp, f, h, xs - cam_x, wy + 2, wz + 1.8), _P(vp, f, h, xs - cam_x, wy, wz + 1.8)]
                            g.polygon(wp, fill=(255, 230, 150, 255) if night else (200, 230, 250, 255))
    # cars far -> near
    for c in sorted(cars, key=lambda c: -c["z"]):
        z = c["z"]
        if z < znear + 0.4: continue
        lx = -half + (c["lane"] + 0.5) * lane_w + c.get("dx", 0)
        sx, gy = _P(vp, f, h, lx - cam_x, 0, z)
        car_at(cv, sx, gy, 1.9 * f / z, c.get("kind", "car"), c.get("color", (220, 60, 60)), c.get("brake", True))
    # atmospheric haze toward horizon
    hz = Image.new("RGBA", cv.size, (0, 0, 0, 0)); hg = ImageDraw.Draw(hz)
    for k in range(40): hg.rectangle([0, vp[1] - 160 + k * 6, W, vp[1] - 160 + k * 6 + 6], fill=(bot[0], bot[1], bot[2], int(110 * math.sin(math.pi * k / 40) ** 1.2)))
    cv.alpha_composite(hz)


def jam_cars(t, lanes=4, n=7, seed=1, z0=3.6, gap=3.4, kinds=None, brake=True):
    rnd = random.Random(seed); cars = []
    cols = [(220, 60, 60), (60, 120, 220), (240, 190, 50), (70, 170, 110), (150, 90, 190), (240, 120, 50), (90, 200, 220), (240, 240, 240)]
    for l in range(lanes):
        for k in range(n):
            cars.append(dict(lane=l, z=z0 + k * gap + rnd.uniform(-0.4, 0.4) + l * 0.9 + 0.05 * math.sin(t * 3 + k + l), color=cols[(k * 3 + l * 5 + seed) % 8], kind=(kinds or {}).get((l, k), "car"), brake=brake, dx=rnd.uniform(-0.15, 0.15)))
    return cars


# ---------------------------------------------------------------- first-person cockpit
def cockpit(cv, t, steer=0.0, hands=True, honk=False, mirror=None):
    g = ImageDraw.Draw(cv, "RGBA"); W, H = cv.size
    g.polygon([(0, 0), (140, 0), (330, 1180), (0, 1500)], fill=(30, 28, 36, 255), outline=OUT)         # left pillar
    g.polygon([(W, 0), (W - 140, 0), (W - 330, 1180), (W, 1500)], fill=(30, 28, 36, 255), outline=OUT)
    g.rectangle([0, 0, W, 90], fill=(30, 28, 36, 255))
    g.polygon([(0, 1900), (W, 1900), (W, H), (0, H)], fill=(36, 34, 46, 255))                               # dashboard
    g.ellipse([-260, 1780, W + 260, 2240], fill=(44, 42, 56, 255), outline=OUT, width=10)
    g.rounded_rectangle([430, 1960, 1010, 2120], 40, fill=(20, 20, 30, 255), outline=(90, 90, 110, 255), width=6)    # cluster
    for k in range(5): g.line([(480 + k * 110, 2070), (480 + k * 110, 2100)], fill=(120, 220, 160, 255), width=6)
    # steering wheel
    cx, cy, R = 720, 2540, 460
    lay = Image.new("RGBA", (int(R * 2.4), int(R * 2.4)), (0, 0, 0, 0)); lg = ImageDraw.Draw(lay); c0 = R * 1.2
    lg.ellipse([c0 - R - 14, c0 - R * 0.8 - 14, c0 + R + 14, c0 + R * 0.8 + 14], outline=OUT, width=96)
    lg.ellipse([c0 - R, c0 - R * 0.8, c0 + R, c0 + R * 0.8], outline=(58, 58, 74, 255), width=72)
    lg.polygon([(c0 - 90, c0 - 30), (c0 + 90, c0 - 30), (c0 + 60, c0 + 100), (c0 - 60, c0 + 100)], fill=(58, 58, 74, 255), outline=OUT)
    lay = lay.rotate(steer, resample=Image.BICUBIC)
    cv.alpha_composite(lay, (int(cx - c0), int(cy - c0)))
    if honk: g.ellipse([cx - 80, cy - 110, cx + 80, cy + 30], fill=(255, 220, 80, 255))
    if hands:
        for sx in (-1, 1):
            hx, hy = cx + sx * (R * 0.78), cy - R * 0.5 + (10 * math.sin(t * 3 + sx) if not honk else 0)
            g.ellipse([hx - 66, hy - 54, hx + 66, hy + 70], fill=(238, 196, 160, 255), outline=OUT, width=8)
            g.rounded_rectangle([hx - 54 + sx * 30, hy + 40, hx + 54 + sx * 30, hy + 260], 30, fill=(70, 120, 180, 255), outline=OUT, width=8)
    # rear-view mirror
    g.rounded_rectangle([520, 110, 920, 250], 40, fill=(40, 40, 52, 255), outline=OUT, width=8)
    g.rounded_rectangle([540, 126, 900, 234], 30, fill=(150, 190, 220, 255))
    if mirror == "eyes":
        for ex in (680, 760): g.ellipse([ex - 24, 160, ex + 24, 208], fill=(255, 255, 255, 255), outline=OUT, width=5); g.ellipse([ex - 8 + 3 * math.sin(t * 2), 172, ex + 8 + 3 * math.sin(t * 2), 190], fill=OUT)
    # windshield glare
    gl = Image.new("RGBA", cv.size, (0, 0, 0, 0)); ImageDraw.Draw(gl).polygon([(300, 180), (620, 180), (380, 1500), (160, 1500)], fill=(255, 255, 255, 24))
    cv.alpha_composite(gl)


# ---------------------------------------------------------------- aerial city (top-down)
def aerial(cv, t, mode="skyway", seed=3):
    """mode: skyway (highway + jammed) | closed (highway gone, spread out) | plain"""
    g = ImageDraw.Draw(cv, "RGBA"); W, H = cv.size
    rnd = random.Random(seed)
    g.rectangle([0, 0, W, H], fill=(120, 170, 100))
    xs = [0, 360, 720, 1080, 1440]; ys = [0, 480, 960, 1440, 1920, 2400, 2880]
    for xi in range(len(xs) - 1):
        for yi in range(len(ys) - 1):
            x0, x1, y0, y1 = xs[xi] + 70, xs[xi + 1] - 70, ys[yi] + 70, ys[yi + 1] - 70
            for bx in range(2):
                for by in range(2):
                    a0 = x0 + bx * (x1 - x0) / 2 + 8; b0 = y0 + by * (y1 - y0) / 2 + 8
                    a1 = a0 + (x1 - x0) / 2 - 16; b1 = b0 + (y1 - y0) / 2 - 16
                    col = rnd.choice([(196, 120, 96), (150, 150, 190), (214, 190, 130), (130, 170, 190), (190, 110, 140)])
                    g.rectangle([a0 + 14, b0 + 14, a1 + 14, b1 + 14], fill=(0, 0, 0, 70))
                    g.rectangle([a0, b0, a1, b1], fill=col, outline=(40, 30, 40, 255), width=5)
                    g.rectangle([a0 + 20, b0 + 20, a1 - 20, b1 - 20], outline=(255, 255, 255, 90), width=4)
    def road_h(y, w, col=(70, 72, 86), dash=True):
        g.rectangle([0, y - w / 2, W, y + w / 2], fill=col)
        if dash:
            for x in range(-40, W, 120): g.rectangle([x, y - 4, x + 60, y + 4], fill=(250, 240, 200, 220))
    def road_v(x, w, col=(70, 72, 86), dash=True):
        g.rectangle([x - w / 2, 0, x + w / 2, H], fill=col)
        if dash:
            for y in range(-40, H, 120): g.rectangle([x - 4, y, x + 4, y + 60], fill=(250, 240, 200, 220))
    for x in xs[1:-1]: road_v(x, 70)
    for y in ys[1:-1]: road_h(y, 70)
    cols = [(220, 60, 60), (60, 120, 220), (240, 190, 50), (70, 170, 110), (150, 90, 190), (240, 120, 50), (240, 240, 240)]
    def tiny_car(x, y, col, vertical, bright=False, s=1.0):
        w, h = (46 * s, 84 * s) if vertical else (84 * s, 46 * s)
        g.rounded_rectangle([x - w / 2 + 6, y - h / 2 + 8, x + w / 2 + 6, y + h / 2 + 8], 14, fill=(0, 0, 0, 80))
        g.rounded_rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], 14, fill=col, outline=OUT, width=4)
        if vertical: g.rounded_rectangle([x - w / 2 + 8, y - h / 2 + 18, x + w / 2 - 8, y - 4], 8, fill=(150, 200, 240, 255))
        else: g.rounded_rectangle([x + 4, y - h / 2 + 8, x + w / 2 - 14, y + h / 2 - 8], 8, fill=(150, 200, 240, 255))
        if bright: glow(cv, x, y + (h / 2 if vertical else 0) - (0 if vertical else w / 2), 40 * s, (255, 60, 60), 0.9)
    if mode == "skyway":
        g.rectangle([590, 0, 850, H], fill=(86, 88, 104)); g.rectangle([575, 0, 590, H], fill=(210, 210, 216)); g.rectangle([850, 0, 865, H], fill=(210, 210, 216))
        for k in range(3):
            for y in range(-40, H, 130): g.rectangle([590 + (k + 1) * 65 - 4, y, 590 + (k + 1) * 65 + 4, y + 60], fill=(250, 240, 200, 220))
        for lane in range(4):
            for k in range(26): tiny_car(622 + lane * 65, 60 + k * 100 + (t * 6 % 6), cols[(k + lane * 3) % 7], True, True, 0.8)
        for k in range(4): tiny_car(360 + 0, 300 + k * 600, cols[k], True)
    elif mode == "closed":
        for lane in range(4):
            x = [360, 720, 1080][lane % 3]
        for rx in (360, 720, 1080):
            for k in range(7): tiny_car(rx + 12, (k * 360 + t * 190) % (H + 200) - 100, cols[(k + rx // 360) % 7], True)
        for ry in (480, 960, 1440, 1920):
            for k in range(4): tiny_car((k * 480 + t * 170 + ry) % (W + 200) - 100, ry + 12, cols[(k + ry // 480) % 7], False)
    return rnd
