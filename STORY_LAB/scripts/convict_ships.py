"""Story 3: One Line That Saved The Ships - shot list (pack section 10)."""
import math, os, random
from engine import *
import cast, props as P
from cast import draw as C

ROOT = os.path.dirname(HERE)
story = Story("convict_ships", ROOT)
shot, sfx = story.shot, story.add_sfx

STORM = ("#1A1E33", "#3A4560", "#55607A")
SUNNY = ("#6EC2F2", "#FFF4D6", "#BFE6FA")
DUSK = ("#2A2350", "#E08A70", "#8A5A80")
NIGHTSKY = ("#0B0E26", "#2E2A55", "#1C1C40")


def seascape(f, pal, cy=960, z=1.0, cx=540, storm=0.0, sea_y=1250, sun=False):
    c = f.ctx
    P.sky(f, pal[0], pal[1], pal[2])
    f.cam(cx, cy, z)
    f.layer(0.2)
    if sun:
        P.sun(c, 820, 420, 80)
        P.cloud(c, 260 + f.t * 8, 380, 0.9)
    elif storm > 0:
        for k in range(3):
            P.cloud(c, 150 + k * 380 + f.t * 20, 250 + (k % 2) * 80, 1.4, (0.35, 0.38, 0.48))
    f.layer(1.0)
    return sea_y


def prisoners_on_deck(c, x0, y, n, t, expr="sad", arms="down", s=0.55, gap=95):
    whos = ["prisoner", "prisoner2", "prisoner3"]
    for k in range(n):
        C(c, whos[k % 3], x0 + k * gap, y, s, expr=expr, arms=arms, t=t + k * 0.4)


# --------------------------------------------------------------------- 0.0 hook: ship pitching on a stormy sea, 1 IN 4
@shot(0.0)
def s_storm(f):
    c = f.ctx
    seascape(f, STORM, 1150, lerp(1.2, 1.32, f.p), storm=1.0)
    lightning = (f.t % 2.6) < 0.08
    if lightning:
        screen_fill(f, (0.9, 0.92, 1.0), 0.35)
        f.cam(540, 1150, lerp(1.2, 1.32, f.p))
    P.ocean(c, 1250, f.t, storm=1.0, col=(0.18, 0.3, 0.5), layers=1)
    P.ship(c, 520, 1300, 1.0, f.t, roll=0.14, lanterns=3, lit=[1, 0.6, 1])
    P.ocean(c, 1330, f.t + 1, storm=1.0, col=(0.16, 0.27, 0.46), layers=3)
    text3d(f, "1 IN 4", 540, 420, 220, f.lt - 0.4, top=(1, 0.45, 0.4), side=(0.5, 0.12, 0.12))
    vignette(f, 0.6)


@shot("Then the government")
def s_quill(f):
    c = f.ctx
    P.sky(f, "#3A2A20", "#1E140E")
    f.cam(540, 1000, lerp(1.1, 1.25, f.p))
    glow(c, 540, 960, 700, (1, 0.8, 0.5), 0.3)
    st = clamp((f.t - f.at("line")) / 0.5)
    P.contract(c, 540, 1000, 1.2, strike=st, line2="ONE LINE")
    qx = lerp(280, 820, st)
    P.quill(c, qx + 60, 1040, 1.2, -0.5)
    vignette(f, 0.5)


@shot("and almost all")
def s_lived(f):
    c = f.ctx
    seascape(f, SUNNY, 1180, 1.35, sun=True)
    P.ocean(c, 1350, f.t, col=(0.25, 0.6, 0.85), layers=1)
    P.ship(c, 520, 1380, 1.1, f.t, roll=0.03,
           people=lambda c: prisoners_on_deck(c, -260, -80, 6, f.t, "happy", "cheer"))
    P.ocean(c, 1440, f.t + 1, col=(0.22, 0.55, 0.82), layers=2)


