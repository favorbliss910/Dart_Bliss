# Shots 36-54 : imaginary probe, dense fluid, metallic hydrogen, magnetic field, fuzzy core, answer, ending.
from common import *
from scenes2 import T_CONTINUE, explorer_look_default
A = at
T_NOTREAL = A('Not with real technology')
T_IMAGINARY = A('but with an imaginary')
T_MODELS = A('scientific models predict')
T_HCOMP = A('As you descend the hydrogen')
T_DENSITY = A('The density rises')
T_PENORM = A('The pressure becomes enormous')
T_GRAD = A('And gradually')
T_DFLUID = A('more like a dense fluid')
T_WEIRD = A("But here's the weird part")
T_SPLASH = A('You never splash')
T_WAVE = A('enormous wave')
T_WLINE = A('No clear water line')
T_SUDDEN = A('No sudden moment')
T_INSTEAD = A('Instead the hydrogen')
T_DEEPF = A('deep fluid interior')
T_STRANGER = A('And now we reach')
T_FARTHER = A('much farther down')
T_SCIFI = A('sounds like science fiction')
T_METAL = A('Metallic hydrogen')
T_ROCKS = A("Now don't imagine")
T_MERCURY = A('Or a shiny metal')
T_NOTMEAN = A("That's not what scientists")
T_UNDER = A('Under extreme pressure')
T_ELECTRONS = A('Its electrons can move')
T_CURRENTS = A('electric currents to flow')
T_BELIEVE = A('And scientists believe')
T_WHYMATTER = A('But why does that matter')
T_REMEMBER = A("Remember Jupiter's powerful")
T_TRAP = A('trapping dangerous radiation')
T_DEEPMOVE = A('Deep inside Jupiter the movement')
T_GENERATE = A('helps generate that magnetic')
T_THINK = A('Think about that')
T_INVISIBLE = A('The invisible danger')
T_COULDNT = A("Something you couldn't see")
T_CENTER = A("But we still haven't")
T_SURPRISE = A('biggest surprise')
T_FORYEARS = A('For years')
T_COMPACT = A('relatively compact core')
T_BALL = A('something like a giant ball')
T_JUNO2 = A('But NASA Juno spacecraft complicated')
T_GRAV = A('By measuring tiny variations')
T_EVIDENCE = A('scientists found evidence')
T_FUZZY = A('A fuzzy core')
T_INSTEAD2 = A('Instead of all the heavier')
T_SPREAD = A('they may be spread')
T_DONTKNOW = A("And scientists still don't know")
T_FORMATION = A('Some models involve')
T_COLLISION = A('Others explore whether')
T_NOSC = A('But no spacecraft has ever reached')
T_NOCAM = A('No camera has photographed')
T_NOBODY = A('And nobody can tell')
T_BACK = A('Which brings us back')
T_IFYOU = A('If you actually fell', after=640)
T_NO = A('No', after=649)
T_WOULDNT = A("You wouldn't reach")
T_REALTECH = A('With real technology')
T_EVENIMAG = A('And even with our imaginary')
T_ROCKY = A('simple rocky landscape')
T_TRAVEL = A('Instead you would travel')
T_DENSEF = A('incredibly dense fluid')
T_LIKEMETAL = A('behaves like a metal')
T_CENTRAL = A('toward a central structure')
T_MOST = A("And here's the most surprising")
T_FROMEARTH = A('From Earth Jupiter looks')
T_ONLYCLOUDS = A('are only its visible clouds')
T_ALMOST = A('Almost everything')
T_PHOTO = A('We can photograph')
T_MEASGRAV = A('measure its gravity')
T_STUDYMAG = A('study its magnetic field')
T_PREDICT = A('and predict the exotic')
T_NEVER = A("But we've never directly")
T_NEXTTIME = A('So the next time')
T_NIGHT = A('in the night sky')
T_NOTLOOK = A("You're not looking at")
T_WORLD = A("You're looking at a world")
T_SENDING = A('sending spacecraft across')
T_BARELY2 = A("we've barely begun")
T_VO_END = 739.7
END_T = T_VO_END + 8.5

MODEL_TAG = 'MODEL-BASED ILLUSTRATION · IMAGINARY PROBE'

def deep_env(c, t, depth, fall=120):
    """depth 0..1: amber clouds -> dense dark-red fluid -> metallic blue-violet."""
    if depth < .5:
        k = depth / .5
        top = mixc('#8a3b1f', '#4a140a', k); bot = mixc('#2a0e06', '#14040a', k)
    else:
        k = (depth - .5) / .5
        top = mixc('#4a140a', '#1b1550', k); bot = mixc('#14040a', '#05031a', k)
    c.drawPaint(P(shader=lin((0, 0), (0, H), [top, bot])))
    hz = haze_sprites()
    for i in range(7):
        d = .4 + (i % 3) * .3
        y = ((i * 197 - t * fall * d) % (H + 300)) - 150
        x = ((i * 331 + t * 10 * d) % (W + 600)) - 600
        col = (1, .55, .35) if depth < .6 else (.55, .6, 1)
        draw_img(c, hz[i % len(hz)], x, y, 1600, 260, .25 * (1 - abs(depth - .5)) + .1, cf=tint_cf(*col))

def molecules(c, t, density, alpha=1.0, fall=100, metal=0.0):
    """H2 molecule field; density 0..1 controls spacing."""
    rng = np.random.default_rng(12)
    n = int(lerp(26, 220, density))
    pts = rng.random((220, 4))
    for i in range(n):
        x = (pts[i, 0] * (W + 100)) - 50 + math.sin(t * 2 + i) * 6
        y = (pts[i, 1] * (H + 100) - t * fall * (.5 + pts[i, 2])) % (H + 100) - 50
        r = lerp(16, 10, density)
        if metal > 0:
            c.drawCircle(x, y, r * .55, P(hexc('#ff9a7a', alpha * (1 - metal * .3))))
        else:
            h2_molecule(c, x, y, r, pts[i, 3] * 6.28 + t * .5, alpha * .85, '#FFE0C0')
    if metal > 0:
        for i in range(160):
            ph = (t * .35 + pts[i % 220, 3]) % 1.0
            x = ph * (W + 200) - 100
            y = pts[i % 220, 1] * H + math.sin(t * 3 + i) * 12
            c.drawCircle(x, y, 4, P(hexc('#8fe8ff', alpha * metal)))
            glow(c, x, y, 14, hexc('#6FD3FF'), alpha * metal * .5)

