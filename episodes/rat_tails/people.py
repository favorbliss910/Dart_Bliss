"""Rat Tails cast, in the reference style (copied from library/people.py and extended):
big white bean heads with thick ink outlines, white disc eyes with dot pupils,
pill-shaped coloured bodies, thin black stick limbs, painterly volume.

New for this episode: period hats (conical non la, pith helmet, kepi, turban),
moustaches, side-buttoned tunics, more arm poses with a hand callback, and the
rats themselves plus the episode's props."""
import math
import sys
import os

import cairo

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'drongo'))
from chars import (C, INK, src, ellipse, stick, eye, fill_stroke, soft_ellipse, form_shade, rim,  # noqa: E402
                   clipped, contact_shadow, grad_fill, taper)

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
           hold=None, shadow=True, pale=False, underlight=None, sweat=0, moustache=None, tunic=False,
           hand=None, pants=None, pupil_scale=1.0, cheeks=0.0):
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
        if pants:  # loose period trousers over the stick legs
            for sx, ww in ((-1, sw), (1, -sw)):
                ctx.move_to(sx * 4, -leg - 4)
                ctx.line_to(sx * 26, -leg - 4)
                ctx.line_to(sx * 15 + ww * 0.8 + sx * 9, -leg * 0.22)
                ctx.line_to(sx * 15 + ww * 0.8 - sx * 9, -leg * 0.22)
                ctx.close_path()
                fill_stroke(ctx, pants, lw * 0.8)
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
        if tunic:  # high collar + diagonal side buttons (period tunic)
            ctx.rectangle(-14, -bh - 4, 28, 10)
            fill_stroke(ctx, _shade(bcol, 0.8), 3)
            stick(ctx, [(4, -bh + 6), (22, -bh * 0.55), (24, -6)], 2.6, _shade(bcol, 0.45))
            for k in range(4):
                yy = -bh + 16 + k * 20
                ellipse(ctx, 6 + min(k, 2) * 7 + (k > 2) * 3, yy, 2.6, 2.6)
                src(ctx, C('#e8d9a8'))
                ctx.fill()
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
        'give': [[sh_l, (-bw - 8, -bh * 0.55), (-bw - 6, -bh * 0.18)], [sh_r, (bw + 30, -bh * 0.7), (bw + 74, -bh * 0.72)]],
        'hold_up': [[sh_l, (-bw - 8, -bh * 0.55), (-bw - 6, -bh * 0.18)], [sh_r, (bw + 26, -bh * 1.0), (bw + 30, -bh * 1.55)]],
        'wag': [[sh_l, (-bw - 8, -bh * 0.55), (-bw - 6, -bh * 0.18)], [sh_r, (bw + 30, -bh * 0.75), (bw + 34, -bh * 1.3)]],
        'pinch': [[sh_l, (-bw - 8, -bh * 0.55), (-bw - 6, -bh * 0.18)], [sh_r, (bw + 14, -bh * 0.7), (4, -bh - 22)]],
        'hips': [[sh_l, (-bw - 30, -bh * 0.6), (-bw + 2, -bh * 0.3)], [sh_r, (bw + 30, -bh * 0.6), (bw - 2, -bh * 0.3)]],
        'twirl': [[sh_l, (-bw - 8, -bh * 0.55), (-bw - 6, -bh * 0.18)], [sh_r, (bw + 26, -bh * 0.8), (bw + 18, -bh - 62)]],
        'carry': [[sh_l, (-bw - 14, -bh * 0.75), (-30, -bh - 6)], [sh_r, (bw + 14, -bh * 0.75), (30, -bh - 6)]],
        'both_out': [[sh_l, (-bw - 30, -bh * 0.7), (-bw - 70, -bh * 0.72)], [sh_r, (bw + 30, -bh * 0.7), (bw + 70, -bh * 0.72)]],
        'pocket': [[sh_l, (-bw - 8, -bh * 0.55), (-bw - 6, -bh * 0.18)], [sh_r, (bw + 12, -bh * 0.5), (bw - 8, -bh * 0.22)]],
        'lantern': [[sh_l, (-bw - 8, -bh * 0.55), (-bw - 6, -bh * 0.18)], [sh_r, (bw + 30, -bh * 0.6), (bw + 56, -bh * 0.55)]],
        'scoop': [[sh_l, (-bw - 4, -bh * 0.4), (-22, -bh * 0.2)], [sh_r, (bw + 4, -bh * 0.4), (22, -bh * 0.2)]],
    }
    arm_list = A[arms] if isinstance(arms, str) else arms
    if hold:
        hold(ctx, bh)
    for a in arm_list:
        stick(ctx, a, lw)
        ellipse(ctx, a[-1][0], a[-1][1], 6, 6)
        src(ctx, INK)
        ctx.fill()
    if hand:  # prop held in the right hand, drawn in torso space at the hand point
        hand(ctx, *arm_list[1][-1])

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

    if hat == 'conical':  # non la: wide straw cone with weave rings and a chin strap
        stick(ctx, [(-40, hy + 10), (-10, hy + 40), (10, hy + 40), (40, hy + 10)], 2.2, C('#7a5a2a'))

        def cone():
            ctx.move_to(-118, hy - 34)
            ctx.line_to(0, hy - 126)
            ctx.line_to(118, hy - 34)
            ctx.curve_to(60, hy - 22, -60, hy - 22, -118, hy - 34)
            ctx.close_path()
        form_shade(ctx, cone, C('#e3c27a'), C('#f8e3a8'), C('#a8823e'), (-118, hy - 126, 118, hy - 24))
        clipped(ctx, cone, lambda: [stick(ctx, [(-118 + k * 23, hy - 34 + k * 9.4), (0, hy - 126),
                                                 (118 - k * 23, hy - 34 + k * 9.4)], 1.6, C('#b8954e', 0.7))
                                    for k in range(1, 5)])
        cone()
        ctx.set_line_width(lw)
        src(ctx, INK)
        ctx.stroke()
    elif hat == 'pith':  # white colonial sun helmet
        def dome():
            ctx.move_to(-56, hy - 22)
            ctx.curve_to(-58, hy - 104, 58, hy - 104, 56, hy - 22)
            ctx.close_path()
        form_shade(ctx, dome, C('#efe9da'), C('#ffffff'), C('#bdb39a'), (-58, hy - 100, 58, hy - 22))
        dome()
        ctx.set_line_width(lw)
        src(ctx, INK)
        ctx.stroke()
        ctx.rectangle(-56, hy - 34, 112, 12)
        fill_stroke(ctx, C('#cfc4a6'), 3.5)
        ellipse(ctx, 0, hy - 20, 74, 9)
        fill_stroke(ctx, C('#f4efe2'), 4)
        ellipse(ctx, 0, hy - 92, 7, 5)
        fill_stroke(ctx, C('#d8cfb6'), 3)
    elif hat == 'kepi':  # flat-topped peaked cap (inspector)
        ctx.move_to(-44, hy - 30)
        ctx.line_to(-38, hy - 84)
        ctx.line_to(38, hy - 84)
        ctx.line_to(44, hy - 30)
        ctx.close_path()
        form_shade(ctx, lambda: (ctx.move_to(-44, hy - 30), ctx.line_to(-38, hy - 84), ctx.line_to(38, hy - 84),
                                 ctx.line_to(44, hy - 30), ctx.close_path()),
                   C('#2a3550'), C('#4a5a80'), C('#151a28'), (-44, hy - 84, 44, hy - 30))
        ctx.move_to(-44, hy - 30)
        ctx.line_to(-38, hy - 84)
        ctx.line_to(38, hy - 84)
        ctx.line_to(44, hy - 30)
        ctx.close_path()
        ctx.set_line_width(lw)
        src(ctx, INK)
        ctx.stroke()
        stick(ctx, [(-42, hy - 44), (42, hy - 44)], 4, C('#d6b25a'))
        ctx.move_to(-46, hy - 30)
        ctx.curve_to(-20, hy - 16, 40, hy - 14, 62, hy - 26)
        ctx.line_to(46, hy - 32)
        ctx.close_path()
        fill_stroke(ctx, C('#151a28'), 4)
    elif hat == 'turban':  # khan xep: wrapped band
        def band():
            ctx.move_to(-52, hy - 26)
            ctx.curve_to(-56, hy - 78, 56, hy - 78, 52, hy - 26)
            ctx.curve_to(20, hy - 34, -20, hy - 34, -52, hy - 26)
            ctx.close_path()
        form_shade(ctx, band, hair_col, _shade(hair_col, 1.5), _shade(hair_col, 0.55), (-56, hy - 74, 56, hy - 26))
        clipped(ctx, band, lambda: [stick(ctx, [(-60, hy - 36 - k * 11), (60, hy - 44 - k * 11)], 2.2,
                                           _shade(hair_col, 0.6)) for k in range(4)])
        band()
        ctx.set_line_width(lw)
        src(ctx, INK)
        ctx.stroke()
    if moustache:
        for sd in (-1, 1):
            ctx.move_to(0, hy + 12)
            if moustache == 'handlebar':
                ctx.curve_to(sd * 12, hy + 6, sd * 26, hy + 20, sd * 34, hy + 6)
                ctx.curve_to(sd * 30, hy + 22, sd * 12, hy + 20, 0, hy + 16)
            else:
                ctx.curve_to(sd * 10, hy + 8, sd * 18, hy + 14, sd * 20, hy + 20)
                ctx.curve_to(sd * 10, hy + 20, sd * 4, hy + 18, 0, hy + 16)
            ctx.close_path()
            fill_stroke(ctx, hair_col if hair_col else INK, 2.4)
    if cheeks > 0:
        for sx in (-34, 34):
            soft_ellipse(ctx, sx, hy + 12, 12, 7, C('#ff8a8a'), 0.45 * cheeks)

    # eyes (reference: two big touching discs)
    er = {'normal': 15, 'wide': 18, 'small': 12, 'huge': 22}[eyes]
    pr = {'normal': 5.4, 'wide': 3.4, 'small': 4.6, 'huge': 3.0}[eyes] * pupil_scale
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
        elif mouth == 'smirk':
            ctx.move_to(-8, my + 1)
            ctx.curve_to(-2, my + 6, 8, my + 4, 12, my - 5)
            ctx.set_line_width(3.6)
            src(ctx, INK)
            ctx.stroke()
        elif mouth == 'shout':
            ctx.move_to(-13, my - 4)
            ctx.curve_to(-10, my + 18, 10, my + 18, 13, my - 4)
            ctx.close_path()
            fill_stroke(ctx, C('#4a1418'), 3.4)
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


