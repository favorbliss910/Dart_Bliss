"""
Sound design for "Highway" — everything synthesized (no sample libraries needed).

High-retention rules applied (the important ones, grouped):
 VOICE   1 voice is king: everything ducks under it (sidechain)   2 HPF 80 Hz   3 cut mud ~300 Hz
         4 presence lift 3-5 kHz   5 de-ess   6 compress 3:1   7 consistent level
 MUSIC   8 score changes with every story act   9 music energy follows the tension curve
        10 tempo-locked (112 BPM) so hits land on beats   11 drop music out right before punchlines
        12 total silence before the big reveal ("It never comes")   13 triumphant lift after the twist
        14 sad/lo-fi palette for the low point (basement)   15 build + stinger at the end
 SFX    16 a whoosh on every scene change   17 an impact on every big reveal   18 a pop on every on-screen label
        19 risers lead into reveals   20 sub-drops under impacts   21 sound for every visible action
        22 comedic sounds for jokes (pizza, coffee, laughs)   23 Foley details (stopwatch, pencil, box thud)
        24 Doppler / panning for moving objects   25 stereo width on ambience, mono-ish centre for voice
 AMBIENCE 26 a bed for every location (traffic, chamber, basement hum, stream)   27 beds sit 20+ dB under voice
 MIX    28 no two loud things at once   29 short tails so it never gets muddy   30 limiter, -14 LUFS, -1 dBTP
"""
import json
import subprocess
from pathlib import Path

import numpy as np
import pyloudnorm as pyln
import soundfile as sf
from scipy import signal

HERE = Path(__file__).resolve().parent
SR = 48000
TL = json.loads((HERE / "timeline.json").read_text())
DUR = TL["duration"]
N = int(DUR * SR) + SR
B = TL["beats"]
SCN = {s["id"]: s for s in TL["scenes"]}
rng = np.random.default_rng(7)
BPM = 112
BEAT = 60 / BPM

# --------------------------------------------------------------------------- helpers
def t_arr(d):
    return np.arange(int(d * SR)) / SR

def env(d, a=0.005, r=0.1, curve=3.0):
    n = int(d * SR); e = np.ones(n)
    na, nr = max(1, int(a * SR)), max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] *= np.linspace(1, 0, nr) ** curve
    return e

def noise(d, color="white"):
    n = int(d * SR); x = rng.standard_normal(n)
    if color == "pink":
        x = signal.lfilter([0.049922035, -0.095993537, 0.050612699, -0.004408786], [1, -2.494956002, 2.017265875, -0.522189400], x)
    elif color == "brown":
        x = np.cumsum(x); x -= signal.savgol_filter(x, 4001 if n > 4001 else (n // 2) * 2 - 1, 2) if n > 10 else 0
    return x / (np.max(np.abs(x)) + 1e-9)

def bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, hi], "bandpass", fs=SR, output="sos"); return signal.sosfilt(sos, x)

def lp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, "lowpass", fs=SR, output="sos"), x)

def hp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, "highpass", fs=SR, output="sos"), x)

def sine(f, d, phase=0):
    t = t_arr(d); f = np.broadcast_to(f, t.shape) if np.ndim(f) else f
    return np.sin(2 * np.pi * np.cumsum(np.full(t.shape, f) if np.ndim(f) == 0 else f) / SR + phase)

def saw(f, d):
    t = t_arr(d); ph = np.cumsum(np.full(t.shape, f) if np.ndim(f) == 0 else f) / SR
    return 2 * (ph % 1) - 1

def square(f, d, duty=0.5):
    t = t_arr(d); ph = (np.cumsum(np.full(t.shape, f) if np.ndim(f) == 0 else f) / SR) % 1
    return np.where(ph < duty, 1.0, -1.0)

def mtof(m):
    return 440 * 2 ** ((m - 69) / 12)

def pan_st(x, p=0.0):
    p = np.clip(p, -1, 1); l = np.cos((p + 1) * np.pi / 4); r = np.sin((p + 1) * np.pi / 4)
    return np.stack([x * l, x * r], 1) if np.ndim(p) == 0 else np.stack([x * l, x * r], 1)

