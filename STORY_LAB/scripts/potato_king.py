"""Story 1: The King Who Wanted To Be Robbed - shot list (pack section 8)."""
import math, os
from engine import *
import cast, props as P
from cast import draw as C

ROOT = os.path.dirname(HERE)
story = Story("potato_king", ROOT)
shot, sfx = story.shot, story.add_sfx

DAY = dict(top="#78C3EE", mid="#BDE3F5", bot="#FFF0CC", hill=(0.45, 0.72, 0.38), hill2=(0.36, 0.62, 0.32), ground=(0.56, 0.78, 0.36))
NIGHT = dict(top="#0E1033", mid="#27245A", bot="#4A3A6E", hill=(0.18, 0.25, 0.35), hill2=(0.14, 0.2, 0.3), ground=(0.2, 0.28, 0.3))
DUSK = dict(top="#3B3F8C", mid="#C77A9A", bot="#FFC48A", hill=(0.42, 0.45, 0.45), hill2=(0.34, 0.38, 0.4), ground=(0.48, 0.55, 0.4))
GREY = dict(top="#9FB4C4", mid="#C9D2D6", bot="#E8E2D2", hill=(0.55, 0.6, 0.5), hill2=(0.48, 0.52, 0.45), ground=(0.68, 0.66, 0.52))
GY = 1250  # ground line


def outside(f, pal, palace=None, snowy=0.0, t_sun=True, houses=None):
    c = f.ctx
    P.sky(f, pal["top"], pal["bot"], pal["mid"])
    f.layer(0.15)
    if pal is NIGHT:
        P.stars(c, -800, -600, 2700, 1500, 120, f.t)
        P.moon(c, 820, 330, 70)
    elif t_sun:
        P.sun(c, 230, 380, 80)
        P.cloud(c, 700 + f.t * 6, 300, 0.9)
        P.cloud(c, -100 + f.t * 4, 520, 0.7)
    f.layer(0.35)
    P.hills(c, GY - 220, pal["hill"], 2, amp=120)
    f.layer(0.6)
    P.hills(c, GY - 110, pal["hill2"], 5, amp=70, n=9)
    if houses:
        for hx in houses:
            P.house(c, hx, GY - 40, 200, 150, lit=pal is NIGHT)
    if palace:
        P.palace(c, palace[0], palace[1], palace[2], lit=pal is NIGHT, t=f.t)
    f.layer(1.0)
    P.ground(c, GY, pal["ground"])
    if snowy > 0:
        c.push_group()
        P.snow_ground(c, GY)
        c.pop_group_to_source()
        c.paint_with_alpha(clamp(snowy))


def pig(c, x, y, s=1.0, t=0, happy=True, fd=1):
    c.save()
    c.translate(x, y)
    c.scale(s * fd, s)
    soft_shadow(c, 0, 4, 120, 16, 0.3)
    for lx in (-60, -25, 30, 60):
        rrect(c, lx - 10, -50, 20, 50, 6)
        fs(c, (0.95, 0.62, 0.68), 5)
    c.move_to(-100, -80)
    c.curve_to(-110, -60, -120, -70, -125, -90)
    stroke(c, 6)
    ellipse(c, 0, -95, 105, 65)
    fs(c, (1.0, 0.72, 0.78), 7)
    c.arc(85, -120, 55, 0, 2 * math.pi)
    fs(c, (1.0, 0.72, 0.78), 7)
    for ex in (60, 105):
        poly(c, [(ex - 18, -165), (ex + 10, -200), (ex + 18, -160)])
        fs(c, (0.98, 0.6, 0.66), 5)
    ellipse(c, 132, -112, 22, 28)
    fs(c, (0.98, 0.6, 0.66), 5)
    for ny in (-120, -104):
        ellipse(c, 134, ny, 4, 6)
        fill(c, INK)
    for ex in (72, 100):
        if happy:
            c.move_to(ex - 9, -135)
            c.curve_to(ex - 5, -146, ex + 5, -146, ex + 9, -135)
            stroke(c, 5)
        else:
            c.arc(ex, -138, 6, 0, 2 * math.pi)
            fill(c, INK)
    c.restore()


