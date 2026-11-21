"""Braess's paradox story (traffic engineer / Skyway): transcript, timing, shots."""
import math, random
from PIL import Image, ImageDraw
import story as base
from story import ss, mix, pop_scale, clean
from toon import *
from toon3 import *
from chars import Char
import story_mafia as M
from story_mafia import HM, calm, stamp
import bgs

DW, DH = 1440, 2560
DURATION = 153.30
DEC_FILE = "hdec_words.json"

SEGS = [
    (0.04, 4.75, "To fix the worst traffic jam in the city, one engineer wanted to delete its fastest highway."),
    (5.07, 7.35, "It all started when the city built the Skyway."),
    (7.61, 21.66, "Six lanes of highway, slicing straight through downtown. It was supposed to be the great shortcut. Instead, a five mile drive now takes forty five minutes. Ambulances sit in traffic with their sirens screaming. Pizza shows up cold. Whole marriages end in the left lane."),
    (22.01, 39.01, "So the city hires a new traffic engineer, and he does what any sane person would do. He sits on a bridge every morning with a stopwatch and a notepad. But he doesn't time the Skyway. He times the little side streets nobody uses. And the only weird thing he ever writes down is this: every single driver takes the shortcut. Every single time."),
    (39.32, 43.26, "Then he walks into City Hall with his plan: tear the Skyway down. All of it."),
    (43.53, 46.51, "The council laughs so hard somebody spills coffee on the budget."),
    (46.80, 54.65, "One guy leans into his microphone and goes, great idea. And to fix hunger, close all the restaurants. The engineer just smiles and says,"),
    (55.06, 55.66, "Fewer roads."),
    (55.94, 58.47, "By the end of the month, he's famous. And not in a good way."),
    (58.81, 64.64, "The newspaper draws him holding a stick of dynamite, with a traffic cone on his head. Radio hosts call him the Highway Hater."),
    (64.91, 67.92, "Strangers honk at him while he's walking down the street."),
    (68.25, 81.68, "Now here's the weird part. Everybody figures he secretly hates cars, or wants people on buses and bikes. He doesn't. He doesn't want a single car off the road. He wants the exact same traffic on fewer roads. And somehow, he thinks that will make it faster. How is that possible?"),
    (82.03, 99.08, "Meanwhile, the city doubles down. The council votes to widen the Skyway to eight lanes. Cranes everywhere. Orange cones everywhere. The engineer gets moved to a desk in the basement, next to the broken coffee machine. His boss drops a cardboard box on his desk and goes, eight years with a stopwatch. You've got time to kill. It's over. This is the Skyway we want."),
    (99.42, 104.97, "Then one morning, a water main bursts right under the Skyway. The whole highway shuts down."),
    (105.23, 105.87, "No warning."),
    (106.31, 112.02, "One hundred sixty thousand cars, and no shortcut. The city braces for the worst traffic jam in its history."),
    (112.32, 113.20, "It never comes."),
    (113.47, 123.13, "Cars flow onto the side streets, and just keep moving. Ambulances arrive early. The five mile drive takes fifteen minutes. Down in the basement, a stopwatch clicks. Nobody's laughing anymore."),
    (123.41, 149.17, "You see, every driver takes the road that's fastest for them. Not the road that's fastest for everyone. With one big shortcut, everybody piles onto it, and it jams every street that leads to it. Take the shortcut away, and the traffic spreads out over all those empty side streets. It's like a stadium where everyone's rushing for one giant exit, while every other door is wide open. It's called Braess's paradox. In real life, Seoul tore down a downtown highway, put a stream there, and traffic actually got faster."),
    (149.54, 153.30, "The fastest way across town? Blowing up the fastest way across town."),
]
WORDS = base._align(SEGS, DEC_FILE)


def W(seg, word=None, n=0):
    if word is None: return SEGS[seg][0]
    hits = [x for x in WORDS if x[3] == seg and clean(x[0]) == word.lower()]
    return hits[n][1]


def E(seg): return SEGS[seg][1]


# ------------------------------------------------------------------ cast
ENG = Char(skin=(238, 196, 160), coat=(255, 150, 40), coat2=(255, 240, 120), pants=(60, 60, 84), hair=(60, 40, 30), hat=(250, 214, 60), hat_style="hard", long_coat=False)
CN1 = Char(skin=(236, 190, 150), coat=(60, 62, 84), coat2=(200, 40, 50), pants=(40, 40, 54), hair=(170, 170, 176), bald=True, stache=True, build=1.15)
CN2 = Char(skin=(246, 206, 170), coat=(86, 60, 100), coat2=(250, 210, 80), pants=(50, 40, 70), hair=(190, 110, 50), build=1.0)
CN3 = Char(skin=(200, 150, 110), coat=(50, 80, 70), coat2=(220, 220, 230), pants=(40, 50, 50), hair=(30, 24, 24), chops=True, build=1.1)
BOSS = Char(skin=(236, 190, 150), coat=(30, 70, 110), coat2=(200, 40, 50), pants=(30, 40, 60), hair=(120, 120, 126), stache=True, build=1.15)
HOST = Char(skin=(244, 206, 170), coat=(190, 60, 90), coat2=(250, 230, 120), pants=(50, 40, 70), hair=(40, 30, 30), long_coat=False)
DRV = Char(skin=(230, 186, 146), coat=(70, 120, 180), coat2=(250, 220, 80), pants=(50, 60, 80), hair=(60, 40, 30), long_coat=False)
COLS = [(220, 60, 60), (60, 120, 220), (240, 190, 50), (70, 170, 110), (150, 90, 190), (240, 120, 50), (90, 200, 220)]