# =========================================================================== rats
RAT = C('#8a8790')
RAT_HI = C('#b9b6bf')
RAT_SH = C('#55525c')
PINK = C('#f2a0a8')
PINK_SH = C('#c46b78')


def rat(ctx, x, y, s=1.0, tail=1.0, fat=0.0, look=(0.4, 0), step=None, blink=0.0, mouth='smile',
        dead=False, chew=0.0, flip=False, bandage=None, eyes=None, pose='walk', tail_wave=0.0, rot=0.0,
        col=None, shadow=True, cheeks=0.0, baby=False, glint=0.0, brows=None):
    """Side-view cartoon rat facing right, origin at the feet. ~150 units long at s=1.
    tail 0..1 (0 = stub; bandage=True draws a red plaster on the stub), fat 0..1 swells the body,
    chew 0..1 puffs the cheeks, pose: walk / sit / sleep / flex."""
    if s <= 0.002:
        return
    body_col = col or RAT
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(-s if flip else s, s)
    ctx.rotate(rot)
    lw = 4.6
    k = 1 + 0.55 * fat
    if baby:
        k = 0.9
    bw, bh = 62 * k, 40 * k * (1.1 if pose == 'sit' else 1)
    cy = -bh - 6
    if shadow:
        contact_shadow(ctx, 0, 0, bw * 0.95, 9, 0.35)
    # ---- tail (behind the body): a tapered pink curve from the rump
    tx0, ty0 = -bw + 6, cy + 6
    if tail > 0.02 and not dead:
        L = 170 * tail
        wv = tail_wave
        pts = [(tx0, ty0), (tx0 - L * 0.35, ty0 + 30 + 10 * math.sin(wv)), (tx0 - L * 0.7, ty0 - 10 + 18 * math.sin(wv + 1.2)),
               (tx0 - L, ty0 - 40 + 22 * math.sin(wv + 2.0))]
        taper(ctx, pts, 11, 2.2, PINK, lw=3.4)
        for j in range(1, 6):  # segment rings
            from chars import bez
            px, py = bez(*pts, j / 6.5)
            stick(ctx, [(px - 1, py - 5 + j * 0.6), (px + 1, py + 5 - j * 0.6)], 1.4, PINK_SH)
    elif dead and tail > 0.02:
        L = 150 * tail
        stick(ctx, [(tx0, ty0 + 10), (tx0 - L * 0.5, ty0 + 24), (tx0 - L, ty0 + 14)], 6, PINK)
    # ---- legs
    sw = math.sin(step) * 10 if step is not None else 0
    if pose != 'sleep':
        for lx, ph in ((-bw * 0.55, 1), (bw * 0.45, -1)):
            stick(ctx, [(lx, cy + bh * 0.6), (lx + ph * sw, -2)], 4.2)
            ellipse(ctx, lx + ph * sw + 6, -2, 9, 4.5)
            fill_stroke(ctx, PINK, 2.6)

    # ---- body: a pear that narrows into the head (head at +x)
    def body():
        ctx.move_to(-bw, cy + 4)
        ctx.curve_to(-bw, cy - bh * 1.05, bw * 0.25, cy - bh * 1.15, bw * 0.55, cy - bh * 0.55)
        ctx.curve_to(bw * 0.85, cy - bh * 0.25, bw + 34, cy - 4, bw + 46, cy + 10)   # snout tip
        ctx.curve_to(bw + 36, cy + 24, bw * 0.6, cy + bh * 0.62, bw * 0.2, cy + bh * 0.85)
        ctx.curve_to(-bw * 0.4, cy + bh * 1.02, -bw * 1.02, cy + bh * 0.75, -bw, cy + 4)
        ctx.close_path()
    form_shade(ctx, body, body_col, _shade(body_col, 1.35) if not col else _shade(body_col, 1.3),
               _shade(body_col, 0.62), (-bw, cy - bh * 1.15, bw + 46, cy + bh))
    clipped(ctx, body, lambda: soft_ellipse(ctx, 0, cy + bh * 0.75, bw * 0.95, bh * 0.45, C('#e8e2e6'), 0.55))  # belly
    rim(ctx, body, (1, 1, 1), 3, 3, 4, 0.3)
    body()
    ctx.set_line_width(lw)
    src(ctx, INK)
    ctx.stroke()
    if bandage and tail <= 0.02:  # red plaster cross over the stub
        ctx.save()
        ctx.translate(-bw + 2, cy + 2)
        for a in (0.6, -0.6):
            ctx.save()
            ctx.rotate(a)
            ctx.rectangle(-16, -6, 32, 12)
            fill_stroke(ctx, C('#e0413a'), 3)
            ctx.restore()
        ctx.restore()
    elif tail <= 0.02 and not dead:
        ellipse(ctx, -bw + 2, cy + 4, 7, 6)
        fill_stroke(ctx, PINK, 3)
    # cheeks (chewing / hamster puff)
    puff = max(chew, cheeks)
    if puff > 0:
        ellipse(ctx, bw * 0.62, cy + 8, 20 + 10 * puff, 14 + 8 * puff)
        fill_stroke(ctx, _shade(body_col, 1.15), 3.4)
    # ear (one big round pink ear on the far side + near side)
    ex, ey = bw * 0.28, cy - bh * 0.78
    for dx, dk in ((14, 0.8), (0, 1.0)):
        ellipse(ctx, ex + dx, ey - 6, 22 * dk, 24 * dk)
        fill_stroke(ctx, body_col, lw * 0.9)
        ellipse(ctx, ex + dx + 1, ey - 4, 13 * dk, 15 * dk)
        src(ctx, PINK)
        ctx.fill()
    # nose + whiskers
    ellipse(ctx, bw + 46, cy + 9, 7.5, 6.5)
    fill_stroke(ctx, C('#e26a7e'), 3)
    for a in (-0.25, 0.0, 0.25):
        stick(ctx, [(bw + 36, cy + 14), (bw + 66, cy + 14 + 40 * a)], 1.4, INK)
    # eyes: two touching white discs near the snout
    if dead:
        for sx in (bw * 0.5, bw * 0.5 + 22):
            stick(ctx, [(sx - 7, cy - 18), (sx + 7, cy - 4)], 3.6)
            stick(ctx, [(sx + 7, cy - 18), (sx - 7, cy - 4)], 3.6)
        stick(ctx, [(bw + 14, cy + 22), (bw + 22, cy + 18)], 2.8)
        ellipse(ctx, bw + 22, cy + 26, 4, 6)
        fill_stroke(ctx, C('#f2a0a8'), 2)
    else:
        er = 13 if eyes is None else {'small': 10, 'wide': 15, 'huge': 18}[eyes]
        pr = er * (0.42 if eyes != 'huge' else 0.22)
        for sx in (bw * 0.46, bw * 0.46 + er * 1.7):
            eye(ctx, sx, cy - 12, er, look, pupil=pr, blink=blink, lw=3.2)
        if glint:
            soft_ellipse(ctx, bw * 0.46 + er * 0.85, cy - 12, er * 3, er * 1.6, C('#fff5c0'), 0.5 * glint)
        if brows:
            for sx, sd in ((bw * 0.46, -1), (bw * 0.46 + er * 1.7, 1)):
                if brows == 'worried':
                    stick(ctx, [(sx - 8, cy - 26 - er + (6 if sd < 0 else 0)), (sx + 8, cy - 26 - er + (0 if sd < 0 else 6))], 3)
                else:
                    stick(ctx, [(sx - 8, cy - 22 - er - 3), (sx + 8, cy - 22 - er - 3)], 3)
        my = cy + 22
        if puff <= 0:
            if mouth == 'smile':
                ctx.new_path()
                ctx.arc(bw + 26, my - 8, 8, 0.2 * PI, 0.85 * PI)
                ctx.set_line_width(3)
                src(ctx, INK)
                ctx.stroke()
            elif mouth == 'o':
                ellipse(ctx, bw + 24, my, 5, 6)
                fill_stroke(ctx, C('#5a1f1f'), 2.6)
            elif mouth == 'grin':  # buck teeth grin
                ctx.move_to(bw + 10, my - 6)
                ctx.curve_to(bw + 16, my + 8, bw + 34, my + 6, bw + 38, my - 6)
                ctx.close_path()
                fill_stroke(ctx, C('#4a1418'), 2.8)
        # buck teeth
        ctx.rectangle(bw + 32, cy + 16, 9, 11)
        fill_stroke(ctx, (1, 1, 1), 2.4)
    # front paws
    if pose in ('sit', 'flex'):
        if pose == 'flex':
            stick(ctx, [(bw * 0.3, cy + 24), (bw + 34, cy + 40), (bw + 40, cy + 4)], 5)
            ellipse(ctx, bw + 18, cy + 34, 14, 10, -0.2)  # bicep
            fill_stroke(ctx, body_col, 3.4)
            ellipse(ctx, bw + 40, cy + 2, 8, 8)
            fill_stroke(ctx, PINK, 2.6)
        else:
            stick(ctx, [(bw * 0.4, cy + 10), (bw * 0.75, cy + 22)], 4.2)
            ellipse(ctx, bw * 0.78, cy + 24, 6, 5)
            fill_stroke(ctx, PINK, 2.4)
    ctx.restore()


