"""Procedural sound effects (no internet sound libraries needed).

    python sfx.py <kind> <seconds> <out.wav>
kinds: rain | roomtone | whoosh | riser | heartbeat | ding | register

These are starting points for the Sound Design Book; real foley or licensed
libraries can replace them later without changing the pipeline.
"""
import sys
import wave

import numpy as np

SR = 44100


def onepole(x, a):
    # vectorised approximation via FFT filtering
    n = len(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    fc = a * SR / (2 * np.pi)
    h = 1 / np.sqrt(1 + (f / max(fc, 1)) ** 2)
    return np.fft.irfft(np.fft.rfft(x) * h, n)


def rain(sec):
    n = int(sec * SR)
    noise = np.random.randn(n, 2)
    bed = np.stack([onepole(noise[:, c], 0.35) - onepole(noise[:, c], 0.02) for c in range(2)], 1) * 0.25
    drops = np.zeros((n, 2))
    for _ in range(int(sec * 120)):
        i = np.random.randint(0, n - 800)
        env = np.exp(-np.linspace(0, 9, 800))
        drops[i:i + 800, np.random.randint(2)] += np.random.randn(800) * env * np.random.uniform(0.05, 0.3)
    return bed + drops


def roomtone(sec):
    n = int(sec * SR)
    x = np.stack([onepole(np.random.randn(n), 0.01) for _ in range(2)], 1)
    hum = 0.02 * np.sin(2 * np.pi * 60 * np.arange(n) / SR)
    return x * 0.6 + hum[:, None]


def whoosh(sec):
    n = int(sec * SR)
    t = np.linspace(0, 1, n)
    env = np.sin(np.pi * t) ** 2
    x = np.random.randn(n)
    # sweep the filter cutoff up then down for the "pass-by" feel
    out = np.zeros(n)
    seg = 2048
    for s in range(0, n, seg):
        a = 0.05 + 0.6 * env[s]
        out[s:s + seg] = onepole(x[s:s + seg], a)[: len(out[s:s + seg])]
    pan = np.clip(t, 0, 1)
    return np.stack([out * env * (1 - pan), out * env * pan], 1) * 0.9


def riser(sec):
    n = int(sec * SR)
    t = np.arange(n) / SR
    f = 80 + 600 * (t / sec) ** 2
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3 + onepole(np.random.randn(n), 0.3) * (t / sec) * 0.4
    return np.stack([tone, tone], 1) * (t / sec)[:, None]


def heartbeat(sec):
    n = int(sec * SR)
    out = np.zeros(n)
    beat = int(SR * 0.85)
    for start in range(0, n - SR // 2, beat):
        for off, g in ((0, 1.0), (int(SR * 0.22), 0.7)):
            m = min(4000, n - start - off)
            tt = np.arange(m) / SR
            out[start + off:start + off + m] += g * np.sin(2 * np.pi * 55 * tt) * np.exp(-tt * 25)
    return np.stack([out, out], 1)


def ding(sec):
    n = int(sec * SR)
    t = np.arange(n) / SR
    x = sum(a * np.sin(2 * np.pi * f * t) for f, a in ((1320, 1), (2640, 0.4), (3960, 0.15))) * np.exp(-t * 4)
    return np.stack([x, x], 1) * 0.4


def register(sec):
    x = ding(sec)
    n = len(x)
    clunk = np.zeros(n)
    m = min(3000, n)
    clunk[:m] = np.random.randn(m) * np.exp(-np.linspace(0, 12, m))
    return x + np.stack([clunk, clunk], 1) * 0.5


def write(path, x):
    x = x / max(1e-9, np.abs(x).max()) * 0.89
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


if __name__ == "__main__":
    kind, sec, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    write(out, globals()[kind](sec))
    print("wrote", out)
