# Shots 18-35 : entry, deceleration, fictional capsule, clouds without horizon, instruments, Galileo's last signal.
from common import *
from scenes1 import HIST_TAG, T_HIT
A = at
T_CHANGES = A('And suddenly everything')
T_COMPRESSED = A('is compressed and')
T_SHIELD = A('Your heat shield')
T_DARKNESS = A('Outside the darkness')
T_DECEL = A('Then the deceleration hits')
T_GREAL = A("During Galileo's real")
T_228 = A('two hundred twenty eight times')
T_228B = A('two hundred and twenty eight')
T_HUMAN = A("A human couldn't")
T_ORDINARY = A('Not in an ordinary')
T_SUIT = A('Not with a normal')
T_HOLD = A('simply holding on')
T_ROBOT = A('But Galileo was')
T_WORST = A('It survived the worst')
T_CHUTE = A('deployed its parachute')
T_TRANSMIT = A('began transmitting')
T_FICT = A('Now imagine you have')
T_SHAKESTOP = A('The shaking stops')
T_GLOWFADE = A('The glow fades')
T_FIRST = A('And for the first time')
T_SURROUND = A("You're surrounded")
T_ABOVE = A('Above you')
T_BESIDE = A('Beside you')
T_BELOW = A('Below you')
T_MORE = A('More clouds')
T_MISSING = A('And something is missing')
T_HORIZON = A('A horizon')
T_ONEARTH = A('On earth you can')
T_GROUND = A('the ground begins')
T_INSIDE = A('But inside Jupiter there')
T_INSTR = A('You check your instruments')
T_1BAR = A('approximately one bar')
T_SEALEVEL = A("close to the atmospheric")
T_SAFE = A('sounds almost safe')
T_UNTIL = A('Until you see')
T_M108 = A('Minus one hundred eight')
T_ATMOS = A('And the atmosphere')
T_HYD = A('Mostly hydrogen')
T_NOO2 = A("There's no breathable")
T_FATAL = A('stepping outside would be fatal')
T_STRANGE = A('But something strange')
T_RISING = A('The temperature starts rising')
T_WARMER = A('becoming warmer')
T_WARMDAY = A('warm day on Earth')
T_IMPROVE = A('Sounds like an improvement')
T_CATCH = A("Except there's a catch")
T_PINC = A('The pressure is increasing')
T_DOESNT = A("pressure doesn't care")
T_DENSER = A('becomes denser')
T_FIVE = A('five bars')
T_TEN = A('ten bars')
T_FIFTEEN = A('fifteen')
T_LOOKOUT = A('Now imagine looking')
T_EXPECT = A('You might expect')
T_SURELY = A('Because surely')
T_DOESNTEND = A("But it doesn't end")
T_BEFORE = A('And before we reach')
T_GDISC = A('Galileo discovers')
T_MEASURE = A('its instruments measure')
T_SURPRISING = A('particularly surprising')
T_LESSWATER = A("There's less water")
T_MATTERS = A('That matters because')
T_FORMED = A('how Jupiter formed')
T_MISUNDER = A('So did scientists')
T_DRY = A('Galileo had entered')
T_LIKE = A('It was like trying')
T_DESERT = A('into one desert')
T_ONELOC = A('One location')
T_KEPTF2 = A('But Galileo kept falling')
T_CLIMBED = A('The temperature climbed')
T_20X = A('The pressure passed twenty')
T_CONT = A('And the probe continued')
T_LOST = A('the signal was lost', end=True) - .15
T_LASTED = A('Its scientific data')
T_FAILED = A('Its transmitter failed')
T_DESTROY = A('ultimately destroyed')
T_EXTRA = A("And here's what makes that")
T_LASTDEPTH = A('At the last measured')
T_FRACTION = A('tiny fraction')
T_HUMANITY = A('Humanity had sent')
T_BARELY = A('barely begun exploring')
T_CONTINUE = A("So let's continue")

FICT_TAG = 'FICTIONAL CAPSULE · NOT REAL TECHNOLOGY'

def explorer_look_default(t):
    """Blinks every few seconds."""
    ph = t % 3.7
    return clamp(1 - abs(ph - 0.08) / 0.08) if ph < 0.16 else 0.0

# ------------------------------------------------------------------ S18 atmospheric entry, compression
def s18(c, t):
    lt = t - T_HIT
    k = prog(t, T_HIT, T_DARKNESS)
    bg(c, '#140a14', '#7a3418', '#3a1810')
    speed_lines(c, t, .35 + .3 * k, direction=(.5, .86), n=70, speed=3000, length=200, color='#ffcf9a', width=2)
    heat = lerp(.15, .75, e_in(k))
    sx, sy = shake(t, T_HIT, 2.0, 10)
    x, y = 860 + sx + math.sin(t * 13) * 3 * k, 520 + sy
    # bow shock arcs ahead of the nose (nose points down-right at 55deg)
    ang = 55
    a = math.radians(ang)
    nx, ny = x + math.cos(a) * 120, y + math.sin(a) * 120
    kc = prog(t, T_COMPRESSED - .5, T_COMPRESSED + .8)
    for i in range(4):
        rr = 150 + i * 36
        c.save(); c.translate(nx, ny); c.rotate(ang)
        c.drawArc(skia.Rect(-rr * .5, -rr, rr * .5 + 20, rr), -80, 160, False, P(hexc('#ffd8a8', (.55 - i * .12) * (0.4 + .6 * kc)), stroke=4 - i * .6))
        c.restore()
    if kc > 0:
        for i in range(-3, 4):
            # gas parcels converging on the nose
            ph = (t * 1.6 + i * .17) % 1.0
            d = lerp(520, 170, ph)
            aa = a + i * .16
            px, py = nx + math.cos(aa) * d, ny + math.sin(aa) * d
            arrow(c, px, py, px - math.cos(aa) * 70, py - math.sin(aa) * 70, hexc('#FFF1D6'), 4, 16, kc * (1 - ph) * .9)
        label_line(c, nx + 170, ny + 120, 1420, 760, 'GAS COMPRESSED & HEATED', hexc('#FFF1D6'), k=kc, size=34, sub='A GLOWING SHOCK LAYER FORMS')
    draw_galileo_entry(c, x, y, 1.15, ang, heat=heat, t=t)
    ks = prog(t, T_SHIELD, T_SHIELD + .6)
    if ks > 0:
        label_line(c, x + 40, y + 60, 420, 820, 'HEAT SHIELD', hexc('#FFB347'), k=ks, size=34, sub='ABSORBING ENORMOUS ENERGY')
        hud_panel(c, 1300, 140, 470, 110, 'HEAT LOAD', e_out(ks))
        fill = e_in(prog(t, T_SHIELD, T_DARKNESS + 2))
        rrect(c, 1320, 190, 430 * fill, 34, 8, P(mixc('#FFB347', '#FF3B30', fill)))
    draw_tag(c, 'ILLUSTRATION BASED ON GALILEO ENTRY · 1995', 40, 36, 'hist')

