"""The Blank Library: sound design + mix around the supplied voiceover.

Voice-first rules (drongo/sound/SPEC.md + principles):
  * the VO is already mastered (-14.2 LUFS, -2.7 dBFS): it is NOT processed, only resampled;
  * music lives in D minor and never sustains near the voice fundamental (~117 Hz / A2-ish);
  * under speech, music is low-passed (consonant band left free) and ducked 12 dB;
  * hits, stingers and anything with transients go in the narration's gaps;
  * the mix is normalised to -14 LUFS with true peak <= -1.5 dBTP after AAC.

    python3 sound.py  ->  out/library_mix.wav + out/stems/
"""
import json
import os
import subprocess
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'drongo'))
sys.path.insert(0, os.path.join(HERE, '..', 'drongo', 'sound'))

import sfxlib as fx  # noqa: E402
from sfxlib import SR, PI, rng, env_exp, fade, bp, lp, hp, comb, pink, at, norm, soft_clip, svf_bp, sweep, grains  # noqa: E402
import score as sc  # noqa: E402
from score import N  # noqa: E402
from design import TL, Stem, speech_mask, limiter, lufs, db  # noqa: E402
import scenes  # noqa: E402
import render as R  # noqa: E402


# ============================================================== new recipes
def page_flip(seed=0, dur=0.45):
    """Paper: band-passed noise flutter with a crisp snap at the end [431, 566]."""
    r = rng(seed)
    n = int(SR * dur)
    u = np.linspace(0, 1, n)
    x = svf_bp(r.standard_normal(n), 1200 + 2500 * u, 1.2) * np.sin(PI * u) ** 1.5
    x *= 1 - 0.5 * (0.5 + 0.5 * np.sin(2 * PI * np.cumsum(18 + 30 * u) / SR))
    snap = bp(r.standard_normal(int(SR * 0.03)), 2000, 7000) * env_exp(int(SR * 0.03), 0.001, 0.006)
    return fade(norm(fx.mix(x, at(snap * 0.7, dur * 0.82))))


def paper_flutter(seed=0):
    return page_flip(seed, 0.3) * 0.7


def wind_howl(dur, seed=0, strength=1.0):
    r = rng(seed)
    n = int(SR * dur)
    t = np.arange(n) / SR
    fc = 380 + 220 * np.sin(2 * PI * t / 5.3 + 1) + 120 * np.sin(2 * PI * t / 2.1)
    x = svf_bp(pink(n, r), fc, 6) * 0.6 + lp(pink(n, r), 300) * 0.5
    x *= 0.6 + 0.4 * np.sin(2 * PI * t / 7 + r.uniform(0, 6)) ** 2
    return fade(norm(x, 0.5) * strength, 0.4, 0.4)


def snow_steps(dur, rate=2.2, seed=0):
    """Squeaky snow crunch: compact granular bursts, low-passed [561, 565]."""
    r = rng(seed)
    out = np.zeros(int(SR * (dur + 0.3)))
    t = 0.05
    k = 0
    while t < dur:
        g = grains(0.13, 2500, 800, 4500, seed * 50 + k, decay=0.05)
        th = lp(r.standard_normal(int(SR * 0.04)), 400) * env_exp(int(SR * 0.04), 0.004, 0.012)
        s = fx.mix(g, th * 0.8) * r.uniform(0.7, 1.0)
        i = int(SR * t)
        out[i:i + len(s)] += s[: len(out) - i]
        t += 1 / rate * r.uniform(0.9, 1.1)
        k += 1
    return fade(norm(out[: int(SR * dur)]))


def wood_steps(count=3, rate=2.0, seed=0, room=True):
    r = rng(seed)
    parts = []
    for k in range(count):
        n = int(SR * 0.12)
        tt = np.arange(n) / SR
        knock = np.sin(2 * PI * 180 * tt) * np.exp(-tt / 0.03) + 0.4 * np.sin(2 * PI * 410 * tt) * np.exp(-tt / 0.015)
        knock += bp(r.standard_normal(n), 300, 2500) * env_exp(n, 0.001, 0.01) * 0.4
        parts.append(at(knock * r.uniform(0.7, 1.0), k / rate))
    x = fx.mix(*parts)
    if room:
        x = fx.mix(x, at(lp(x, 1500) * 0.25, 0.045), at(lp(x, 1000) * 0.12, 0.11))
    return fade(norm(x))


