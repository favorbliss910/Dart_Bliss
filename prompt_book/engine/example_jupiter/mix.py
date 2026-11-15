"""Jupiter cue sheet (worked example). Run from the engine folder:
   JV_PROJECT=example_jupiter python3 example_jupiter/mix.py <voiceover> <drama.mp3> <suspense.mp3> <inspiring.mp3> <out_dir>
Every SFX time comes from the narration (phrase lookups in scenes*.py), never from guessed seconds."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from sfxlib import *
import scenes1 as S1, scenes2 as S2, scenes3 as S3
VO, M_DRAMA, M_SUSP, M_INSP, OUT = sys.argv[1:6]
END = S3.END_T
N = int(END * SR) + SR

# ------------------------------------------------------------------ build SFX bus
sfx = np.zeros((N, 2), np.float32)
amb = np.zeros((N, 2), np.float32)
A = S1
# opening
place(sfx, boom(4, 55, 30, .45, .2), 0.0)
place(amb, drone(9, .10, (41.2, 61.7, 82.4)), 0.0)
place(sfx, whoosh(.9, 200, 3000, .25), S1.T_DROPPED - .3)
place(sfx, rumble(2.5, .25) * fade_env(int(2.5 * SR), 1.2, .8)[:, None], S1.T_SURV_ENTRY - 1.5)
place(sfx, ui_pop(.2), S1.T_SURV_ENTRY + .6)
place(amb, wind(5.0, .16, 2500), S1.T_WINDS - .3)
place(sfx, ui_pop(.15), S1.T_WINDS + .5); place(sfx, ui_pop(.15), S1.T_WINDS + 1.6)
place(amb, wind(4.0, .12, 1500), S1.T_KEPT)
place(sfx, alarm(.8, .1), S1.T_NOGROUND)
for i in range(8):
    place(sfx, blip(1000, .08, .12), S1.T_THEN58 + .4 + i * .45)
place(sfx, tone(1000, 1.8, .12, .005, 1.2), S1.T_ENDED + .25)
place(sfx, static(.35, .2), S1.T_ENDED + .1)
# scale pull-out
place(sfx, whoosh(2.5, 100, 1500, .2, .3), S1.T_SCRATCH + .2)
place(amb, drone(10, .08, (49, 73.4, 98)), S1.T_BUTHERE)
for tt in (S1.T_SOLID, S1.T_OCEAN, S1.T_CENTER):
    place(sfx, thud(.18), tt + .1)
place(sfx, whoosh(.5, 400, 5000, .3), S1.T_BUTFIRST - .2)
place(sfx, thud(.25), S1.T_EARTHFALL + .5)
place(sfx, boom(4, 60, 30, .35, .3), S1.T_NOWHERE)
place(sfx, whoosh(2.0, 150, 2000, .15, .6), S1.T_REDOVAL)
place(amb, wind(8, .07, 1800), S1.T_CLOUDS)
place(sfx, whoosh(.5, 400, 5000, .3), S1.T_ENORMOUS - .2)
for i in range(12):
    place(sfx, blip(900 + i * 60, .05, .06), S1.T_1300 - .3 + i * .14)
place(sfx, whoosh(3.0, 200, 3000, .3, .5), S1.T_JUNO - .2)
place(sfx, boom(3, 50, 28, .3, .2), S1.T_3000B)
place(sfx, riser(2.8, .25), S1.T_ABOUT)
place(sfx, boom(3, 70, 30, .5, .6), S1.T_OBSTACLE)
place(amb, rumble(15, .10, 30, 400, .3) * fade_env(int(15 * SR), 3, 1)[:, None], S1.T_OBSTACLE)
for i in range(10):
    place(sfx, blip(1500, .03, .05), S1.T_170 + i * .18)
# entry
entry_dur = S2.T_SHAKESTOP + .5 - S2.T_HIT
er = rumble(entry_dur, 1.0, 25, 900, .2)
t = tvec(entry_dur)
env = np.interp(t, [0, S2.T_DARKNESS - S2.T_HIT, S2.T_DECEL - S2.T_HIT, S2.T_DECEL - S2.T_HIT + 3, S2.T_HUMAN - S2.T_HIT, entry_dur - .5, entry_dur], [.15, .45, .7, .5, .12, .1, 0])
place(sfx, er * env[:, None] * .7, S2.T_HIT)
place(sfx, boom(2, 80, 40, .3, .7, 2500), S2.T_HIT)
place(sfx, riser(S2.T_DECEL - S2.T_DARKNESS, .3), S2.T_DARKNESS)
place(sfx, boom(5, 90, 25, 1.0, .9, 3000), S2.T_DECEL)
place(sfx, boom(3, 70, 30, .55, .5), S2.T_228B)
for tt in (S2.T_ORDINARY, S2.T_SUIT, S2.T_HOLD):
    place(sfx, thud(.2), tt + .4)
place(sfx, creak(1.0, .15, 120), S2.T_WORST + .6)
place(sfx, chute_snap(.35), S2.T_CHUTE - .2)
for i in range(6):
    place(sfx, blip(1400, .07, .05), S2.T_TRANSMIT + i * .5)
place(sfx, whoosh(1.2, 100, 1200, .2, .3), S2.T_FICT)
place(amb, wind(S2.T_ONEARTH - S2.T_FIRST, .10, 1400), S2.T_FIRST)
place(sfx, shimmer(2.0, .05), S2.T_HORIZON - .2)
place(sfx, alarm(.5, .06), S2.T_HORIZON)
for tt in (S2.T_1BAR, S2.T_M108, S2.T_HYD):
    place(sfx, ui_pop(.16), tt - .2)
place(sfx, alarm(1.6, .12), S2.T_FATAL + .2)
place(amb, wind(S2.T_GDISC - S2.T_STRANGE, .09, 1000), S2.T_STRANGE)
place(sfx, creak(1.6, .22, 80), S2.T_DOESNT + .2)
for i, tt in enumerate((S2.T_FIVE, S2.T_TEN, S2.T_FIFTEEN)):
    place(sfx, boom(1.6, 80, 40, .35 + .1 * i, .6), tt)
    place(sfx, creak(1.2, .18 + .05 * i, 70 - 8 * i), tt + .1)
place(sfx, ui_pop(.12), S2.T_WARMDAY)
place(amb, wind(S2.T_LESSWATER - S2.T_GDISC, .08, 1600), S2.T_GDISC)
place(sfx, ui_pop(.15), S2.T_SURPRISING)
place(sfx, whoosh(.5, 400, 5000, .3), S2.T_LIKE - .2)
place(amb, wind(S2.T_LOST - S2.T_KEPTF2, .12, 900), S2.T_KEPTF2)
for i in range(int((S2.T_LOST - S2.T_CONT) / .5)):
    place(sfx, blip(1000, .08, .08), S2.T_CONT + i * .5)
place(sfx, static(.6, .35), S2.T_LOST - .35)
place(sfx, tone(1000, 2.5, .09, .005, 2.0), S2.T_LOST + .2)
place(amb, drone(S2.T_CONTINUE - S2.T_LOST + 2, .09, (36.7, 55, 73.4)), S2.T_LOST + 1.0)
place(sfx, boom(4, 45, 25, .3, .1), S2.T_EXTRA)
# interior
place(sfx, thud(.25), S3.T_NOTREAL + .6)
place(sfx, shimmer(2.5, .07), S3.T_IMAGINARY)
place(amb, rumble(S3.T_STRANGER - S3.T_HCOMP, .08, 25, 200, .4) * fade_env(int((S3.T_STRANGER - S3.T_HCOMP) * SR), 2, 2)[:, None], S3.T_HCOMP)
for tt in (S3.T_SPLASH, S3.T_WAVE, S3.T_WLINE, S3.T_SUDDEN):
    place(sfx, thud(.18), tt + .15)
place(sfx, riser(S3.T_METAL - S3.T_STRANGER - .1, .22), S3.T_STRANGER)
place(sfx, boom(4, 60, 30, .45, .4), S3.T_METAL)
place(sfx, shimmer(4, .09), S3.T_METAL)
place(amb, crackle(S3.T_WHYMATTER - S3.T_METAL, .08, 6), S3.T_METAL)
place(sfx, whoosh(.5, 400, 5000, .3), S3.T_ROCKS - .2)
place(sfx, thud(.2), S3.T_ROCKS + .4); place(sfx, thud(.2), S3.T_MERCURY + .4)
place(amb, hum(S3.T_CENTER - S3.T_REMEMBER, .07, 55), S3.T_REMEMBER)
place(amb, crackle(S3.T_CENTER - S3.T_TRAP, .05, 4), S3.T_TRAP)
place(sfx, boom(3, 50, 28, .3, .2), S3.T_CENTER)
place(sfx, riser(S3.T_FUZZY - S3.T_EVIDENCE, .2), S3.T_EVIDENCE)
place(sfx, shimmer(3, .08), S3.T_FUZZY)
place(sfx, boom(3, 55, 30, .3, .3), S3.T_FUZZY)
place(sfx, boom(3, 80, 30, .35, .7), S3.T_COLLISION + 1.2)
place(sfx, thud(.25), S3.T_NOCAM + .4)
place(sfx, riser(S3.T_NO - S3.T_IFYOU, .18), S3.T_IFYOU)
place(sfx, boom(4.5, 70, 28, .7, .6), S3.T_NO)
for tt in (S3.T_TRAVEL, S3.T_DENSEF, S3.T_LIKEMETAL, S3.T_CENTRAL):
    place(sfx, ui_pop(.12), tt)
for tt in (S3.T_PHOTO, S3.T_MEASGRAV, S3.T_STUDYMAG, S3.T_PREDICT):
    place(sfx, ui_pop(.13), tt)
place(sfx, shimmer(4, .06), S3.T_NIGHT - .5)
place(sfx, boom(5, 50, 28, .4, .2), S3.T_VO_END + 1.2)

# ------------------------------------------------------------------ music bus
mus = np.zeros((N, 2), np.float32)
drama = load(M_DRAMA); susp = load(M_SUSP); insp = load(M_INSP)
cue(mus, drama, 0.0, 0.0, S2.T_HIT + 1.0, .05, 3.0, -3)
cue(mus, susp, S2.T_FIRST - 1.0, 0.0, S2.T_LOST - S2.T_FIRST + 1.0, 4.0, .25, -6)
cue(mus, drama, S2.T_CONTINUE - .3, 28.0, S3.T_CENTER - S2.T_CONTINUE + 2.5, 3.0, 3.0, -4)
cue(mus, susp, S3.T_CENTER + .5, 40.0, S3.T_BACK - S3.T_CENTER + 1.0, 4.0, 2.5, -9)
ti = S3.T_BACK - 1.0
cue(mus, insp, ti, 14.0, END - ti, 3.0, 4.0, -2)


# ------------------------------------------------------------------ voice + mix + finish
vo = load(VO, VO_CHAIN)
voice = np.zeros((N, 2), np.float32); place(voice, vo, 0.0)
os.makedirs(OUT, exist_ok=True)
raw = mixdown(voice, mus, sfx, amb, os.path.join(OUT, 'mix_raw.wav'))
print('final (LUFS, true peak dBFS):', finish(raw, os.path.join(OUT, 'mix_final.wav')))
