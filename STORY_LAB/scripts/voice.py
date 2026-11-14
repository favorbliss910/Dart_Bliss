"""Generate the voiceover for one story with Kokoro (am_michael) + word timings.

usage: python voice.py <story_dir>
reads  <story_dir>/vo_chunks.txt   (mood | text, blank line = paragraph break)
writes <story_dir>/audio/voice.wav, voice.mp3, timing.json

Word timings: Kokoro gives no timestamps, so each chunk is rendered on its own
(chunk start/end are exact), split into phrases at punctuation, the phrases are
snapped to the silences found in that chunk's audio, and words inside a phrase
are spread by phoneme count.
"""
import json, os, re, subprocess, sys
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

MODELS = os.environ.get("KOKORO_DIR", "/home/user/models")
VOICE = "am_michael"
SPEED = {"hook": 1.10, "normal": 1.16, "turn": 1.08, "dread": 1.04, "final": 1.00}
GAP = 0.22        # silence between chunks (s)
PARA_GAP = 0.40   # silence between paragraphs (s)
LEAD, OUTRO = 0.25, 1.6
SR = 24000


def load_chunks(path):
    chunks, para = [], 0
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            para += 1
            continue
        mood, text = [s.strip() for s in line.split("|", 1)]
        chunks.append({"mood": mood, "text": text, "para": para})
    return chunks


def trim(a, thr=0.008):
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx) == 0:
        return a
    return a[max(0, idx[0] - 240): idx[-1] + 1200]


def silences(a, min_len=0.09, thr=0.012):
    """return list of (start,end) seconds of silent stretches inside a."""
    win = int(SR * 0.01)
    n = len(a) // win
    env = np.sqrt(np.mean(a[: n * win].reshape(n, win) ** 2, axis=1))
    quiet = env < thr
    out, s = [], None
    for i, q in enumerate(quiet):
        if q and s is None:
            s = i
        if not q and s is not None:
            if (i - s) * 0.01 >= min_len:
                out.append((s * 0.01, i * 0.01))
            s = None
    return out


def phrases(text):
    # split after , . ? ! ... ; keep punctuation with the word
    words = text.split()
    groups, cur = [], []
    for w in words:
        cur.append(w)
        if re.search(r"[,.?!;:]$|\.\.\.$", w):
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    return groups


def main(story):
    global SPEED, GAP, PARA_GAP
    cfg = f"{story}/voice.json"
    if os.path.exists(cfg):  # per-story pacing (e.g. slower documentary read)
        c = json.load(open(cfg))
        SPEED = {**SPEED, **c.get("speed", {})}
        GAP, PARA_GAP = c.get("gap", GAP), c.get("para_gap", PARA_GAP)
    kok = Kokoro(f"{MODELS}/kokoro-v1.0.onnx", f"{MODELS}/voices-v1.0.bin")
    chunks = load_chunks(f"{story}/vo_chunks.txt")
    os.makedirs(f"{story}/audio", exist_ok=True)
    out = [np.zeros(int(LEAD * SR), np.float32)]
    t = LEAD
    words_out, chunk_out = [], []
    prev_para = 0
    for ci, ch in enumerate(chunks):
        if ci:
            g = PARA_GAP if ch["para"] != prev_para else GAP
            out.append(np.zeros(int(g * SR), np.float32))
            t += g
        prev_para = ch["para"]
        a, sr = kok.create(ch["text"], voice=VOICE, speed=SPEED[ch["mood"]], lang="en-us")
        assert sr == SR
        a = trim(a.astype(np.float32))
        dur = len(a) / SR
        # --- align phrases to silences
        groups = phrases(ch["text"])
        sil = [s for s in silences(a) if s[0] > 0.15 and s[1] < dur - 0.1]
        weights = [sum(len(kok.tokenizer.phonemize(w.strip(".,?!;:"))) + 1 for w in g) for g in groups]
        tot = sum(weights)
        # expected boundaries
        exp, acc = [], 0
        for wt in weights[:-1]:
            acc += wt
            exp.append(acc / tot * dur)
        bounds = []  # (end_of_phrase, start_of_next)
        used = set()
        for e in exp:
            best, bd = None, 0.6
            for si, (s0, s1) in enumerate(sil):
                if si in used:
                    continue
                d = abs((s0 + s1) / 2 - e)
                if d < bd:
                    best, bd = si, d
            if best is None:
                bounds.append((e, e))
            else:
                used.add(best)
                bounds.append(sil[best])
        # keep monotonic
        starts = [0.0] + [b[1] for b in bounds]
        ends = [b[0] for b in bounds] + [dur]
        for i in range(1, len(starts)):
            starts[i] = max(starts[i], ends[i - 1])
        for gi, g in enumerate(groups):
            s0, s1 = starts[gi], max(ends[gi], starts[gi] + 0.1)
            ws = [len(kok.tokenizer.phonemize(w.strip(".,?!;:"))) + 1 for w in g]
            tw, acc = sum(ws), 0
            for w, wt in zip(g, ws):
                words_out.append({"w": w, "s": round(t + s0 + (s1 - s0) * acc / tw, 3),
                                  "e": round(t + s0 + (s1 - s0) * (acc + wt) / tw, 3), "chunk": ci})
                acc += wt
        chunk_out.append({"i": ci, "mood": ch["mood"], "text": ch["text"], "s": round(t, 3), "e": round(t + dur, 3)})
        out.append(a)
        t += dur
        print(f"  [{ch['mood']:6}] {dur:5.2f}s  {ch['text'][:60]}")
    out.append(np.zeros(int(OUTRO * SR), np.float32))
    audio = np.concatenate(out)
    audio = audio / max(1e-6, np.abs(audio).max()) * 0.89
    sf.write(f"{story}/audio/voice.wav", audio, SR)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{story}/audio/voice.wav",
                    "-b:a", "192k", f"{story}/audio/voice.mp3"], check=True)
    total = len(audio) / SR
    nw = len(words_out)
    json.dump({"voice": f"kokoro/{VOICE}", "duration": round(total, 3), "speech_end": round(t, 3),
               "chunks": chunk_out, "words": words_out}, open(f"{story}/audio/timing.json", "w"), indent=1)
    print(f"{story}: {nw} words, speech {t:.1f}s, total {total:.1f}s, {nw / (t - LEAD) * 60:.0f} wpm")


if __name__ == "__main__":
    for s in sys.argv[1:]:
        main(s.rstrip("/"))