def BG(cv, name, dx=0, dy=0, zoom=1.0): cv.alpha_composite(bgs.crop(name, dx, dy, zoom))


def traffic(cv, t, lanes, speed=0.0, n=6, seed=0, sc=0.8, jam=False, kinds=None):
    rnd = random.Random(seed)
    for li, y in enumerate(lanes):
        for k in range(n):
            col = COLS[(k * 3 + li * 2 + seed) % len(COLS)]
            kind = (kinds or {}).get((li, k), "car")
            gap = 330 * sc + (0 if jam else 120)
            x = (k * gap * 1.0 + speed * t * (1 + 0.15 * li)) % (n * gap) - 250 + (math.sin(t * 9 + k) * 6 if jam else 0)
            car(cv, x, y + (math.sin(t * 14 + k + li) * 3 if not jam else 0), kind, col, sc, 1)


def sign(cv, text, x, y, size=100, col=(255, 240, 120), tcol=(40, 30, 40)):
    g = ImageDraw.Draw(cv); f = ImageFont.truetype(FONT, size); bb = g.textbbox((0, 0), text, font=f)
    w, h = bb[2] - bb[0] + 80, bb[3] - bb[1] + 60
    g.rounded_rectangle([x - w / 2 - 8, y - h / 2 - 8, x + w / 2 + 8, y + h / 2 + 8], 26, fill=OUT)
    g.rounded_rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], 20, fill=col)
    g.text((x - (bb[2] - bb[0]) / 2 - bb[0], y - (bb[3] - bb[1]) / 2 - bb[1]), text, font=f, fill=tcol)


def clock(cv, x, y, r, ang, col=(255, 255, 255)):
    g = ImageDraw.Draw(cv)
    g.ellipse([x - r - 10, y - r - 10, x + r + 10, y + r + 10], fill=OUT); g.ellipse([x - r, y - r, x + r, y + r], fill=col)
    for k in range(12):
        a = k * math.pi / 6; g.line([(x + math.sin(a) * r * 0.82, y - math.cos(a) * r * 0.82), (x + math.sin(a) * r * 0.94, y - math.cos(a) * r * 0.94)], fill=OUT, width=6)
    a = math.radians(ang); g.line([(x, y), (x + math.sin(a) * r * 0.7, y - math.cos(a) * r * 0.7)], fill=(220, 50, 60), width=10)
    g.ellipse([x - 10, y - 10, x + 10, y + 10], fill=OUT)


SHOTS = []


def shot(t0, cam=(1.0, 1.07, 0.5, 0.5)):
    def deco(fn): SHOTS.append((t0, fn, cam)); return fn
    return deco


# ------------------------------------------------------------------ shots
@shot(W(0), cam=(1.0, 1.1, 0.5, 0.55))
def h01(cv, t, u):
    BG(cv, "c_city")
    HM(cv, ENG, 520, 2480, 1.8, 1, **calm(t, armF=(100, 130), eyes="dot", mouth="smile", brow=-0.3, tilt=-3))
    stopwatch(cv, 520 + 280, 1500, 0.9, u * 90)
    traffic(cv, t, (2100, 2300), 80, 5, 1, 0.7, jam=True)


@shot(W(0, "jam"), cam=(1.0, 1.08, 0.5, 0.65))
def h02(cv, t, u):
    BG(cv, "c_city")
    traffic(cv, t, (2000, 2200, 2400), 0, 6, 2, 0.85, jam=True)
    for k in range(4): honk(cv, 220 + k * 330, 1900 + (k % 2) * 200, t + k * 0.1)
    sign(cv, "WORST JAM EVER", 720, 1000, 100, col=(255, 120, 100))


@shot(W(0, "delete"), cam=(1.0, 1.1, 0.5, 0.5))
def h03(cv, t, u):
    BG(cv, "c_hwy")
    g = ImageDraw.Draw(cv)
    sign(cv, "SKYWAY", 720, 1180, 140, col=(70, 170, 110), tcol=(255, 255, 255))
    a = ss((u - 0.3) / 0.35)
    if a > 0:
        g.line([(300, 900), (300 + 840 * a, 900 + 560 * a)], fill=(230, 40, 50), width=34)
        g.line([(1140, 900), (1140 - 840 * a, 900 + 560 * a)], fill=(230, 40, 50), width=34)
    HM(cv, ENG, 300, 2500, 1.3, 1, **calm(t, armF=(140, 170), mouth="smile", eyes="dot"))


