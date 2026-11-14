"""Story 2: Why Coins Have Ridges - shot list (pack section 9)."""
import math, os, random
from engine import *
import cast, props as P
from cast import draw as C

ROOT = os.path.dirname(HERE)
story = Story("coin_ridges", ROOT)
shot, sfx = story.shot, story.add_sfx

DESK_WALL = (0.42, 0.28, 0.2)
MODERN = dict(body="kid", outfit="tunic", tunic=(70, 160, 220), trim=(250, 250, 250), hat="hair", hatc=(60, 40, 30), face="kid", iris=(60, 110, 200))


def desk_room(f, cx=540, cy=960, z=1.0):
    c = f.ctx
    f.cam(cx, cy, z)
    P.interior(c, DESK_WALL, (0.3, 0.2, 0.15), fy=1350)
    P.window_night(c, 640, 380, 300, 340, f.t)
    glow(c, 300, 1100, 700, (1, 0.7, 0.35), 0.25)


def desk(f, y=1450):
    c = f.ctx
    c.rectangle(-600, y, 2300, 900)
    fill(c, (0.5, 0.32, 0.2))
    c.move_to(-600, y)
    c.line_to(1700, y)
    stroke(c, 8)
    for k in range(-6, 20):
        c.move_to(k * 120, y + 10)
        c.line_to(k * 120 + 60, y + 900)
        stroke(c, 3, (0.4, 0.25, 0.15))


def market(f, cx=540, cy=1100, z=1.0, pal=("#9AD0F0", "#FFF0D0"), chaos=0.0):
    c = f.ctx
    P.sky(f, pal[0], pal[1])
    f.cam(cx, cy, z)
    f.layer(0.3)
    P.hills(c, 1050, (0.5, 0.7, 0.42), 3, amp=110)
    f.layer(0.6)
    for hx, col in ((-260, (0.95, 0.85, 0.65)), (100, (0.9, 0.78, 0.7)), (700, (0.85, 0.88, 0.7)), (1050, (0.95, 0.85, 0.65))):
        P.house(c, hx, 1160, 240, 200, wall=col)
    f.layer(1.0)
    P.ground(c, 1250, (0.78, 0.68, 0.5))


# --------------------------------------------------------------------- 0.0 macro: coin edge rotating, rack focus to the merchant
@shot(0.0)
def s_macro(f):
    c = f.ctx
    P.sky(f, "#20142E", "#4A2E44")
    f.cam(540, 960, lerp(1.25, 1.0, ease(f.p)))
    glow(c, 540, 900, 700, (1, 0.75, 0.4), 0.25)
    rack = ease((f.lt - 1.6) / 0.8)
    if rack > 0:
        c.push_group()
        C(c, "merchant", 540, 1900, 2.6, expr="smug", arms="snip", t=f.t, look=(0.3, 0),
          hold=lambda c, hx, hy: P.scissors(c, hx, hy, 0.7, 0.3 + 0.3 * abs(math.sin(f.t * 5)), -0.4))
        c.pop_group_to_source()
        c.paint_with_alpha(rack)
    a = 1 - 0.7 * rack
    c.push_group()
    P.coin_edge(c, 540, 960 - rack * 500, 470 * (1 - 0.5 * rack), 220 * (1 - 0.5 * rack), f.t)
    c.pop_group_to_source()
    c.paint_with_alpha(a)
    vignette(f, 0.5)


