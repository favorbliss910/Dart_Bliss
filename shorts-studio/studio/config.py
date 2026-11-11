"""Paths and global defaults. Override any path with an environment variable."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS = Path(os.environ.get("SHORTS_MODELS", ROOT / "models"))
OUTPUT = Path(os.environ.get("SHORTS_OUTPUT", ROOT / "output"))
ASSETS = Path(os.environ.get("SHORTS_ASSETS", ROOT / "assets"))
SFX_LIBRARY = Path(os.environ.get("SHORTS_SFX_LIBRARY", ROOT / "sfx_library"))
FONTS = ROOT / "studio" / "assets" / "fonts"


def _first_existing(*cands: Path) -> Path:
    for c in cands:
        if c.exists():
            return c
    return cands[0]


KOKORO_MODEL = Path(os.environ.get("KOKORO_MODEL", _first_existing(
    MODELS / "kokoro-v1.0.onnx", MODELS / "kokoro-v1.0.int8.onnx", MODELS / "kokoro-q8.onnx")))
KOKORO_VOICES = Path(os.environ.get("KOKORO_VOICES", _first_existing(
    MODELS / "voices-v1.0.bin", MODELS / "voices-en.bin")))
# faster-whisper model: a local folder, or a name like "small.en" that it downloads itself.
WHISPER_MODEL = os.environ.get("WHISPER_MODEL", str(_first_existing(MODELS / "whisper-small", Path("small.en"))))

# ---- house style (all measured from the reference Shorts, see docs/ANALYSIS.md)
WIDTH, HEIGHT, FPS = 1080, 1920, 30
SR = 48000
DEFAULT_VOICE = "am_michael"
DEFAULT_SPEED = 1.18          # ~215-230 wpm while talking, matching the references
TARGET_LUFS = -14.0           # YouTube playback reference; refs measured -9..-17
TRUE_PEAK = -1.0
MUSIC_DB = -13.0              # bed level vs voice before ducking (refs: -11..-15 between words)
DUCK_DB = 5.0                 # extra music dip while the narrator speaks