def reverb(x, size=0.4, wet=0.25):
    ir_len = int(SR * (0.3 + size * 1.5)); ir = rng.standard_normal(ir_len) * np.exp(-np.linspace(0, 6 / (0.3 + size), ir_len))
    ir = lp(ir, 6000); ir /= np.sqrt(np.sum(ir ** 2))
    if x.ndim == 1:
        return x * (1 - wet) + signal.fftconvolve(x, ir)[: len(x)] * wet
    ir2 = np.roll(ir, 211)
    return np.stack([x[:, 0] * (1 - wet) + signal.fftconvolve(x[:, 0], ir)[: len(x)] * wet,
                     x[:, 1] * (1 - wet) + signal.fftconvolve(x[:, 1], ir2)[: len(x)] * wet], 1)

class Bus:
    def __init__(self):
        self.x = np.zeros((N, 2))
    def add(self, sig, t, gain=1.0, pan=0.0):
        if sig.ndim == 1:
            sig = pan_st(sig, pan)
        i = int(t * SR)
        if i >= N: return
        j = min(N, i + len(sig)); self.x[i:j] += sig[: j - i] * gain

music, sfx, amb = Bus(), Bus(), Bus()

# --------------------------------------------------------------------------- SFX library
def whoosh(d=0.6, up=True):
    n = noise(d, "pink"); t = t_arr(d)
    f = np.linspace(300, 4000, len(t)) if up else np.linspace(4000, 300, len(t))
    out = np.zeros_like(n); blk = 1024
    for k in range(0, len(n), blk):
        fc = f[k]; out[k:k + blk] = bp(n[k:k + blk], max(80, fc * 0.6), min(20000, fc * 1.4), 1)
    e = np.sin(np.linspace(0, np.pi, len(t))) ** 1.5
    return out * e * 1.6

def impact(d=1.4, sub=48):
    t = t_arr(d)
    body = sine(sub * np.exp(-t * 3) + 28, d) * np.exp(-t * 3.5)
    crack = lp(noise(d), 3500) * np.exp(-t * 18)
    return body * 1.0 + crack * 0.6

def riser(d=2.0):
    t = t_arr(d); n = noise(d, "pink")
    out = np.zeros_like(n); f = np.geomspace(200, 9000, len(t)); blk = 1024
    for k in range(0, len(n), blk):
        out[k:k + blk] = bp(n[k:k + blk], f[k] * 0.7, min(20000, f[k] * 1.3), 1)
    tone = saw(np.geomspace(110, 880, len(t)), d) * 0.15
    return (out + lp(tone, 3000)) * (t / d) ** 2

def pop_sfx():
    d = 0.12; t = t_arr(d); return sine(np.linspace(900, 300, len(t)), d) * np.exp(-t * 40)

def click():
    d = 0.03; return hp(noise(d), 2000) * np.exp(-t_arr(d) * 200)

def tick():
    d = 0.05; t = t_arr(d); return (sine(3200, d) * 0.5 + hp(noise(d), 4000) * 0.5) * np.exp(-t * 120)

def ding(f=1318.5, d=1.8):
    t = t_arr(d); return sum(sine(f * h, d) * a * np.exp(-t * (2 + h)) for h, a in ((1, 1), (2.76, 0.4), (5.4, 0.15)))

def horn(d=0.5, f=(392, 466)):
    t = t_arr(d); x = sum(lp(square(fr, d, 0.4), 2500) for fr in f) * 0.4
    return x * env(d, 0.01, 0.06, 1)

def siren(d=2.5):
    t = t_arr(d); f = 900 + 350 * signal.sawtooth(2 * np.pi * 1.6 * t, 0.5)
    return lp(square(f, d, 0.5), 3000) * 0.35 * env(d, 0.05, 0.3)

def sad_trombone():
    out = []
    for i, (m, d) in enumerate(((58, 0.35), (57, 0.35), (56, 0.35), (55, 1.0))):
        t = t_arr(d); f = mtof(m) * (1 + 0.015 * np.sin(2 * np.pi * 6 * t) * (i == 3))
        out.append(lp(saw(f, d), 1500) * env(d, 0.02, 0.1 if i < 3 else 0.5, 1))
    return np.concatenate(out) * 0.5

