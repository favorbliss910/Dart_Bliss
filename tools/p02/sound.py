"""Stage 8 for P02: all sound is generated here in code (no samples), timed from the exported events.

Inputs : manifests/p02_audio_timing.json, manifests/p02_events/<shot>.json, assets/audio/p02/<shot>_line.wav
Outputs: assets/audio/p02/{dialogue,ambience,foley,fx,music,mix}.wav (48 kHz, 24-bit) and loudness in
         manifests/p02_audio_timing.json["mix"]
"""
import json
import os
import subprocess

import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SR, FPS = 48000, 24
rng = np.random.default_rng(11)
timing = json.load(open(os.path.join(ROOT, "manifests", "p02_audio_timing.json")))
TOTAL = timing["total_frames"] / FPS
N = int(round(TOTAL * SR))
OUT = os.path.join(ROOT, "assets", "audio", "p02")
start_s = {s["id"]: s["film_start_s"] for s in timing["shots"]}


def db(x):
    return 10 ** (x / 20)


def fft_filter(x, lo=None, hi=None, tilt=0.0):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = np.ones_like(f)
    if lo:
        g *= 1 / np.sqrt(1 + (lo / np.maximum(f, 1)) ** 4)
    if hi:
        g *= 1 / np.sqrt(1 + (f / hi) ** 4)
    if tilt:
        g *= (np.maximum(f, 20) / 1000) ** (tilt / 6.0206)
    return np.fft.irfft(X * g, n=len(x))


def smooth_gate(g, ms=40):
    k = int(SR * ms / 1000)
    ker = np.ones(k) / k
    return np.convolve(g, ker, mode="same")


def place(buf, clip, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= len(buf) or i < 0:
        return
    clip = clip[: len(buf) - i]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[i:i + len(clip), 0] += clip * gain * l
    buf[i:i + len(clip), 1] += clip * gain * r


def env(n, a=0.005, d=8.0):
    x = np.arange(n) / SR
    return np.minimum(1, x / a) * np.exp(-x * d)


def norm(x):
    return x / (np.max(np.abs(x)) + 1e-9)


def noise(sec):
    return rng.standard_normal(int(SR * sec))


def tone(f0, sec, decay=6.0, partials=((1, 1.0),)):
    x = np.arange(int(SR * sec)) / SR
    y = sum(a * np.sin(2 * np.pi * f0 * m * x) for m, a in partials)
    return y * env(len(x), 0.004, decay)


def sweep(f0, f1, sec, shape="exp"):
    n = int(SR * sec)
    f = np.geomspace(f0, f1, n) if shape == "exp" else np.linspace(f0, f1, n)
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


# ------------------------------------------------------------------ sound designs
def s_click():
    return norm(fft_filter(noise(0.03), 1500, 9000) * env(int(SR * 0.03), 0.0005, 120) + tone(2200, 0.03, 90) * 0.5)


def s_tone(f):
    return norm(tone(f, 0.35, 9, ((1, 1), (2, 0.25), (3, 0.08))))


def s_powerdown():
    n = int(SR * 0.9)
    return norm(sweep(900, 70, 0.9) * np.linspace(1, 0, n) ** 1.5)


def s_shimmer():
    out = np.zeros(int(SR * 0.8))
    for _ in range(24):
        f = rng.uniform(2500, 7000)
        t = rng.uniform(0, 0.4)
        c = tone(f, 0.35, 14) * rng.uniform(0.3, 1)
        i = int(t * SR)
        out[i:i + len(c)] += c[: len(out) - i]
    return norm(out)


def s_swell(sec=1.6, f=110):
    n = int(SR * sec)
    x = np.arange(n) / SR
    y = (np.sin(2 * np.pi * f * x) + 0.5 * np.sin(2 * np.pi * 2.01 * f * x) + 0.25 * np.sin(2 * np.pi * 3.02 * f * x))
    return norm(y * np.sin(np.pi * x / sec) ** 2)


def s_machine_on():
    n = int(SR * 1.2)
    x = np.arange(n) / SR
    thrum = np.sin(2 * np.pi * 50 * x) * (1 - np.exp(-x * 6))
    wh = sweep(180, 420, 1.2) * 0.4 * np.minimum(1, x / 0.3)
    return norm((thrum + wh) * np.minimum(1, (1.2 - x) / 0.3))


def s_knock():
    n = int(SR * 0.06)
    return norm(fft_filter(rng.standard_normal(n), 800, 3500) * env(n, 0.0005, 70) + tone(320, 0.06, 60))


def s_thud(f=60, sec=0.5, bright=0.3):
    n = int(SR * sec)
    return norm(tone(f, sec, 9) + bright * fft_filter(rng.standard_normal(n), 200, 2000) * env(n, 0.001, 25))


def s_creak(sec=0.7):
    n = int(SR * sec)
    x = np.arange(n) / SR
    fm = 140 + 40 * np.sin(2 * np.pi * 3 * x)
    y = np.sign(np.sin(2 * np.pi * np.cumsum(fm) / SR)) * 0.4
    return norm(fft_filter(y + 0.3 * rng.standard_normal(n), 200, 2500) * np.sin(np.pi * x / sec))


def s_ratchet(sec):
    out = np.zeros(int(SR * max(sec, 0.1)))
    t = 0.0
    while t < sec - 0.03:
        c = s_click() * 0.6
        i = int(t * SR)
        out[i:i + len(c)] += c[: len(out) - i]
        t += 0.045
    return out


def s_bolt():
    n = int(SR * 0.6)
    x = np.arange(n) / SR
    y = sum(a * np.sin(2 * np.pi * f * x) * np.exp(-x * d) for f, a, d in ((310, 1, 9), (730, 0.6, 12), (1130, 0.4, 16), (1790, 0.2, 22)))
    return norm(y + s_thud(70, 0.6, 0.5)[:n])


def s_whine(sec):
    n = int(SR * sec)
    x = np.arange(n) / SR
    return norm(sweep(300, 1400, sec) * np.minimum(1, x / 0.2) * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * x)))


