# Shots 01-17 : hook, Galileo summary, the questions, nowhere to land, scale, Juno, speed.
from common import *

A = at  # alias
T_DROPPED = A('dropped a spacecraft')
T_SURV_ENTRY = A('It survived the entry')
T_WINDS = A('It survived winds')
T_KEPT = A('And it kept falling')
T_NOGROUND = A('no ground')
T_THEN58 = A('Then fifty eight')
T_ENDED = A('transmission ended')
T_BUTHERE = A("But here's the disturbing")
T_SCRATCH = A('barely scratched')
T_INTERIOR = A("Jupiter's enormous interior")
T_KEPTF = A('kept falling', after=30)
T_SOLID = A('Would you eventually hit')
T_OCEAN = A('Would you sink')
T_CENTER = A('Or could you actually reach')
T_LARGEST = A('largest planet', after=40)
T_FINDOUT = A('To find out')
T_REAL = A('follow the real spacecraft')
T_NOSPACE = A('go somewhere no spacecraft')
T_BUTFIRST = A("But first there's")
T_DIFFERENT = A('completely different')
T_EARTHFALL = A('falling toward Earth')
T_NOWHERE = A("There's nowhere to land")
T_PEACEFUL = A('From space')
T_STRIPES = A('Beautiful orange')
T_WRAP = A('wrap around')
T_REDOVAL = A('and that enormous red oval')
T_GRS = A("That's the great red spot")
T_CENTURIES = A('existed for centuries')
T_NOTGROUND = A("But those stripes aren't")
T_CLOUDS = A('They are clouds')
T_MOVING = A('they are moving')
T_WINDRACE = A('winds race')
T_ENORMOUS = A('The planet is so enormous')
T_1300 = A('thirteen hundred Earths')
T_YET = A('Yet somehow')
T_TENH = A('less than ten hours')
T_JET = A('powerful jet streams')
T_UNSETTLE = A("But here's where things")
T_JUNO = A('NASA Juno spacecraft discovered')
T_EXTEND = A('extend roughly')
T_3000 = A('three thousand kilometers below')
T_3000B = A('3000 kilometers')
T_STORMSYS = A('Imagine a storm system')
T_ABOUT = A("and you're about to fall")
T_OBSTACLE = A('But your first')
T_SPEED = A("It's your speed")
T_170 = A('one hundred seventy thousand')
T_SIMILAR = A('similar to the entry speed')
T_HIT = A('Then you hit the upper atmosphere')

HIST_TAG = 'HISTORICAL RECONSTRUCTION · GALILEO PROBE, 1995'

# ------------------------------------------------------------------ S01 hook
def s01(c, t):
    d = t
    zoom = tw(t, 0, T_DROPPED, 1.0, 1.07, e_sine)
    space(c, t, zoom=zoom, ox=-t * 6)
    c.save(); c.translate(W / 2, H / 2); c.scale(zoom, zoom); c.translate(-W / 2, -H / 2)
    draw_jupiter(c, 1430, 610, 720, rot=2.4 + t * 0.012)
    # tiny probe drifting toward the planet
    px = lerp(330, 560, e_sine(prog(t, 0, T_DROPPED + .5)))
    py = lerp(300, 420, e_sine(prog(t, 0, T_DROPPED + .5)))
    for i in range(14):
        c.drawCircle(px - i * 9, py - i * 4.6, 2.2 * (1 - i / 14), P(hexc('#FFF1D6', .35 * (1 - i / 14))))
    draw_galileo_entry(c, px, py, .17, 27)
    glow(c, px, py, 26, hexc('#FFB347'), .35 + .15 * math.sin(t * 4))
    c.restore()
    # title
    a = fade_window(t, 0.12, 3.35, .45, .45)
    f1 = font(76, 'black')
    draw_text(c, 'WHAT IF YOU ACTUALLY', 110, 250, f1, hexc('#FFF1D6'), alpha=a, shadow=1)
    draw_text(c, 'FELL INTO JUPITER?', 110, 338, f1, hexc('#E3B47A'), alpha=a * e_out(prog(t, .35, .9)), shadow=1, glow=.25)
    # scale callout to the probe after title
    k = prog(t, 3.4, 4.2)
    if k > 0:
        label_line(c, px - 8, py + 8, px - 120, py + 150, 'DEC 7, 1995', hexc('#FFB347'), alpha=1, k=k, size=34, sub='GALILEO PROBE · NASA')
        draw_tag(c, HIST_TAG, 40, 36, 'hist', alpha=e_out(k))

# ------------------------------------------------------------------ S02 dropped / survived entry
def s02(c, t):
    lt = t - T_DROPPED
    space(c, t, ox=-lt * 40)
    # planet limb filling bottom right
    draw_jupiter(c, 1250 - lt * 10, 2350, 1900, rot=2.1 + t * .01)
    p = e_in(prog(t, T_DROPPED, T_SURV_ENTRY + .2))
    px, py = lerp(380, 1180, p), lerp(170, 640, p)
    heat = e_in(prog(t, T_SURV_ENTRY - 1.4, T_SURV_ENTRY + .1)) * (1 - e_out(prog(t, T_SURV_ENTRY + .9, T_WINDS)))
    trail = heat
    if trail > 0:
        for i in range(30):
            q = i / 30
            glow(c, px - (px - 380) * q * .35, py - (py - 170) * q * .35, 60 * (1 - q) + 8, hexc('#ff8a3a'), trail * (1 - q) * .5)
    sc = lerp(.42, .55, p)
    draw_galileo_entry(c, px, py, sc, 30, heat=heat)
    flash(c, heat * .18, '#ffb070')
    k = prog(t, T_SURV_ENTRY + .55, T_SURV_ENTRY + 1.0)
    if k > 0:
        card(c, 1240, 140, 520, 120, e_out(k))
        draw_check(c, 1310, 200, 56, e_out(prog(t, T_SURV_ENTRY + .7, T_SURV_ENTRY + 1.2)))
        draw_text(c, 'ENTRY SURVIVED', 1365, 214, font(44, 'black'), hexc('#FFF1D6'), alpha=e_out(k))
    draw_tag(c, HIST_TAG, 40, 36, 'hist')