def creak(dur=0.7, f0=140, seed=0):
    """Wood/hinge creak: stick-slip pulse train through a resonant band [442, 497]."""
    r = rng(seed)
    n = int(SR * dur)
    u = np.linspace(0, 1, n)
    rate = f0 * (1 + 0.35 * np.sin(2 * PI * u * r.uniform(1, 2.5)) + 0.1 * r.standard_normal(n).cumsum() / np.sqrt(n))
    ph = np.cumsum(rate) / SR
    pulses = (np.diff(np.floor(ph), prepend=0) > 0).astype(float)
    x = svf_bp(pulses, 900, 8) + svf_bp(pulses, 1900, 10) * 0.5
    return fade(norm(lp(x, 2500) * np.sin(PI * u) ** 0.6), 0.02, 0.05)


def door_thud(seed=0):
    th = fx.thump(52, 1.4, seed, material='wood')
    tail = comb(lp(th, 900), 9, 0.55)
    return fade(norm(fx.mix(th, at(tail * 0.5, 0.02), at(creak(0.4, 90, seed) * 0.25, 0.0))))


def low_boom(seed=0, f=42, dur=2.2):
    """Cinematic sub boom with audible harmonics for phones [407, 443]."""
    r = rng(seed)
    s, _ = sweep(f * 2.2, f, 0.25)
    body = np.concatenate([s, np.sin(2 * PI * f * np.arange(int(SR * dur)) / SR)])[: int(SR * dur)]
    body = soft_clip(body * env_exp(len(body), 0.002, dur / 4), 3.0)
    air = lp(pink(int(SR * dur), r), 900) * env_exp(int(SR * dur), 0.005, dur / 5) * 0.4
    return fade(norm(fx.mix(body, air)), 0.002, 0.2)


def reverse_swell(dur=1.0, seed=0, hi=True):
    r = rng(seed)
    n = int(SR * dur)
    x = bp(pink(n, r), 300, 6000 if hi else 2000) * env_exp(n, 0.001, dur / 3)
    tone = sum(np.sin(2 * PI * f * np.arange(n) / SR) for f in (293.66, 440, 587.3)) * env_exp(n, 0.001, dur / 2.5) * 0.15
    return fade(norm((x + tone)[::-1]), 0.05, 0.003)


def celesta(f, dur, vel, r):
    """Music-box / celesta: FM bell, ratio 1:3.5-ish, bright then pure [436, 437]."""
    n = int(SR * 1.6)
    t = np.arange(n) / SR
    idx = 2.2 * np.exp(-t / 0.05)
    x = np.sin(2 * PI * f * t + idx * np.sin(2 * PI * f * 4.0 * t)) * np.exp(-t / 0.55)
    x += 0.25 * np.sin(2 * PI * f * 2 * t) * np.exp(-t / 0.2)
    return x * vel * 0.55


def drone(f, dur, vel, r):
    n = int(SR * (dur + 1.0))
    t = np.arange(n) / SR
    x = sum(np.sin(2 * PI * f * m * t + r.random() * 6) / m for m in (1, 2, 3, 4))
    x *= 1 + 0.15 * np.sin(2 * PI * 0.3 * t)
    e = np.minimum(1, t / 0.8) * np.where(t < dur, 1.0, np.exp(-(t - dur) / 0.5))
    return lp(x, 500) * e * vel * 0.5


def tick(f, dur, vel, r):
    n = int(SR * 0.04)
    t = np.arange(n) / SR
    return (np.sin(2 * PI * 2400 * t) * 0.3 + bp(r.standard_normal(n), 2500, 6000) * 0.6) * np.exp(-t / 0.006) * vel


sc.INSTR.update(celesta=celesta, drone=drone, tick=tick)


