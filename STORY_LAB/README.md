# STORY_LAB: Blender-free Shorts pipeline

This pipeline renders the three stories from the *Story & Prompt Pack* as vertical 2K Shorts
(1440x2560, 30 fps, H.264 + AAC). It does not need Blender or a GPU.

| Step | Tool | File |
|---|---|---|
| Script | the pack's 9.0+ scripts, written as `mood \| line` chunks | `stories/<slug>/vo_chunks.txt` |
| Voiceover | **Kokoro-82M, voice `am_michael`** (ONNX, CPU) | `scripts/voice.py` → `stories/<slug>/audio/voice.wav/.mp3`, `timing.json` |
| Characters | Style DNA stickman cards (Cairo vector) | `scripts/cast.py` |
| Sets / props | warm toon 2.5D (lit front faces, darker side faces, parallax layers) | `scripts/props.py` |
| Camera, 3D titles, captions, whip-pans | | `scripts/engine.py` |
| Shot lists (from the pack's camera plans) | | `scripts/potato_king.py`, `coin_ridges.py`, `convict_ships.py` |
| Music bed + SFX (synthesised, no samples) | | `scripts/audio.py` |
| Final videos | | `renders/<slug>_2K.mp4` |

The scene is drawn in 2.5D, not real 3D. Depth comes from parallax camera layers,
3-tone toon shading, soft violet contact shadows, extruded gold 3D text, and push-ins and whip-pans.

## Setup
```bash
pip install kokoro-onnx soundfile pycairo numpy pillow
mkdir -p /home/user/models && cd /home/user/models
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
cp STORY_LAB/assets/fonts/*.ttf ~/.fonts/ && fc-cache -f      # Lilita One for titles/captions
```
(`KOKORO_DIR` env var overrides the model folder.)

## Commands
```bash
cd STORY_LAB
python scripts/voice.py stories/potato_king          # 1. voiceover + word timings
python scripts/run.py potato_king stills             # 2. QC contact sheet (one frame per shot)
python scripts/run.py potato_king preview            # 3. optional 540x960 quick render
python scripts/run.py potato_king full               # 4. 2K final  -> renders/potato_king_2K.mp4
```
Each final render takes about 2 minutes on 4 CPU cores.

## Notes
- Word timings are estimated, because Kokoro gives no timestamps. Each chunk is voiced on its own, so chunk boundaries are exact.
  Phrases are snapped to the silences found in the audio, and words within a phrase are spread by phoneme count.
- Kokoro speed per mood (in `voice.py`): hook 1.10, normal 1.16, turn 1.08, dread 1.04, final 1.00. That gives about 175 wpm and about 60 s of speech per story.
- To add a shot, write a function decorated `@shot("first words of the VO line")` in the story file.
  It starts on that word, and cuts are whip-pans unless `whip=False`.