# ------------------------------------------------------------------ S03 winds
def s03(c, t):
    lt = t - T_WINDS
    cloud_world(c, t, fall=10, drift=-900, tint=(1, .8, .56), bg_top='#efc58f', bg_bot='#9a5a32')
    # wind streaks
    speed_lines(c, t, .55, direction=(-1, 0), n=70, speed=4200, length=260, color='#FFF1D6', width=3)
    sway = math.sin(t * 2.6) * 9 - 6
    draw_galileo_descent(c, 820 + math.sin(t * 1.3) * 30, 560, .9, chute=1, sway=sway, t=t)
    # comparison bars
    k1 = e_out(prog(t, T_WINDS + .5, T_WINDS + 1.1)); k2 = e_out(prog(t, T_WINDS + 1.6, T_WINDS + 2.4))
    x0, y0 = 1180, 160
    card(c, x0 - 30, y0 - 50, 700, 300, k1)
    draw_text(c, 'WIND SPEED', x0, y0, mono(22, 'semi'), hexc(HUDC), alpha=k1, spacing=2)
    draw_text(c, 'STRONG EARTH HURRICANE', x0, y0 + 50, font(24, 'bold'), hexc('#FFF1D6'), alpha=k1)
    rrect(c, x0, y0 + 65, 250 / 650 * 600 * k1, 30, 8, P(hexc('#6FD3FF', k1)))
    draw_text(c, '~250+ km/h', x0 + 250 / 650 * 600 * k1 + 14, y0 + 90, mono(22, 'bold'), hexc('#FFFFFF'), alpha=k1)
    draw_text(c, 'GALILEO-MEASURED WINDS', x0, y0 + 150, font(24, 'bold'), hexc('#FFF1D6'), alpha=k2)
    rrect(c, x0, y0 + 165, 520 * k2, 30, 8, P(hexc('#FF8A3A', k2)))
    draw_text(c, 'UP TO ~650 km/h', x0 + 10, y0 + 230, mono(22, 'bold'), hexc('#FFFFFF'), alpha=k2)
    draw_tag(c, HIST_TAG, 40, 36, 'hist')

# ------------------------------------------------------------------ S04 falling, no ground
def s04(c, t):
    lt = t - T_KEPT
    fall = 520
    cloud_world(c, t, fall=fall, drift=-30, tint=(1, .76, .5), bg_top='#d9a066', bg_bot='#6b3a20', depth_dark=.3)
    sway = math.sin(t * 2.2) * 5
    draw_galileo_descent(c, 960, 520 + math.sin(t * 1.7) * 8, 1.0, chute=1, sway=sway, t=t)
    depth_ruler(c, 1820, 120, 900, lt * 260, 1, label_fn=lambda i: '')
    k = prog(t, T_NOGROUND - .1, T_NOGROUND + .35)
    if k > 0:
        hud_panel(c, 1240, 700, 520, 110, 'SOLID GROUND BELOW', k, warn=True)
        draw_text(c, 'NONE DETECTED', 1300, 778, mono(40, 'bold'), hexc(PAL['danger']), alpha=k * (.75 + .25 * math.sin(t * 9)))
    draw_tag(c, HIST_TAG, 40, 36, 'hist')

# ------------------------------------------------------------------ S05 58 minutes, transmission ended
def s05(c, t):
    lt = t - T_THEN58
    bg(c, '#0a1022', '#04060c')
    end = T_ENDED + .25
    lost = t >= end
    # monitor panel
    x, y, w, h = 260, 200, 1400, 560
    hud_panel(c, x, y, w, h, 'GALILEO PROBE → ORBITER RELAY · TELEMETRY', 1)
    # timer
    mins = 58 * e_io(prog(t, T_THEN58 + .2, T_ENDED - .2))
    mm = int(mins); ss = int((mins - mm) * 60)
    draw_text(c, f'T+ {mm:02d}:{ss:02d}', x + w - 40, y + 110, mono(64, 'bold'), hexc('#FFFFFF'), 'right')
    draw_text(c, 'MINUTES OF DATA', x + w - 40, y + 145, mono(18, 'semi'), hexc(HUDC), 'right', spacing=1.5)
    # waveform
    pa = skia.Path()
    for i in range(0, 1101, 4):
        xx = x + 150 + i
        if lost:
            amp = 0
        else:
            amp = 70 * (1 - .5 * prog(t, T_ENDED - 1.5, end))
        yy = y + 330 + amp * math.sin(i * .045 + t * 14) * math.sin(i * .011 + t * 2.3)
        if i == 0: pa.moveTo(xx, yy)
        else: pa.lineTo(xx, yy)
    col = hexc(PAL['danger']) if lost else hexc(PAL['ok'])
    c.drawPath(pa, P(with_alpha(col, .35), stroke=9, blur=6))
    c.drawPath(pa, P(col, stroke=3))
    signal_bars(c, x + 40, y + 140, 0 if lost else 1 - .6 * prog(t, T_ENDED - 1.5, end), lost=lost)
    if lost:
        k = prog(t, end, end + .3)
        draw_text(c, 'SIGNAL LOST', x + w / 2, y + 480, font(72, 'black'), hexc(PAL['danger']), 'center', alpha=e_out(k), glow=.5)
    draw_tag(c, HIST_TAG, 40, 36, 'hist')

