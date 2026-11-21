"""Procedural PLACEHOLDER backgrounds (swap for Pinterest photos: same 9:16 slot)."""
import math, random
from PIL import Image, ImageDraw, ImageFilter

DW, DH = 1440, 2560
BW, BH = int(DW * 1.14), int(DH * 1.14)
_cache = {}


def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(g, y0, y1, c0, c1, w=BW):
    for y in range(int(y0), int(y1)):
        g.line([(0, y), (w, y)], fill=lerp(c0, c1, (y - y0) / max(1, y1 - y0)))


def vignette(im, strength=110):
    v = Image.new("L", im.size, 0)
    ImageDraw.Draw(v).ellipse([-im.width * 0.25, -im.height * 0.08, im.width * 1.25, im.height * 1.08], fill=255)
    v = v.filter(ImageFilter.GaussianBlur(280))
    dark = Image.new("RGB", im.size, (20, 12, 14))
    return Image.composite(im, dark, v.point(lambda p: strength + p * (255 - strength) // 255))


def desert(name, horizon, sky, sand, sun=None, tree=False, holes=False, blur=4, seed=1, rocks=False, haze=0.0):
    key = name
    if key in _cache: return _cache[key]
    rnd = random.Random(seed)
    im = Image.new("RGB", (BW, BH))
    g = ImageDraw.Draw(im)
    vgrad(g, 0, horizon, sky[0], sky[1])
    if sun:
        sx, sy, sr = sun
        glow = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
        gg = ImageDraw.Draw(glow)
        for k in range(8):
            r = sr * (3.2 - k * 0.3)
            gg.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 236, 190, 22))
        gg.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 250, 225, 255))
        im = Image.alpha_composite(im.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(10))).convert("RGB")
        g = ImageDraw.Draw(im)
    for k in range(4):                                     # far dunes
        col = lerp(sand[0], sky[1], 0.55 - k * 0.14)
        base = horizon - 70 + k * 46
        ph = rnd.uniform(0, 6)
        pts = [(0, BH)] + [(x, base + 38 * math.sin(x / 260 + ph + k) + 22 * math.sin(x / 90 + k * 2)) for x in range(0, BW + 40, 40)] + [(BW, BH)]
        g.polygon(pts, fill=col)
    vgrad(g, horizon + 90, BH, lerp(sand[0], sand[1], 0.1), sand[1])
    for _ in range(700):                                   # sand ripples
        x = rnd.randint(0, BW); y = rnd.randint(horizon + 110, BH)
        l = 20 + (y - horizon) * 0.14
        g.line([(x, y), (x + l, y + rnd.randint(-4, 4))], fill=lerp(sand[1], (255, 240, 200), 0.18) if rnd.random() < 0.5 else lerp(sand[1], (60, 30, 10), 0.14), width=3 + (y - horizon) // 260)
    if tree:
        tx = int(BW * 0.78)
        g.polygon([(tx - 32, BH * 0.62), (tx + 32, BH * 0.62), (tx + 14, horizon - 40), (tx - 14, horizon - 20)], fill=(70, 48, 36))
        for k in range(14):
            cx = tx + rnd.randint(-330, 330); cy = horizon - 330 + rnd.randint(-70, 70) + abs(cx - tx) * 0.12
            g.ellipse([cx - 150, cy - 34, cx + 150, cy + 34], fill=(90, 120, 64))
        g.line([(tx, horizon - 70), (tx - 480, horizon - 150)], fill=(70, 48, 36), width=26)
    if rocks:
        for _ in range(6):
            x = rnd.randint(100, BW - 100); y = rnd.randint(horizon + 300, BH - 200); r = rnd.randint(40, 110)
            g.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], fill=(150, 120, 96), outline=(60, 40, 30), width=5)
    if holes:
        for hx, hy in ((0.2, 0.74), (0.55, 0.80), (0.82, 0.70), (0.38, 0.9), (0.7, 0.93)):
            x, y = int(BW * hx), int(BH * hy)
            g.ellipse([x - 150, y - 36, x + 150, y + 36], fill=lerp(sand[1], (60, 30, 10), 0.45))
            g.ellipse([x - 124, y - 22, x + 124, y + 32], fill=(40, 22, 20))
    if haze:
        hz = Image.new("RGB", (BW, BH), (255, 230, 190))
        m = Image.new("L", (BW, BH), 0)
        ImageDraw.Draw(m).rectangle([0, horizon - 160, BW, horizon + 120], fill=int(255 * haze))
        im = Image.composite(hz, im, m.filter(ImageFilter.GaussianBlur(60)))
    im = im.filter(ImageFilter.GaussianBlur(blur))
    im = vignette(im).convert("RGBA")
    _cache[key] = im
    return im


