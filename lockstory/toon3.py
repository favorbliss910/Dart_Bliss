"""Highway-story props: cars, cones, stopwatch, pizza, pipes, crane, mic, newspaper."""
import math, random
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont
from toon import Pen, OUT, put, FONT


@lru_cache(maxsize=256)
def car_img(kind="car", color=(220, 60, 60), scale=1.0, d=1):
    p = Pen(560, 300, 280, 250, scale, d)
    w = 460 if kind != "bus" else 640
    if kind == "bus": p = Pen(760, 320, 380, 270, scale, d)
    body = color
    if kind == "amb": body = (250, 250, 252)
    p.poly([(-w / 2, -50), (w / 2, -50), (w / 2 + 10, -120), (w / 2 - 20, -140), (-w / 2 + 10, -140), (-w / 2 - 10, -100)], body, 8)
    if kind == "bus":
        p.poly([(-w / 2 + 10, -140), (w / 2 - 20, -140), (w / 2 - 20, -250), (-w / 2 + 10, -250)], body, 8)
        for k in range(5): p.poly([(-w / 2 + 40 + k * 110, -225), (-w / 2 + 120 + k * 110, -225), (-w / 2 + 120 + k * 110, -160), (-w / 2 + 40 + k * 110, -160)], (170, 220, 250), 4)
    else:
        p.poly([(-120, -140), (-70, -230), (95, -230), (150, -140)], body, 8)
        p.poly([(-98, -148), (-60, -216), (-4, -216), (-4, -148)], (170, 220, 250), 4)
        p.poly([(10, -148), (10, -216), (88, -216), (126, -148)], (170, 220, 250), 4)
    if kind == "amb":
        p.line((-w / 2 + 10, -92), (w / 2 - 10, -92), 22, (220, 40, 50), 0)
        p.poly([(-20, -222), (20, -222), (20, -262), (-20, -262)], (230, 50, 60), 4)
        p.line((-4, -118), (-4, -70), 14, (220, 40, 50), 0); p.line((-26, -94), (18, -94), 14, (220, 40, 50), 0)
    for wx in (-w / 2 + 90, w / 2 - 90):
        p.ell(wx, -44, 48, 48, (40, 40, 52), 0, 7); p.ell(wx, -44, 20, 20, (190, 190, 200), 0, 3)
    p.ell(w / 2 - 6, -96, 14, 14, (255, 240, 160), 0, 4)
    return p.done()


def car(cv, x, y, kind="car", color=(220, 60, 60), sc=1.0, d=1): put(cv, car_img(kind, color, sc, d), x, y)


def honk(cv, x, y, t, d=1):
    g = ImageDraw.Draw(cv)
    for k in range(3):
        a = math.radians(-35 + k * 35)
        g.line([(x + d * 40 * math.cos(a), y + 40 * math.sin(a)), (x + d * 90 * math.cos(a), y + 90 * math.sin(a))], fill=(255, 220, 60, 255 if int(t * 8) % 2 else 120), width=10)


def cone(cv, x, y, sc=1.0):
    p = Pen(200, 260, 100, 250, sc)
    p.poly([(-70, 0), (70, 0), (70, -16), (-70, -16)], (40, 40, 50), 6)
    p.poly([(-50, -16), (50, -16), (14, -200), (-14, -200)], (250, 120, 30), 8)
    p.poly([(-34, -90), (34, -90), (28, -116), (-28, -116)], (255, 255, 255), 4)
    put(cv, p.done(), x, y)


def stopwatch(cv, x, y, sc=1.0, ang=0.0):
    p = Pen(320, 360, 160, 200, sc)
    p.poly([(-16, -150), (16, -150), (16, -126), (-16, -126)], (90, 90, 100), 6)
    p.ell(0, 0, 130, 130, (240, 240, 244), 0, 10)
    p.ell(0, 0, 100, 100, (255, 255, 255), 0, 4)
    for k in range(12):
        a = k * math.pi / 6; p.line((math.sin(a) * 84, -math.cos(a) * 84), (math.sin(a) * 96, -math.cos(a) * 96), 6, OUT, 0)
    p.line((0, 0), (math.sin(math.radians(ang)) * 80, -math.cos(math.radians(ang)) * 80), 8, (220, 50, 60), 0)
    p.ell(0, 0, 10, 10, OUT, 0, 0)
    put(cv, p.done(), x, y)