# --------------------------------------------------------------------- 6.0 map: 1790, Britain -> Australia, 8 months
@shot("In seventeen")
def s_map(f):
    c = f.ctx
    P.sky(f, "#4A3020", "#2A1A10")
    f.cam(540, 1000, lerp(1.25, 1.05, ease(f.p)))
    route = clamp((f.t - f.at("Australia.") + 1.2) / 2.5)
    P.map_table(c, 540, 1000, 1.0, route,
                ship_draw=lambda c, x, y: P.ship(c, x, y, 0.13, f.t, roll=0.05))
    text3d(f, "1790", 540, 380, 220, f.lt - 0.4)
    if f.t > f.at("Eight"):
        text3d(f, "8 MONTHS", 540, 1600, 150, f.t - f.at("Eight"), top=(0.95, 0.95, 1.0), side=(0.3, 0.35, 0.55))
    vignette(f, 0.5)


# --------------------------------------------------------------------- 10.0 dock: paid per prisoner who walked on
@shot("The captains were")
def s_board(f):
    c = f.ctx
    seascape(f, ("#8AB8D8", "#F2E2C8", "#C8D8E0"), 1350, 1.25)
    P.ocean(c, 1200, f.t, col=(0.3, 0.55, 0.75), layers=1)
    P.ship(c, 820, 1210, 0.9, f.t, roll=0.01)
    P.dock(c, 1500, f.t)
    # gangplank
    poly(c, [(560, 1500), (640, 1500), (780, 1150), (720, 1150)])
    fs(c, (0.65, 0.45, 0.28), 6)
    # captain counting coins
    n_coins = int(max(0, f.lt - 0.4) / 0.55)
    C(c, "captain", 330, 1520, 1.35, expr="happy", arms="count", fd=1, t=f.t,
      hold=lambda c, hx, hy: [P.coin(c, hx, hy - 12 - k * 9, 22, squash=0.4, col=GOLD) for k in range(min(n_coins, 8))])
    for k in range(4):
        u = (f.lt * 0.35 + k * 0.25) % 1.0
        x = lerp(450, 760, u)
        y = 1500 if u < 0.35 else lerp(1500, 1160, (u - 0.35) / 0.65)
        C(c, ["prisoner", "prisoner2", "prisoner3"][k % 3], x, y, 0.85, expr="sad", arms="down", legs="walk", fd=1, t=f.t + k)
    vignette(f, 0.35)


@shot("So the captains")
def s_math(f):
    c = f.ctx
    P.sky(f, "#2E2A26", "#4A3F36")
    f.cam(540, 960, 1.0)
    P.chalkboard(c, 540, 820, 900, 900)
    t1 = f.t - f.at("eats")
    t2 = f.t - f.at("dies...")
    chalk_text(c, "CAPTAIN'S MATH", 540, 430, 80, (0.75, 0.9, 1.0), reveal=clamp(f.lt / 0.6))
    chalk_text(c, "LESS FOOD", 540, 580, 100, reveal=clamp(t1 / 0.6))
    chalk_text(c, "=", 540, 690, 100, reveal=clamp((t1 - 0.6) / 0.2))
    chalk_text(c, "MORE MONEY", 540, 820, 100, (1, 0.85, 0.4), reveal=clamp((t1 - 0.8) / 0.6))
    if t2 > -0.3:
        chalk_text(c, "DEAD = FREE", 540, 1040, 100, (1, 0.5, 0.5), reveal=clamp((t2 + 0.3) / 0.6))
    C(c, "captain", 880, 1900, 1.6, expr="smug", arms="point", fd=-1, look=(-1, -0.5), t=f.t)


@shot("A prisoner who dies")
def s_grin(f):
    c = f.ctx
    P.sky(f, "#0A0814", "#1E1428")
    f.cam(540, 1100, lerp(1.0, 1.1, f.p))
    C(c, "captain", 540, 2000, 3.6, expr="smug" if f.t < f.at("nothing.") else "sly", arms="hold", t=f.t, look=(0, 0.2),
      hold=lambda c, hx, hy: P.lamp(c, hx, hy + 30, 1.4, f.t))
    # under-light: darken top
    f.screen()
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgba(0, 0, 0, 0.05, 0.65)
    g.add_color_stop_rgba(0.55, 0, 0, 0.05, 0.0)
    c.rectangle(0, 0, W, H)
    c.set_source(g)
    c.fill()
    if f.t > f.at("nothing."):
        text3d(f, "COSTS NOTHING", 540, 380, 140, f.t - f.at("nothing."), top=(1, 0.45, 0.4), side=(0.5, 0.12, 0.12))
    vignette(f, 0.6)