# ------------------------------------------------------------------ S06 barely scratched the surface (scale pull-out)
def s06(c, t):
    lt = t - T_BUTHERE
    space(c, t)
    R = 380
    cx, cy = 960, 600
    # camera: start zoomed on the top of the planet, pull out to full cross-section
    z = keys(t, [(T_BUTHERE, 9.0), (T_SCRATCH + .3, 9.0), (T_INTERIOR + 1.2, 1.0)], e_io)
    c.save()
    fy = cy - R  # focus at top of planet
    c.translate(960, lerp(540, 330, 1) if z > 1 else 330)
    c.translate(0, 0)
    c.restore()
    c.save()
    # focus point blends from planet top to centre
    fp = lerp(cy - R, cy - 60, e_io(prog(z, 9.0, 1.0)) if False else 1 - (z - 1) / 8)
    c.translate(960, lerp(420, 540, 1 - (z - 1) / 8)); c.scale(z, z); c.translate(-cx, -fp)
    draw_cross_section(c, cx, cy, R, wedge=(-90, 0), rot=2.0, dark_unknown=.82, core_alpha=0, show_metal=0, metal_glow=0, t=t)
    # galileo depth mark (~150 km of 69,911 km radius) at top of wedge
    dep = 150 / 69911 * R
    c.drawLine(cx + 4, cy - R, cx + 4, cy - R + max(dep, .15), P(hexc(PAL['danger']), stroke=3 / z))
    c.drawCircle(cx + 4, cy - R + dep, 5 / z, P(hexc(PAL['danger'])))
    glow(c, cx + 4, cy - R + dep, 22 / z, hexc(PAL['danger']), .8)
    c.restore()
    k1 = prog(t, T_SCRATCH, T_SCRATCH + .6)
    zz = z
    mx, my = 960 + 4 * zz, 540 + (cy - R + dep - (lerp(420, 540, 1 - (z - 1) / 8) * 0 + 0)) * 0
    # compute screen position of the mark
    fpp = lerp(cy - R, cy - 60, 1 - (z - 1) / 8)
    sy = lerp(420, 540, 1 - (z - 1) / 8) + (cy - R + dep - fpp) * z
    sx = 960 + 4 * z
    if k1 > 0:
        label_line(c, sx, sy, sx + 260, sy - 110 if sy > 300 else sy + 110, "GALILEO'S DEEPEST POINT", hexc('#FF8A7A'), k=k1, size=30, sub='≈ 150 km below the cloud tops')
    k2 = prog(t, T_INTERIOR + 1.0, T_INTERIOR + 1.6)
    if k2 > 0:
        draw_text(c, '≈ 0.2% OF THE WAY TO THE CENTER', 960, 1000 - 70, font(40, 'black'), hexc('#FFF1D6'), 'center', alpha=e_out(k2), shadow=1)
        draw_text(c, 'JUPITER RADIUS ≈ 70,000 km', 960, 1000 - 20 - 160 + 160 - 0 - 0 - 0 + 0, font(1, 'bold'), hexc('#FFF1D6'), 'center', alpha=0)
        draw_text(c, 'RADIUS ≈ 70,000 km', cx - R * .5 - 10, cy - 18, mono(22, 'semi'), hexc('#FFF1D6'), 'center', alpha=e_out(k2))
        c.drawLine(cx - R, cy, cx - 6, cy, P(hexc('#FFF1D6', .6 * e_out(k2)), stroke=2))
    k3 = prog(t, T_KEPTF - .2, T_KEPTF + .8)
    if k3 > 0:
        dashed(c, [(cx + 4, cy - R + dep + 10), (cx + 4, cy - 30)], hexc('#6FD3FF'), 5, phase=-t * 60, k=e_io(k3))
        if k3 > .6:
            draw_text(c, '?', cx + 40, cy - 40, font(120, 'black'), hexc('#6FD3FF'), 'left', alpha=e_out(prog(t, T_KEPTF + .4, T_KEPTF + .8)), glow=.5)

# ------------------------------------------------------------------ S07 three questions
def _panel_solid(c, x, y, w, h, t, a):
    c.save(); c.clipRect(skia.Rect(x, y, x + w, y + h))
    c.drawRect(skia.Rect(x, y, x + w, y + h), P(shader=lin((x, y), (x, y + h), [hexc('#2a1e2e', a), hexc('#6b3a24', a)])))
    pa = path_from([(x, y + h * .72), (x + w * .2, y + h * .64), (x + w * .38, y + h * .7), (x + w * .6, y + h * .6), (x + w * .8, y + h * .69), (x + w, y + h * .62), (x + w, y + h), (x, y + h)], True)
    c.drawPath(pa, P(hexc('#4a3428', a)))
    for i in range(7):
        c.drawCircle(x + w * (.1 + i * .13), y + h * (.8 + .06 * math.sin(i * 2)), 10 + 6 * (i % 3), P(hexc('#3a271e', a)))
    c.restore()

def _panel_ocean(c, x, y, w, h, t, a):
    c.save(); c.clipRect(skia.Rect(x, y, x + w, y + h))
    c.drawRect(skia.Rect(x, y, x + w, y + h), P(shader=lin((x, y), (x, y + h), [hexc('#1b2a50', a), hexc('#0c3a5a', a)])))
    for j in range(4):
        pa = skia.Path(); yy = y + h * (.62 + j * .09)
        pa.moveTo(x, yy)
        for i in range(0, int(w) + 20, 20):
            pa.lineTo(x + i, yy + 8 * math.sin(i * .03 + t * 2.4 + j))
        pa.lineTo(x + w, y + h); pa.lineTo(x, y + h); pa.close()
        c.drawPath(pa, P(hexc(['#2f6fa3', '#28608f', '#1f4f7a', '#173f63'][j], a)))
    c.restore()