# ------------------------------------------------------------------ S19 brilliant glow (visual peak)
def s19(c, t):
    k = e_in(prog(t, T_DARKNESS, T_DECEL - .2))
    bg(c, '#3a1408', '#a8461c')
    c.drawPaint(P(shader=rad(960, 600, 1300, [mixc('#ffb070', '#fff4dc', k), mixc('#c4541c', '#ffb070', k), hexc('#3a1408')], [0, .45, 1])))
    speed_lines(c, t, .5 + .4 * k, direction=(.5, .86), n=110, speed=5200, length=320, color='#fff1d6', width=3)
    sx, sy = shake(t, T_DARKNESS, 6, 6 + 10 * k, freq=18)
    draw_galileo_entry(c, 960 + sx, 520 + sy, 1.35, 55, heat=1.0, t=t)
    glow(c, 1040, 650, 700 * (0.6 + k), hexc('#fff1d6'), .45 + .4 * k)
    draw_tag(c, 'ILLUSTRATION BASED ON GALILEO ENTRY · 1995', 40, 36, 'hist')

# ------------------------------------------------------------------ S20 228 g
def s20(c, t):
    lt = t - T_DECEL
    bg(c, '#1a0806', '#4a140a')
    k = 1 - e_out(prog(t, T_DECEL, T_DECEL + 3.5))
    speed_lines(c, t, .2 + .5 * k, direction=(.5, .86), n=60, speed=600 + 3000 * k, length=80 + 200 * k, color='#ffb080', width=2)
    sx, sy = shake(t, T_DECEL, 2.2, 38, freq=16)
    sx2, sy2 = shake(t, T_228B, 1.0, 14, freq=20, seed=3)
    c.save(); c.translate(sx + sx2, sy + sy2)
    draw_galileo_entry(c, 520, 560, .9, 55, heat=.7 * k + .2, t=t)
    g = 228 * e_out(prog(t, T_228 - 1.2, T_228 + 1.6))
    draw_gauge(c, 1300, 470, 230, g / 260, 'DECELERATION', f'{int(g)} g', warn_from=.35,
               tick_labels=['0', '', '', '', '', '130', '', '', '', '', '260'])
    c.restore()
    kb = prog(t, T_228B, T_228B + .4)
    if t > T_228 + 1.2:
        pulse = 1 + .12 * math.exp(-max(0, t - T_228B) * 5) * (t > T_228B)
        c.save(); c.translate(1300, 900 - 30); c.scale(pulse, pulse)
        draw_text(c, "× EARTH'S GRAVITY", 0, 0, font(40, 'black'), hexc('#FFF1D6'), 'center', alpha=e_out(prog(t, T_228 + 1.2, T_228 + 1.8)), shadow=1)
        c.restore()
    flash(c, (1 - e_out(prog(t, T_DECEL, T_DECEL + .5))) * .6, '#ff6040')
    flash(c, (1 - e_out(prog(t, T_228B, T_228B + .4))) * .25 * (t > T_228B), '#ff3b30')
    draw_tag(c, 'GALILEO PROBE · MEASURED PEAK ≈ 228 g', 40, 36, 'hist')

# ------------------------------------------------------------------ S21 a human couldn't survive
def _ico_craft(c, x, y, s, t, a):
    rrect(c, x - 60 * s, y - 80 * s, 120 * s, 160 * s, 40 * s, P(hexc('#a9b0bb', a)))
    c.drawCircle(x, y - 20 * s, 26 * s, P(hexc('#2b4a66', a)))
    c.drawRect(skia.Rect(x - 60 * s, y + 30 * s, x + 60 * s, y + 42 * s), P(hexc('#6FD3FF', a)))
def _ico_suit(c, x, y, s, t, a):
    draw_explorer_bust(c, x, y - 30 * s, 60 * s, alpha=a, brow=-1, mouth='grit', look=(0, 0))
def _ico_hold(c, x, y, s, t, a):
    c.drawRect(skia.Rect(x - 120 * s, y - 70 * s, x + 120 * s, y - 56 * s), P(hexc('#a9b0bb', a)))
    for side in (-1, 1):
        c.drawLine(x + side * 30 * s, y - 60 * s, x + side * 40 * s, y + 10 * s, P(hexc(SUIT, a), stroke=22 * s, cap='round'))
        c.drawCircle(x + side * 30 * s, y - 62 * s, 16 * s, P(hexc(SUIT, a)))
    c.drawCircle(x, y + 40 * s, 48 * s, P(hexc(SUIT, a)))
    c.drawCircle(x, y + 40 * s, 48 * s, P(hexc('#6a655a', a), stroke=3))

