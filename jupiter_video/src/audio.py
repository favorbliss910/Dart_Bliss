import sys, subprocess, math
import numpy as np
sys.path.insert(0, '.')
import scenes1 as S1, scenes2 as S2, scenes3 as S3
SR = 48000
UP = '/root/.claude/uploads/2ff7e691-2177-511a-be3d-6c8c56bb3218/'
VO = UP + '562c6c8f-jupiter_voiceover_am_michael.mp3'
M_DRAMA = UP + 'd59bc489-musicdream-dramatic-cinematic-documentary-609202.mp3'
M_SUSP = UP + '16c6ea4b-sub_clair-suspense-cinematic-633037.mp3'
M_INSP = UP + '3dc10482-tunetank-inspiring-cinematic-music-409347.mp3'
END = S3.END_T
N = int(END * SR) + SR
rng = np.random.default_rng(1)

def load(path, filt=None):
    cmd = ['ffmpeg', '-v', 'error', '-i', path]
    if filt: cmd += ['-af', filt]
    cmd += ['-ac', '2', '-ar', str(SR), '-f', 'f32le', '-']
    a = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32)
    return a.reshape(-1, 2).copy()

def db(x): return 10 ** (x / 20)

def fade_env(n, fin, fout):
    e = np.ones(n, np.float32)
    fi, fo = int(fin * SR), int(fout * SR)
    if fi > 0: e[:fi] = np.linspace(0, 1, fi) ** 2 if fi <= n else e[:fi]
    if fo > 0: e[-fo:] *= np.linspace(1, 0, fo) ** 1.5
    return e

def place(bus, clip, t0, gain=1.0):
    i0 = int(t0 * SR)
    if i0 < 0: clip = clip[-i0:]; i0 = 0
    n = min(len(clip), len(bus) - i0)
    if n > 0: bus[i0:i0 + n] += clip[:n] * gain


# simple filters via FFT (offline, fine for clips)
def fft_filter(x, lo=None, hi=None):
    n = len(x); X = np.fft.rfft(x, axis=0); f = np.fft.rfftfreq(n, 1 / SR)
    m = np.ones_like(f)
    if lo: m *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi: m *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(X * (m[:, None] if x.ndim == 2 else m), n=n, axis=0).astype(np.float32)

def noise(dur, st=True):
    n = int(dur * SR)
    return rng.standard_normal((n, 2) if st else n).astype(np.float32)

def st(x): return np.stack([x, x], 1)

def tvec(dur): return np.arange(int(dur * SR)) / SR

# ------------------------------------------------------------------ SFX generators
def boom(dur=3.0, f0=70, f1=28, amp=1.0, noise_amt=.5, hi=900):
    t = tvec(dur)
    f = f1 + (f0 - f1) * np.exp(-t * 3)
    ph = 2 * np.pi * np.cumsum(f) / SR
    sub = np.sin(ph) * np.exp(-t * 1.6)
    nz = fft_filter(noise(dur, False), hi=hi) * np.exp(-t * 6) * noise_amt
    x = (sub + nz) * amp
    x[:200] *= np.linspace(0, 1, 200)
    return st(x.astype(np.float32))

def whoosh(dur=0.6, lo=300, hi=4000, amp=.5, peak=.55):
    t = tvec(dur)
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2
    env = np.where(t / dur < peak, (t / dur / peak) ** 2, ((1 - t / dur) / (1 - peak)) ** 1.5)
    n = fft_filter(noise(dur), lo=lo, hi=hi)
    n /= np.abs(n).max() + 1e-9
    pan = np.stack([1 - .3 * t / dur, .7 + .3 * t / dur], 1)
    return (n * env[:, None] * pan * amp).astype(np.float32)

def riser(dur=4.0, amp=.35):
    t = tvec(dur)
    f = 120 * (2 ** (3 * t / dur))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * .5 + np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR) * .3
    n = fft_filter(noise(dur, False), lo=800, hi=9000) * .6
    env = (t / dur) ** 2.2
    x = (s + n * (t / dur)) * env * amp
    x[-400:] *= np.linspace(1, 0, 400)
    return st(x.astype(np.float32))

