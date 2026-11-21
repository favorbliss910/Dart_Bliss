"""Highway / Braess story, v2: first-person cockpit, perspective canyon, aerial city,
giant foreground props, depth-of-field, glow. Same transcript + timing as story_highway."""
import math, random
from PIL import Image, ImageDraw
import story as base
from story import ss, mix, pop_scale, clean
from toon import *
from toon3 import stopwatch, newspaper, mic, coffee_machine, crane, cone, pizza, water_jet, honk
from toon4 import *
import story_highway as H
from story_highway import SEGS, WORDS, W, E, DURATION, ENG, CN1, CN2, CN3, BOSS, HOST, DRV, COLS, sign, clock
from story_mafia import HM, calm, stamp
import bgs

DW, DH = 1440, 2560
SHOTS = []


def shot(t0, cam=(1.0, 1.1, 0.5, 0.55)):
    def deco(fn): SHOTS.append((t0, fn, cam)); return fn
    return deco


def dim(cv, a, col=(0, 0, 0)):
    cv.alpha_composite(Image.new("RGBA", cv.size, col + (int(a),)))


def layer(cv, fn, blur=0):
    """Draw a background with fn(layer) then optionally defocus it (depth of field)."""
    lay = Image.new("RGBA", cv.size, (0, 0, 0, 255)); fn(lay)
    cv.alpha_composite(soft(lay, blur) if blur else lay)


def BGI(cv, name, blur=0, dx=0):
    layer(cv, lambda l: l.alpha_composite(bgs.crop(name, dx, 0, 1.0)), blur)


def canyon(cv, t, lanes=4, jam=True, speed=0.0, night=False, vp=(720, 1000), n=8, seed=1, h=3.2, kinds=None, z0=2.6, cam_x=0.0, blur=0, brake=True, lane_w=3.8):
    cars = jam_cars(t, lanes, n, seed, z0=z0, kinds=kinds, brake=brake) if jam else []
    layer(cv, lambda l: road_view(l, t, vp=vp, lanes=lanes, speed=speed, cars=cars, night=night, seed=seed, h=h, cam_x=cam_x, lane_w=lane_w), blur)


def flow(t, lanes, n, seed, speed=26.0, kinds=None, brake=False):
    rnd = random.Random(seed); cars = []
    cols = [(220, 60, 60), (60, 120, 220), (240, 190, 50), (70, 170, 110), (150, 90, 190), (240, 120, 50), (90, 200, 220), (240, 240, 240)]
    for l in range(lanes):
        for k in range(n):
            z = (3.0 + k * 9.0 + rnd.uniform(0, 4) - speed * 0.12 * t * (0.8 + 0.1 * l)) % (n * 9.0) + 2.6
            cars.append(dict(lane=l, z=z, color=cols[(k * 3 + l * 5 + seed) % 8], kind=(kinds or {}).get((l, k), "car"), brake=brake))
    return cars


def hero(cv, ch, x, y, sc, d=1, **pose):
    return HM(cv, ch, x, y, sc, d, **pose)


def title(cv, text, y=520, size=120, col=(255, 255, 255)): label(cv, text, 720, y, size, col=col)


def xmark(cv, cx, cy, r, a, col=(230, 40, 50)):
    g = ImageDraw.Draw(cv)
    g.line([(cx - r, cy - r), (cx - r + 2 * r * a, cy - r + 2 * r * a)], fill=col, width=44)
    g.line([(cx + r, cy - r), (cx + r - 2 * r * a, cy - r + 2 * r * a)], fill=col, width=44)


def cup(cv, x, y, sc=1.0, tilt=0):
    p = Pen(420, 420, 210, 300, sc)
    p.poly([(-110, -190), (110, -190), (84, 0), (-84, 0)], (250, 250, 252), 9)
    p.poly([(-96, -150), (96, -150), (92, -190), (-92, -190)], (110, 70, 44), 0)
    p.curve([(110, -150), (180, -130), (170, -60), (96, -40)], 22, (250, 250, 252), 8)
    im, (ox, oy) = p.done()
    im = im.rotate(-tilt, resample=Image.BICUBIC, center=(ox, oy))
    cv.alpha_composite(im, (int(x - ox), int(y - oy)))


def burst(cv, x, y, t, n=22, seed=0, spread=700):
    rnd = random.Random(seed); g = ImageDraw.Draw(cv, "RGBA")
    for i in range(n):
        a = rnd.uniform(0, 6.28); sp = rnd.uniform(0.3, 1.0) * spread * min(1, t * 2.5)
        px, py = x + math.cos(a) * sp, y + math.sin(a) * sp * 0.8
        r = rnd.randint(30, 90) * (1 - min(1, t * 0.9)) + 6
        g.ellipse([px - r, py - r, px + r, py + r], fill=rnd.choice([(255, 210, 60, 235), (255, 120, 40, 235), (255, 245, 200, 235), (90, 80, 90, 200)]))


# ================================================================== SHOTS
@shot(W(0), cam=(1.0, 1.16, 0.4, 0.5, 0.45, 0.45))
def v01(cv, t, u):
    canyon(cv, t, 4, True, 0, n=7, seed=2, blur=14)
    glow(cv, 1020, 1500, 520, (255, 220, 120), 0.8)
    HM(cv, ENG, 520, 2540, 2.1, 1, **calm(t, armF=(100, 130), eyes="dot", mouth="smile", brow=-0.4, tilt=-4))
    stopwatch(cv, 1130, 1700, 1.7, u * 90)


