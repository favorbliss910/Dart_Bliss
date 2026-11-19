"""Rat Tails: sound design + mix around the supplied voiceover.

Voice-first rules (drongo/sound/SPEC.md + PRINCIPLES_1000.md, as in library/sound.py):
  * the VO is already mastered (-14.2 LUFS, -2.7 dBFS): it is NOT processed, only resampled;
  * the VO sits around D#3 (median 154 Hz, A2-G3), so the score is in F# minor pentatonic
    (F# A B C# E) with drones below 93 Hz and melody above 370 Hz; nothing sustains in 100-200 Hz;
  * under speech, music is low-passed at 1.8 kHz and ducked 13 dB; SFX low-passed at 3.5 kHz, -8 dB;
  * hits, stingers and anything with transients go in the narration's gaps (hero stem, -10 dB under words);
  * the mix is normalised to -14 LUFS with true peak <= -2 dBTP.

    python3 sound.py  ->  out/rat_tails_mix.wav + out/stems/ + out/stems/report.json
"""
import importlib.util
import json
import os
import subprocess
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..')
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'drongo'))
sys.path.insert(0, os.path.join(ROOT, 'drongo', 'sound'))

import sfxlib as fx  # noqa: E402
from sfxlib import SR, PI, rng, env_exp, fade, bp, lp, hp, pink, at, norm, soft_clip, svf_bp, sweep, grains  # noqa: E402
import score as sc  # noqa: E402
from score import N  # noqa: E402
from design import TL, Stem, speech_mask, limiter, lufs, db  # noqa: E402
import scenes  # noqa: E402  (this episode's shots; must be imported before library/sound.py below)

# Reuse The Blank Library's recipes (page_flip, creak, low_boom, reverse_swell, celesta, drone, tick,
# whisper_texture, glitch, hum, room_tone, sparkle...). Its own `import scenes` resolves to this
# episode's module, which is already loaded, so nothing from the library episode is rendered.
_spec = importlib.util.spec_from_file_location('library_sound', os.path.join(ROOT, 'library', 'sound.py'))
LS = importlib.util.module_from_spec(_spec)
sys.path.insert(0, os.path.join(ROOT, 'library'))
_spec.loader.exec_module(LS)
sys.path.remove(os.path.join(ROOT, 'library'))


# ============================================================== new recipes
def zither(f, dur, vel, r):
    """Plucked 16-string zither (dan tranh flavour): Karplus-Strong string, then the player's
    left hand bends the note up and back after the attack (the signature ornament)."""
    n = int(SR * 1.8)
    period = max(2, int(SR / f))
    buf = r.uniform(-1, 1, period) * np.hanning(period) ** 0.3
    out = np.empty(n)
    for i in range(n):
        v = buf[i % period]
        out[i] = v
        buf[i % period] = 0.5 * (v + buf[(i + 1) % period]) * 0.996
    t = np.arange(n) / SR
    bend = 1 + 0.03 * np.clip((t - 0.12) / 0.15, 0, 1) * np.exp(-np.maximum(0, t - 0.27) / 0.25)
    idx = np.clip(np.cumsum(bend) - bend[0], 0, n - 1)  # read faster during the bend -> pitch rises
    out = np.interp(idx, np.arange(n), out)
    out += 0.15 * np.sin(2 * PI * f * 2 * t) * np.exp(-t / 0.08)
    return hp(out, 200) * env_exp(n, 0.001, 0.6) * vel * 0.8


def squeak(seed=0, semis=0, n=2):
    """Rat squeak: short bright FM chirps (kept for the gaps; very high, very short)."""
    r = rng(seed)
    parts = []
    t = 0.0
    for k in range(n):
        f0 = 2600 * 2 ** ((semis + r.uniform(-2, 2)) / 12)
        d = r.uniform(0.04, 0.07)
        parts.append(at(fx.fm_chirp(f0, f0 * r.uniform(1.15, 1.35), d, 2.0, 0.8, 0.02, seed * 10 + k), t))
        t += d + r.uniform(0.02, 0.05)
    return fade(norm(fx.mix(*parts)))


def snip(seed=0):
    """Scissors: two blades shearing (bright metallic tick + short scrape) then the closing clack."""
    r = rng(seed)
    scrape = bp(r.standard_normal(int(SR * 0.05)), 3000, 9000) * env_exp(int(SR * 0.05), 0.002, 0.015)
    clack = fx.mix(fx.fm_ding(3200, 2.7, 0.12, 2.5) * 0.6, bp(fx.click(r, 2, 2500), 1500, 8000))
    body = lp(fx.thump(160, 0.25, seed, material='wood'), 1500) * 0.4
    return fade(norm(fx.mix(scrape * 0.6, at(clack, 0.04), at(body, 0.04))))