# ------------------------------------------------------------------ S36 imaginary indestructible probe
def s36(c, t):
    deep_env(c, t, .1)
    cloud_world(c, t, fall=80, tint=(.9, .6, .42), bg_draw=False, alpha=.6, depth_dark=.6)
    kr = prog(t, T_NOTREAL, T_NOTREAL + .5)
    if t < T_IMAGINARY:
        draw_galileo_descent(c, 960, 560, .9, chute=1, alpha=e_out(kr) * (1 - prog(t, T_IMAGINARY - .5, T_IMAGINARY)), t=t)
        draw_x(c, 960, 500, 260, prog(t, T_NOTREAL + .6, T_NOTREAL + 1.2))
        draw_text(c, 'NO REAL SPACECRAFT COULD SURVIVE THIS', 960, 880, font(40, 'black'), hexc('#FFF1D6'), 'center', alpha=e_out(prog(t, T_NOTREAL + 1, T_NOTREAL + 1.5)), shadow=1)
    else:
        k = e_out(prog(t, T_IMAGINARY, T_IMAGINARY + .8))
        draw_capsule(c, 960, 540, lerp(.8, 1.2, k), 0, k, t, shield=k, face=dict(look=(0, .4), brow=.6, mouth='neutral', blink=explorer_look_default(t)))
        draw_text(c, 'IMAGINARY · INDESTRUCTIBLE', 960, 900 - 20, font(44, 'black'), hexc('#8fd8ff'), 'center', alpha=k, glow=.3)
        km = prog(t, T_MODELS - .3, T_MODELS + .3)
        draw_tag(c, 'FROM HERE ON: WHAT SCIENTIFIC MODELS PREDICT', 960, 140, 'model', align='center', alpha=e_out(km))
    draw_tag(c, MODEL_TAG, 40, 36, 'model', alpha=e_out(prog(t, T_IMAGINARY, T_IMAGINARY + .5)))

# ------------------------------------------------------------------ S37 hydrogen compressed -> dense fluid
def s37(c, t):
    dens = e_io(prog(t, T_HCOMP, T_DFLUID + 1.0))
    deep_env(c, t, .15 + .25 * dens)
    molecules(c, t, dens, 1, fall=lerp(140, 40, dens))
    draw_capsule(c, 760, 540, .85, 0, 1, t, shield=.6, ambient='#c4541c', face=dict(look=(.6, .2), brow=.3, blink=explorer_look_default(t)))
    kd = prog(t, T_DENSITY - .2, T_DENSITY + .4)
    if kd > 0:
        draw_gauge(c, 1450, 330, 150, .15 + .7 * dens, 'DENSITY', 'RISING', alpha=e_out(kd), warn_from=.8)
    kp = prog(t, T_PENORM - .2, T_PENORM + .4)
    if kp > 0:
        hud_readout(c, 1260, 540, 380, 'PRESSURE (MODEL)', 'THOUSANDS', 'bar', e_out(kp), size=36)
    kg = prog(t, T_GRAD, T_GRAD + .8)
    if kg > 0:
        x0, y0, L = 1180, 760, 560
        c.drawRect(skia.Rect(x0, y0, x0 + L, y0 + 40), P(shader=lin((x0, 0), (x0 + L, 0), [hexc('#E3B47A'), hexc('#8a3b1f'), hexc('#3a0e08')])))
        draw_text(c, 'GAS', x0, y0 + 76, mono(24, 'bold'), hexc('#FFF1D6'), alpha=e_out(kg))
        draw_text(c, 'DENSE FLUID', x0 + L, y0 + 76, mono(24, 'bold'), hexc('#FFF1D6'), 'right', alpha=e_out(kg))
        mk = x0 + L * e_io(prog(t, T_GRAD, T_DFLUID + .8))
        c.drawCircle(mk, y0 + 20, 14, P(hexc('#6FD3FF')))
    draw_tag(c, MODEL_TAG, 40, 36, 'model')

# ------------------------------------------------------------------ S38 no splash
def s38(c, t):
    deep_env(c, t, .42)
    molecules(c, t, .85, .6, fall=60)
    sway = math.sin(t * 1.2) * 3
    brace = 1 if t > T_SPLASH else 0
    draw_capsule(c, 620, 520, .95, sway, 1, t, shield=.5, ambient='#c4541c', face=dict(look=(0, 1), brow=-1 if brace else .5, mouth='grit' if T_SPLASH < t < T_WAVE else 'o', blink=0))
    items = [(T_SPLASH, 'NO SPLASH'), (T_WAVE, 'NO WAVE'), (T_WLINE, 'NO WATER LINE'), (T_SUDDEN, 'NO SEPARATE SEA')]
    for i, (tt, txt) in enumerate(items):
        k = prog(t, tt, tt + .35)
        if k <= 0:
            continue
        y = 260 + i * 140
        card(c, 1100, y - 60, 640, 105, e_out(k))
        draw_x(c, 1160, y - 8, 46, prog(t, tt + .15, tt + .5))
        draw_text(c, txt, 1220, y + 8, font(44, 'black'), hexc('#FFF1D6'), alpha=e_out(k))
    draw_tag(c, MODEL_TAG, 40, 36, 'model')