def guard_ring(f, cx, cy, rx, ry, n=6, s=0.8, expr="flat", look=(0, 0), torches=True, legs="stand", back=True):
    c = f.ctx
    pts = []
    for k in range(n):
        a = math.pi * (k / (n - 1)) if not back else 2 * math.pi * k / n + 0.3
        pts.append((cx + math.cos(a) * rx, cy + math.sin(a) * ry))
    pts.sort(key=lambda p: p[1])
    for x, y in pts:
        sc = s * (0.85 + 0.3 * (y - cy + ry) / (2 * ry))
        C(c, "guard", x, y, sc, expr=expr, arms="hold" if torches else "down", legs=legs, t=f.t + x * 0.01, look=look,
          hold=(lambda c, hx, hy: P.torch(c, hx, hy + 10, 0.9, f.t + hx)) if torches else None)


# --------------------------------------------------------------------- 0.0 hook: aerial push-down, guards ring the field at night
@shot(0.0)
def s_hook(f):
    c = f.ctx
    k = ease(f.p)
    f.cam(540, lerp(950, 1330, k), lerp(0.95, 1.35, k))
    outside(f, NIGHT, palace=(540, GY - 80, 0.75))
    P.field(c, 160, 920, GY + 70, GY + 380, f.t, rows=4)
    guard_ring(f, 540, GY + 230, 470, 230, n=8, s=0.75)
    vignette(f, 0.5)


# --------------------------------------------------------------------- 2.5 ECU: king's sly wink
@shot("and secretly")
def s_wink(f):
    c = f.ctx
    f.cam(540, 760, lerp(1.0, 1.1, f.p))
    P.sky(f, NIGHT["top"], NIGHT["bot"], NIGHT["mid"])
    f.layer(0.3)
    P.palace(c, 540, 1900, 1.6, lit=True, t=f.t)
    f.layer(1)
    expr = "wink" if f.lt > 0.9 else "sly"
    C(c, "king", 540, 1900, 4.2, expr=expr, arms="chin", t=f.t, look=(0.6, 0))
    if f.lt > 0.9:
        a = clamp((f.lt - 0.9) * 4) * (1 - clamp((f.lt - 1.5) * 3))
        glow(c, 700, 640, 140, (1, 1, 0.8), a)
    vignette(f, 0.5)


# --------------------------------------------------------------------- 4.0 low wide: empty market, thin villagers
@shot("You see")
def s_starving(f):
    c = f.ctx
    f.cam(lerp(480, 600, f.p), 1380, 1.22)
    outside(f, GREY, t_sun=False, houses=[-150, 980])
    P.stall(c, 230, GY + 30, 1.0, empty=True)
    P.stall(c, 830, GY + 30, 1.0, cols=((0.4, 0.55, 0.85), (1, 1, 1)), empty=True)
    for k, (who, x) in enumerate((("n1", 120), ("n3", 420), ("n2", 650), ("kid", 900))):
        C(c, who, x, GY + 260 + (k % 2) * 40, 1.05, expr="sad", arms="down", t=f.t + k, look=(0, 0.6), squash=-0.05)
    P.basket(c, 540, GY + 330, 1.1, 0)
    P.basket(c, 290, GY + 360, 0.9, 0)
    vignette(f, 0.5)


# --------------------------------------------------------------------- 6.5 the perfect food
@shot("And he had")
def s_king_idea(f):
    c = f.ctx
    f.cam(540, 1000, lerp(1.05, 1.15, f.p))
    outside(f, DAY, palace=(540, GY - 40, 0.8))
    C(c, "king", 540, GY + 330, 1.6, expr="happy" if f.lt > 0.6 else "smile", arms="up" if f.lt > 0.6 else "hips", t=f.t)
    vignette(f, 0.35)