def pizza(cv, x, y, sc=1.0, cold=False):
    p = Pen(420, 300, 210, 160, sc)
    p.poly([(-150, -20), (150, -20), (170, 80), (-170, 80)], (200, 150, 90), 7)
    p.poly([(-150, -20), (150, -20), (110, -80), (-110, -80)], (220, 170, 110), 7)
    p.ell(0, 20, 80, 36, (240, 190, 70), 0, 5)
    for sx, sy in ((-30, 18), (20, 12), (46, 28)): p.ell(sx, sy, 12, 9, (200, 50, 40), 0, 0)
    put(cv, p.done(), x, y)
    if cold:
        g = ImageDraw.Draw(cv)
        for k in range(5):
            a = k * 1.25; g.line([(x + math.cos(a) * 14 + k * 30 - 70, y - 160), (x + math.cos(a) * 14 + k * 30 - 70, y - 120)], fill=(150, 200, 255, 255), width=8)


def newspaper(cv, x, y, headline, sc=1.0, rot=0, sub=""):
    W, H = int(900 * sc), int(700 * sc)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(im)
    g.rectangle([8, 8, W - 8, H - 8], fill=(252, 250, 240), outline=OUT, width=10)
    f = ImageFont.truetype(FONT, int(74 * sc)); g.text((40 * sc, 30 * sc), "DAILY NEWS", font=f, fill=OUT)
    g.line([(30 * sc, 130 * sc), (W - 30 * sc, 130 * sc)], fill=OUT, width=6)
    f2 = ImageFont.truetype(FONT, int(58 * sc)); g.text((40 * sc, 160 * sc), headline, font=f2, fill=(180, 30, 40))
    for k in range(6): g.line([(40 * sc, (380 + k * 40) * sc), ((W / sc - 360 if k % 2 else W / sc - 200) * sc, (380 + k * 40) * sc)], fill=(150, 150, 160), width=8)
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    return im, (im.width / 2, im.height / 2)


def mic(cv, x, y, sc=1.0):
    p = Pen(200, 420, 100, 400, sc)
    p.poly([(-40, 0), (40, 0), (24, -30), (-24, -30)], (70, 70, 80), 6)
    p.line((0, -30), (0, -300), 14, (110, 110, 120), 5)
    p.ell(0, -330, 40, 52, (60, 60, 70), 0, 6)
    put(cv, p.done(), x, y)


def coffee_machine(cv, x, y, sc=1.0, broken=True):
    p = Pen(420, 560, 210, 540, sc)
    p.poly([(-130, 0), (130, 0), (130, -440), (-130, -440)], (130, 130, 144), 8)
    p.poly([(-90, -300), (90, -300), (90, -420), (-90, -420)], (60, 60, 72), 6)
    p.poly([(-60, -200), (60, -200), (60, -100), (-60, -100)], (40, 40, 52), 6)
    put(cv, p.done(), x, y)
    if broken:
        g = ImageDraw.Draw(cv)
        g.rectangle([x - 90, y - 330 * sc, x + 90, y - 300 * sc], fill=(255, 255, 255), outline=OUT, width=4)


def crane(cv, x, y, sc=1.0, swing=0.0):
    p = Pen(800, 1100, 400, 1080, sc)
    p.poly([(-40, 0), (40, 0), (40, -900), (-40, -900)], (250, 190, 40), 8)
    p.line((-300 + swing * 30, -880), (340 + swing * 30, -880), 26, (250, 190, 40), 8)
    p.line((300 + swing * 30, -880), (300 + swing * 30, -600), 6, OUT, 0)
    p.poly([(270 + swing * 30, -600), (330 + swing * 30, -600), (330 + swing * 30, -560), (270 + swing * 30, -560)], (180, 180, 190), 5)
    put(cv, p.done(), x, y)


def water_jet(cv, x, y, t, h=900, n=70):
    rnd = random.Random(1); g = ImageDraw.Draw(cv)
    for i in range(n):
        ph = (t * 1.2 + i / n) % 1.0
        a = rnd.uniform(-0.5, 0.5)
        px = x + a * 600 * ph; py = y - h * math.sin(math.pi * ph * 0.9) * (1 - abs(a))
        r = 18 + 10 * (1 - ph)
        g.ellipse([px - r, py - r, px + r, py + r], fill=(120, 190, 250, 230), outline=(240, 250, 255, 255), width=3)
