"""Speak any text in the "Abel" voice with Kokoro TTS (CPU only, no GPU).

Abel is a custom Kokoro voice (abel_voice.npy) tuned to match the reference
recordings in reference/.

Setup:
    pip install kokoro-onnx soundfile
    Kokoro model: kokoro-q8.onnx (from the npm package kokoro-q8-shards:
    join kokoro-q8.part0.bin ... part5.bin in order into one file).

Usage:
    python abel_speak.py "Hello, my name is Abel." -o abel_hello.wav
    python abel_speak.py -f script.txt -o voiceover.wav --speed 1.1
"""
import argparse
import os

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    p = argparse.ArgumentParser(description="Abel voice (Kokoro)")
    p.add_argument("text", nargs="?", help="text to speak")
    p.add_argument("-f", "--file", help="read the text from a file instead")
    p.add_argument("-o", "--out", default="abel_output.wav")
    p.add_argument("--speed", type=float, default=1.0, help="1.0 normal, 1.2 faster")
    p.add_argument("--model", default=os.environ.get("KOKORO_MODEL", "/root/kokoro/kokoro-q8.onnx"))
    p.add_argument("--voices", default=os.environ.get("KOKORO_VOICES", "/root/kokoro/voices.npz"))
    args = p.parse_args()

    text = open(args.file, encoding="utf-8").read() if args.file else args.text
    if not text:
        p.error("give some text or -f FILE")

    abel = np.load(os.path.join(HERE, "abel_voice.npy")).astype(np.float32)
    tts = Kokoro(args.model, args.voices)
    audio, sr = tts.create(text, voice=abel, speed=args.speed, lang="en-us")
    sf.write(args.out, audio, sr)
    print(f"Abel said it -> {args.out} ({len(audio) / sr:.1f}s)")


if __name__ == "__main__":
    main()