def glass_crack():
    d = 0.8; t = t_arr(d); return hp(noise(d), 2500) * np.exp(-t * 9) * (1 + 0.6 * np.sign(np.sin(2 * np.pi * 37 * t)))

def laugh(d=2.0, voices=7):
    out = np.zeros(int(d * SR))
    for v in range(voices):
        f0 = rng.uniform(120, 260); rate = rng.uniform(4.5, 6.5); st = rng.uniform(0, 0.3)
        t = t_arr(d); gate = (np.sin(2 * np.pi * rate * t + v) > 0.2).astype(float); gate = lp(gate, 30)
        voc = saw(f0 * (1 + 0.04 * np.sin(2 * np.pi * 3 * t)), d)
        form = bp(voc, 600, 1300) + 0.6 * bp(voc, 1600, 2600)
        breath = bp(noise(d), 900, 3000) * 0.3
        seg = (form + breath) * gate * np.exp(-t * rng.uniform(0.4, 0.9))
        i = int(st * SR); out[i:] += seg[: len(out) - i]
    return out / (np.max(np.abs(out)) + 1e-9)

def splash():
    d = 0.7; t = t_arr(d); return bp(noise(d), 400, 5000) * (np.exp(-t * 8) + 0.3 * np.exp(-((t - 0.15) * 30) ** 2))

def paper_flip():
    d = 0.25; t = t_arr(d); return bp(noise(d), 1500, 8000) * np.exp(-t * 18)

def scribble(d=1.5):
    t = t_arr(d); g = (np.sin(2 * np.pi * 7 * t) > -0.3).astype(float)
    return bp(noise(d), 2500, 7000) * lp(g, 40) * 0.6

def static(d=1.0):
    return bp(noise(d), 1500, 7000) * 0.5 * env(d, 0.02, 0.2, 1)

def buzzer(d=0.45):
    return lp(square(110, d, 0.5) + square(116, d, 0.5), 2000) * 0.4 * env(d, 0.005, 0.05, 1)

def beep_reverse(n=4):
    out = []
    for _ in range(n):
        out.append(sine(1000, 0.25) * 0.4 * env(0.25, 0.005, 0.02, 1)); out.append(np.zeros(int(0.25 * SR)))
    return np.concatenate(out)

def thud():
    d = 0.6; t = t_arr(d); return sine(70 * np.exp(-t * 6) + 40, d) * np.exp(-t * 9) + lp(noise(d), 900) * np.exp(-t * 25) * 0.6

def water_burst(d=3.0):
    t = t_arr(d); n = noise(d, "pink"); r = bp(n, 200, 9000) * (1 - np.exp(-t * 8)) * np.exp(-t * 0.5)
    im = impact(1.2, 40); r[: len(im)] += im * 0.8
    return r

def clank():
    d = 0.5; t = t_arr(d); return sum(sine(f, d) * np.exp(-t * 10) for f in (523, 1240, 2210)) * 0.4 + hp(noise(d), 3000) * np.exp(-t * 40) * 0.3

def thunder(d=3.5):
    t = t_arr(d); return lp(noise(d, "brown"), 300) * np.exp(-t * 1.2) * (1 + 0.5 * np.sin(2 * np.pi * 3 * t)) + lp(noise(d), 1500) * np.exp(-t * 6) * 0.4

def explosion(d=4.0):
    t = t_arr(d); return lp(noise(d, "brown"), 400) * np.exp(-t * 1.0) * 1.2 + impact(d, 36) * 1.0 + bp(noise(d), 500, 6000) * np.exp(-t * 3) * 0.5

def heartbeat():
    d = 0.8; t = t_arr(d); h = lambda o: sine(55, d) * np.exp(-((t - o) * 30) ** 2)
    return (h(0.05) + 0.7 * h(0.28)) * 1.2

def sizzle(d):
    t = t_arr(d); return hp(noise(d), 3000) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 11 * t))) * 0.35