@shot("one greedy")
def s_greedy(f):
    c = f.ctx
    desk_room(f, 540, 900, lerp(1.0, 1.08, f.p))
    P.candle(c, 180, 1450, 1.2, f.t)
    C(c, "merchant", 560, 1830, 3.0, expr="smug", arms="hips", t=f.t, look=(0.5, 0))
    desk(f, 1550)
    for k in range(6):
        P.coin(c, 760 + (k % 3) * 70, 1600 - (k // 3) * 22, 45, squash=0.45)
    vignette(f, 0.5)


@shot("and a pair")
def s_scissors(f):
    c = f.ctx
    P.sky(f, "#5A2A40", "#2A1428")
    f.cam(540, 960, 1.0 + f.lt * 0.06)
    glow(c, 540, 960, 600, (1, 0.8, 0.5), 0.35)
    snaps = [f.at("scissors.") + 0.05, f.at("scissors.") + 0.35]
    op = 0.6
    for st in snaps:
        if f.t >= st:
            op = 0.05 if f.t - st < 0.12 else 0.6
    P.scissors(c, 520, 960, 3.2, op, -0.3)
    vignette(f, 0.5)


# --------------------------------------------------------------------- 5.0 hundreds of years ago: real silver
@shot("You see")
def s_long_ago(f):
    c = f.ctx
    market(f, lerp(500, 580, f.p), 1250, 1.15)
    P.stall(c, 320, 1500, 1.0, goods=[(0.9, 0.3, 0.2), (1, 0.7, 0.2), (0.4, 0.75, 0.3)])
    C(c, "vendor", 330, 1480, 0.75, expr="smile", arms="count", t=f.t,
      hold=lambda c, hx, hy: P.coin(c, hx, hy - 20, 22))
    C(c, "customer", 760, 1760, 1.15, expr="smile", arms="count", fd=-1, t=f.t,
      hold=lambda c, hx, hy: P.coin(c, hx, hy - 25, 26))
    C(c, "n2", 960, 1720, 1.05, expr="smile", arms="down", fd=-1, t=f.t + 1)
    text3d(f, "LONG AGO", 540, 400, 170, f.lt - 0.2, top=(0.95, 0.85, 0.65), side=(0.5, 0.35, 0.2))
    vignette(f, 0.35)


@shot("A coin was")
def s_scales(f):
    c = f.ctx
    P.sky(f, "#F6E7C8", "#E8C99A")
    f.cam(540, 960, lerp(1.0, 1.08, f.p))
    glow(c, 540, 900, 600, (1, 1, 0.9), 0.4)
    tilt = 0.25 * math.cos(f.lt * 3) * math.exp(-f.lt * 1.0)
    def nugget(c, x, y):
        poly(c, [(x - 50, y), (x - 40, y - 45), (x - 5, y - 65), (x + 40, y - 40), (x + 50, y)])
        fs(c, P.SILVER, 6)
        poly(c, [(x - 30, y - 35), (x - 5, y - 52), (x + 10, y - 40)])
        fill(c, (1, 1, 1), 0.5)
    P.scales(c, 540, 1450, 2.0, tilt,
             left=lambda c, x, y: P.coin(c, x, y - 40, 48),
             right=nugget)
    if f.t > f.at("inside"):
        text3d(f, "COIN = METAL", 540, 380, 140, f.t - f.at("inside"), top=(0.9, 0.92, 0.98), side=(0.4, 0.42, 0.5))


# --------------------------------------------------------------------- 10.0 the merchant's trick
@shot("So a merchant")
def s_merchant(f):
    c = f.ctx
    desk_room(f, 540, 1000, 1.05)
    P.candle(c, 220, 1460, 1.1, f.t)
    C(c, "merchant", 600, 1760, 2.4, expr="sly" if f.lt < 0.8 else "smug", arms="chin", t=f.t, look=(-0.7, 0.3))
    desk(f, 1500)
    for k in range(9):
        P.coin(c, 120 + (k % 5) * 90, 1560 + (k // 5) * 40, 40, squash=0.45)
    vignette(f, 0.5)


@shot("From every")
def s_snip(f):
    c = f.ctx
    desk_room(f, 540, 1100, 1.25)
    P.candle(c, 860, 1440, 1.0, f.t)
    desk(f, 1480)
    # over-the-shoulder: merchant's shoulder in the foreground, coin + scissors on the desk
    snip_t = f.at("trimmed")
    cut = clamp((f.t - snip_t) / 0.3)
    P.coin(c, 540, 1300, 170, clipped=0.6 * cut)
    op = 0.7 if f.t < snip_t else (0.05 if f.t - snip_t < 0.15 else 0.6)
    P.scissors(c, 760, 1180 + 30 * cut, 1.4, op, 2.6)
    if cut > 0:
        dt = f.t - snip_t
        sy = 1180 + min(dt * 90, 330)
        c.save()
        c.translate(700 + dt * 15, sy)
        c.rotate(dt * 1.2)
        c.arc(0, 0, 60, -0.5, 0.5)
        c.arc_negative(-8, 0, 56, 0.45, -0.45)
        c.close_path()
        fs(c, P.SILVER, 4)
        c.restore()
        glow(c, 700, sy, 80, (1, 1, 1), 0.4 * (1 - clamp(dt / 2)))
    f.layer(1.5)
    C(c, "merchant", -60, 2350, 3.2, expr="sly", arms="down", t=f.t, fd=1, look=(1, 0.5), shadow=False)
    vignette(f, 0.5)


@shot("Too small")
def s_customer(f):
    c = f.ctx
    market(f, 540, 1000, 1.0)
    C(c, "customer", 640, 1900, 2.8, expr="happy", arms="count", t=f.t, fd=-1,
      hold=lambda c, hx, hy: P.coin(c, hx, hy - 50, 50, clipped=0.6))
    f.layer(1.3)
    C(c, "merchant", 60, 2200, 2.4, expr="smug", arms="down", t=f.t, fd=1, look=(1, 0))
    vignette(f, 0.35)


# --------------------------------------------------------------------- 16.0 one sliver / a thousand slivers / melted
def sliver(c, x, y, s, rot):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(s, s)
    c.arc(0, 0, 60, -0.5, 0.5)
    c.arc_negative(-8, 0, 56, 0.45, -0.45)
    c.close_path()
    fs(c, P.SILVER, 4)
    c.restore()


@shot("One sliver")
def s_one(f):
    c = f.ctx
    P.sky(f, "#3A2430", "#1E1218")
    f.cam(540, 1000, lerp(1.4, 1.2, ease(f.p)))
    desk(f, 900)
    sliver(c, 540, 1150, 2.6, 0.3)
    glow(c, 540, 1150, 120, (1, 1, 1), 0.3)
    text3d(f, "1", 540, 650, 260, f.lt - 0.1, top=(0.9, 0.92, 0.98), side=(0.4, 0.42, 0.5))


@shot("A thousand")
def s_pile(f):
    c = f.ctx
    P.sky(f, "#3A2430", "#1E1218")
    f.cam(540, 1050, lerp(1.0, 0.9, f.p))
    desk(f, 600)
    rnd = random.Random(2)
    n = int(30 + 500 * ease(f.lt / 1.0))
    for k in range(n):
        r = rnd.random() ** 0.5 * 360
        a = rnd.random() * 6.28
        sliver(c, 540 + math.cos(a) * r, 1150 + math.sin(a) * r * 0.7, 0.55, rnd.random() * 6)
    text3d(f, "1,000", 540, 500, 230, f.lt - 0.1, top=(0.9, 0.92, 0.98), side=(0.4, 0.42, 0.5))


@shot("He melted")
def s_melt(f):
    c = f.ctx
    P.sky(f, "#2A1418", "#5A2418")
    f.cam(560, 1380, lerp(1.35, 1.45, f.p))
    m = clamp((f.t - f.at("bar")) / 0.7)
    P.crucible(c, 360, 1500, 1.3, 1.0, f.t)
    # pour stream
    if 0 < m < 1:
        c.move_to(450, 1300)
        c.curve_to(560, 1260, 620, 1340, 640, 1450)
        stroke(c, 22, (1, 0.7, 0.25))
    P.silver_bar(c, 760, 1560, 1.3 * (0.3 + 0.7 * m), hot=1 - clamp((f.t - f.at("silver.", 2)) / 0.8) * 0.9)
    if f.t > f.at("solid"):
        text3d(f, "SOLID SILVER", 540, 600, 150, f.t - f.at("solid"), top=(0.92, 0.94, 1.0), side=(0.4, 0.42, 0.5))
    vignette(f, 0.5)


# --------------------------------------------------------------------- 21.0 everyone clips; coins shrink
@shot("Soon")
def s_everyone(f):
    c = f.ctx
    P.sky(f, "#E8C2A0", "#B07A70")
    f.cam(540, 1000, 1.05)
    for k, who in enumerate(("vendor", "n3", "farmer")):
        y = 700 + k * 420
        rrect(c, 60, y - 200, 960, 400, 30)
        fs(c, [(0.95, 0.85, 0.7), (0.85, 0.9, 0.78), (0.8, 0.85, 0.95)][k], 8)
        c.save()
        rrect(c, 60, y - 200, 960, 400, 30)
        c.clip()
        appear = f.lt > k * 0.35
        if appear:
            C(c, who, 300, y + 330, 1.2, expr="sly", arms="snip", t=f.t + k,
              hold=lambda c, hx, hy: P.scissors(c, hx, hy, 0.45, 0.2 + 0.4 * abs(math.sin(f.t * 6 + k)), -0.5))
            P.coin(c, 720, y, 120, clipped=0.4 + 0.2 * k)
        c.restore()
        rrect(c, 60, y - 200, 960, 400, 30)
        stroke(c, 8)


@shot("Coins shrank", whip=False)
def s_shrink(f):
    c = f.ctx
    P.sky(f, "#3A2440", "#7A4A60")
    f.cam(540, 960, 1.0)
    k = ease(f.lt / 1.2)
    for r in (420, 360):
        c.arc(540, 960, r, 0, 2 * math.pi)
        c.set_dash([18, 14])
        stroke(c, 5, (1, 1, 1), 0.4)
    c.set_dash([])
    P.coin(c, 540, 960, lerp(420, 250, k), clipped=k)
    text3d(f, "SHRINKING", 540, 330, 150, f.lt - 0.1, top=(1, 0.6, 0.55), side=(0.5, 0.2, 0.2))


@shot("Shopkeepers")
def s_weigh(f):
    c = f.ctx
    market(f, 540, 1300, 1.2)
    tilt = 0.18 * math.sin(f.t * 3)
    P.scales(c, 300, 1560, 1.0, tilt, left=lambda c, x, y: P.coin(c, x, y - 25, 30, clipped=0.6))
    C(c, "vendor", 470, 1700, 1.25, expr="angry", arms="hips", fd=-1, t=f.t, look=(-1, 0))
    for k, who in enumerate(("n1", "n2", "customer", "n3")):
        C(c, who, 700 + k * 150, 1780 + (k % 2) * 30, 1.0, expr="angry" if k % 2 else "worried", arms="cross" if k % 2 else "hips", fd=-1, t=f.t + k)
    vignette(f, 0.4)


@shot("and the whole")
def s_chaos(f):
    c = f.ctx
    market(f, 540 + math.sin(f.t * 30) * 4, 1150, 1.05, pal=("#6A5A8A", "#C89A90"))
    f.layer(0.6)
    # king worried at a window
    rrect(c, 380, 700, 300, 260, 20)
    fs(c, (0.95, 0.88, 0.75), 8)
    c.save()
    rrect(c, 410, 730, 240, 200, 10)
    c.clip()
    fill(c, (0.3, 0.25, 0.4))
    rrect(c, 410, 730, 240, 200, 10)
    c.clip()
    C(c, "king", 530, 1180, 0.9, expr="worried", arms="down", t=f.t, shadow=False)
    c.restore()
    rrect(c, 410, 730, 240, 200, 10)
    stroke(c, 7)
    f.layer(1.0)
    for k, who in enumerate(("n1", "n2", "vendor", "customer", "n3", "farmer")):
        x = (k * 210 + f.lt * (200 if k % 2 else -200)) % 1400 - 160
        C(c, who, x, 1600 + (k % 3) * 70, 1.0, expr=["angry", "worried", "shock"][k % 3], arms=["wag", "up", "shrug"][k % 3],
          legs="run", fd=1 if k % 2 else -1, t=f.t + k)
    vignette(f, 0.55)


# --------------------------------------------------------------------- 32.0 the mint changes one thing
def mint_room(f, z=1.0, cy=960, shake=0.0):
    c = f.ctx
    f.cam(540, cy, z, shake=shake)
    P.interior(c, (0.45, 0.42, 0.45), (0.35, 0.32, 0.32), fy=1450, planks=False)
    for k in range(-3, 6):
        for r in range(8):
            rrect(c, k * 260 + (r % 2) * 130, 200 + r * 150, 250, 140, 6)
            stroke(c, 3, (0.35, 0.33, 0.36))


@shot("So the mint")
def s_press(f):
    c = f.ctx
    slam = f.at("thing.")
    press = 0 if f.t < slam - 0.25 else ease_in(clamp((f.t - slam + 0.25) / 0.25))
    mint_room(f, 1.3, 1250, shake=14 * max(0, 1 - (f.t - slam) * 4) if f.t > slam else 0)
    P.coin_press(c, 540, 1650, 1.2, press)
    C(c, "minter", 900, 1750, 1.1, expr="determined", arms="hammer" if f.t < slam else "cheer", fd=-1, t=f.t)
    if f.t > slam:
        glow(c, 540, 1500, 300, (1, 1, 0.9), 0.6 * max(0, 1 - (f.t - slam) * 2))
    vignette(f, 0.45)


@shot("Every new")
def s_ridges_form(f):
    c = f.ctx
    P.sky(f, "#2A3050", "#5A6A90")
    f.cam(540, 960, lerp(1.0, 1.15, ease(f.p)))
    glow(c, 540, 960, 600, (1, 1, 1), 0.2)
    k = clamp((f.t - f.at("ridges", 2)) / 1.0)
    P.coin_edge(c, 540, 960, 430, 230, f.t * 0.6, ridged=k > 0)
    if 0 < k < 1:
        # sweep line revealing ridges
        c.rectangle(lerp(-430, 430, k) + 540, 840, 600, 240)
        P_col = (0.8, 0.82, 0.86)
        fill(c, P_col)
    text3d(f, "RIDGES", 540, 420, 190, f.t - f.at("ridges", 2), top=(0.92, 0.94, 1.0), side=(0.4, 0.42, 0.5))


@shot("Shave a")
def s_split(f):
    c = f.ctx
    P.sky(f, "#F3E6D0", "#E0C8A8")
    f.cam(540, 960, 1.0)
    c.rectangle(540, 0, 540, 1920)
    fill(c, (0.88, 0.8, 0.7))
    c.move_to(540, 0)
    c.line_to(540, 1920)
    stroke(c, 10)
    P.coin_edge(c, 270, 960, 210, 150, f.t)
    shaved = clamp((f.t - f.at("disappear.")) / 0.4)
    c.push_group()
    P.coin_edge(c, 810, 960, 210, 150, f.t, ridged=shaved < 0.5)
    c.pop_group_to_source()
    c.paint()
    label(c, "RIDGED", 270, 760, 60, INK, "Lilita One", cairo.FONT_WEIGHT_NORMAL)
    label(c, "SHAVED", 810, 760, 60, INK, "Lilita One", cairo.FONT_WEIGHT_NORMAL)
    if f.t > f.at("disappear."):
        P.red_x(c, 810, 960, 1.1, pop(f.t - f.at("disappear.")))
        P.check(c, 270, 960 + 230, 0.7)
    if f.t > f.at("Everyone", 2):
        for k, who in enumerate(("vendor", "n2", "customer")):
            C(c, who, 220 + k * 320, 1850, 1.2, expr="angry" if k != 1 else "surprise", arms="point", fd=1, look=(1, 0), t=f.t + k)


# --------------------------------------------------------------------- 41.0 who ran the mint? undercover in taverns
@shot("And the man")
def s_who(f):
    c = f.ctx
    mint_room(f, lerp(1.0, 1.12, f.p), 1100)
    rrect(c, 380, 950, 320, 500, 160)
    fill(c, (0.12, 0.1, 0.14))
    c.push_group()
    C(c, "newton", 540, 1450, 1.25, t=f.t, shadow=False, expr="flat")
    pat = c.pop_group()
    c.set_source_rgb(0.05, 0.04, 0.08)
    c.mask(pat)
    for ex in (515, 565):
        c.arc(ex, 1450 + cast.head_y("newton", 1.25), 7, 0, 2 * math.pi)
        fill(c, (1, 0.95, 0.6))
    text3d(f, "?", 540, 750, 300, f.lt - 0.3, top=(1, 0.85, 0.3))
    vignette(f, 0.55)


def tavern(f, cx=540, cy=1000, z=1.0):
    c = f.ctx
    f.cam(cx, cy, z)
    P.interior(c, (0.5, 0.32, 0.2), (0.35, 0.22, 0.15), fy=1400)
    for k in range(-2, 5):
        c.rectangle(k * 420, 0, 40, 1400)
        fs(c, (0.35, 0.22, 0.14), 6)
    c.rectangle(-600, 120, 2400, 50)
    fs(c, (0.35, 0.22, 0.14), 6)
    for lx in (150, 900):
        P.lamp(c, lx, 400, 1.0, f.t)
    P.barrel(c, 960, 1420, 1.2)
    P.barrel(c, 820, 1440, 1.0)


@shot("who went")
def s_tavern(f):
    c = f.ctx
    tavern(f, lerp(520, 580, f.p), 1420, 1.35)
    P.table(c, 160, 1750, 480)
    C(c, "merchant", 260, 1700, 1.2, expr="sly", arms="count", fd=1, t=f.t, look=(1, 0),
      hold=lambda c, hx, hy: P.coin(c, hx, hy - 20, 22, clipped=0.6))
    C(c, "n3", 500, 1700, 1.2, expr="happy", arms="down", fd=-1, t=f.t)
    P.mug(c, 300, 1594, 0.9)
    P.mug(c, 470, 1594, 0.9)
    # hooded listener with a fake moustache
    lean = 0.08 + 0.04 * math.sin(f.t * 2)
    C(c, "newton_hood", 860, 1900, 1.45, expr="sly", arms="chin", fd=-1, t=f.t, look=(-1, 0), lean=-lean)
    vignette(f, 0.55)


@shot("Isaac")
def s_reveal(f):
    c = f.ctx
    tavern(f, 540, 1000, lerp(1.0, 1.1, f.p))
    off = f.lt > 0.15
    C(c, "newton" if off else "newton_hood", 540, 1900, 2.2, expr="surprise" if f.lt < 0.6 else "smug", arms="up" if f.lt < 0.4 else "hips", t=f.t)
    # apple bonk
    ta = f.lt - 0.3
    if ta > 0:
        hy = 1900 + cast.head_y("newton", 2.2) - 64 * 2.2
        if ta < 0.25:
            P.apple(c, 600, lerp(-100, hy - 30, ta / 0.25), 1.4, ta * 4)
        else:
            tb = ta - 0.25
            P.apple(c, 600 + tb * 500, hy - 30 - 300 * tb + 900 * tb * tb, 1.4, ta * 4)
            for k in range(4):
                a = f.t * 5 + k * 1.57
                poly(c, [(560 + math.cos(a) * 120, hy - 80 + math.sin(a) * 30 - 10), (570 + math.cos(a) * 120, hy - 80 + math.sin(a) * 30),
                         (560 + math.cos(a) * 120, hy - 80 + math.sin(a) * 30 + 10), (550 + math.cos(a) * 120, hy - 80 + math.sin(a) * 30)])
                fill(c, (1, 0.9, 0.3))
    flash(f, 0.8 * (1 - clamp(f.lt / 0.25)))
    text3d(f, "ISAAC\nNEWTON", 540, 380, 170, f.lt - 0.1)


@shot("Yes.", whip=False)
def s_shock(f):
    c = f.ctx
    tavern(f, 540, 1400, 1.35)
    frz = f.lt > 0.15
    for k, who in enumerate(("merchant", "n3", "vendor", "customer")):
        C(c, who, 180 + k * 240, 1800 + (k % 2) * 40, 1.25, expr="shock", arms="up", t=0 if frz else f.t, look=(0, 0))
    if frz:
        f.screen()
        c.rectangle(0, 0, W, H)
        fill(c, (0.9, 0.85, 1.0), 0.12)


# --------------------------------------------------------------------- 49.0 300 years later
@shot("Three hundred")
def s_later(f):
    c = f.ctx
    P.sky(f, "#8FD0F5", "#E8F6FF")
    f.cam(540, 1250, 1.15)
    f.layer(0.5)
    for k, (bx, bh, col) in enumerate(((-200, 700, (0.75, 0.82, 0.9)), (150, 900, (0.85, 0.8, 0.75)), (520, 620, (0.7, 0.78, 0.85)), (860, 820, (0.9, 0.85, 0.8)))):
        P.box3d(c, bx, 1250, 300, bh, 40, col)
        for r in range(int(bh / 120)):
            for q in range(3):
                c.rectangle(bx + 30 + q * 90, 1250 - bh + 40 + r * 120, 60, 70)
                fs(c, (0.55, 0.75, 0.95), 4)
    f.layer(1.0)
    P.ground(c, 1250, (0.7, 0.72, 0.75))
    c.rectangle(-1000, 1330, 3000, 20)
    fill(c, (1, 1, 1), 0.7)
    flip = f.t - f.at("coins", 4)
    hy = 1700 + cast.head_y(MODERN, 1.5)
    C(c, MODERN, 540, 1700, 1.5, expr="happy", arms="count", t=f.t,
      hold=(lambda c, hx, hy2: P.coin(c, hx, hy2 - 30 - max(0, math.sin(min(flip, 1.0) * math.pi)) * 500, 26, squash=abs(math.cos(f.t * 12)) + 0.05,
                                     col=(0.85, 0.75, 0.55), face="head")))
    text3d(f, "300 YEARS\nLATER", 540, 450, 140, f.lt - 0.1, top=(1, 1, 1), side=(0.3, 0.5, 0.75))


@shot("aren't")
def s_not_silver(f):
    c = f.ctx
    P.sky(f, "#FFE9C8", "#F5C890")
    f.cam(540, 960, 1.0)
    P.coin(c, 540, 1000, 330, col=(0.82, 0.72, 0.52), face="head")
    if f.t > f.at("anymore.", 2):
        P.red_x(c, 540, 1000, 1.6, pop(f.t - f.at("anymore.", 2)))
    text3d(f, "NOT SILVER", 540, 420, 160, f.lt - 0.4, top=(0.82, 0.72, 0.52), side=(0.45, 0.35, 0.2))


@shot("But they")
def s_still(f):
    c = f.ctx
    P.sky(f, "#20142E", "#4A2E44")
    k = ease(f.p)
    f.cam(540, 960, lerp(0.9, 1.15, k))
    glow(c, 540, 1000, 700, (1, 0.8, 0.5), 0.3)
    P.coin_edge(c, 540, 1050, 420, 220, f.t * 0.7, col=(0.82, 0.72, 0.52))
    f.screen()
    if f.t > f.at("ridges.", 4) - 0.2:
        text3d(f, "STILL\nRIDGED", 540, 470, 190, f.t - f.at("ridges.", 4) + 0.2)
    vignette(f, 0.5)


# --------------------------------------------------------------------- sound
sfx(0.1, "coin", 1.0)
sfx("greedy", "sting_low", 0.6)
sfx(story.at("scissors.") + 0.05, "snip", 1.0)
sfx(story.at("scissors.") + 0.35, "snip", 1.0)
sfx("You see", "pizz_up", 0.6)
sfx("worth", "ting", 0.8)
sfx("tried something", "tiptoe", 0.6)
sfx("trimmed", "snip", 1.0)
sfx(story.at("trimmed") + 0.5, "snip", 0.8)
sfx(story.at("trimmed") + 1.0, "snip", 0.8)
sfx("One sliver", "ting", 0.8)
sfx("thousand", "riser", 0.6)
sfx("melted", "sizzle", 0.9)
sfx("solid", "braam", 0.8)
sfx("everyone was", "snip", 0.7)
sfx(story.at("everyone was") + 0.35, "snip", 0.7)
sfx(story.at("everyone was") + 0.7, "snip", 0.7)
sfx("shrank.", "boing", 0.6)
sfx("Shopkeepers", "grumble", 0.9)
sfx("the whole", "braam", 0.7)
sfx(story.at("thing.") - 0.02, "slam", 1.0)
sfx("ridges pressed", "shimmer", 0.8)
sfx("disappear.", "buzzer", 0.8)
sfx("And the man", "sting_low", 0.6)
sfx("undercover", "tiptoe", 0.7)
sfx("Isaac", "hit", 1.0)
sfx(story.at("Isaac") + 0.3, "boing", 0.8)
sfx("Yes.", "scratch", 0.9)
sfx("Three hundred", "whoosh", 0.6)
sfx(story.at("anymore.", 2), "buzzer", 0.5)
sfx(story.at("ridges.", 4), "final", 1.0)