def s_buzz(sec=0.45, f=110):
    n = int(SR * sec)
    x = np.arange(n) / SR
    y = np.sign(np.sin(2 * np.pi * f * x))
    return norm(fft_filter(y, 80, 3000) * np.minimum(1, x / 0.01) * np.minimum(1, (sec - x) / 0.03))


def s_rip():
    n = int(SR * 0.4)
    x = np.arange(n) / SR
    jag = np.clip(np.abs(rng.standard_normal(n // 200)), 0, 2.5).repeat(200)[:n]
    return norm(fft_filter(rng.standard_normal(n), 900, 7000) * jag * np.minimum(1, x / 0.01) * np.exp(-x * 4))


def s_roll(sec):
    n = int(SR * sec)
    x = np.arange(n) / SR
    y = fft_filter(rng.standard_normal(n), 40, 350) * (0.7 + 0.3 * np.sin(2 * np.pi * 9 * x))
    sq = sweep(2400, 2700, sec) * 0.08 * (np.sin(2 * np.pi * 1.3 * x) > 0.6)
    return norm((y + sq) * np.minimum(1, x / 0.15) * np.minimum(1, (sec - x) / 0.15))


def s_beep():
    return norm(tone(1250, 0.14, 6) * np.minimum(1, (0.14 - np.arange(int(SR * 0.14)) / SR) / 0.01))


def s_warning():
    a = tone(880, 0.32, 3, ((1, 1), (2, 0.2)))
    b = tone(660, 0.5, 3, ((1, 1), (2, 0.2)))
    return norm(np.concatenate([a, b]))


def s_glitter(sec):
    out = np.zeros(int(SR * (sec + 0.5)))
    for _ in range(int(40 * sec)):
        c = tone(rng.uniform(3000, 9000), 0.15, 30) * rng.uniform(0.2, 1)
        i = int(rng.uniform(0, sec) * SR)
        out[i:i + len(c)] += c[: len(out) - i]
    return norm(out)


def s_bonded():
    return norm(s_thud(55, 0.7, 0.2) + sweep(600, 200, 0.7)[: int(SR * 0.7)] * 0.3 * env(int(SR * 0.7), 0.002, 4))


def s_rise(sec):
    n = int(SR * sec)
    x = np.arange(n) / SR
    y = fft_filter(rng.standard_normal(n), 300, 3000) * 0.4 + sweep(90, 260, sec) * 0.7
    return norm(y * (x / sec) ** 1.5)


def s_whoosh(sec=0.8, down=True):
    n = int(SR * sec)
    x = np.arange(n) / SR
    y = rng.standard_normal(n)
    out = np.zeros(n)
    k = 8
    for i in range(k):
        seg = slice(i * n // k, (i + 1) * n // k)
        f = 4000 * (1 - i / k) + 300 if down else 300 + 4000 * i / k
        out[seg] = fft_filter(y, f * 0.6, f * 1.6)[seg]
    return norm(out * np.sin(np.pi * x / sec))


def s_step(run=False, wet=False):
    n = int(SR * 0.16)
    x = np.linspace(0, 1, n)
    th = np.sin(2 * np.pi * 95 * x * 0.16) * np.exp(-x * 30)
    slap = fft_filter(rng.standard_normal(n), 900, 6000) * np.exp(-x * 26)
    s = th * 0.9 + slap * (0.55 if run else 0.4)
    if wet:
        s += fft_filter(rng.standard_normal(n), 2500, 11000) * np.exp(-((x - 0.12) ** 2) / 0.004) * 0.6
    return norm(s)


def s_scrape():
    n = int(SR * 1.1)
    x = np.arange(n) / SR
    y = fft_filter(rng.standard_normal(n), 600, 5000) * (0.5 + 0.5 * np.sin(2 * np.pi * 11 * x) ** 2)
    rattle = sum(tone(f, 1.1, 3) for f in (520, 1380, 2210))[:n] * 0.4
    return norm((y + rattle) * np.exp(-x * 2.2))


def s_flutter():
    n = int(SR * 1.6)
    x = np.arange(n) / SR
    y = fft_filter(rng.standard_normal(n), 1500, 9000) * (np.sin(2 * np.pi * 14 * x) > 0.2)
    return norm(y * np.exp(-x * 1.6))


def s_lever():
    b = s_bolt() * 0.8
    t = np.pad(tone(240, 0.5, 5, ((1, 1), (2.7, 0.4))), (int(SR * 0.05), len(b)))[: len(b)]
    return norm(b + t)


def s_groan(sec=1.4):
    n = int(SR * sec)
    x = np.arange(n) / SR
    f = 70 + 15 * np.sin(2 * np.pi * 0.9 * x)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(2 * np.pi * np.cumsum(f * 2.03) / SR)
    return norm(y * np.sin(np.pi * x / sec))


def s_gasp():
    n = int(SR * 0.45)
    x = np.arange(n) / SR
    return norm(fft_filter(rng.standard_normal(n), 700, 4500) * np.sin(np.pi * np.minimum(1, x / 0.45)) ** 2)


def s_boom():
    n = int(SR * 3.0)
    x = np.arange(n) / SR
    low = sweep(90, 30, 3.0) * np.exp(-x * 1.6)
    burst = fft_filter(rng.standard_normal(n), 100, 8000) * np.exp(-x * 7)
    ring = np.sin(2 * np.pi * 3950 * x) * 0.06 * np.minimum(1, x / 0.3) * np.exp(-x * 1.2)
    return norm(low + 0.6 * burst + ring)


# ------------------------------------------------------------------ stems
dialogue = np.zeros((N, 2))
amb = np.zeros((N, 2))
foley = np.zeros((N, 2))
fx = np.zeros((N, 2))
music = np.zeros((N, 2))
alarm_g = np.zeros(N)
water_g = np.zeros(N)
holo_g = np.zeros(N)
muffle_g = np.zeros(N)       # 1 where the camera is outside the soundproof lab
silence_g = np.ones(N)       # dips to 0 for the "soundproof" beat
duck = np.ones(N)
drain_g = np.ones(N)
tension = np.zeros(N)
log = []

CORRIDOR = {"S17", "S20", "S21"}
HOLO = {"S12", "S13", "S14"}
for sh in timing["shots"]:
    sid, t0 = sh["id"], sh["film_start_s"]
    i0, i1 = int(t0 * SR), int((t0 + sh["duration_s"]) * SR)
    v, _ = sf.read(os.path.join(ROOT, sh["line_file"]), dtype="float64")
    place(dialogue, v, t0 + sh["line_start_s"], gain=db(-3))
    duck[int((t0 + sh["line_start_s"]) * SR): int((t0 + sh["line_end_s"]) * SR)] = db(-6)
    if sid in CORRIDOR:
        muffle_g[i0:i1] = 1
    if sid in HOLO:
        holo_g[i0:i1] = 1
    if sid in {f"S{k:02d}" for k in range(10, 22)}:
        alarm_g[i0:i1] = 1
    if sid in {f"S{k:02d}" for k in range(20, 25)}:
        water_g[i0:i1] = 1
    if sid in {f"S{k:02d}" for k in range(9, 22)}:
        tension[i0:i1] = 1
    evp = os.path.join(ROOT, "manifests", "p02_events", f"{sid}.json")
    events = json.load(open(evp))["events"] if os.path.exists(evp) else []
    wet = sid in {f"S{k:02d}" for k in range(20, 25)}
    for e in events:
        k, t = e["kind"], t0 + (e["frame"] - 1) / FPS
        dur = e.get("dur", 24) / FPS
        tgt, gain, clip, pan = fx, -18, None, 0.0
        if k == "step":
            tgt, clip = foley, s_step(e.get("run", False), wet)
            gain = -14 if e.get("who") == "quill" and sid == "S15" else -17
            pan = -0.2 if e.get("side") == "L" else 0.2
            if sid in CORRIDOR or sid == "S16":
                gain -= 4
        elif k == "click":
            clip, gain = s_click(), -20
        elif k == "tone_low":
            clip, gain = s_tone(440), -22
        elif k == "tone_high":
            clip, gain = s_tone(660), -22
        elif k == "powerdown":
            clip, gain = s_powerdown(), -20
        elif k == "shimmer":
            clip, gain = s_shimmer(), -21
        elif k == "halo_swell":
            clip, gain = s_swell(), -24
        elif k == "machine_on":
            clip, gain = s_machine_on(), -24  # heard through the glass
        elif k == "tap":
            tgt, clip, gain = foley, s_knock(), -16
        elif k == "door_creak":
            clip, gain = s_creak(), -22
        elif k in ("door_thud", "thump"):
            clip, gain = s_thud(55, 0.6, 0.5), -12 if k == "door_thud" else -14
        elif k == "ratchet":
            clip, gain = s_ratchet(dur), -24
        elif k == "bolt":
            clip, gain = s_bolt(), -14
        elif k == "whine":
            clip, gain = s_whine(min(dur, 3.0)), -27
        elif k == "error":
            clip, gain = s_buzz(), -20
        elif k == "alarm_on":
            alarm_g[int(t * SR): i1] = 1
        elif k == "rip":
            tgt, clip, gain = foley, s_rip(), -14
        elif k == "cloth_thump":
            tgt, clip, gain = foley, s_thud(80, 0.3, 0.6), -16
        elif k == "roll":
            tgt, clip, gain = foley, s_roll(dur), -20
        elif k == "beep":
            clip, gain = s_beep(), -22
        elif k == "warning":
            clip, gain = s_warning(), -17
        elif k == "glitter":
            clip, gain = s_glitter(dur), -24
        elif k == "bonded":
            clip, gain = s_bonded(), -16
        elif k == "swell":
            clip, gain = s_rise(dur), -22
        elif k == "bend":
            clip, gain = s_whoosh(1.0, True), -20
        elif k == "drain":
            drain_g[int(t * SR): i1] = db(-14)
        elif k == "stool":
            tgt, clip, gain = foley, s_scrape(), -15
        elif k == "papers":
            tgt, clip, gain = foley, s_flutter(), -20
        elif k == "silence":
            a = int(t * SR)
            silence_g[a: a + int(dur * SR)] = 0.0
        elif k == "lever":
            clip, gain = s_lever(), -13
        elif k == "pipe_groan":
            clip, gain = s_groan(), -18
        elif k == "water_on":
            water_g[int(t * SR): i1] = 1
            clip, gain = s_whoosh(0.9, True), -16
        elif k == "water_off":
            water_g[int(t * SR): i1] = 0
        elif k == "gasp":
            tgt, clip, gain = foley, s_gasp(), -24
        elif k == "charge":
            clip, gain = s_whine(min(dur, 4.0)), -22
        elif k == "flash_boom":
            clip, gain = s_boom(), -9
            alarm_g[int(t * SR): i1] = 0
            tension[int(t * SR):] = 0
        elif k == "collapse":
            tgt, clip, gain = foley, s_step(False, True) * 0.5 + s_thud(70, 0.4, 0.6)[: int(SR * 0.16)] * 0.8, -12
        elif k == "sting":
            continue  # handled in music below
        if clip is not None:
            place(tgt, clip, t, db(gain), pan)
            log.append({"shot": sid, "kind": k, "time_s": round(t, 3), "gain_db": gain})

# muffle FX/foley that happen inside the lab while the camera is in the corridor
for buf in (fx,):
    lp = np.stack([fft_filter(buf[:, c], None, 500) for c in range(2)], 1)
    m = smooth_gate(muffle_g)[:, None]
    buf[:] = buf * (1 - m) + lp * m * db(-8)

# ------------------------------------------------------------------ ambience beds
tt = np.arange(N) / SR
room = (np.sin(2 * np.pi * 60 * tt) * 0.6 + np.sin(2 * np.pi * 120 * tt) * 0.3) * db(-40)
air = rng.standard_normal((N, 2))
for c in range(2):
    air[:, c] = fft_filter(air[:, c], 80, 4000, -3.0)
air = air / np.max(np.abs(air)) * db(-36)
halo = (np.sin(2 * np.pi * 110 * tt) + 0.4 * np.sin(2 * np.pi * 220.7 * tt)) * (0.75 + 0.25 * np.sin(2 * np.pi * 0.3 * tt)) * db(-40)
amb += air
amb[:, 0] += room + halo
amb[:, 1] += room * 0.9 + halo
# hologram hum
hh = (np.sin(2 * np.pi * 174 * tt) + 0.5 * np.sin(2 * np.pi * 348.5 * tt)) * (0.6 + 0.4 * np.sin(2 * np.pi * 4 * tt)) * db(-32)
hg = smooth_gate(holo_g, 200)
amb[:, 0] += hh * hg
amb[:, 1] += hh * hg
# alarm: original two-tone siren
seg = (np.floor(tt / 0.45) % 2).astype(bool)
fsig = np.where(seg, 880.0, 660.0)
siren = np.sin(2 * np.pi * np.cumsum(fsig) / SR)
siren = fft_filter(np.sign(siren) * 0.4 + siren * 0.6, 200, 3500)
siren = siren / np.max(np.abs(siren))
ag = smooth_gate(alarm_g, 30)
mg = smooth_gate(muffle_g, 30)
siren_l = siren * ag * (db(-30) * (1 - mg) + db(-48) * mg)
amb[:, 0] += siren_l * 0.9
amb[:, 1] += siren_l
# sprinkler water bed + droplet ticks
water = rng.standard_normal((N, 2))
for c in range(2):
    water[:, c] = fft_filter(water[:, c], 250, 9000, -2.5)
water /= np.max(np.abs(water))
wg = smooth_gate(water_g, 120)
wlev = db(-17) * (1 - mg) + db(-30) * mg
amb += water * (wg * wlev)[:, None]
for _ in range(int(TOTAL * 30)):
    t = rng.uniform(0, TOTAL)
    i = int(t * SR)
    if wg[i] < 0.5:
        continue
    n = int(SR * rng.uniform(0.004, 0.012))
    tick = fft_filter(rng.standard_normal(n) * np.exp(-np.linspace(0, 8, n)), 1500, 7000)
    place(amb, norm(tick), t, db(rng.uniform(-36, -24)) * (1 - mg[i] * 0.8), rng.uniform(-0.9, 0.9))

# ------------------------------------------------------------------ music (original, synthesized)
# opening pad (A minor-ish, S01-S08), a heartbeat pulse under the countdown (S09 until the flash), final sting
pad_end = start_s["S09"]
pad = np.zeros(N)
for f0 in (110.0, 130.81, 164.81, 220.0):
    pad += np.sin(2 * np.pi * f0 * tt) + 0.2 * np.sin(2 * np.pi * 2.003 * f0 * tt)
pad *= np.clip(tt / 2.0, 0, 1) * np.clip((pad_end - tt) / 1.5, 0, 1) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.11 * tt))
pad = fft_filter(pad, None, 1200) / 4 * db(-30)
music[:, 0] += pad
music[:, 1] += pad
tg = tension > 0
if tg.any():
    a, b = np.argmax(tg) / SR, (len(tg) - np.argmax(tg[::-1])) / SR
    t = a
    while t < b:
        bpm = 70 + 50 * (t - a) / max(1e-3, b - a)
        beat = s_thud(48, 0.25, 0.05)
        place(music, beat, t, db(-22))
        place(music, beat, t + 0.16, db(-27))
        t += 60 / bpm
sting_t = None
for sh in timing["shots"]:
    if sh["id"] == "S24":
        evs = json.load(open(os.path.join(ROOT, "manifests", "p02_events", "S24.json")))["events"]
        st = [e for e in evs if e["kind"] == "sting"]
        if st:
            sting_t = sh["film_start_s"] + (st[0]["frame"] - 1) / FPS
if sting_t is not None:
    for f0, dt in ((261.63, 0.0), (329.63, 0.12), (392.0, 0.24), (493.88, 0.38), (523.25, 0.55)):
        n = int(SR * 3.0)
        x = np.arange(n) / SR
        tn = (np.sin(2 * np.pi * f0 * x) + 0.35 * np.sin(2 * np.pi * 2 * f0 * x) + 0.1 * np.sin(2 * np.pi * 3.01 * f0 * x)) * np.exp(-x * 1.3)
        tn *= np.minimum(1, x / 0.005)
        place(music, tn, sting_t + dt, db(-25), 0.1)
    # soft resolving pad under the last lines
    m = (tt > sting_t - 1.0)
    rp = sum(np.sin(2 * np.pi * f * tt) for f in (130.81, 196.0, 261.63, 329.63)) / 4
    rp *= np.clip((tt - sting_t + 1.0) / 2.0, 0, 1) * m * db(-32)
    music[:, 0] += rp
    music[:, 1] += rp

# ------------------------------------------------------------------ mix
duck = smooth_gate(duck, 80)
sg = smooth_gate(silence_g, 60)
dg = smooth_gate(drain_g, 150)
stems = {"dialogue": dialogue, "ambience": amb * (duck * sg * dg)[:, None], "foley": foley * sg[:, None],
         "fx": fx * sg[:, None], "music": music * (duck * dg)[:, None]}
mix = sum(stems.values())
fade = np.minimum(1, np.arange(N) / (0.15 * SR)) * np.minimum(1, (N - np.arange(N)) / (0.6 * SR))
mix *= fade[:, None]
os.makedirs(OUT, exist_ok=True)
for k, s in stems.items():
    sf.write(os.path.join(OUT, f"{k}.wav"), s, SR, subtype="PCM_24")
pre = os.path.join(OUT, "mix_prenorm.wav")
sf.write(pre, mix / max(1.0, np.max(np.abs(mix))), SR, subtype="PCM_24")


def measure(path):
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    tail = p.stderr[p.stderr.rfind("Summary:"):]
    return float(tail.split("I:")[1].split("LUFS")[0]), float(tail.split("Peak:")[1].split("dBFS")[0])


l0, p0 = measure(pre)
target = -16.0
base = mix / max(1.0, np.max(np.abs(mix)))
g = target - l0
y = base * db(g)
# soft limiter so the flash boom cannot break the -1 dBTP ceiling
ceil = db(-1.5)
y = np.where(np.abs(y) > ceil * 0.8, np.sign(y) * (ceil * 0.8 + (ceil * 0.2) * np.tanh((np.abs(y) - ceil * 0.8) / (ceil * 0.2))), y)
mix_path = os.path.join(OUT, "mix.wav")
sf.write(mix_path, y, SR, subtype="PCM_24")
l1, p1 = measure(mix_path)
if abs(l1 - target) > 0.3:  # one corrective pass after limiting
    y = y * db(target - l1)
    y = np.where(np.abs(y) > ceil * 0.8, np.sign(y) * (ceil * 0.8 + (ceil * 0.2) * np.tanh((np.abs(y) - ceil * 0.8) / (ceil * 0.2))), y)
    sf.write(mix_path, y, SR, subtype="PCM_24")
    l1, p1 = measure(mix_path)
os.remove(pre)
timing["mix"] = {"file": os.path.relpath(mix_path, ROOT), "duration_s": round(N / SR, 3), "prenorm_lufs_i": l0,
                 "final_lufs_i": l1, "final_true_peak_dbfs": p1, "target_lufs_i": target,
                 "stems": [f"assets/audio/p02/{k}.wav" for k in stems], "fx_events": len(log)}
json.dump(timing, open(os.path.join(ROOT, "manifests", "p02_audio_timing.json"), "w"), indent=2)
json.dump(log, open(os.path.join(ROOT, "manifests", "p02_sound_log.json"), "w"), indent=1)
print(json.dumps(timing["mix"], indent=2))
