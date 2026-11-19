"""Procedural score: synthesized instruments, a humanized sequencer and the
character motifs. Principle numbers in []."""
import numpy as np
from sfxlib import (SR, PI, rng, env_exp, fade, bp, lp, hp, svf_lp, pink, soft_clip, norm)

A4 = 440.0


def hz(midi):
    return A4 * 2 ** ((midi - 69) / 12)


def N(name):
    """'F4' / 'D#5' / 'Bb3' -> midi."""
    base = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}[name[0]]
    acc = name[1:-1]
    base += {'': 0, '#': 1, 'b': -1}[acc]
    return 12 * (int(name[-1]) + 1) + base


# ------------------------------------------------------------------ instruments [787-800]
def marimba(f, dur, vel, r):
    """Modal bar: partials 1:4:10, decays 0.6/0.15/0.05 s + mallet click [788]."""
    n = int(SR * min(dur + 0.6, 1.2))
    t = np.arange(n) / SR
    b = vel ** 0.7
    x = (np.sin(2 * PI * f * t) * np.exp(-t / 0.5)
         + 0.35 * b * np.sin(2 * PI * f * 3.93 * t) * np.exp(-t / 0.12)
         + 0.12 * b * np.sin(2 * PI * f * 9.9 * t) * np.exp(-t / 0.04))
    k = int(SR * 0.002)
    x[:k] += r.standard_normal(k) * 0.25 * b
    return x * vel


def pizz(f, dur, vel, r):
    """Karplus-Strong pluck with a closing low-pass [787, 790]."""
    n = int(SR * 0.6)
    p = max(2, int(SR / f))
    buf = r.uniform(-1, 1, p)
    out = np.empty(n)
    fb = 0.993
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = fb * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    out = lp(out, 2500 + 2500 * vel)
    return out * env_exp(n, 0.003, 0.25) * vel


def kalimba(f, dur, vel, r):  # [789]
    n = int(SR * 0.8)
    t = np.arange(n) / SR
    x = np.sin(2 * PI * f * t) * np.exp(-t / 0.35) + 0.25 * np.sin(2 * PI * f * 5.4 * t) * np.exp(-t / 0.04)
    return x * env_exp(n, 0.002, 0.5) * vel


def bass(f, dur, vel, r):
    """Reedy comic bassoon-ish bark: saw → resonant LP with filter env, saturated [791, 689]."""
    d = max(dur, 0.12)
    n = int(SR * (d + 0.08))
    t = np.arange(n) / SR
    saw = 2 * ((f * t) % 1) - 1
    cut = 350 + 900 * vel * np.exp(-t / 0.08)
    y = svf_lp(saw, cut, q=2.2)
    y = soft_clip(y * 1.5, 1.8)
    e = np.minimum(1, t / 0.004) * np.where(t < d, 1.0, np.exp(-(t - d) / 0.03))
    return y * e * vel * 0.8


def whistle(f, dur, vel, r):
    """Drongo's lead: sine with delayed 5.5 Hz vibrato + breath [793, 624]."""
    n = int(SR * (dur + 0.08))
    t = np.arange(n) / SR
    vib = 1 + 0.012 * np.minimum(1, np.maximum(0, t - 0.12) / 0.1) * np.sin(2 * PI * 5.5 * t)
    ph = 2 * PI * np.cumsum(f * vib) / SR
    x = np.sin(ph) + 0.05 * np.sin(2 * ph)
    x += bp(r.standard_normal(n), f * 0.9, f * 1.4) * 0.15
    e = np.minimum(1, t / 0.015) * np.where(t < dur, 1.0, np.exp(-(t - dur) / 0.03))
    return x * e * vel * 0.7


def clarinet(f, dur, vel, r):  # [794]
    n = int(SR * (dur + 0.06))
    t = np.arange(n) / SR
    vib = 1 + 0.006 * np.minimum(1, np.maximum(0, t - 0.2) / 0.2) * np.sin(2 * PI * 5 * t)
    ph = (np.cumsum(f * vib) / SR) % 1
    sq = np.where(ph < 0.5, 1.0, -1.0)
    x = lp(sq, 1600)
    e = np.minimum(1, t / 0.02) * np.where(t < dur, 1.0, np.exp(-(t - dur) / 0.03))
    return x * e * vel * 0.5