def coin_clink(seed=0, f=2637.0):
    r = rng(seed)
    a = fx.fm_ding(f * r.uniform(0.98, 1.02), 2.76, 0.4, 3.0)
    b = fx.fm_ding(f * 1.5 * r.uniform(0.98, 1.02), 2.76, 0.3, 2.0) * 0.5
    return fade(norm(fx.mix(a, at(b, 0.035), bp(fx.click(r, 1.5, 3000), 2000, 9000) * 0.4)))


def register_ding(seed=0):
    """Cash register: drawer thunk + bell."""
    r = rng(seed)
    thunk = lp(fx.thump(90, 0.5, seed, material='wood'), 1200)
    bell = fx.mix(fx.fm_ding(2093, 3.5, 0.9, 3.5), 0.5 * fx.fm_ding(3136, 3.5, 0.7, 2.0))
    return fade(norm(fx.mix(thunk * 0.6, at(bell, 0.06))))


def crackle(dur, seed=0, density=14):
    """Old film / phonograph surface noise for the sepia sequences."""
    r = rng(seed)
    n = int(SR * dur)
    x = lp(pink(n, r), 3000) * 0.08
    k = 0
    t = r.uniform(0, 0.1)
    while t < dur - 0.01:
        c = hp(fx.click(r, r.uniform(0.5, 2), 1500), 1000) * r.uniform(0.2, 1)
        i = int(SR * t)
        x[i:i + len(c)] += c[: n - i]
        t += r.exponential(1 / density)
        k += 1
    return fade(norm(x, 0.6), 0.1, 0.1)


def crickets(dur, seed=0):
    r = rng(seed)
    n = int(SR * dur)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for k in range(3):
        f = r.uniform(4200, 5200)
        rate = r.uniform(14, 20)
        chirp = np.sin(2 * PI * f * t) * (np.sin(2 * PI * rate * t + k) > 0.2)
        gate = (np.sin(2 * PI * t / r.uniform(1.1, 1.7) + r.uniform(0, 6)) > 0.0)
        out += chirp * gate * r.uniform(0.3, 0.6)
    return fade(lp(out, 7000) * 0.3 + lp(pink(n, r), 300) * 0.25, 0.3, 0.3)


def clank(seed=0, f=520):
    """Iron hit (manhole cover, ladder rung)."""
    r = rng(seed)
    t = np.arange(int(SR * 0.7)) / SR
    x = sum(np.sin(2 * PI * f * m * t) * np.exp(-t / (0.25 / m)) / m for m in (1, 2.41, 3.9, 5.3))
    return fade(norm(fx.mix(x, fx.thump(70, 0.5, seed, material='wood') * 0.6)))


def rice_pour(dur, seed=0):
    return fade(norm(grains(dur, 900, 1500, 7000, seed) + lp(pink(int(SR * dur), rng(seed)), 900) * 0.2), 0.05, 0.1)


def chalk(dur, seed=0):
    r = rng(seed)
    n = int(SR * dur)
    u = np.arange(n) / SR
    x = svf_bp(r.standard_normal(n), 2400 + 800 * np.sin(2 * PI * 3 * u), 4)
    x *= (np.sin(2 * PI * 6 * u) > -0.3)
    return fade(norm(x), 0.01, 0.03)


def murmur(dur, seed=0, voices=8):
    """Crowd walla: overlapping band-passed noise syllables, voiced-band only, kept very low."""
    r = rng(seed)
    n = int(SR * dur)
    out = np.zeros(n)
    for v in range(voices):
        t = r.uniform(0, 0.4)
        while t < dur - 0.2:
            d = r.uniform(0.1, 0.25)
            m = int(SR * d)
            f = r.uniform(300, 900)
            syl = svf_bp(r.standard_normal(m), np.linspace(f, f * r.uniform(0.8, 1.3), m), 6) * np.hanning(m)
            i = int(SR * t)
            out[i:i + m] += syl[: n - i] * r.uniform(0.3, 1)
            t += d + r.uniform(0.05, 0.3)
    return fade(norm(lp(out, 1500)), 0.2, 0.2)


def sleigh(dur=1.0, seed=0):
    r = rng(seed)
    parts = []
    for k in range(int(dur * 16)):
        f = r.uniform(5000, 7000)
        parts.append(at(fx.fm_ding(f, 1.41, 0.12, 1.0) * r.uniform(0.3, 1), k / 16 + r.uniform(0, 0.02)))
    return fade(norm(fx.mix(*parts)))


def buzz(dur, seed=0):
    t = np.arange(int(SR * dur)) / SR
    f = 190 + 30 * np.sin(2 * PI * 3 * t) + 20 * np.sin(2 * PI * 7.3 * t)
    x = np.sign(np.sin(2 * PI * np.cumsum(f) / SR))
    return fade(norm(lp(x, 2500) * (0.6 + 0.4 * np.sin(2 * PI * 0.7 * t) ** 2)), 0.05, 0.1)