@shot("Potatoes.")
def s_potato_pop(f):
    c = f.ctx
    f.cam(540, 1050, lerp(1.0, 1.08, f.p))
    outside(f, DAY)
    c.rectangle(-500, GY, 2200, 1200)
    fill(c, (0.55, 0.38, 0.24))
    for k in range(14):
        P.potato_plant(c, -100 + k * 100, GY + 30 + (k % 2) * 30, 0.9, f.t)
    up = back(clamp(f.lt / 0.35), 2.5)
    y = lerp(GY + 260, GY - 100, up)
    soft_shadow(c, 560, GY + 280, 150, 26, 0.4)
    P.potato(c, 540, y, 3.2, wob(f.t, 0.6, 0.1))
    ellipse(c, 540, GY + 280, 200, 40)
    fill(c, (0.4, 0.26, 0.15))
    text3d(f, "POTATO", 540, 520, 190, f.lt - 0.15)
    vignette(f, 0.3)


# --------------------------------------------------------------------- 9.0 snap close-ups: Ugly. Dirty. Food for pigs.
@shot("Ugly.", whip=False)
def s_ugly(f):
    c = f.ctx
    f.cam(540, 760, 1.0 + f.lt * 0.05)
    P.sky(f, "#F7D7A8", "#F09A6A")
    C(c, "n1", 540, 1850, 3.9, expr="disgust", arms="down", t=f.t, look=(0.7, 0.4))
    P.potato(c, 860, 1500, 2.2, 0.4)
    text3d(f, "UGLY", 540, 300, 170, f.lt, top=(0.75, 0.95, 0.5), side=(0.25, 0.45, 0.15))


@shot("Dirty.", whip=False)
def s_dirty(f):
    c = f.ctx
    f.cam(540, 760, 1.0 + f.lt * 0.05)
    P.sky(f, "#C8E6B0", "#86B86A")
    C(c, "n4", 540, 1850, 3.9, expr="disgust", arms="whisper", t=f.t, look=(-0.5, 0.2))
    for k in range(5):
        x = 200 + k * 60 + wob(f.t, 1.2, 15, k * 0.2)
        c.move_to(x, 1450 - k * 40)
        c.curve_to(x + 30, 1400 - k * 40, x - 30, 1350 - k * 40, x, 1300 - k * 40)
        stroke(c, 7, (0.45, 0.6, 0.25))
    P.potato(c, 230, 1560, 2.0, -0.3)
    text3d(f, "DIRTY", 540, 300, 170, f.lt, top=(0.75, 0.55, 0.35), side=(0.4, 0.25, 0.12))


@shot("Food for", whip=False)
def s_pigs(f):
    c = f.ctx
    f.cam(540, 1000, 1.05)
    P.sky(f, "#FFE0B0", "#F5B880")
    P.ground(c, 1350, (0.62, 0.48, 0.32))
    P.fence(c, -100, 1200, 1350)
    pig(c, 330, 1600, 1.6, f.t)
    P.trough(c, 600, 1640, 1.2, n_pot=min(5, int(f.lt * 10)))
    C(c, "worker", 840, 1620, 1.4, expr="flat", arms="hold", t=f.t, fd=-1,
      hold=lambda c, hx, hy: P.basket(c, hx - 20, hy + 40, 0.8, 4))
    text3d(f, "FOOD FOR PIGS", 540, 330, 130, f.lt, top=(1.0, 0.7, 0.75), side=(0.6, 0.3, 0.35))