def s21(c, t):
    bg(c, '#14080a', '#05070f')
    draw_text(c, "A HUMAN COULDN'T SURVIVE 228 g", 960, 190, font(56, 'black'), hexc('#FFF1D6'), 'center', alpha=e_out(prog(t, T_HUMAN, T_HUMAN + .5)), shadow=1)
    items = [(T_ORDINARY, 'ORDINARY SPACECRAFT', _ico_craft), (T_SUIT, 'NORMAL SPACE SUIT', _ico_suit), (T_HOLD, 'HOLDING ON', _ico_hold)]
    for i, (tt, lab, fn) in enumerate(items):
        k = prog(t, tt, tt + .45)
        if k <= 0:
            continue
        x = 360 + i * 600; y = 560
        card(c, x - 230, y - 230, 460, 470, e_out(k))
        fn(c, x, y - 20, 1.0, t, e_out(k))
        draw_text(c, lab, x, y + 200, font(32, 'black'), hexc('#FFF1D6'), 'center', alpha=e_out(k))
        draw_x(c, x, y - 20, 220, prog(t, tt + .35, tt + .8), alpha=.92)

# ------------------------------------------------------------------ S22 Galileo robotic probe: chute, transmitting
def s22(c, t):
    lt = t - T_ROBOT
    cloud_world(c, t, fall=40, drift=-20, tint=(1, .8, .56), bg_top='#2a1830', bg_bot='#c27a44', bg_mid='#6b3a30')
    sep = e_in(prog(t, T_WORST + .6, T_CHUTE + .3))
    chute = prog(t, T_CHUTE, T_CHUTE + 1.0)
    x, y = 900, 560
    if chute <= 0:
        draw_galileo_entry(c, x, y, 1.0, 90, heat=.25 * (1 - sep), t=t)
        if sep > 0:
            pass
    else:
        # heat shield falling away
        draw_galileo_entry(c, x + 30 * chute, y + 600 * e_in(prog(t, T_CHUTE, T_CHUTE + 2.5)), 1.0, 90 + 40 * chute, heat=0, t=t, alpha=1 - prog(t, T_CHUTE + 1.5, T_CHUTE + 2.5))
        sway = math.sin(t * 1.8) * 6 * chute
        draw_galileo_descent(c, x, y - 40 * e_out(chute), 1.15, chute=chute, sway=sway, t=t, transmit=prog(t, T_TRANSMIT, T_TRANSMIT + .6))
    kr = prog(t, T_ROBOT + .2, T_ROBOT + .8)
    if kr > 0:
        draw_tag(c, 'ROBOTIC PROBE · BUILT TO SURVIVE ENTRY', 1300, 160, 'hist', alpha=e_out(kr))
    ko = prog(t, T_TRANSMIT, T_TRANSMIT + .8)
    if ko > 0:
        draw_text(c, 'DATA → GALILEO ORBITER (RELAY TO EARTH)', 960, 120, mono(24, 'semi'), hexc('#9FE3FF'), 'center', alpha=e_out(ko))
    draw_tag(c, HIST_TAG, 40, 36, 'hist')

# ------------------------------------------------------------------ S23 fictional capsule reveal
def s23(c, t):
    lt = t - T_FICT
    calm = e_out(prog(t, T_SHAKESTOP, T_SHAKESTOP + 1.0))
    gf = e_io(prog(t, T_GLOWFADE, T_FIRST + .3))
    bg(c, '#3a1408', '#8a4a26')
    c.drawPaint(P(hexc('#ffb070', .55 * (1 - gf))))
    cloud_world(c, t, fall=lerp(700, 60, calm), drift=0, tint=(1, .78, .52), bg_draw=False, alpha=.85)
    amp = 14 * (1 - calm)
    sx, sy = math.sin(t * 41) * amp, math.cos(t * 37) * amp * .6
    draw_capsule(c, 960 + sx, 540 + sy, 1.35, 0, 1, t, heat=.9 * (1 - gf),
                 face=dict(blink=1.0 if t < T_SHAKESTOP + .4 else explorer_look_default(t), brow=-1 + calm, mouth='grit' if calm < .5 else 'neutral', look=(0, 0)))
    k = prog(t, T_FICT + .4, T_FICT + 1.0)
    draw_tag(c, FICT_TAG, 40, 36, 'fict', alpha=e_out(k))
    if k > 0:
        label_line(c, 1080, 400, 1400, 260, 'YOUR FICTIONAL CAPSULE', hexc('#6FD3FF'), k=k, size=36, sub='IMAGINARY PROTECTION FROM THOSE FORCES')

# ------------------------------------------------------------------ S24 surrounded by clouds, no horizon
def s24(c, t):
    lt = t - T_FIRST
    look_y = keys(t, [(T_ABOVE - .3, 0), (T_ABOVE + .2, -1), (T_BESIDE - .2, -1), (T_BESIDE + .3, 0), (T_BELOW - .2, 0), (T_BELOW + .3, 1), (T_MISSING, 1), (T_MISSING + .6, 0)])
    look_x = keys(t, [(T_BESIDE - .2, 0), (T_BESIDE + .3, 1), (T_BELOW - .2, 1), (T_BELOW + .3, 0)])
    pull = e_io(prog(t, T_MISSING, T_HORIZON + .6))
    cam_y = look_y * 260 * (1 - pull)
    cam_x = look_x * 260 * (1 - pull)
    cloud_world(c, t, fall=55, drift=-12, ox=-cam_x, oy=-cam_y, tint=(1, .8, .56), bg_top='#efc58f', bg_bot='#a0582e', bg_mid='#d89a5c', depth_dark=.2)
    s = lerp(1.25, .32, pull)
    cx = 960 + cam_x * .3; cy = 560 + cam_y * .3
    draw_capsule(c, cx, cy, s, 0, 1, t, face=dict(look=(look_x, look_y), blink=explorer_look_default(t), brow=.6 if pull < .5 else .3, mouth='o' if T_SURROUND < t < T_BELOW + 1.5 else 'neutral'))
    for tt, txt, (lx, ly) in ((T_ABOVE, 'ABOVE: CLOUDS', (960, 150)), (T_BESIDE, 'BESIDE: CLOUDS', (1560, 540)), (T_BELOW, 'BELOW: MORE CLOUDS', (960, 880))):
        a = fade_window(t, tt, T_MISSING + .2, .3, .4)
        draw_text(c, txt, lx, ly, mono(32, 'bold'), hexc('#FFF1D6'), 'center', alpha=a, shadow=1)
    kh = prog(t, T_HORIZON - .1, T_HORIZON + .4)
    if kh > 0:
        dashed(c, [(80, 540), (1840, 540)], hexc('#FFF1D6'), 3, alpha=.6 * e_out(kh) * (.5 + .5 * math.sin(t * 5)), phase=t * 30)
        hud_panel(c, 1260, 150, 520, 120, 'HORIZON', e_out(kh), warn=True)
        draw_text(c, 'NOT FOUND', 1290, 240, mono(52, 'bold'), hexc(PAL['danger']), alpha=e_out(kh))
    draw_tag(c, FICT_TAG, 40, 36, 'fict')

