"""City backgrounds (procedural PLACEHOLDERS) for the highway/Braess story."""
import math, random
from PIL import Image, ImageDraw, ImageFilter

DW, DH = 1440, 2560
BW, BH = int(DW * 1.14), int(DH * 1.14)
_c = {}


def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vg(g, y0, y1, c0, c1):
    for y in range(int(y0), int(y1)): g.line([(0, y), (BW, y)], fill=lerp(c0, c1, (y - y0) / max(1, y1 - y0)))


def vig(im, s=120):
    v = Image.new("L", im.size, 0)
    ImageDraw.Draw(v).ellipse([-im.width * 0.25, -im.height * 0.08, im.width * 1.25, im.height * 1.08], fill=255)
    v = v.filter(ImageFilter.GaussianBlur(280))
    return Image.composite(im, Image.new("RGB", im.size, (14, 12, 20)), v.point(lambda p: s + p * (255 - s) // 255))


def skyline(g, horizon, cols, seed, win=(255, 230, 150), n=14, lit=0.4):
    rnd = random.Random(seed)
    for layer, col in enumerate(cols):
        x = -40
        while x < BW:
            w = rnd.randint(110, 230); h = rnd.randint(300, 760) - layer * 60
            top = horizon - h
            g.rectangle([x, top, x + w, horizon + 40], fill=col)
            for wy in range(int(top) + 30, horizon - 20, 56):
                for wx in range(x + 18, x + w - 24, 44):
                    if rnd.random() < lit: g.rectangle([wx, wy, wx + 20, wy + 28], fill=win)
            x += w + rnd.randint(-10, 30)


def road(g, y0, y1, lanes=3, line=(250, 240, 200), asphalt=(70, 72, 84)):
    g.rectangle([0, y0, BW, y1], fill=asphalt)
    for i in range(1, lanes):
        y = y0 + (y1 - y0) * i / lanes
        for x in range(-40, BW, 150): g.rectangle([x, y - 6, x + 80, y + 6], fill=line)
    g.rectangle([0, y0 - 14, BW, y0], fill=(150, 150, 160)); g.rectangle([0, y1, BW, y1 + 14], fill=(150, 150, 160))


def make(name):
    rnd = random.Random(hash(name) % 1000)
    im = Image.new("RGB", (BW, BH)); g = ImageDraw.Draw(im)
    if name == "c_city":
        vg(g, 0, 1500, (120, 180, 235), (255, 232, 190)); skyline(g, 1450, [(150, 170, 200), (110, 130, 170), (80, 96, 140)], 1)
        g.rectangle([0, 1450, BW, BH], fill=(120, 124, 134)); road(g, 1900, 2500, 3)
        g.rectangle([0, 1480, BW, 1900], fill=(172, 176, 184))
    elif name == "c_hwy":
        vg(g, 0, 1500, (120, 180, 235), (255, 232, 190)); skyline(g, 1250, [(150, 170, 200), (110, 130, 170)], 2)
        g.rectangle([0, 1250, BW, BH], fill=(96, 100, 112))
        g.rectangle([0, 1560, BW, 1700], fill=(150, 150, 160)); road(g, 1700, 2300, 4)
        g.rectangle([0, 1520, BW, 1565], fill=(190, 190, 196))
    elif name == "c_hall":
        vg(g, 0, BH, (116, 82, 56), (84, 56, 40))
        g.rectangle([0, 1500, BW, BH], fill=(96, 64, 44))
        for k in range(8): g.rectangle([k * 190, 500, k * 190 + 100, 1500], fill=(130, 94, 66))
        g.ellipse([480, 700, 960, 1180], fill=(214, 176, 80), outline=(70, 50, 30), width=14)
        g.rectangle([0, 1620, BW, 1760], fill=(70, 46, 32))
        for fx in (150, 1290): g.rectangle([fx - 8, 400, fx + 8, 1500], fill=(190, 190, 190)); g.polygon([(fx + 8, 420), (fx + 230, 480), (fx + 8, 540)], fill=(200, 50, 60))
    elif name == "c_base":
        vg(g, 0, BH, (66, 70, 80), (40, 42, 52))
        for k in range(6): g.rectangle([0, 340 + k * 30, BW, 358 + k * 30], fill=(100, 106, 120)) if k < 2 else None
        g.rectangle([0, 1900, BW, BH], fill=(56, 52, 58))
        for y in (520, 640): g.rectangle([0, y, BW, y + 40], fill=(120, 126, 140), outline=(30, 30, 40), width=4)
        g.rectangle([80, 900, 360, 1900], fill=(86, 88, 100), outline=(30, 30, 40), width=8)
        g.rectangle([1050, 1050, 1390, 1900], fill=(100, 70, 50), outline=(30, 30, 40), width=8)
    elif name == "c_bridge":
        vg(g, 0, 1300, (120, 180, 235), (255, 232, 190)); skyline(g, 1250, [(150, 170, 200), (110, 130, 170)], 3)
        road(g, 1500, 2200, 4); g.rectangle([0, 1250, BW, 1500], fill=(116, 120, 130))
        g.rectangle([0, 2200, BW, BH], fill=(150, 150, 158)); g.rectangle([0, 2300, BW, 2380], fill=(90, 90, 100))
    elif name == "c_alley":
        vg(g, 0, 1500, (130, 186, 235), (255, 236, 200))
        for k in range(6):
            x = k * 270; col = rnd.choice([(230, 190, 150), (200, 150, 120), (170, 200, 180), (230, 210, 150)])
            g.rectangle([x, 1100, x + 250, 1900], fill=col, outline=(70, 50, 40), width=8)
            g.polygon([(x - 10, 1100), (x + 125, 940), (x + 260, 1100)], fill=(176, 80, 66), outline=(70, 50, 40))
            g.rectangle([x + 90, 1500, x + 160, 1900], fill=(110, 80, 60)); g.rectangle([x + 30, 1250, x + 90, 1340], fill=(255, 236, 160))
        road(g, 1950, 2400, 2, asphalt=(100, 100, 108))
    elif name == "c_dusk":
        vg(g, 0, 1500, (70, 50, 120), (255, 150, 90)); skyline(g, 1450, [(120, 90, 130), (86, 64, 110), (60, 44, 90)], 4, lit=0.6)
        g.rectangle([0, 1450, BW, BH], fill=(80, 70, 90)); road(g, 1900, 2500, 3, asphalt=(54, 54, 68))
    else:
        raise KeyError(name)
    im = im.filter(ImageFilter.GaussianBlur(4))
    return vig(im).convert("RGBA")


def get(name):
    if name not in _c: _c[name] = make(name)
    return _c[name]