# ------------------------------------------------------------------ S39 gradual change
def s39(c, t):
    bg(c, '#140608', '#05030a')
    x, top, bot, w = 960, 120, 960, 300
    c.drawRect(skia.Rect(x - w / 2, top, x + w / 2, bot), P(shader=lin((0, top), (0, bot), [hexc('#E3B47A'), hexc('#b8693a'), hexc('#6b2a14'), hexc('#3a0e08'), hexc('#1b1550')], [0, .2, .5, .8, 1])))
    c.drawRect(skia.Rect(x - w / 2, top, x + w / 2, bot), P(hexc('#FFF1D6', .4), stroke=2))
    yy = lerp(top + 40, bot - 140, e_io(prog(t, T_INSTEAD, T_DEEPF + 1.2)))
    draw_capsule(c, x, yy, .32, 0, 1, t, shield=.5)
    k = prog(t, T_INSTEAD + .4, T_INSTEAD + 1.0)
    draw_text(c, 'GAS', x - w / 2 - 30, top + 40, mono(26, 'bold'), hexc('#FFF1D6'), 'right', alpha=e_out(k))
    draw_text(c, 'DENSE FLUID', x - w / 2 - 30, bot - 160, mono(26, 'bold'), hexc('#FFF1D6'), 'right', alpha=e_out(k))
    kk = prog(t, T_INSTEAD + 1.4, T_INSTEAD + 2.0)
    label_line(c, x + w / 2, (top + bot) / 2, x + w / 2 + 160, (top + bot) / 2 - 60, 'NO SURFACE · NO BOUNDARY', hexc('#FFF1D6'), k=kk, size=36, sub='PROPERTIES CHANGE GRADUALLY WITH PRESSURE & TEMPERATURE')
    kd = prog(t, T_DEEPF - .2, T_DEEPF + .4)
    if kd > 0:
        draw_text(c, 'THE DEEP FLUID INTERIOR', x - w / 2 - 30, bot - 110, font(34, 'black'), hexc('#ff9a6a'), 'right', alpha=e_out(kd))
    draw_text(c, 'SCHEMATIC · NOT TO SCALE', x + w / 2 + 30, bot, mono(16, 'medium'), hexc(HUDC), alpha=.7)
    draw_tag(c, MODEL_TAG, 40, 36, 'model')

# ------------------------------------------------------------------ S40 metallic hydrogen reveal (visual peak)
def s40(c, t):
    k = e_io(prog(t, T_STRANGER, T_METAL))
    deep_env(c, t, .45 + .55 * k, fall=60)
    molecules(c, t, .9, 1 - .5 * k, fall=40, metal=k * .9)
    km = prog(t, T_METAL - .1, T_METAL + .4)
    flash(c, (1 - e_out(prog(t, T_METAL - .1, T_METAL + .5))) * .45 * (t > T_METAL - .1), '#9fb0ff')
    draw_capsule(c, 960, 520, .7, 0, 1, t, shield=.6, ambient='#6a6aff', hull_light='#bfc8ff', face=dict(look=(-.5, 0), brow=1, mouth='o', blink=0))
    if km > 0:
        draw_text(c, 'METALLIC HYDROGEN', 960, 900, font(96, 'black'), hexc('#cfd6ff'), 'center', alpha=e_out(km), glow=.6, glow_color=hexc('#6FD3FF'))
        draw_text(c, 'PREDICTED BY HIGH-PRESSURE PHYSICS', 960, 960 - 4, mono(22, 'semi'), hexc('#9FE3FF'), 'center', alpha=e_out(km) * .9)
    kf = fade_window(t, T_FARTHER, T_METAL - .1, .3, .2)
    draw_text(c, 'MUCH FARTHER DOWN…', 960, 200, font(52, 'black'), hexc('#FFF1D6'), 'center', alpha=kf, shadow=1)
    draw_tag(c, MODEL_TAG, 40, 36, 'model')

# ------------------------------------------------------------------ S41 not silver rocks, not mercury
def s41(c, t):
    bg(c, '#0d0a24', '#05031a')
    for i, (tt, txt) in enumerate(((T_ROCKS, 'SILVER ROCKS'), (T_MERCURY, 'A MERCURY-LIKE OCEAN'))):
        k = prog(t, tt, tt + .4)
        if k <= 0:
            continue
        x = 520 + i * 880; y = 480
        card(c, x - 340, y - 260, 680, 520, e_out(k))
        c.save(); c.clipRect(skia.Rect(x - 330, y - 250, x + 330, y + 170))
        if i == 0:
            for j in range(6):
                rx = x - 240 + j * 95; ry = y + 60 - (j % 2) * 40
                pa = path_from([(rx - 50, ry + 50), (rx - 30, ry - 40), (rx + 20, ry - 60), (rx + 55, ry + 10), (rx + 40, ry + 50)], True)
                c.drawPath(pa, P(shader=lin((rx - 50, ry - 60), (rx + 50, ry + 50), [hexc('#f4f6fb', e_out(k)), hexc('#7d8494', e_out(k))])))
        else:
            c.drawRect(skia.Rect(x - 330, y - 250, x + 330, y + 170), P(shader=lin((0, y - 250), (0, y + 170), [hexc('#2a2e3a', e_out(k)), hexc('#0e1018', e_out(k))])))
            for j in range(5):
                pa = skia.Path(); yy = y - 20 + j * 40
                pa.moveTo(x - 330, yy)
                for q in range(0, 680, 20):
                    pa.lineTo(x - 330 + q, yy + 8 * math.sin(q * .03 + t * 2 + j))
                pa.lineTo(x + 330, y + 170); pa.lineTo(x - 330, y + 170); pa.close()
                c.drawPath(pa, P(shader=lin((0, yy - 10), (0, yy + 40), [hexc('#f0f3f8', e_out(k) * .9), hexc('#5a6070', e_out(k))])))
        c.restore()
        draw_text(c, txt, x, y + 225, font(38, 'black'), hexc('#FFF1D6'), 'center', alpha=e_out(k))
        draw_x(c, x, y - 40, 300, prog(t, tt + .4, tt + .9), alpha=.9)
    kn = prog(t, T_NOTMEAN, T_NOTMEAN + .4)
    draw_text(c, "NOT WHAT SCIENTISTS MEAN", 960, 140, font(52, 'black'), hexc('#cfd6ff'), 'center', alpha=e_out(kn), shadow=1)

