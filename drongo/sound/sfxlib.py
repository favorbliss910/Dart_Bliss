"""Procedural SFX library. Every recipe is seeded and parameterised [451, 453],
built transient/body/tail [401] and click-free [419]. Principle numbers in [].

    python3 sound/sfxlib.py   -> renders the audition bank to sound/bank/*.wav
"""
import os
import numpy as np
from scipy.signal import butter, sosfilt, lfilter

SR = 48000
PI = np.pi


# ------------------------------------------------------------------ primitives
def rng(seed):
    return np.random.default_rng(seed)


def t_(dur):
    return np.arange(int(SR * dur)) / SR


def env_exp(n, attack=0.002, tau=0.1, hold=0.0):
    t = np.arange(n) / SR
    a = np.minimum(1.0, t / max(attack, 1e-4))
    d = np.where(t < attack + hold, 1.0, np.exp(-(t - attack - hold) / tau))
    return a * d


def fade(x, fin=0.002, fout=0.008):  # [419]
    x = x.copy()
    a, b = int(SR * fin), int(SR * fout)
    if a:
        x[:a] *= np.linspace(0, 1, a)
    if b:
        x[-b:] *= np.linspace(1, 0, b)
    return x


def bp(x, lo, hi, order=2):
    lo = max(lo, 20)
    hi = min(hi, SR / 2 - 100)
    return sosfilt(butter(order, [lo, hi], 'bandpass', fs=SR, output='sos'), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, 'highpass', fs=SR, output='sos'), x)


def lp(x, f, order=2):
    return sosfilt(butter(order, min(f, SR / 2 - 100), 'lowpass', fs=SR, output='sos'), x)


def dc_block(x):  # [454]
    return hp(x, 25, 1)


def pink(n, r):
    w = r.standard_normal(n)
    # Paul Kellet-style economy pinking
    b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
    a = [1, -2.494956002, 2.017265875, -0.522189400]
    return lfilter(b, a, w) * 6


def svf_bp(x, fc, q=1.0):
    """Time-varying state-variable band-pass; fc is an array (Hz)."""
    y = np.zeros_like(x)
    low = band = 0.0
    damp = 1.0 / q
    fc = np.broadcast_to(fc, x.shape)
    f = 2 * np.sin(PI * np.minimum(fc, SR / 6) / SR)
    for i in range(len(x)):
        high = x[i] - low - damp * band
        band += f[i] * high
        low += f[i] * band
        y[i] = band
    return y


def svf_lp(x, fc, q=0.707):
    y = np.zeros_like(x)
    low = band = 0.0
    damp = 1.0 / q
    fc = np.broadcast_to(fc, x.shape)
    f = 2 * np.sin(PI * np.minimum(fc, SR / 6) / SR)
    for i in range(len(x)):
        high = x[i] - low - damp * band
        band += f[i] * high
        low += f[i] * band
        y[i] = low
    return y


def sweep(f0, f1, dur, shape=1.0):
    """Exponential (constant semitones/s) sweep [446]; shape>1 steepens the end [533]."""
    n = int(SR * dur)
    u = np.linspace(0, 1, n) ** shape
    f = f0 * (f1 / f0) ** u
    return np.sin(2 * PI * np.cumsum(f) / SR), f


def comb(x, delay_ms=5.0, fb=0.7):  # tunnel colour [441]
    d = int(SR * delay_ms / 1000)
    b = np.zeros(d + 1); b[0] = 1
    a = np.zeros(d + 1); a[0] = 1; a[-1] = -fb
    return lfilter(b, a, x) * (1 - fb)


def norm(x, peak=0.89):
    m = np.abs(x).max()
    return x * (peak / m) if m > 0 else x


def mix(*parts):
    n = max(len(p) for p in parts)
    out = np.zeros(n)
    for p in parts:
        out[:len(p)] += p
    return out


def at(x, delay):
    return np.concatenate([np.zeros(int(SR * delay)), x])


def soft_clip(x, drive=3.0):  # [443]
    return np.tanh(x * drive) / np.tanh(drive)


def click(r, ms=2.0, hi=3000):
    n = int(SR * ms / 1000) + 1
    return hp(r.standard_normal(n) * env_exp(n, 0.0002, ms / 3000), hi)