@shot(W(1), cam=(1.0, 1.1, 0.5, 0.5))
def h04(cv, t, u):
    BG(cv, "c_city")
    crane(cv, 330, 1650, 1.0, math.sin(t * 2)); crane(cv, 1100, 1650, 0.8, math.sin(t * 2 + 1))
    g = ImageDraw.Draw(cv); rise = ss(u / 1.8)
    g.rectangle([0, 2150 - 420 * rise, DW, 2150], fill=(96, 100, 112), outline=OUT, width=8)
    for k in range(7): cone(cv, 150 + k * 190, 2260, 0.55)
    sign(cv, "THE SKYWAY", 720, 800, 130, col=(70, 170, 110), tcol=(255, 255, 255)) if u > 1.0 else None


@shot(W(2), cam=(1.0, 1.08, 0.5, 0.55))
def h05(cv, t, u):
    BG(cv, "c_hwy")
    traffic(cv, t, (1790, 1930, 2070, 2210), 220, 6, 3, 0.55)
    label(cv, "SIX LANES", 720, 760, 150)


@shot(W(2, "shortcut"), cam=(1.0, 1.1, 0.5, 0.5))
def h06(cv, t, u):
    BG(cv, "c_hwy")
    traffic(cv, t, (1790, 1930, 2070, 2210), 240, 6, 4, 0.55)
    sign(cv, "SHORTCUT!", 720, 900, 150, col=(255, 235, 110))
    for k in range(4): sparkle(cv, 280 + k * 290, 1100 + 40 * math.sin(t * 5 + k), 36 + 8 * math.sin(t * 6 + k))


@shot(W(2, "five"), cam=(1.0, 1.08, 0.5, 0.5))
def h07(cv, t, u):
    BG(cv, "paper")
    sign(cv, "5 MILES", 720, 800, 170, col=(255, 255, 255))
    clock(cv, 720, 1450, 260, u * 360)
    sign(cv, "45 MINUTES", 720, 2000, 150, col=(255, 140, 120)) if u > 1.4 else None


@shot(W(2, "ambulances"), cam=(1.0, 1.08, 0.5, 0.6))
def h08(cv, t, u):
    BG(cv, "c_hwy")
    traffic(cv, t, (2000, 2210), 0, 6, 5, 0.75, jam=True)
    car(cv, 720, 2130, "amb", (255, 255, 255), 1.3, 1)
    g = ImageDraw.Draw(cv); on = int(t * 6) % 2
    g.ellipse([690, 1740, 750, 1790], fill=(255, 60, 60) if on else (255, 200, 200))
    rings(cv, 720, 1900, t, d=1, col=(255, 120, 120)); rings(cv, 720, 1900, t + 0.3, d=-1, col=(255, 120, 120))


@shot(W(2, "pizza"), cam=(1.0, 1.1, 0.5, 0.5))
def h09(cv, t, u):
    BG(cv, "c_city")
    pizza(cv, 720, 1650, 2.2, cold=True)
    HM(cv, DRV, 260, 2480, 1.2, 1, **calm(t, armF=(60, 90), eyes="wide", mouth="open", open=0.4, brow=1))
    label(cv, "COLD", 960, 1000, 170, col=(170, 220, 255))


@shot(W(2, "whole"), cam=(1.0, 1.1, 0.5, 0.55))
def h10(cv, t, u):
    BG(cv, "c_hwy")
    car(cv, 720, 2150, "car", (220, 60, 60), 1.6, 1)
    label(cv, "LEFT LANE", 720, 760, 130)
    bubble(cv, "YOU NEVER LISTEN!", 560, 1300, 78, tail=(100, 220), scale=pop_scale(u - 0.3))
    if u > 1.5: label(cv, "x", 920, 1250, 200, col=(255, 90, 110))


@shot(W(3), cam=(1.0, 1.08, 0.5, 0.6))
def h11(cv, t, u):
    BG(cv, "c_hall")
    HM(cv, CN1, 330, 2480, 1.5, 1, **calm(t, armF=(100, 130)))
    HM(cv, ENG, 1000, 2480, 1.5, -1, **calm(t, mouth="smile"))
    sign(cv, "NEW TRAFFIC ENGINEER", 720, 900, 76, col=(255, 255, 255))


@shot(W(3, "sits"), cam=(1.0, 1.1, 0.5, 0.45))
def h12(cv, t, u):
    BG(cv, "c_bridge")
    traffic(cv, t, (1600, 1760, 1920, 2080), 180, 6, 6, 0.5)
    HM(cv, ENG, 640, 2300, 1.4, 1, **calm(t, armF=(70, 100), look=(0.6, 0.5), eyes="dot", mouth="flat", tilt=6))
    stopwatch(cv, 960, 1900, 0.8, u * 120)


@shot(W(3, "doesn't"), cam=(1.0, 1.1, 0.5, 0.6))
def h13(cv, t, u):
    BG(cv, "c_alley")
    traffic(cv, t, (2100, 2290), 20, 2, 7, 0.7)
    stopwatch(cv, 720, 1300, 1.6, u * 150)
    label(cv, "SIDE STREETS", 720, 800, 120)