# ------------------------------------------------------------------ S25 Earth horizon vs Jupiter
def s25(c, t):
    k = e_out(prog(t, T_ONEARTH, T_ONEARTH + .8))
    split = W / 2
    c.save(); c.clipRect(skia.Rect(0, 0, split - 3, H))
    bg(c, '#4f8fd8', '#cfe6ff')
    c.drawRect(skia.Rect(0, 620, split, H), P(shader=lin((0, 620), (0, H), [hexc('#6aa04a'), hexc('#2f5a22')])))
    for i in range(6):
        c.drawCircle(80 + i * 170, 625, 70 + (i % 3) * 25, P(hexc('#4a7d38')))
    c.drawLine(0, 620, split, 620, P(hexc('#FFFFFF', .9), stroke=3))
    label_line(c, 700, 620, 760, 470, 'HORIZON', hexc('#0b1230'), k=prog(t, T_ONEARTH + .8, T_GROUND + .5), size=36)
    draw_text(c, 'SKY', 200, 320, font(44, 'black'), hexc('#ffffff'), 'center', alpha=e_out(prog(t, T_ONEARTH + 1, T_ONEARTH + 1.5)))
    draw_text(c, 'GROUND', 200, 820, font(44, 'black'), hexc('#ffffff'), 'center', alpha=e_out(prog(t, T_GROUND, T_GROUND + .5)))
    draw_text(c, 'EARTH', 480, 110, font(44, 'black'), hexc('#0b1230'), 'center')
    c.restore()
    c.save(); c.clipRect(skia.Rect(split + 3, 0, W, H)); c.translate(split, 0)
    c.save(); c.scale(.5, 1)
    cloud_world(c, t, fall=40, tint=(1, .78, .52), bg_top='#E3B47A', bg_mid='#a8582a', bg_bot='#3a1408', depth_dark=.5)
    c.restore()
    ki = prog(t, T_INSIDE, T_INSIDE + .6)
    draw_text(c, 'NO HORIZON', 480, 560, font(52, 'black'), hexc('#FFF1D6'), 'center', alpha=e_out(ki), shadow=1)
    draw_text(c, 'NO LANDSCAPE BELOW', 480, 620, mono(24, 'semi'), hexc('#FFF1D6'), 'center', alpha=e_out(ki), shadow=1)
    draw_text(c, 'JUPITER', 480, 110, font(44, 'black'), hexc('#FFF1D6'), 'center', shadow=1)
    c.restore()
    c.drawRect(skia.Rect(split - 3, 0, split + 3, H), P(hexc('#070B1A')))

# ------------------------------------------------------------------ S26 instruments: 1 bar, -108 C, H/He, fatal
def s26(c, t):
    lt = t - T_INSTR
    cold = e_io(prog(t, T_M108 - .3, T_M108 + 1.2))
    cloud_world(c, t, fall=40, drift=-10, tint=(lerp(1, .8, cold), lerp(.78, .8, cold), lerp(.52, .75, cold)), bg_top='#d9a066', bg_bot='#6b3a20', alpha=1)
    c.drawPaint(P(hexc('#06101f', .55)))
    # cockpit: explorer bust left, lit by instruments
    mood = keys(t, [(T_SAFE, 0), (T_SAFE + .3, 1), (T_UNTIL, 1), (T_UNTIL + .3, -1)])
    mouth = 'smile' if T_SAFE < t < T_UNTIL else 'frown' if t > T_UNTIL else 'neutral'
    if t > T_FATAL: mouth = 'grit'
    lookx = .7 if t > T_INSTR + .3 else 0
    draw_explorer_bust(c, 430, 470, 170, look=(lookx, .1), blink=explorer_look_default(t), brow=mood if mood > 0 else mood, mouth=mouth, light='#9FE3FF', light_amt=.7, sweat=prog(t, T_FATAL, T_FATAL + .5))
    # instrument column right
    x = 960
    k1 = prog(t, T_1BAR - .3, T_1BAR + .3)
    if k1 > 0:
        draw_gauge(c, x + 170, 330, 150, .1 * e_out(k1), 'PRESSURE', f'{1.0 * e_out(k1):.1f} bar', alpha=e_out(k1), tick_labels=['0', '', '', '', '', '5', '', '', '', '', '10'],
                   sub='≈ EARTH SEA LEVEL' if t > T_SEALEVEL else None)
    k2 = prog(t, T_M108 - .4, T_M108 + .2)
    if k2 > 0:
        temp = -108 * e_out(prog(t, T_M108 - .4, T_M108 + 1.0))
        draw_thermo(c, x + 520, 220, 280, .08, f'{temp:.0f}°C', alpha=e_out(k2), marks=[(.08, '-108'), (.5, '0'), (.9, '+50')])
    k3 = prog(t, T_HYD - .2, T_HYD + .5)
    if k3 > 0:
        hud_panel(c, x, 560, 760, 220, 'ATMOSPHERE (GALILEO, BY VOLUME)', e_out(k3))
        rows = [('H₂  HYDROGEN', .86, '#FFF1D6', '~86%'), ('He  HELIUM', .136, '#E3B47A', '~14%')]
        for i, (lab, v, col, txt) in enumerate(rows):
            yy = 630 + i * 50
            draw_text(c, lab, x + 24, yy + 8, mono(22, 'semi'), hexc('#FFFFFF'), alpha=e_out(k3))
            rrect(c, x + 270, yy - 14, 380 * v * e_out(k3), 26, 6, P(hexc(col, e_out(k3))))
            draw_text(c, txt, x + 280 + 380 * v * e_out(k3), yy + 8, mono(22, 'bold'), hexc('#FFFFFF'), alpha=e_out(k3))
        ko = prog(t, T_NOO2, T_NOO2 + .4)
        if ko > 0:
            draw_text(c, 'O₂  BREATHABLE OXYGEN', x + 24, 738, mono(22, 'semi'), hexc(PAL['danger']), alpha=e_out(ko))
            draw_text(c, 'NONE', x + 380, 738, mono(26, 'bold'), hexc(PAL['danger']), alpha=e_out(ko))
    kf = prog(t, T_FATAL + .2, T_FATAL + .6)
    if kf > 0:
        hud_panel(c, 300, 790, 640, 90, None, e_out(kf), warn=True)
        draw_text(c, '⚠ OUTSIDE: LETHAL', 620, 852, font(44, 'black'), hexc(PAL['danger']), 'center', alpha=e_out(kf) * (.8 + .2 * math.sin(t * 8)))
    # frost on screen edges when cold
    if cold > 0:
        draw_img(c, vignette_img(.9), 0, 0, W, H, cold * .6, cf=tint_cf(0, 0, 0))
        c.drawPaint(P(shader=rad(960, 540, 1150, [hexc('#9FE3FF', 0), hexc('#9FE3FF', 0), hexc('#cfefff', .28 * cold)], [0, .7, 1])))
    draw_tag(c, FICT_TAG, 40, 36, 'fict')

