"""Break down any reference Short the same way docs/ANALYSIS.md was made.

    python -m studio.analyze_reference path/to/video1.mp4 path/to/video2.mp4

For each video, writes analysis/<name>/:
    transcript.txt     sentence timings      words.json   word-level timings
    sheet_NN.jpg       timestamped contact sheets (look at these!)
    spectrogram.png    music / SFX / silence at a glance
    metrics.json       wpm, speech coverage, first-word time, LUFS, bed level, cuts...
and prints a comparison table. Compare your own renders against references:
    python -m studio.analyze_reference output/my_story/final.mp4 refs/*.mp4
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.signal import resample_poly

from . import align, config


def _ff(*args) -> str:
    return subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-y", *args], capture_output=True, text=True).stderr


def analyze(video: Path, out_root: Path) -> dict:
    out = out_root / re.sub(r"[^A-Za-z0-9_-]+", "_", video.stem)[:60]
    out.mkdir(parents=True, exist_ok=True)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                               capture_output=True, text=True).stdout.strip())
    fps = 2 if dur <= 20 else 1
    _ff("-i", str(video), "-vf", f"fps={fps},scale=270:480,drawtext=text='%{{pts\\:hms}}':x=6:y=6:fontsize=22:"
        "fontcolor=yellow:box=1:boxcolor=black@0.7,tile=6x2:padding=4", str(out / "sheet_%02d.jpg"))
    _ff("-i", str(video), "-lavfi", "showspectrumpic=s=1200x300:legend=1:scale=log:fscale=log:stop=12000", str(out / "spectrogram.png"))
    cuts = re.findall(r"pts_time:([\d.]+)", _ff("-i", str(video), "-vf", "select='gt(scene,0.2)',showinfo", "-an", "-f", "null", "-"))
    loud = _ff("-i", str(video), "-vn", "-af", "ebur128=peak=true", "-f", "null", "-")
    summ = loud[loud.rfind("Summary:"):]
    lufs = float(re.search(r"I:\s+(-?[\d.]+)", summ).group(1))
    peak = float(re.search(r"Peak:\s+(-?[\d.]+)", summ).group(1))

    wav = out / "_audio.wav"
    _ff("-i", str(video), "-vn", "-ac", "1", "-ar", str(config.SR), str(wav))
    import soundfile as sf
    a, _ = sf.read(wav, dtype="float32")
    wav.unlink()
    words, segs_txt = [], []
    model = align._whisper()
    if model is not None:
        segs, _ = model.transcribe(resample_poly(a, 1, 3).astype(np.float32), word_timestamps=True, beam_size=5)
        for s in segs:
            segs_txt.append(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text.strip()}")
            words += [{"word": w.word.strip(), "start": round(w.start, 2), "end": round(w.end, 2)} for w in s.words]
    (out / "transcript.txt").write_text("\n".join(segs_txt))
    (out / "words.json").write_text(json.dumps(words, indent=1))

    hop = int(0.05 * config.SR)
    rms = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2) + 1e-12) for i in range(0, len(a) - hop, hop)])
    t = np.arange(len(rms)) * 0.05
    mask = np.zeros(len(rms), bool)
    for w in words:
        mask[(t >= w["start"] - 0.06) & (t <= w["end"] + 0.06)] = True
    db = 20 * np.log10(rms + 1e-9)
    talk = sum(w["end"] - w["start"] for w in words)
    m = {
        "video": video.name, "duration_s": round(dur, 2), "words": len(words),
        "wpm_overall": round(len(words) / dur * 60) if dur else 0,
        "wpm_while_talking": round(len(words) / talk * 60) if talk else 0,
        "speech_coverage_pct": round(100 * mask.mean()),
        "first_word_s": words[0]["start"] if words else None,
        "integrated_lufs": lufs, "true_peak_dbfs": peak,
        "bed_vs_voice_db": round(float(np.median(db[~mask]) - np.median(db[mask])), 1) if mask.any() and (~mask).sum() > 5 else None,
        "hard_cuts": len(cuts), "avg_shot_s": round(dur / (len(cuts) + 1), 2),
        "hook": segs_txt[0] if segs_txt else "",
    }
    (out / "metrics.json").write_text(json.dumps(m, indent=1))
    return m


def main(argv=None):
    args = argv or sys.argv[1:]
    if not args:
        print(__doc__)
        return 1
    out_root = config.ROOT / "analysis"
    rows = [analyze(Path(v), out_root) for v in args]
    cols = ["duration_s", "words", "wpm_while_talking", "speech_coverage_pct", "first_word_s",
            "integrated_lufs", "bed_vs_voice_db", "avg_shot_s"]
    print(f"{'video':40s} " + " ".join(f"{c[:12]:>12s}" for c in cols))
    for r in rows:
        print(f"{r['video'][:40]:40s} " + " ".join(f"{str(r[c]):>12s}" for c in cols))
    print(f"\nDetails, contact sheets and spectrograms in {out_root}/")


if __name__ == "__main__":
    sys.exit(main())
