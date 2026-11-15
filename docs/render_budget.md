# Render budget and cost gates (V3 p.013)

Hardware: 4 vCPU Xeon @ 2.10 GHz, 15 GiB RAM, **no GPU**. Engine: Cycles CPU with the OIDN denoiser, adaptive sampling (threshold 0.03), and persistent data.
All numbers below were measured in this container. The "Measured" table is filled from `renders/*/render_timings.json`.

## Measured

| Test | Resolution | Samples | Frames | s / frame | Notes |
|---|---|---|---|---|---|
| Smoke (cube, floor, area light, moving camera) | 360×640 | 16 | 12 | 2.35 | `renders/smoke/check_blender.json` |
| P01 lookdev stills | 270×480 | 16 | 5 | 5.6–6.9 | first-pass layout |
| P01 lookdev stills | 360×640 | 16 | 5 | 9.2–12.0 | |
| P01 final-res test | 540×960 | 32 | 2 | 47–49 | about 96 min per 5 s, rejected for proof |
| P01 final-res test | 540×960 | 24 | 1 | 37.5 | chosen setting |
| **P01 full proof** | **540×960** | **24** | **120** | **__MEAN__** (total __TOTAL__ min) | `renders/proof_v1/render_timings.json`; other jobs shared the CPU during the first ~10 frames |
| Remotion assembly + encode | 540×960 | — | 120 | __REMOTION__ | h264 CRF 18 + AAC |

Peak memory for the bpy process stayed well under the 15 GiB available; the scene is about 0.5 MB as a .blend.

## Extrapolation (not measured; linear in pixels × samples)

| Target | Per frame (est.) | 78 s @ 24 fps = 1 872 frames |
|---|---|---|
| 540×960, 24 spp (proof quality) | ~33 s | **~17 h** on this container |
| 1080×1920, 24 spp | ~130 s | **~68 h** |
| 1080×1920, 64 spp | ~350 s | **~180 h** |
| 1080×1920 on one modern NVIDIA GPU (OptiX) | typically 10–30× faster than this CPU (unverified here) | ~2–7 h |

## Gates

1. **Gate A, 5 s proof (this deliverable).** Passed technically if every frame exists, audio drifts less than one frame, and parallax and foot metrics pass. It still needs a human visual and audio review before any expansion.
2. **Gate B, a 24- and 72-frame benchmark per new environment** before rendering any shot longer than 3 s.
3. **Gate C, full 78 s.** **Do not start on this container.** It needs either (a) GPU compute, or (b) explicit approval of ~17 h CPU at 540×960 then upscaling, or (c) reduced scope. The decision belongs to the owner.

## Restart safety

`tools/build_proof_scene.py` skips frames that already exist on disk, so an interrupted render resumes where it stopped. Frames are written individually as PNG, so a crash loses at most one frame. Delete a frame to force it to re-render (the "fix → rerender affected frames → retest" loop).