def hills(name, horizon, sky, cols, sun=None, trees=True, blur=5, seed=2, bush=False, tree_big=False, dim=1.0):
    if name in _cache: return _cache[name]
    rnd = random.Random(seed)
    im = Image.new("RGB", (BW, BH)); g = ImageDraw.Draw(im)
    vgrad(g, 0, horizon + 80, sky[0], sky[1])
    if sun:
        sx, sy, sr = sun
        glow = Image.new("RGBA", (BW, BH), (0, 0, 0, 0)); gg = ImageDraw.Draw(glow)
        for k in range(8):
            r = sr * (3.0 - k * 0.3); gg.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 236, 190, 22))
        gg.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 250, 225, 255))
        im = Image.alpha_composite(im.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(10))).convert("RGB"); g = ImageDraw.Draw(im)
    for k, col in enumerate(cols):
        base = horizon - 140 + k * 150; ph = rnd.uniform(0, 6)
        pts = [(0, BH)] + [(x, base + 70 * math.sin(x / 330 + ph + k) + 30 * math.sin(x / 110 + k)) for x in range(0, BW + 40, 40)] + [(BW, BH)]
        g.polygon(pts, fill=col)
        if trees:
            for _ in range(7 - k):
                x = rnd.randint(40, BW - 40); y = base + 70 * math.sin(x / 330 + ph + k) + 60 + k * 30
                r = 46 + k * 22
                g.rectangle([x - 6, y - r * 0.4, x + 6, y + 8], fill=(80, 56, 40))
                g.ellipse([x - r, y - r * 1.3, x + r, y - r * 0.1], fill=(96 + k * 8, 120 + k * 6, 70))
    vgrad(g, int(BH * 0.78), BH, cols[-1], tuple(int(c * 0.78) for c in cols[-1]))
    if tree_big:
        tx = int(BW * 0.5)
        g.polygon([(tx - 120, BH), (tx + 120, BH), (tx + 60, 900), (tx - 60, 900)], fill=(86, 60, 42))
        for sgn, y in ((-1, 1250), (1, 1050), (-1, 880), (1, 1500)):
            g.line([(tx, y), (tx + sgn * 520, y - 70)], fill=(86, 60, 42), width=54)
        for _ in range(26):
            x = tx + rnd.randint(-620, 620); y = rnd.randint(300, 1500)
            g.ellipse([x - 120, y - 70, x + 120, y + 70], fill=(80 + rnd.randint(0, 30), 120 + rnd.randint(0, 30), 66))
    if bush:
        for _ in range(26):
            x = rnd.randint(-100, BW); y = rnd.randint(int(BH * 0.55), BH)
            r = rnd.randint(120, 260)
            g.ellipse([x - r, y - r, x + r, y + r * 0.8], fill=(54 + rnd.randint(0, 30), 100 + rnd.randint(0, 40), 56))
    im = im.filter(ImageFilter.GaussianBlur(blur))
    if dim != 1.0: im = Image.eval(im, lambda v: int(v * dim))
    im = vignette(im).convert("RGBA"); _cache[name] = im
    return im


def indoor(name):
    if name in _cache: return _cache[name]
    rnd = random.Random(4)
    im = Image.new("RGB", (BW, BH), (214, 196, 160)); g = ImageDraw.Draw(im)
    vgrad(g, 0, BH, (226, 208, 172), (188, 166, 128))
    g.rectangle([0, int(BH * 0.66), BW, BH], fill=(120, 90, 66))
    for i in range(10): g.line([(0, int(BH * 0.66) + i * 90), (BW, int(BH * 0.66) + i * 90)], fill=(96, 70, 50), width=5)
    g.rounded_rectangle([140, 380, 560, 880], 14, fill=(255, 238, 190), outline=(70, 50, 40), width=14)       # window
    g.line([(350, 380), (350, 880)], fill=(70, 50, 40), width=10); g.line([(140, 630), (560, 630)], fill=(70, 50, 40), width=10)
    g.rectangle([BW * 0.52, 400, BW * 0.95, 900], fill=(170, 130, 90), outline=(70, 50, 40), width=12)          # cork board
    for _ in range(14):
        x = rnd.randint(int(BW * 0.55), int(BW * 0.92)); y = rnd.randint(430, 850)
        g.rectangle([x, y, x + 90, y + 60], fill=(250, 250, 244), outline=(80, 80, 90), width=3); g.ellipse([x + 40, y - 6, x + 52, y + 6], fill=(220, 50, 50))
    g.rectangle([0, int(BH * 0.60), BW, int(BH * 0.66)], fill=(150, 108, 72), outline=(70, 50, 40), width=6)    # desk edge
    im = im.filter(ImageFilter.GaussianBlur(5)); im = vignette(im, 130).convert("RGBA"); _cache[name] = im
    return im


