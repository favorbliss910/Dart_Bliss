#!/usr/bin/env bash
# Toolchain for rendering SHORTS_KIT-style videos in a cloud session:
# Blender 5.2 (as the bpy Python module, Eevee on CPU), ffmpeg, a fallback voice.
# Paste the body into the environment's setup script, or run: bash shorts_env/setup.sh
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

apt-get update -qq
apt-get install -y -qq ffmpeg libegl1 libegl-mesa0 libgl1-mesa-dri mesa-vulkan-drivers \
  libvulkan1 libxrender1 libxi6 libxkbcommon0 libsm6 libxfixes3 libsndfile1 \
  espeak-ng fonts-dejavu-core >/dev/null

mkdir -p /opt/shorts
[ -x /opt/shorts/venv/bin/python ] || uv venv --python 3.13 /opt/shorts/venv
uv pip install --python /opt/shorts/venv/bin/python "bpy==5.2.4" numpy pillow soundfile

echo "Ready: /opt/shorts/venv/bin/python (import bpy -> Blender 5.2)"