# --------------------------------------------------------------------- 20.0 cutaway: the crowded dark hold
@shot("They packed")
def s_hold(f):
    c = f.ctx
    seascape(f, NIGHTSKY, 1250, lerp(1.3, 1.4, f.p))
    P.ocean(c, 1000, f.t, col=(0.12, 0.2, 0.38), layers=1)
    def crowd(c):
        whos = ["prisoner", "prisoner2", "prisoner3"]
        for r in range(2):
            for k in range(7):
                C(c, whos[(k + r) % 3], -330 + k * 110 + r * 50, -280 + r * 0 if r == 0 else 100, 0.55, expr="sad" if k % 2 else "tired",
                  arms="down", t=f.t + k, look=(0, 0.6), shadow=False)
        # chains
        if f.t > f.at("chains."):
            c.move_to(-420, 60)
            for k in range(28):
                c.line_to(-420 + k * 30, 60 + (8 if k % 2 else -4))
            stroke(c, 7, (0.6, 0.6, 0.65))
    P.hold_cutaway(c, 540, 1350, 1.05, f.t, crowd=crowd, light=0.25 if f.t < f.at("dark.") else 0.0)
    P.ocean(c, 1360, f.t + 1, col=(0.1, 0.18, 0.34), layers=2)
    vignette(f, 0.65)


@shot("And sold")
def s_sell(f):
    c = f.ctx
    seascape(f, DUSK, 1350, 1.25)
    P.ocean(c, 1200, f.t, col=(0.3, 0.38, 0.6), layers=1)
    P.dock(c, 1500, f.t)
    swap = clamp((f.lt - 0.5) / 0.6)
    sx = lerp(400, 640, swap)
    P.sack(c, sx, 1420 - math.sin(swap * math.pi) * 60, 0.9, 1.0)
    P.crate(c, 200, 1520, 0.8)
    C(c, "captain", 320, 1520, 1.3, expr="smug", arms="hold", fd=1, t=f.t)
    C(c, "merchant", 790, 1520, 1.3, expr="happy", arms="count", fd=-1, t=f.t,
      hold=lambda c, hx, hy: P.coin(c, hx, hy - 20, 28, col=GOLD))
    vignette(f, 0.45)


@shot("On one fleet")
def s_lanterns(f):
    c = f.ctx
    seascape(f, DUSK, 1220, 1.35)
    P.ocean(c, 1300, f.t, col=(0.25, 0.3, 0.55), layers=1)
    out = clamp((f.t - f.at("never")) / 0.3)
    P.ship(c, 540, 1360, 1.05, f.t, roll=0.02, lanterns=4, lit=[1, 1, 1 - out, 1])
    P.ocean(c, 1380, f.t + 1, col=(0.22, 0.27, 0.5), layers=2)
    text3d(f, "1 IN 4", 540, 420, 200, f.t - f.at("one in four", 2), top=(1, 0.45, 0.4), side=(0.5, 0.12, 0.12))
    vignette(f, 0.55)


@shot("People were")
def s_scold(f):
    c = f.ctx
    seascape(f, ("#9EC4DC", "#F0E6D2", "#C8D8E0"), 1350, 1.25)
    P.ocean(c, 1250, f.t, col=(0.3, 0.55, 0.75), layers=1)
    P.dock(c, 1500, f.t)
    horrified = f.t < f.at("Captains", 3)
    for k, who in enumerate(("official", "n2", "n3")):
        C(c, who, 190 + k * 190, 1540 + (k % 2) * 40, 1.15, expr="shock" if horrified else "angry", arms="up" if horrified else "wag",
          fd=1, t=f.t + k, look=(1, 0))
    C(c, "captain", 860, 1540, 1.35, expr="flat" if f.t < f.at("Nothing", 2) else "smug", arms="shrug" if f.t > f.at("Nothing", 2) else "cross", fd=-1, t=f.t)
    vignette(f, 0.35)


