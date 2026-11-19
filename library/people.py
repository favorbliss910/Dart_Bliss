"""Human characters in the reference style: big white bean heads with thick ink
outlines, white disc eyes with dot pupils, pill-shaped coloured bodies, thin black
stick limbs. Painterly volume via the shared shading helpers."""
import math
import sys
import os

import cairo

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'drongo'))
from chars import (C, INK, src, ellipse, stick, eye, fill_stroke, soft_ellipse, form_shade, rim,  # noqa: E402
                   clipped, contact_shadow, grad_fill)

PI = math.pi
SKIN = C('#fbfaf6')
SKIN_SH = C('#d9d6d0')
SKIN_HI = C('#ffffff')


def _shade(col, k):
    return tuple(max(0, min(1, c * k)) for c in col[:3])


def person(ctx, x, y, s=1.0, body=C('#7b5cc4'), hair='short', hair_col=C('#4a3426'), look=(0, 0),
           mouth='flat', blink=0.0, brows=None, arms='down', sit=False, lean=0.0, tilt=0.0,
           glasses=False, coat=None, beard=0.0, tears=0.0, eyes='normal', lid=0.0, flip=False,
           hat=None, scarf=None, height=1.0, head_col=None, no_mouth=False, step=0.0,
           hold=None, shadow=True, pale=False, underlight=None, sweat=0):
    """Origin at the feet (or the seat when sit=True). ~270 units tall at s=1."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(-s if flip else s, s)
    lw = 5.2
    leg = 92 * height
    if shadow and not sit:
        contact_shadow(ctx, 0, 0, 70, 12, 0.35)

    # ---- legs
    if sit:
        stick(ctx, [(-12, -4), (18, -2), (34, 0)], lw)
        stick(ctx, [(12, -4), (40, -2), (54, 0)], lw)
        stick(ctx, [(34, 0), (36, 60)], lw)
        stick(ctx, [(54, 0), (56, 60)], lw)
        hip = 0
    else:
        sw = math.sin(step) * 14
        stick(ctx, [(-12, -leg), (-14 + sw * 0.5, -leg / 2), (-15 + sw, -2)], lw)
        stick(ctx, [(12, -leg), (14 - sw * 0.5, -leg / 2), (15 - sw, -2)], lw)
        for fx in (-15 + sw, 15 - sw):
            ellipse(ctx, fx + (4 if fx > 0 else -4), -1, 9, 4.5)
            src(ctx, INK)
            ctx.fill()
        hip = -leg

    ctx.save()
    ctx.translate(0, hip)
    ctx.rotate(lean)
    bh = 104
    bw = 34

    def body_path():
        ctx.move_to(-bw + 4, -bh)
        ctx.curve_to(-bw - 2, -bh * 0.6, -bw - 4, -12, -bw + 6, 0)
        ctx.curve_to(-14, 6, 14, 6, bw - 6, 0)
        ctx.curve_to(bw + 4, -12, bw + 2, -bh * 0.6, bw - 4, -bh)
        ctx.curve_to(10, -bh - 10, -10, -bh - 10, -bw + 4, -bh)
        ctx.close_path()

    bcol = coat or body
    long_coat = coat is not None and coat == C('#2b2b33')
    if long_coat:  # librarian's long dark coat down to the shins
        def coat_path():
            ctx.move_to(-bw + 4, -bh)
            ctx.curve_to(-bw - 6, -bh * 0.4, -bw - 14, leg * 0.5, -bw - 10, leg * 0.75)
            ctx.line_to(bw + 10, leg * 0.75)
            ctx.curve_to(bw + 14, leg * 0.5, bw + 6, -bh * 0.4, bw - 4, -bh)
            ctx.curve_to(10, -bh - 10, -10, -bh - 10, -bw + 4, -bh)
            ctx.close_path()
        form_shade(ctx, coat_path, bcol, _shade(bcol, 1.5), _shade(bcol, 0.55), (-bw - 14, -bh - 10, bw + 14, leg * 0.75))
        rim(ctx, coat_path, C('#9fb4ff'), 4, 3, 4, 0.35)
        coat_path()
        ctx.set_line_width(lw)
        src(ctx, INK)
        ctx.stroke()
        stick(ctx, [(0, -bh + 10), (0, leg * 0.7)], 2.5, _shade(bcol, 0.4))
    else:
        form_shade(ctx, body_path, bcol, _shade(bcol, 1.25), _shade(bcol, 0.62), (-bw - 4, -bh - 10, bw + 4, 6),
                   ao=[(0, -bh - 2, 30, 10)])
        if coat:  # lab coat: lapels + pocket + pens
            stick(ctx, [(-6, -bh + 4), (0, -bh * 0.45), (6, -bh + 4)], 3.2)
            stick(ctx, [(0, -bh * 0.45), (0, -4)], 2.4, C('#9aa0aa'))
            ctx.rectangle(10, -bh * 0.62, 16, 14)
            ctx.set_line_width(2.6)
            src(ctx, INK)
            ctx.stroke()
            for k, pc in enumerate((C('#2f6fd6'), C('#d6332f'))):
                stick(ctx, [(14 + k * 6, -bh * 0.62 + 2), (14 + k * 6, -bh * 0.62 - 6)], 2.6, pc)
        rim(ctx, body_path, (1, 1, 1), 4, 3, 4, 0.35)
        body_path()
        ctx.set_line_width(lw)
        src(ctx, INK)
        ctx.stroke()
    if scarf:
        ctx.move_to(-bw + 2, -bh + 2)
        ctx.curve_to(-10, -bh + 16, 10, -bh + 16, bw - 2, -bh + 2)
        ctx.line_to(bw - 4, -bh - 8)
        ctx.curve_to(10, -bh + 2, -10, -bh + 2, -bw + 4, -bh - 8)
        ctx.close_path()
        fill_stroke(ctx, scarf, 4)
        ctx.rectangle(8, -bh + 8, 14, 40)
        fill_stroke(ctx, scarf, 4)

    # ---- arms
    sh_l, sh_r = (-bw + 4, -bh + 14), (bw - 4, -bh + 14)
    A = {
        'down': [[sh_l, (-bw - 8, -bh * 0.55), (-bw - 6, -bh * 0.18)], [sh_r, (bw + 8, -bh * 0.55), (bw + 6, -bh * 0.18)]],
        'read': [[sh_l, (-bw - 4, -bh * 0.45), (-14, -bh * 0.5)], [sh_r, (bw + 4, -bh * 0.45), (14, -bh * 0.5)]],
        'hug': [[sh_l, (-bw + 6, -bh * 0.55), (8, -bh * 0.7)], [sh_r, (bw - 4, -bh * 0.5), (-6, -bh * 0.62)]],
        'reach': [[sh_l, (-bw - 8, -bh * 0.55), (-bw - 6, -bh * 0.18)], [sh_r, (bw + 30, -bh * 0.9), (bw + 70, -bh * 1.05)]],
        'shh': [[sh_l, (-bw - 8, -bh * 0.55), (-bw - 6, -bh * 0.18)], [sh_r, (bw + 6, -bh * 0.6), (6, -bh - 38)]],
        'whisper': [[sh_l, (-bw - 8, -bh * 0.55), (-bw - 6, -bh * 0.18)], [sh_r, (bw + 10, -bh * 0.7), (bw + 4, -bh - 44)]],
        'face': [[sh_l, (-bw - 4, -bh * 0.6), (-24, -bh - 44)], [sh_r, (bw + 4, -bh * 0.6), (24, -bh - 44)]],
        'sneak': [[sh_l, (-bw - 14, -bh * 0.8), (-bw - 22, -bh * 0.5)], [sh_r, (bw + 26, -bh * 0.95), (bw + 50, -bh * 1.1)]],
        'up': [[sh_l, (-bw - 22, -bh * 0.9), (-bw - 26, -bh * 1.4)], [sh_r, (bw + 22, -bh * 0.9), (bw + 26, -bh * 1.4)]],
        'cheeks': [[sh_l, (-bw - 30, -bh * 0.55), (-50, -bh - 34)], [sh_r, (bw + 30, -bh * 0.55), (50, -bh - 34)]],
    }
    arm_list = A[arms] if isinstance(arms, str) else arms
    if hold:
        hold(ctx, bh)
    for a in arm_list:
        stick(ctx, a, lw)
        ellipse(ctx, a[-1][0], a[-1][1], 6, 6)
        src(ctx, INK)
        ctx.fill()

    # ---- head
    ctx.save()
    ctx.translate(0, -bh)
    ctx.rotate(tilt)
    hy = -44
    hcol = head_col or (C('#eceae6') if pale else SKIN)

    def head():
        ctx.move_to(-50, hy)
        ctx.curve_to(-52, hy - 66, 52, hy - 66, 50, hy)
        ctx.curve_to(50, hy + 48, -50, hy + 48, -50, hy)
        ctx.close_path()

    # hair behind (bun / long)
    if hair == 'bun':
        ellipse(ctx, 0, hy - 60, 22, 18)
        fill_stroke(ctx, hair_col, lw)
    form_shade(ctx, head, hcol, SKIN_HI, SKIN_SH if not pale else C('#bdbab4'), (-52, hy - 50, 52, hy + 36))
    if underlight:
        clipped(ctx, head, lambda: (soft_ellipse(ctx, 0, hy + 40, 70, 46, underlight, 0.75),
                                    soft_ellipse(ctx, 0, hy + 30, 40, 24, (1, 1, 1), 0.35)))
    head()
    ctx.set_line_width(lw)
    src(ctx, INK)
    ctx.stroke()
    # hair on top
    if hair in ('short', 'bun', 'bowl', 'messy', 'side'):
        def hair_path():
            ctx.move_to(-50, hy - 4)
            if hair == 'side':
                ctx.curve_to(-54, hy - 68, 40, hy - 74, 52, hy - 10)
                ctx.curve_to(30, hy - 28, -10, hy - 20, -26, hy - 30)
                ctx.curve_to(-34, hy - 18, -42, hy - 10, -50, hy - 4)
            else:
                ctx.curve_to(-54, hy - 68, 54, hy - 68, 50, hy - 4)
                ctx.curve_to(40, hy - 22, 20, hy - 24, 0, hy - 22)
                ctx.curve_to(-20, hy - 24, -40, hy - 22, -50, hy - 4)
            ctx.close_path()
        form_shade(ctx, hair_path, hair_col, _shade(hair_col, 1.6), _shade(hair_col, 0.6), (-52, hy - 52, 52, hy - 4))
        hair_path()
        ctx.set_line_width(lw)
        src(ctx, INK)
        ctx.stroke()
        if hair == 'messy':
            for k in range(5):
                stick(ctx, [(-30 + k * 15, hy - 40), (-34 + k * 15, hy - 52)], 3.5, INK)
        stick(ctx, [(-20, hy - 34), (-2, hy - 26)], 2.2, _shade(hair_col, 1.8))
    elif hair == 'grey':
        hair_path = lambda: (ctx.move_to(-50, hy - 4), ctx.curve_to(-54, hy - 68, 54, hy - 68, 50, hy - 4),
                             ctx.curve_to(30, hy - 30, -30, hy - 30, -50, hy - 4), ctx.close_path())
        form_shade(ctx, hair_path, C('#b9bcc4'), C('#e6e8ee'), C('#7f838d'), (-52, hy - 52, 52, hy - 4))
        hair_path()
        ctx.set_line_width(lw)
        src(ctx, INK)
        ctx.stroke()
    if hat == 'beanie':
        def hat_path():
            ctx.move_to(-52, hy - 12)
            ctx.curve_to(-54, hy - 80, 54, hy - 80, 52, hy - 12)
            ctx.close_path()
        form_shade(ctx, hat_path, C('#c0453c'), C('#e2685d'), C('#82271f'), (-54, hy - 64, 54, hy - 12))
        hat_path()
        ctx.set_line_width(lw)
        src(ctx, INK)
        ctx.stroke()
        ctx.rectangle(-54, hy - 22, 108, 16)
        fill_stroke(ctx, C('#e9e2d6'), 4)
        ellipse(ctx, 0, hy - 72, 10, 10)
        fill_stroke(ctx, C('#e9e2d6'), 4)
    if beard > 0:
        ctx.move_to(-40, hy + 6)
        ctx.curve_to(-36, hy + 30 + 80 * beard, 36, hy + 30 + 80 * beard, 40, hy + 6)
        ctx.curve_to(20, hy + 18, -20, hy + 18, -40, hy + 6)
        fill_stroke(ctx, C('#8a8e98') if beard > 0.6 else C('#5a4030'), 4.4)

    # eyes (reference: two big touching discs)
    er = {'normal': 15, 'wide': 18, 'small': 12, 'huge': 22}[eyes]
    pr = {'normal': 5.4, 'wide': 3.4, 'small': 4.6, 'huge': 3.0}[eyes]
    ey = hy + (4 if eyes == 'huge' else -4)
    for sx in ((-21, 21) if eyes == 'huge' else (-17, 17)):
        eye(ctx, sx, ey, er, look, pupil=pr, blink=blink, lid=lid)
    if glasses:
        for sx in (-17, 17):
            ctx.new_path()
            ctx.arc(sx, hy - 4, er + 5, 0, 2 * PI)
            ctx.set_line_width(3.4)
            src(ctx, INK)
            ctx.stroke()
            soft_ellipse(ctx, sx - 5, hy - 10, 6, 4, (1, 1, 1), 0.55)
        stick(ctx, [(-2, hy - 6), (2, hy - 6)], 3)
    if brows:
        for side in (-1, 1):
            if brows == 'shock':
                a, b = (side * 36, hy - 34), (side * 8, hy - 46)
            elif brows == 'worried':
                a, b = (side * 30, hy - 22), (side * 8, hy - 30)
            elif brows == 'angry':
                a, b = (side * 30, hy - 30), (side * 8, hy - 22)
            else:
                a, b = (side * 30, hy - 32), (side * 8, hy - 34)
            stick(ctx, [a, b], 4.2)
    if tears > 0:
        for sx in (-17, 17):
            ctx.move_to(sx - 4, hy + 8)
            ctx.curve_to(sx - 8, hy + 8 + 20 * tears, sx + 2, hy + 18 + 30 * tears, sx - 2, hy + 26 + 50 * tears)
            ctx.set_line_width(6)
            src(ctx, C('#7fc8ff', 0.9))
            ctx.stroke()
    # mouth
    my = hy + 22
    if not no_mouth:
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        if mouth == 'flat':
            stick(ctx, [(-6, my), (6, my)], 3.6)
        elif mouth == 'smile':
            ctx.new_path()
            ctx.arc(0, my - 8, 10, 0.25 * PI, 0.75 * PI)
            ctx.set_line_width(3.6)
            src(ctx, INK)
            ctx.stroke()
        elif mouth == 'frown':
            ctx.new_path()
            ctx.arc(0, my + 8, 9, 1.2 * PI, 1.8 * PI)
            ctx.set_line_width(3.6)
            src(ctx, INK)
            ctx.stroke()
        elif mouth == 'o':
            ellipse(ctx, 0, my + 2, 6, 7)
            fill_stroke(ctx, C('#5a1f1f'), 3.4)
        elif mouth == 'wobble':
            ctx.move_to(-12, my)
            for i in range(6):
                ctx.line_to(-12 + i * 5, my + (3 if i % 2 else -2))
            ctx.set_line_width(3.2)
            src(ctx, INK)
            ctx.stroke()
        elif mouth == 'grin':
            ctx.move_to(-14, my - 4)
            ctx.curve_to(-8, my + 12, 8, my + 12, 14, my - 4)
            ctx.close_path()
            fill_stroke(ctx, (1, 1, 1), 3.4)
        elif mouth == 'scream':  # huge shocked O with tongue
            def mo():
                ellipse(ctx, 0, my + 8, 14, 21)
            mo()
            src(ctx, C('#4a1418'))
            ctx.fill()
            clipped(ctx, mo, lambda: (ellipse(ctx, 0, my + 26, 12, 9), src(ctx, C('#e0707a')), ctx.fill()))
            mo()
            ctx.set_line_width(4)
            src(ctx, INK)
            ctx.stroke()
        elif mouth == 'whisper':
            ellipse(ctx, 4, my, 4, 3)
            fill_stroke(ctx, C('#5a1f1f'), 2.8)
    for k in range(int(sweat)):
        sx, sy = (58, hy - 30) if k == 0 else (-60, hy - 18)
        ctx.move_to(sx, sy)
        ctx.curve_to(sx - 9, sy + 14, sx - 6, sy + 22, sx, sy + 22)
        ctx.curve_to(sx + 6, sy + 22, sx + 9, sy + 14, sx, sy)
        fill_stroke(ctx, C('#9fdcff'), 3)
    ctx.restore()  # head
    ctx.restore()  # lean
    ctx.restore()


def librarian(ctx, x, y, s=1.0, look=(0, 0.1), blink=0.0, lid=0.45, arms='down', lean=0.0, tilt=0.0,
              flip=False, ghost=0.0):
    """Tall, pale, silent: long charcoal coat, grey bun, round glasses, no mouth."""
    if ghost > 0:
        ctx.push_group()
    person(ctx, x, y, s * 1.12, coat=C('#2b2b33'), hair='bun', hair_col=C('#9a9ea8'), look=look, blink=blink,
           lid=lid, glasses=True, no_mouth=False, mouth='flat', arms=arms, lean=lean, tilt=tilt, flip=flip,
           height=1.2, pale=True, eyes='small')
    if ghost > 0:
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(1 - ghost)


# --------------------------------------------------------------------------- props
def book_open(ctx, x, y, s=1.0, text=0.0, glow=0.0, flip=0.0, seed=0, color=C('#7a2e2e'), ink=None,
              drawing=None):
    """Open book seen from slightly above. text 0..1 reveals handwriting lines."""
    import random
    rnd = random.Random(seed)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    soft_ellipse(ctx, 0, 70, 260, 34, INK, 0.35)
    # cover
    ctx.move_to(-250, -100)
    ctx.curve_to(-120, -120, -20, -110, 0, -96)
    ctx.curve_to(20, -110, 120, -120, 250, -100)
    ctx.line_to(258, 74)
    ctx.curve_to(120, 56, 20, 66, 0, 80)
    ctx.curve_to(-20, 66, -120, 56, -258, 74)
    ctx.close_path()
    fill_stroke(ctx, color, 5)
    for side in (-1, 1):
        def page():
            ctx.move_to(0, -88)
            ctx.curve_to(side * 30, -104, side * 140, -112, side * 236, -92)
            ctx.line_to(side * 242, 62)
            ctx.curve_to(side * 140, 46, side * 30, 52, 0, 70)
            ctx.close_path()
        grad_fill(ctx, page, C('#fbf6e9'), C('#e6dcc4'), side * 240, 0, 0, 0)
        clipped(ctx, page, lambda: soft_ellipse(ctx, side * 10, 0, 50, 160, C('#b9a986'), 0.55))
        page()
        ctx.set_line_width(4)
        src(ctx, INK)
        ctx.stroke()
        if text > 0:
            lines = 9
            for i in range(lines):
                k = max(0.0, min(1.0, text * lines * 1.0 - i - (0 if side < 0 else lines * 0.0)))
                if side > 0:
                    k = max(0.0, min(1.0, (text - 0.5) * 2 * lines - i))
                else:
                    k = max(0.0, min(1.0, text * 2 * lines - i))
                if k <= 0:
                    continue
                yy = -66 + i * 14
                x0 = side * 26 if side > 0 else -210
                L = 180 * k * rnd.uniform(0.75, 1.0)
                ctx.move_to(x0, yy)
                n = int(L / 6)
                for j in range(n):
                    ctx.line_to(x0 + j * 6, yy + rnd.uniform(-2.5, 2.5))
                ctx.set_line_width(2.2)
                src(ctx, ink or C('#3b2a5a', 0.9))
                ctx.stroke()
        if drawing and side > 0:
            drawing(ctx)
    if glow > 0:
        soft_ellipse(ctx, 0, -20, 280 * (0.8 + 0.2 * glow), 160, C('#ffe9a8'), 0.45 * glow)
    if flip > 0:  # a page turning over
        a = flip * PI
        w = 236 * math.cos(a)
        ctx.move_to(0, -88)
        ctx.curve_to(w * 0.2, -100 - 40 * math.sin(a), w * 0.7, -110 - 40 * math.sin(a), w, -92 - 20 * math.sin(a))
        ctx.line_to(w * 1.02, 62 - 20 * math.sin(a))
        ctx.curve_to(w * 0.6, 46, w * 0.15, 52, 0, 70)
        ctx.close_path()
        fill_stroke(ctx, C('#fffaf0'), 4)
    ctx.restore()


def book_closed(ctx, x, y, s=1.0, color=C('#5b2b6b'), open_k=0.0, glow=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    soft_ellipse(ctx, 10, 40, 200, 30, INK, 0.4)
    # pages block
    ctx.move_to(-170, -10)
    ctx.line_to(170, -10)
    ctx.line_to(170, 30)
    ctx.line_to(-170, 30)
    ctx.close_path()
    fill_stroke(ctx, C('#efe6cf'), 4)
    for i in range(5):
        stick(ctx, [(-160, -2 + i * 7), (160, -2 + i * 7)], 1.2, C('#bfb093'))
    if glow > 0:
        soft_ellipse(ctx, 0, -20, 260, 110, C('#ffe39a'), 0.7 * glow)
    # pages' top surface (revealed as the lid lifts)
    ctx.move_to(-170, -150)
    ctx.line_to(170, -150)
    ctx.line_to(170, -10)
    ctx.line_to(-170, -10)
    ctx.close_path()
    fill_stroke(ctx, C('#f6eedb'), 4)
    if glow > 0:
        soft_ellipse(ctx, 0, -80, 200, 90, C('#fff2c0'), 0.9 * glow)
    # lid hinged at the back edge (y=-150); front edge swings up and over
    th = open_k * PI * 0.62
    fy = -150 + 140 * math.cos(th) + 10
    wid = 178 * (1 + 0.06 * math.sin(th))
    if fy > -150:
        quad = lambda: (ctx.move_to(-178, -150), ctx.line_to(178, -150), ctx.line_to(wid, fy), ctx.line_to(-wid, fy), ctx.close_path())
        form_shade(ctx, quad, color, _shade(color, 1.5), _shade(color, 0.6), (-178, -150, 178, fy))
        quad()
        ctx.set_line_width(5)
        src(ctx, INK)
        ctx.stroke()
        k = (fy + 150) / 150
        ctx.rectangle(-120, -150 + 38 * k, 240, 74 * k)
        ctx.set_line_width(3)
        src(ctx, C('#d6b25a'))
        ctx.stroke()
    else:  # inside of the cover faces us, lit by the pages
        quad = lambda: (ctx.move_to(-178, -150), ctx.line_to(178, -150), ctx.line_to(wid, fy), ctx.line_to(-wid, fy), ctx.close_path())
        grad_fill(ctx, quad, C('#efe2c4'), C('#c9b48a'), 0, fy, 0, -150)
        quad()
        ctx.set_line_width(5)
        src(ctx, INK)
        ctx.stroke()
        stick(ctx, [(-wid, fy), (wid, fy)], 7, color)
    ctx.restore()


def car(ctx, x, y, s=1.0, color=C('#d23b33'), lights=False):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    soft_ellipse(ctx, 0, 6, 190, 14, INK, 0.45)

    def body():
        ctx.move_to(-170, -10)
        ctx.line_to(-176, -50)
        ctx.curve_to(-170, -66, -130, -70, -100, -72)
        ctx.line_to(-60, -120)
        ctx.curve_to(-20, -128, 50, -128, 80, -118)
        ctx.line_to(120, -74)
        ctx.curve_to(160, -70, 178, -60, 178, -40)
        ctx.line_to(176, -10)
        ctx.close_path()
    form_shade(ctx, body, color, _shade(color, 1.35), _shade(color, 0.55), (-176, -128, 178, -10))
    rim(ctx, body, (1, 1, 1), 4, 3, 4, 0.4)
    body()
    ctx.set_line_width(5)
    src(ctx, INK)
    ctx.stroke()
    for wx0, wx1 in ((-90, -14), (0, 104)):
        ctx.move_to(wx0, -76)
        ctx.line_to(wx0 + 34 if wx0 < 0 else wx0, -114)
        ctx.line_to(wx1 - (0 if wx0 < 0 else 30), -114)
        ctx.line_to(wx1, -76)
        ctx.close_path()
        fill_stroke(ctx, C('#9fc3d8'), 4)
    for wx in (-104, 112):
        ellipse(ctx, wx, -8, 34, 34)
        fill_stroke(ctx, C('#24242a'), 5)
        ellipse(ctx, wx, -8, 14, 14)
        fill_stroke(ctx, C('#b8bcc6'), 3)
    if lights:
        soft_ellipse(ctx, 200, -46, 120, 40, C('#fff3b0'), 0.6)
    ellipse(ctx, 168, -46, 9, 7)
    fill_stroke(ctx, C('#fff3b0'), 3)
    ctx.restore()


def cctv(ctx, x, y, s=1.0, rec=True, rot=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.rotate(rot)
    stick(ctx, [(0, 0), (0, -40)], 8)
    ctx.rectangle(-70, -84, 120, 52)
    form_shade(ctx, lambda: ctx.rectangle(-70, -84, 120, 52), C('#e6e7eb'), C('#ffffff'), C('#9ea2ac'), (-70, -84, 50, -32))
    ctx.rectangle(-70, -84, 120, 52)
    ctx.set_line_width(5)
    src(ctx, INK)
    ctx.stroke()
    ctx.rectangle(50, -76, 22, 36)
    fill_stroke(ctx, C('#3a3d45'), 5)
    ellipse(ctx, 72, -58, 12, 14)
    fill_stroke(ctx, C('#1b1d22'), 4)
    soft_ellipse(ctx, 69, -62, 4, 4, (1, 1, 1), 0.7)
    if rec:
        soft_ellipse(ctx, -50, -70, 16, 16, C('#ff3030'), 0.8)
        ellipse(ctx, -50, -70, 6, 6)
        src(ctx, C('#ff4040'))
        ctx.fill()
    ctx.restore()


def lamp(ctx, x, y, s=1.0, on=True):
    """Green banker's lamp; origin at base."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ellipse(ctx, 0, -4, 34, 8)
    fill_stroke(ctx, C('#b08a3e'), 4)
    stick(ctx, [(0, -6), (0, -70)], 6, C('#b08a3e'))
    stick(ctx, [(0, -6), (0, -70)], 2, INK)
    ctx.move_to(-56, -60)
    ctx.curve_to(-50, -96, 50, -96, 56, -60)
    ctx.close_path()
    form_shade(ctx, lambda: (ctx.move_to(-56, -60), ctx.curve_to(-50, -96, 50, -96, 56, -60), ctx.close_path()),
               C('#2f7a4a'), C('#5fb57d'), C('#1a4a2b'), (-56, -92, 56, -60))
    ctx.move_to(-56, -60)
    ctx.curve_to(-50, -96, 50, -96, 56, -60)
    ctx.close_path()
    ctx.set_line_width(4.4)
    src(ctx, INK)
    ctx.stroke()
    if on:
        ellipse(ctx, 0, -60, 52, 6)
        src(ctx, C('#fff2b8'))
        ctx.fill()
    ctx.restore()
