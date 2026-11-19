"""Sound design: spotting (cue sheet) + mix. Principle numbers in [].

    python3 sound/design.py --voice VOICE.wav [--words words.json] [--out out/mix.wav]
    python3 sound/design.py --no-voice     # music+SFX+ambience only (preview before the VO)

Every cue is anchored to a script word index or an animation event inside a shot,
so the whole design re-times itself to whatever voiceover is aligned into words.json.
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)

import sfxlib as fx  # noqa: E402
from sfxlib import SR, lp, hp, bp, comb, at, norm  # noqa: E402
import score as sc  # noqa: E402
from score import N  # noqa: E402


def db(x):
    return 10 ** (x / 20)


# ------------------------------------------------------------------ timeline helpers
class TL:
    def __init__(self, words, total, shot_bounds):
        self.words, self.total, self.sb = words, total, shot_bounds

    def w(self, i):
        return self.words[i]['t0']

    def we(self, i):
        w = self.words[i]
        if 't1' in w:
            return w['t1']
        return self.words[i + 1]['t0'] - 0.08 if i + 1 < len(self.words) else w['t0'] + 0.4

    def gap_after(self, i):
        return (self.we(i), self.w(i + 1) if i + 1 < len(self.words) else self.total)

    def s(self, k):
        return self.sb[k][0]

    def d(self, k):
        return self.sb[k][1] - self.sb[k][0]


class Stem:
    def __init__(self, n):
        self.x = np.zeros(n)

    def add(self, sig, t, gain_db=0.0):
        i = int(SR * t)
        if i < 0:
            sig, i = sig[-i:], 0
        e = min(len(self.x), i + len(sig))
        if e > i:
            self.x[i:e] += sig[: e - i] * db(gain_db)


# ------------------------------------------------------------------ spotting
def spot(tl, n, hero_log):
    """Returns stems: sfx (ducked lightly), hero (unducked gap hits), amb, music buses."""
    sfx, hero, amb = Stem(n), Stem(n), Stem(n)
    bpm = 104
    beat = 60 / bpm
    seq = sc.Seq(tl.total + 1, seed=104)
    S, D, W = tl.s, tl.d, tl.w

    def H(name, sig, t, g=0.0):
        hero.add(sig, t, g)
        hero_log.append((round(t, 2), name))

    # ---- AMBIENCE: never true silence; dawn vs day beds; burrow + sky spaces [801-860]
    dawn = fx.desert_bed(tl.total + 1, seed=1, time='dawn', insects=0.6)
    day = fx.desert_bed(tl.total + 1, seed=2, time='day', insects=1.0, wind=1.1)
    m = np.zeros(n)
    for k in range(len(tl.sb)):
        a, b = int(SR * tl.sb[k][0]), int(SR * tl.sb[k][1])
        m[a:b] = 0.0 if k in (0, 1, 2, 3, 15, 16, 17) else 1.0
    m = np.convolve(m, np.ones(int(SR * 0.4)) / int(SR * 0.4), 'same')  # 0.4 s crossfades
    amb.x[:] = dawn[:n] * (1 - m) + day[:n] * m

    # =============== SHOT 0-1: dawn vista + drongo idle =======================
    # HOOK on frame one: drongo motif, low clarinet under the first line [608, 664, 668]
    sc.drongo_motif(seq, 0.02, beat, octave=4, instr='clarinet', vel=0.55, last=True, bus='lead_low')
    # F Lydian dawn shimmer, airy above the voice [644, 693]
    for k, nm in enumerate(('F5', 'A5', 'C6', 'E6', 'B5')):
        seq.note(0.05 + k * 0.35, 'shimmer', N(nm) + 12, S(2) - 0.4 - k * 0.35, 0.18, 'pad')
    seq.note(0.0, 'bass', N('F2'), 0.5, 0.55, 'bass')
    # distant birds already in bed; a soft drongo chirp as the camera finds him
    sfx.add(fx.lp(fx.drongo_call(2), 5000), S(0) + D(0) * 0.78, -14)          # far → low-passed [548]
    sfx.add(fx.drongo_call(1), S(1) + 0.15, -9)                               # close: smug little call

    # =============== SHOT 2: "It just screams" =================================
    # music hits then silence: everything stops for the scream [705, 600]
    H('drongo scream', fx.drongo_scream(3, 5), S(2) + 0.0, -2)
    sfx.add(fx.whoosh(0.18, 'up', 0.8, seed=21), S(2) - 0.14, -8)              # punch-in zoom [483]

    # =============== SHOT 3: animals drop their lunch =========================
    t3 = S(3)
    H('meerkat yelps', fx.mix(fx.yelp(1, 0), fx.at(fx.yelp(2, 3), 0.05)), t3 + 0.15, -5)
    sfx.add(fx.startle_sting(), t3 + 0.16, -12)                                # '!' graphics, secondary [706]
    sfx.add(fx.falling_whistle(0.62, 2200, 500), t3 + 0.27, -11)               # grub falls [511, 512]
    sfx.add(fx.thump(90, 0.4, 3), t3 + 0.95, -9)                               # lands (soft sand) [525]
    sfx.add(fx.dust_puff(3), t3 + 0.97, -15)
    sfx.add(fx.thump(140, 0.3, 4), t3 + 0.8, -12)                              # beetle lands
    sfx.add(fx.beetle_skitter(min(1.4, D(3) - 0.85), 5), t3 + 0.85, -8)       # and escapes
    # sly drongo fragment in the gap after "lunch!" — last note withheld [662]
    g0, g1 = tl.gap_after(20)
    sc.drongo_motif(seq, g0 + 0.05, beat * 0.7, octave=5, instr='whistle', vel=0.55, last=False, bus='lead')

    # =============== SHOT 4: "Meet the meerkats." =============================
    t4, d4 = S(4), D(4)
    order = [1, 2, 0, 3]
    for k in range(4):  # pops step up a whole tone each [470], with sand spill [527]
        tp = t4 + (0.05 + k * 0.17) * d4
        sfx.add(fx.pop(True, 1.0, 349.23, seed=40 + k, semis=2 * k), tp + 0.02, -6)
        sfx.add(fx.sand_spill(0.4, 41 + k), tp + 0.04, -16)
        sfx.add(fx.meerkat_chirp(42 + k, k * 2), tp + 0.2, -14)
    sc.gliss(seq, t4 + 0.02, up=True, steps=8, span=0.3)                        # popping up [707]
    sc.groove(seq, t4 + 0.6, S(9), bpm, [N('F2'), N('F2'), N('A#1'), N('C2')], density=2)
    g0, g1 = tl.gap_after(23)
    sc.meerkat_motif(seq, g0 + 0.02, beat * 0.8, 'C6', 0.6)                    # first statement, near solo [654]

    # =============== SHOTS 5-8: digging, beetles, scorpions, lizard ============
    sfx.add(fx.digging(D(5) + 0.2, 6, 50), S(5), -11)                          # 4-8 strokes/s [521]
    sfx.add(fx.digging(D(5) + 0.2, 5, 51), S(5) + 0.07, -15)
    sfx.add(fx.whoosh(0.5, 'pass', 1.2, seed=52), S(5) - 0.35, -14)            # time-lapse pan
    sfx.add(fx.beetle_skitter(0.7, 53), S(6) + 0.1, -9)
    sfx.add(fx.sand_spill(0.6, 54), S(6) + 0.02, -15)
    sfx.add(fx.whip_land(55), S(7) - 0.14, -9)                                 # snap punch-in [476]
    sfx.add(fx.scorpion_threat(min(0.65, D(7)), 56), S(7) + 0.02, -10)
    sfx.add(fx.lizard_patter(0.35, 57), S(8) + 0.05, -12)
    sfx.add(fx.heartbeat(70, 2), S(8) + 0.5, -18)                             # nervous lizard
    sfx.add(fx.whoosh(0.35, 'down', 0.9, seed=58), S(8) + 1.55 - 0.25, -10)    # meerkat looms in
    H('lizard gulp', fx.gulp(), S(8) + 2.05, -8)

    # =============== SHOT 9: head in a hole → tilt to the sky ==================
    t9, d9 = S(9), D(9)
    sfx.add(fx.digging(1.7, 6, 60, depth=0.85), t9, -10)                       # muffled, comb-coloured [522]
    sc.groove(seq, t9, t9 + 1.6, bpm, [N('F2')], density=1)                    # thin out [679]
    sfx.add(fx.whoosh(min(1.5, d9 - 1.6), 'up', 1.4, seed=61), t9 + 1.6, -9)   # the long tilt up [483]
    sfx.add(fx.hawk_cry(62, distance=0.9), t9 + d9 - 0.55, -13)                 # far above [548]

    # =============== SHOT 10: "the sky is full of hawks" =======================
    t10, d10 = S(10), D(10)
    sc.hawk_motif(seq, t10 + 0.02, beat)                                        # low brass + tom [651, 623]
    seq.note(t10, 'pad', N('E3'), d10, 0.25, 'pad')
    for k, (dt, dist) in enumerate(((0.15, 0.2), (0.75, 0.7), (1.25, 0.0))):  # every cry different [549]
        sfx.add(fx.hawk_cry(70 + k, distance=dist), t10 + dt, -9 - 4 * dist)
    sfx.add(fx.flyby(1.4, 73), t10 + 0.3, -11)
    sfx.add(fx.flaps(2, 3, 1.4, 74), t10 + 0.9, -14)                            # slow hawk wingbeats [568]

    # =============== SHOT 11: sentinel stands guard ===========================
    t11, d11 = S(11), D(11)
    sc.sentinel_motif(seq, t11 + 0.02, beat, vel=0.7)                           # lookout figure [652]
    for k in range(int(d11 / (beat / 2))):                                      # E Phrygian ostinato [733]
        seq.note(t11 + 0.6 + k * beat / 2, 'pizz', N('E3') if k % 2 == 0 else N('F3'), 0.12, 0.35, 'harm')
    sfx.add(fx.desert_bed(d11, 80, wind=1.4, insects=0, birds=0), t11, -12)     # wind lifts on the mound

    # =============== SHOT 12: spots trouble ===================================
    t12 = S(12)
    sfx.add(fx.whoosh(0.3, 'up', 0.8, seed=81), t12 + 0.85 - 0.22, -7)         # crash zoom [483]
    H('gasp', fx.gasp(82), t12 + 0.86, -7)
    sfx.add(fx.heartbeat(110, 2), t12 + 1.0, -14)

    # =============== SHOT 13: barks a warning (hero) ==========================
    t13 = S(13)
    H('alarm bark volley', fx.bark_volley(4, 6.5, 90), t13 + 0.02, -1)         # urgent 5-8/s [542]
    sc.alarm_figure(seq, t13 + 0.05, beat, reps=6, vel=0.45)                    # the alarm figure [653]

    # =============== SHOT 14: everyone dives underground ======================
    t14, d14 = S(14), D(14)
    sc.gliss(seq, t14 + 0.05, up=False, steps=8, span=0.35, start='C5', vel=0.6)  # diving down [707]
    for i in range(4):
        t0 = t14 + 0.1 + i * 0.16
        sfx.add(fx.whoosh(0.2, 'down', 0.8, seed=100 + i), t0, -10)            # down-swish [528]
        thud = comb(lp(fx.thump(70, 0.6, 110 + i), 800), 4.0, 0.5) * 1.6       # muffled underground
        sfx.add(thud, t0 + 0.24, -6)
        sfx.add(fx.dust_puff(120 + i), t0 + 0.28, -17)
    sfx.add(fx.flyby(min(1.6, d14 - 1.1), 130), t14 + 1.1, -9)                 # shadow sweeps the empty ground

    # =============== SHOT 15: "Then one morning, a new guy shows up." =========
    t15, d15 = S(15), D(15)
    land = t15 + 0.55 * d15
    sfx.add(fx.flaps(max(2, int((land - t15) * 8)), 8, 0.45, 140), t15, -9)   # drongo flaps in [568]
    sfx.add(fx.flaps(3, 9, 0.45, 141, decel=True), land - 0.05, -8)             # landing flutter [570]
    sfx.add(fx.bp(fx.click(fx.rng(142), 3, 2000), 2000, 5000), land + 0.03, -12)  # talon tick [574]
    sfx.add(fx.meerkat_chirp(143, 5), t15 + 0.66 * d15, -12)
    sfx.add(fx.meerkat_chirp(144, 8), t15 + 0.70 * d15, -13)
    # music returns CHANGED: F Mixolydian, swung, pizz bass, drongo colour [720, 632, 641]
    sc.groove(seq, t15 + 0.1, tl.total, bpm, [N('F2'), N('D#2'), N('F2'), N('C2')], density=2, swing=0.58)

    # =============== SHOT 16: "...called a drongo." name card ==================
    t16, d16 = S(16), D(16)
    sfx.add(fx.whoosh(0.9, 'down', 1.0, seed=150), t16 + 0.05, -15)            # tilt down to the tail
    H('name card', fx.name_card(151), t16 + 0.62 * d16, -6)                    # graphics stinger [579, 580]
    g0, g1 = tl.gap_after(len(tl.words) - 4)  # gap after "drongo."
    sfx.add(fx.drongo_call(152), g0 + 0.05, -8)

    # =============== SHOT 17: "He doesn't dig." + button ======================
    t17 = S(17)
    sfx.add(fx.digging(1.6, 6, 160), t17, -14)
    sfx.add(fx.drongo_call(161), t17 + 0.15, -14)
    tb = max(tl.we(len(tl.words) - 1) + 0.35, tl.total - 1.2)                   # >=300 ms after last word [759]
    # button: drongo motif's last two notes + tonic hit [754, 755]
    seq.note(tb, 'whistle', N('D#5'), 0.06, 0.7, 'button')
    seq.note(tb + 0.08, 'whistle', N('E5'), 0.22, 0.75, 'button')
    for nm in ('F3', 'C4', 'A4', 'F5'):
        seq.note(tb + beat, 'marimba', N(nm), 0.3, 0.8, 'button')
        seq.note(tb + beat, 'pizz', N(nm) - 12, 0.3, 0.6, 'button')
    seq.note(tb + beat, 'bass', N('F2'), 0.25, 0.9, 'button')
    seq.note(tb + beat, 'woodblock', 1050, 0.05, 0.7, 'button')
    music_stop = tb + beat - 0.05  # the bed stops for the button [713]
    return sfx, hero, amb, seq, music_stop


# ------------------------------------------------------------------ dynamics
def follower(x, attack, release):
    from scipy.signal import lfilter
    a_a, a_r = np.exp(-1 / (SR * attack)), np.exp(-1 / (SR * release))
    y = np.zeros_like(x)
    prev = 0.0
    # vectorised-ish: process in blocks of 32 samples
    blk = 32
    for i in range(0, len(x), blk):
        v = x[i:i + blk].max()
        c = a_a ** blk if v > prev else a_r ** blk
        prev = c * prev + (1 - c) * v
        y[i:i + blk] = prev
    return y


def speech_mask(voice, words_tl, n, lookahead=0.15):
    """1 where narration is active; pre-ducked 150 ms, held through gaps < 400 ms [771, 774]."""
    if voice is not None:
        env = np.abs(voice[:n]) if len(voice) >= n else np.pad(np.abs(voice), (0, n - len(voice)))
        env = np.convolve(env, np.ones(480) / 480, 'same')
        thr = np.percentile(env[env > 1e-5], 35) if (env > 1e-5).any() else 1
        m = (env > thr * 0.6).astype(float)
    else:
        m = np.zeros(n)
        for i, w in enumerate(words_tl.words):
            a = int(SR * w['t0'])
            b = int(SR * words_tl.we(i))
            m[a:b] = 1
    # hold through short gaps
    hold = int(SR * 0.4)
    idx = np.flatnonzero(np.diff(np.r_[0, m, 0]))
    starts, ends = idx[::2], idx[1::2]
    for e, s2 in zip(ends[:-1], starts[1:]):
        if s2 - e < hold:
            m[e:s2] = 1
    la = int(SR * lookahead)
    m = np.maximum(m, np.r_[m[la:], np.zeros(la)])
    return follower(m, 0.08, 0.45)  # attack 80 ms, release 450 ms [769]


def limiter(x, ceiling_db=-1.5, look=0.003, release=0.08):
    """Look-ahead peak limiter on a 4x-oversampled estimate (true-peak-ish)."""
    from scipy.signal import resample_poly
    c = db(ceiling_db)
    up = np.abs(resample_poly(x, 4, 1, axis=0)).max(axis=1) if x.ndim == 2 else np.abs(resample_poly(x, 4, 1))
    pk = up.reshape(-1, 4).max(axis=1)[: len(x)]
    need = np.minimum(1, c / np.maximum(pk, 1e-9))
    la = int(SR * look)
    # smooth: instant down (with lookahead window min), slow up
    from scipy.ndimage import minimum_filter1d
    g = minimum_filter1d(need, size=2 * la + 1, origin=0)
    g = np.r_[g[la:], np.ones(la)]
    out = np.empty_like(g)
    a = np.exp(-1 / (SR * release))
    prev = 1.0
    for i in range(0, len(g), 16):
        v = g[i:i + 16].min()
        prev = v if v < prev else a ** 16 * prev + (1 - a ** 16) * v
        out[i:i + 16] = prev
    return x * (out[:, None] if x.ndim == 2 else out)


def lufs(x):
    import pyloudnorm as pyln
    return pyln.Meter(SR).integrated_loudness(x)


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--voice', default=None)
    ap.add_argument('--no-voice', action='store_true')
    ap.add_argument('--words', default=os.path.join(ROOT, 'words.json'))
    ap.add_argument('--out', default=os.path.join(ROOT, 'out', 'mix.wav'))
    ap.add_argument('--stems', default=os.path.join(ROOT, 'out', 'stems'))
    a = ap.parse_args()

    import render
    meta = json.load(open(a.words))
    words, total = meta['words'], meta['duration']
    tl = TL(words, total, render.shot_bounds(words, total))
    n = int(SR * total)

    voice = None
    if a.voice and not a.no_voice:
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', a.voice, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                             capture_output=True, check=True).stdout
        voice = np.frombuffer(raw, np.float32).astype(float)
        voice = hp(voice, 70)                       # rumble out, leave the read alone
        voice = np.pad(voice, (0, max(0, n - len(voice))))[:n]

    hero_log = []
    sfx, hero, amb, seq, music_stop = spot(tl, n, hero_log)

    # ---- music bus: per-bus balance, speech-safe variant, ducking [669-696, 767-774]
    def bus(name, g):
        return seq.get(name)[:n] * db(g)

    full = (bus('lead', -6) + bus('lead_low', -9) + bus('pad', -14) + bus('bass', -9) + bus('harm', -13)
            + bus('perc', -12) + bus('hawk', -6) + bus('marimba', -10))
    full[int(SR * music_stop):] *= 0
    button = bus('button', -15)
    full = hp(full, 38)                                                    # nothing below 40 Hz [690]
    safe = lp(full, 2000)                                                  # leave 1-4 kHz to consonants [685]
    m = speech_mask(voice, tl, n)  # without a VO: shaped around the scripted word timings
    music = (full * (1 - m) + safe * m) * db(-10 * m)                      # 10 dB duck under speech [768]
    music += button                                                        # button exempt from duck [773]
    sfx_x = sfx.x * db(-4 * m)                                             # incidental SFX yield to VO
    amb_x = hp(amb.x, 60) * db(-23) * db(-6 * m)                            # floor, felt in pauses [802]
    hero_x = hero.x                                                        # gap hits stay full size

    stems = {'music': music, 'sfx': sfx_x + hero_x, 'amb': amb_x}
    if voice is not None:
        stems['vo'] = norm(voice, 0.7)
    mixm = sum(stems.values())
    # tiny stereo width only on ambience (mono-safe core) [477]
    side = np.convolve(amb_x, np.r_[np.zeros(int(SR * 0.011)), 1], 'same') * 0.25
    st = np.stack([mixm + side, mixm - side], axis=1)

    # loudness: -14 LUFS, true peak <= -1.5 dBTP (reference-matched)
    for _ in range(3):
        L = lufs(st)
        st = st * db(-14 - L)
        st = limiter(st, -2.0)  # headroom for AAC overshoot
    L = lufs(st)

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    sf.write(a.out, st.astype(np.float32), SR, subtype='PCM_24')
    os.makedirs(a.stems, exist_ok=True)
    for k, v in stems.items():
        sf.write(os.path.join(a.stems, f'{k}.wav'), v.astype(np.float32), SR, subtype='PCM_24')
    json.dump({'hero_events': hero_log, 'lufs': round(L, 2)}, open(os.path.join(a.stems, 'cue_log.json'), 'w'), indent=1)
    print(f'mix -> {a.out}  {total:.2f}s  {L:.2f} LUFS  peak {20*np.log10(np.abs(st).max()):.2f} dBFS')


if __name__ == '__main__':
    main()