def _panel_center(c, x, y, w, h, t, a):
    c.save(); c.clipRect(skia.Rect(x, y, x + w, y + h))
    c.drawRect(skia.Rect(x, y, x + w, y + h), P(hexc('#0b0612', a)))
    cx, cy = x + w / 2, y + h * .58
    for i in range(5):
        c.drawCircle(cx, cy, 160 - i * 30, P(hexc(['#3a1a12', '#5a2a18', '#7a3b1f', '#a8582a', '#e8a860'][i], a)))
    glow(c, cx, cy, 90, hexc('#ffd28a'), a * (.6 + .2 * math.sin(t * 3)))
    c.restore()

def s07(c, t):
    bg(c, '#0b1230', '#05070f')
    particles(c, t, .4, n=60, vy=-30, color='#9FB6FF', size=(1, 2.5))
    items = [(T_SOLID, 'SOMETHING SOLID?', _panel_solid), (T_OCEAN, 'AN OCEAN?', _panel_ocean), (T_CENTER, 'THE CENTER?', _panel_center)]
    w, h, gap = 500, 560, 60
    x0 = (W - (3 * w + 2 * gap)) / 2
    push = e_io(prog(t, T_LARGEST - .4, T_FINDOUT + .1))
    c.save()
    if push > 0:
        cx3 = x0 + 2 * (w + gap) + w / 2
        z = lerp(1, 1.35, push)
        c.translate(lerp(960, 960, push), 540); c.scale(z, z); c.translate(-lerp(960, cx3, push), -540)
    for i, (tt, label, fn) in enumerate(items):
        k = prog(t, tt + .1, tt + .55)
        if k <= 0:
            continue
        a = e_out(k)
        x = x0 + i * (w + gap); y = 190 + (1 - a) * 60
        dim = 1 - .55 * (i < 2) * push
        card(c, x - 8, y - 8, w + 16, h + 16, a * dim, color='#0b1330', border='#3D5A9E')
        fn(c, x, y, w, h * .78, t, a * dim)
        draw_text(c, label, x + w / 2, y + h * .78 + 78, font(40, 'black'), hexc('#FFF1D6'), 'center', alpha=a * dim)
        # falling capsule silhouette into each panel
        fy = y + 40 + ((t - tt) * 60) % (h * .4)
        draw_capsule(c, x + w / 2, fy, .18, 0, a * dim * .9, t, lamp=False)
        draw_text(c, '?', x + w - 50, y + 80, font(80, 'black'), hexc('#6FD3FF'), 'center', alpha=a * dim, glow=.4)
    c.restore()

# ------------------------------------------------------------------ S08 route: real vs imagined
def s08(c, t):
    bg(c, '#0b1230', '#05070f')
    # vertical depth column
    x = 760
    top, bot = 170, 980
    col_w = 180
    c.drawRect(skia.Rect(x - col_w / 2, top, x + col_w / 2, bot), P(shader=lin((0, top), (0, bot), [hexc('#E3B47A'), hexc('#8a3b1f'), hexc('#2d2a7a'), hexc('#1a1030')], [0, .3, .65, 1])))
    c.drawRect(skia.Rect(x - col_w / 2, top, x + col_w / 2, bot), P(hexc('#FFF1D6', .4), stroke=2))
    draw_text(c, 'CLOUD TOPS', x - col_w / 2 - 20, top + 8, mono(20, 'semi'), hexc('#FFF1D6'), 'right')
    draw_text(c, 'CENTER', x - col_w / 2 - 20, bot, mono(20, 'semi'), hexc('#FFF1D6'), 'right')
    draw_text(c, 'NOT TO SCALE', x - col_w / 2 - 20, top + 40, mono(16, 'medium'), hexc(HUDC), 'right', alpha=.7)
    k1 = e_io(prog(t, T_REAL, T_REAL + 1.6))
    real_end = top + 60
    if k1 > 0:
        c.drawLine(x, top, x, lerp(top, real_end, k1), P(hexc('#FFB347'), stroke=10, cap='round'))
        draw_galileo_descent(c, x, lerp(top, real_end, k1) - 5, .25, chute=1, t=t)
        label_line(c, x + 20, real_end, x + 220, real_end - 40, 'REAL SPACECRAFT', hexc('#FFB347'), k=prog(t, T_REAL + .8, T_REAL + 1.6), size=32, sub='GALILEO PROBE · 1995 · MEASURED DATA')
    k2 = e_io(prog(t, T_NOSPACE, T_NOSPACE + 2.4))
    if k2 > 0:
        dashed(c, [(x, real_end + 14), (x, bot - 20)], hexc('#6FD3FF'), 8, on=20, off=14, phase=-t * 50, k=k2)
        yy = lerp(real_end + 14, bot - 60, k2)
        draw_capsule(c, x, yy, .2, 0, 1, t)
        label_line(c, x + 20, (real_end + bot) / 2 + 80, x + 220, (real_end + bot) / 2 + 40, 'WHERE NO SPACECRAFT HAS GONE', hexc('#6FD3FF'), k=prog(t, T_NOSPACE + 1.0, T_NOSPACE + 1.8), size=32, sub='FICTIONAL JOURNEY · GUIDED BY SCIENTIFIC MODELS')