@shot(W(0, "jam"), cam=(1.0, 1.1, 0.5, 0.6, 0.5, 0.55))
def v02(cv, t, u):
    canyon(cv, t, 3, True, 0, n=7, seed=3, z0=2.5)
    cockpit(cv, t, steer=3 * math.sin(t * 4), honk=int(t * 4) % 2 == 0, mirror="eyes")
    for k in range(5): glow(cv, 300 + k * 210, 1200 + 40 * (k % 2), 70, (255, 60, 60), 0.5)
    sign(cv, "WORST JAM EVER", 720, 520, 110, col=(255, 120, 100))


@shot(W(0, "delete"), cam=(1.0, 1.12, 0.5, 0.5, 0.5, 0.45))
def v03(cv, t, u):
    layer(cv, lambda l: aerial(l, t, "skyway"), 0)
    dim(cv, 60); g = ImageDraw.Draw(cv, "RGBA")
    sign(cv, "THE SKYWAY", 720, 560, 140, col=(70, 170, 110), tcol=(255, 255, 255))
    xmark(cv, 720, 1300, 520, ss((u - 0.3) / 0.5))
    label(cv, "DELETE IT.", 720, 2060, 150) if u > 1.0 else None


@shot(W(1), cam=(1.0, 1.12, 0.5, 0.5, 0.5, 0.4))
def v04(cv, t, u):
    layer(cv, lambda l: aerial(l, t, "plain"), 0)
    g = ImageDraw.Draw(cv, "RGBA"); rise = ss(u / 1.8)
    g.rectangle([590, 0, 850, DH * rise], fill=(86, 88, 104)); g.rectangle([575, 0, 590, DH * rise], fill=(210, 210, 216)); g.rectangle([850, 0, 865, DH * rise], fill=(210, 210, 216))
    for y in range(-40, int(DH * rise), 130):
        for k in range(1, 4): g.rectangle([590 + k * 65 - 4, y, 590 + k * 65 + 4, y + 60], fill=(250, 240, 200, 220))
    glow(cv, 720, DH * rise, 260, (255, 220, 120), 0.8)
    label(cv, "BUILDING THE SKYWAY", 720, 400, 90)


@shot(W(2), cam=(1.0, 1.14, 0.5, 0.55, 0.5, 0.5))
def v05(cv, t, u):
    canyon(cv, t, 6, True, 0, n=6, seed=4, lane_w=3.3, z0=2.8)
    title(cv, "SIX LANES", 440, 190)
    rays(cv, 720, 1000, t, a=26)


@shot(W(2, "shortcut"), cam=(1.0, 1.15, 0.5, 0.6, 0.5, 0.5))
def v06(cv, t, u):
    canyon(cv, t, 4, False, 30, n=6, seed=5)
    cv.alpha_composite(Image.new("RGBA", cv.size, (0, 0, 0, 0)))
    layer(cv, lambda l: road_view(l, t, vp=(720, 1000), lanes=4, speed=30, cars=flow(t, 4, 6, 5, 30)), 0)
    sign(cv, "SHORTCUT!", 720, 560, 180, col=(255, 235, 110))
    for k in range(6): sparkle(cv, 220 + k * 200, 760 + 60 * math.sin(t * 5 + k), 44 + 10 * math.sin(t * 6 + k))
    rays(cv, 720, 1000, t, a=30)


@shot(W(2, "five"), cam=(1.0, 1.1, 0.5, 0.5, 0.5, 0.5))
def v07(cv, t, u):
    BGI(cv, "c_dusk", 16)
    glow(cv, 720, 1300, 900, (255, 200, 120), 0.5)
    sign(cv, "5 MILES", 720, 560, 190, col=(255, 255, 255))
    clock(cv, 720, 1400, 420, u * 540)
    sign(cv, "45 MINUTES", 720, 2180, 160, col=(255, 140, 120)) if u > 1.3 else None


@shot(W(2, "ambulances"), cam=(1.0, 1.12, 0.5, 0.55, 0.5, 0.5))
def v08(cv, t, u):
    cars = jam_cars(t, 3, 6, 6, z0=5.4, kinds={(1, 0): "amb"})
    layer(cv, lambda l: road_view(l, t, vp=(720, 1000), lanes=3, cars=cars + [dict(lane=1, z=3.0, kind="amb", color=(255, 255, 255), brake=True)], seed=6), 0)
    on = int(t * 6) % 2
    glow(cv, 720, 1560, 460, (255, 60, 60) if on else (60, 110, 255), 0.7)
    cockpit(cv, t, steer=2, mirror="eyes")
    rings(cv, 720, 1500, t, d=1, col=(255, 120, 120)); rings(cv, 720, 1500, t + 0.3, d=-1, col=(120, 160, 255))
    label(cv, "WEE-OO WEE-OO", 720, 520, 100)


@shot(W(2, "pizza"), cam=(1.0, 1.12, 0.5, 0.6, 0.5, 0.55))
def v09(cv, t, u):
    canyon(cv, t, 3, True, 0, n=6, seed=7, blur=18)
    cockpit(cv, t, steer=2)
    pizza(cv, 1060, 2020, 2.4, cold=True)
    for k in range(10): sparkle(cv, 760 + (k * 97) % 600, 1500 + 14 * k + 20 * math.sin(t * 3 + k), 26)
    label(cv, "COLD", 720, 620, 220, col=(170, 220, 255))