# ------------------------------------------------------------------ whooshes [471-490]
def whoosh(dur=0.35, direction='pass', size=1.0, flutter=0.0, seed=0, tonal=True):
    r = rng(seed)
    n = int(SR * dur)
    u = np.linspace(0, 1, n)
    peak = 0.7  # [472]
    amp = np.where(u < peak, (u / peak) ** 2.2, ((1 - u) / (1 - peak)) ** 1.4)
    lo, mid, hi = (300, 3000, 600)
    if direction == 'up':
        lo, mid, hi = 300, 1800, 4500    # zoom-in / launch [479, 483]
    elif direction == 'down':
        lo, mid, hi = 3500, 1500, 250    # dive / zoom-out
    lo, mid, hi = lo / size, mid / size, hi / size  # size → band [480]
    fc = np.where(u < peak, lo * (mid / lo) ** (u / peak), mid * (hi / mid) ** ((u - peak) / (1 - peak)))
    x = svf_bp(pink(n, r), fc, q=1.4 if size >= 1 else 2.5)  # [484]
    x = svf_lp(x, fc * 2.2)  # keep the whoosh out of the sibilance band [687]
    if flutter:
        x *= 1 - 0.6 * (0.5 + 0.5 * np.sin(2 * PI * np.cumsum(flutter * (0.6 + u)) / SR))  # [478]
    if tonal:  # [475]
        s, _ = sweep(fc[0] * 0.5, fc[-1] * 0.5, dur)
        x = x + 0.12 * s * np.abs(x).max()
    return fade(norm(x * amp))


def whip_land(seed=0):  # [476]
    r = rng(seed)
    return norm(mix(whoosh(0.2, 'up', 0.9, seed=seed) * 0.8, at(lp(click(r, 6, 1500), 4000) * 0.5, 0.14)))


def suck_in(dur=0.45, seed=0):  # reverse tail [482]
    r = rng(seed)
    n = int(SR * dur)
    x = bp(pink(n, r), 400, 5000) * env_exp(n, 0.001, dur / 4)
    return fade(norm(x[::-1]), 0.01, 0.002)


# ------------------------------------------------------------------ impacts / pops [491-510]
def thump(f_end=55, size=1.0, seed=0, material='sand'):
    r = rng(seed)
    dur = 0.25 * size
    s, _ = sweep(f_end * 2.6, f_end, 0.06 * size + 0.02)  # [492]
    body = np.concatenate([s, np.sin(2 * PI * f_end * t_(dur))[: int(SR * dur)]])[: int(SR * dur)]
    body = soft_clip(body * env_exp(len(body), 0.001, 0.05 * size), 2.5)  # harmonics for phones
    tr = click(r, 4, 1200) * (0.4 if material == 'sand' else 0.9)
    if material == 'sand':
        tr = lp(tr, 3500)  # soft sand transient [525]
    tail = bp(r.standard_normal(int(SR * 0.2 * size)), 400, 3000) * env_exp(int(SR * 0.2 * size), 0.003, 0.05)
    return fade(norm(mix(body, tr, tail * 0.25)))


def pop(up=True, size=1.0, f0=420, seed=0, semis=0):
    r = rng(seed)
    k = 2 ** (semis / 12)
    a, b = (f0 * k, f0 * 2.9 * k) if up else (f0 * 2.6 * k, f0 * 0.8 * k)
    dur = 0.05 * size + 0.02
    s, _ = sweep(a, b, dur)
    s *= env_exp(len(s), 0.001, dur / 2.5)
    puff = hp(r.standard_normal(int(SR * 0.04)), 2500) * env_exp(int(SR * 0.04), 0.002, 0.01)
    return fade(norm(mix(s, click(r, 1.5, 2000) * 0.3, puff * 0.25)))


def boing(f=260, dur=0.45):
    t = t_(dur)
    depth = 0.25 * np.exp(-t / 0.18)
    ph = 2 * PI * np.cumsum(f * (1 + depth * np.sin(2 * PI * 8 * t))) / SR
    return fade(norm(np.sin(ph) * env_exp(len(t), 0.002, 0.15)))


def falling_whistle(dur=0.7, f0=2000, f1=420):  # [511-512]
    s, f = sweep(f0, f1, dur, shape=1.6)
    t = t_(dur)
    s = np.sin(2 * PI * np.cumsum(f * (1 + 0.006 * np.sin(2 * PI * 5 * t[:len(f)]))) / SR)
    return fade(norm(s * np.minimum(1, t[:len(s)] / 0.05) * 0.8), 0.01, 0.04)


