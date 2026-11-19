"""Clone the "Abel" voice with Qwen3-TTS and speak any text in it.

Setup (needs access to huggingface.co; a GPU helps, CPU works but is slow):
    pip install -U qwen-tts torch soundfile

Usage:
    # 1) Build the Abel voice once (saves voices/abel.pt)
    python clone_abel.py build --ref reference/abel_ref_short.wav \
        --ref-text "exact words spoken in the reference clip"
    #    No transcript? Omit --ref-text and it uses speaker-embedding-only mode
    #    (works, but likeness is a bit lower).

    # 2) Speak with Abel
    python clone_abel.py say "Hello, my name is Abel." -o abel_hello.wav
"""
import argparse
import os

import soundfile as sf
import torch
from qwen_tts import Qwen3TTSModel

VOICE_NAME = "Abel"
HERE = os.path.dirname(os.path.abspath(__file__))
VOICE_FILE = os.path.join(HERE, "voices", "abel.pt")
DEFAULT_MODEL = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"  # use ...-0.6B-Base on CPU


def load_model(name):
    if torch.cuda.is_available():
        return Qwen3TTSModel.from_pretrained(name, device_map="cuda:0", dtype=torch.bfloat16)
    return Qwen3TTSModel.from_pretrained(name, device_map="cpu", dtype=torch.float32)


def build(args):
    model = load_model(args.model)
    prompt = model.create_voice_clone_prompt(
        ref_audio=args.ref,
        ref_text=args.ref_text,
        x_vector_only_mode=args.ref_text is None,
    )
    os.makedirs(os.path.dirname(VOICE_FILE), exist_ok=True)
    torch.save({"name": VOICE_NAME, "model": args.model, "prompt": prompt}, VOICE_FILE)
    print(f"Saved voice '{VOICE_NAME}' to {VOICE_FILE}")


def say(args):
    voice = torch.load(VOICE_FILE, weights_only=False)
    model = load_model(voice["model"])
    wavs, sr = model.generate_voice_clone(
        text=args.text,
        language=args.language,
        voice_clone_prompt=voice["prompt"],
    )
    sf.write(args.out, wavs[0], sr)
    print(f"{voice['name']} said it -> {args.out}")


def main():
    p = argparse.ArgumentParser(description="Qwen3-TTS voice clone: Abel")
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="create the Abel voice from reference audio")
    b.add_argument("--ref", default=os.path.join(HERE, "reference", "abel_ref_short.wav"))
    b.add_argument("--ref-text", default=None, help="transcript of the reference clip")
    b.add_argument("--model", default=DEFAULT_MODEL)
    b.set_defaults(func=build)

    s = sub.add_parser("say", help="speak text in Abel's voice")
    s.add_argument("text")
    s.add_argument("-o", "--out", default="abel_output.wav")
    s.add_argument("--language", default="English")
    s.set_defaults(func=say)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