# ------------------------------------------------------------------ S27 temperature rises, pressure increases
def hud_values(t):
    """Approx. Galileo-like profile: (pressure bar, temp C, depth km below 1-bar level). Values approximate."""
    kf = [(T_STRANGE, (1.0, -108, 0)), (T_WARMDAY + .5, (6.0, 25, 70)), (T_FIVE, (5.0, 10, 60)),
          (T_TEN, (10.0, 70, 95)), (T_FIFTEEN, (15.0, 110, 125)), (T_FIFTEEN + 1.5, (15.0, 110, 125))]
    if t < T_FIVE:
        p = keys(t, [(T_STRANGE, 1.0), (T_PINC, 4.0), (T_DENSER + .5, 4.8)])
        tc = keys(t, [(T_RISING, -108), (T_WARMDAY + .3, 25), (T_DENSER, 40)])
        d = keys(t, [(T_STRANGE, 0), (T_DENSER + .5, 58)])
        return p, tc, d
    p = keys(t, [(T_FIVE, 5.0), (T_TEN, 10.0), (T_FIFTEEN, 15.0)], e_out)
    tc = keys(t, [(T_FIVE, 45), (T_TEN, 80), (T_FIFTEEN, 115)], e_out)
    d = keys(t, [(T_FIVE, 60), (T_TEN, 100), (T_FIFTEEN, 125)], e_out)
    return p, tc, d

def hud_stack(c, t, alpha=1.0):
    p, tc, d = hud_values(t)
    hud_readout(c, 1440, 120, 380, 'PRESSURE', f'{p:.1f}', 'bar', alpha, warn=p > 9, size=40)
    hud_readout(c, 1440, 250, 380, 'TEMPERATURE', f'{tc:+.0f}', '°C', alpha, size=40)
    hud_readout(c, 1440, 380, 380, 'DEPTH (≈, BELOW 1-BAR)', f'{d:.0f}', 'km', alpha, size=40)

def s27(c, t):
    lt = t - T_STRANGE
    p, tc, d = hud_values(t)
    dk = clamp((p - 1) / 15)
    cloud_world(c, t, fall=160, drift=-10, tint=(1, .74 - .1 * dk, .5 - .12 * dk), bg_top=PAL['jlight'], bg_mid='#a8582a', bg_bot='#3a1408', depth_dark=.3 + .4 * dk, haze=.15 + .35 * dk)
    mouth = 'smile' if T_IMPROVE - .2 < t < T_CATCH + .2 else ('frown' if t > T_CATCH + .2 else 'neutral')
    brow = 1 if T_IMPROVE - .2 < t < T_CATCH else (-1 if t > T_CATCH else 0)
    sq = e_out(prog(t, T_DOESNT, T_DOESNT + 1.0))
    draw_capsule(c, 800, 540, 1.25, 0, 1, t, face=dict(look=(.5, 0), blink=explorer_look_default(t), brow=brow, mouth=mouth))
    if sq > 0:
        for i in range(10):
            a = i / 10 * math.tau + t * .2
            r0 = 420 - 40 * ((t * 1.3 + i * .13) % 1.0)
            arrow(c, 800 + math.cos(a) * r0, 540 + math.sin(a) * r0 * .9, 800 + math.cos(a) * (r0 - 110), 540 + math.sin(a) * (r0 - 110) * .9, hexc('#FFF1D6'), 5, 20, .75 * sq)
        draw_text(c, 'PRESSURE PUSHES FROM EVERY SIDE', 800, 980 - 70, mono(26, 'bold'), hexc('#FFF1D6'), 'center', alpha=sq, shadow=1)
    hud_stack(c, t)
    kw = fade_window(t, T_WARMDAY - .1, T_CATCH + .3, .3, .4)
    if kw > 0:
        draw_tag(c, '≈ A WARM DAY ON EARTH', 1440, 530, 'concept', alpha=kw)
    draw_tag(c, FICT_TAG, 40, 36, 'fict')