# ------------------------------------------------------------------ S09 Earth vs Jupiter falling
def s09(c, t):
    lt = t - T_BUTFIRST
    # left half: Earth sky + ground
    c.save(); c.clipRect(skia.Rect(0, 0, W / 2 - 3, H))
    bg(c, '#5fa3e8', '#cfe6ff')
    c.drawRect(skia.Rect(0, 760, W / 2, H), P(shader=lin((0, 760), (0, H), [hexc('#5f9a45'), hexc('#3c6b2c')])))
    c.drawLine(0, 760, W / 2, 760, P(hexc('#ffffff', .6), stroke=2))
    p = e_in(prog(t, T_BUTFIRST + .3, T_EARTHFALL + .5))
    yy = lerp(150, 700, p)
    draw_capsule(c, 480, yy, .38, 0, 1, t, lamp=False, ambient='#9fd0ff')
    if p >= 1:
        k = prog(t, T_EARTHFALL + .5, T_EARTHFALL + 1.3)
        for i in range(10):
            ang = math.pi + i / 9 * math.pi
            c.drawCircle(480 + math.cos(ang) * 120 * e_out(k), 760 + math.sin(ang) * 40 * e_out(k), 16 * (1 - k), P(hexc('#d8c8a8', .7 * (1 - k))))
        draw_text(c, 'LANDED', 480, 870, font(46, 'black'), hexc('#FFFFFF'), 'center', alpha=e_out(prog(t, T_EARTHFALL + .5, T_EARTHFALL + .9)), shadow=1)
    draw_text(c, 'EARTH', 480, 120, font(44, 'black'), hexc('#0b1230'), 'center')
    c.restore()
    # right half: Jupiter endless clouds
    c.save(); c.clipRect(skia.Rect(W / 2 + 3, 0, W, H)); c.translate(W / 2, 0)
    c.save(); c.scale(.5, 1)
    cloud_world(c, t, fall=lerp(60, 260, prog(t, T_BUTFIRST, T_EARTHFALL + 1)), tint=(1, .74, .5), bg_top='#E3B47A', bg_bot='#3a1a10', depth_dark=.5)
    c.restore()
    draw_capsule(c, 480, 470 + math.sin(t * 1.5) * 10, .38, 0, 1, t, lamp=False)
    dashed(c, [(60, 760), (900, 760)], hexc('#FFF1D6'), 3, alpha=.5 * (.6 + .4 * math.sin(t * 4)))
    draw_text(c, 'GROUND?', 480, 805, mono(30, 'bold'), hexc('#FFF1D6'), 'center', alpha=.8)
    draw_x(c, 480, 870, 46, prog(t, T_DIFFERENT, T_DIFFERENT + .5))
    draw_text(c, 'JUPITER', 480, 120, font(44, 'black'), hexc('#FFF1D6'), 'center', shadow=1)
    c.restore()
    c.drawRect(skia.Rect(W / 2 - 3, 0, W / 2 + 3, H), P(hexc('#070B1A')))

# ------------------------------------------------------------------ S10 nowhere to land / peaceful
def s10(c, t):
    lt = t - T_NOWHERE
    z = tw(t, T_PEACEFUL, T_REDOVAL, 1.0, 1.12, e_sine)
    space(c, t, zoom=z * .9 + .1)
    R = 400 * z
    a_pl = e_out(prog(t, T_NOWHERE + .8, T_PEACEFUL + .6))
    draw_jupiter(c, 960, 560, R, rot=2.6 + t * .03, alpha=a_pl)
    # wrap-around band tracers
    k = prog(t, T_WRAP - .6, T_WRAP + 1.2)
    if k > 0 and k < 1:
        for lat in (12, -14, 30, -32):
            yy = 560 - R * math.sin(math.radians(lat))
            rx = R * math.cos(math.radians(lat))
            arc = skia.Path(); arc.addArc(skia.Rect(960 - rx, yy - rx * .08, 960 + rx, yy + rx * .08), 180, -180 * e_io(k))
            c.drawPath(arc, P(hexc('#FFF1D6', .8 * math.sin(math.pi * k)), stroke=3))
    # title text
    a = fade_window(t, T_NOWHERE - .05, T_PEACEFUL + .2, .3, .5)
    draw_text(c, "THERE'S NOWHERE TO LAND.", 960, 560, font(96, 'black'), hexc('#FFF1D6'), 'center', alpha=a, glow=.3, shadow=1)
    chapter_card(c, 1, 'NOWHERE TO LAND', t, T_PEACEFUL + .4, T_STRIPES + 1.6)

# ------------------------------------------------------------------ S11 Great Red Spot zoom
def s11(c, t):
    lt = t - T_REDOVAL
    zk = e_io(prog(t, T_REDOVAL, T_CENTURIES))
    R = lerp(450, 1900, zk)
    lat = math.radians(-22)
    cy0 = 560
    gy = math.sin(-lat)  # ny of GRS
    cx = 960
    cy = lerp(cy0, 540 - gy * R, zk)
    pull = e_io(prog(t, T_NOTGROUND, T_CLOUDS + .3))
    R = lerp(R, 1450, pull)
    cy = lerp(cy, 540 - gy * R + 120, pull)
    space(c, t, zoom=1 + zk * .3)
    draw_jupiter(c, cx, cy, R, rot=math.pi + .35 - .35 * zk + t * .004)
    gx_s, gy_s = cx + R * math.sin(.35 * (1 - zk) - t * .004) * 0, cy + gy * R
    k = prog(t, T_GRS, T_GRS + .6)
    if k > 0:
        ga = 1 - pull
        rx, ry = R * .118, R * .082
        c.drawOval(skia.Rect(960 - rx * 1.3, gy_s - ry * 1.3, 960 + rx * 1.3, gy_s + ry * 1.3), P(hexc('#FFF1D6', .8 * e_out(k) * ga), stroke=3))
        label_line(c, 960 + rx * 1.2, gy_s - ry * 1.0, 1450, 260, 'GREAT RED SPOT', hexc('#FFF1D6'), alpha=ga, k=k, size=40, sub='A GIANT STORM · WIDER THAN EARTH')
        k2 = prog(t, T_CENTURIES - .3, T_CENTURIES + .3)
        if k2 > 0:
            er = 6371 / 71492 * R
            ex, ey = 420, gy_s
            draw_earth(c, ex, ey, er * e_back(min(1, k2), 1.3) if k2 < 1 else er, rot=1.0, alpha=ga, max_grid=500)
            draw_text(c, 'EARTH · TO SCALE', ex, ey + er + 40, mono(22, 'semi'), hexc('#FFF1D6'), 'center', alpha=ga * e_out(k2))
            draw_text(c, 'OBSERVED FOR CENTURIES', 1450 + 14, 260 + 100, mono(24, 'semi'), hexc('#E3B47A'), 'left', alpha=ga * e_out(k2))
    k3 = prog(t, T_NOTGROUND + .3, T_NOTGROUND + .9)
    if k3 > 0:
        for i, lat_ in enumerate((8, -9, -20)):
            yy = cy - R * math.sin(math.radians(lat_))
            c.drawLine(200, yy, 1720, yy, P(hexc('#FFF1D6', .6 * e_out(k3)), stroke=2))
        hud_panel(c, 1240, 160, 520, 100, None, e_out(k3))
        draw_text(c, 'STRIPES ≠ GROUND', 1500, 228, font(46, 'black'), hexc('#FFF1D6'), 'center', alpha=e_out(k3))