# --------------------------------------------------------------------- 12.0 orders, refused, free, pigs
@shot("He ordered")
def s_orders(f):
    c = f.ctx
    f.cam(lerp(520, 560, f.p), 1330, 1.18)
    outside(f, DAY, houses=[-200, 1000])
    P.board(c, 300, GY + 120, 420, 300, ["ROYAL ORDER:", "EAT", "POTATOES!"])
    C(c, "king", 760, GY + 230, 1.15, expr="angry" if f.at("They refused") < f.t else "determined", arms="point", look=(-1, 0), fd=-1, t=f.t)
    refused = f.t > f.at("refused")
    for k, (who, x) in enumerate((("n1", 120), ("n3", 400), ("n2", 640), ("farmer", 920))):
        C(c, who, x, GY + 470, 1.0, expr="disgust" if refused else "doubt", arms="cross" if refused else "down", t=f.t + k,
          look=(math.sin(f.t * 9) if refused else 0, 0))
    vignette(f, 0.35)


@shot("He gave")
def s_free(f):
    c = f.ctx
    f.cam(540, 1330, 1.18)
    outside(f, DAY, houses=[-220, 1020])
    P.table(c, 330, GY + 220, 420)
    for k in range(9):
        P.potato(c, 400 + (k % 5) * 70, GY - 20 - (k // 5) * 40, 0.75, k)
    P.board(c, 540, GY - 90, 300, 160, ["FREE!"], 0.8, col=(0.95, 0.75, 0.3))
    C(c, "king", 220, GY + 300, 1.0, expr="worried", arms="shrug", t=f.t)
    for k, who in enumerate(("n2", "n3", "kid")):
        x = 1300 - ((f.lt * 260 + k * 260) % 1700)
        C(c, who, x, GY + 470 + k * 15, 1.0, expr="flat", arms="down", legs="walk", fd=-1, t=f.t + k, look=(0, 0))
    vignette(f, 0.35)


@shot("They fed")
def s_fed(f):
    c = f.ctx
    f.cam(540, 1000, lerp(1.0, 1.1, f.p))
    P.sky(f, "#FFE0B0", "#F5B880")
    P.ground(c, 1350, (0.62, 0.48, 0.32))
    P.fence(c, -100, 1200, 1350)
    pig(c, 380, 1600, 1.4, f.t)
    pig(c, 120, 1700, 1.2, f.t + 1)
    P.trough(c, 640, 1660, 1.2, n_pot=6)
    C(c, "king", 900, 1640, 1.3, expr="sad", arms="down", t=f.t, fd=-1, look=(-1, 0.5))


# --------------------------------------------------------------------- 16.0 winter coming
@shot("So with")
def s_winter(f):
    c = f.ctx
    f.cam(540, 1050, lerp(1.0, 1.08, f.p))
    outside(f, GREY, houses=[60, 760], snowy=ease(f.lt / 1.2), t_sun=False)
    P.tree(c, 470, GY + 20, 1.1, (0.55, 0.6, 0.45))
    P.snow(f, f.t, int(40 + f.lt * 80))
    text3d(f, "WINTER", 540, 560, 190, f.lt - 0.3, top=(0.8, 0.92, 1.0), side=(0.35, 0.5, 0.75))
    vignette(f, 0.4)


@shot("the king tried")
def s_strange(f):
    c = f.ctx
    f.cam(540, 820, lerp(1.0, 1.12, f.p))
    P.sky(f, "#7A5BA8", "#E0A0C0")
    P.snow(f, f.t, 50)
    f.cam(540, 820, lerp(1.0, 1.12, f.p))
    C(c, "king", 540, 1850, 3.4, expr="sly" if f.lt < 0.6 else "smug", arms="chin", t=f.t, look=(0.7, -0.4))
    if f.lt > 0.7:
        a = pop(f.lt - 0.7)
        c.save()
        c.translate(850, 470)
        c.scale(a, a)
        c.arc(0, 0, 70, 0, 2 * math.pi)
        fs(c, (1, 0.93, 0.5), 8)
        glow(c, 0, 0, 160, (1, 0.9, 0.4), 0.5)
        rrect(c, -30, 60, 60, 40, 8)
        fs(c, (0.6, 0.6, 0.65), 6)
        c.restore()


# --------------------------------------------------------------------- 18.5 crane up over the palace wall to the field
@shot("He planted")
def s_crane(f):
    c = f.ctx
    k = ease(f.p)
    f.cam(540, lerp(800, 1300, k), lerp(1.2, 1.1, k))
    outside(f, DAY, palace=(540, GY - 60, 0.85), snowy=0.6)
    P.field(c, 140, 940, GY + 60, GY + 420, f.t, rows=4, grow=clamp(f.lt / 1.5))
    P.fence(c, 120, 960, GY + 470, 0.9)
    C(c, "king", 980, GY + 600, 1.0, expr="smug", arms="point", fd=-1, look=(-1, 0), t=f.t)
    P.snow(f, f.t, 30)


@shot("and put soldiers")
def s_march(f):
    c = f.ctx
    night = f.t > f.at("night.") - 0.15
    pal = NIGHT if night else (DUSK if f.t > f.at("Day") else DAY)
    f.cam(540, 1330, 1.15)
    outside(f, pal, palace=(540, GY - 60, 0.85), snowy=0.6)
    P.field(c, 140, 940, GY + 60, GY + 380, f.t, rows=4)
    for k in range(5):
        x = lerp(-300, 140 + k * 200, ease(f.lt / 1.6))
        C(c, "guard", x, GY + 520, 0.95, expr="determined", arms="hold", legs="march" if f.lt < 1.6 else "stand", fd=1, t=f.t + k * 0.1,
          hold=(lambda c, hx, hy: P.torch(c, hx, hy + 10, 0.9, f.t + hx, lit=night)))
    P.snow(f, f.t, 30)
    if night:
        vignette(f, 0.55)


# --------------------------------------------------------------------- 22.0 OTS: farmers whisper at the fence; a potato glints gold
@shot("And the farmers")
def s_whisper(f):
    c = f.ctx
    f.cam(lerp(560, 520, f.p), 1100, 1.0)
    outside(f, DUSK, palace=(700, GY - 60, 0.7), snowy=0.5)
    P.field(c, 300, 1100, GY + 40, GY + 300, f.t, rows=3)
    for k in range(3):
        C(c, "guard", 450 + k * 230, GY + 160, 0.6, expr="flat", arms="hold", t=f.t,
          hold=lambda c, hx, hy: P.torch(c, hx, hy + 10, 0.6, f.t + hx))
    P.fence(c, -200, 1300, GY + 520, 1.2)
    C(c, "farmer", 170, GY + 760, 1.6, expr="whisper", arms="whisper", fd=1, look=(1, 0), t=f.t)
    C(c, "n3", 470, GY + 800, 1.6, expr="surprise", arms="down", fd=-1, look=(-1, 0), t=f.t)


@shot("If the king")
def s_gold(f):
    c = f.ctx
    f.cam(540, 1000, lerp(1.0, 1.25, ease(f.p)))
    outside(f, DUSK, snowy=0.5)
    c.rectangle(-500, GY, 2200, 1200)
    fill(c, (0.5, 0.36, 0.24))
    for k in range(10):
        P.potato_plant(c, -100 + k * 140, GY + 40 + (k % 2) * 40, 1.3, f.t)
    g = clamp((f.t - f.at("gold...")) * 1.5)
    P.potato(c, 540, GY + 330, 2.6, 0.2, gold=g > 0.2)
    glow(c, 540, GY + 330, 300 * (0.3 + g), (1, 0.85, 0.3), 0.6 * g)
    for k in range(6):
        a = f.t * 2 + k
        sx, sy = 540 + math.cos(a) * 200, GY + 330 + math.sin(a * 1.3) * 120
        sz = 18 * g * (0.5 + 0.5 * math.sin(f.t * 8 + k))
        poly(c, [(sx, sy - sz * 2), (sx + sz * 0.5, sy), (sx, sy + sz * 2), (sx - sz * 0.5, sy)])
        fill(c, (1, 1, 0.8))
        poly(c, [(sx - sz * 2, sy), (sx, sy + sz * 0.5), (sx + sz * 2, sy), (sx, sy - sz * 0.5)])
        fill(c, (1, 1, 0.8))
    if f.t > f.at("maybe"):
        text3d(f, "GOLD?", 540, 560, 200, f.t - f.at("maybe"))


# --------------------------------------------------------------------- 26.0 ground-level tracking: the farmer tiptoes past
def night_field(f, camx, cy=1150, z=1.0):
    c = f.ctx
    f.cam(camx, cy, z)
    outside(f, NIGHT, snowy=0.4)
    P.field(c, -400, 1600, GY + 40, GY + 300, f.t, rows=3)


@shot("One night")
def s_tiptoe(f):
    c = f.ctx
    night_field(f, lerp(420, 640, f.p), 1450, 1.4)
    x = lerp(150, 900, f.p)
    C(c, "farmer", x, GY + 600, 1.15, expr="worried", arms="sneak", legs="tiptoe", fd=1, look=(1, 0), t=f.t)
    f.layer(1.6)
    C(c, "guard", -160, GY + 1150, 2.8, expr="flat", arms="hold", t=f.t, fd=1, look=(1, 0),
      hold=lambda c, hx, hy: P.torch(c, hx, hy + 10, 0.9, f.t))
    vignette(f, 0.55)


@shot("They didn't", whip=False)
def s_eyes(f):
    c = f.ctx
    f.cam(540, 800, 1.0)
    P.sky(f, NIGHT["top"], NIGHT["bot"], NIGHT["mid"])
    P.torch(c, 900, 1500, 2.2, f.t)
    lookx = -1 if f.lt < 0.25 else lerp(-1, 1, ease((f.lt - 0.25) / 0.4))
    C(c, "guard", 540, 1970, 4.6, expr="flat", arms="down", t=f.t, look=(lookx, 0))
    vignette(f, 0.55)


def sack_parade(f, n):
    c = f.ctx
    night_field(f, 540, 1560, 1.55)
    whos = ["farmer", "n3", "n1", "n2", "n4", "kid", "granny"][:n]
    for k, who in enumerate(whos):
        x = 1100 - ((f.lt * 300 + k * 170) % 1500)
        C(c, who, x, GY + 640 + (k % 2) * 60, 1.0, expr="happy" if k % 2 else "sly", arms="carry", legs="tiptoe", fd=-1, t=f.t + k * 0.3,
          hold=lambda c, hx, hy: P.sack(c, hx + 10, hy - 10, 0.75, 1.0))
    vignette(f, 0.55)


@shot("He came back")
def s_sack1(f):
    sack_parade(f, 1)


@shot("Then his", whip=False)
def s_sack2(f):
    sack_parade(f, 2)


@shot("Then the whole", whip=False)
def s_sack3(f):
    sack_parade(f, 7)


# --------------------------------------------------------------------- 35.0 Look the other way
@shot("The soldiers saw")
def s_saw(f):
    c = f.ctx
    f.cam(540, 1360, lerp(1.2, 1.26, f.p))
    outside(f, NIGHT, palace=(540, GY - 60, 0.8), snowy=0.4)
    for k in range(4):
        C(c, "guard", 150 + k * 260, GY + 250, 0.9, expr="flat", arms="hold", t=f.t, look=(math.sin(f.t * 2), 0.3),
          hold=lambda c, hx, hy: P.torch(c, hx, hy + 10, 0.8, f.t + hx))
    for k, who in enumerate(("n1", "n2", "farmer")):
        x = 1200 - ((f.lt * 320 + k * 260) % 1600)
        C(c, who, x, GY + 560, 0.95, expr="sly", arms="carry", legs="tiptoe", fd=-1, t=f.t + k,
          hold=lambda c, hx, hy: P.sack(c, hx + 10, hy - 10, 0.75))
    vignette(f, 0.5)


@shot("Their orders")
def s_scroll(f):
    c = f.ctx
    f.cam(540, 960, lerp(1.0, 1.08, f.p))
    P.sky(f, "#3A2A5A", "#6A4A7A")
    c.save()
    c.translate(540, 960)
    c.rotate(-0.04)
    rrect(c, -380, -520, 760, 1040, 30)
    fs(c, (0.97, 0.9, 0.72), 9)
    for yy in (-540, 520):
        rrect(c, -420, yy - 30, 840, 60, 30)
        fs(c, (0.85, 0.72, 0.5), 8)
    label(c, "ROYAL ORDERS", 0, -380, 74, (0.45, 0.15, 0.2), "Lilita One", cairo.FONT_WEIGHT_NORMAL)
    for k in range(3):
        c.move_to(-280, -260 + k * 50)
        c.line_to(280, -260 + k * 50)
        stroke(c, 5, (0.7, 0.6, 0.45))
    rv = clamp((f.t - f.at("Look")) / 0.7)
    chalk_text(c, "LOOK THE", 0, 0, 110, (0.15, 0.1, 0.2), reveal=rv * 2)
    chalk_text(c, "OTHER WAY", 0, 150, 110, (0.15, 0.1, 0.2), reveal=rv * 2 - 1)
    c.arc(220, 360, 80, 0, 2 * math.pi)
    fs(c, (0.8, 0.15, 0.2), 7)
    label(c, "K", 220, 360, 80, (1, 0.85, 0.85), "Lilita One", cairo.FONT_WEIGHT_NORMAL)
    c.restore()
    vignette(f, 0.4)


@shot("Look the", whip=True)
def s_turn(f):
    c = f.ctx
    f.cam(540, lerp(1250, 1180, f.p), lerp(1.15, 1.08, f.p))
    outside(f, NIGHT, palace=(540, GY - 60, 0.8), snowy=0.4)
    f.layer(0.6)
    C(c, "king", 540, GY - 330, 0.42, expr="happy", arms="wave", t=f.t)
    f.layer(1.0)
    turned = f.lt > 0.25
    for k in range(5):
        C(c, "guard", 100 + k * 220, GY + 320 + (k % 2) * 40, 0.95, expr="happy" if turned else "flat", arms="cross" if turned else "hold",
          t=f.t, fd=-1 if turned else 0, look=(-1, -0.5) if turned else (0, 0),
          hold=None if turned else (lambda c, hx, hy: P.torch(c, hx, hy + 10, 0.8, f.t + hx)))
    vignette(f, 0.5)


# --------------------------------------------------------------------- 40.0 top-down time-lapse: secret gardens
@shot("By spring")
def s_gardens(f):
    c = f.ctx
    f.cam(540, 960, lerp(1.15, 0.9, ease(f.p)))
    screen_fill(f, (0.52, 0.76, 0.36))
    f.cam(540, 960, lerp(1.15, 0.9, ease(f.p)))
    for gy in range(5):
        for gx in range(3):
            x0, y0 = -60 + gx * 420, 120 + gy * 400
            idx = gy * 3 + gx
            # roof (top-down)
            rrect(c, x0, y0, 220, 170, 14)
            fs(c, [(0.85, 0.35, 0.25), (0.35, 0.45, 0.8), (0.9, 0.7, 0.3)][idx % 3], 7)
            c.move_to(x0, y0 + 85)
            c.line_to(x0 + 220, y0 + 85)
            stroke(c, 5, (0.2, 0.1, 0.1), 0.5)
            # garden patch
            rrect(c, x0 + 240, y0 - 10, 150, 200, 10)
            fs(c, (0.55, 0.38, 0.24), 6)
            grow = clamp(f.lt * 1.2 - idx * 0.12)
            for py in range(3):
                for px in range(2):
                    P.potato_plant(c, x0 + 280 + px * 70, y0 + 50 + py * 60, 0.45, f.t, grow)


@shot("And by winter")
def s_festival(f):
    c = f.ctx
    f.cam(540, 1250, lerp(1.1, 1.16, f.p))
    outside(f, DAY, palace=(540, GY - 60, 0.8), snowy=0.7, t_sun=True)
    P.bunting(c, -100, 1180, 500, f.t)
    P.table(c, 260, GY + 300, 560)
    for k in range(7):
        P.potato(c, 330 + k * 70, GY + 125 - (k % 2) * 10, 0.7, k, gold=k == 3)
    C(c, "king", 540, GY + 120, 0.9, expr="laugh", arms="cheer", t=f.t)
    C(c, "kid", 230, GY + 560, 1.2, expr="happy", arms="eat", t=f.t,
      hold=lambda c, hx, hy: P.potato(c, hx, hy, 0.5, 0.3))
    C(c, "granny", 820, GY + 560, 1.15, expr="happy", arms="eat", fd=-1, t=f.t + 0.4,
      hold=lambda c, hx, hy: P.potato(c, hx, hy, 0.5, -0.3))
    P.snow(f, f.t, 25)


# --------------------------------------------------------------------- 52.0 slow push-in on the potato on a velvet cushion
@shot("Because")
def s_final(f):
    c = f.ctx
    k = ease(f.p)
    f.cam(540, 1060, lerp(0.95, 1.3, k))
    P.sky(f, "#2A1240", "#7A2850", "#4A1A50")
    f.cam(540, 1060, lerp(0.95, 1.3, k))
    glow(c, 540, 1050, 600, (1, 0.8, 0.4), 0.35)
    # pedestal
    P.box3d(c, 330, 1500, 420, 300, 40, (0.85, 0.75, 0.6))
    P.cushion(c, 560, 1170, 1.0)
    P.potato(c, 560, 1100, 2.0, 0.1, gold=True)
    for k2 in range(5):
        a = f.t * 1.5 + k2 * 1.3
        sx, sy = 560 + math.cos(a) * 240, 1060 + math.sin(a) * 80
        c.arc(sx, sy, 6 + 3 * math.sin(f.t * 6 + k2), 0, 2 * math.pi)
        fill(c, (1, 1, 0.8), 0.8)
    # velvet rope
    for px in (220, 900):
        rrect(c, px - 12, 1380, 24, 260, 8)
        fs(c, GOLD, 5)
    c.move_to(220, 1400)
    c.curve_to(400, 1520, 720, 1520, 900, 1400)
    stroke(c, 18, (0.75, 0.1, 0.2))
    f.screen()
    t_title = f.t - f.at("can't")
    if t_title > -0.0:
        text3d(f, "FORBID IT", 540, 430, 190, t_title)
    vignette(f, 0.5)


# --------------------------------------------------------------------- sound
sfx(0.15, "hit", 0.8)
sfx(0.1, "wind", 0.5)
sfx("secretly", "sting", 0.6)
sfx("You see", "wind", 0.7)
sfx("Potatoes.", "pop", 1.0)
sfx("Ugly.", "sting_low", 0.7)
sfx("Dirty.", "sting_low", 0.7)
sfx("Food for", "sting_low", 0.7)
sfx("refused.", "boing", 0.7)
sfx(story.at("pigs.", 2), "gulp")
sfx("winter coming", "riser", 0.8)
sfx("strange.", "ting", 0.8)
sfx("and put soldiers", "drums", 0.8)
sfx("gold...", "shimmer", 1.0)
sfx("maybe", "pop", 0.8)
sfx("One night", "tiptoe", 0.9)
sfx("didn't", "boing", 0.9)
sfx("sack.", "hit", 0.6)
sfx("neighbor", "hit", 0.6)
sfx("village.", "hit", 0.7)
sfx("Look the", "braam", 0.9)
sfx("By spring", "bells", 0.8)
sfx("by winter", "pizz_up", 0.8)
sfx("can't", "final", 1.0)