def rat_dangle(ctx, hx, hy, s=1.0, swing=0.0, **kw):
    """A rat hanging head-down by its tail from a hand at (hx, hy)."""
    L = 120 * s
    ex, ey = hx + L * math.sin(swing), hy + L * math.cos(swing)
    stick(ctx, [(hx, hy), ((hx + ex) / 2 + 8 * s, (hy + ey) / 2), (ex, ey)], 9 * s + 1.5, INK)
    stick(ctx, [(hx, hy), ((hx + ex) / 2 + 8 * s, (hy + ey) / 2), (ex, ey)], 9 * s - 1.5, PINK)
    ctx.save()
    ctx.translate(ex, ey)
    ctx.rotate(PI / 2 - swing)
    kw.setdefault('look', (0.6, 0.3))
    rat(ctx, 62 * s - 6 * s, 52 * s, s, tail=0.0, shadow=False, **kw)
    ctx.restore()


def rat_front(ctx, x, y, s=1.0, look=(0, 0), blink=0.0, mouth='smile', chew=0.0, eyes=None, col=None, hearts=0.0):
    """Front-facing rat bust (for cages and close-ups). Origin at the chin bottom."""
    if s <= 0.002:
        return
    body_col = col or RAT
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for sd in (-1, 1):
        ellipse(ctx, sd * 52, -112, 30, 32)
        fill_stroke(ctx, body_col, 4.4)
        ellipse(ctx, sd * 52, -110, 18, 20)
        src(ctx, PINK)
        ctx.fill()

    def head():
        ctx.move_to(-64, -60)
        ctx.curve_to(-70, -150, 70, -150, 64, -60)
        ctx.curve_to(60, -10, 22, 0, 0, 2)
        ctx.curve_to(-22, 0, -60, -10, -64, -60)
        ctx.close_path()
    form_shade(ctx, head, body_col, _shade(body_col, 1.35), _shade(body_col, 0.62), (-70, -140, 70, 2))
    head()
    ctx.set_line_width(4.6)
    src(ctx, INK)
    ctx.stroke()
    if chew > 0:
        for sd in (-1, 1):
            ellipse(ctx, sd * 40, -30, 24 + 8 * chew, 20 + 6 * chew)
            fill_stroke(ctx, _shade(body_col, 1.12), 3.4)
    er = 17 if eyes is None else {'small': 13, 'wide': 20, 'huge': 24}[eyes]
    for sx in (-er, er):
        eye(ctx, sx, -76, er, look, pupil=er * (0.4 if eyes != 'huge' else 0.2), blink=blink, lw=3.4)
    if hearts > 0:
        for sx in (-er, er):
            heart(ctx, sx, -76, er * 0.9 * hearts, C('#ff4f6d'))
    ellipse(ctx, 0, -34, 10, 8)
    fill_stroke(ctx, C('#e26a7e'), 3)
    for sd in (-1, 1):
        for a in (-0.2, 0.1):
            stick(ctx, [(sd * 16, -26), (sd * 62, -26 + 60 * a)], 1.5)
    if mouth == 'smile':
        ctx.new_path()
        ctx.arc(0, -26, 9, 0.2 * PI, 0.8 * PI)
        ctx.set_line_width(3)
        src(ctx, INK)
        ctx.stroke()
    ctx.rectangle(-7, -18, 14, 13)
    fill_stroke(ctx, (1, 1, 1), 2.6)
    stick(ctx, [(0, -18), (0, -6)], 1.6)
    ctx.restore()