def whisper_texture(dur, seed=0):
    """Many overlapping unvoiced 'whispers': formant-filtered noise syllables,
    high-passed so they never mask the narrator's voiced band [553, 412]."""
    r = rng(seed)
    n = int(SR * dur)
    out = np.zeros(n)
    t = 0.0
    while t < dur - 0.15:
        d = r.uniform(0.12, 0.3)
        m = int(SR * d)
        f1, f2 = r.uniform(1800, 2800), r.uniform(3500, 6000)
        syl = svf_bp(r.standard_normal(m), np.linspace(f1, f2, m), 5) * np.sin(PI * np.linspace(0, 1, m)) ** 2
        i = int(SR * t)
        out[i:i + m] += syl[: n - i] * r.uniform(0.4, 1)
        t += r.uniform(0.05, 0.14)
    return fade(norm(hp(out, 2500)), 0.08, 0.15)


def cctv_click(seed=0):
    r = rng(seed)
    a = bp(fx.click(r, 3, 1500), 1500, 6000)
    b = np.sin(2 * PI * 1800 * np.arange(int(SR * 0.12)) / SR) * env_exp(int(SR * 0.12), 0.002, 0.05)
    servo = svf_bp(r.standard_normal(int(SR * 0.25)), 700, 6) * np.hanning(int(SR * 0.25))
    return fade(norm(fx.mix(servo * 0.5, at(a, 0.26), at(b * 0.5, 0.34))))


def tape_whir(dur=0.9, up=True, seed=0):
    r = rng(seed)
    n = int(SR * dur)
    u = np.linspace(0, 1, n)
    f = (300 + 1500 * u) if up else (1600 - 1200 * u)
    ph = 2 * PI * np.cumsum(f) / SR
    x = (np.sin(ph) * 0.3 + bp(r.standard_normal(n), 1500, 5000) * 0.6) * (1 - 0.5 * (np.sin(2 * PI * 40 * u * dur) > 0))
    return fade(norm(x * np.sin(PI * u) ** 0.4))