def startle_sting(key_hz=698.46, seed=0):
    """Graphic '!' sting: bright fifth + octave stack, purer than world sounds [577, 579]."""
    out = []
    for m in (1, 1.5, 2):
        out.append(np.sin(2 * PI * key_hz * m * t_(0.35)) * env_exp(int(SR * 0.35), 0.001, 0.09) / m)
    r = rng(seed)
    return fade(norm(mix(*out, click(r, 1.5, 4000) * 0.4)))


def fm_ding(fc=1396.9, ratio=3.5, dur=0.6, index=4.0):  # [581, 436-437]
    t = t_(dur)
    idx = index * np.exp(-t / 0.12)
    s = np.sin(2 * PI * fc * t + idx * np.sin(2 * PI * fc * ratio * t))
    return fade(norm(s * env_exp(len(t), 0.001, 0.22)))


def name_card(seed=0):
    """Title-card stinger: thump + fifth swell + FM ding shimmer, < 1.5 s [579, 580]."""
    r = rng(seed)
    swell = sum(np.sin(2 * PI * f * t_(1.0)) for f in (349.23, 523.25, 698.46)) * env_exp(int(SR), 0.01, 0.3)
    return fade(norm(mix(thump(70, 0.8, seed) * 0.5, swell * 0.25, fm_ding() * 0.6, at(fm_ding(2093, 3.5, 0.5) * 0.25, 0.08))))


# ------------------------------------------------------------------ sand & ground [515-535]
def grains(dur, density, lo=1500, hi=7000, seed=0, decay=None, gmin=1, gmax=5):
    """Granular sand [438]: density grains/s (scalar or array)."""
    r = rng(seed)
    n = int(SR * dur)
    out = np.zeros(n)
    dens = np.broadcast_to(np.asarray(density, float), (n,))
    i = 0
    while i < n:
        d = max(dens[min(i, n - 1)], 1.0)
        i += int(SR * r.exponential(1 / d))
        if i >= n:
            break
        g = int(SR * r.uniform(gmin, gmax) / 1000) + 2
        grain = r.standard_normal(g) * np.hanning(g) * r.uniform(0.2, 1.0)
        e = min(n, i + g)
        out[i:e] += grain[: e - i]
    out = bp(out, lo, hi)
    if decay:
        out *= np.exp(-np.arange(n) / SR / decay)
    return out


def dig_stroke(seed=0):  # [521]
    r = rng(seed)
    th = lp(r.standard_normal(int(SR * 0.04)), 500) * env_exp(int(SR * 0.04), 0.003, 0.012)
    throw = grains(0.16, 1800, 1500, 7000, seed, decay=0.05)
    return fade(norm(mix(th * 0.8, at(throw, 0.01))))


def digging(dur=2.0, rate=6.0, seed=0, depth=0.0):
    r = rng(seed)
    out = np.zeros(int(SR * (dur + 0.3)))
    t = 0.0
    k = 0
    while t < dur:
        s = dig_stroke(seed * 100 + k) * r.uniform(0.6, 1.0) * (1.25 if k % 4 == 0 else 1)  # [429]
        i = int(SR * t)
        out[i:i + len(s)] += s[: len(out) - i]
        t += (1 / rate) * r.uniform(0.85, 1.15)  # jitter [588]
        k += 1
    if depth:  # deeper → darker + tunnel colour [522]
        out = comb(lp(out, 5000 - 3500 * depth), 4.0, 0.5 * depth) + out * (1 - depth) * 0.5
    return fade(norm(out[: int(SR * dur)]))


def sand_spill(dur=0.5, seed=0):
    return fade(norm(grains(dur, np.linspace(2500, 200, int(SR * dur)), 1500, 8000, seed, decay=dur / 3)))


def dust_puff(seed=0):  # [524]
    r = rng(seed)
    n = int(SR * 0.18)
    return fade(norm(bp(r.standard_normal(n), 900, 5000) * env_exp(n, 0.01, 0.05)))