# ------------------------------------------------------------------ S12 clouds moving / winds
def s12(c, t):
    lt = t - T_CLOUDS
    strip = tex_strip_img(34, -34)
    sw, sh = strip.width(), strip.height()
    scale = H / sh * 1.25
    nb = 14
    for i in range(nb):
        y0 = sh * i / nb; y1 = sh * (i + 1) / nb
        lat = 34 - 68 * (i + .5) / nb
        v = 60 * math.sin(math.radians(lat) * 7.5) * (1.0 + .5 * (abs(lat) < 8)) + 25
        off = (t * v * 1.2) % sw
        dy = (y0 * scale) - (sh * scale - H) / 2
        for k in (-1, 0, 1):
            src = skia.Rect(0, y0, sw, y1)
            dst = skia.Rect(-off * scale + k * sw * scale, dy, -off * scale + (k + 1) * sw * scale, dy + (y1 - y0) * scale + 1)
            c.drawImageRect(strip, src, dst, LIN, P())
    letter_dim(c, .15)
    k = prog(t, T_MOVING, T_MOVING + .8)
    for i in range(6):
        lat = 34 - 68 * (i * 2 + 1.5) / nb
        v = math.sin(math.radians(lat) * 7.5)
        y = (H / 2) - lat / 34 * H * .62
        if 120 < y < 900:
            d = 1 if v > 0 else -1
            xs = 960 - d * 260
            arrow(c, xs, y, xs + d * 520 * e_out(k), y, hexc('#FFF1D6'), 6, 26, .85 * k)
    k2 = prog(t, T_WINDRACE, T_WINDRACE + .6)
    if k2 > 0:
        hud_readout(c, 1290, 140, 480, 'JET STREAM SPEED', 'HUNDREDS', 'km/h', e_out(k2), sub='ALTERNATING EAST ↔ WEST', size=46)
    draw_tag(c, 'CLOUD-TOP VIEW · ILLUSTRATIVE', 40, 36, 'concept', alpha=1)