def glitch(dur=0.2, seed=0):
    r = rng(seed)
    n = int(SR * dur)
    x = r.standard_normal(n)
    hold = int(SR * 0.004)
    x = np.repeat(x[::hold], hold)[:n]  # sample-and-hold "bitcrush"
    x = np.round(x * 3) / 3
    return fade(norm(bp(x, 400, 6000) * (r.random(n // 400 + 1) > 0.35).repeat(400)[:n]))


def hum(dur, f=60, seed=0, level=1.0):
    t = np.arange(int(SR * dur)) / SR
    x = sum(np.sin(2 * PI * f * m * t) / m for m in (1, 2, 3, 5))
    x += hp(rng(seed).standard_normal(len(t)), 6000) * 0.1
    return fade(x * 0.2 * level, 0.2, 0.2)


def rain_bed(dur, seed=0):
    return fade(norm(grains(dur, 2200, 1500, 9000, seed) + lp(pink(int(SR * dur), rng(seed)), 600) * 0.4, 0.5), 0.2, 0.2)


def room_tone(dur, seed=0):
    r = rng(seed)
    return fade(lp(pink(int(SR * dur), r), 250) * 0.15 + hum(dur, 50, seed, 0.15), 0.3, 0.3)


def sparkle(dur=0.8, seed=0, f0=1760):
    r = rng(seed)
    parts = []
    for k in range(int(dur * 14)):
        f = f0 * 2 ** (r.choice([0, 3, 5, 7, 10, 12]) / 12)
        n = int(SR * 0.25)
        tt = np.arange(n) / SR
        parts.append(at(np.sin(2 * PI * f * tt) * np.exp(-tt / 0.07) * r.uniform(0.3, 1), k / 14 + r.uniform(0, 0.03)))
    return fade(norm(fx.mix(*parts)))


# ============================================================== spotting
def build(tl, n, log):
    sfx, hero, amb = Stem(n), Stem(n), Stem(n)
    bpm = 76
    beat = 60 / bpm
    seq = sc.Seq(tl.total + 2, seed=76)
    S, D, W = tl.s, tl.d, tl.w

    def H(name, sig, t, g=0.0):
        hero.add(sig, t, g)
        log.append((round(t, 2), name))

    ext = {0, 2, 3, 9, 11}
    # ---- ambience per space [801-860]
    for k, (t0, t1) in enumerate(tl.sb):
        d = t1 - t0 + 0.5
        if k in ext:
            amb.add(wind_howl(d, 10 + k), t0 - 0.2, -2)
        elif k in (12, 13):
            amb.add(rain_bed(d, 20 + k), t0 - 0.1, -4)
        elif k in (15, 16, 17):
            amb.add(hum(d, 60, k, 1.0), t0, -6)
        else:
            amb.add(room_tone(d, 30 + k), t0 - 0.2, 0)

    # ---- MUSIC: D minor music box over a low D drone [631-646 adapted to a mystery]
    D1, D2 = N('D2'), N('D3')
    seq.note(0.0, 'drone', D1, S(8) - 0.3, 0.6, 'drone')                    # avoids the voice's ~117 Hz
    motif = ['D5', 'F5', 'A5', 'G5', 'F5', 'E5', 'C#5', 'D5']               # music-box motif, harmonic minor
    for k, nm in enumerate(motif[:4]):                                       # hook on frame one [608]
        seq.note(0.02 + k * beat / 2, 'celesta', N(nm), 0.3, 0.55, 'lead')
    # clock-tick pulse from the facade to the reading scene (sparse, under speech) [669]
    t = S(3)
    while t < S(8) - 0.2:
        seq.note(t, 'tick', 0, 0.03, 0.35, 'perc')
        t += beat
    for k, nm in enumerate(('D3', 'A2', 'D3', 'A#2', 'D3', 'A2', 'C#3', 'A2')):  # low pizz ostinato
        tt = S(4) + k * beat
        if tt < S(8) - 0.3:
            seq.note(tt, 'pizz', N(nm) - 12, 0.2, 0.4, 'bass')
    # gap motifs (melody only in gaps >= 0.25 s) [604]
    for gi in (16, 23, 30):
        g0, g1 = tl.gap_after(gi)
        if g1 - g0 > 0.2:
            seq.note(g0 + 0.03, 'celesta', N('A5'), 0.2, 0.5, 'lead')
            seq.note(g0 + 0.03 + beat / 3, 'celesta', N('F5'), 0.2, 0.42, 'lead')

    # "But here's the strange part." — drop out, then boom [714, 741]
    g0, g1 = tl.gap_after(45)
    H('reverse swell', reverse_swell(0.9, 1), g1 - 0.9 + 0.02, -9)
    H('low boom', low_boom(2, 44, 1.1), g0 + 0.02, -9)
    seq.note(S(8), 'pad', N('D3'), D(8), 0.22, 'pad')
    seq.note(S(8), 'pad', N('G#3'), D(8), 0.16, 'pad')                         # tritone unease

    # wonder: walk out + their story (Bb major lift)
    t9 = S(9)
    seq.note(t9, 'drone', N('A#1'), D(9) + D(10), 0.5, 'drone')
    arp = ['A#4', 'D5', 'F5', 'A5', 'F5', 'D5']
    t = t9 + 0.1
    k = 0
    while t < S(11) - 0.2:
        seq.note(t, 'celesta', N(arp[k % len(arp)]), 0.2, 0.32, 'lead')
        t += beat / 2
        k += 1
    sfx.add(sparkle(1.4, 3), t9 + 0.4, -20)
    sfx.add(sparkle(2.0, 4, 2093), S(10) + 0.2, -20)

    # sorrow: crying + flashback (G minor), slow music box
    seq.note(S(11), 'drone', N('G1'), D(11) + D(12) + D(13), 0.5, 'drone')
    for k, nm in enumerate(('D5', 'C5', 'A#4', 'A4', 'G4')):
        seq.note(S(11) + k * beat, 'celesta', N(nm), 0.4, 0.35, 'lead')
    sfx.add(lp(hum(D(12) + D(13), 38, 7), 400), S(12), -6)                     # car idle rumble
    sfx.add(snow_steps(1.6, 2.4, 8), S(12) + 0.1, -18)                          # wet steps
    H('colour sting', reverse_swell(0.5, 9) * 0.6, S(13) + 0.05, -14)
    H('colour shimmer', sparkle(0.6, 10, 1396.9), S(13) + 0.35, -18)

    # science: sneaky pizz + CCTV
    t14 = S(14)
    for k in range(int(D(14) / (beat / 2))):                                   # tiptoe pizz [618, 704]
        seq.note(t14 + k * beat / 2, 'pizz', N('D3') + (0, 1, 3, 1)[k % 4], 0.12, 0.35, 'bass')
    H('cctv click', cctv_click(11), t14 + 0.75, -10)
    # time-lapse: ticks accelerate through three hours
    t15, d15 = S(15), D(15)
    k = 0
    tt = t15
    while tt < t15 + d15 - 0.05:
        seq.note(tt, 'tick', 0, 0.03, 0.45, 'perc')
        k += 1
        tt += max(0.06, beat * (0.9 ** k))
    sfx.add(tape_whir(d15, True, 12), t15, -22)
    seq.note(t15, 'drone', N('D2'), d15 + D(16), 0.5, 'drone')

    # playback: rewind, then SILENCE before the reveal [741, 744]
    sfx.add(tape_whir(min(0.9, D(16)), False, 13), S(16) + D(16) - 0.95, -14)
    music_cut = (S(16) + D(16) - 0.5, S(17) + 0.05)

    # REVEAL: glitch + boom + dissonant cluster
    t17 = S(17)
    H('glitch', glitch(0.18, 14), t17 - 0.02, -8)
    H('reveal boom', low_boom(15, 40, 1.3), t17 - 0.02, -7)
    for nm in ('D3', 'D#3', 'G#3', 'A4'):
        seq.note(t17, 'pad', N(nm), D(17) + 0.3, 0.2, 'pad')
    sfx.add(glitch(0.12, 16), t17 + 1.0, -14)
    w0 = W(118)  # "whispering."
    g0, g1 = tl.gap_after(118)
    sfx.add(whisper_texture(g1 - w0 + 0.1, 17), w0, -24)                        # high-band only, under/after the word
    H('whispers', whisper_texture(max(0.3, g1 - g0 + 0.15), 18), g0, -16)

    # "So, be honest. Would you open the book?" — the music box, alone [654]
    t18 = S(18)
    for k, nm in enumerate(motif[:4]):
        seq.note(t18 + 0.05 + k * beat / 2, 'celesta', N(nm), 0.3, 0.42, 'lead')
    seq.note(t18, 'drone', D1, tl.total - t18, 0.5, 'drone')
    sfx.add(lp(creak(1.4, 110, 19), 1200), S(19) + 0.3, -16)                    # book cover creaks open, low band
    end = tl.we(len(tl.words) - 1)
    tb = end + 0.32                                                              # button >= 300 ms after last word [759]
    H('final boom', low_boom(20, 44, 1.2), tb, -6)
    H('final shimmer', sparkle(0.9, 21, 1174.7), tb + 0.02, -12)
    for nm in ('D4', 'A4', 'D5', 'F5'):
        seq.note(tb, 'celesta', N(nm), 0.6, 0.5, 'button')

    # ---- per-shot SFX
    sfx.add(fx.whoosh(0.8, 'down', 1.4, seed=30), max(0, S(1) - 0.6), -16)
    sfx.add(page_flip(31, 0.5), S(1) + 0.3 * D(1), -10)
    for k in range(6):
        sfx.add(paper_flutter(32 + k), S(2) + (0.1 + k * 0.13) * D(2), -16)
    sfx.add(snow_steps(D(2), 2.0, 33), S(2), -20)
    sfx.add(fx.whoosh(1.2, 'up', 1.4, seed=34), S(3) + 0.1, -18)
    sfx.add(lp(fx.thump(120, 0.4, 35), 1200), S(3) + 0.75, -16)                  # windows crossed out
    sfx.add(fx.pop(False, 1.0, 300, seed=36), S(3) + 1.45, -16)                  # empty plaque
    H('door thud', door_thud(37), S(4) - 0.05, -10)
    sfx.add(fx.pop(True, 1.0, 330, seed=38), S(4) + 1.05, -18)                   # empty bubble
    sfx.add(fx.pop(False, 1.0, 330, seed=39), S(4) + 1.6, -20)
    sfx.add(wood_steps(2, 2.4, 40), S(5) + 0.05, -16)
    sfx.add(lp(creak(0.5, 160, 41), 2000), S(6) + 0.1, -16)                      # book slides out
    sfx.add(lp(creak(0.4, 120, 42), 1500), S(7) + 0.05, -18)                     # chair
    sfx.add(page_flip(43, 0.4), S(7) + 0.4, -14)
    sfx.add(fx.pop(True, 1.0, 392, seed=44), S(7) + 1.0, -16)                    # "?" pop
    sfx.add(fx.heartbeat(56, 2) * 0.6, S(8) + 0.4, -14)
    sfx.add(lp(creak(0.5, 100, 45), 1500), S(8) + 0.6, -20)                      # librarian turns
    sfx.add(lp(door_thud(46), 1500), S(9) - 0.05, -18)
    sfx.add(snow_steps(D(9), 2.6, 47), S(9) + 0.2, -20)
    sfx.add(snow_steps(D(11), 1.8, 48), S(11), -20)
    sfx.add(hum(D(15) + D(17), 120, 49, 0.5), S(15), -16)
    return sfx, hero, amb, seq, music_cut


def main():
    meta = json.load(open(os.path.join(HERE, 'words.json')))
    words, total = meta['words'], meta['duration']
    bounds = scenes.install(words, total)
    tl = TL(words, total, bounds)
    n = int(SR * total)

    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(HERE, 'vo_blank_library.mp3'), '-ac', '1',
                          '-ar', str(SR), '-af', 'aresample=resampler=soxr', '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    vo = np.frombuffer(raw, np.float32).astype(float)
    vo = np.pad(vo, (0, max(0, n - len(vo))))[:n]           # UNPROCESSED voice

    log = []
    sfx, hero, amb, seq, music_cut = build(tl, n, log)

    def bus(name, g):
        return seq.get(name)[:n] * db(g)

    full = (bus('lead', -9) + bus('drone', -15) + bus('pad', -19) + bus('bass', -13) + bus('perc', -17))
    a, b = int(SR * music_cut[0]), int(SR * music_cut[1])
    full[a:b] *= np.linspace(1, 0, b - a) ** 3                # the drop-out before the reveal
    full = hp(full, 38)
    safe = lp(full, 1800)
    m = speech_mask(vo, tl, n)
    music = (full * (1 - m) + safe * m) * db(-13 * m) + bus('button', -10)
    sfx_x = (sfx.x * (1 - m) + lp(sfx.x, 3500) * m) * db(-8 * m)   # SFX under words: darker and lower
    amb_x = hp(amb.x, 80) * db(-28) * db(-8 * m)
    hero_x = hero.x * db(-10 * m)  # gap hits; tails duck hard once words return

    stems = {'vo': vo, 'music': music, 'sfx': sfx_x + hero_x, 'amb': amb_x}
    mixm = sum(stems.values())
    side = np.convolve(amb_x + 0.3 * music, np.r_[np.zeros(int(SR * 0.012)), 1], 'same') * 0.25
    st = np.stack([mixm + side, mixm - side], axis=1)
    for _ in range(3):
        st = st * db(-14 - lufs(st))
        st = limiter(st, -2.0)
    L = lufs(st)

    out = os.path.join(HERE, 'out')
    os.makedirs(os.path.join(out, 'stems'), exist_ok=True)
    sf.write(os.path.join(out, 'library_mix.wav'), st.astype(np.float32), SR, subtype='PCM_24')
    for k, v in stems.items():
        sf.write(os.path.join(out, 'stems', f'{k}.wav'), v.astype(np.float32), SR, subtype='PCM_24')
    json.dump({'hero_events': log, 'lufs': round(L, 2)}, open(os.path.join(out, 'stems', 'cue_log.json'), 'w'), indent=1)
    print(f'mix {total:.2f}s  {L:.2f} LUFS  peak {20 * np.log10(np.abs(st).max()):.2f} dBFS')


if __name__ == '__main__':
    main()