def scurry(dur=0.8, rate=11, seed=0, size=1.0):  # [515-516]
    r = rng(seed)
    out = np.zeros(int(SR * dur))
    t = 0.0
    k = 0
    while t < dur - 0.05:
        n = int(SR * 0.03)
        pat = lp(r.standard_normal(n), 900 / size) * env_exp(n, 0.002, 0.008)
        pat += grains(0.03, 900, 2000, 6000, seed * 7 + k) * 0.4
        i = int(SR * t)
        out[i:i + n] += pat[: len(out) - i] * (1.0 if k % 2 else 0.8)
        t += (1 / rate) * r.uniform(0.85, 1.15)
        k += 1
    out += grains(dur, 120, 2500, 7000, seed + 1) * 0.15
    return fade(norm(out))


def beetle_skitter(dur=0.6, seed=0):  # [517]
    r = rng(seed)
    out = np.zeros(int(SR * dur))
    t = 0.0
    while t < dur - 0.01:
        c = bp(click(r, r.uniform(1, 3), 2500), 3000, 7000)
        i = int(SR * t)
        out[i:i + len(c)] += c[: len(out) - i] * r.uniform(0.4, 1)
        t += r.choice([1 / 35, 1 / 25, 1 / 30, 0.09])
    return fade(norm(out))


def chitin_crunch(seed=0):  # [573]
    r = rng(seed)
    parts = []
    for k in range(4):
        f = r.uniform(3000, 5500)
        m = sum(np.sin(2 * PI * f * q * t_(0.05)) * np.exp(-t_(0.05) / 0.01) / (j + 1)
                for j, q in enumerate((1, 1.51, 2.27)))
        parts.append(at(m, k * r.uniform(0.02, 0.05)))
    return fade(norm(mix(*parts, grains(0.25, 600, 2500, 6000, seed, decay=0.08) * 0.5)))


def scorpion_threat(dur=0.7, seed=0):  # [551, 444]
    r = rng(seed)
    t = t_(dur)
    pulses = (np.sin(2 * PI * 70 * t) > 0.6).astype(float)
    x = bp(r.standard_normal(len(t)) * pulses, 3000, 6000)
    x *= np.minimum(1, t / (dur * 0.6))
    ring = np.sin(2 * PI * 1200 * t) * np.sin(2 * PI * 90 * t) * 0.15
    return fade(norm(x + ring * np.minimum(1, t / dur)))


def lizard_patter(dur=0.5, seed=0):  # [519]
    r = rng(seed)
    out = np.zeros(int(SR * (dur + 0.05)))
    t = 0.0
    while t < dur:
        c = bp(r.standard_normal(int(SR * 0.012)), 1200, 6500) * env_exp(int(SR * 0.012), 0.001, 0.003)
        i = int(SR * t)
        out[i:i + len(c)] += c * r.uniform(0.5, 1)
        t += 1 / 18 * r.uniform(0.9, 1.1)
    c = click(r, 2, 3000)
    i = int(SR * dur)
    out[i:i + len(c)] += c * 1.2  # freeze click
    return fade(norm(out))


def gulp(seed=0):
    s, _ = sweep(520, 180, 0.16)
    return fade(norm(s * env_exp(len(s), 0.01, 0.06)))


# ------------------------------------------------------------------ voices
def fm_chirp(f0, f1, dur, ratio=2.0, index=1.5, vib=0.0, seed=0, harsh=0.0):
    """Swept FM syllable: the drongo's bright metallic voice [536, 538]."""
    r = rng(seed)
    n = int(SR * dur)
    u = np.linspace(0, 1, n)
    f = f0 * (f1 / f0) ** u
    if vib:
        f = f * (1 + vib * np.sin(2 * PI * 6 * u * dur))
    f = f * (1 + 0.01 * r.standard_normal(n).cumsum() / np.sqrt(n))  # jitter [448]
    ph = 2 * PI * np.cumsum(f) / SR
    idx = index * (1 - 0.6 * u)
    s = np.sin(ph + idx * np.sin(ratio * ph))
    if harsh:
        s += harsh * bp(r.standard_normal(n), 1500, 6000) * 0.6
        s = soft_clip(s, 1 + 2 * harsh)
    a = np.minimum(1, u * dur / 0.008) * np.minimum(1, (1 - u) * dur / 0.02)
    return s * a