# ------------------------------------------------------------------ S42 conductivity
def s42(c, t):
    show_cs = e_io(prog(t, T_BELIEVE - .3, T_BELIEVE + .8))
    bg(c, '#120c34', '#05031a')
    if show_cs < 1:
        a = 1 - show_cs
        x0, y0, w, h = 260, 220, 1400, 560
        card(c, x0, y0, w, h, a, color='#0a0a26', border='#8A5CFF')
        rng = np.random.default_rng(3)
        for i in range(10):
            for j in range(4):
                px = x0 + 100 + i * 135 + math.sin(t * 3 + i + j) * 4
                py = y0 + 110 + j * 115 + math.cos(t * 2.5 + i * j) * 4
                c.drawCircle(px, py, 18, P(shader=rad(px - 5, py - 5, 22, [hexc('#ffc4b0', a), hexc('#ff6a4a', a)])))
                draw_text(c, '+', px, py + 8, font(24, 'black'), hexc('#5a1a10'), 'center', alpha=a)
        ke = prog(t, T_ELECTRONS - .3, T_ELECTRONS + .5)
        for i in range(70):
            r = rng.random(3)
            ph = (t * (.12 + .1 * r[2]) * (1 + 2 * prog(t, T_CURRENTS - .5, T_CURRENTS + .5)) + r[0]) % 1.0
            ex = x0 + 40 + ph * (w - 80); ey = y0 + 60 + r[1] * (h - 120) + math.sin(t * 4 + i) * 10
            c.drawCircle(ex, ey, 6, P(hexc('#8fe8ff', a * e_out(ke))))
            glow(c, ex, ey, 18, hexc('#6FD3FF'), a * e_out(ke) * .6)
        draw_text(c, '+  HYDROGEN NUCLEI (PROTONS)', x0 + 30, y0 + h + 50, mono(24, 'semi'), hexc('#ff9a7a'), alpha=a)
        draw_text(c, '●  FREE-MOVING ELECTRONS', x0 + 600, y0 + h + 50, mono(24, 'semi'), hexc('#8fe8ff'), alpha=a * e_out(ke))
        kc = prog(t, T_CURRENTS - .3, T_CURRENTS + .5)
        arrow(c, x0 + 300, y0 - 50, x0 + w - 300, y0 - 50, hexc('#8fe8ff'), 8, 30, a, k=e_out(kc), glow_=1)
        draw_text(c, 'ELECTRIC CURRENT', 960, y0 - 80, mono(26, 'bold'), hexc('#8fe8ff'), 'center', alpha=a * e_out(kc))
        draw_text(c, 'UNDER EXTREME PRESSURE: HYDROGEN CONDUCTS ELECTRICITY', 960, 150, font(38, 'black'), hexc('#cfd6ff'), 'center', alpha=a * e_out(prog(t, T_UNDER, T_UNDER + .5)))
        draw_tag(c, 'CONCEPTUAL DIAGRAM', 40, 36, 'concept', alpha=a)
    if show_cs > 0:
        space(c, t, alpha=show_cs)
        R = 420
        draw_cross_section(c, 960, 560, R, alpha=show_cs, wedge=(-90, 90), t=t, core_alpha=0, metal_glow=.9, highlight=(0.0, 0.8, '#8fe8ff'))
        label_line(c, 960 + R * .5, 560 - R * .1, 1560, 300, 'LIQUID METALLIC HYDROGEN', hexc('#cfd6ff'), alpha=show_cs, k=prog(t, T_BELIEVE + .5, T_BELIEVE + 1.2), size=36, sub='ENORMOUS REGIONS OF THE INTERIOR (MODEL)')
        draw_tag(c, 'MODEL-BASED CUTAWAY · NOT TO SCALE', 40, 36, 'model', alpha=show_cs)

# ------------------------------------------------------------------ S43 magnetic field + radiation (callback)
def belts(c, cx, cy, R, t, alpha):
    if alpha <= 0:
        return
    c.drawOval(skia.Rect(cx - R * 3.4, cy - R * .8, cx + R * 3.4, cy + R * .8), P(hexc('#6FD3FF', .12 * alpha), stroke=R * .5, blur=30))
    rng = np.random.default_rng(8)
    for i in range(140):
        r = rng.random(3)
        L = lerp(1.6, 3.4, r[0])
        ph = t * (.2 + .3 * r[1]) + r[2] * 6.28
        x = cx + math.cos(ph) * R * L; y = cy + math.sin(ph) * R * L * .22 + math.sin(t * 6 + i) * R * .05
        if math.sin(ph) < 0 and abs(x - cx) < R:
            continue
        c.drawCircle(x, y, 3, P(hexc('#cfefff', alpha * .8)))

def s43(c, t):
    space(c, t)
    R = 260
    cx, cy = 960, 560
    kf = e_io(prog(t, T_REMEMBER, T_REMEMBER + 2.5))
    dipole_lines(c, cx, cy, R, alpha=kf, k=kf, t=t)
    draw_jupiter(c, cx, cy, R, rot=2.2 + t * .03)
    kb = prog(t, T_TRAP - .3, T_TRAP + 1.0)
    belts(c, cx, cy, R, t, e_out(kb))
    if kf > 0:
        label_line(c, cx + R * 2.2, cy - R * 1.2, 1560, 180, 'MAGNETIC FIELD', hexc('#6FD3FF'), k=prog(t, T_REMEMBER + .8, T_REMEMBER + 1.6), size=38, sub='THE STRONGEST OF ANY PLANET')
    if kb > 0:
        label_line(c, cx - R * 2.4, cy + 20, 300, 840, 'TRAPPED RADIATION', hexc('#FF8A7A'), k=kb, size=36, sub='DANGEROUS TO SPACECRAFT')
    kq = fade_window(t, T_WHYMATTER, T_REMEMBER, .3, .3)
    draw_text(c, 'WHY DOES IT MATTER?', 960, 150, font(56, 'black'), hexc('#FFF1D6'), 'center', alpha=kq, shadow=1)
    draw_tag(c, 'ILLUSTRATION · FIELD LINES SIMPLIFIED', 40, 36, 'concept')