# ------------------------------------------------------------------ S28 five, ten, fifteen bars
def s28(c, t):
    p, tc, d = hud_values(t)
    cloud_world(c, t, fall=300, tint=(.9, .6, .4), bg_top='#a8582a', bg_bot='#2a0e06', depth_dark=.7, haze=.45)
    sx, sy = 0, 0
    for tt in (T_FIVE, T_TEN, T_FIFTEEN):
        a, b = shake(t, tt, .45, 12)
        sx += a; sy += b
    c.save(); c.translate(sx, sy)
    draw_capsule(c, 960, 600, 1.0, 0, 1, t, face=dict(look=(0, -.4), brow=-1, mouth='grit', blink=0))
    c.restore()
    for tt, txt, xx in ((T_FIVE, '5 BAR', 420), (T_TEN, '10 BAR', 960), (T_FIFTEEN, '15 BAR', 1500)):
        big_number(c, txt, xx, 250, 110, hexc('#FFF1D6') if txt != '15 BAR' else hexc(PAL['danger']), t, tt, glow_=.4)
    hud_stack(c, t, .0)
    draw_tag(c, FICT_TAG, 40, 36, 'fict')

# ------------------------------------------------------------------ S29 expecting an ocean
def s29(c, t):
    lt = t - T_LOOKOUT
    cloud_world(c, t, fall=120, tint=(.9, .62, .42), bg_top='#a8582a', bg_bot='#2a0e06', depth_dark=.6, haze=.35)
    # explorer looks down through window
    draw_explorer_bust(c, 960, 360, 150, look=(0, 1), blink=explorer_look_default(t), brow=.4, mouth='neutral', light='#ffb070', light_amt=.5)
    k = prog(t, T_EXPECT + .3, T_EXPECT + 1.5)
    gone = e_io(prog(t, T_DOESNTEND, T_DOESNTEND + 1.6))
    if k > 0:
        a = e_out(k) * (1 - gone)
        for j in range(4):
            pa = skia.Path(); yy = 800 + j * 40
            pa.moveTo(0, yy)
            for i in range(0, W + 40, 40):
                pa.lineTo(i, yy + 10 * math.sin(i * .01 + t * 2 + j))
            p_ = P(hexc('#6FD3FF', a * (.8 - j * .15)), stroke=3)
            p_.setPathEffect(skia.DashPathEffect.Make([20, 14], 0))
            c.drawPath(pa, p_)
        draw_tag(c, 'WHAT YOU MIGHT EXPECT: AN OCEAN SURFACE', 960, 720, 'concept', align='center', alpha=a)
    if gone > 0:
        draw_text(c, "BUT IT DOESN'T END THE WAY YOU EXPECT", 960, 860, font(46, 'black'), hexc('#FFF1D6'), 'center', alpha=fade_window(t, T_DOESNTEND + .3, T_BEFORE + 1.2, .4, .4), shadow=1)
    draw_tag(c, FICT_TAG, 40, 36, 'fict')

# ------------------------------------------------------------------ S30 Galileo measures
def s30(c, t):
    lt = t - T_GDISC
    cloud_world(c, t, fall=60, drift=-15, tint=(1, .78, .52), bg_top='#d9a066', bg_bot='#6b3a20', depth_dark=.3)
    # sepia archival treatment
    sway = math.sin(t * 1.6) * 5
    draw_galileo_descent(c, 760, 580, 1.2, chute=1, sway=sway, t=t, transmit=1)
    km = prog(t, T_MEASURE, T_MEASURE + .6)
    if km > 0:
        for i in range(16):
            ph = (t * .8 + i / 16) % 1.0
            a = i / 16 * math.tau
            r = lerp(300, 60, ph)
            c.drawCircle(760 + math.cos(a) * r, 600 + math.sin(a) * r * .7, 5, P(hexc('#9FE3FF', km * (1 - ph))))
        hud_panel(c, 1240, 300, 540, 300, 'PROBE INSTRUMENTS', e_out(km), color='#FFB347')
        for i, lab in enumerate(['TEMPERATURE', 'PRESSURE', 'COMPOSITION', 'CLOUDS', 'WINDS']):
            draw_text(c, '▸ ' + lab, 1270, 380 + i * 42, mono(24, 'semi'), hexc('#FFF1D6'), alpha=e_out(prog(t, T_MEASURE + i * .25, T_MEASURE + .3 + i * .25)))
    ks = prog(t, T_SURPRISING, T_SURPRISING + .4)
    if ks > 0:
        draw_text(c, '!', 1700, 380, font(140, 'black'), hexc('#FFB347'), 'center', alpha=e_out(ks), glow=.5)
    c.drawPaint(P(hexc('#704214', .12)))
    draw_tag(c, HIST_TAG, 40, 36, 'hist')

