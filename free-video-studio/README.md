# Free Video Studio

A free toolkit for making 2.5D cartoon shorts like the reference videos
(bean-style characters, 3D-looking scenes, camera moves, word-by-word captions, sound effects).
**No paid tools and no credit card.** This folder only gathers the tools and assets; the
automation that ties them together comes next.

## What you provide
- The idea / prompts
- Your voiceover (MP3/WAV)
- Your still images (from any image tool)

## The free tools and where each runs

| Step | Free tool | Runs on | Notes |
|---|---|---|---|
| Script + scene list | Gemini (free tier) or Claude | Browser | Splits the story into ~12–15 shots per minute |
| Still images (optional) | **SD 1.5 / SDXL cartoon models** in ComfyUI | Laptop (slow) or Kaggle | Only if you don't already have images |
| **Image → animated clip** | **Wan 2.2 TI2V 5B** in ComfyUI ([`../kaggle/`](../kaggle/wan22_image_to_video.ipynb)) | **Kaggle free GPU** | Too heavy for a 4 GB Quadro P1000 |
| Image → video (fallback) | LTX-Video, Stable Video Diffusion | Kaggle | Lighter, lower quality |
| Camera moves on stills (zoom, pan, parallax, shake) | **FFmpeg** | **Laptop** | Free, fast, no AI needed — covers many shots |
| Word-by-word captions | **faster-whisper** + FFmpeg (ASS subtitles) | **Laptop** (CPU) | Same caption style as the references |
| Sound effects | **Freesound.org** (CC0 filter), **Pixabay SFX**, Kenney audio packs | Download | Free; or Stable Audio Open / MMAudio on Kaggle |
| Background music | **Pixabay Music**, YouTube Audio Library, **ACE-Step 1.5** (AI) | Download / Kaggle | ACE-Step reportedly fits in ~4 GB VRAM but is slow on Pascal; Kaggle is safer |
| Final edit + export 9:16 | **FFmpeg** (automated) or CapCut / DaVinci Resolve (manual) | Laptop / phone | |
| Optional 3D | **Blender** + free Mixamo animations + Kenney CC0 3D assets | Laptop | For a recurring cast later; not needed to start |

## Your laptop (i5 8th gen, 16 GB RAM, Quadro P1000 4 GB)
- ✅ FFmpeg, captions, camera moves, final assembly, SD 1.5 images (~30–60 s each)
- ❌ AI video (Wan 2.2, LTX, SVD) — use Kaggle
- ⚠️ The P1000 is a **Pascal** card. New PyTorch builds (CUDA 12.8+) dropped Pascal,
  so the setup script installs **PyTorch for CUDA 12.6**. Don't use ComfyUI's "portable" download.

## Setup (Windows)
1. Open **PowerShell** in this folder.
2. Run:
   ```powershell
   Set-ExecutionPolicy -Scope Process Bypass
   .\setup_windows.ps1            # core tools
   .\setup_windows.ps1 -WithImages  # + ComfyUI and an SD 1.5 model (~4 GB more)
   .\setup_windows.ps1 -WithBlender # + Blender
   ```
3. Grab free sound effects and music using [`assets/DOWNLOAD_LIST.md`](assets/DOWNLOAD_LIST.md).

## Folder layout
```
free-video-studio/
  setup_windows.ps1     installs everything
  assets/
    fonts/              caption fonts (downloaded by setup)
    sfx/                sound effects (whoosh, pop, boing, crowd…)
    music/              background tracks
    DOWNLOAD_LIST.md    where to get free SFX/music
  projects/             one folder per video (voiceover, images, clips) — created later
```

## Licenses to respect
- Freesound: use the **CC0** filter to avoid attribution requirements.
- Pixabay content: free for commercial use, no attribution required.
- Wan 2.2: Apache 2.0. SD 1.5: CreativeML OpenRAIL-M. Stable Audio Open: Stability Community License.
- Always check a model's page before using output commercially.

## Animation engines (installed and tested)
| Engine | Use | Render a test |
|---|---|---|
| **Manim** (Python, MIT) | 2D cartoon scenes drawn from shapes | `.venv/bin/manim -qm --fps 30 -r 1080,1920 manim_demo/bean_demo.py BeanDemo` |
| **Remotion** (React, free for individuals/≤3-person teams) | 2.5D parallax scenes, pop captions, final assembly | `cd remotion && npm i && npx remotion render src/index.ts CaptionShort out.mp4` |

Sample outputs are in `samples/`. Both run on CPU, so the laptop's Quadro P1000 is fine.
Manim on Windows needs no extra system libraries (`pip install manim`); Remotion needs Node.js (`winget install OpenJS.NodeJS.LTS`).

## Engine comparison (`compare/`)
The same 16 s teleport scene (`compare/script.json` + `compare/soundtrack.m4a`) made with each engine:

| File | Engine | Render time here | Notes |
|---|---|---|---|
| `1_Remotion.mp4` | Remotion | ~45 s | Richest look (gradients, blur, CSS). Best for final assembly. |
| `2_Revideo.mp4` | Revideo | ~40 s | Same code as Motion Canvas, renders from a script (automatable). |
| `3_MotionCanvas.mp4` | Motion Canvas | ~40 s | Renders only from its editor UI (automated here with Playwright). |
| `4_Manim.mp4` | Manim | ~30 s | Python. Great for diagrams; cartoon styling takes more work. |
| `5_Combined_All4.mp4` | All four | ~60 s | Counter = Motion Canvas, New York = Remotion, blueprint = Manim, Tokyo = Revideo; Remotion assembles + captions. |

Re-render: Remotion `npx remotion render src/index.ts Teleport|Combined out.mp4`;
Revideo `DISABLE_TELEMETRY=true node render.mjs`; Motion Canvas `npx vite` then click Render;
Manim `.venv/bin/manim -qh --fps 30 -r 1080,1920 manim_demo/teleport.py Teleport` (`CAPS=0` = no captions).
