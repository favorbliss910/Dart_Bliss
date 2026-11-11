#!/usr/bin/env bash
# One-time setup: Python deps + Kokoro (am_michael) + Whisper word-timing model.
# Usage:  bash scripts/setup.sh
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT=$(pwd)
mkdir -p models

echo "== Checking ffmpeg"
command -v ffmpeg >/dev/null || { echo "Install ffmpeg first (needs libass): brew install ffmpeg / sudo apt install ffmpeg / winget install ffmpeg"; exit 1; }
ffmpeg -hide_banner -filters 2>/dev/null | grep -q " ass " || echo "WARNING: your ffmpeg lacks libass - captions will fail. Install a full build."

echo "== Python packages"
python3 -m pip install -r requirements.txt

echo "== Kokoro TTS model"
if [ ! -f models/kokoro-v1.0.onnx ] && [ ! -f models/kokoro-q8.onnx ]; then
  BASE=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
  if curl -fL --retry 3 -o models/kokoro-v1.0.onnx.part "$BASE/kokoro-v1.0.onnx" \
     && curl -fL --retry 3 -o models/voices-v1.0.bin "$BASE/voices-v1.0.bin"; then
    mv models/kokoro-v1.0.onnx.part models/kokoro-v1.0.onnx
    echo "   downloaded official Kokoro v1.0 (fp32)"
  else
    rm -f models/kokoro-v1.0.onnx.part
    echo "   GitHub blocked - using npm mirror of onnx-community/Kokoro-82M-v1.0-ONNX (q8)"
    TMP=$(mktemp -d)
    (cd "$TMP" && npm pack -q kokoro-q8-shards@1.0.0 kokoro-js@1.2.1 >/dev/null \
      && tar xzf kokoro-q8-shards-1.0.0.tgz && mkdir js && tar xzf kokoro-js-1.2.1.tgz -C js)
    cat "$TMP"/package/kokoro-q8.part{0,1,2,3,4,5}.bin > models/kokoro-q8.onnx
    echo "fbae9257e1e05ffc727e951ef9b9c98418e6d79f1c9b6b13bd59f5c9028a1478  models/kokoro-q8.onnx" | sha256sum -c -
    python3 - "$TMP/js/package/voices" "$ROOT/models/voices-en.bin" <<'EOF'
import sys, os, numpy as np
d, out = sys.argv[1], sys.argv[2]
v = {f[:-4]: np.fromfile(os.path.join(d, f), dtype=np.float32).reshape(-1, 1, 256)
     for f in sorted(os.listdir(d)) if f[:3] in ("am_", "af_", "bm_", "bf_")}
with open(out, "wb") as fh:
    np.savez(fh, **v)
print("   voices:", len(v), "(includes am_michael)" if "am_michael" in v else "MISSING am_michael")
EOF
    rm -rf "$TMP"
  fi
fi

echo "== Whisper (word timings)"
if [ ! -d models/whisper-small ]; then
  if python3 -c "from faster_whisper import WhisperModel; WhisperModel('small.en', device='cpu', compute_type='int8')" 2>/dev/null; then
    echo "   faster-whisper small.en cached by Hugging Face hub"
  else
    echo "   Hugging Face blocked - using npm mirror (Whisper small, CTranslate2 int8)"
    TMP=$(mktemp -d); mkdir -p models/whisper-small
    (cd "$TMP" && for i in 0 1 2 3; do npm pack -q "@skillninja/shortmovie-telop-model-p$i@1.0.0" >/dev/null; mkdir p$i; tar xzf skillninja-shortmovie-telop-model-p$i-1.0.0.tgz -C p$i; done)
    cp "$TMP"/p0/package/{config.json,preprocessor_config.json,tokenizer.json,vocabulary.json} models/whisper-small/
    cat "$TMP"/p0/package/model.bin.part0 "$TMP"/p1/package/model.bin.part1 "$TMP"/p2/package/model.bin.part2 "$TMP"/p3/package/model.bin.part3 > models/whisper-small/model.bin
    echo "ca732cb1379efc49417d028465f543d83a39de2c61f3027678de103dc404ce73  models/whisper-small/model.bin" | sha256sum -c -
    rm -rf "$TMP"
  fi
fi

echo "== Smoke test"
python3 - <<'EOF'
from studio import tts
a = tts.synth("Setup complete. The narrator is ready.")
print(f"   am_michael OK ({len(a)/48000:.1f}s of audio)")
EOF
echo "Done. Try: python3 -m studio.make_short specs/example_lighthouse.json --preview"
