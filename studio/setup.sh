#!/usr/bin/env bash
# One-shot environment setup for the animation studio (cloud container or Linux box).
# Re-run in every fresh cloud session: the container is wiped between sessions.
#   bash studio/setup.sh
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== system libraries (headless OpenGL/EGL for Blender, ffmpeg) =="
if command -v apt-get >/dev/null; then
  SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"
  $SUDO apt-get update -qq
  DEBIAN_FRONTEND=noninteractive $SUDO apt-get install -y -qq \
    ffmpeg libegl1 libgl1 libegl-mesa0 libgl1-mesa-dri libxkbcommon0 \
    libsm6 libxi6 libxxf86vm1 libxfixes3 libxrender1 >/dev/null
fi

echo "== python venv with Blender-as-a-module (bpy) =="
PY=${PYTHON:-python3.13}
command -v "$PY" >/dev/null || PY=python3
if command -v uv >/dev/null; then
  [ -d .venv ] || uv venv -q --python "$PY" .venv
  uv pip install -q --python .venv/bin/python -r studio/requirements.txt
else
  [ -d .venv ] || "$PY" -m venv .venv
  .venv/bin/pip install -q -r studio/requirements.txt
fi

echo "== smoke test =="
.venv/bin/python - <<'EOF'
import bpy, PIL, numpy
print("Blender", bpy.app.version_string, "| Pillow", PIL.__version__, "| numpy", numpy.__version__)
EOF
ffmpeg -version | head -1
echo "Ready. Try: .venv/bin/python studio/pipeline/render_shot.py studio/shots/test_counter.json studio/renders/test --preview --still"