def flea(ctx, x, y, s=1.0, hop=0.0, look=(0.3, 0)):
    ctx.save()
    ctx.translate(x, y - abs(math.sin(hop)) * 26 * s)
    ctx.scale(s, s)
    for k in (-1, 0, 1):
        stick(ctx, [(k * 6, 4), (k * 10 - 4, 14), (k * 12, 18)], 2.2)
    ellipse(ctx, 0, 0, 14, 11, 0.3)
    fill_stroke(ctx, C('#6b3b22'), 2.8)
    ellipse(ctx, 6, -4, 5.5, 5.5)
    fill_stroke(ctx, (1, 1, 1), 2)
    ellipse(ctx, 6 + look[0] * 2.5, -4 + look[1] * 2.5, 2, 2)
    src(ctx, INK)
    ctx.fill()
    ctx.restore()


def heart(ctx, x, y, r, col=C('#ff4f6d'), lw=3.0):
    if r <= 0:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(r / 20, r / 20)
    ctx.move_to(0, 16)
    ctx.curve_to(-26, -2, -18, -26, 0, -12)
    ctx.curve_to(18, -26, 26, -2, 0, 16)
    ctx.close_path()
    fill_stroke(ctx, col, lw * 20 / max(r, 1) * 0.5)
    ctx.restore()