def stopwatch_click():
    return click() * 1.2 + np.pad(click(), (int(0.06 * SR), 0))[: int(0.09 * SR)] * 0.8 if False else np.concatenate([click(), np.zeros(int(0.05 * SR)), click() * 0.7])

# --------------------------------------------------------------------------- ambience beds
def bed(kind, d):
    if kind == "traffic":
        x = lp(noise(d, "brown"), 250) * 0.6 + bp(noise(d, "pink"), 300, 2500) * 0.12
        stereo = np.stack([x, np.roll(x, 2400)], 1)
        return stereo
    if kind == "chamber":
        x = lp(noise(d, "pink"), 1200) * 0.15; return np.stack([x, np.roll(x, 1800)], 1)
    if kind == "basement":
        t = t_arr(d); x = sine(60, d) * 0.25 + sine(120, d) * 0.12 + bp(noise(d), 3000, 6000) * 0.05
        return np.stack([x, x], 1)
    if kind == "stream":
        x = bp(noise(d, "pink"), 800, 6000) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 0.3 * t_arr(d))))
        return np.stack([x, np.roll(x, 3000)], 1) * 0.5
    if kind == "construction":
        x = lp(noise(d, "brown"), 180) * 0.6; t = t_arr(d)
        x += lp(square(26, d, 0.5), 400) * 0.08 * (np.sin(2 * np.pi * 0.25 * t) > 0)
        return np.stack([x, np.roll(x, 1200)], 1)
    if kind == "night":
        x = lp(noise(d, "pink"), 800) * 0.1; return np.stack([x, np.roll(x, 2000)], 1)

def fade(st, a=0.4, r=0.6):
    n = len(st); e = np.ones(n); na, nr = int(a * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na); e[-nr:] = np.linspace(1, 0, nr)
    return st * e[:, None]

# --------------------------------------------------------------------------- MUSIC (procedural score, 112 BPM)
def pluck(m, d=0.4, bright=3000):
    t = t_arr(d); f = mtof(m)
    x = (saw(f, d) * 0.6 + square(f * 1.003, d, 0.3) * 0.3); x = lp(x, bright) * np.exp(-t * 7)
    return x

def pad(chord, d, cutoff=1500):
    t = t_arr(d); x = sum(saw(mtof(m) * (1 + dt), d) for m in chord for dt in (-0.004, 0.004)) / (len(chord) * 2)
    return lp(x, cutoff) * env(d, 0.6, 0.8, 1)

def bass(m, d):
    t = t_arr(d); return lp(saw(mtof(m), d), 700) * np.exp(-t * 3) * 0.9 + sine(mtof(m), d) * 0.4 * np.exp(-t * 2)

def kick():
    d = 0.35; t = t_arr(d); return sine(120 * np.exp(-t * 25) + 45, d) * np.exp(-t * 9)

def hat(open_=False):
    d = 0.2 if open_ else 0.05; t = t_arr(d); return hp(noise(d), 7000) * np.exp(-t * (15 if open_ else 80)) * 0.4

def snare():
    d = 0.25; t = t_arr(d); return (bp(noise(d), 1500, 7000) * 0.7 + sine(190, d) * 0.4) * np.exp(-t * 18)