@shot(W(3, "weird"), cam=(1.0, 1.08, 0.5, 0.5))
def h14(cv, t, u):
    BG(cv, "c_base")
    g = ImageDraw.Draw(cv)
    g.rounded_rectangle([160, 560, 1280, 2000], 40, fill=(252, 250, 240), outline=OUT, width=12)
    label(cv, "EVERY DRIVER", 720, 760, 100, col=(40, 30, 50), stroke=0); label(cv, "TAKES THE SKYWAY", 720, 880, 100, col=(40, 30, 50), stroke=0)
    for k in range(8):
        a = pop_scale(u - 0.4 - k * 0.3)
        if a > 0.1: label(cv, "v", 330 + (k % 4) * 260, 1250 + (k // 4) * 260, int(180 * a), col=(60, 170, 90), stroke=0)


@shot(W(4), cam=(1.0, 1.1, 0.5, 0.55))
def h15(cv, t, u):
    BG(cv, "c_hall")
    x = mix(-100, 720, ss(u / 1.4))
    HM(cv, ENG, x, 2500, 1.6, 1, **calm(t, bob=-abs(math.sin(t * 8)) * 8 if u < 1.4 else 0, walk=math.sin(t * 8) * (u < 1.4), armF=(100, 120)))
    sign(cv, "TEAR IT DOWN", 720, 800, 130, col=(255, 130, 110)) if u > 1.4 else None


@shot(W(5), cam=(1.0, 1.08, 0.5, 0.6))
def h16(cv, t, u):
    BG(cv, "c_hall")
    for i, (ch, x) in enumerate(((CN1, 280), (CN2, 720), (CN3, 1160))):
        k = abs(math.sin(t * 13 + i))
        HM(cv, ch, x, 2480, 1.35, 1 if x < 720 else -1, eyes="closed", mouth="laugh" if False else "open", open=0.4 + 0.6 * k, tilt=-10 + 4 * math.sin(t * 13 + i), bob=-k * 12, armF=(30, 60))
    if u > 1.2:
        g = ImageDraw.Draw(cv); g.ellipse([560, 1900, 880, 2020], fill=(90, 50, 30)); label(cv, "BUDGET", 720, 1760, 90)


@shot(W(6), cam=(1.0, 1.12, 0.5, 0.45))
def h17(cv, t, u):
    BG(cv, "c_hall")
    k = abs(math.sin(t * 12))
    HM(cv, CN1, 640, 2500, 1.9, 1, eyes="squint", mouth="open", open=0.3 + 0.7 * k, brow=-0.6, tilt=-5, armF=(120, 150))
    mic(cv, 960, 2300, 1.4)
    bubble(cv, "GREAT IDEA!", 720, 760, 130, tail=(-80, 220), scale=pop_scale(u - 0.3))


@shot(W(6, "fix"), cam=(1.0, 1.08, 0.5, 0.5))
def h18(cv, t, u):
    BG(cv, "c_hall")
    sign(cv, "HUNGRY?", 720, 760, 150, col=(255, 255, 255))
    g = ImageDraw.Draw(cv)
    g.ellipse([470, 1200, 970, 1700], fill=(255, 255, 255), outline=OUT, width=14)
    label(cv, "FOOD", 720, 1450, 150, col=(60, 60, 70), stroke=0)
    a = ss((u - 0.8) / 0.4)
    g.line([(420, 1150), (420 + 600 * a, 1150 + 600 * a)], fill=(230, 40, 50), width=34)
    label(cv, "CLOSE THE RESTAURANTS", 720, 2000, 78) if u > 1.0 else None


@shot(W(6, "smiles"), cam=(1.0, 1.25, 0.5, 0.35))
def h19(cv, t, u):
    BG(cv, "c_hall")
    HM(cv, ENG, 720, 2520, 2.0, 1, **calm(t, mouth="smile", eyes="dot", armF=(8, 8)))
    sparkle(cv, 940, 900, 40 * pop_scale(u - 0.7)) if u > 0.7 else None


@shot(W(7), cam=(1.0, 1.1, 0.5, 0.5))
def h20(cv, t, u):
    BG(cv, "c_hwy")
    n = 4 - int(ss(u / 0.7) * 2.2)
    traffic(cv, t, (1790, 1930, 2070, 2210)[:max(2, n)], 160, 5, 8, 0.5)
    label(cv, "FEWER ROADS", 720, 760, 170)


@shot(W(8), cam=(1.0, 1.08, 0.5, 0.5))
def h21(cv, t, u):
    BG(cv, "c_city")
    im, (ox, oy) = newspaper(cv, 0, 0, "THE ROAD ENEMY?", 1.5, rot=-5)
    cv.alpha_composite(im, (int(720 - ox), int(1250 - oy)))
    HM(cv, ENG, 260, 2480, 1.0, 1, **calm(t, mouth="flat", eyes="wide")) if u > 0.4 else None


@shot(W(9), cam=(1.0, 1.1, 0.5, 0.55))
def h22(cv, t, u):
    BG(cv, "paper")
    g = ImageDraw.Draw(cv)
    g.rounded_rectangle([140, 540, 1300, 2000], 40, fill=(252, 250, 240), outline=OUT, width=14)
    cx, cy = 720, 1450
    g.ellipse([cx - 230, cy - 230, cx + 230, cy + 230], fill=(244, 206, 170), outline=OUT, width=12)                 # drawn face
    g.polygon([(cx - 120, cy - 220), (cx + 120, cy - 220), (cx + 60, cy - 520), (cx - 60, cy - 520)], fill=(250, 120, 30), outline=OUT)   # cone hat
    g.ellipse([cx - 100, cy - 70, cx - 50, cy - 20], fill=(255, 255, 255), outline=OUT, width=6); g.ellipse([cx + 50, cy - 70, cx + 100, cy - 20], fill=(255, 255, 255), outline=OUT, width=6)
    g.line([(cx - 90, cy + 80), (cx + 90, cy + 80)], fill=OUT, width=10)
    g.rectangle([cx + 260, cy - 20, cx + 400, cy + 60], fill=(220, 50, 50), outline=OUT, width=8)                       # dynamite
    g.line([(cx + 400, cy + 20), (cx + 460, cy - 60)], fill=OUT, width=8)
    sparkle(cv, cx + 470, cy - 70, 40 + 10 * math.sin(t * 20))


@shot(W(9, "radio"), cam=(1.0, 1.08, 0.5, 0.55))
def h23(cv, t, u):
    BG(cv, "c_hall")
    k = abs(math.sin(t * 12))
    HM(cv, HOST, 640, 2500, 1.8, 1, eyes="squint", mouth="open", open=0.3 + 0.7 * k, brow=-0.5, armF=(120, 150))
    mic(cv, 980, 2300, 1.4)
    bubble(cv, "THE HIGHWAY HATER!", 720, 760, 92, tail=(-60, 220), scale=pop_scale(u - 0.2))


@shot(W(10), cam=(1.0, 1.08, 0.5, 0.6))
def h24(cv, t, u):
    BG(cv, "c_city")
    x = mix(300, 1000, ss(u / 3.0))
    HM(cv, ENG, x, 2480, 1.3, 1, bob=-abs(math.sin(t * 8)) * 8, walk=math.sin(t * 8), armF=(20 * math.sin(t * 8), 10), armB=(-20 * math.sin(t * 8), 10), mouth="flat", eyes="dot")
    for k in range(3):
        car(cv, 250 + k * 450, 2050, "car", COLS[k], 0.7, 1); honk(cv, 250 + k * 450 + 150, 1900, t + k * 0.2)
    label(cv, "HONK!", 720, 800, 160) if int(t * 4) % 2 else None


@shot(W(11), cam=(1.0, 1.1, 0.5, 0.45))
def h25(cv, t, u):
    BG(cv, "c_city")
    HM(cv, ENG, 720, 2500, 1.7, 1, **calm(t, eyes="squint", mouth="flat", brow=0.4, tilt=-4))
    label(cv, "THE WEIRD PART", 720, 700, 120)
    bubble(cv, "?", 1100, 1000, 200, tail=(-100, 160), scale=pop_scale(u - 0.2))


@shot(W(11, "everybody"), cam=(1.0, 1.08, 0.5, 0.5))
def h26(cv, t, u):
    BG(cv, "paper")
    g = ImageDraw.Draw(cv)
    bubble(cv, "HE HATES CARS!", 720, 800, 100, tail=(0, 150), scale=pop_scale(u - 0.2))
    car(cv, 720, 1750, "car", (220, 60, 60), 1.8, 1)
    a = ss((u - 1.0) / 0.4)
    g.line([(300, 1250), (300 + 840 * a, 1250 + 650 * a)], fill=(230, 40, 50), width=34)


@shot(W(11, "doesn't"), cam=(1.0, 1.1, 0.5, 0.5))
def h27(cv, t, u):
    BG(cv, "c_city")
    HM(cv, ENG, 560, 2480, 1.6, 1, **calm(t, mouth="smile", eyes="dot", armF=(60, 100), tilt=4 * math.sin(t * 5)))
    car(cv, 1000, 2250, "car", (60, 120, 220), 1.1, -1)
    label(cv, "LOVES CARS", 720, 780, 130) if u > 0.6 else None
    for k in range(3): sparkle(cv, 1000 + (k - 1) * 120, 1850 + 30 * math.sin(t * 5 + k), 30)


@shot(W(11, "wants", 1), cam=(1.0, 1.06, 0.5, 0.5))
def h28(cv, t, u):
    BG(cv, "paper")
    g = ImageDraw.Draw(cv)
    for k, y in enumerate((900, 1150, 1400)):
        g.rounded_rectangle([140, y - 60, 1300, y + 60], 30, fill=(80, 84, 96), outline=OUT, width=8)
    f = ss((u - 1.0) / 0.6)
    for k in range(5): car(cv, (t * 200 + k * 260) % 1700 - 150, 900 + (k % 3) * 250 * (1 - f) + (k % 2) * 125 * f, "car", COLS[k], 0.4, 1)
    if f > 0.5: g.rounded_rectangle([140, 1340, 1300, 1460], 30, fill=(255, 255, 255, 0))
    label(cv, "SAME TRAFFIC. FEWER ROADS.", 720, 560, 80)
    g.line([(280, 1400), (1160, 1400)], fill=(250, 250, 250), width=0)


@shot(W(11, "how"), cam=(1.0, 1.12, 0.5, 0.45))
def h29(cv, t, u):
    BG(cv, "c_city")
    HM(cv, ENG, 720, 2500, 1.7, 1, **calm(t, eyes="dot", mouth="smile", tilt=3))
    label(cv, "HOW?", 720, 800, int(300 * pop_scale(u - 0.1)) + 1)


@shot(W(12), cam=(1.0, 1.08, 0.5, 0.5))
def h30(cv, t, u):
    BG(cv, "c_hall")
    for i, (ch, x) in enumerate(((CN1, 280), (CN2, 720), (CN3, 1160))):
        HM(cv, ch, x, 2480, 1.3, 1 if x < 720 else -1, **calm(t, armF=(160, 175), mouth="smile", ph=i))
    sign(cv, "WIDEN TO 8 LANES", 720, 800, 100, col=(255, 235, 110))


@shot(W(12, "cranes"), cam=(1.0, 1.08, 0.5, 0.55))
def h31(cv, t, u):
    BG(cv, "c_hwy")
    for k, x in enumerate((220, 720, 1220)): crane(cv, x, 1700, 0.7 + 0.2 * (k == 1), math.sin(t * 2 + k))
    for k in range(9): cone(cv, 100 + k * 160, 2300 + (k % 2) * 40, 0.55)
    label(cv, "CRANES. CONES. EVERYWHERE.", 720, 700, 80)


@shot(W(12, "engineer"), cam=(1.0, 1.08, 0.5, 0.6))
def h32(cv, t, u):
    BG(cv, "c_base")
    coffee_machine(cv, 1100, 1900, 1.5)
    sign(cv, "OUT OF ORDER", 1100, 1180, 56, col=(255, 130, 110))
    HM(cv, ENG, 480, 2450, 1.4, 1, **calm(t, mouth="flat", eyes="dot", tilt=5, armF=(30, 60)))
    label(cv, "BASEMENT", 720, 640, 100)


@shot(W(12, "boss"), cam=(1.0, 1.1, 0.5, 0.55))
def h33(cv, t, u):
    BG(cv, "c_base")
    k = abs(math.sin(t * 12))
    HM(cv, BOSS, 640, 2500, 1.8, 1, eyes="squint", mouth="open", open=0.3 + 0.7 * k, brow=-1, angry=1, armF=(140, 170), tilt=-5)
    g = ImageDraw.Draw(cv); g.rectangle([900, 1800, 1260, 2060], fill=(200, 160, 100), outline=OUT, width=10); label(cv, "BOX", 1080, 1930, 80, col=(90, 60, 30), stroke=0)
    bubble(cv, "TIME TO KILL.", 760, 760, 110, tail=(-80, 220), scale=pop_scale(u - 0.4))


@shot(W(12, "over"), cam=(1.0, 1.1, 0.5, 0.55))
def h34(cv, t, u):
    BG(cv, "c_base")
    HM(cv, ENG, 560, 2480, 1.7, 1, **calm(t, mouth="smile", eyes="dot", armF=(60, 100)))
    stopwatch(cv, 1020, 2000, 1.1, u * 200)
    stamp(cv, "IT'S OVER", 720, 900, u - 0.2, rot=-8)


@shot(W(13), cam=(1.0, 1.1, 0.5, 0.55))
def h35(cv, t, u):
    BG(cv, "c_hwy")
    traffic(cv, t, (1790, 1930, 2070, 2210), 200, 6, 9, 0.55)
    water_jet(cv, 720, 2300, t - W(13) + 0.3, 1300)
    label(cv, "WATER MAIN!", 720, 700, 140)


@shot(W(13, "highway"), cam=(1.0, 1.08, 0.5, 0.55))
def h36(cv, t, u):
    BG(cv, "c_hwy")
    for k in range(9): cone(cv, 90 + k * 170, 2330, 0.6)
    g = ImageDraw.Draw(cv)
    g.rectangle([100, 1850, 1340, 2000], fill=(250, 250, 250), outline=OUT, width=10)
    for k in range(7): g.polygon([(100 + k * 180, 2000), (180 + k * 180, 1850), (260 + k * 180, 1850), (180 + k * 180, 2000)], fill=(230, 50, 60))
    sign(cv, "CLOSED", 720, 1200, 200, col=(230, 50, 60), tcol=(255, 255, 255))


@shot(W(14), cam=(1.0, 1.25, 0.5, 0.5))
def h37(cv, t, u):
    BG(cv, "c_hwy")
    label(cv, "NO WARNING", 720, 1100, 200)
    label(cv, "!", 720, 1500, 380)


@shot(W(15), cam=(1.0, 1.06, 0.5, 0.5))
def h38(cv, t, u):
    BG(cv, "c_city")
    traffic(cv, t, (1980, 2090, 2200, 2310, 2420), 0, 12, 10, 0.4, jam=True)
    sign(cv, "160,000 CARS", 720, 900, 140, col=(255, 255, 255))
    sign(cv, "NO SHORTCUT", 720, 1250, 110, col=(255, 130, 110)) if u > 2.0 else None


@shot(W(15, "city"), cam=(1.0, 1.1, 0.5, 0.55))
def h39(cv, t, u):
    BG(cv, "c_hall")
    for i, (ch, x) in enumerate(((CN1, 280), (CN2, 720), (CN3, 1160))):
        HM(cv, ch, x, 2480, 1.3, 1 if x < 720 else -1, eyes="wide", mouth="open", open=0.8, brow=1, armF=(150, 170), armB=(150, 170), bob=math.sin(t * 20 + i) * 4)
    label(cv, "WORST JAM EVER?", 720, 800, 100)


@shot(W(16), cam=(1.0, 1.15, 0.5, 0.5))
def h40(cv, t, u):
    BG(cv, "c_city")
    traffic(cv, t, (2000, 2200, 2400), 300, 4, 11, 0.75)
    label(cv, "...", 720, 900, 300) if u < 0.4 else label(cv, "NOTHING", 720, 900, 170)


@shot(W(17), cam=(1.0, 1.08, 0.5, 0.55))
def h41(cv, t, u):
    BG(cv, "c_alley")
    traffic(cv, t, (2100, 2290), 380, 5, 12, 0.7)
    label(cv, "KEEP MOVING", 720, 800, 140)


@shot(W(17, "ambulances"), cam=(1.0, 1.08, 0.5, 0.6))
def h42(cv, t, u):
    BG(cv, "c_alley")
    car(cv, mix(-400, 1900, ss(u / 1.8)), 2200, "amb", (255, 255, 255), 1.4, 1)
    sign(cv, "EARLY!", 720, 800, 160, col=(120, 220, 140))


@shot(W(17, "five"), cam=(1.0, 1.08, 0.5, 0.5))
def h43(cv, t, u):
    BG(cv, "paper")
    sign(cv, "5 MILES", 720, 700, 150, col=(255, 255, 255))
    clock(cv, 720, 1400, 260, 90 + u * 40)
    sign(cv, "15 MINUTES", 720, 1950, 150, col=(150, 230, 160))


@shot(W(17, "down"), cam=(1.0, 1.3, 0.5, 0.6))
def h44(cv, t, u):
    BG(cv, "c_base")
    HM(cv, ENG, 520, 2480, 1.5, 1, **calm(t, mouth="smile", eyes="dot", armF=(90, 120)))
    stopwatch(cv, 960, 1800, 1.6, 180 + u * 60)
    label(cv, "click", 960, 1360, 110) if int(u * 4) % 2 == 0 else None


@shot(W(17, "nobody's"), cam=(1.0, 1.08, 0.5, 0.55))
def h45(cv, t, u):
    BG(cv, "c_hall")
    for i, (ch, x) in enumerate(((CN1, 280), (CN2, 720), (CN3, 1160))):
        HM(cv, ch, x, 2480, 1.3, 1 if x < 720 else -1, eyes="dot", mouth="flat", brow=1, tilt=-6, armF=(10, 10), look=(0, 1))
    label(cv, "...", 720, 800, 300)


@shot(W(18), cam=(1.0, 1.06, 0.5, 0.5))
def h46(cv, t, u):
    BG(cv, "paper")
    g = ImageDraw.Draw(cv)
    g.rounded_rectangle([160, 800, 1280, 1160], 40, fill=(255, 255, 255), outline=OUT, width=10)
    label(cv, "FASTEST FOR ME", 720, 980, 96, col=(60, 140, 90), stroke=0)
    g.rounded_rectangle([160, 1360, 1280, 1720], 40, fill=(255, 255, 255), outline=OUT, width=10)
    label(cv, "FASTEST FOR ALL", 720, 1540, 96, col=(60, 100, 190), stroke=0)
    g.text((600, 1190), "!=", fill=OUT) if False else label(cv, "NOT THE SAME", 720, 1250, 70)


@shot(W(18, "one"), cam=(1.0, 1.06, 0.5, 0.5))
def h47(cv, t, u):
    BG(cv, "paper")
    g = ImageDraw.Draw(cv)
    g.rounded_rectangle([140, 1380, 1300, 1500], 30, fill=(70, 170, 110), outline=OUT, width=8)
    for k, y in enumerate((900, 1050, 1200)): g.rounded_rectangle([140, y - 30, 1300, y + 30], 20, fill=(170, 172, 182), outline=OUT, width=6)
    for k in range(12): car(cv, (t * 140 + k * 120) % 1500 - 100, 1440 + (k % 3) * 4, "car", COLS[k % 7], 0.3, 1)
    for k in range(5): honk(cv, 300 + k * 220, 1360, t + k * 0.1)
    label(cv, "ONE BIG SHORTCUT = JAM", 720, 600, 80)


@shot(W(18, "take"), cam=(1.0, 1.06, 0.5, 0.5))
def h48(cv, t, u):
    BG(cv, "paper")
    g = ImageDraw.Draw(cv)
    a = ss(u / 0.8)
    g.rounded_rectangle([140, 1380, 1300, 1500], 30, fill=(70, 170, 110) if a < 0.5 else (230, 230, 230), outline=OUT, width=8)
    for k, y in enumerate((900, 1050, 1200)): g.rounded_rectangle([140, y - 30, 1300, y + 30], 20, fill=(170, 172, 182), outline=OUT, width=6)
    for k in range(12):
        ty = mix(1440, (900, 1050, 1200)[k % 3], a)
        car(cv, (t * 260 + k * 120) % 1500 - 100, ty, "car", COLS[k % 7], 0.3, 1)
    label(cv, "TAKE IT AWAY. IT SPREADS OUT.", 720, 600, 70)
    stamp(cv, "SMOOTH", 720, 2000, u - 1.4, rot=-6, col=(60, 170, 90))


@shot(W(18, "stadium"), cam=(1.0, 1.08, 0.5, 0.55))
def h49(cv, t, u):
    BG(cv, "paper")
    g = ImageDraw.Draw(cv)
    g.ellipse([140, 760, 1300, 1700], fill=(236, 230, 214), outline=OUT, width=14)
    g.rectangle([660, 740, 780, 800], fill=(60, 170, 90), outline=OUT, width=6)                       # big exit
    for (x, y) in ((250, 1230), (1190, 1230), (720, 1690)): g.rectangle([x - 40, y - 40, x + 40, y + 40], fill=(255, 255, 255), outline=OUT, width=6)
    for k in range(30):
        a = k * 2.4; r = 280 * (1 - ss(u / 3.0) * 0.8) + 40 * math.sin(k)
        g.ellipse([720 + math.cos(a) * r - 18, 1230 + math.sin(a) * r * 0.8 - 18, 720 + math.cos(a) * r + 18, 1230 + math.sin(a) * r * 0.8 + 18], fill=(230, 90, 90), outline=OUT, width=3)
    label(cv, "ONE GIANT EXIT", 720, 620, 100)
    label(cv, "OTHER DOORS: OPEN", 720, 1880, 80)


@shot(W(18, "called"), cam=(1.0, 1.06, 0.5, 0.5))
def h50(cv, t, u):
    BG(cv, "paper")
    label(cv, "BRAESS'S PARADOX", 720, 1200, int(130 * pop_scale(u - 0.1)) + 1, col=(255, 255, 255))
    put(cv, __import__("toon2").magnifier(2.8), 980 + 40 * math.sin(t * 2), 1650 + 20 * math.cos(t * 2))
    label(cv, "More roads. Slower traffic.", 720, 2150, 66) if u > 1.0 else None


@shot(W(18, "real"), cam=(1.0, 1.06, 0.5, 0.5))
def h51(cv, t, u):
    BG(cv, "c_hwy")
    f = ss((u - 0.6) / 1.0)
    g = ImageDraw.Draw(cv)
    if f < 0.5: g.rectangle([0, 1700, DW, 2300], fill=(70, 72, 84))
    else:
        g.rectangle([0, 1700, DW, 2300], fill=(110, 190, 235))
        for k in range(8): g.arc([k * 200 - 100, 1900 + 30 * math.sin(t * 3 + k), k * 200 + 100, 2000], 0, 180, fill=(240, 250, 255), width=8)
    label(cv, "SEOUL", 720, 760, 160)
    label(cv, "HIGHWAY -> STREAM" if False else "HIGHWAY GONE. STREAM IN.", 720, 1100, 76) if f > 0.4 else None
    if f > 0.8: label(cv, "TRAFFIC GOT FASTER", 720, 2450, 90, col=(160, 255, 190))


@shot(W(19), cam=(1.0, 1.12, 0.5, 0.5))
def h52(cv, t, u):
    BG(cv, "c_dusk")
    traffic(cv, t, (2000, 2200, 2400), 260, 5, 13, 0.75)
    label(cv, "THE FASTEST WAY", 720, 760, 120); label(cv, "ACROSS TOWN?", 720, 920, 120)
    if u > 1.6:
        stamp(cv, "BLOWN UP", 720, 1700, u - 1.6, rot=-8)
        for k in range(10): sparkle(cv, 220 + k * 110, 1200 + 70 * math.sin(t * 8 + k), 40)


SHOT_TIMES = [s[0] for s in SHOTS]


def shot_at(t):
    i = 0
    for k, (t0, fn, cam) in enumerate(SHOTS):
        if t >= t0: i = k
    return i