def stamp_thud(seed=0):
    return fade(norm(fx.mix(fx.thump(60, 1.0, seed, material='wood'), at(lp(fx.click(rng(seed), 4, 600), 3000) * 0.5, 0.0))))


sc.INSTR.update(zither=zither)


# ============================================================== spotting
def build(tl, n, log):
    sfx, hero, amb = Stem(n), Stem(n), Stem(n)
    bpm = 96
    beat = 60 / bpm
    seq = sc.Seq(tl.total + 2, seed=1902)
    W = tl.w

    def S(k):  # start of shot k (1-based, as in the shot list)
        return tl.s(k - 1)

    def D(k):
        return tl.d(k - 1)

    def H(name, sig, t, g=0.0):
        hero.add(sig, t, g)
        log.append((round(t, 2), name))

    def gap(i):
        return tl.gap_after(i)

    def in_gap(i, min_len=0.18):
        g0, g1 = gap(i)
        return g0 + 0.02 if g1 - g0 >= min_len else None

    # ---- ambience per space [801-860]
    sepia = set(range(5, 11)) | {84}
    sewer = {9, 11, 12, 14, 15, 28, 29, 30, 78, 79, 80}
    night = set(range(60, 72))
    office = {4, 18, 21, 22, 24, 35, 36, 56, 57, 58}
    shed_in = {49, 72, 73, 74}
    for k in range(1, len(tl.sb) + 1):
        t0, d = S(k), D(k) + 0.4
        if k in sepia:
            amb.add(crackle(d, 10 + k), t0 - 0.1, -2)
        if k in sewer:
            amb.add(LS.room_tone(d, 30 + k), t0 - 0.1, 2)
            for j in range(int(d * 1.5)):  # water drips in the tunnel
                amb.add(fx.fm_ding(1400 + 300 * (j % 3), 1.0, 0.15, 0.6) * 0.3, t0 + 0.3 + j * 0.67, -10)
        elif k in night:
            amb.add(crickets(d, 40 + k), t0 - 0.1, -2)
        elif k in office or k in shed_in or k in (23, 25, 33, 40, 41, 75, 76, 77, 81, 86, 87):
            amb.add(LS.room_tone(d, 50 + k), t0 - 0.1, 0)
        else:  # street / fields: town walla + light breeze
            amb.add(fx.mix(murmur(d, 60 + k, 5) * 0.5, LS.wind_howl(d, 70 + k, 0.3)), t0 - 0.1, -4)

    # ---- MUSIC (F# minor pentatonic, 96 BPM)
    F1, Cs2, B1, A1, E2 = N('F#1'), N('C#2'), N('B1'), N('A1'), N('E2')
    motif = ['F#5', 'A5', 'B5', 'C#6', 'B5', 'A5', 'F#5', 'E5']  # the catcher's sly zither motif

    def play_motif(t, k=4, vel=0.55, bus='lead', step=None):
        for j, nm in enumerate(motif[:k]):
            seq.note(t + j * (step or beat / 2), 'zither', N(nm), 0.3, vel, bus)

    # Act 1 hook (shots 1-4): zither motif on frame one over a low drone; woodblock pulse
    seq.note(0.0, 'drone', F1, S(5) - 0.2, 0.55, 'drone')
    play_motif(0.03, 4, 0.5)
    t = S(2)
    while t < S(5) - 0.1:
        seq.note(t, 'woodblock', N('C#6'), 0.05, 0.25, 'perc')
        t += beat
    play_motif(S(4) + 0.05, 2, 0.45)

    # Act 2 sepia flashback (5-10): music-box waltz in 3/4
    seq.note(S(5), 'drone', Cs2, S(11) - S(5), 0.4, 'drone')
    waltz = ['F#5', 'C#6', 'A5', 'E5', 'B5', 'A5', 'F#5', 'C#6', 'B5', 'A5', 'E5', 'F#5']
    t, j = S(5) + 0.05, 0
    while t < S(11) - 0.2:
        seq.note(t, 'celesta', N(waltz[j % len(waltz)]), 0.3, 0.32 if j % 3 else 0.42, 'lead')
        t += beat * 0.75
        j += 1
    sfx.add(LS.reverse_swell(0.8, 3), S(5) - 0.6, -18)
    sfx.add(fx.whoosh(0.6, 'down', 1.2, seed=4), S(5), -18)

    # Act 3 rats move in (11-14): pizz bass + marimba offbeats
    t0, t1 = S(11), S(15)
    prog = [(F1, 'F#'), (E2 - 12, 'E'), (B1, 'B'), (Cs2, 'C#')]
    t, j = t0, 0
    while t < t1 - 0.1:
        root = prog[(j // 4) % 4][0]
        seq.note(t, 'pizz', root + (0, 7, 12, 7)[j % 4], 0.2, 0.45, 'bass')
        if j % 2 == 1:
            seq.note(t, 'marimba', N('F#5') + (0, 3, 5, 7)[(j // 2) % 4], 0.15, 0.3, 'lead')
        t += beat / 2
        j += 1

    # Act 4 plague (15-16): dark tritone pad, drone
    seq.note(S(15), 'drone', F1, D(15) + D(16), 0.55, 'drone')
    seq.note(S(16), 'pad', N('F#4'), D(16), 0.22, 'pad')
    seq.note(S(16), 'pad', N('C5'), D(16), 0.16, 'pad')

    # Act 5 the bounty office (17-25): oom-pah march
    t, j = S(17), 0
    while t < S(26) - 0.15:
        seq.note(t, 'brass', (F1 + 12, Cs2 + 12)[j % 2] - 12, 0.18, 0.5, 'bass')
        seq.note(t + beat / 2, 'pizz', N('A4') if j % 2 == 0 else N('B4'), 0.1, 0.25, 'lead')
        seq.note(t + beat / 2, 'woodblock', N('E6'), 0.05, 0.2, 'perc')
        t += beat
        j += 1

    # Act 6 hero intro (26): drop the march, the motif alone in the gaps
    seq.note(S(26), 'drone', F1, D(26), 0.45, 'drone')
    play_motif(S(26) + 0.05, 4, 0.5)
    g = in_gap(170)
    if g:
        play_motif(g, 3, 0.55, step=0.12)

    # Act 7 the trick (27-34): tiptoe pizzicato
    t, j = S(27), 0
    tip = ['F#3', 'A3', 'B3', 'C4', 'C#4', 'C4', 'B3', 'A3']
    while t < S(35) - 0.1:
        seq.note(t, 'pizz', N(tip[j % 8]), 0.1, 0.32, 'lead')
        if j % 4 == 0:
            seq.note(t, 'pizz', F1 + 12 if j % 8 == 0 else Cs2, 0.2, 0.4, 'bass')
        t += beat / 2
        j += 1

    # Act 8 tails roll in (35-41): rising groove, fanfare on "thrilled", bells for Christmas
    t, j = S(35), 0
    while t < S(42) - 0.15:
        seq.note(t, 'pizz', (F1, F1, A1, B1, Cs2, B1, A1, E2 - 12)[j % 8] + 12, 0.18, 0.45, 'bass')
        if j % 2:
            seq.note(t, 'marimba', N(('F#5', 'A5', 'B5', 'C#6')[(j // 2) % 4]), 0.12, 0.3, 'lead')
        seq.note(t, 'shaker', 0, 0.05, 0.15, 'perc')
        t += beat / 2
        j += 1
    for nm in ('F#4', 'A4', 'C#5'):  # fanfare stab after "thrilled."
        seq.note(gap(241)[0] + 0.02, 'brass', N(nm), 0.35, 0.35, 'button')
    sfx.add(sleigh(1.2, 41), W(269) - 0.1, -18)
    sfx.add(LS.sparkle(0.6, 42, 1480), S(38) + 0.05, -18)

    # Act 9 "Now here's the weird part." drop-out -> swell -> boom in the gap
    music_cuts = [(S(42) - 0.05, S(43) - 0.1)]
    g0, g1 = gap(274)
    H('reverse swell', LS.reverse_swell(0.8, 9), g1 - 0.8, -12)
    H('low boom', LS.low_boom(10, 46, 1.1), S(42) + 0.02, -10)

    # Act 10 the rice and the shed (43-49): mysterious tiptoe with the zither
    seq.note(S(43), 'drone', F1, S(50) - S(43), 0.45, 'drone')
    t, j = S(43), 0
    while t < S(50) - 0.1:
        seq.note(t, 'pizz', N(('F#3', 'C#4', 'A3', 'B3')[j % 4]), 0.1, 0.3, 'lead')
        seq.note(t, 'tick', 0, 0.03, 0.25, 'perc')
        t += beat
        j += 1
    play_motif(S(46) + 0.05, 4, 0.4)
    H('?! sting', fx.startle_sting(739.99, 48), S(48) + 0.1, -12)

    # Act 11 gossip + the official (50-55): playful marimba, brass scold
    t, j = S(50), 0
    while t < S(56) - 0.1:
        seq.note(t, 'marimba', N(('F#5', 'E5', 'C#5', 'B4', 'C#5', 'E5')[j % 6]), 0.12, 0.28, 'lead')
        if j % 2 == 0:
            seq.note(t, 'pizz', (F1, Cs2, B1)[(j // 2) % 3] + 12, 0.18, 0.4, 'bass')
        t += beat / 2
        j += 1
    for nm in ('C4', 'F#4'):
        seq.note(W(349) - 0.02, 'brass', N(nm), 0.3, 0.3, 'pad')

    # Act 12 30,000 / 40,000 (56-59): ticks accelerate; register dings on each number
    t, k = S(56), 0
    while t < S(60) - 0.1:
        seq.note(t, 'tick', 0, 0.03, 0.4, 'perc')
        k += 1
        t += max(0.09, beat * 0.92 ** k)
    seq.note(S(56), 'drone', Cs2, S(60) - S(56), 0.45, 'drone')
    H('register 30k', register_ding(57), S(57) + 0.02, -12)
    H('register 40k', register_ding(58), S(58) + 0.02, -12)

    # Act 13 night (60-71): suspense pulse, tremolo pad, then silence before the door
    seq.note(S(60), 'drone', F1, S(72) - S(60), 0.55, 'drone')
    t = S(60)
    while t < S(71) - 0.5:
        seq.note(t, 'bass', F1 + 12, 0.15, 0.35, 'bass')
        t += beat
    for nm in ('F#4', 'C#5'):
        seq.note(S(61), 'pad', N(nm), S(66) - S(61), 0.12, 'pad')
    for nm in ('F#4', 'G4', 'C#5'):
        seq.note(S(66), 'pad', N(nm), S(71) - S(66), 0.12, 'pad')
    music_cuts.append((S(71) - 0.45, S(72) - 0.02))

    # Act 14 the reveal (72-74): boom + dissonant cluster, then chewing
    t72 = S(72)
    H('reveal boom', LS.low_boom(15, 42, 1.3), t72 - 0.02, -7)
    H('reveal glitch', LS.glitch(0.15, 16), t72 - 0.02, -14)
    for nm in ('F#4', 'G4', 'C5', 'C#5'):
        seq.note(t72, 'pad', N(nm), S(75) - t72, 0.16, 'pad')
    seq.note(t72, 'drone', F1, S(75) - t72, 0.55, 'drone')

    # Act 15 the explanation (75-83): light thinking groove
    t, j = S(75), 0
    while t < S(84) - 0.15:
        seq.note(t, 'marimba', N(('F#5', 'C#5', 'A5', 'C#5')[j % 4]), 0.12, 0.26, 'lead')
        if j % 2 == 0:
            seq.note(t, 'pizz', (F1, A1, B1, Cs2)[(j // 4) % 4] + 12, 0.2, 0.42, 'bass')
        t += beat / 2
        j += 1

    # Act 16 "In real life" (84): archival, a held drone only
    seq.note(S(84), 'drone', Cs2, D(84), 0.4, 'drone')

    # Act 17 ending (85-87): the motif alone, then the button
    seq.note(S(85), 'drone', F1, tl.total - S(85), 0.5, 'drone')
    play_motif(S(85) + 0.05, 4, 0.45)
    play_motif(S(86) + 0.05, 2, 0.4)
    end = tl.we(len(tl.words) - 1)
    tb = end + 0.32  # button >= 300 ms after the last word [759]
    H('final register', register_ding(87), tb, -8)
    H('final boom', LS.low_boom(88, 46, 1.2), tb, -8)
    for nm in ('F#4', 'A4', 'C#5', 'F#5'):
        seq.note(tb + 0.05, 'celesta', N(nm), 0.6, 0.5, 'button')

    # ---- per-shot SFX (anchored to the words the gags land on)
    sfx.add(squeak(1, 0, 3), S(1) + 0.4, -20)
    H('snip', snip(2), W(10) - 0.02, -8)                                    # "off" (shot 2)
    sfx.add(fx.whoosh(0.3, 'pass', 0.8, seed=3), W(10) + 0.05, -20)          # tail flips away
    sfx.add(fx.scurry(0.8, 14, 3, 0.6), S(3) + 0.12, -16)
    sfx.add(coin_clink(4), W(20), -12)                                       # "paid"
    for k in range(5):
        sfx.add(LS.paper_flutter(5 + k), S(5) + 0.15 + k * 0.28, -20)
    sfx.add(LS.creak(0.3, 300, 6) * 0.4, S(5) + 0.1, -22)                    # clock spring rewinding
    sfx.add(snip(7) * 0.7, S(7) + 0.4, -16)                                  # ribbon cut
    sfx.add(fx.pop(True, 1.0, 523, seed=7), W(41), -20)                      # proud sparkle
    H('manhole', clank(8, 330), S(8) + 0.15, -14)
    sfx.add(fx.whoosh(0.9, 'down', 1.4, seed=8), S(8) + 0.6, -16)
    sfx.add(LS.sparkle(0.9, 9, 1760), S(9) + 0.2, -22)
    for i in range(5):
        sfx.add(fx.pop(True, 0.8, 600 + 80 * i, seed=11 + i), S(11) + 0.05 + i * 0.2, -20)
    sfx.add(squeak(11, 3, 2), W(62) + 0.05, -20)
    sfx.add(LS.creak(0.6, 70, 12) * 0.5, S(12) + 0.1, -22)                    # snore
    sfx.add(fx.scurry(1.0, 16, 13, 0.5), S(13) + 0.1, -18)                   # up the pipe
    sfx.add(fx.pop(True, 1.0, 440, seed=13), W(78) - 0.05, -16)               # pops out by the stove
    for k in range(5):
        sfx.add(fx.pop(True, 0.6, 880 + 110 * k, seed=14 + k), W(81) + k * 0.09, -20)
    sfx.add(coin_clink(14, 3520) * 0.5, W(85), -22)                          # room-service cloche
    for k in range(6):
        sfx.add(fx.boing(900 + 60 * k, 0.12) * 0.5, W(90) + k * 0.06, -24)   # fleas hop on
    sfx.add(fx.whoosh(1.2, 'pass', 1.5, seed=16), S(16) + 0.1, -18)          # miasma rolls in
    for k in range(3):
        sfx.add(lp(fx.thump(200, 0.25, 17 + k, material='wood'), 2000), S(17) + 0.2 + k * 0.12, -16)  # hammer
    sfx.add(lp(fx.thump(70, 0.6, 18, material='wood'), 1500), W(104), -12)   # dead rat lands
    H('one cent', coin_clink(18), in_gap(111) or W(110), -12)
    sfx.add(fx.mix(*[at(lp(clank(19 + k, 700), 2500) * 0.3, k * 0.45) for k in range(4)]), S(19) + 0.1, -22)
    sfx.add(LS.creak(1.2, 90, 20) * 0.6, S(20), -18)                         # cart wheel
    sfx.add(lp(fx.mix(*[at(fx.thump(90, 0.4, 21 + k, material='wood'), k * 0.13) for k in range(14)]), 1200),
            S(21) + 0.1, -16)                                                # the pile rising
    sfx.add(buzz(D(22), 22), S(22), -24)
    sfx.add(chalk(0.35, 23), W(147), -20)                                    # pen strikes it out
    sfx.add(fx.pop(False, 1.0, 300, seed=24), W(153) - 0.08, -16)            # the NO sign
    sfx.add(LS.sparkle(0.8, 25, 1760), W(157), -20)
    sfx.add(snip(26) * 0.5, S(26) + 0.6, -22)                                # scissors twirl
    sfx.add(fx.mix(*[at(clank(27 + k, 900), k * 0.28) for k in range(5)]), S(27) + 0.15, -20)  # ladder
    sfx.add(squeak(28, 0, 3), W(179) + 0.2, -16)
    H('snip 2', snip(29), W(187) - 0.07, -8)
    sfx.add(fx.scurry(1.0, 13, 30, 0.7), W(191) - 0.2, -16)
    sfx.add(fx.pop(True, 1.0, 660, seed=30), W(191), -20)                    # heart
    sfx.add(squeak(32, 5, 1), S(32) + 0.4, -22)
    for k in range(6):                                                       # barber snips
        sfx.add(snip(33 + k) * 0.35, S(33) + 0.1 + k * 0.2, -22)
    sfx.add(fx.whoosh(0.25, 'pass', 0.6, seed=34), W(218), -20)              # into the pocket
    sfx.add(LS.sparkle(0.4, 34, 2093), W(218) + 0.3, -22)
    for k, i in enumerate((228, 237)):
        H(f'register {k}', register_ding(35 + k), W(i) + 0.1, -14)
    H('fanfare cheer', fx.mix(*[at(fx.pop(True, 0.6, 700 + 90 * j, seed=37 + j), j * 0.05) for j in range(8)]),
      gap(241)[0] + 0.02, -16)
    sfx.add(LS.page_flip(38, 0.4), S(38), -16)
    sfx.add(murmur(D(39), 39, 12), S(39), -14)
    sfx.add(fx.mix(*[at(coin_clink(390 + j) * 0.3, j * 0.08) for j in range(12)]), W(254), -20)
    sfx.add(chalk(1.0, 40), S(40) + 0.1, -18)
    sfx.add(chalk(0.6, 41), S(41) + 0.1, -20)
    sfx.add(coin_clink(43), W(279), -14)
    for i in range(6):
        sfx.add(lp(fx.thump(80, 0.5, 44 + i, material='sand'), 1500), S(44) + 0.2 + i * 0.12, -14)
    sfx.add(fx.mix(*[at(lp(fx.thump(70, 0.5, 45 + i, material='sand'), 1200), i * 0.1) for i in range(6)]), S(45) + 0.1, -22)
    sfx.add(LS.wood_steps(5, 2.5, 46), S(46) + 0.1, -22)
    sfx.add(LS.creak(0.5, 140, 47), S(47) + 0.8, -22)
    sfx.add(rice_pour(D(49), 49), S(49), -18)
    sfx.add(squeak(49, 6, 3), S(49) + 0.5, -20)
    sfx.add(LS.whisper_texture(D(50), 50), S(50), -20)
    sfx.add(fx.mix(*[at(fx.yelp(51 + k, -6) * 0.4, k * 0.18) for k in range(4)]), S(51) + 0.05, -24)  # laughs
    sfx.add(fx.pop(True, 1.0, 392, seed=51), W(324) - 0.4, -18)              # thought bubble
    sfx.add(fx.mix(*[at(lp(fx.thump(250, 0.2, 52 + k, material='wood'), 2500), k * 0.12) for k in range(3)]),
            W(333) - 0.1, -18)                                               # sign nailed up
    sfx.add(LS.wood_steps(3, 3.0, 53), S(53) + 0.1, -18)
    sfx.add(fx.pop(True, 1.0, 330, seed=54), W(349) - 0.1, -18)
    sfx.add(squeak(55, 4, 2), W(353), -18)
    sfx.add(grains(D(56) + D(57) + D(58), 260, 600, 3500, 56) * 0.6, S(56), -18)  # tails sliding down the chute
    sfx.add(fx.mix(*[at(squeak(59 + k, k), k * 0.3) for k in range(6)]), W(370), -20)
    sfx.add(LS.wood_steps(4, 1.8, 61), S(61) + 0.1, -18)                     # footsteps on cobbles
    H('scurry over shoe', fx.scurry(0.4, 18, 62, 0.6), W(387) - 0.05, -12)
    H('! sting', fx.startle_sting(739.99, 62), in_gap(390) or W(390) + 0.3, -14)
    sfx.add(squeak(63, 2, 1), S(63) + 0.15, -16)
    H('fat boing', fx.boing(220, 0.4), S(64) + 0.02, -12)
    H('healthy sparkle', LS.sparkle(0.6, 65, 2349), S(65) + 0.05, -14)
    H('no tail sting', fx.startle_sting(783.99, 66) * 0.8, in_gap(397) or W(397) + 0.3, -12)
    sfx.add(fx.scurry(0.6, 18, 67, 0.6), S(67) + 0.05, -14)
    H('stampede', fx.mix(*[at(fx.scurry(0.8, 16, 68 + k, 0.6), k * 0.05) for k in range(6)]), S(68) + 0.1, -12)
    sfx.add(fx.mix(*[at(squeak(680 + k, k), k * 0.12) for k in range(5)]), S(68) + 0.3, -18)
    sfx.add(LS.wood_steps(5, 2.2, 69), S(69) + 0.1, -20)
    sfx.add(LS.wood_steps(4, 2.0, 70), S(70) + 0.4, -22)
    H('door creak', LS.creak(0.9, 85, 71), S(71) + 0.12, -12)
    sfx.add(fx.chew(D(74) + 0.4, 74), S(74), -14)
    sfx.add(rice_pour(D(73), 73) * 0.4, S(73), -24)
    sfx.add(fx.mix(*[at(squeak(730 + k, k % 4), k * 0.25) for k in range(8)]), S(73) + 0.1, -22)
    sfx.add(coin_clink(75), S(75) + 0.15, -16)
    sfx.add(fx.pop(False, 1.0, 300, seed=75), W(442) - 0.05, -16)            # red X
    sfx.add(fx.whoosh(0.35, 'pass', 0.8, seed=76), S(76) + 0.05, -18)        # arrow to the tail
    sfx.add(fx.pop(True, 1.0, 523, seed=77), W(458) - 0.1, -18)              # "="
    for k in range(14):
        sfx.add(squeak(780 + k, 7, 1) * 0.6, W(467) - 0.3 + k * 0.06, -22)
    for k in range(8):
        sfx.add(coin_clink(790 + k, 2637 + 200 * k) * 0.5, W(480) + k * 0.03, -20)
    sfx.add(fx.scurry(1.0, 13, 80, 0.7), S(80) + 0.2, -18)
    sfx.add(fx.whoosh(1.0, 'up', 1.2, seed=81), S(81) + 0.1, -18)            # the curve shoots up
    sfx.add(fx.mix(*[at(coin_clink(810 + k) * 0.3, k * 0.1) for k in range(8)]), S(81) + 0.4, -22)
    sfx.add(fx.pop(True, 1.0, 300, seed=82), W(501), -14)                    # weed pulled
    sfx.add(coin_clink(82), W(503), -16)
    sfx.add(fx.pop(True, 1.0, 392, seed=83), W(509), -16)                    # weed sprouts back
    sfx.add(fx.thump(60, 1.2, 84, material='wood') * 0.5, W(515), -16)       # backfire puff
    H('stamp', stamp_thud(84), W(520) - 0.05, -10)
    sfx.add(squeak(85, 3, 3), S(85) + 0.5, -20)
    sfx.add(fx.whoosh(0.4, 'pass', 0.7, seed=86), W(538) - 0.25, -18)        # tail -> coin
    sfx.add(coin_clink(86), W(538) + 0.1, -14)
    sfx.add(lp(LS.creak(1.2, 60, 87), 1200), S(87), -16)                     # vault door swings
    return sfx, hero, amb, seq, music_cuts


def report(stems, tl, n, st, pre_limit):
    """Voice-first verification: bed vs voice, consonant band, worst window, limiter vs voice."""
    vo = stems['vo']
    bed = stems['music'] + stems['sfx'] + stems['amb']
    m = np.zeros(n, bool)
    for i, w in enumerate(tl.words):
        m[int(SR * w['t0']):int(SR * tl.we(i))] = True

    def rms(x):
        return 10 * np.log10(np.mean(x ** 2) + 1e-12)
    out = {'bed_vs_voice_during_speech_db': round(rms(vo[m]) - rms(bed[m]), 1)}
    vb, bb = bp(vo, 1000, 4000), bp(bed, 1000, 4000)
    out['bed_vs_voice_1_4k_db'] = round(rms(vb[m]) - rms(bb[m]), 1)
    worst = 99
    for s0 in range(0, n - SR, SR // 2):
        mm = m[s0:s0 + SR]
        if mm.mean() > 0.5:
            worst = min(worst, rms(vo[s0:s0 + SR][mm]) - rms(bed[s0:s0 + SR][mm]))
    out['worst_1s_window_db'] = round(worst, 1)
    gapm = ~m
    gapm[: int(SR * 0.3)] = False
    out['bed_in_gaps_vs_speech_db'] = round(rms(vo[m]) - rms(bed[gapm]), 1)
    g = np.abs(st[:, 0]) / np.maximum(np.abs(pre_limit[:, 0]), 1e-9)
    loud_vo = m & (np.abs(vo) > 0.05)
    out['limiter_gain_on_voice_min_db'] = round(20 * np.log10(max(1e-9, np.min(g[loud_vo]) if loud_vo.any() else 1)), 2)
    return out


def main():
    meta = json.load(open(os.path.join(HERE, 'words.json')))
    words, total = meta['words'], meta['duration']
    bounds = scenes.install(words, total)
    tl = TL(words, total, bounds)
    n = int(SR * total)

    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(HERE, 'vo.mp3'), '-ac', '1',
                          '-ar', str(SR), '-af', 'aresample=resampler=soxr', '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    vo = np.frombuffer(raw, np.float32).astype(float)
    vo = np.pad(vo, (0, max(0, n - len(vo))))[:n]           # UNPROCESSED voice

    log = []
    sfx, hero, amb, seq, music_cuts = build(tl, n, log)

    def bus(name, g):
        return seq.get(name)[:n] * db(g)

    full = (bus('lead', -10) + bus('drone', -16) + bus('pad', -19) + bus('bass', -13) + bus('perc', -18))
    for c0, c1 in music_cuts:                                 # drop-outs before the big beats
        a, b = int(SR * c0), int(SR * c1)
        full[a:b] *= np.linspace(1, 0, b - a) ** 3
    full = hp(full, 38)
    safe = lp(full, 1800)
    m = speech_mask(vo, tl, n)
    music = (full * (1 - m) + safe * m) * db(-13 * m) + bus('button', -10)
    sfx_x = (sfx.x * (1 - m) + lp(sfx.x, 3500) * m) * db(-8 * m)    # SFX under words: darker and lower
    amb_x = hp(amb.x, 80) * db(-28) * db(-8 * m)
    hero_x = hero.x * db(-10 * m)  # gap hits; tails duck hard once words return

    stems = {'vo': vo, 'music': music, 'sfx': sfx_x + hero_x, 'amb': amb_x}
    mixm = sum(stems.values())
    side = np.convolve(amb_x + 0.3 * music, np.r_[np.zeros(int(SR * 0.012)), 1], 'same') * 0.25
    st = np.stack([mixm + side, mixm - side], axis=1)
    pre = st.copy()
    for _ in range(3):
        g = db(-14 - lufs(st))
        st = st * g
        pre = pre * g
        st = limiter(st, -1.5)
    L = lufs(st)

    out = os.path.join(HERE, 'out')
    os.makedirs(os.path.join(out, 'stems'), exist_ok=True)
    sf.write(os.path.join(out, 'rat_tails_mix.wav'), st.astype(np.float32), SR, subtype='PCM_24')
    for k, v in stems.items():
        sf.write(os.path.join(out, 'stems', f'{k}.wav'), v.astype(np.float32), SR, subtype='PCM_24')
    rep = report(stems, tl, n, st, pre)
    rep.update(lufs=round(L, 2), peak_dbfs=round(20 * np.log10(np.abs(st).max()), 2))
    json.dump({'report': rep, 'hero_events': log}, open(os.path.join(out, 'stems', 'cue_log.json'), 'w'), indent=1)
    print(f'mix {total:.2f}s  {L:.2f} LUFS  peak {rep["peak_dbfs"]:.2f} dBFS')
    for k, v in rep.items():
        print(f'  {k}: {v}')


if __name__ == '__main__':
    main()
