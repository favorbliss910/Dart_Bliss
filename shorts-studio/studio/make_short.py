"""Render a Short from a spec JSON.

    python -m studio.make_short specs/my_story.json            # full render
    python -m studio.make_short specs/my_story.json --preview  # fast, low-res motion
    python -m studio.make_short specs/my_story.json --audio-only

Outputs land in output/<slug>/:
    final.mp4        the Short (1080x1920, 30 fps, -14 LUFS)
    master.wav       final mix          stems/  voice, music, sfx
    shotlist.md      exact length of every beat -> generate visuals to fit
    timeline.json    word-level timings for every beat
    captions.ass     editable subtitles
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf

from . import align, captions, config, mix, music, tts, video

AUTO_TRANSITION_SFX = {"whip": "whoosh", "whip_right": "whoosh", "whip_up": "whoosh",
                       "zoom": "swish", "glitch": "glitch", "flash": "impact"}


HITS = {"impact", "boom", "braam"}


def _norm(w: str) -> str:
    return re.sub(r"[^a-z0-9]", "", w.lower())


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:60] or "short"


def build_timeline(spec: dict) -> tuple[dict, np.ndarray]:
    voice_name = spec.get("voice", config.DEFAULT_VOICE)
    base_speed = float(spec.get("speed", config.DEFAULT_SPEED))
    sr = config.SR
    pieces, beats, cursor = [], [], 0.0
    lead_in = float(spec.get("lead_in", 0.0))
    if lead_in:
        pieces.append(np.zeros(int(lead_in * sr), np.float32))
        cursor = lead_in
    for i, b in enumerate(spec["beats"]):
        vo = b["vo"].strip()
        say = b.get("say", vo)   # optional pronunciation override; captions still show `vo`
        audio = tts.synth(say, b.get("voice", voice_name), float(b.get("speed") or base_speed))
        words = align.align(vo, audio)
        dur = len(audio) / sr
        pause = float(b.get("pause_after", spec.get("pause_after", 0.12)))
        if i == len(spec["beats"]) - 1:
            pause = float(spec.get("tail", 0.6))
        beat = {k: v for k, v in b.items() if k != "words"}
        beat.update({
            "index": i + 1, "start": cursor, "speech_end": cursor + dur, "end": cursor + dur + pause,
            "words": [{"word": w["word"], "start": cursor + w["start"], "end": cursor + w["end"]} for w in words],
        })
        beats.append(beat)
        pieces += [audio, np.zeros(int(pause * sr), np.float32)]
        cursor += dur + pause
    voice = np.concatenate(pieces)
    return {"title": spec.get("title", ""), "duration": len(voice) / sr, "beats": beats}, voice


def resolve_sfx(timeline: dict, spec: dict) -> list[dict]:
    cues = []
    auto = spec.get("auto_sfx", True)
    for b in timeline["beats"]:
        explicit = {c["name"] for c in b.get("sfx", []) or []}
        auto_name = AUTO_TRANSITION_SFX.get(b.get("transition"))
        if auto_name in HITS and explicit & HITS:
            auto_name = "swish"   # an explicit hit is already planned; keep the transition light
        if auto and b["index"] > 1 and auto_name:
            cues.append({"name": auto_name, "time": b["start"], "auto": True})
        if auto and b.get("overlay"):
            cues.append({"name": "pop", "time": b["start"] + 0.06, "auto": True})
        if auto and b.get("music") == "drop":
            cues.append({"name": "reverse_swell", "time": b["start"], "auto": True})
        for c in b.get("sfx", []) or []:
            name = c["name"]
            if "on_word" in c:
                target = _norm(c["on_word"])
                hit = next((w for w in b["words"] if _norm(w["word"]).startswith(target)), None)
                if hit is None:
                    print(f"  ! beat {b['index']}: on_word '{c['on_word']}' not found, using beat start")
                    t = b["start"]
                else:
                    t = hit["start"]
            else:
                at = c.get("at", "start")
                t = b["start"] if at == "start" else b["speech_end"] if at == "end" else b["start"] + float(at)
            t += float(c.get("offset", 0))
            cue = {"name": name, "time": t}
            if "gain_db" in c:
                cue["gain_db"] = c["gain_db"]
            if "params" in c:
                cue["params"] = c["params"]
            cues.append(cue)
    # explicit cues win over auto cues of the same name within 150 ms
    final = []
    for c in sorted(cues, key=lambda c: (c["time"], c.get("auto", False))):
        if any(f["name"] == c["name"] and abs(f["time"] - c["time"]) < 0.15 for f in final):
            continue
        final.append(c)
    return final


def write_shotlist(timeline: dict, path: Path) -> None:
    lines = [f"# Shot list - {timeline['title']}", "",
             f"Total: {timeline['duration']:.2f}s · {len(timeline['beats'])} beats", "",
             "Save each visual as `beat_NN.png` (image) or `beat_NN.mp4` (clip) in the assets folder.",
             "Clips should be at least as long as the beat; extra length is trimmed.", ""]
    for b in timeline["beats"]:
        lines += [f"## beat_{b['index']:02d} · {b['end'] - b['start']:.2f}s "
                  f"({b['start']:.2f} → {b['end']:.2f}) · {b.get('motion', 'push_in')} · in: {b.get('transition', 'cut')}",
                  f"**VO:** {b['vo']}", "", f"**Visual:** {b.get('visual', '')}", ""]
        if b.get("overlay"):
            lines += [f"**Overlay text:** {b['overlay']}", ""]
    path.write_text("\n".join(lines))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("--assets", help="folder with beat_01.png / beat_01.mp4 ... (default assets/<slug>)")
    ap.add_argument("--out", help="output folder (default output/<slug>)")
    ap.add_argument("--audio-only", action="store_true")
    ap.add_argument("--preview", action="store_true", help="faster, lower-quality video render")
    ap.add_argument("--seed", type=int, default=None, help="music seed (same seed = same music)")
    a = ap.parse_args(argv)

    spec = json.loads(Path(a.spec).read_text())
    slug = spec.get("slug") or slugify(spec.get("title", Path(a.spec).stem))
    out = Path(a.out) if a.out else config.OUTPUT / slug
    assets = Path(a.assets) if a.assets else config.ASSETS / slug
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    print(f"[1/6] Voice: Kokoro {spec.get('voice', config.DEFAULT_VOICE)} @ {spec.get('speed', config.DEFAULT_SPEED)}x")
    timeline, voice = build_timeline(spec)
    words = sum(len(b["words"]) for b in timeline["beats"])
    print(f"      {timeline['duration']:.1f}s, {words} words, "
          f"{words / timeline['duration'] * 60:.0f} wpm overall")
    if timeline["duration"] > 60:
        print("      ! longer than 60 s - trim the script (Shorts sweet spot here is 30-60 s)")

    print("[2/6] Voice chain (EQ, de-ess, compression)")
    voice_p = mix.process_voice(voice)
    vpeak = float(np.max(np.abs(voice_p)))

    print("[3/6] Sound design")
    cues = resolve_sfx(timeline, spec)
    sfx_bus = mix.place_sfx(cues, timeline["duration"], vpeak)
    print(f"      {len(cues)} cues: " + ", ".join(f"{c['name']}@{c['time']:.1f}" for c in cues))

    print("[4/6] Music")
    bed = None
    if spec.get("music_file"):
        bed = mix.load_music_file(spec["music_file"], timeline["duration"])
        print(f"      using {spec['music_file']}")
    elif spec.get("mood", "mystery") != "none":
        drops = [b["start"] for b in timeline["beats"] if b.get("music") == "drop"]
        lifts = [b["start"] for b in timeline["beats"] if b.get("music") == "lift"]
        bed = music.generate(spec.get("mood", "mystery"), timeline["duration"], drops, lifts, seed=a.seed)
        print(f"      generated '{spec.get('mood', 'mystery')}' bed, drops at {[round(d, 1) for d in drops]}")

    print("[5/6] Mix + master")
    stats = mix.master(voice_p, bed, sfx_bus, out / "master.wav",
                       music_db=float(spec.get("music_db", config.MUSIC_DB)),
                       duck_db=float(spec.get("duck_db", config.DUCK_DB)))
    print(f"      {stats}")

    timeline["sfx"] = cues
    timeline["loudness"] = stats
    (out / "timeline.json").write_text(json.dumps(timeline, indent=1))
    write_shotlist(timeline, out / "shotlist.md")
    ass = captions.build_ass(timeline, spec.get("caption_style"))
    (out / "captions.ass").write_text(ass)

    if a.audio_only:
        print(f"Done (audio only) in {time.time() - t0:.0f}s -> {out}")
        return
    print(f"[6/6] Video ({'preview' if a.preview else 'final'}) from {assets}")
    video.render(timeline, assets, out / "captions.ass", out / "master.wav", out / "final.mp4",
                 out / "_work", preview=a.preview)
    print(f"Done in {time.time() - t0:.0f}s -> {out / 'final.mp4'}")


if __name__ == "__main__":
    sys.exit(main())
