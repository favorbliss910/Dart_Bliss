"""Burned-in captions (ASS / libass), styled after the reference Shorts.

Measured house style:
  * 1-2 words on screen at a time, switching on the spoken word
  * heavy rounded sans (Inter ExtraBold here), white, thick dark outline + soft shadow
  * centred horizontally, ~68% down the frame (clear of the UI at the bottom)
  * key words / numbers in yellow; quick scale "pop" as each chunk appears
  * optional big overlay text near the top for numbers and time jumps
    ("208 FT", "YEARS LATER", "47 SCRATCHES")
"""
from __future__ import annotations

import re

from . import config

STYLE = {
    "font": "Inter ExtraBold",
    "size": 92,
    "y": 1290,                # vertical centre of caption line (of 1920)
    "words_per_chunk": 2,
    "uppercase": False,
    "color": "#FFFFFF",
    "highlight": "#FFD60A",   # yellow emphasis
    "outline": 7,
    "shadow": 3,
    "overlay_font": "Inter Black",
    "overlay_size": 150,
    "overlay_y": 430,
}


def _ass_color(hex_rgb: str, alpha: int = 0) -> str:
    h = hex_rgb.lstrip("#")
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"&H{alpha:02X}{b}{g}{r}".upper()


def _ts(t: float) -> str:
    t = max(0.0, t)
    h = int(t // 3600)
    m = int(t % 3600 // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def _esc(s: str) -> str:
    return s.replace("{", "(").replace("}", ")").replace("\\", "/")


def _is_number(w: str) -> bool:
    return bool(re.search(r"\d", w))


def chunk_words(words: list[dict], emphasis: set[str], per_chunk: int) -> list[list[dict]]:
    """Group words into on-screen chunks. Emphasis words and sentence ends break chunks."""
    chunks, cur = [], []
    for w in words:
        key = re.sub(r"[^a-z0-9']", "", w["word"].lower())
        is_emph = key in emphasis or _is_number(w["word"])
        if is_emph and cur:
            chunks.append(cur)
            cur = []
        cur.append({**w, "emph": is_emph})
        if is_emph or len(cur) >= per_chunk or w["word"][-1:] in ".!?,;:":
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    return chunks


def build_ass(timeline: dict, style: dict | None = None) -> str:
    st = {**STYLE, **(style or {})}
    W, H = 1080, 1920   # layout space; libass scales it to the real video size
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{st['font']},{st['size']},{_ass_color(st['color'])},&H000000FF,&H00101010,&H80000000,0,0,0,0,100,100,0,0,1,{st['outline']},{st['shadow']},5,60,60,0,1
Style: Over,{st['overlay_font']},{st['overlay_size']},{_ass_color(st['highlight'])},&H000000FF,&H00101010,&H80000000,0,0,0,0,100,100,1,0,1,9,4,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    hl = _ass_color(st["highlight"])
    x = W // 2
    for beat in timeline["beats"]:
        emph = {re.sub(r"[^a-z0-9']", "", e.lower()) for e in beat.get("emphasis", [])}
        chunks = chunk_words(beat["words"], emph, st["words_per_chunk"])
        for ci, ch in enumerate(chunks):
            start = ch[0]["start"]
            if ci + 1 < len(chunks):
                end = chunks[ci + 1][0]["start"]
            else:
                end = min(ch[-1]["end"] + 0.35, beat["end"] - 0.02)
            end = max(end, start + 0.12)
            parts = []
            for w in ch:
                txt = _esc(w["word"].upper() if st["uppercase"] else w["word"])
                parts.append(f"{{\\c{hl}}}{txt}{{\\r}}" if w["emph"] else txt)
            text = " ".join(parts)
            pop = "\\fscx118\\fscy118\\t(0,90,\\fscx100\\fscy100)" if any(w["emph"] for w in ch) else \
                  "\\fscx88\\fscy88\\t(0,70,\\fscx100\\fscy100)"
            lines.append(f"Dialogue: 1,{_ts(start)},{_ts(end)},Cap,,0,0,0,,{{\\pos({x},{st['y']}){pop}}}{text}")
        if beat.get("overlay"):
            s, e = beat["start"] + 0.05, beat["end"]
            anim = "\\fad(60,120)\\fscx40\\fscy40\\t(0,140,\\fscx108\\fscy108)\\t(140,220,\\fscx100\\fscy100)"
            lines.append(f"Dialogue: 2,{_ts(s)},{_ts(e)},Over,,0,0,0,,{{\\pos({x},{st['overlay_y']}){anim}}}{_esc(beat['overlay'])}")
    return head + "\n".join(lines) + "\n"