def get(name):
    if name in _cache: return _cache[name]
    if name.startswith("c_"):
        import bgs2
        _cache[name] = bgs2.get(name); return _cache[name]
    if name == "wide":
        return desert(name, 1250, ((90, 160, 230), (255, 224, 170)), ((236, 200, 140), (214, 168, 100)),
                      sun=(BW * 0.28, 520, 90), tree=True, holes=True, rocks=True, seed=3)
    if name == "close":
        return desert(name, 900, ((110, 170, 235), (252, 226, 180)), ((240, 206, 150), (206, 156, 92)),
                      sun=None, holes=True, rocks=True, seed=5, blur=6)
    if name == "sky":
        return desert(name, 2000, ((60, 130, 225), (200, 225, 245)), ((230, 190, 130), (200, 150, 90)),
                      sun=(BW * 0.7, 640, 110), seed=7, blur=3)
    if name == "morning":
        return desert(name, 1300, ((250, 170, 140), (255, 226, 170)), ((236, 190, 130), (206, 150, 96)),
                      sun=(BW * 0.5, 1180, 130), tree=True, seed=9, haze=0.5)
    if name == "dusk":
        return desert(name, 1350, ((70, 50, 120), (255, 150, 90)), ((190, 130, 90), (130, 84, 70)),
                      sun=(BW * 0.5, 1260, 150), tree=True, seed=11, haze=0.35)
    if name == "branch":
        im = desert("branch_base", 1500, ((120, 180, 235), (255, 226, 180)), ((236, 200, 140), (214, 168, 100)),
                    sun=(BW * 0.7, 700, 90), seed=13, blur=14).copy()
        g = ImageDraw.Draw(im)
        g.line([(-50, 1560), (BW + 50, 1500)], fill=(86, 58, 40), width=70)
        g.line([(-50, 1535), (BW + 50, 1478)], fill=(120, 84, 58), width=18)
        for k in range(9):
            x = 120 + k * 170; y = 1500 - 40 + (k % 3) * 20
            g.ellipse([x - 70, y - 160, x + 70, y - 90], fill=(86, 128, 70))
        _cache[name] = im
        return im
    if name == "burrow":
        im = Image.new("RGB", (BW, BH))
        g = ImageDraw.Draw(im)
        vgrad(g, 0, 700, (120, 180, 235), (255, 226, 180))
        g.rectangle([0, 700, BW, BH], fill=(120, 80, 56))
        vgrad(g, 700, BH, (170, 120, 80), (84, 52, 40))
        rnd = random.Random(2)
        for _ in range(500):
            x = rnd.randint(0, BW); y = rnd.randint(720, BH); r = rnd.randint(4, 16)
            g.ellipse([x - r, y - r, x + r, y + r], fill=(rnd.randint(70, 150),) * 1 + (rnd.randint(50, 100), rnd.randint(36, 70)))
        g.rectangle([0, 700, BW, 760], fill=(236, 200, 140))
        for tx0, ty0, tx1, ty1 in ((300, 760, 300, 1500), (300, 1500, 1100, 1500), (1100, 1500, 1100, 760), (700, 1500, 700, 1900)):
            g.line([(tx0, ty0), (tx1, ty1)], fill=(36, 22, 22), width=190)
        im = vignette(im.filter(ImageFilter.GaussianBlur(3))).convert("RGBA")
        _cache[name] = im
        return im
    if name == "paper":
        im = Image.new("RGB", (BW, BH), (250, 240, 214))
        g = ImageDraw.Draw(im)
        for x in range(0, BW, 70):
            for y in range(0, BH, 70): g.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(226, 208, 170))
        im = im.convert("RGBA"); _cache[name] = im
        return im
    if name == "valley":
        return hills(name, 1200, ((110, 170, 235), (255, 232, 178)), ((200, 176, 110), (176, 150, 84), (150, 126, 64)), sun=(BW * 0.25, 520, 90), seed=21)
    if name == "dawn":
        return hills(name, 1250, ((255, 150, 120), (255, 222, 160)), ((190, 140, 100), (160, 116, 80), (130, 96, 64)), sun=(BW * 0.5, 1180, 140), seed=22)
    if name == "tree":
        return hills(name, 1250, ((120, 180, 235), (255, 232, 178)), ((200, 176, 110), (176, 150, 84), (150, 126, 64)), trees=False, tree_big=True, seed=23, blur=7)
    if name == "bush":
        return hills(name, 1200, ((110, 170, 235), (255, 232, 178)), ((200, 176, 110), (176, 150, 84), (150, 126, 64)), bush=True, seed=24, blur=6)
    if name == "gloom":
        return hills(name, 1250, ((90, 70, 110), (230, 150, 110)), ((150, 110, 90), (120, 86, 70), (96, 66, 56)), sun=(BW * 0.7, 1150, 120), tree_big=True, trees=False, seed=25, blur=7, dim=0.85)
    if name == "office":
        return indoor(name)
    raise KeyError(name)


def crop(name, dx=0, dy=0, zoom=1.0):
    """Return DWxDH view into the background with optional pan/zoom (px of slack)."""
    im = get(name)
    cw, ch = DW / zoom, DH / zoom
    cx = BW / 2 + dx; cy = BH / 2 + dy
    cx = min(max(cx, cw / 2), BW - cw / 2); cy = min(max(cy, ch / 2), BH - ch / 2)
    return im.resize((DW, DH), Image.BILINEAR, box=(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2))