def drongo_call(seed=0):
    """Signature: 3-4 bright metallic chirps, zigzag contour [538]."""
    r = rng(seed)
    sy = [(2400, 3600, 0.07), (3800, 2600, 0.09), (2200, 3000, 0.06), (3400, 4200, 0.11)]
    parts = []
    t = 0.0
    for k, (a, b, d) in enumerate(sy[: 3 + seed % 2]):
        sc = 2 ** (r.uniform(-1, 1) / 12)
        parts.append(at(fm_chirp(a * sc, b * sc, d, 2.0, 1.0, 0.01, seed * 10 + k), t))
        t += d + r.uniform(0.03, 0.06)
    return fade(norm(mix(*parts)))


def drongo_scream(seed=0, n_syll=4):
    """Harsh alarm: noisy-FM syllables at ~10/s, descending overall [557]."""
    r = rng(seed)
    parts = []
    t = 0.0
    for k in range(n_syll):
        top = 3600 * 2 ** (-k * 1.2 / 12)
        d = r.uniform(0.07, 0.1)
        parts.append(at(fm_chirp(top, top * 0.62, d, 1.98, 3.0, 0.0, seed * 10 + k, harsh=0.7), t))
        t += d + r.uniform(0.015, 0.03)
    breath = bp(r.standard_normal(int(SR * 0.12)), 1000, 3000) * env_exp(int(SR * 0.12), 0.08, 0.02) * 0.2  # [555]
    return fade(norm(lp(bp(mix(breath, at(mix(*parts), 0.1)), 1200, 7000), 6000)))


def meerkat_chirp(seed=0, semis=0):  # contact chirp [544]
    r = rng(seed)
    f = 1700 * 2 ** ((semis + r.uniform(-1, 1)) / 12)
    s, _ = sweep(f, f * 1.25, r.uniform(0.035, 0.06))
    return fade(norm(s * env_exp(len(s), 0.004, 0.02)))


def meerkat_bark(seed=0, semis=0, aerial=True, tell=False):
    """Alarm bark: abrupt, noisy 1-2 kHz burst over a harmonic buzz [541, 543].
    tell=True is the drongo's copy: same recipe + faint metallic FM edge, +1 st [539]."""
    r = rng(seed)
    d = r.uniform(0.09, 0.13)
    n = int(SR * d)
    k = 2 ** ((semis + (1 if tell else 0)) / 12)
    f0 = (520 if aerial else 380) * k
    tt = np.arange(n) / SR
    f = f0 * (1 - 0.25 * tt / d)
    ph = 2 * PI * np.cumsum(f) / SR
    buzz = np.sign(np.sin(ph)) * 0.6 + np.sin(2 * ph) * 0.4
    buzz = bp(buzz, 600, 3200)
    noise = bp(r.standard_normal(n), 1000 * k, 2200 * k) * (1.3 if aerial else 0.7)
    x = (buzz + noise) * env_exp(n, 0.001, d / 2.2)
    if tell:
        x += 0.06 * fm_chirp(f0 * 4, f0 * 3.2, d, 3.5, 1.2, 0, seed) * env_exp(n, 0.001, d / 2)
    return fade(norm(soft_clip(x, 1.6)))


def bark_volley(count=3, rate=6.0, seed=0, semis=0, tell=False, aerial=True):  # urgency [542]
    parts = [at(meerkat_bark(seed * 10 + k, semis, aerial, tell), k / rate) for k in range(count)]
    return fade(norm(mix(*parts)))


def yelp(seed=0, semis=0):
    """Startled formant yelp: +12 st in 80 ms, abrupt cutoff [560, 449]."""
    r = rng(seed)
    d = 0.14
    n = int(SR * d)
    u = np.linspace(0, 1, n)
    f = 330 * 2 ** ((semis + 12 * np.minimum(1, u / 0.55)) / 12)
    ph = 2 * PI * np.cumsum(f) / SR
    src = sum(np.sin(h * ph) / h for h in range(1, 12))
    x = bp(src, 600, 1400) + 0.6 * bp(src, 1900, 2800)  # "ah"→"ee"-ish formants
    return fade(norm(x * np.minimum(1, u / 0.05)), 0.003, 0.006)


def gasp(seed=0):
    r = rng(seed)
    n = int(SR * 0.22)
    x = svf_bp(r.standard_normal(n), np.linspace(900, 1700, n), 4) * env_exp(n, 0.03, 0.06)
    return fade(norm(x))


