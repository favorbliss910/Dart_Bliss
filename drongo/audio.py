"""Procedural score + SFX, mixed under the narration -> mix.wav"""
import json, math, numpy as np, soundfile as sf
import render

SR = 24000
voice, _ = sf.read('voice.wav', dtype='float32')
meta = json.load(open('words.json'))
total = meta['duration']
N = int(SR * (total + 0.5))
rng = np.random.default_rng(7)
t_all = np.arange(N) / SR


def add(buf, sig, t0, gain=1.0):
    i = int(t0 * SR)
    if i >= len(buf):
        return
    sig = sig[:len(buf) - i]
    buf[i:i + len(sig)] += sig * gain


def env(n, a=0.005, d=0.3):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)


def lp(x, k):
    y = np.zeros_like(x); acc = 0.0
    for i in range(len(x)):  # small signals only
        acc += k * (x[i] - acc); y[i] = acc
    return y


def lp_fast(x, k, passes=1):
    from scipy.signal import lfilter
    for _ in range(passes):
        x = lfilter([k], [1, -(1 - k)], x)
    return x


def marimba(f, dur=0.5):
    n = int(SR * dur); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t / 0.03)
    return (s * env(n, 0.002, 0.22)).astype(np.float32)


def pluck(f, dur=0.6):
    n = int(SR * dur); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * 2 * f * t)
    return (s * env(n, 0.003, 0.18)).astype(np.float32)


def noise(dur):
    return rng.standard_normal(int(SR * dur)).astype(np.float32)


# ---------------- music: sneaky pizzicato in D minor, 100 bpm
music = np.zeros(N, np.float32)
bpm = 100; beat = 60 / bpm
D = 146.83
scale = [0, 3, 5, 7, 10, 12, 15]
mel = [0, None, 3, 5, None, 3, 0, None, 7, None, 5, 3, 5, None, None, None,
       0, None, 3, 5, None, 7, 10, None, 12, None, 10, 7, 5, None, 3, None]
bass = [0, 0, 5, 5, 3, 3, 7, 5]
step = beat / 2
k = 0
t = 0.0
while t < total + 0.4:
    m = mel[k % len(mel)]
    if m is not None:
        add(music, marimba(D * 2 * 2 ** (m / 12)), t, 0.16)
    if k % 2 == 0:
        b = bass[(k // 4) % len(bass)]
        add(music, pluck(D / 2 * 2 ** (b / 12)), t, 0.22)
    hh = noise(0.05) * env(int(SR * 0.05), 0.001, 0.012)
    hh = hh - lp_fast(hh, 0.3)
    add(music, hh, t, 0.05 if k % 2 else 0.025)
    k += 1; t += step
# music swells in "sky full of hawks" with a low drone
wind = lp_fast(noise(total + 0.5), 0.004, 2)[:N] * 6
wind *= 0.5 + 0.5 * np.sin(t_all * 0.7) ** 2

sfx = np.zeros(N, np.float32)
bounds = render.shot_bounds(meta['words'], total)
starts = [b[0] for b in bounds]
# whoosh on every cut
for s0 in starts[1:]:
    n = noise(0.35); e = np.sin(np.linspace(0, np.pi, len(n))) ** 2
    add(sfx, lp_fast(n * e, 0.08, 2) * 3, s0 - 0.12, 0.25)


def chirp(f0, f1, dur, harsh=0.0):
    n = int(SR * dur); tt = np.arange(n) / SR
    f = np.geomspace(f0, f1, n)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) + 0.5 * np.sin(2 * ph) + harsh * np.sign(np.sin(3 * ph)) * 0.3
    s *= 1 + 0.4 * np.sin(2 * np.pi * 38 * tt)
    return (s * env(n, 0.01, dur * 0.6)).astype(np.float32)


# drongo scream (shot 3)
s3 = starts[2]
for i in range(3):
    add(sfx, chirp(2600, 1700, 0.22, 1.0), s3 + 0.02 + i * 0.2, 0.28)
# startle sting
add(sfx, marimba(D * 8, 0.4) + marimba(D * 8 * 1.5, 0.4), starts[3] + 0.15, 0.25)
# pops as meerkats appear (shot 5)
s5, d5 = bounds[4]
for kk in range(4):
    tt = s5 + (0.05 + kk * 0.17) * (d5 - s5)
    add(sfx, chirp(300, 900, 0.09), tt + 0.05, 0.35)
# hawk cry (shot 11) + low drone
s11 = starts[10]
add(sfx, chirp(3200, 1500, 0.9, 0.6), s11 + 0.1, 0.18)
add(sfx, chirp(2900, 1400, 0.7, 0.6), s11 + 1.0, 0.12)
n = int(SR * 2.0); drone = np.sin(2 * np.pi * 73 * np.arange(n) / SR) * np.sin(np.linspace(0, np.pi, n))
add(sfx, drone.astype(np.float32), s11, 0.12)
# "spots" sting
add(sfx, chirp(400, 1600, 0.25), starts[12] + 0.85, 0.2)
# meerkat alarm barks (shot 14)
for i in range(3):
    b = chirp(1300, 900, 0.09, 1.0) + noise(0.09) * 0.25 * env(int(SR * 0.09), 0.002, 0.03)
    add(sfx, b, starts[13] + 0.03 + i * 0.16, 0.35)
# dives (shot 15)
s15, e15 = bounds[14]
for i in range(4):
    add(sfx, chirp(900, 200, 0.18), s15 + (0.1 + i * 0.16) * (e15 - s15), 0.25)

# duck music under voice
venv = np.abs(np.pad(voice, (0, max(0, N - len(voice))))[:N])
venv = lp_fast(venv, 0.002, 2)
duck = 1 - 0.45 * np.clip(venv / (venv.max() * 0.3), 0, 1)
mix = np.pad(voice, (0, max(0, N - len(voice))))[:N] * 1.0 + music * duck * 0.55 + wind * 0.08 + sfx
fade = np.ones(N); fl = int(SR * 0.4); fade[-fl:] = np.linspace(1, 0, fl)
mix *= fade
mix /= max(1.0, np.abs(mix).max() / 0.95)
sf.write('mix.wav', mix.astype(np.float32), SR)
print('mix ok', N / SR)