def brass(f, dur, vel, r):
    """Low brass swell for the hawk only [623, 795]."""
    n = int(SR * (dur + 0.3))
    t = np.arange(n) / SR
    x = sum(2 * ((f * (1 + d) * t) % 1) - 1 for d in (-0.004, 0, 0.005))
    cut = 250 + 900 * np.minimum(1, t / 0.4) * vel
    y = soft_clip(svf_lp(x / 3, cut, 0.9), 1.5)
    e = np.minimum(1, t / 0.25) * np.where(t < dur, 1.0, np.exp(-(t - dur) / 0.15))
    return y * e * vel


def woodblock(f, dur, vel, r):  # [792]
    n = int(SR * 0.08)
    t = np.arange(n) / SR
    return (np.sin(2 * PI * f * t) + 0.4 * np.sin(2 * PI * f * 2.7 * t)) * np.exp(-t / 0.025) * vel


def shaker(f, dur, vel, r):
    n = int(SR * 0.05)
    x = bp(r.standard_normal(n), 6000, 11000) * np.hanning(n) ** 0.5
    return x * vel * 0.35


def tom(f, dur, vel, r):  # [797]
    n = int(SR * 0.5)
    t = np.arange(n) / SR
    fr = f * (1 + 0.5 * np.exp(-t / 0.05))
    x = np.sin(2 * PI * np.cumsum(fr) / SR) * np.exp(-t / 0.2)
    x[: int(SR * 0.003)] += r.standard_normal(int(SR * 0.003)) * 0.3
    return soft_clip(x * vel * 1.4, 1.5)


def pad(f, dur, vel, r):
    """Detuned saws, dark, slow attack [796, 693]."""
    n = int(SR * (dur + 0.6))
    t = np.arange(n) / SR
    x = sum(2 * ((f * 2 ** (c / 1200) * t + r.random()) % 1) - 1 for c in (-11, -4, 0, 6, 12))
    y = lp(x / 5, 800)
    e = np.minimum(1, t / 0.5) * np.where(t < dur, 1.0, np.exp(-(t - dur) / 0.25))
    return y * e * vel


def shimmer(f, dur, vel, r):
    """Dawn glass: soft sine cluster, high-passed so it floats above the voice [693]."""
    n = int(SR * (dur + 0.8))
    t = np.arange(n) / SR
    x = np.sin(2 * PI * f * t) * (0.5 + 0.5 * np.sin(2 * PI * 0.7 * t + r.random() * 6))
    e = np.minimum(1, t / 0.4) * np.where(t < dur, 1.0, np.exp(-(t - dur) / 0.35))
    return x * e * vel * 0.5


INSTR = dict(marimba=marimba, pizz=pizz, kalimba=kalimba, bass=bass, whistle=whistle,
             clarinet=clarinet, brass=brass, woodblock=woodblock, shaker=shaker, tom=tom,
             pad=pad, shimmer=shimmer)

# per-instrument character placement [784]: drongo late, meerkats early
FEEL = dict(whistle=0.015, clarinet=0.012, marimba=-0.006, kalimba=-0.004)


class Seq:
    """Humanized sequencer [775-786]. Events: (time_s, instr, midi or Hz, dur_s, vel)."""

    def __init__(self, length, seed=7):
        self.n = int(SR * (length + 2))
        self.buses = {}
        self.r = rng(seed)

    def note(self, t, instr, pitch, dur=0.2, vel=0.7, bus=None, jitter=0.007):
        r = self.r
        f = hz(pitch) if pitch < 200 and isinstance(pitch, (int, np.integer)) else float(pitch)
        f *= 2 ** (r.normal(0, 4) / 1200)                      # ±cents [778]
        t = t + r.normal(0, jitter) + FEEL.get(instr, 0)      # onset jitter [775]
        vel = float(np.clip(vel * (1 + r.normal(0, 0.08)), 0.05, 1.2))
        dur = dur * (1 + r.normal(0, 0.12)) if instr in ('pizz', 'marimba') else dur  # [783]
        x = INSTR[instr](f, dur, vel, r)
        x = fade(x, 0.0015, 0.004)                             # click-free [799]
        b = bus or instr
        buf = self.buses.setdefault(b, np.zeros(self.n))
        i = int(SR * max(t, 0))
        e = min(self.n, i + len(x))
        buf[i:e] += x[: e - i]

    def get(self, bus):
        return self.buses.get(bus, np.zeros(self.n))