def section(start, end, style):
    """Render a music section between [start,end] with a given style onto the music bus."""
    d = end - start
    nb = int(d / BEAT)
    if style == "tense":  # hook: low pulses + riser
        for k in range(nb * 2):
            music.add(bass(33, BEAT / 2) * 0.7, start + k * BEAT / 2)
        music.add(pad([45, 48, 52], d, 900) * 0.5, start)
    elif style == "quirky":  # jam: staccato plucks, bouncy bass, light drums
        prog = [(50, [62, 65, 69]), (55, [62, 67, 71]), (48, [60, 64, 67]), (53, [60, 65, 69])]
        for k in range(nb):
            root, ch = prog[(k // 4) % 4]; tt = start + k * BEAT
            music.add(bass(root - 12, BEAT * 0.9) * 0.8, tt)
            if k % 2 == 0: music.add(kick() * 0.9, tt)
            else: music.add(snare() * 0.5, tt)
            music.add(hat(), tt + BEAT / 2)
            for j, m in enumerate(ch):
                music.add(pluck(m + 12, 0.25, 4000) * 0.25, tt + (j * BEAT / 3 if k % 2 else BEAT / 2), pan=(j - 1) * 0.4)
    elif style == "mystery":  # engineer/sidestreets: minor plucks + ticking
        prog = [[57, 60, 64], [53, 57, 60], [55, 59, 62], [52, 56, 59]]
        for k in range(nb):
            tt = start + k * BEAT; ch = prog[(k // 4) % 4]
            music.add(tick() * 0.5, tt); music.add(tick() * 0.3, tt + BEAT / 2)
            music.add(pluck(ch[k % 3] + 12, 0.5, 2500) * 0.3, tt + BEAT / 4, pan=0.3 * np.sin(k))
            if k % 4 == 0: music.add(pad(ch, BEAT * 4, 1100) * 0.35, tt); music.add(bass(ch[0] - 24, BEAT * 2) * 0.6, tt)
    elif style == "playful":  # city hall / famous
        prog = [(48, [64, 67, 72]), (53, [65, 69, 72]), (55, [62, 67, 71]), (48, [64, 67, 72])]
        for k in range(nb):
            root, ch = prog[(k // 4) % 4]; tt = start + k * BEAT
            music.add(bass(root - 12 + (7 if k % 2 else 0), BEAT * 0.8) * 0.8, tt)
            if k % 2 == 0: music.add(kick(), tt)
            music.add(hat(k % 4 == 3), tt + BEAT / 2)
            if k % 2 == 1: music.add(snare() * 0.4, tt)
            music.add(pluck(ch[(k * 2) % 3] + 12, 0.2, 5000) * 0.22, tt + BEAT / 2, pan=0.5)
            music.add(pluck(ch[(k * 2 + 1) % 3] + 12, 0.2, 5000) * 0.2, tt + 3 * BEAT / 4, pan=-0.5)
    elif style == "suspense":  # weird: rising pad + pulse
        for k in range(nb * 2):
            music.add(pluck(45 + (k // 8), 0.2, 1800) * 0.35, start + k * BEAT / 2)
        music.add(pad([45, 52, 57, 60], d, 1400) * 0.45, start)
        music.add(riser(min(3.0, d)) * 0.35, end - min(3.0, d))
    elif style == "sad":  # basement
        prog = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [52, 55, 59]]
        for k in range(0, nb, 4):
            tt = start + k * BEAT; ch = prog[(k // 4) % 4]
            music.add(pad(ch, BEAT * 4.2, 900) * 0.5, tt)
            for j in range(4): music.add(pluck(ch[j % 3] + 12, 0.9, 1400) * 0.22, tt + j * BEAT)
        # vinyl crackle = lo-fi sadness
        cr = (rng.random(int(d * SR)) > 0.9993).astype(float) * rng.uniform(0.2, 1, int(d * SR)); music.add(hp(cr, 2000) * 0.25, start)
    elif style == "build":  # burst: heartbeat + drones + risers
        music.add(pad([38, 45, 50], d, 600) * 0.6, start)
        for k in range(int(d / 0.9)):
            music.add(heartbeat() * (0.4 + 0.6 * k / max(1, d / 0.9)), start + k * 0.9)
    elif style == "triumph":  # flow: major, driving
        prog = [(48, [60, 64, 67]), (55, [62, 67, 71]), (57, [60, 64, 69]), (53, [60, 65, 69])]
        for k in range(nb):
            root, ch = prog[(k // 4) % 4]; tt = start + k * BEAT
            music.add(kick(), tt); music.add(hat(), tt + BEAT / 2)
            if k % 2: music.add(snare() * 0.6, tt)
            music.add(bass(root - 12, BEAT * 0.9), tt)
            if k % 4 == 0: music.add(pad([m + 12 for m in ch], BEAT * 4, 3000) * 0.45, tt)
            music.add(pluck(ch[k % 3] + 24, 0.25, 6000) * 0.18, tt + BEAT / 4)
    elif style == "think":  # explainer: light groove
        prog = [(50, [62, 65, 69]), (46, [62, 65, 70]), (48, [60, 64, 67]), (45, [60, 64, 69])]
        for k in range(nb):
            root, ch = prog[(k // 4) % 4]; tt = start + k * BEAT
            if k % 2 == 0: music.add(kick() * 0.7, tt)
            music.add(hat() * 0.7, tt + BEAT / 2)
            music.add(bass(root - 12, BEAT * 0.7) * 0.6, tt)
            music.add(pluck(ch[k % 3] + 12, 0.35, 3000) * 0.22, tt + BEAT / 2, pan=0.4 * ((k % 2) * 2 - 1))
    elif style == "finale":
        music.add(pad([50, 57, 62, 66], d, 2500) * 0.55, start)
        for k in range(nb):
            music.add(kick() * 0.9, start + k * BEAT)
            music.add(pluck([62, 66, 69, 74][k % 4] + 12, 0.3, 6000) * 0.2, start + k * BEAT + BEAT / 2)

S = lambda i: SCN[i]["start"]
E = lambda i: SCN[i]["end"]
section(0, S("skyway"), "tense")
section(S("skyway"), E("jam"), "quirky")
section(S("engineer"), E("sidestreets"), "mystery")
section(S("cityhall"), B["samecars"] - 0.15, "playful")       # drop out before the punchline
section(B["samecars"] + 1.6, E("famous"), "playful")
section(S("weird"), E("weird"), "suspense")
section(S("doubles"), B["basement"], "quirky")
section(B["basement"], E("doubles"), "sad")
section(S("burst"), S("flow") - 0.7, "build")                 # silence before the reveal
section(S("flow") + 1.1, E("flow"), "triumph")
section(S("braess"), E("braess"), "think")
section(B["seoul"], B["blowingup"] - 0.2, "finale")

# --------------------------------------------------------------------------- SFX cues
for s in TL["scenes"][1:]:
    sfx.add(whoosh(0.55), s["start"] - 0.3, 0.55)                       # every cut gets a whoosh

cue = sfx.add
cue(riser(2.0), B["blowup"] - 2.0 + 0.4, 0.5)
cue(impact(1.6), B["blowup"] + 0.05, 0.9)
cue(sizzle(SCN["hook"]["end"] - B["blowup"]), B["blowup"], 0.5, 0.3)
for k in range(int((SCN["hook"]["end"] - B["blowup"]) / 0.5)): cue(tick(), B["blowup"] + 0.3 + k * 0.5, 0.35)
for k in range(10): cue(clank() * 0.5, S("skyway") + 0.2 + k * 0.24, 0.35, -0.8 + k * 0.16)   # skyway being built
cue(pop_sfx(), B["sixlanes"], 0.6)
cue(whoosh(0.5, False), B["shortcut1"] - 0.25, 0.5); cue(thud(), B["shortcut1"] + 0.3, 0.6)
for k, p in enumerate((-0.6, 0.5, -0.2, 0.7, -0.8)): cue(horn(0.35 + 0.1 * (k % 2), (370 + k * 20, 440 + k * 25)), S("jam") + 0.3 + k * 0.45, 0.35, p)
for k in range(8): cue(tick() * 0.6, S("jam") + 0.2 + k * 0.25, 0.4)
sir = siren(2.8); dop = np.linspace(-1, 0.2, len(sir)); cue(np.stack([sir * np.cos((dop + 1) * np.pi / 4), sir * np.sin((dop + 1) * np.pi / 4)], 1), B["ambulance"], 0.5)
cue(sad_trombone(), B["pizza"] + 0.1, 0.55)
cue(glass_crack(), B["marriage"] + 0.15, 0.6)
cue(pop_sfx(), B["marriage"], 0.5)
for k in range(6): cue(np.concatenate([click(), np.zeros(int(0.12 * SR))]) * 0.7, B["bridge"] - 2.5 + k * 0.45, 0.4, -0.4 + 0.15 * k)  # footsteps
cue(stopwatch_click(), B["stopwatch"] + 0.3, 0.8)
cue(scribble(1.4), B["stopwatch"] + 1.6, 0.5, 0.3)
for k in range(4): cue(pop_sfx() * 0.8, B["sidestreets"] + 1.2 + k * 0.25, 0.45, -0.6 + 0.4 * k)
cue(paper_flip(), B["weirdthing"] + 0.4, 0.7); cue(scribble(2.2), B["everydriver"], 0.55)
cue(paper_flip() * 0.8, B["tear"], 0.7); cue(impact(0.9, 60) * 0.6, B["tear"] + 0.15, 0.5)
cue(laugh(2.2), B["laughs"], 0.55); cue(splash(), B["coffee"] + 0.3, 0.7, 0.4)
cue(sine(2600, 0.5) * 0.15 * env(0.5, 0.05, 0.2), B["greatidea"] + 0.2, 0.4)                   # mic feedback
cue(pop_sfx(), B["greatidea"] + 1.4, 0.6); cue(pop_sfx(), B["hunger"], 0.5)
cue(ding(1567.98), B["samecars"], 0.6); cue(impact(1.0, 55) * 0.5, B["samecars"], 0.5)
for k in range(10): cue(paper_flip() * 0.6, S("famous") + k * 0.1, 0.45)                          # calendar
cue(whoosh(0.7), B["newspaper"] - 0.4, 0.6); cue(thud() * 0.6, B["newspaper"] + 0.3, 0.6)
cue(static(1.4), B["radio"], 0.4)
for k, p in enumerate((-0.7, 0.4, -0.2, 0.7, 0.0)): cue(horn(0.4, (330 + 30 * k, 415 + 20 * k)), B["honk"] + 0.25 + k * 0.35, 0.45, p)
cue(buzzer(), B["doesnt"], 0.55)
cue(pop_sfx(), B["sametraffic"] + 0.2, 0.5); cue(ding(1318.5), B["faster"] + 0.1, 0.45)
cue(impact(1.0, 50) * 0.6, B["howpossible"] + 0.1, 0.5)
cue(pop_sfx(), B["widen"], 0.6); cue(beep_reverse(5), B["cranes"], 0.25, 0.5)
cue(sine(1200, 0.12) * 0.3, B["basement"] + 0.2, 0.6)                                             # light flicker blip
cue(thud(), B["box"] + 0.3, 1.0); cue(impact(0.8, 45) * 0.5, B["box"] + 0.3, 0.6)
cue(paper_flip(), B["skywaywon"], 0.7); cue(impact(1.2, 45) * 0.6, B["skywaywon"] + 0.05, 0.5)
cue(riser(1.0) * 0.6, B["watermain"] - 0.8, 0.5); cue(water_burst(3.0), B["watermain"] + 0.05, 0.8)
for k in range(4): cue(clank(), B["shutdown"] + k * 0.12, 0.55, -0.6 + 0.4 * k)
for k in range(16): cue(tick() * 0.6, B["cars160"] + k * 0.1, 0.4)
cue(impact(1.4, 40), B["noshortcut"] + 0.2, 0.75)
cue(thunder(), B["braces"] + 0.5, 0.6); cue(riser(2.0) * 0.8, S("flow") - 2.6, 0.5)
cue(impact(2.0, 34), S("flow") + 0.9, 0.7)                                                          # reveal after the silence
cue(whoosh(0.8, True), B["spill"], 0.5)
amb_s = siren(1.6); dp = np.linspace(-0.9, 0.9, len(amb_s)); cue(np.stack([amb_s * np.cos((dp + 1) * np.pi / 4), amb_s * np.sin((dp + 1) * np.pi / 4)], 1) * 0.7, B["arriveearly"], 0.45)
cue(ding(1760), B["fifteen"] + 0.3, 0.55)
cue(stopwatch_click() * 1.5, B["click"] + 0.5, 0.9); cue(ding(1046.5, 2.5) * 0.4, B["click"] + 0.6, 0.4)
cue(pop_sfx(), B["fastestthem"] + 0.2, 0.4); cue(buzzer(0.3) * 0.6, B["everyone"] + 0.1, 0.35)
cue(riser(1.4) * 0.5, B["piles"] - 0.6, 0.4); cue(impact(0.8, 55) * 0.4, B["piles"] + 0.6, 0.4)
cue(glass_crack() * 0.6, B["takeaway"] + 0.15, 0.5); cue(ding(1567.98), B["takeaway"] + 0.6, 0.5)
cue(laugh(2.5, 14) * 0.25, B["stadium"] + 0.3, 0.45)                                                 # crowd
cue(whoosh(0.6), B["sidedoors"] + 0.2, 0.5)
cue(impact(1.6, 40), B["paradox"] + 0.1, 0.85); cue(ding(880, 2.5) * 0.5, B["paradox"] + 0.15, 0.4)
cue(whoosh(0.9), B["seoul"] + 0.5, 0.6)
cue(ding(1318.5) * 0.7, B["stream"] + 1.0, 0.5)
cue(riser(1.3), B["blowingup"] - 1.1, 0.6); cue(explosion(4.5), B["blowingup"] + 0.05, 1.0)

# ambience beds per location (sit well under the voice)
for kind, a, b, g in (("traffic", 0, S("engineer") + 9.6, 0.13), ("chamber", S("cityhall"), E("cityhall"), 0.12), ("night", S("famous"), E("famous"), 0.1),
                      ("construction", S("doubles"), B["basement"], 0.14), ("basement", B["basement"], E("doubles"), 0.12),
                      ("traffic", S("burst"), B["shutdown"], 0.12), ("traffic", S("flow") + 0.9, E("flow"), 0.1), ("stream", B["seoul"], B["fastestway"], 0.18)):
    amb.add(fade(bed(kind, b - a)), a, g)

# --------------------------------------------------------------------------- voice chain (ffmpeg) + mix
vo_path = HERE / "voiceover.wav"
proc = HERE / "vo_processed.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(vo_path), "-af",
                "highpass=f=80,equalizer=f=300:t=q:w=1.2:g=-3,equalizer=f=4000:t=q:w=1.0:g=3,deesser=i=0.4,"
                "acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=4,aresample=48000",
                "-ac", "1", str(proc)], check=True)
vo, _ = sf.read(proc)
voice = np.zeros(N); voice[: len(vo)] = vo[:N]

# sidechain: duck music & beds when the voice is talking
envv = np.abs(signal.hilbert(lp(voice, 1000)))
envv = lp(envv, 6)
envv = np.clip(envv / (np.percentile(envv, 95) + 1e-9), 0, 1)
duck = 1 - 0.62 * envv            # ~ -8.5 dB under speech
music.x *= duck[:, None]
amb.x *= (1 - 0.45 * envv)[:, None]

music.x = reverb(music.x, 0.35, 0.18)
sfx.x = reverb(sfx.x, 0.25, 0.12)

def norm(x, peak=1.0):
    m = np.max(np.abs(x)) + 1e-9; return x / m * peak

mix = (pan_st(voice, 0) * 1.0 * np.sqrt(2) * 0.5 / (np.max(np.abs(voice)) + 1e-9) * 1.4
       + norm(music.x) * 0.22 + norm(sfx.x) * 0.5 + norm(amb.x) * 0.10)
mix = mix[: int(DUR * SR)]

# loudness -14 LUFS, soft limiter, true-peak headroom
meter = pyln.Meter(SR)
mix = pyln.normalize.loudness(mix, meter.integrated_loudness(mix), -14.0)
for _ in range(3):  # limiter + re-normalize until loudness and peak both sit right
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    mix = pyln.normalize.loudness(mix, meter.integrated_loudness(mix), -14.0)
mix = np.clip(mix, -0.89, 0.89)
sf.write(HERE / "soundtrack_final.wav", mix.astype(np.float32), SR, subtype="PCM_24")
print("LUFS:", round(meter.integrated_loudness(mix), 2), "peak:", round(float(np.max(np.abs(mix))), 3), "dur:", round(len(mix) / SR, 2))