# ------------------------------------------------------------------ S44 dynamo: interior generates field
def s44(c, t):
    pull = e_io(prog(t, T_COULDNT - .3, T_CENTER))
    R = lerp(400, 230, pull)
    cx, cy = 960, 560
    space(c, t)
    dipole_lines(c, cx, cy, R, alpha=.4 + .6 * prog(t, T_GENERATE, T_GENERATE + 1), k=e_io(prog(t, T_DEEPMOVE, T_GENERATE + 1.5)), t=t)
    draw_cross_section(c, cx, cy, R, wedge=(-90, 90), t=t, core_alpha=0, metal_glow=1)
    # convection swirls in metallic region
    kd = prog(t, T_DEEPMOVE, T_DEEPMOVE + 1)
    for i in range(4):
        rr = R * (.35 + .1 * i)
        start = -60 + ((t * 40 + i * 50) % 120)
        c.drawArc(skia.Rect(cx - rr, cy - rr, cx + rr, cy + rr), start, 40, False, P(hexc('#8fe8ff', .8 * e_out(kd)), stroke=5, cap='round'))
    belts(c, cx, cy, R, t, pull)
    ki = prog(t, T_INVISIBLE, T_INVISIBLE + 1.0)
    if ki > 0:
        dashed(c, [(cx + R * .5, cy - R * .2), (cx + R * 2.0, cy - R * 1.3)], hexc('#FFF1D6'), 4, phase=-t * 40, k=e_out(ki))
        draw_text(c, 'MOVING CONDUCTIVE FLUID  →  MAGNETIC FIELD', 960, 150, font(40, 'black'), hexc('#FFF1D6'), 'center', alpha=e_out(ki), shadow=1)
    kt = fade_window(t, T_THINK, T_INVISIBLE, .3, .3)
    draw_text(c, 'THINK ABOUT THAT.', 960, 150, font(52, 'black'), hexc('#FFF1D6'), 'center', alpha=kt, shadow=1)
    draw_tag(c, 'MODEL-BASED CUTAWAY · NOT TO SCALE', 40, 36, 'model')

# ------------------------------------------------------------------ S45 the center: older compact-core model
def s45(c, t):
    space(c, t)
    z = e_io(prog(t, T_CENTER, T_FORYEARS))
    R = lerp(300, 430, z)
    draw_cross_section(c, 960, 560, R, wedge=(-90, 90), t=t, core_fuzz=0, core_alpha=e_out(prog(t, T_COMPACT - .3, T_COMPACT + .5)), show_metal=1, metal_glow=.3)
    chapter_card(c, 2, 'THE CENTER', t, T_CENTER + .2, T_FORYEARS + .5)
    kc = prog(t, T_COMPACT, T_COMPACT + .6)
    label_line(c, 960 + R * .12, 560, 1500, 700, 'COMPACT CORE', hexc('#FFF1D6'), k=kc, size=38, sub='HEAVY ELEMENTS IN A SHARP, SMALL BALL')
    ko = prog(t, T_FORYEARS, T_FORYEARS + .5)
    draw_tag(c, 'OLDER, SIMPLER MODEL', 1500, 160, 'model', alpha=e_out(ko))

# ------------------------------------------------------------------ S46 Juno gravity -> fuzzy core (visual peak)
def s46(c, t):
    space(c, t)
    R = 380; cx, cy = 820, 560
    fz = e_io(prog(t, T_EVIDENCE, T_FUZZY + .6))
    draw_cross_section(c, cx, cy, R, wedge=(-90, 90), t=t, core_fuzz=fz, core_alpha=1, metal_glow=.3)
    # Juno polar orbit
    kj = prog(t, T_JUNO2, T_JUNO2 + .6)
    if kj > 0:
        orb = skia.Rect(cx - R * .55, cy - R * 1.35, cx + R * .55, cy + R * 1.35)
        c.drawOval(orb, P(hexc('#9FE3FF', .45 * e_out(kj)), stroke=2))
        ph = t * .9
        jx = cx + math.cos(ph) * R * .55; jy = cy + math.sin(ph) * R * 1.35
        draw_juno(c, jx, jy, .16, ph * 50, alpha=e_out(kj))
        draw_tag(c, 'NASA JUNO', jx + 30, jy - 50, 'concept', alpha=e_out(kj))
    kg = prog(t, T_GRAV, T_GRAV + .8)
    if kg > 0:
        # gravity measurement: wavy contours
        for i in range(4):
            rr = R * (1.08 + i * .07)
            pa = skia.Path()
            for j in range(0, 361, 4):
                a = math.radians(j)
                r2 = rr + math.sin(a * 6 + t * 2 + i) * 4 * e_out(kg)
                x, y = cx + math.cos(a) * r2, cy + math.sin(a) * r2
                pa.moveTo(x, y) if j == 0 else pa.lineTo(x, y)
            c.drawPath(pa, P(hexc('#58E08A', .35 * e_out(kg) * (1 - fz * .6)), stroke=2))
        draw_text(c, 'MEASURING TINY GRAVITY VARIATIONS', 1440, 200, mono(24, 'bold'), hexc('#58E08A'), 'center', alpha=e_out(kg) * (1 - fz))
    if fz > 0:
        kk = prog(t, T_FUZZY - .2, T_FUZZY + .5)
        label_line(c, cx + R * .35, cy - R * .2, 1420, 330, 'A "FUZZY" CORE', hexc('#FFE2B0'), k=kk, size=52, sub='HEAVY ELEMENTS SPREAD OUT · DILUTE')
        draw_tag(c, 'EVIDENCE FROM JUNO GRAVITY DATA', 1300, 470, 'model', alpha=e_out(kk))