# ------------------------------------------------------------------ motifs [647-668]
def drongo_motif(seq, t, beat, octave=5, instr='whistle', vel=0.8, last=True, bus='lead'):
    """Sly zigzag: rising 4th, chromatic step down, rest, grace D#–E [649]."""
    o = 12 * (octave - 5)
    swing = beat * 0.58 * 2  # 58% swing on eighths [641]
    pts = [(0, N('C5')), (beat * 0.5 + 0.08 * beat, N('F5')), (beat * 1.0, N('E5'))]
    for dt, m in pts:
        seq.note(t + dt, instr, m + o, beat * 0.42, vel, bus)
    if last:  # withheld last note = suspense [662]
        seq.note(t + beat * 2.0, instr, N('D#5') + o, beat * 0.12, vel * 0.7, bus)
        seq.note(t + beat * 2.15, instr, N('E5') + o, beat * 0.7, vel, bus)


def meerkat_motif(seq, t, beat, pitch='C6', vel=0.6, bus='lead'):
    """Nervous repeated 16ths, quick step up [650]."""
    m = N(pitch)
    for k in range(4):
        seq.note(t + k * beat / 4, 'marimba', m, beat / 5, vel * (1.1 if k == 0 else 0.85), bus)
    seq.note(t + beat, 'marimba', m + 2, beat / 3, vel, bus)


def sentinel_motif(seq, t, beat, instr='marimba', vel=0.7, inverted=False, bus='lead'):
    """Lookout: rising 4th C→F, shared with the drongo theme [652, 657, 658]."""
    a, b = (N('C5'), N('F5')) if not inverted else (N('F5'), N('C5'))
    seq.note(t, instr, a, beat * 0.4, vel, bus)
    seq.note(t + beat * 0.5, instr, b, beat * 0.9, vel, bus)


def alarm_figure(seq, t, beat, reps=6, vel=0.7, bus='lead'):
    """One alarm figure for real AND fake alarms: rapid high minor 3rd [653]."""
    for k in range(reps):
        seq.note(t + k * beat / 4, 'marimba', N('A5') if k % 2 == 0 else N('C6'), beat / 6, vel, bus)


def hawk_motif(seq, t, beat, vel=0.8, bus='hawk'):
    """Slow falling minor 2nd, low brass, then silence [651]. E Phrygian F→E."""
    seq.note(t, 'brass', N('F2'), beat * 2.2, vel, bus)
    seq.note(t + beat * 2, 'brass', N('E2'), beat * 3, vel, bus)
    seq.note(t, 'tom', N('E2'), 0.3, vel * 0.8, 'perc')


def gliss(seq, t, up=True, steps=8, span=0.25, start='C5', vel=0.55, bus='lead'):
    """Marimba glissando for popping up / diving down [707]. F major scale."""
    scale = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17]
    m0 = N(start)
    notes = scale[:steps] if up else scale[:steps][::-1]
    for k, s in enumerate(notes):
        seq.note(t + k * span / steps, 'marimba', m0 + s, 0.08, vel * (0.7 + 0.3 * k / steps), bus, jitter=0.002)


def groove(seq, t0, t1, bpm, chords, density=2, swing=0.0, bass_pat='walk', seed=0):
    """Bed with a density ladder [677]: 1 pulse, 2 +bass, 3 +harmony (pizz shells), 4 +shaker 8ths.
    chords: list of root midi per bar (bass register)."""
    beat = 60 / bpm
    bar = beat * 4
    k = 0
    t = t0
    while t < t1 - 1e-3:
        root = chords[k % len(chords)]
        for b in range(4):
            tb = t + b * beat
            if tb >= t1:
                break
            if density >= 1:  # pulse: woodblock on 2 & 4, ghost notes [782]
                if b in (1, 3):
                    seq.note(tb, 'woodblock', 1050, 0.05, 0.35, 'perc')
                else:
                    seq.note(tb + beat * 0.5, 'woodblock', 1250, 0.05, 0.12, 'perc')
            if density >= 2:  # walking bass root–fifth, staccato [622]
                m = root if b in (0, 2) else root + 7
                if bass_pat == 'walk' or b == 0:
                    seq.note(tb, 'bass', m, beat * 0.42, 0.75 if b == 0 else 0.6, 'bass')
            if density >= 3 and b in (1, 3):  # thin shells [674]
                for iv in (16, 22):  # 3rd and 7th an octave up = shells
                    seq.note(tb + (beat * 0.5 * (swing - 0.5) * 2 if swing else 0), 'pizz', root + iv, beat * 0.3, 0.32, 'harm')
            if density >= 4:
                for h in (0, 0.5):
                    off = beat * (swing if h else 0) if swing else beat * h
                    seq.note(tb + off, 'shaker', 0, 0.04, 0.5 if h == 0 else 0.3, 'perc')
        t += bar
        k += 1