# ------------------------------------------------------------------ S31 less water, dry region (hot spot)
def s31(c, t):
    lt = t - T_LESSWATER
    bg(c, '#140d08', '#05070f')
    mapk = e_io(prog(t, T_DRY - .5, T_DRY + .8))
    if mapk < 1:
        a = 1 - mapk
        x0, y0 = 520, 820
        card(c, 300, 180, 1320, 720, a)
        draw_text(c, 'WATER VAPOR AT THE PROBE SITE', 960, 260, font(40, 'black'), hexc('#FFF1D6'), 'center', alpha=a)
        ke = e_out(prog(t, T_LESSWATER + .2, T_LESSWATER + 1.0)); km = e_out(prog(t, T_LESSWATER + 1.2, T_LESSWATER + 2.0))
        rrect(c, 560, 780 - 440 * ke, 240, 440 * ke, 10, P(hexc('#6FD3FF', .35 * a)))
        rrect(c, 560, 780 - 440 * ke, 240, 440 * ke, 10, P(hexc('#6FD3FF', a), stroke=3))
        draw_text(c, 'EXPECTED', 680, 830, mono(26, 'bold'), hexc('#6FD3FF'), 'center', alpha=a * ke)
        rrect(c, 1120, 780 - 120 * km, 240, 120 * km, 10, P(hexc('#FFB347', a)))
        draw_text(c, 'MEASURED', 1240, 830, mono(26, 'bold'), hexc('#FFB347'), 'center', alpha=a * km)
        draw_text(c, 'MUCH LESS', 1240, 780 - 120 * km - 24, font(34, 'black'), hexc('#FFFFFF'), 'center', alpha=a * km)
        draw_text(c, 'SCHEMATIC · NOT EXACT VALUES', 1580, 870, mono(16, 'medium'), hexc(HUDC), 'right', alpha=a * .8)
        kf = fade_window(t, T_FORMED - .3, T_DRY - .3, .4, .3)
        if kf > 0:
            draw_tag(c, 'WATER ABUNDANCE → CLUES TO HOW JUPITER FORMED', 960, 120, 'concept', align='center', alpha=kf)
        kq = fade_window(t, T_MISUNDER, T_DRY, .3, .3)
        draw_text(c, '?', 1240, 470, font(160, 'black'), hexc('#FFB347'), 'center', alpha=kq, glow=.4)
    if mapk > 0:
        a = mapk
        space(c, t, alpha=a)
        R = 420
        draw_jupiter(c, 960, 560, R, rot=1.0 + t * .01, alpha=a)
        hx, hy = 960 - 60, 560 - R * math.sin(math.radians(6.5))
        c.drawOval(skia.Rect(hx - 50, hy - 16, hx + 50, hy + 16), P(hexc('#2a1208', .75 * a), blur=6))
        kk = prog(t, T_DRY + .5, T_DRY + 1.2)
        label_line(c, hx, hy, 1500, 300, 'PROBE ENTRY SITE', hexc('#FFB347'), alpha=a, k=kk, size=36, sub='A RARE, UNUSUALLY DRY "HOT SPOT"')
    draw_tag(c, HIST_TAG, 40, 36, 'hist')

# ------------------------------------------------------------------ S32 weather station in a desert
def s32(c, t):
    lt = t - T_LIKE
    z = e_io(prog(t, T_LIKE + .5, T_DESERT + .2))
    space(c, t)
    R = lerp(330, 900, z)
    cx, cy = 960, lerp(560, 560 + 900 * .2, z)
    draw_earth(c, cx, cy, R, rot=0.6, max_grid=900)
    if z > .8:
        a = prog(z, .8, 1)
        c.drawOval(skia.Rect(760, 360, 1160, 520), P(hexc('#d8b07a', .85 * a), blur=20))
        # weather station
        sx, sy = 960, 430
        c.drawLine(sx, sy, sx, sy - 120, P(hexc('#e8e8e8', a), stroke=5))
        c.drawRect(skia.Rect(sx - 26, sy - 90, sx + 26, sy - 50), P(hexc('#ffffff', a)))
        for i in range(3):
            ang = t * 6 + i * 2.09
            c.drawLine(sx, sy - 120, sx + math.cos(ang) * 40, sy - 120 + math.sin(ang) * 10, P(hexc('#cccccc', a), stroke=3))
        label_line(c, sx + 30, sy - 70, 1400, 260, 'ONE WEATHER STATION', hexc('#FFF1D6'), alpha=a, k=prog(t, T_DESERT, T_DESERT + .6), size=36, sub='IN ONE DESERT')
    ko = prog(t, T_ONELOC, T_ONELOC + .5)
    if ko > 0:
        card(c, 560, 760, 800, 110, e_out(ko))
        draw_text(c, '1 LOCATION ≠ THE WHOLE PLANET', 960, 830, font(44, 'black'), hexc('#FFF1D6'), 'center', alpha=e_out(ko))
    draw_tag(c, 'ANALOGY', 40, 36, 'concept')

# ------------------------------------------------------------------ S33 Galileo keeps falling, signal lost
def s33(c, t):
    lt = t - T_KEPTF2
    k = prog(t, T_KEPTF2, T_LOST)
    cloud_world(c, t, fall=200, tint=(.9, .62, .42), bg_top='#a8582a', bg_bot='#2a0e06', depth_dark=.4 + .4 * k, haze=.2 + .4 * k)
    draw_galileo_descent(c, 820, 560, 1.0, chute=1, sway=math.sin(t * 2) * 4, t=t, transmit=1 if t < T_LOST - .3 else 0, heat=k * .6)
    p = keys(t, [(T_KEPTF2, 15), (T_20X, 20), (T_CONT, 22)])
    tc = keys(t, [(T_KEPTF2, 110), (T_CLIMBED + 1.0, 140), (T_CONT, 152)])
    d = keys(t, [(T_KEPTF2, 125), (T_CONT + 1, 150)])
    hud_readout(c, 1440, 120, 380, 'PRESSURE', f'{p:.0f}', 'bar', 1, warn=p >= 20, size=40, color='#FFB347')
    hud_readout(c, 1440, 250, 380, 'TEMPERATURE', f'{tc:+.0f}', '°C', 1, size=40, color='#FFB347')
    hud_readout(c, 1440, 380, 380, 'DEPTH (≈, BELOW 1-BAR)', f'{d:.0f}', 'km', 1, size=40, color='#FFB347')
    k20 = prog(t, T_20X, T_20X + .5)
    if k20 > 0:
        draw_tag(c, '> 20× EARTH SEA-LEVEL PRESSURE', 1440, 520, 'hist', alpha=e_out(k20))
    lost = t >= T_LOST - .3
    signal_bars(c, 1460, 640, 0 if lost else 1, lost=lost)
    draw_text(c, 'SIGNAL LOST' if lost else 'TRANSMITTING', 1560, 636, mono(22, 'bold'), hexc(PAL['danger']) if lost else hexc(PAL['ok']), alpha=1)
    if lost:
        # static burst
        rng = np.random.default_rng(int(t * 60))
        a = 1 - prog(t, T_LOST - .3, T_LOST)
        for i in range(160):
            y = rng.random() * H
            c.drawRect(skia.Rect(0, y, W, y + rng.random() * 6), P(rgba(255, 255, 255, a * .35 * rng.random())))
    draw_tag(c, HIST_TAG, 40, 36, 'hist')