def chew(dur=0.6, seed=0):
    r = rng(seed)
    out = np.zeros(int(SR * dur))
    t = 0.0
    while t < dur - 0.06:
        c = chitin_crunch(seed + int(t * 100))[: int(SR * 0.06)] * 0.4
        c += lp(r.standard_normal(len(c)), 700) * env_exp(len(c), 0.005, 0.02) * 0.6
        i = int(SR * t)
        out[i:i + len(c)] += c[: len(out) - i]
        t += r.uniform(0.11, 0.16)
    return fade(norm(out))


def hawk_cry(seed=0, distance=0.0):
    """Descending raspy scream, every instance different [546, 547, 549]; distance [548]."""
    r = rng(seed)
    d = r.uniform(0.55, 0.85)
    n = int(SR * d)
    u = np.linspace(0, 1, n)
    f0, f1 = r.uniform(3000, 3400), r.uniform(2050, 2350)
    f = f0 * (f1 / f0) ** (u ** r.uniform(0.6, 1.3))
    f *= 1 + 0.012 * np.sin(2 * PI * r.uniform(5, 8) * u * d)
    ph = 2 * PI * np.cumsum(f) / SR
    tone = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph)
    rasp = 1 - 0.55 * (0.5 + 0.5 * np.sign(np.sin(2 * PI * r.uniform(70, 110) * u * d)))
    noise = bp(r.standard_normal(n), 2000, 4500) * 0.35
    x = (tone * rasp + noise) * np.minimum(1, u * d / 0.02) * np.minimum(1, (1 - u) * d / 0.15) * (1 - 0.3 * u)
    if distance:
        x = lp(x, 5000 - 2000 * distance)
        x = mix(x, at(lp(x, 2500) * 0.25 * distance, 0.09), at(lp(x, 2000) * 0.15 * distance, 0.21))
    return fade(norm(x))


def wing_flap(size=1.0, seed=0):  # [567]
    r = rng(seed)
    d = 0.06 + 0.09 * size
    n = int(SR * d)
    whump = bp(pink(n, r), 200 / size, 1200 / size) * env_exp(n, 0.006, d / 3)
    flutter = bp(r.standard_normal(n), 3000, 6000) * env_exp(n, 0.002, d / 5) * 0.08
    return fade(norm(whump + flutter))


def flaps(count=3, rate=8.0, size=0.5, seed=0, decel=False):  # landing flutter [570]
    parts = []
    t = 0.0
    for k in range(count):
        parts.append(at(wing_flap(size, seed * 10 + k) * (0.6 ** k if decel else 1), t))
        t += 1 / rate * (1 + (0.25 * k if decel else 0))
    return fade(norm(mix(*parts)))


def hawk_dive(dur=0.6, seed=0):  # [520]
    w = whoosh(dur, 'down', 1.6, flutter=30, seed=seed)
    return fade(norm(w * np.linspace(0.5, 1, len(w)) ** 2), 0.02, 0.003)


def flyby(dur=1.6, seed=0, size=1.6):
    """Hawk shadow pass with Doppler drop at closest point [467]."""
    w = whoosh(dur, 'pass', size, flutter=4, seed=seed)
    n = len(w)
    u = np.linspace(0, 1, n)
    s, _ = sweep(260, 190, dur)
    tone = s[:n] * np.exp(-((u - 0.5) ** 2) / 0.04) * 0.25
    return fade(norm(w + tone))


def heartbeat(bpm=52, beats=2):
    out = []
    for k in range(beats):
        th = thump(48, 0.7, k)
        out.append(at(th, k * 60 / bpm))
        out.append(at(th * 0.6, k * 60 / bpm + 0.16))
    return norm(mix(*out))