@shot(W(2, "whole"), cam=(1.0, 1.1, 0.5, 0.55, 0.5, 0.55))
def v10(cv, t, u):
    canyon(cv, t, 3, True, 0, n=4, seed=8, z0=7.0, blur=10)
    car_at(cv, 720, 2320, 1250, "car", (220, 60, 60), True)
    g = ImageDraw.Draw(cv)
    for hx, col in ((560, (238, 196, 160)), (880, (244, 206, 170))):
        g.ellipse([hx - 70, 1780, hx + 70, 1930], fill=col, outline=OUT, width=8)
        g.ellipse([hx - 40, 1830, hx - 18, 1856], fill=(255, 255, 255), outline=OUT, width=4); g.ellipse([hx + 18, 1830, hx + 40, 1856], fill=(255, 255, 255), outline=OUT, width=4)
        g.line([(hx - 30, 1900), (hx + 30, 1896)], fill=OUT, width=6)
    bubble(cv, "YOU NEVER LISTEN!", 520, 1380, 78, tail=(40, 240), scale=pop_scale(u - 0.3))
    bubble(cv, "WE'RE IN THE LEFT LANE!", 920, 1160, 70, tail=(-40, 300), scale=pop_scale(u - 1.2))


@shot(W(3), cam=(1.0, 1.1, 0.5, 0.55))
def v11(cv, t, u):
    BGI(cv, "c_hall", 14)
    glow(cv, 720, 1100, 700, (255, 220, 140), 0.5)
    HM(cv, CN1, 280, 2540, 2.0, 1, **calm(t, armF=(100, 130)))
    HM(cv, ENG, 1120, 2540, 2.0, -1, **calm(t, mouth="smile"))
    sign(cv, "NEW TRAFFIC ENGINEER", 720, 520, 78, col=(255, 255, 255))


@shot(W(3, "sits"), cam=(1.0, 1.15, 0.4, 0.5, 0.5, 0.55))
def v12(cv, t, u):
    cars = flow(t, 4, 7, 9, 22)
    layer(cv, lambda l: road_view(l, t, vp=(720, 700), f=900, h=11.0, lanes=4, speed=22, cars=cars, seed=9), 0)
    g = ImageDraw.Draw(cv); g.rectangle([0, 2060, DW, 2200], fill=(120, 120, 130), outline=OUT, width=10)
    for x in range(40, DW, 160): g.rectangle([x, 2200, x + 30, 2560], fill=(100, 100, 112), outline=OUT, width=6)
    HM(cv, ENG, 520, 2560, 2.3, 1, **calm(t, armF=(70, 100), look=(0.6, 0.5), eyes="dot", mouth="flat", tilt=6))
    stopwatch(cv, 1060, 2100, 1.4, u * 120)


@shot(W(3, "doesn't"), cam=(1.0, 1.12, 0.5, 0.5, 0.5, 0.6))
def v13(cv, t, u):
    layer(cv, lambda l: aerial(l, t, "closed"), 0)
    dim(cv, 90); g = ImageDraw.Draw(cv, "RGBA")
    stopwatch(cv, 720, 1280, 3.2, u * 150)
    label(cv, "THE SIDE STREETS", 720, 500, 120)