def star(ctx, x, y, r, col=C('#ffd23f'), lw=3.4, rot=0.0):
    if r <= 0:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    for i in range(10):
        a = -PI / 2 + i * PI / 5
        rr = r if i % 2 == 0 else r * 0.45
        (ctx.move_to if i == 0 else ctx.line_to)(math.cos(a) * rr, math.sin(a) * rr)
    ctx.close_path()
    fill_stroke(ctx, col, lw)
    ctx.restore()


# =========================================================================== props
def tail_prop(ctx, x, y, s=1.0, rot=0.0, curl=0.0):
    """A loose rat tail (the currency)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    pts = [(-70, 0), (-20, -20 - 30 * curl), (30, 20 + 20 * curl), (80, -10 - 40 * curl)]
    taper(ctx, pts, 12, 2.4, PINK, lw=3.4)
    ellipse(ctx, -70, 0, 7, 7)
    fill_stroke(ctx, C('#d97f8c'), 2.6)
    ctx.restore()


def scissors(ctx, x, y, s=1.0, open_k=0.5, rot=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    a = 0.05 + 0.4 * open_k
    for sd in (-1, 1):
        ctx.save()
        ctx.rotate(sd * a)
        ctx.move_to(0, -4)
        ctx.line_to(110, -2 * sd)
        ctx.line_to(0, 6)
        ctx.close_path()
        fill_stroke(ctx, C('#cfd6de'), 3.6)
        stick(ctx, [(10, 0), (100, -1 * sd)], 1.4, (1, 1, 1, 0.8))
        ellipse(ctx, -34, 0, 22, 14)
        ctx.set_line_width(9)
        src(ctx, INK)
        ctx.stroke_preserve()
        ctx.set_line_width(5)
        src(ctx, C('#c0453c'))
        ctx.stroke()
        ctx.restore()
    ellipse(ctx, 0, 0, 5, 5)
    fill_stroke(ctx, C('#9aa0aa'), 2.4)
    ctx.restore()


def coin(ctx, x, y, r=30, glint=0.0, label='1', col=C('#e8b53a'), edge=1.0):
    if r <= 0.2 or edge <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(edge, 1)
    if glint > 0:
        soft_ellipse(ctx, 0, 0, r * 2.4, r * 2.4, C('#fff1a0'), 0.45 * glint)
    ellipse(ctx, 0, 0, r, r)
    form_shade(ctx, lambda: ellipse(ctx, 0, 0, r, r), col, _shade(col, 1.35), _shade(col, 0.6), (-r, -r, r, r))
    ellipse(ctx, 0, 0, r, r)
    ctx.set_line_width(max(2.5, r * 0.12))
    src(ctx, INK)
    ctx.stroke()
    ellipse(ctx, 0, 0, r * 0.74, r * 0.74)
    ctx.set_line_width(max(1.2, r * 0.06))
    src(ctx, _shade(col, 0.6))
    ctx.stroke()
    if label and edge > 0.4:
        ctx.select_font_face('Poppins', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(r * 0.9)
        e = ctx.text_extents(label)
        ctx.move_to(-e.x_advance / 2, r * 0.32)
        src(ctx, _shade(col, 0.45))
        ctx.show_text(label)
    if glint > 0:
        star(ctx, r * 0.5, -r * 0.55, r * 0.35 * glint, (1, 1, 1), 0)
    ctx.restore()


def sack(ctx, x, y, s=1.0, col=C('#d9c79a'), label=True, spill=0.0):
    """Rice sack, origin bottom-centre."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    contact_shadow(ctx, 0, 0, 80, 12, 0.35)

    def bag():
        ctx.move_to(-62, 0)
        ctx.curve_to(-80, -60, -70, -130, -40, -150)
        ctx.curve_to(-20, -170, 20, -170, 40, -150)
        ctx.curve_to(70, -130, 80, -60, 62, 0)
        ctx.curve_to(20, 8, -20, 8, -62, 0)
        ctx.close_path()
    form_shade(ctx, bag, col, _shade(col, 1.2), _shade(col, 0.62), (-80, -170, 80, 6))
    bag()
    ctx.set_line_width(5)
    src(ctx, INK)
    ctx.stroke()
    # tied neck
    ctx.move_to(-26, -160)
    ctx.curve_to(-30, -196, 30, -196, 26, -160)
    fill_stroke(ctx, col, 4)
    stick(ctx, [(-24, -162), (24, -162)], 5, C('#8a5a2e'))
    if label:  # stamped rice grain mark
        for k in range(3):
            ellipse(ctx, -16 + k * 16, -76, 5, 11, 0.4)
            fill_stroke(ctx, (1, 1, 1), 2.4)
        stick(ctx, [(-34, -50), (34, -50)], 3.4, C('#b0563a'))
        stick(ctx, [(-34, -104), (34, -104)], 3.4, C('#b0563a'))
    ctx.restore()