# ------------------------------------------------------------------ S47 spread through broad region
def s47(c, t):
    space(c, t)
    z = e_io(prog(t, T_INSTEAD2, T_SPREAD + 1))
    R = lerp(380, 900, z)
    cx, cy = lerp(820, 600, z), 560
    draw_cross_section(c, cx, cy, R, wedge=(-90, 90), t=t, core_fuzz=1, core_alpha=1, metal_glow=.3)
    ks = prog(t, T_SPREAD, T_SPREAD + 1.5)
    if ks > 0:
        rr = R * .52
        c.drawArc(skia.Rect(cx - rr, cy - rr, cx + rr, cy + rr), -90, 180, False, P(hexc('#FFE2B0', .8 * e_out(ks)), stroke=3))
        draw_text(c, 'A BROAD CENTRAL REGION', cx + rr + 30, cy + 10, font(40, 'black'), hexc('#FFE2B0'), alpha=e_out(ks), shadow=1)
    kd = prog(t, T_DONTKNOW, T_DONTKNOW + .5)
    if kd > 0:
        draw_text(c, 'HOW DID IT FORM?', 1500, 200, font(52, 'black'), hexc('#FFF1D6'), 'center', alpha=e_out(kd), shadow=1)
        draw_text(c, '?', 1500, 400, font(170, 'black'), hexc('#6FD3FF'), 'center', alpha=e_out(kd), glow=.4)
    draw_tag(c, 'MODEL-BASED CUTAWAY · NOT TO SCALE', 40, 36, 'model')

# ------------------------------------------------------------------ S48 formation vs giant collision
def s48(c, t):
    bg(c, '#0b1230', '#05070f')
    k1 = prog(t, T_FORMATION, T_FORMATION + .5)
    k2 = prog(t, T_COLLISION, T_COLLISION + .5)
    for i, (k, title) in enumerate(((k1, 'SLOW FORMATION PROCESSES'), (k2, 'A GIANT EARLY COLLISION?'))):
        if k <= 0:
            continue
        a = e_out(k)
        x = 500 + i * 920; y = 520
        card(c, x - 400, y - 330, 800, 640, a)
        c.save(); c.clipRect(skia.Rect(x - 390, y - 320, x + 390, y + 220))
        if i == 0:
            for j in range(6):
                rx = 340 - j * 45
                c.drawOval(skia.Rect(x - rx, y - rx * .22, x + rx, y + rx * .22), P(hexc('#E3B47A', a * (.15 + j * .05)), stroke=8))
            for j in range(40):
                ang = t * (.6 + j % 5 * .1) + j
                rr = 60 + (j * 37 % 280)
                c.drawCircle(x + math.cos(ang) * rr, y + math.sin(ang) * rr * .22, 3 + j % 3, P(hexc('#FFF1D6', a * .8)))
            c.drawCircle(x, y, 70, P(shader=rad(x - 20, y - 20, 90, [hexc('#f0c890', a), hexc('#8a4e2b', a)])))
        else:
            hit = (t - T_COLLISION) % 4.0
            draw_jupiter(c, x + 60, y, 150, rot=t * .2, alpha=a)
            ix = x + 60 - 150 - 300 * max(0, 1 - hit / 1.2); iy = y - 120 - 250 * max(0, 1 - hit / 1.2)
            if hit < 1.2:
                c.drawCircle(ix, iy, 50, P(shader=rad(ix - 15, iy - 15, 60, [hexc('#c8b8a8', a), hexc('#5a4a40', a)])))
            else:
                kb = (hit - 1.2) / 2.8
                glow(c, x - 60, y - 100, 260 * (0.3 + kb), hexc('#ffb070'), a * (1 - kb))
        c.restore()
        draw_text(c, title, x, y + 270, font(34, 'black'), hexc('#FFF1D6'), 'center', alpha=a)
        draw_tag(c, 'HYPOTHESIS', x, y - 300, 'model', align='center', alpha=a)

# ------------------------------------------------------------------ S49 no spacecraft, no camera
def s49(c, t):
    bg(c, '#05030a', '#000000')
    glow(c, 960, 560, 330, hexc('#ffb070'), .25 + .05 * math.sin(t * 2))
    glow(c, 960, 560, 160, hexc('#fff1d6'), .12)
    draw_text(c, '?', 960, 640, font(260, 'black'), hexc('#FFF1D6'), 'center', alpha=.8, glow=.4)
    k1 = prog(t, T_NOSC, T_NOSC + .5)
    draw_text(c, 'NO SPACECRAFT HAS BEEN THERE', 960, 170, font(44, 'black'), hexc('#FFF1D6'), 'center', alpha=e_out(k1), shadow=1)
    k2 = prog(t, T_NOCAM, T_NOCAM + .5)
    if k2 > 0:
        x, y = 1550, 560
        rrect(c, x - 90, y - 55, 180, 120, 18, P(hexc('#cfd6e0', e_out(k2))))
        c.drawCircle(x, y + 5, 40, P(hexc('#1d2027', e_out(k2))))
        c.drawCircle(x, y + 5, 26, P(hexc('#3d5a9e', e_out(k2))))
        rrect(c, x - 50, y - 80, 60, 30, 6, P(hexc('#cfd6e0', e_out(k2))))
        draw_x(c, x, y, 200, prog(t, T_NOCAM + .4, T_NOCAM + .9))
        draw_text(c, 'NEVER PHOTOGRAPHED', x, y + 170, mono(24, 'bold'), hexc('#FFF1D6'), 'center', alpha=e_out(k2))
    k3 = prog(t, T_NOBODY + .5, T_NOBODY + 1.2)
    draw_text(c, "NOBODY KNOWS EXACTLY WHAT JUPITER'S CENTER LOOKS LIKE", 960, 900 - 20, mono(26, 'bold'), hexc('#9FE3FF'), 'center', alpha=e_out(k3))

# ------------------------------------------------------------------ S50 back to the question: NO.
def s50(c, t):
    space(c, t)
    no = t >= T_NO
    draw_jupiter(c, 1430, 610, 720, rot=2.4 + t * .012, alpha=.55 if no else 1)
    px, py = 520, 400
    draw_capsule(c, px, py + math.sin(t * 1.4) * 8, .45, 25, 1, t, face=dict(look=(.6, .3), brow=.3, blink=explorer_look_default(t)))
    k = prog(t, T_IFYOU, T_IFYOU + .6)
    draw_text(c, 'WOULD YOU EVENTUALLY', 110, 700, font(64, 'black'), hexc('#FFF1D6'), alpha=e_out(k) * (1 - .6 * no), shadow=1)
    draw_text(c, 'LAND?', 110, 780, font(64, 'black'), hexc('#E3B47A'), alpha=e_out(k) * (1 - .6 * no), shadow=1)
    if no:
        kn = prog(t, T_NO, T_NO + .3)
        c.save(); c.translate(960, 560); s = lerp(1.6, 1.0, e_out(kn)); c.scale(s, s)
        draw_text(c, 'NO.', 0, 80, font(300, 'black'), hexc('#FFFFFF'), 'center', alpha=e_out(kn), glow=.5, shadow=1)
        c.restore()
    draw_tag(c, 'BACK TO THE QUESTION', 40, 36, 'concept', alpha=e_out(prog(t, T_BACK, T_BACK + .5)))