@shot(W(3, "weird"), cam=(1.0, 1.12, 0.5, 0.5, 0.5, 0.45))
def v14(cv, t, u):
    BGI(cv, "c_bridge", 22)
    g = ImageDraw.Draw(cv)
    g.rounded_rectangle([100, 520, 1340, 2200], 50, fill=(252, 250, 240), outline=OUT, width=14)
    for k in range(9): g.line([(140, 640 + k * 150), (1300, 640 + k * 150)], fill=(180, 200, 240), width=5)
    label(cv, "EVERY DRIVER", 720, 740, 120, col=(40, 30, 50), stroke=0); label(cv, "TAKES THE SKYWAY", 720, 890, 120, col=(40, 30, 50), stroke=0)
    for k in range(8):
        a = pop_scale(u - 0.4 - k * 0.3)
        if a > 0.1: label(cv, "v", 330 + (k % 4) * 260, 1300 + (k // 4) * 300, int(220 * a), col=(60, 170, 90), stroke=0)


@shot(W(4), cam=(1.0, 1.15, 0.5, 0.6, 0.5, 0.5))
def v15(cv, t, u):
    BGI(cv, "c_hall", 12)
    x = mix(-200, 720, ss(u / 1.4))
    HM(cv, ENG, x, 2540, 2.2, 1, **calm(t, bob=-abs(math.sin(t * 8)) * 8 if u < 1.4 else 0, walk=math.sin(t * 8) * (u < 1.4), armF=(100, 120)))
    g = ImageDraw.Draw(cv); g.rounded_rectangle([760 + x * 0.2, 1650, 1320 + x * 0.2, 1780], 40, fill=(240, 236, 220), outline=OUT, width=10)
    sign(cv, "TEAR IT DOWN", 720, 520, 150, col=(255, 130, 110)) if u > 1.4 else None


@shot(W(5), cam=(1.0, 1.14, 0.5, 0.55, 0.5, 0.6))
def v16(cv, t, u):
    BGI(cv, "c_hall", 16)
    for i, (ch, x) in enumerate(((CN1, 240), (CN2, 720), (CN3, 1200))):
        k = abs(math.sin(t * 13 + i))
        HM(cv, ch, x, 2100, 1.5, 1 if x < 720 else -1, eyes="closed", mouth="open", open=0.4 + 0.6 * k, tilt=-10 + 4 * math.sin(t * 13 + i), bob=-k * 14, armF=(30, 60))
    g = ImageDraw.Draw(cv)
    g.rounded_rectangle([200, 2250, 1240, 2500], 24, fill=(252, 250, 240), outline=OUT, width=10); label(cv, "BUDGET", 720, 2330, 100, col=(40, 30, 50), stroke=0)
    sp = ss((u - 1.0) / 0.8)
    g.ellipse([720 - 380 * sp, 2370 - 70 * sp, 720 + 380 * sp, 2370 + 90 * sp], fill=(100, 62, 40, 255))
    cup(cv, 1040, 2100 - 120 * sp, 1.6, -20 - 80 * sp)


@shot(W(6), cam=(1.0, 1.18, 0.5, 0.5, 0.5, 0.42))
def v17(cv, t, u):
    BGI(cv, "c_hall", 16)
    k = abs(math.sin(t * 12))
    HM(cv, CN1, 560, 2540, 2.4, 1, eyes="squint", mouth="open", open=0.3 + 0.7 * k, brow=-0.6, tilt=-5, armF=(120, 150))
    mic(cv, 1060, 2540, 3.0)
    bubble(cv, "GREAT IDEA!", 720, 520, 150, tail=(-80, 260), scale=pop_scale(u - 0.3))


@shot(W(6, "fix"), cam=(1.0, 1.1, 0.5, 0.5, 0.5, 0.5))
def v18(cv, t, u):
    BGI(cv, "c_city", 18)
    g = ImageDraw.Draw(cv)
    sign(cv, "HUNGRY?", 720, 520, 170, col=(255, 255, 255))
    g.rounded_rectangle([220, 1000, 1220, 1700], 60, fill=(255, 236, 190), outline=OUT, width=14)
    label(cv, "RESTAURANT", 720, 1350, 140, col=(160, 60, 40), stroke=0)
    xmark(cv, 720, 1350, 480, ss((u - 0.8) / 0.5))
    label(cv, "CLOSE THEM ALL", 720, 2000, 110) if u > 1.2 else None


@shot(W(6, "smiles"), cam=(1.0, 1.3, 0.5, 0.45, 0.5, 0.38))
def v19(cv, t, u):
    BGI(cv, "c_hall", 20)
    glow(cv, 720, 1200, 800, (255, 220, 140), 0.5)
    HM(cv, ENG, 720, 2640, 2.4, 1, **calm(t, mouth="smile", eyes="dot", armF=(8, 8)))
    sparkle(cv, 1000, 900, 50 * pop_scale(u - 0.7)) if u > 0.7 else None


@shot(W(7), cam=(1.0, 1.1, 0.5, 0.5, 0.5, 0.45))
def v20(cv, t, u):
    layer(cv, lambda l: aerial(l, t, "closed"), 0)
    dim(cv, 80); g = ImageDraw.Draw(cv, "RGBA")
    a = ss(u / 0.7)
    for x in (360, 1080): g.rectangle([x - 40, 0, x + 40, DH], fill=(120, 170, 100, int(255 * a)))
    label(cv, "FEWER ROADS", 720, 1150, 150)


@shot(W(8), cam=(1.0, 1.12, 0.5, 0.5, 0.5, 0.5))
def v21(cv, t, u):
    BGI(cv, "c_city", 22)
    glow(cv, 720, 1250, 900, (255, 230, 170), 0.5)
    im, (ox, oy) = newspaper(cv, 0, 0, "ROAD ENEMY #1?", 1.55, rot=-8 + 14 * (1 - ss(u / 0.6)) + 40 * max(0, 1 - u * 3))
    cv.alpha_composite(im, (int(720 - ox), int(1280 - oy)))


@shot(W(9), cam=(1.0, 1.16, 0.5, 0.5, 0.5, 0.5))
def v22(cv, t, u):
    BGI(cv, "paper")
    g = ImageDraw.Draw(cv)
    g.rounded_rectangle([100, 520, 1340, 2200], 50, fill=(252, 250, 240), outline=OUT, width=14)
    cx, cy = 720, 1500
    g.ellipse([cx - 330, cy - 330, cx + 330, cy + 330], fill=(244, 206, 170), outline=OUT, width=14)
    g.polygon([(cx - 180, cy - 310), (cx + 180, cy - 310), (cx + 90, cy - 760), (cx - 90, cy - 760)], fill=(250, 120, 30), outline=OUT)
    g.polygon([(cx - 130, cy - 560), (cx + 130, cy - 560), (cx + 110, cy - 640), (cx - 110, cy - 640)], fill=(255, 255, 255))
    for ex in (-130, 130): g.ellipse([cx + ex - 60, cy - 100, cx + ex + 60, cy + 20], fill=(255, 255, 255), outline=OUT, width=8); g.ellipse([cx + ex - 20, cy - 60, cx + ex + 20, cy - 20], fill=OUT)
    g.line([(cx - 120, cy + 150), (cx + 120, cy + 150)], fill=OUT, width=14)
    g.rectangle([cx + 340, cy - 40, cx + 560, cy + 80], fill=(220, 50, 50), outline=OUT, width=10)
    g.line([(cx + 560, cy + 20), (cx + 620, cy - 90)], fill=OUT, width=10)
    glow(cv, cx + 630, cy - 100, 120 + 30 * math.sin(t * 22), (255, 200, 80), 1.0)


@shot(W(9, "radio"), cam=(1.0, 1.16, 0.5, 0.5, 0.5, 0.45))
def v23(cv, t, u):
    BGI(cv, "c_hall", 18)
    k = abs(math.sin(t * 12))
    HM(cv, HOST, 540, 2540, 2.3, 1, eyes="squint", mouth="open", open=0.3 + 0.7 * k, brow=-0.5, armF=(120, 150))
    mic(cv, 1060, 2540, 3.0)
    for i in range(4): rings(cv, 1060, 1500, t + i * 0.2, d=1, col=(255, 230, 120), maxr=700)
    bubble(cv, "THE HIGHWAY HATER!", 720, 520, 100, tail=(-60, 260), scale=pop_scale(u - 0.2))


@shot(W(10), cam=(1.0, 1.18, 0.5, 0.55, 0.5, 0.5))
def v24(cv, t, u):
    canyon(cv, t, 3, False, 0, n=1, seed=10, blur=0)
    layer(cv, lambda l: road_view(l, t, vp=(720, 1000), lanes=3, cars=[], seed=10), 0)
    x = mix(300, 1100, ss(u / 3.0))
    HM(cv, ENG, x, 1640, 0.9, 1, bob=-abs(math.sin(t * 8)) * 4, walk=math.sin(t * 8), armF=(20 * math.sin(t * 8), 10), armB=(-20 * math.sin(t * 8), 10), mouth="flat")
    cockpit(cv, t, honk=int(t * 5) % 2 == 0, mirror="eyes")
    label(cv, "HONK! HONK!", 720, 520, 170) if int(t * 4) % 2 else None
    for k in range(4): honk(cv, 300 + k * 280, 1500, t + k * 0.1)


@shot(W(11), cam=(1.0, 1.3, 0.5, 0.5, 0.5, 0.4))
def v25(cv, t, u):
    BGI(cv, "c_city", 18)
    glow(cv, 720, 1300, 800, (255, 230, 170), 0.4)
    HM(cv, ENG, 720, 2640, 2.3, 1, **calm(t, eyes="squint", mouth="flat", brow=0.4, tilt=-4))
    label(cv, "THE WEIRD PART", 720, 560, 140)
    bubble(cv, "?", 1130, 900, 260, tail=(-100, 180), scale=pop_scale(u - 0.2))


@shot(W(11, "everybody"), cam=(1.0, 1.1, 0.5, 0.5, 0.5, 0.5))
def v26(cv, t, u):
    BGI(cv, "paper")
    bubble(cv, "HE HATES CARS!", 720, 700, 120, tail=(0, 200), scale=pop_scale(u - 0.2))
    car_at(cv, 720, 2000, 1100, "car", (220, 60, 60), True)
    xmark(cv, 720, 1600, 460, ss((u - 1.0) / 0.5))


@shot(W(11, "doesn't"), cam=(1.0, 1.14, 0.5, 0.55, 0.5, 0.5))
def v27(cv, t, u):
    BGI(cv, "c_dusk", 14)
    car_at(cv, 720, 2200, 1150, "car", (60, 120, 220), False)
    HM(cv, ENG, 220, 2540, 1.8, 1, **calm(t, mouth="smile", eyes="dot", armF=(60, 100)))
    for k in range(6): sparkle(cv, 520 + k * 150, 1450 + 80 * math.sin(t * 4 + k) - 40 * k, 40)
    label(cv, "LOVES CARS", 720, 560, 150) if u > 0.5 else None


@shot(W(11, "wants", 1), cam=(1.0, 1.1, 0.5, 0.5, 0.5, 0.5))
def v28(cv, t, u):
    layer(cv, lambda l: aerial(l, t, "closed"), 0)
    dim(cv, 100); g = ImageDraw.Draw(cv, "RGBA")
    f = ss((u - 0.8) / 0.8)
    for x in (360, 720, 1080):
        if x == 720: g.rectangle([x - 36, 0, x + 36, DH], fill=(120, 170, 100, int(255 * f)))
    label(cv, "SAME TRAFFIC.", 720, 560, 140); label(cv, "FEWER ROADS.", 720, 740, 140)


@shot(W(11, "how"), cam=(1.0, 1.25, 0.5, 0.5, 0.5, 0.42))
def v29(cv, t, u):
    BGI(cv, "c_city", 20)
    HM(cv, ENG, 720, 2640, 2.4, 1, **calm(t, eyes="dot", mouth="smile", tilt=3))
    label(cv, "HOW?", 720, 760, int(300 * pop_scale(u - 0.1)) + 1)
    for k in range(5): label(cv, "?", 220 + k * 250, 1100 + 80 * math.sin(t * 3 + k), 150, col=(255, 230, 120))


@shot(W(12), cam=(1.0, 1.15, 0.5, 0.55, 0.5, 0.5))
def v30(cv, t, u):
    lanes = 4 + int(4 * ss(u / 2.0))
    canyon(cv, t, 8 if lanes >= 8 else lanes, False, 24, n=5, seed=11, lane_w=3.0)
    layer(cv, lambda l: road_view(l, t, vp=(720, 1000), lanes=max(4, min(8, lanes)), speed=24, cars=flow(t, max(4, min(8, lanes)), 5, 11, 24), lane_w=3.0, seed=11), 0)
    sign(cv, "8 LANES", 720, 500, 220, col=(255, 235, 110))


@shot(W(12, "cranes"), cam=(1.0, 1.15, 0.5, 0.6, 0.5, 0.45))
def v31(cv, t, u):
    BGI(cv, "c_hwy", 14)
    crane(cv, 300, 2560, 2.4, math.sin(t * 2)); crane(cv, 1150, 2560, 2.0, math.sin(t * 2 + 1))
    for k in range(8): cone(cv, 80 + k * 190, 2540 + (k % 2) * 30, 1.5)
    label(cv, "CRANES. CONES.", 720, 520, 130); label(cv, "EVERYWHERE.", 720, 700, 130)


@shot(W(12, "engineer"), cam=(1.0, 1.12, 0.5, 0.55, 0.5, 0.5))
def v32(cv, t, u):
    BGI(cv, "c_base", 16)
    coffee_machine(cv, 1070, 2300, 2.6)
    sign(cv, "OUT OF ORDER", 1070, 1120, 70, col=(255, 130, 110))
    HM(cv, ENG, 440, 2540, 2.0, 1, **calm(t, mouth="flat", eyes="dot", tilt=5, armF=(30, 60)))
    label(cv, "THE BASEMENT", 720, 520, 110)


@shot(W(12, "boss"), cam=(1.0, 1.18, 0.5, 0.5, 0.5, 0.5))
def v33(cv, t, u):
    BGI(cv, "c_base", 16)
    k = abs(math.sin(t * 12))
    HM(cv, BOSS, 560, 2640, 2.5, 1, eyes="squint", mouth="open", open=0.3 + 0.7 * k, brow=-1, angry=1, armF=(140, 170), tilt=-5)
    g = ImageDraw.Draw(cv); g.rectangle([900, 2000, 1380, 2400], fill=(200, 160, 100), outline=OUT, width=12); label(cv, "BOX", 1140, 2200, 130, col=(90, 60, 30), stroke=0)
    bubble(cv, "TIME TO KILL.", 760, 520, 130, tail=(-80, 240), scale=pop_scale(u - 0.4))


@shot(W(12, "over"), cam=(1.0, 1.15, 0.5, 0.55, 0.5, 0.5))
def v34(cv, t, u):
    BGI(cv, "c_base", 18)
    HM(cv, ENG, 480, 2540, 2.1, 1, **calm(t, mouth="smile", eyes="dot", armF=(60, 100)))
    stopwatch(cv, 1100, 2150, 2.0, u * 200)
    stamp(cv, "IT'S OVER", 720, 900, u - 0.2, rot=-8)


@shot(W(13), cam=(1.0, 1.15, 0.5, 0.6, 0.5, 0.5))
def v35(cv, t, u):
    cars = flow(t, 4, 6, 12, 22)
    layer(cv, lambda l: road_view(l, t, vp=(720, 1000), lanes=4, speed=22, cars=cars, seed=12), 0)
    tt = t - W(13)
    water_jet(cv, 720, 1700, tt + 0.3, 1500)
    glow(cv, 720, 1300, 500, (160, 210, 255), 0.6)
    label(cv, "WATER MAIN!", 720, 480, 160)


@shot(W(13, "highway"), cam=(1.0, 1.15, 0.5, 0.6, 0.5, 0.5))
def v36(cv, t, u):
    canyon(cv, t, 4, False, 0, seed=13)
    g = ImageDraw.Draw(cv)
    g.rectangle([100, 1700, 1340, 1900], fill=(250, 250, 250), outline=OUT, width=12)
    for k in range(7): g.polygon([(100 + k * 180, 1900), (180 + k * 180, 1700), (260 + k * 180, 1700), (180 + k * 180, 1900)], fill=(230, 50, 60))
    for k in range(5): cone(cv, 140 + k * 290, 2300 + (k % 2) * 40, 2.0)
    sign(cv, "CLOSED", 720, 1100, 260, col=(230, 50, 60), tcol=(255, 255, 255))


@shot(W(14), cam=(1.0, 1.35, 0.5, 0.5, 0.5, 0.5))
def v37(cv, t, u):
    canyon(cv, t, 4, False, 0, seed=14, blur=20)
    dim(cv, int(160 * max(0, 1 - u * 3)), (255, 255, 255))
    label(cv, "NO WARNING", 720, 1100, 165); label(cv, "!", 720, 1650, 520)


@shot(W(15), cam=(1.0, 1.12, 0.5, 0.55, 0.5, 0.5))
def v38(cv, t, u):
    layer(cv, lambda l: aerial(l, t, "skyway"), 0)
    dim(cv, 70); g = ImageDraw.Draw(cv, "RGBA")
    n = int(160000 * ss(u / 3.0))
    sign(cv, f"{n:,} CARS", 720, 560, 190, col=(255, 255, 255))
    sign(cv, "NO SHORTCUT", 720, 2100, 130, col=(255, 130, 110)) if u > 3.0 else None


@shot(W(15, "city"), cam=(1.0, 1.15, 0.5, 0.55, 0.5, 0.5))
def v39(cv, t, u):
    BGI(cv, "c_hall", 14)
    for i, (ch, x) in enumerate(((CN1, 240), (CN2, 720), (CN3, 1200))):
        HM(cv, ch, x, 2540, 1.9, 1 if x < 720 else -1, eyes="wide", mouth="open", open=0.8, brow=1, armF=(150, 170), armB=(150, 170), bob=math.sin(t * 20 + i) * 5)
    label(cv, "WORST JAM EVER?", 720, 520, 130)
    clock(cv, 720, 1120, 190, u * 700)


@shot(W(16), cam=(1.0, 1.25, 0.5, 0.5, 0.5, 0.5))
def v40(cv, t, u):
    layer(cv, lambda l: aerial(l, t, "closed"), 0)
    label(cv, "...", 720, 900, 360) if u < 0.4 else label(cv, "NOTHING.", 720, 900, 220)


@shot(W(17), cam=(1.0, 1.1, 0.5, 0.5, 0.5, 0.55))
def v41(cv, t, u):
    layer(cv, lambda l: aerial(l, t, "closed"), 0)
    dim(cv, 40); g = ImageDraw.Draw(cv, "RGBA")
    label(cv, "KEEP MOVING", 720, 560, 190)
    for k in range(6): sparkle(cv, 160 + k * 230, 1000 + 160 * math.sin(t * 3 + k), 36)


@shot(W(17, "ambulances"), cam=(1.0, 1.14, 0.5, 0.55, 0.5, 0.55))
def v42(cv, t, u):
    layer(cv, lambda l: road_view(l, t, vp=(720, 1000), lanes=3, speed=20, cars=flow(t, 3, 4, 15, 20), seed=15), 0)
    z = mix(30.0, 2.6, ss(u / 1.8))
    sx, gy = 720 + 0, 1000 + 3.2 * 1000 / z
    car_at(cv, sx, gy, 1.9 * 1000 / z, "amb", (255, 255, 255), False)
    on = int(t * 6) % 2
    glow(cv, sx, gy - 380 * (1.9 * 1000 / z) / 400, 420, (255, 60, 60) if on else (60, 110, 255), 0.7)
    sign(cv, "EARLY!", 720, 520, 200, col=(120, 220, 140))


@shot(W(17, "five"), cam=(1.0, 1.1, 0.5, 0.5, 0.5, 0.5))
def v43(cv, t, u):
    BGI(cv, "c_dusk", 16)
    glow(cv, 720, 1300, 900, (255, 200, 120), 0.5)
    sign(cv, "5 MILES", 720, 560, 190, col=(255, 255, 255))
    clock(cv, 720, 1400, 420, 90 + u * 40)
    sign(cv, "15 MINUTES", 720, 2150, 170, col=(150, 230, 160))


@shot(W(17, "down"), cam=(1.0, 1.25, 0.5, 0.6, 0.5, 0.65))
def v44(cv, t, u):
    BGI(cv, "c_base", 20)
    HM(cv, ENG, 440, 2560, 1.9, 1, **calm(t, mouth="smile", eyes="dot", armF=(90, 120)))
    stopwatch(cv, 1000, 1950, 3.6, 180 + u * 60)
    label(cv, "CLICK", 1000, 1050, 160) if int(u * 4) % 2 == 0 else None


@shot(W(17, "nobody's"), cam=(1.0, 1.15, 0.5, 0.55, 0.5, 0.5))
def v45(cv, t, u):
    BGI(cv, "c_hall", 14)
    for i, (ch, x) in enumerate(((CN1, 240), (CN2, 720), (CN3, 1200))):
        HM(cv, ch, x, 2540, 1.9, 1 if x < 720 else -1, eyes="dot", mouth="flat", brow=1, tilt=-6, armF=(10, 10), look=(0, 1))
    label(cv, "...", 720, 700, 360)


@shot(W(18), cam=(1.0, 1.1, 0.5, 0.5, 0.5, 0.5))
def v46(cv, t, u):
    layer(cv, lambda l: aerial(l, t, "plain"), 0)
    dim(cv, 60); g = ImageDraw.Draw(cv, "RGBA")
    a = ss(u / 1.2)
    pts_me = [(150, 2200), (150, 1700), (720, 1700), (720, 600)]
    pts_all = [(1290, 2200), (1290, 1400), (1000, 1400), (1000, 600)]
    for pts, col in ((pts_me, (70, 200, 120, 255)), (pts_all, (90, 150, 255, 255))):
        n = int(len(pts) * a * 1.0)
        for i in range(min(len(pts) - 1, max(0, int((len(pts) - 1) * a + 0.999)))): g.line([pts[i], pts[i + 1]], fill=col, width=36)
    label(cv, "FASTEST FOR ME", 400, 500, 80, col=(150, 255, 190)); label(cv, "FASTEST FOR ALL", 1040, 380, 80, col=(170, 200, 255))


@shot(W(18, "one"), cam=(1.0, 1.12, 0.5, 0.5, 0.5, 0.45))
def v47(cv, t, u):
    layer(cv, lambda l: aerial(l, t, "skyway"), 0)
    dim(cv, 70); g = ImageDraw.Draw(cv, "RGBA")
    glow(cv, 720, 1300, 700, (255, 60, 60), 0.5)
    label(cv, "ONE BIG SHORTCUT", 720, 520, 120); label(cv, "= ONE BIG JAM", 720, 680, 120, col=(255, 130, 110))


@shot(W(18, "take"), cam=(1.0, 1.12, 0.5, 0.5, 0.5, 0.5))
def v48(cv, t, u):
    layer(cv, lambda l: aerial(l, t, "closed"), 0)
    dim(cv, 40); g = ImageDraw.Draw(cv, "RGBA")
    label(cv, "TAKE IT AWAY...", 720, 520, 130); label(cv, "...IT SPREADS OUT.", 720, 690, 100, col=(160, 255, 190))
    stamp(cv, "SMOOTH", 720, 2100, u - 1.5, rot=-6, col=(60, 170, 90))


@shot(W(18, "stadium"), cam=(1.0, 1.1, 0.5, 0.5, 0.5, 0.5))
def v49(cv, t, u):
    BGI(cv, "paper")
    g = ImageDraw.Draw(cv, "RGBA")
    g.ellipse([100, 700, 1340, 2000], fill=(206, 214, 196), outline=OUT, width=18)
    g.ellipse([300, 880, 1140, 1820], fill=(110, 170, 100), outline=OUT, width=10)
    exits = [(720, 700), (100, 1350), (1340, 1350), (720, 2000), (260, 960), (1180, 960), (260, 1750), (1180, 1750)]
    for i, (x, y) in enumerate(exits):
        big = i == 0
        g.rectangle([x - (90 if big else 36), y - (40 if big else 30), x + (90 if big else 36), y + (40 if big else 30)], fill=(70, 220, 120) if big else (255, 255, 255), outline=OUT, width=8)
        if big: glow(cv, x, y, 280, (80, 255, 140), 0.8)
    rnd = random.Random(2)
    for k in range(70):
        a = rnd.uniform(0, 6.28); r = rnd.uniform(60, 420); px, py = 720 + math.cos(a) * r, 1350 + math.sin(a) * r * 0.75
        f = ss((u - 0.3) / 3.0) * rnd.uniform(0.6, 1.0)
        px, py = mix(px, 720, f), mix(py, 780, f)
        g.ellipse([px - 16, py - 16, px + 16, py + 16], fill=(230, 90, 90, 255), outline=OUT, width=3)
    label(cv, "ONE GIANT EXIT", 720, 540, 120); label(cv, "ALL OTHER DOORS: OPEN", 720, 2200, 90)


@shot(W(18, "called"), cam=(1.0, 1.1, 0.5, 0.5, 0.5, 0.5))
def v50(cv, t, u):
    layer(cv, lambda l: aerial(l, t, "skyway"), 12)
    dim(cv, 110); g = ImageDraw.Draw(cv, "RGBA")
    label(cv, "BRAESS'S PARADOX", 720, 1100, int(112 * pop_scale(u - 0.1)) + 1)
    label(cv, "MORE ROADS", 720, 1500, 120, col=(255, 255, 255)); label(cv, "= SLOWER TRAFFIC", 720, 1660, 110, col=(255, 130, 110)) if u > 1.0 else None


@shot(W(18, "real"), cam=(1.0, 1.12, 0.5, 0.5, 0.5, 0.5))
def v51(cv, t, u):
    f = ss((u - 0.6) / 1.2)
    def bgf(l):
        aerial(l, t, "closed")
        g = ImageDraw.Draw(l, "RGBA")
        g.rectangle([590, 0, 850, DH], fill=(86, 88, 104) if f < 0.5 else (90, 180, 235))
        if f > 0.5:
            for k in range(14): g.arc([620 - 20 * (k % 2), k * 190 - 30, 800, k * 190 + 100], 0, 180, fill=(240, 250, 255, 255), width=8)
            for k in range(8): g.ellipse([540 - (k % 2) * 30, k * 330 + 40, 590, k * 330 + 130], fill=(80, 150, 70, 255), outline=OUT, width=5)
    layer(cv, bgf, 0)
    label(cv, "SEOUL", 720, 460, 190)
    label(cv, "HIGHWAY OUT. STREAM IN.", 720, 700, 84) if f > 0.4 else None
    label(cv, "TRAFFIC GOT FASTER", 720, 2300, 100, col=(160, 255, 190)) if f > 0.85 else None


@shot(W(19), cam=(1.0, 1.2, 0.5, 0.55, 0.5, 0.5))
def v52(cv, t, u):
    canyon(cv, t, 3, False, 0, seed=16, night=True)
    layer(cv, lambda l: road_view(l, t, vp=(720, 1000), lanes=3, speed=24, cars=flow(t, 3, 5, 16, 24), night=True, seed=16), 0)
    label(cv, "THE FASTEST WAY", 720, 520, 130); label(cv, "ACROSS TOWN?", 720, 700, 130)
    if u > 1.6:
        burst(cv, 720, 1500, u - 1.6, seed=3)
        glow(cv, 720, 1500, 900, (255, 200, 80), 0.9 * max(0, 1 - (u - 1.6)))
        stamp(cv, "BLOWN UP", 720, 2000, u - 1.6, rot=-8)


SHOT_TIMES = [s[0] for s in SHOTS]


def shot_at(t):
    i = 0
    for k, (t0, fn, cam) in enumerate(SHOTS):
        if t >= t0: i = k
    return i