# --------------------------------------------------------------------- 33.0 one line changes: ON crossed out, OFF ALIVE stamped
@shot("Then someone")
def s_contract(f):
    c = f.ctx
    P.sky(f, "#3A2A20", "#1E140E")
    t_strike = f.at("on the ship.")
    t_stamp = f.at("Alive.")
    z = lerp(1.0, 1.15, ease(f.p))
    f.cam(540, 1000, z, shake=10 * max(0, 1 - (f.t - t_stamp) * 4) if f.t > t_stamp else 0)
    glow(c, 540, 960, 700, (1, 0.8, 0.5), 0.3)
    P.contract(c, 540, 1000, 1.2, strike=clamp((f.t - t_strike) / 0.5), stamp=clamp((f.t - t_stamp) / 1.0))
    if f.t < t_strike + 0.6:
        P.quill(c, lerp(380, 820, clamp((f.t - t_strike) / 0.5)), 1100, 1.2, -0.5)
    vignette(f, 0.5)


# --------------------------------------------------------------------- 46.0 doctors, fresh food, sunlight
@shot("Suddenly")
def s_doctor(f):
    c = f.ctx
    seascape(f, SUNNY, 1350, 1.25, sun=True)
    P.ocean(c, 1200, f.t, col=(0.3, 0.6, 0.85), layers=1)
    P.ship(c, 820, 1210, 0.9, f.t, roll=0.01)
    P.dock(c, 1500, f.t)
    poly(c, [(560, 1500), (640, 1500), (780, 1150), (720, 1150)])
    fs(c, (0.65, 0.45, 0.28), 6)
    u = clamp(f.lt / 1.8)
    x = lerp(300, 740, u)
    y = 1500 if u < 0.6 else lerp(1500, 1160, (u - 0.6) / 0.4)
    C(c, "doctor", x, y, 1.15, expr="happy", arms="down", legs="walk" if u < 1 else "stand", fd=1, t=f.t)
    C(c, "captain", 200, 1530, 1.35, expr="smile", arms="wave", fd=1, t=f.t)


@shot("Bought fresh")
def s_food(f):
    c = f.ctx
    seascape(f, SUNNY, 1350, 1.25, sun=True)
    P.ocean(c, 1250, f.t, col=(0.3, 0.6, 0.85), layers=1)
    P.dock(c, 1500, f.t)
    for k in range(4):
        d = clamp((f.lt - k * 0.2) / 0.3)
        P.crate(c, 160 + k * 250, lerp(1100, 1520, ease_out(d)), 0.9, [(1, 0.6, 0.1), (0.3, 0.75, 0.3), (1, 0.85, 0.2), (0.9, 0.2, 0.2)][k])


@shot("Let the")
def s_sunlight(f):
    c = f.ctx
    seascape(f, SUNNY, 1200, lerp(1.4, 1.3, f.p), sun=True)
    P.ocean(c, 1350, f.t, col=(0.25, 0.6, 0.85), layers=1)
    up = ease(clamp(f.lt / 1.0))
    P.ship(c, 520, 1380, 1.15, f.t, roll=0.03,
           people=lambda c: prisoners_on_deck(c, -280, -80 + 120 * (1 - up), 6, f.t, "happy", "cheer" if up > 0.9 else "down"))
    P.ocean(c, 1440, f.t + 1, col=(0.22, 0.55, 0.82), layers=2)
    f.screen()
    for k in range(5):
        a = 0.08 + 0.04 * math.sin(f.t + k)
        poly(c, [(820 + k * 30, 420), (860 + k * 30, 420), (300 + k * 150, 1500), (200 + k * 150, 1500)])
        fill(c, (1, 0.97, 0.8), a)


@shot("And almost every")
def s_graph(f):
    c = f.ctx
    P.sky(f, "#2E2A26", "#4A3F36")
    f.cam(540, 960, 1.0)
    P.chalkboard(c, 540, 860, 900, 1000)
    chalk_text(c, "DEATHS", 540, 460, 80)
    c.move_to(180, 520)
    c.line_to(180, 1240)
    c.line_to(920, 1240)
    stroke(c, 6, (0.95, 0.95, 0.92))
    k = clamp(f.lt / 1.2)
    c.move_to(200, 600)
    pts = [(200, 600), (380, 610), (450, 620)]
    n = 30
    for i in range(n + 1):
        u = i / n
        if u > k:
            break
        x = lerp(450, 900, u)
        y = 620 + (1200 - 620) * ease(u * 1.4)
        pts.append((x, min(y, 1210)))
    poly(c, pts, close=False)
    stroke(c, 12, (1, 0.5, 0.5))
    if f.t > f.at("arrived"):
        C(c, "prisoner", 260, 1900, 1.4, expr="happy", arms="cheer", t=f.t)
        C(c, "prisoner3", 540, 1940, 1.4, expr="laugh", arms="wave", t=f.t)
        C(c, "prisoner2", 820, 1900, 1.4, expr="happy", arms="cheer", t=f.t + 0.5)