# ------------------------------------------------------------------ S34 58 minutes, destroyed
def s34(c, t):
    lt = t - T_LOST
    bg(c, '#0a0506', '#000000')
    kd = e_io(prog(t, T_DESTROY - .5, T_EXTRA))
    glow(c, 960, 700, 500, hexc('#7a2a10'), .5)
    draw_galileo_descent(c, 960, lerp(420, 640, kd), .8, chute=1, alpha=(1 - kd) * .8, t=t)
    k = prog(t, T_LASTED, T_LASTED + 2.5)
    if k > 0:
        x0, x1, y = 460, 1460, 200
        c.drawLine(x0, y, x1, y, P(hexc('#ffffff', .2), stroke=6, cap='round'))
        c.drawLine(x0, y, lerp(x0, x1, e_io(k)), y, P(hexc('#FFB347'), stroke=6, cap='round'))
        draw_text(c, '0 MIN', x0, y + 44, mono(22, 'semi'), hexc('#FFF1D6'), 'center')
        draw_text(c, '≈ 58 MIN OF SCIENCE DATA', x1, y + 44, mono(22, 'semi'), hexc('#FFB347'), 'center', alpha=e_out(prog(k, .8, 1)))
    kf = prog(t, T_FAILED, T_FAILED + .5)
    if kf > 0:
        draw_text(c, 'TRANSMITTER FAILED · PROBE LATER DESTROYED BY HEAT AND PRESSURE', 960, 900 - 40, mono(22, 'semi'), hexc('#FFF1D6'), 'center', alpha=e_out(kf) * .9)
    draw_tag(c, HIST_TAG, 40, 36, 'hist')

# ------------------------------------------------------------------ S35 tiny fraction
def s35(c, t):
    lt = t - T_EXTRA
    space(c, t)
    z = keys(t, [(T_EXTRA, 1.0), (T_FRACTION + .2, 1.0), (T_HUMANITY, 1.15)])
    R = 400 * z
    cx, cy = 960, 560
    unknown = e_io(prog(t, T_BARELY - .5, T_BARELY + 1))
    draw_cross_section(c, cx, cy, R, wedge=(-90, 0), rot=2.0, dark_unknown=.85, core_alpha=0, show_metal=0, metal_glow=0, t=t)
    dep = 150 / 69911 * R
    c.drawLine(cx + 3, cy - R, cx + 3, cy - R + 3, P(hexc(PAL['danger']), stroke=4))
    glow(c, cx + 3, cy - R + 2, 30, hexc(PAL['danger']), .9)
    k = prog(t, T_LASTDEPTH, T_LASTDEPTH + .6)
    label_line(c, cx + 3, cy - R + 2, cx + 380, cy - R - 20 if cy - R > 120 else 140, 'GALILEO STOPPED HERE', hexc('#FF8A7A'), k=k, size=34, sub='≈ 150 km DOWN')
    kf = prog(t, T_FRACTION, T_FRACTION + .5)
    if kf > 0:
        # depth bar comparison
        x0, y0, L = 300, 930 - 60, 1320
        c.drawRect(skia.Rect(x0, y0, x0 + L, y0 + 22), P(hexc('#3D5A9E', .5 * e_out(kf))))
        c.drawRect(skia.Rect(x0, y0, x0 + max(3, L * 150 / 69911), y0 + 22), P(hexc(PAL['danger'], e_out(kf))))
        draw_text(c, 'CLOUD TOPS', x0, y0 - 14, mono(18, 'semi'), hexc('#FFF1D6'), alpha=e_out(kf))
        draw_text(c, 'CENTER ≈ 70,000 km', x0 + L, y0 - 14, mono(18, 'semi'), hexc('#FFF1D6'), 'right', alpha=e_out(kf))
        draw_text(c, 'GALILEO: ≈ 0.2%', x0, y0 + 56, mono(22, 'bold'), hexc('#FF8A7A'), alpha=e_out(kf))
    if unknown > 0:
        draw_text(c, '?', cx + R * .4, cy - R * .25, font(170, 'black'), hexc('#6FD3FF'), 'center', alpha=unknown, glow=.5)
        draw_text(c, 'UNEXPLORED', cx + R * .4, cy - R * .25 + 60, mono(24, 'bold'), hexc('#6FD3FF'), 'center', alpha=unknown)

SHOTS2 = [
    (T_HIT, s18, ('flash', .35)),
    (T_DARKNESS, s19, ('fade', .6)),
    (T_DECEL, s20, ('cut', 0)),
    (T_HUMAN, s21, ('black', .4)),
    (T_ROBOT, s22, ('fade', .5)),
    (T_FICT, s23, ('black', .6)),
    (T_FIRST, s24, ('fade', .6)),
    (T_ONEARTH, s25, ('fade', .4)),
    (T_INSTR, s26, ('fade', .5)),
    (T_STRANGE, s27, ('fade', .6)),
    (T_FIVE - .15, s28, ('cut', 0)),
    (T_LOOKOUT, s29, ('fade', .5)),
    (T_GDISC, s30, ('fade', .7)),
    (T_LESSWATER, s31, ('fade', .4)),
    (T_LIKE, s32, ('whip', .35)),
    (T_KEPTF2, s33, ('fade', .5)),
    (T_LOST, s34, ('cut', 0)),
    (T_EXTRA, s35, ('black', .8)),
]
