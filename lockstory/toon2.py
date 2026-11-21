"""Extra props for the magpie/cuckoo story (nest, eggs, ladder, notebook, fox, snake...)."""
import math, random
from PIL import Image
from toon import Pen, OUT, put

EGG = (248, 238, 214); SPK = (150, 100, 70)


def _egg(p, x, y, r, col=EGG, spk=SPK, rot=0, seed=0, glow=False):
    rnd = random.Random(seed)
    if glow: p.ell(x, y, r * 1.9, r * 1.9, (255, 244, 170), 0, 0)
    p.ell(x, y, r * 0.78, r, col, rot, 5)
    for _ in range(8):
        a = rnd.uniform(0, 6.28); d = rnd.uniform(0, r * 0.55)
        p.ell(x + math.cos(a) * d * 0.7, y + math.sin(a) * d, 4, 4, spk, 0, 0, 8)


def nest(state="ok", eggs=3, extra=False, scale=1.0, shake=0.0, glow_extra=False, chicks=0):
    """state: ok | smashed | empty | torn"""
    p = Pen(600, 420, 300, 300, scale)
    twig = (120, 82, 50)
    if state == "torn":
        rnd = random.Random(3)
        for i in range(16):
            a = rnd.uniform(0, 6.28); r = rnd.uniform(80, 250)
            p.line((math.cos(a) * 40, math.sin(a) * 20), (math.cos(a) * r, math.sin(a) * r * 0.6 + 30), 11, twig, 4)
        return p.done()
    for i in range(22):                                     # bowl of twigs
        a = i / 22 * 2 * math.pi
        p.line((math.cos(a) * 150 + shake, 40 + math.sin(a) * 40), (math.cos(a + 0.7) * 215 + shake, 70 + math.sin(a + 0.7) * 70), 12, twig, 4)
    p.ell(shake, 70, 190, 70, (150, 104, 66), 0, 7)
    if state == "ok":
        for k in range(eggs):
            _egg(p, -90 + k * 90 + shake, 30 + (k % 2) * 10, 44, seed=k)
        if extra: _egg(p, 0 + shake, -20, 44, col=(222, 238, 226), spk=(70, 110, 90), seed=9, glow=glow_extra)
        for k in range(chicks):
            p.ell(-60 + k * 120, 0, 52, 46, (250, 210, 120), 0, 6)
            p.ell(-60 + k * 120 + 20, -8, 8, 8, OUT, 0, 0)
            p.poly([(-60 + k * 120 + 44, 0), (-60 + k * 120 + 80, 8), (-60 + k * 120 + 44, 18)], (240, 150, 60), 4)
    elif state == "smashed":
        p.ell(0, 56, 160, 36, (255, 200, 60), 0, 0)
        for k in range(5):
            p.poly([(-110 + k * 56, 20), (-80 + k * 56, 2), (-62 + k * 56, 34)], EGG, 5)
    return p.done()


def ladder(h=900, scale=1.0):
    p = Pen(260, h + 40, 130, h + 20, scale)
    for sx in (-70, 70): p.line((sx, 0), (sx - 14 * (sx > 0) + 7, -h), 26, (190, 140, 80), 6)
    for k in range(1, 9): p.line((-64, -k * h / 9), (64, -k * h / 9), 18, (170, 120, 66), 5)
    return p.done()


def notebook(scale=1.0, open_=True):
    p = Pen(420, 300, 210, 160, scale)
    p.poly([(-170, -90), (170, -90), (170, 90), (-170, 90)], (60, 90, 150), 7)
    p.poly([(-150, -74), (-6, -80), (-6, 76), (-150, 80)], (252, 250, 240), 4)
    p.poly([(6, -80), (150, -74), (150, 80), (6, 76)], (252, 250, 240), 4)
    for k in range(5):
        p.line((-134, -50 + k * 28), (-24, -52 + k * 28), 6, (90, 90, 140), 0)
        p.line((24, -52 + k * 28), (134, -50 + k * 28), 6, (90, 90, 140), 0)
    return p.done()


def flask(scale=1.0):
    p = Pen(200, 340, 100, 320, scale)
    p.poly([(-60, 0), (60, 0), (60, -230), (-60, -230)], (200, 60, 50), 7)
    p.poly([(-50, -230), (50, -230), (50, -270), (-50, -270)], (90, 90, 100), 6)
    p.line((-30, -160), (30, -160), 10, (255, 255, 255), 0)
    return p.done()


def fox(d=1, scale=1.0, shrug=0.0):
    p = Pen(700, 560, 350, 520, scale, d)
    O = (226, 120, 50)
    p.curve([(-120, -150), (-260, -100), (-330, -30)], 60, O, 7)
    p.ell(-330, -30, 30, 30, (250, 250, 250), 0, 5)
    for sx in (-60, 60): p.line((sx, -150), (sx + 6, -20), 36, (150, 70, 36), 6)
    p.ell(0, -200, 150, 90, O, 0, 7)
    p.ell(60, -190, 70, 50, (250, 240, 220), 0, 0)
    p.ell(150, -320, 80, 74, O, 0, 7)
    p.poly([(150, -330), (190, -300), (330, -270), (190, -250)], O, 7)
    p.ell(330, -270, 16, 14, OUT, 0, 0)
    p.poly([(100, -380), (130, -470), (170, -390)], O, 6); p.poly([(170, -380), (210, -460), (230, -370)], O, 6)
    p.ell(170, -330, 20, 20, (255, 255, 255), 0, 4); p.ell(176, -330, 9, 9, OUT, 0, 0)
    p.line((120, -362), (210, -348 - shrug * 0), 8, OUT, 0)
    return p.done()


def snake(scale=1.0, t=0.0):
    p = Pen(700, 300, 350, 150, scale)
    pts = [(-300 + i * 40, math.sin(i * 0.8 + t * 5) * 50) for i in range(16)]
    p.curve(pts, 46, (110, 170, 70), 7)
    for i in range(0, 15, 2): p.ell(pts[i][0], pts[i][1], 14, 14, (240, 210, 70), 0, 0)
    hx, hy = pts[-1]
    p.ell(hx + 20, hy, 52, 40, (120, 184, 78), 0, 7); p.ell(hx + 30, hy - 10, 11, 11, (255, 255, 255), 0, 4); p.ell(hx + 33, hy - 10, 5, 5, OUT, 0, 0)
    p.line((hx + 70, hy + 8), (hx + 120, hy + 8), 5, (230, 40, 60), 0)
    return p.done()


def badge(scale=1.0):
    p = Pen(260, 260, 130, 130, scale)
    pts = [(math.cos(i * math.pi / 5 - math.pi / 2) * (110 if i % 2 == 0 else 50), math.sin(i * math.pi / 5 - math.pi / 2) * (110 if i % 2 == 0 else 50)) for i in range(10)]
    p.poly(pts, (240, 200, 70), 8)
    p.ell(0, 0, 30, 30, (200, 150, 40), 0, 4)
    return p.done()


def magnifier(scale=1.0):
    p = Pen(420, 420, 210, 210, scale)
    p.line((60, 60), (170, 170), 34, (110, 70, 40), 7)
    p.ell(-30, -30, 120, 120, (220, 240, 255), 0, 12)
    return p.done()


def footprints(cv_size=None):
    pass