# ------------------------------------------------------------------ S51 recap journey
def s51(c, t):
    bg(c, '#0b1230', '#05070f')
    x, top, bot, w = 520, 110, 980, 220
    c.drawRect(skia.Rect(x - w / 2, top, x + w / 2, bot), P(shader=lin((0, top), (0, bot), [hexc('#E3B47A'), hexc('#8a3b1f'), hexc('#3a0e08'), hexc('#2d2a7a'), hexc('#c98a4a')], [0, .25, .5, .72, 1])))
    c.drawRect(skia.Rect(x - w / 2, top, x + w / 2, bot), P(hexc('#FFF1D6', .4), stroke=2))
    draw_text(c, 'SCHEMATIC · NOT TO SCALE', x, bot + 40, mono(16, 'medium'), hexc(HUDC), 'center', alpha=.7)
    kg = prog(t, T_WOULDNT, T_WOULDNT + .5)
    if kg > 0:
        draw_text(c, 'NO SOLID SURFACE LIKE EARTH', 1300, 880, font(44, 'black'), hexc('#FFF1D6'), 'center', alpha=e_out(kg), shadow=1)
    kr = prog(t, T_REALTECH, T_REALTECH + .5)
    if kr > 0:
        draw_galileo_descent(c, x - 160, top + 70, .25, chute=1, t=t, alpha=e_out(kr))
        draw_x(c, x - 160, top + 60, 80, prog(t, T_REALTECH + .5, T_REALTECH + 1.0))
        draw_text(c, 'REAL SPACECRAFT: DESTROYED EARLY', x - 240, top + 150, mono(18, 'bold'), hexc('#FF8A7A'), 'right' if False else 'left', alpha=0)
    stations = [(T_TRAVEL, .12, 'ATMOSPHERE', '#FFF1D6'), (T_DENSEF, .42, 'INCREDIBLY DENSE FLUID', '#ff9a6a'), (T_LIKEMETAL, .68, 'HYDROGEN BEHAVES LIKE A METAL', '#9fb0ff'), (T_CENTRAL, .92, 'A CENTRAL STRUCTURE STILL BEING STUDIED', '#FFE2B0')]
    prog_y = top
    for tt, f, lab, col in stations:
        k = prog(t, tt, tt + .6)
        if k > 0:
            yy = top + (bot - top) * f
            label_line(c, x + w / 2, yy, x + w / 2 + 140, yy, lab, hexc(col), k=k, size=36)
            prog_y = max(prog_y, lerp(prog_y, yy, 1))
    if t > T_TRAVEL:
        yy = keys(t, [(T_TRAVEL, top + 30)] + [(tt + .8, top + (bot - top) * f) for tt, f, _, _ in stations[1:]])
        draw_capsule(c, x, yy, .22, 0, 1, t, shield=.6)
    kk = prog(t, T_ROCKY - .3, T_ROCKY + .3)
    a = fade_window(t, T_ROCKY - .3, T_TRAVEL + .2, .3, .3)
    if a > 0:
        card(c, 1000, 380, 620, 120, a)
        draw_text(c, 'SIMPLE ROCKY LANDSCAPE', 1330, 455, font(36, 'black'), hexc('#FFF1D6'), 'center', alpha=a)
        draw_x(c, 1060, 440, 50, prog(t, T_ROCKY, T_ROCKY + .5), alpha=a)
    draw_tag(c, 'RECAP · MODEL-BASED', 40, 36, 'model')

# ------------------------------------------------------------------ S52 stripes are only the visible clouds
def s52(c, t):
    space(c, t)
    z = e_io(prog(t, T_MOST, T_FROMEARTH + 1.5))
    R = lerp(40, 380, z)
    op = e_io(prog(t, T_ONLYCLOUDS, T_ALMOST + 1.0))
    draw_cross_section(c, 960, 560, R, wedge=(-90, -90 + 150 * op), t=t, core_fuzz=1, metal_glow=.6)
    kc = prog(t, T_ONLYCLOUDS, T_ONLYCLOUDS + .6)
    if kc > 0 and R > 300:
        label_line(c, 960 - R * .7, 560 - R * .7, 420, 200, 'VISIBLE CLOUDS: A THIN SKIN', hexc('#FFF1D6'), k=kc, size=34)
    ka = prog(t, T_ALMOST + .5, T_ALMOST + 1.2)
    if ka > 0:
        draw_text(c, 'ALMOST EVERYTHING IS HIDDEN BENEATH', 960, 1000 - 70, font(44, 'black'), hexc('#FFF1D6'), 'center', alpha=e_out(ka), shadow=1)