def rice_pile(ctx, x, y, w, h, seed=0):
    import random
    rnd = random.Random(seed)
    ctx.save()
    ctx.translate(x, y)
    ctx.move_to(-w / 2, 0)
    ctx.curve_to(-w * 0.3, -h * 0.9, w * 0.3, -h * 0.9, w / 2, 0)
    ctx.close_path()
    form_shade(ctx, lambda: (ctx.move_to(-w / 2, 0), ctx.curve_to(-w * 0.3, -h * 0.9, w * 0.3, -h * 0.9, w / 2, 0),
                             ctx.close_path()), C('#f2ecdc'), C('#ffffff'), C('#c9bfa6'), (-w / 2, -h * 0.7, w / 2, 0))
    ctx.move_to(-w / 2, 0)
    ctx.curve_to(-w * 0.3, -h * 0.9, w * 0.3, -h * 0.9, w / 2, 0)
    ctx.set_line_width(4)
    src(ctx, INK)
    ctx.stroke()
    for i in range(int(w * h / 900)):
        u = rnd.uniform(-0.45, 0.45)
        yy = -rnd.uniform(0, h * 0.62 * (1 - (2 * u) ** 2))
        ellipse(ctx, u * w, yy, 2.2, 4.4, rnd.uniform(0, 3))
        src(ctx, C('#cfc4a8'))
        ctx.fill()
    ctx.restore()