# ------------------------------------------------------------------ ambience [801-860]
def desert_bed(dur, seed=0, wind=1.0, insects=1.0, birds=1.0, time='dawn'):
    """Loop-free, randomized-event desert bed [803]."""
    r = rng(seed)
    n = int(SR * dur)
    t = np.arange(n) / SR
    w = lp(pink(n, r), 400) * (0.6 + 0.4 * np.sin(2 * PI * t / r.uniform(6, 11) + r.uniform(0, 6)) ** 2)
    w += 0.2 * svf_bp(pink(n, r) * 0.3, 900 + 500 * np.sin(2 * PI * t / 7.3), 3)
    out = norm(w, 0.5) * wind
    if insects:  # sparse high cicada-like trills
        ins = np.sin(2 * PI * 5200 * t) * (np.sin(2 * PI * 38 * t) > 0.3)
        gate = (np.sin(2 * PI * t / 4.7 + 1) > 0.65).astype(float)
        out += lp(ins * gate, 7000) * 0.02 * insects * (1.5 if time == 'day' else 0.5)
    if birds:  # distant small birds, low-passed for distance [548]
        k = r.uniform(1.0, 3.0)
        while k < dur - 1:
            c = lp(meerkat_chirp(int(k * 100), 12 + r.uniform(-2, 4)), 4000) * 0.05 * birds
            i = int(SR * k)
            out[i:i + len(c)] += c[: n - i]
            k += r.uniform(1.5, 4.5)
    return fade(out, 0.3, 0.3)


def burrow_room(dur, seed=0):
    r = rng(seed)
    x = comb(lp(pink(int(SR * dur), r), 300), 6, 0.6)
    return fade(norm(x, 0.4), 0.2, 0.2)


# ------------------------------------------------------------------ audition bank
BANK = {
    'whoosh_cut_short': lambda: whoosh(0.22, 'pass', 1, seed=1),
    'whoosh_zoom_in': lambda: whoosh(0.4, 'up', 1, seed=2),
    'whoosh_pan': lambda: whoosh(0.7, 'pass', 1.2, seed=3),
    'whoosh_tilt_up_long': lambda: whoosh(1.3, 'up', 1.4, seed=4),
    'whip_land': lambda: whip_land(5),
    'suck_in': lambda: suck_in(0.45, 6),
    'thump_sand': lambda: thump(55, 1, 7),
    'pop_up': lambda: pop(True, 1, seed=8),
    'pop_down': lambda: pop(False, 1, seed=9),
    'boing': lambda: boing(),
    'falling_whistle': lambda: falling_whistle(0.6),
    'startle_sting': lambda: startle_sting(),
    'name_card': lambda: name_card(),
    'dig_2s': lambda: digging(2.0, 6, 10),
    'dig_deep': lambda: digging(1.5, 6, 11, depth=0.8),
    'sand_spill': lambda: sand_spill(0.5, 12),
    'dust_puff': lambda: dust_puff(13),
    'scurry': lambda: scurry(0.8, 11, 14),
    'beetle_skitter': lambda: beetle_skitter(0.6, 15),
    'chitin_crunch': lambda: chitin_crunch(16),
    'scorpion_threat': lambda: scorpion_threat(0.7, 17),
    'lizard_patter': lambda: lizard_patter(0.5, 18),
    'gulp': lambda: gulp(),
    'drongo_call_a': lambda: drongo_call(1),
    'drongo_call_b': lambda: drongo_call(2),
    'drongo_scream': lambda: drongo_scream(3),
    'meerkat_chirps': lambda: mix(*[at(meerkat_chirp(k, k % 3 * 2), k * 0.23) for k in range(5)]),
    'meerkat_bark_volley': lambda: bark_volley(3, 6, 4),
    'drongo_mimic_bark': lambda: bark_volley(3, 6, 4, tell=True),
    'yelp': lambda: yelp(5),
    'gasp': lambda: gasp(6),
    'chew': lambda: chew(0.6, 7),
    'hawk_cry_near': lambda: hawk_cry(8),
    'hawk_cry_far': lambda: hawk_cry(9, distance=0.8),
    'hawk_dive': lambda: hawk_dive(0.6, 10),
    'hawk_flyby': lambda: flyby(1.6, 11),
    'wing_flaps_drongo_land': lambda: flaps(3, 9, 0.45, 12, decel=True),
    'heartbeat': lambda: heartbeat(),
    'desert_bed_10s': lambda: desert_bed(10, 1),
    'burrow_room_5s': lambda: burrow_room(5, 2),
}


def write(path, x):
    import soundfile as sf
    sf.write(path, np.asarray(x, np.float32), SR, subtype='PCM_24')


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(__file__), 'bank')
    os.makedirs(out, exist_ok=True)
    for name, fn in BANK.items():
        x = dc_block(fn())
        write(os.path.join(out, name + '.wav'), x)
    print(f'{len(BANK)} sounds -> {out}')