# ------------------------------------------------------------------ S53 what we can do vs never explored
def s53(c, t):
    bg(c, '#0b1230', '#05070f')
    items = [(T_PHOTO, 'PHOTOGRAPH ITS STORMS'), (T_MEASGRAV, 'MEASURE ITS GRAVITY'), (T_STUDYMAG, 'STUDY ITS MAGNETIC FIELD'), (T_PREDICT, 'PREDICT WHAT LIES INSIDE')]
    dim = e_io(prog(t, T_NEVER, T_NEVER + 1.0))
    for i, (tt, lab) in enumerate(items):
        k = prog(t, tt, tt + .4)
        if k <= 0:
            continue
        a = e_out(k) * (1 - .6 * dim)
        x = 250 + (i % 2) * 720; y = 130 + (i // 2) * 370
        card(c, x, y, 680, 330, a)
        cx_, cy_ = x + 170, y + 165
        c.save(); c.clipRect(skia.Rect(x + 10, y + 10, x + 670, y + 320))
        if i == 0:
            draw_jupiter(c, cx_, cy_ - 520 * 0 , 130, rot=math.pi, alpha=a, max_grid=300)
            if t - tt < .3:
                flash(c, (1 - (t - tt) / .3) * .5 * a)
        elif i == 1:
            draw_jupiter(c, cx_, cy_, 100, rot=2.0, alpha=a, max_grid=300)
            draw_juno(c, cx_ + 120, cy_ - 80, .18, t * 30, alpha=a)
        elif i == 2:
            dipole_lines(c, cx_, cy_, 50, alpha=a, k=1, t=t, Ls=(1.6, 2.4, 3.2), width=2)
            draw_jupiter(c, cx_, cy_, 50, rot=2.0, alpha=a, max_grid=200)
        else:
            draw_cross_section(c, cx_, cy_, 120, alpha=a, wedge=(-60, 60), t=t, core_fuzz=1, metal_glow=.8)
        c.restore()
        draw_text(c, lab, x + 340, y + 175, font(30, 'black'), hexc('#FFF1D6'), 'left', alpha=a)
        draw_check(c, x + 620, y + 60, 40, prog(t, tt + .2, tt + .6), alpha=a)
    if dim > 0:
        card(c, 360, 380, 1200, 220, dim, color='#140608', border='#FF3B30')
        draw_text(c, 'DIRECTLY EXPLORED:', 960, 470, mono(30, 'bold'), hexc('#FF8A7A'), 'center', alpha=dim)
        draw_text(c, 'ONLY THE TOP SLIVER', 960, 550, font(64, 'black'), hexc('#FFFFFF'), 'center', alpha=dim, glow=.3)

# ------------------------------------------------------------------ S54 night sky ending
def s54(c, t):
    zoom = e_io(prog(t, T_WORLD, T_VO_END + 1.5))
    bg(c, '#070B1A', '#1C2A55')
    draw_stars(c, t, 1.0, zoom=1 + zoom * 2, cx=1240, cy=300)
    # Jupiter: a bright point, growing to the planet as we "look closer"
    jx, jy = 1240, 300
    R = lerp(5, 330, e_in(zoom))
    glow(c, jx, jy, lerp(60, 520, zoom), hexc('#ffe2b0'), lerp(.7, .25, zoom))
    if R > 8:
        draw_jupiter(c, lerp(jx, 960, zoom), lerp(jy, 470, zoom), R, rot=2.6 + t * .02, alpha=prog(R, 8, 40))
    else:
        c.drawCircle(jx, jy, 5, P(hexc('#fff6e0')))
    # landscape silhouette and a person looking up
    ga = 1 - prog(zoom, .2, .7)
    if ga > 0:
        pa = skia.Path(); pa.moveTo(0, 860)
        for i in range(0, W + 60, 60):
            pa.lineTo(i, 850 + 30 * math.sin(i * .004) + 14 * math.sin(i * .013))
        pa.lineTo(W, H); pa.lineTo(0, H); pa.close()
        c.drawPath(pa, P(hexc('#03050c', ga)))
        px, py = 600, 840
        c.drawCircle(px, py - 120, 22, P(hexc('#03050c', ga)))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(px - 30, py - 98, px + 30, py + 10), 18, 18), P(hexc('#03050c', ga)))
        kl = prog(t, T_NIGHT, T_NIGHT + .6)
        label_line(c, jx, jy, jx + 200, jy + 110, 'JUPITER', hexc('#FFE2B0'), alpha=ga, k=kl, size=34)
    kn = fade_window(t, T_NOTLOOK, T_WORLD, .3, .3)
    draw_text(c, 'NOT A BALL OF GAS WITH A SECRET LANDING SPOT', 960, 120, font(40, 'black'), hexc('#FFF1D6'), 'center', alpha=kn, shadow=1)
    kb = fade_window(t, T_BARELY2 - .3, T_VO_END + 1.0, .5, .6)
    draw_text(c, "WE'VE BARELY BEGUN TO DISCOVER WHAT'S INSIDE", 960, 940 - 40, font(44, 'black'), hexc('#FFF1D6'), 'center', alpha=kb, shadow=1)
    ke = fade_window(t, T_VO_END + 1.2, END_T, .8, 1.0)
    if ke > 0:
        c.drawPaint(P(rgba(3, 4, 10, .45 * ke)))
        draw_text(c, 'WHAT IF YOU ACTUALLY', 960, 810, font(64, 'black'), hexc('#FFF1D6'), 'center', alpha=ke, shadow=1)
        draw_text(c, 'FELL INTO JUPITER?', 960, 890, font(64, 'black'), hexc('#E3B47A'), 'center', alpha=ke, shadow=1, glow=.25)
        draw_text(c, 'Illustrations combine historical data, scientific models and clearly labeled fiction.', 960, 960, font(22, 'medium'), hexc('#9FE3FF'), 'center', alpha=ke * .9)

SHOTS3 = [
    (T_CONTINUE, s36, ('black', .6)),
    (T_HCOMP, s37, ('fade', .6)),
    (T_WEIRD, s38, ('fade', .5)),
    (T_INSTEAD, s39, ('fade', .5)),
    (T_STRANGER, s40, ('fade', .7)),
    (T_ROCKS, s41, ('whip', .35)),
    (T_UNDER, s42, ('fade', .5)),
    (T_WHYMATTER, s43, ('fade', .6)),
    (T_DEEPMOVE, s44, ('fade', .6)),
    (T_CENTER, s45, ('black', .6)),
    (T_JUNO2, s46, ('fade', .4)),
    (T_INSTEAD2, s47, ('cut', 0)),
    (T_FORMATION, s48, ('fade', .5)),
    (T_NOSC, s49, ('black', .5)),
    (T_BACK, s50, ('fade', .6)),
    (T_WOULDNT, s51, ('fade', .5)),
    (T_MOST, s52, ('black', .5)),
    (T_PHOTO, s53, ('fade', .4)),
    (T_NEXTTIME, s54, ('black', .7)),
]