# --------------------------------------------------------------------- 54.0 same ships, same captains, same ocean
@shot("Same ships")
def s_same(f):
    c = f.ctx
    seascape(f, SUNNY, 1250, lerp(1.2, 1.32, ease(f.p)), sun=True)
    P.ocean(c, 1300, f.t, col=(0.25, 0.6, 0.85), layers=1)
    stage = (f.t >= f.at("Same", 2)) + (f.t >= f.at("Same", 3))
    for k, x in enumerate((290, 790)):
        P.ship(c, x, 1350, 0.62, f.t + k * 0.2, roll=0.02, lanterns=0)
    if stage >= 1:
        for x in (290, 790):
            C(c, "captain", x - 60, 1250, 0.6, expr="smug", arms="hips", t=f.t)
    P.ocean(c, 1380, f.t + 1, col=(0.22, 0.55, 0.82), layers=2)
    f.screen()
    for k, word in enumerate(("SAME", "SAME", "SAME")):
        if stage >= k:
            pass
    label_txt = ["SAME SHIPS", "SAME CAPTAINS", "SAME OCEAN"][min(stage, 2)]
    text3d(f, label_txt, 540, 420, 130, f.t - f.at("Same", stage + 1), top=(0.95, 0.95, 1.0), side=(0.3, 0.35, 0.55))


@shot("The only")
def s_final(f):
    c = f.ctx
    k = ease(f.p)
    seascape(f, DUSK, lerp(1250, 1150, k), lerp(1.45, 1.1, k), sun=False)
    f.layer(0.2)
    P.sun(c, 540, 1180, 120, "#FFB070")
    f.layer(1.0)
    P.ocean(c, 1250, f.t, col=(0.3, 0.35, 0.6), layers=1)
    P.ship(c, 540, 1300, 0.9, f.t, roll=0.02, lanterns=4,
           people=lambda c: prisoners_on_deck(c, -240, -80, 5, f.t, "happy", "down", 0.5, 110))
    P.ocean(c, 1330, f.t + 1, col=(0.26, 0.3, 0.55), layers=2)
    tt = f.t - f.at("paid", 4) + 0.3
    if tt > 0:
        text3d(f, "WHAT DO\nYOU PAY FOR?", 540, 440, 150, tt)
    vignette(f, 0.5)


# --------------------------------------------------------------------- sound
sfx(0.05, "storm", 0.9)
sfx(0.3, "braam", 0.6)
sfx("line", "chalk", 0.9)
sfx("lived.", "bells", 0.6)
sfx("seventeen", "whoosh", 0.7)
sfx("Eight", "pop", 0.8)
for k in range(8):
    sfx(story.at("The captains were") + 0.4 + k * 0.55, "tick", 0.9)
sfx("did the math", "chalk", 0.8)
sfx("eats", "chalk", 0.8)
sfx("dies...", "chalk", 0.8)
sfx("nothing.", "braam", 0.9)
sfx("They packed", "creak", 0.8)
sfx("chains.", "creak", 0.8)
sfx("And sold", "coin", 0.7)
sfx("never", "sting_low", 0.5)
sfx("horrified.", "grumble", 0.8)
sfx(story.at("Nothing", 2), "boing", 0.6)
sfx(story.at("one line.", 2), "chalk", 0.8)
sfx("on the ship.", "chalk", 0.9)
sfx("Alive.", "stamp", 1.0)
sfx("Suddenly", "pizz_up", 0.8)
sfx("Bought", "pop", 0.6)
sfx(story.at("Bought") + 0.2, "pop", 0.6)
sfx(story.at("Bought") + 0.4, "pop", 0.6)
sfx("sunlight.", "shimmer", 0.8)
sfx("And almost every", "whoosh", 0.7)
sfx("arrived", "bells", 0.8)
sfx("Same", "hit", 0.6)
sfx(story.at("Same", 2), "hit", 0.6)
sfx(story.at("Same", 3), "hit", 0.7)
sfx(story.at("paid", 4), "final", 1.0)