def bucket(ctx, x, y, s=1.0, rats=3, seed=0):
    """Wooden bucket full of (dead, X-eyed) rats; origin bottom-centre."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for k in range(rats):
        ctx.save()
        ctx.translate(-30 + k * 30, -96 - (k % 2) * 10)
        ctx.rotate(-0.5 + k * 0.45)
        rat(ctx, 0, 0, 0.42, dead=True, shadow=False, tail=0.8)
        ctx.restore()
    ctx.move_to(-62, -100)
    ctx.line_to(62, -100)
    ctx.line_to(50, 0)
    ctx.line_to(-50, 0)
    ctx.close_path()
    form_shade(ctx, lambda: (ctx.move_to(-62, -100), ctx.line_to(62, -100), ctx.line_to(50, 0), ctx.line_to(-50, 0),
                             ctx.close_path()), C('#9a6a3e'), C('#c48d58'), C('#5a3a1e'), (-62, -100, 62, 0))
    ctx.move_to(-62, -100)
    ctx.line_to(62, -100)
    ctx.line_to(50, 0)
    ctx.line_to(-50, 0)
    ctx.close_path()
    ctx.set_line_width(5)
    src(ctx, INK)
    ctx.stroke()
    for yy in (-80, -24):
        stick(ctx, [(-60 + (100 + yy) * 0.12, yy), (60 - (100 + yy) * 0.12, yy)], 5, C('#4a4a52'))
    ctx.restore()


def cage(ctx, x, y, w=150, h=110, rats=1, t=0.0, seed=0, chew=True, look=(0, 0)):
    """Small wire cage with front-facing rats chewing rice; origin bottom-left."""
    import random
    rnd = random.Random(seed)
    ctx.save()
    ctx.translate(x, y)
    ctx.rectangle(0, -h, w, h)
    src(ctx, C('#3a2a1c'))
    ctx.fill()
    rice_pile(ctx, w * 0.5, -6, w * 0.7, 30, seed)
    for k in range(rats):
        cx = w * (k + 1) / (rats + 1) + rnd.uniform(-6, 6)
        ph = rnd.uniform(0, 6)
        rat_front(ctx, cx, -8, 0.36 * min(w / 150, h / 110), look=look, chew=(0.5 + 0.5 * math.sin(t * 14 + ph)) if chew else 0,
                  blink=1.0 if (t * 0.7 + ph) % 3 < 0.08 else 0)
    for i in range(int(w / 16) + 1):
        stick(ctx, [(i * w / int(w / 16), -h), (i * w / int(w / 16), 0)], 2.6, C('#a9adb5'))
    for yy in (-h, -h / 2, 0):
        stick(ctx, [(0, yy), (w, yy)], 4, C('#7d828c'))
    ctx.rectangle(0, -h, w, h)
    ctx.set_line_width(4.4)
    src(ctx, INK)
    ctx.stroke()
    ctx.restore()


def cart(ctx, x, y, s=1.0, load=1.0, seed=0, t=0.0):
    """Two-wheeled wooden hand cart heaped with dead rats; origin at ground under the axle."""
    import random
    rnd = random.Random(seed)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    contact_shadow(ctx, 0, 0, 200, 16, 0.4)
    n = int(14 * load)
    for k in range(n):
        ctx.save()
        ctx.translate(rnd.uniform(-150, 150), -150 - rnd.uniform(0, 70 * load) * (1 - abs(k - n / 2) / (n / 2 + 1)))
        ctx.rotate(rnd.uniform(-1, 1))
        rat(ctx, 0, 0, 0.45, dead=True, shadow=False, tail=rnd.uniform(0.5, 1))
        ctx.restore()
    ctx.rectangle(-190, -150, 380, 80)
    form_shade(ctx, lambda: ctx.rectangle(-190, -150, 380, 80), C('#8a5a32'), C('#b07a48'), C('#4a2e16'),
               (-190, -150, 190, -70))
    ctx.rectangle(-190, -150, 380, 80)
    ctx.set_line_width(5)
    src(ctx, INK)
    ctx.stroke()
    for k in range(1, 4):
        stick(ctx, [(-190, -150 + k * 20), (190, -150 + k * 20)], 2, C('#4a2e16'))
    stick(ctx, [(-190, -110), (-330, -80)], 8, C('#6a4424'))
    stick(ctx, [(-190, -110), (-330, -80)], 2, INK)
    ellipse(ctx, 0, -50, 50, 50)
    fill_stroke(ctx, C('#6a4424'), 6)
    for a in range(6):
        aa = a * PI / 3 + t * 3
        stick(ctx, [(0, -50), (math.cos(aa) * 46, -50 + math.sin(aa) * 46)], 4, INK)
    ellipse(ctx, 0, -50, 9, 9)
    fill_stroke(ctx, C('#b8bcc6'), 3)
    ctx.restore()


def shoulder_pole(sacks=True, s=0.38):
    """Use as person(hand=...)? No: as hold= callback. Draws a carrying pole across the shoulders
    with a rice sack hanging from each end (torso coordinates, bh = body height)."""
    def draw(c, bh):
        stick(c, [(-150, -bh - 2), (150, -bh - 10)], 8, C('#8a6a3a'))
        stick(c, [(-150, -bh - 2), (150, -bh - 10)], 2.4, INK)
        if sacks:
            for sx, sy in ((-140, -bh), (140, -bh - 8)):
                stick(c, [(sx, sy), (sx, sy + 40)], 2.2)
                sack(c, sx, sy + 40 + 196 * s * 0.9, s, label=False)
    return draw


def shed(ctx, x, y, s=1.0, door=0.0, light=0.0, night=False, sign=None, sign_k=1.0, t=0.0):
    """Little wooden shed on stilts-free ground, origin bottom-centre. door 0..1 opens, light spills."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    contact_shadow(ctx, 0, 4, 260, 24, 0.45)
    wood = C('#8a5f3a') if not night else C('#4a3a40')

    def walls():
        ctx.rectangle(-200, -280, 400, 280)
    form_shade(ctx, walls, wood, _shade(wood, 1.3), _shade(wood, 0.55), (-200, -280, 200, 0))
    for k in range(1, 12):
        stick(ctx, [(-200 + k * 34, -280), (-200 + k * 34, 0)], 2.4, _shade(wood, 0.5))
    walls()
    ctx.set_line_width(5)
    src(ctx, INK)
    ctx.stroke()
    # thatched/plank roof
    ctx.move_to(-250, -270)
    ctx.line_to(0, -420)
    ctx.line_to(250, -270)
    ctx.close_path()
    roof = C('#b98d4a') if not night else C('#5a4c50')
    form_shade(ctx, lambda: (ctx.move_to(-250, -270), ctx.line_to(0, -420), ctx.line_to(250, -270), ctx.close_path()),
               roof, _shade(roof, 1.3), _shade(roof, 0.55), (-250, -420, 250, -270))
    for k in range(1, 7):
        stick(ctx, [(-250 + k * 36, -270), (0, -420)], 1.8, _shade(roof, 0.6))
    ctx.move_to(-250, -270)
    ctx.line_to(0, -420)
    ctx.line_to(250, -270)
    ctx.close_path()
    ctx.set_line_width(5)
    src(ctx, INK)
    ctx.stroke()
    # door opening (light inside) + door leaf swinging outward to the left
    ctx.rectangle(-60, -200, 120, 200)
    if light > 0:
        src(ctx, C('#ffd98a'))
    else:
        src(ctx, C('#1a120c'))
    ctx.fill()
    if light > 0:
        soft_ellipse(ctx, 0, -100, 150, 200, C('#ffd98a'), 0.5 * light)
        soft_ellipse(ctx, 0, 30, 260, 50, C('#ffd98a'), 0.5 * light)
    w = 120 * math.cos(door * PI * 0.48)
    ctx.move_to(-60, -200)
    ctx.line_to(-60 - (120 - w) * 0.25, -206)
    ctx.line_to(-60 + w - (120 - w) * 0.25 * 0, -200 + 0)
    ctx.line_to(-60 + w, 0)
    ctx.line_to(-60 - (120 - w) * 0.25, 6)
    ctx.line_to(-60, 0)
    ctx.close_path()
    if door < 0.99:
        ctx.new_path()
        ctx.move_to(-60, -200)
        ctx.line_to(-60 + w, -200 - 10 * door)
        ctx.line_to(-60 + w, 10 * door)
        ctx.line_to(-60, 0)
        ctx.close_path()
        form_shade(ctx, lambda: (ctx.move_to(-60, -200), ctx.line_to(-60 + w, -200 - 10 * door),
                                 ctx.line_to(-60 + w, 10 * door), ctx.line_to(-60, 0), ctx.close_path()),
                   _shade(wood, 0.9), _shade(wood, 1.2), _shade(wood, 0.5), (-60, -200, 60, 0))
        ctx.move_to(-60, -200)
        ctx.line_to(-60 + w, -200 - 10 * door)
        ctx.line_to(-60 + w, 10 * door)
        ctx.line_to(-60, 0)
        ctx.close_path()
        ctx.set_line_width(4.4)
        src(ctx, INK)
        ctx.stroke()
    ctx.rectangle(-60, -200, 120, 200)
    ctx.set_line_width(4.4)
    src(ctx, INK)
    ctx.stroke()
    if sign and sign_k > 0:  # the mocking painted board
        ctx.save()
        ctx.translate(0, -320)
        ctx.rotate(0.05 * math.sin(t * 3))
        ctx.scale(sign_k, sign_k)
        stick(ctx, [(-80, -50), (-60, -96)], 2.4)
        stick(ctx, [(80, -50), (60, -96)], 2.4)
        ctx.rectangle(-150, -50, 300, 84)
        fill_stroke(ctx, C('#e9dcc0'), 4.4)
        ctx.select_font_face('Poppins', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(36)
        e = ctx.text_extents(sign)
        ctx.move_to(-e.x_advance / 2, -6)
        src(ctx, C('#7a2e2e'))
        ctx.show_text(sign)
        for k in range(5):
            star(ctx, -64 + k * 32, 18, 11, C('#e8b53a'), 2.2)
        ctx.restore()
    ctx.restore()


def manhole(ctx, x, y, s=1.0, lift=0.0, shine=0.0):
    """Iron manhole cover seen at a low angle; lift raises it off the ring."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ellipse(ctx, 0, 0, 120, 36)
    fill_stroke(ctx, C('#141414'), 5)
    ctx.save()
    ctx.translate(-lift * 60, -lift * 110)
    ctx.rotate(-lift * 0.5)
    ellipse(ctx, 0, 0, 112, 32)
    form_shade(ctx, lambda: ellipse(ctx, 0, 0, 112, 32), C('#5a5f68'), C('#8e949e'), C('#2c3036'), (-112, -32, 112, 32))
    ellipse(ctx, 0, 0, 112, 32)
    ctx.set_line_width(5)
    src(ctx, INK)
    ctx.stroke()
    for k in range(-3, 4):
        stick(ctx, [(k * 26 - 16, -20 + abs(k) * 2), (k * 26 + 16, 20 - abs(k) * 2)], 2, C('#2c3036'))
    if shine > 0:
        star(ctx, 60, -16, 18 * shine, (1, 1, 1), 0)
    ctx.restore()
    ctx.restore()
