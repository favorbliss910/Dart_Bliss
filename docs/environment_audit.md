# Environment audit: 3D production pipeline

Audited on 2026-11-15 in the Claude Code cloud container, branch `ccr-eb4a4a08-p49urw`.
Every version below was printed by a command in this session. Nothing is assumed.

## Repository state (before this work)

| Item | Finding |
|---|---|
| Purpose | A small Express + socket.io chat app (`index.js`, `public/`), deployed with GitHub Pages (`CNAME`) |
| package.json deps | `express ^4.18.1`, `socket.io ^4.5.1`, `git ^0.1.5`, dev `nodemon` |
| Remotion | **Not present** |
| Blender scripts | **None** |
| Reference video | **Not present** in the repo or uploads. Only the PDF-derived brief (`Claude_Code_3D_Production_System_V3.txt`) was supplied |

The chat app files are untouched. The new pipeline lives in `tools/`, `docs/`, `manifests/`, `benchmark/`, `assets/`, `renders/` and a self-contained `remotion/` package. The root `package.json` is unchanged.

## Toolchain (verified)

| Tool | Command | Result |
|---|---|---|
| Blender binary | `command -v blender` | **not installed**; `download.blender.org` returns **403** through the egress proxy |
| Blender as a module | `pip install bpy` (PyPI) | **bpy 5.3.0** (cp313 manylinux wheel, 427.5 MB) works headless |
| Render engines | `tools/check_blender.py` | **Cycles CPU works**. EEVEE is listed but did not produce an image (no GPU or GL context) |
| GPU | `nvidia-smi`; Cycles device query | **none** (CUDA, OptiX, HIP and oneAPI device lists are empty) |
| CPU / RAM / disk | `lscpu`, `free -h`, `df -h .` | 4 vCPU Intel Xeon @ 2.10 GHz, 15 GiB RAM, no swap, ~30 GB free |
| FFmpeg | `ffmpeg -version` | 6.1.1-3ubuntu5 (has `ebur128` loudness meter) |
| Node / npm | `node --version` | v22.23.4 / 10.9.9 |
| Python | `python3 --version` | 3.13.18 (venv in scratch dir; see `tools/requirements.txt`) |
| Remotion | `npm view remotion version` | 4.0.543 pinned in `remotion/package.json` (with React 19.1.1) |
| Browser for Remotion | pre-installed Playwright Chromium | `/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell` |
| Kokoro | `pip install kokoro-onnx` | **kokoro-onnx 0.6.1**, onnxruntime 1.32.0, espeakng-loader 0.2.4 |
| Kokoro weights | HuggingFace `hexgrad/Kokoro-82M` | **403 (blocked)** |
| Kokoro weights (alt) | GitHub release `thewh1teagle/kokoro-onnx` `model-files-v1.0` | **OK**: `kokoro-v1.0.int8.onnx` (92 MB) and `voices-v1.0.bin` (28 MB) |

### How Claude controls Blender (V3 p.003)

Blender runs as **Python `bpy` in-process (Blender-as-a-module)**. There is no MCP connector, remote Blender API, or GUI. All scenes are built by scripts and rendered with `bpy.ops.render.render`. This was tested, not assumed:

```
python tools/check_blender.py renders/smoke
→ bpy 5.3.0, 12/12 frames, 360x640, Cycles CPU 16 spp, 2.35 s/frame (renders/smoke/check_blender.json)
```

### Kokoro `am_michael` (V3 p.009)

* Installed voices: 54. The male US-English (`am_*`) voices are am_adam, am_echo, am_eric, am_fenrir, am_liam, **am_michael**, am_onyx, am_puck and am_santa.
* `am_michael` **is available** and synthesizes: 24 kHz mono float output, `lang="en-us"`, espeak-ng phonemization. A test sentence took 0.67 s to generate 1.62 s of audio on CPU.
* The model is **Kokoro-82M v1.0 as int8 ONNX** (not the PyTorch `kokoro` package). The int8 quantisation may differ slightly from fp32 output.
* Controls actually exposed: `voice`, `speed`, `lang`, plus text and punctuation. **No word timestamps, emotion, or pitch controls are exposed**, so caption timing is measured from the audio's energy envelope (`tools/make_audio.py`).
* No claim is made that `am_michael` resembles any real speaker.

### Plugins and add-ons (V3 p.004)

None were installed. The character is built procedurally from rounded primitives and a parented pivot hierarchy, which suits the stylized design. Rigify, MPFB, MB-Lab and "Makeware Umabean" were **not** evaluated. If the last one is wanted, its exact project URL is needed first.

## Constraints that shape scope

1. **CPU-only Cycles.** About 32–37 s/frame at 540×960 with 24 spp (see `docs/render_budget.md`). Full 1080×1920 delivery would be about 4× slower per frame.
2. **No Blender GUI or playblast viewport.** "Playblasts" are low-sample Cycles renders.
3. **No human audition.** Audio levels are measured (LUFS and true peak), but nobody has listened for pronunciation or artifacts. This needs a human pass.
4. **Remotion license.** Remotion is free for individuals and companies with up to 3 people. Larger organizations need a company license. Check this before production use.

## Reproduce

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r tools/requirements.txt
mkdir -p .models && cd .models
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
cd ..
python tools/check_blender.py renders/smoke                        # smoke test
python tools/build_proof_scene.py --out renders/proof_v1 --res 540x960 --samples 24   # ~70 min, restart-safe
python tools/make_audio.py --kokoro-model .models/kokoro-v1.0.int8.onnx --kokoro-voices .models/voices-v1.0.bin
python tools/qc_p01.py renders/proof_v1/proof_scene.blend          # parallax / foot-slide metrics
cd remotion && npm ci && REMOTION_BROWSER=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell npm run render
```