# ------------------------------------------------------------------ S13 1,300 Earths
def s13(c, t):
    lt = t - T_ENORMOUS
    space(c, t)
    R = 380; cx, cy = 820, 560
    draw_jupiter(c, cx, cy, R, rot=2.9 + t * .02)
    er = 6371 / 71492 * R
    k0 = e_out(prog(t, T_ENORMOUS + .2, T_ENORMOUS + .8))
    draw_earth(c, 1420, 300, er * 1.0, rot=1.0, alpha=k0, max_grid=300)
    draw_text(c, 'EARTH · TO SCALE', 1420, 300 + er + 38, mono(20, 'semi'), hexc('#FFF1D6'), 'center', alpha=k0)
    k = prog(t, T_1300 - .4, T_YET - .2)
    if k > 0:
        # fill disc with earth icons (2D illustration of a volume comparison)
        n_show = int(e_io(k) * 600)
        rng = np.random.default_rng(2)
        r_ic = 9.5
        pts = []
        row = 0
        yy = cy - R + r_ic
        while yy < cy + R:
            half = math.sqrt(max(0, R * R - (yy - cy) ** 2)) - r_ic
            xx = cx - half + (row % 2) * r_ic
            while xx <= cx + half:
                pts.append((xx, yy)); xx += r_ic * 2.05
            yy += r_ic * 1.78; row += 1
        pts.sort(key=lambda p: -p[1])
        c.save(); c.clipPath(skia.Path().addCircle(cx, cy, R), doAntiAlias=True)
        for i, (px, py) in enumerate(pts[:n_show * len(pts) // 600]):
            draw_earth_icon(c, px, py, r_ic * .92, .95)
        c.restore()
        num = int(1300 * e_io(prog(t, T_1300 - .3, T_1300 + 1.4)))
        hud_panel(c, 1240, 560, 540, 210, None, e_out(prog(t, T_1300 - .4, T_1300)))
        draw_text(c, f'{num:,}+', 1510, 680, font(110, 'black'), hexc('#FFF1D6'), 'center', alpha=e_out(prog(t, T_1300 - .4, T_1300)), glow=.3)
        draw_text(c, 'EARTHS COULD FIT INSIDE (BY VOLUME)', 1510, 735, mono(19, 'semi'), hexc(HUDC), 'center', alpha=e_out(prog(t, T_1300 - .4, T_1300)))
    draw_tag(c, 'ILLUSTRATION · VOLUME SHOWN IN 2D', 40, 36, 'concept')

# ------------------------------------------------------------------ S14 rotation < 10 h, jet streams
def s14(c, t):
    lt = t - T_YET
    space(c, t)
    R = 380; cx, cy = 960, 560
    spin = lerp(.02, .9, e_io(prog(t, T_YET + .3, T_TENH))) if t < T_JET else lerp(.9, .15, e_io(prog(t, T_JET - .5, T_JET + .8)))
    # integrate spin roughly: use quadratic approx
    ang = 2.0 + (t - T_YET) * spin
    draw_jupiter(c, cx, cy, R, rot=ang)
    k = prog(t, T_YET + .3, T_TENH + 1.2)
    rect = skia.Rect(cx - R - 40, cy - R - 40, cx + R + 40, cy + R + 40)
    c.drawArc(rect, -90, 360 * e_io(k), False, P(hexc('#FFB347', .9), stroke=6, cap='round'))
    c.drawArc(rect, -90, 360, False, P(hexc('#FFB347', .2), stroke=6))
    hrs = 9 + 56 / 60
    hh = hrs * e_io(k)
    kk = prog(t, T_TENH - .2, T_TENH + .3)
    hud_panel(c, 1390, 220, 420, 200, 'ONE JUPITER DAY', e_out(kk))
    draw_text(c, f'{int(hh)} h {int((hh % 1) * 60):02d} min', 1410, 330, mono(52, 'bold'), hexc('#FFFFFF'), alpha=e_out(kk))
    draw_text(c, 'EARTH DAY: 24 h', 1410, 385, mono(22, 'semi'), hexc(HUDC), alpha=e_out(kk))
    k2 = prog(t, T_JET, T_JET + 1.0)
    if k2 > 0:
        c.save(); c.clipPath(skia.Path().addCircle(cx, cy, R), doAntiAlias=True)
        for i, lat in enumerate((26, 18, 7, -2, -12, -20, -30, -40)):
            yy = cy - R * math.sin(math.radians(lat))
            rx = R * math.cos(math.radians(lat)) * .8
            d = 1 if i % 2 == 0 else -1
            ph = (t * .6 * d) % 1.0
            x0 = cx - rx + ph * rx * .5
            arrow(c, cx - d * rx * .6, yy, cx + d * rx * .6, yy, hexc('#FFF1D6'), 4, 18, .8 * e_out(k2), k=e_out(k2))
        c.restore()
        label_line(c, cx + R * .7, cy - R * .5, 1500, 620, 'JET STREAMS', hexc('#FFF1D6'), k=k2, size=36, sub='SHAPE THE STRIPES')

# ------------------------------------------------------------------ S15 Juno: winds extend ~3,000 km deep
def s15(c, t):
    lt = t - T_UNSETTLE
    dark = e_io(prog(t, T_UNSETTLE, T_UNSETTLE + 2.0))
    split = e_io(prog(t, T_EXTEND - .6, T_3000))
    space(c, t, alpha=1)
    # slab view: zoomed section of the planet edge
    Rb = lerp(500, 2600, split)
    cx, cy = 960, lerp(560, 440 + 2600, split)
    if split < .999:
        draw_jupiter(c, cx, cy, Rb, rot=2.2 + t * .02, alpha=1)
    if split > 0:
        c.save()
        c.drawCircle(cx, cy, Rb, P(shader=rad(cx, cy, Rb, [hexc('#3a1408', split), hexc('#6b2a14', split), hexc('#b8693a', split), hexc('#E3B47A', split)], [0, .9, .985, 1])))
        # wind layer band ~3000 km thick
        th = 3000 / 69911 * Rb
        band = skia.Path(); band.addCircle(cx, cy, Rb); band.addCircle(cx, cy, Rb - th); band.setFillType(skia.PathFillType.kEvenOdd)
        c.drawPath(band, P(hexc('#FFB347', .28 * split)))
        # flowing arrows within band
        c.save(); c.clipPath(band, doAntiAlias=True)
        for j in range(3):
            rr = Rb - th * (.2 + .3 * j)
            for i in range(9):
                ang = -90 + (i - 4) * 9 + ((t * (4 - j) * (1 if j % 2 == 0 else -1)) % 9)
                a = math.radians(ang)
                x = cx + math.cos(a) * rr; y = cy + math.sin(a) * rr
                d = 1 if j % 2 == 0 else -1
                a2 = a + d * .02
                arrow(c, x, y, cx + math.cos(a2) * rr, cy + math.sin(a2) * rr, hexc('#FFF1D6'), 4, 16, .8 * split)
        c.restore()
        c.restore()
        kb = prog(t, T_3000 - .2, T_3000 + .5)
        if kb > 0:
            xb = 1500
            ytop = cy - math.sqrt(max(0, Rb ** 2 - (xb - cx) ** 2))
            ybot = cy - math.sqrt(max(0, (Rb - th) ** 2 - (xb - cx) ** 2))
            c.drawLine(xb + 30, ytop, xb + 30, lerp(ytop, ybot, e_out(kb)), P(hexc('#FFFFFF'), stroke=4))
            c.drawLine(xb + 18, ytop, xb + 42, ytop, P(hexc('#FFFFFF'), stroke=4))
            if kb >= 1:
                c.drawLine(xb + 18, ybot, xb + 42, ybot, P(hexc('#FFFFFF'), stroke=4))
            draw_text(c, '≈ 3,000 km', xb + 60, (ytop + ybot) / 2 + 14, mono(40, 'bold'), hexc('#FFFFFF'), alpha=e_out(kb), shadow=1)
            draw_text(c, 'VISIBLE CLOUD TOPS', 330, cy - Rb - 24 + (Rb - math.sqrt(max(0, Rb ** 2 - (330 - cx) ** 2))) , mono(22, 'semi'), hexc('#FFF1D6'), alpha=e_out(kb))
    letter_dim(c, .3 * dark * (1 - split))
    # Juno flyby
    kj = prog(t, T_JUNO - .4, T_EXTEND + 1.5)
    if 0 < kj < 1:
        jx = lerp(-300, 2200, e_sine(kj)); jy = lerp(300, 200, kj)
        draw_juno(c, jx, jy, .75, 15 + kj * 40, t=t)
        if kj > .15:
            draw_tag(c, 'NASA JUNO · AT JUPITER SINCE 2016', 960, 860 - 30, 'concept', align='center', alpha=fade_window(kj, .15, .95, .1, .1))
    if split > .5:
        draw_tag(c, 'CUTAWAY · JUNO GRAVITY RESULTS (2018)', 40, 36, 'model', alpha=e_out(prog(split, .5, 1)))

# ------------------------------------------------------------------ S16 3000 km, storm system, about to fall in
def s16(c, t):
    lt = t - T_3000B
    plunge = e_in(prog(t, T_ABOUT, T_OBSTACLE))
    Rb = 2600
    cx, cy = 960, 440 + 2600
    c.save()
    z = lerp(1, 4.5, plunge)
    c.translate(960, 600); c.scale(z, z); c.translate(-960, -600 + plunge * 40)
    space(c, t)
    c.drawCircle(cx, cy, Rb, P(shader=rad(cx, cy, Rb, [hexc('#3a1408'), hexc('#6b2a14'), hexc('#b8693a'), hexc('#E3B47A')], [0, .9, .985, 1])))
    th = 3000 / 69911 * Rb
    band = skia.Path(); band.addCircle(cx, cy, Rb); band.addCircle(cx, cy, Rb - th); band.setFillType(skia.PathFillType.kEvenOdd)
    c.drawPath(band, P(hexc('#FFB347', .28)))
    # storm column
    ks = e_io(prog(t, T_STORMSYS, T_STORMSYS + 2.0))
    if ks > 0:
        sx = 960
        top = 440
        for i in range(10):
            y = top + i * th / 9 * ks
            rw = 70 - i * 3
            c.drawOval(skia.Rect(sx - rw, y - 8, sx + rw, y + 8), P(hexc('#FFF1D6', .55 * ks), stroke=3))
            ph = t * 4 + i * .6
            c.drawCircle(sx + math.cos(ph) * rw, y + math.sin(ph) * 8, 5, P(hexc('#FFFFFF', .9 * ks)))
        glow(c, sx, top + th * .5 * ks, 120, hexc('#FFB347'), .4 * ks)
    c.restore()
    k = prog(t, T_3000B, T_3000B + .45)
    big_number(c, '3,000 km', 960, 260, 150, hexc('#FFF1D6'), t, T_3000B, alpha=1 - plunge, glow_=.35)
    draw_text(c, 'DEEP', 960, 330, mono(28, 'semi'), hexc('#E3B47A'), 'center', alpha=e_out(k) * (1 - plunge), spacing=8)
    flash(c, e_in(prog(t, T_OBSTACLE - .25, T_OBSTACLE)) * .9, '#FFF1D6')

# ------------------------------------------------------------------ S17 speed 170,000 km/h
def s17(c, t):
    lt = t - T_OBSTACLE
    # star streaks
    space(c, t, ox=-lt * 120, star_alpha=.6)
    sp = e_in(prog(t, T_SPEED, T_170 + 1.5))
    speed_lines(c, t, .2 + .6 * sp, direction=(-.86, -.5), n=80, speed=1500 + 5000 * sp, length=120 + 400 * sp, color='#cfe0ff', width=2)
    draw_jupiter(c, 1750 + lt * 3, 1300, 1150 + lt * 12, rot=2.0 + t * .01)
    px = 760 + math.sin(t * 7) * 2 * sp; py = 520 + math.cos(t * 9) * 2 * sp
    draw_galileo_entry(c, px, py, .9, 30, heat=0)
    kv = prog(t, T_170 - .2, T_170 + 2.2)
    v = int(170000 * e_out(kv)) // 100 * 100
    hud_readout(c, 1260, 150, 560, 'APPROACH SPEED', f'{v:,}', 'km/h', e_out(prog(t, T_SPEED, T_SPEED + .5)), sub='≈ 47 km EVERY SECOND' if kv > .9 else ' ', size=64)
    ks = prog(t, T_SIMILAR, T_SIMILAR + .5)
    if ks > 0:
        draw_tag(c, 'SAME AS GALILEO ENTRY SPEED · 1995', 1260, 360, 'hist', alpha=e_out(ks))
    draw_tag(c, 'ILLUSTRATION · YOUR APPROACH', 40, 36, 'concept')

SHOTS1 = [
    (0.0, s01, ('cut', 0)),
    (T_DROPPED, s02, ('fade', .35)),
    (T_WINDS, s03, ('flash', .25)),
    (T_KEPT, s04, ('fade', .4)),
    (T_THEN58, s05, ('fade', .4)),
    (T_BUTHERE, s06, ('black', .5)),
    (T_SOLID - .2, s07, ('fade', .4)),
    (T_FINDOUT, s08, ('fade', .45)),
    (T_BUTFIRST, s09, ('whip', .35)),
    (T_NOWHERE, s10, ('black', .3)),
    (T_REDOVAL, s11, ('fade', .5)),
    (T_CLOUDS, s12, ('fade', .5)),
    (T_ENORMOUS, s13, ('whip', .35)),
    (T_YET, s14, ('fade', .4)),
    (T_UNSETTLE, s15, ('fade', .5)),
    (T_3000B, s16, ('cut', 0)),
    (T_OBSTACLE, s17, ('flash', .3)),
]