def blip(f=1200, dur=.09, amp=.25):
    t = tvec(dur)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t * 40) * amp
    return st(x.astype(np.float32))

def ui_pop(amp=.18):
    return blip(1800, .06, amp) + np.pad(blip(2400, .05, amp * .6), ((int(.03 * SR), 0), (0, 0)))[:int(.06 * SR)]

def alarm(dur=1.2, amp=.18):
    t = tvec(dur)
    f = np.where((t * 4) % 1 < .5, 880, 660)
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * .3 + np.sin(2 * np.pi * np.cumsum(f) / SR) * .7
    x = fft_filter(x, hi=3000) * amp * fade_env(len(t), .02, .1)
    return st(x.astype(np.float32))

def tone(f, dur, amp, fin=.01, fout=.2):
    t = tvec(dur)
    return st((np.sin(2 * np.pi * f * t) * amp * fade_env(len(t), fin, fout)).astype(np.float32))

def static(dur, amp=.25):
    n = fft_filter(noise(dur), lo=1500, hi=8000)
    n /= np.abs(n).max()
    gate = (rng.random(int(dur * 60)) > .3).repeat(SR // 60)[:len(n)]
    gate = np.pad(gate, (0, len(n) - len(gate)))
    return (n * gate[:, None] * amp * fade_env(len(n), .005, .1)[:, None]).astype(np.float32)

def rumble(dur, amp, lo=25, hi=220, mod=.5):
    t = tvec(dur)
    n = fft_filter(noise(dur), lo=lo, hi=hi); n /= np.abs(n).max()
    m = 1 + mod * np.sin(2 * np.pi * .7 * t)[:, None]
    return (n * m * amp).astype(np.float32)

def creak(dur=1.4, amp=.3, f0=90):
    t = tvec(dur)
    f = f0 * (1 + .25 * np.sin(2 * np.pi * .6 * t)) * (1 - .2 * t / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = (np.sin(ph) + .5 * np.sin(2 * ph * 1.01) + .3 * np.sin(3.7 * ph)) * (1 + .5 * np.sin(2 * np.pi * 23 * t))
    x = x * fade_env(len(t), .08, .5) * amp
    return st(fft_filter(x.astype(np.float32), lo=60, hi=1500))

def shimmer(dur, amp=.12):
    t = tvec(dur); x = np.zeros(len(t), np.float32)
    for f in (1760, 2217, 2637, 3520, 4186):
        x += np.sin(2 * np.pi * f * t + rng.random() * 6) * (0.5 + .5 * np.sin(2 * np.pi * rng.uniform(.3, 1.2) * t))
    x = x / 5 * amp * fade_env(len(t), dur * .3, dur * .4)
    return np.stack([x, np.roll(x, 900)], 1).astype(np.float32)

def crackle(dur, amp=.2, rate=25):
    n = int(dur * SR); x = np.zeros((n, 2), np.float32)
    k = int(rate * dur)
    for i in range(k):
        p = rng.integers(0, n - 2000); L = rng.integers(200, 1500)
        b = fft_filter(rng.standard_normal(L).astype(np.float32), lo=2000, hi=12000) * np.exp(-np.arange(L) / (L / 5))
        pan = rng.random()
        x[p:p + L, 0] += b * (1 - pan) * amp; x[p:p + L, 1] += b * pan * amp
    return x * fade_env(n, .5, .8)[:, None]

def hum(dur, amp=.12, f=55):
    t = tvec(dur)
    x = (np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * 2 * f * t + 1) + .25 * np.sin(2 * np.pi * 3.01 * f * t)) * (1 + .3 * np.sin(2 * np.pi * .25 * t))
    return st((x * amp * fade_env(len(t), 1.5, 2.0) / 1.75).astype(np.float32))

def drone(dur, amp=.15, fs=(55, 82.4, 110)):
    t = tvec(dur); x = np.zeros(len(t))
    for i, f in enumerate(fs):
        x += np.sin(2 * np.pi * f * t * (1 + .002 * np.sin(2 * np.pi * .1 * t + i)))
    x = x / len(fs)
    n = fft_filter(noise(dur, False), lo=100, hi=600) * .15
    y = (x + n) * amp * fade_env(len(t), 2.5, 3.0)
    return np.stack([y, np.roll(y, 1200)], 1).astype(np.float32)

def wind(dur, amp=.12, hi=1200):
    t = tvec(dur)
    n = fft_filter(noise(dur), lo=150, hi=hi); n /= np.abs(n).max()
    m = (0.6 + .4 * np.sin(2 * np.pi * .13 * t) * np.sin(2 * np.pi * .07 * t + 1))[:, None]
    return (n * m * amp * fade_env(len(t), 1.0, 1.5)[:, None]).astype(np.float32)

def chute_snap(amp=.4):
    w = whoosh(.7, 400, 6000, amp * .7, .8)
    t = tvec(.25); snap = fft_filter(noise(.25, False), lo=200, hi=3000) * np.exp(-t * 25) * amp
    out = np.zeros((int(.95 * SR), 2), np.float32)
    out[:len(w)] += w; out[int(.68 * SR):int(.68 * SR) + len(snap)] += st(snap.astype(np.float32))
    return out

def thud(amp=.25):
    return boom(.5, 140, 60, amp, .3, hi=600)

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
def cue(track, t_prog, t_track, dur, fin, fout, gain_db):
    seg = track[int(t_track * SR):int((t_track + dur) * SR)]
    seg = seg * fade_env(len(seg), fin, fout)[:, None]
    place(mus, seg, t_prog, db(gain_db))
cue(drama, 0.0, 0.0, S2.T_HIT + 1.0, .05, 3.0, -3)
cue(susp, S2.T_FIRST - 1.0, 0.0, S2.T_LOST - S2.T_FIRST + 1.0, 4.0, .25, -6)
cue(drama, S2.T_CONTINUE - .3, 28.0, S3.T_CENTER - S2.T_CONTINUE + 2.5, 3.0, 3.0, -4)
cue(susp, S3.T_CENTER + .5, 40.0, S3.T_BACK - S3.T_CENTER + 1.0, 4.0, 2.5, -9)
ti = S3.T_BACK - 1.0
cue(insp, ti, 14.0, END - ti, 3.0, 4.0, -2)

# ------------------------------------------------------------------ voice
vo = load(VO, 'highpass=f=70,equalizer=f=3000:t=q:w=1.2:g=1.5,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2')
voice = np.zeros((N, 2), np.float32); place(voice, vo, 0.0)
# ducking envelope from VO
mono = np.abs(voice[:, 0])
win = int(.02 * SR)
env = np.sqrt(np.convolve(mono ** 2, np.ones(win) / win, 'same'))
env = np.clip(env / (np.percentile(env[env > 1e-4], 90) + 1e-9), 0, 1)
# attack/release smoothing
sm = np.empty_like(env); a_att = math.exp(-1 / (.03 * SR)); a_rel = math.exp(-1 / (.45 * SR)); s = 0.0
step = 48
for i in range(0, len(env), step):
    v = env[i]; a = a_att if v > s else a_rel
    s = a ** step * s + (1 - a ** step) * v
    sm[i:i + step] = s
duck = 1 - .62 * np.clip(sm * 1.4, 0, 1)
mus *= duck[:, None]
amb *= (1 - .45 * np.clip(sm * 1.4, 0, 1))[:, None]

mix = voice * db(0) + mus * db(-9) + sfx * db(-3) + amb * db(-4)
np.clip(mix, -4, 4, out=mix)
out = '../out/mix_raw.wav'
import wave
pcm = (np.clip(mix / max(1.0, np.abs(mix).max()), -1, 1) * 32767).astype(np.int16)
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
# stems for reference
print('peak', np.abs(mix).max(), 'dur', len(mix) / SR)
