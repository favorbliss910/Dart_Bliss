# QC scorecard: P01 "Last Stop" (5-second 3D proof)

**Deliverable:** `renders/proof_v1/p01_last_stop.mp4`. 540×960, 24 fps, 120 frames, 5.000 s, h264 + AAC 48 kHz stereo, −16.0 LUFS integrated, −1.1 dBTP (pre-encode).
Stills: `renders/proof_v1/contact_sheet.png` (every 12th frame) and `final_f21/f46/f101/f120.png`.

## Measured checks (pass/fail, automated)

| Check | Result | Evidence |
|---|---|---|
| All 120 frames present, 540×960, non-blank | PASS | `remotion/scripts/validate-media.mjs`; ffmpeg `blackdetect` found no black segments |
| Audio vs. video drift | PASS (13 ms, < 1 frame) | ffprobe: video 5.000 s, audio 5.013 s (AAC priming) |
| Genuine 3D parallax | PASS | near:far screen-shift ratio **16.8** (frames 1–60); `benchmark/p01_qc_metrics.json` |
| Foot sliding during stance | PASS (0.0 mm max) | `tools/qc_p01.py` |
| Ground contact (no float or sink) | PASS (boot bottom −5 mm, a deliberate small sink into the wet surface) | same |
| Footsteps on contact frames | PASS by construction | Foley placed from `manifests/p01_animation_events.json` |
| Caption timing | PASS (measured) | phrase boundaries from the energy envelope: 0.58–1.55 s and 1.95–3.10 s |
| Loudness | PASS | −16.0 LUFS integrated, true peak −1.1 dBTP |

## Visual rating (1–5): self-review only, **not independent**

The brief requires an *independent* reviewer and real-time playback (V3 p.014). These scores are Claude's own, from stills and a contact sheet. Claude has **not** watched the clip in real time or listened to the audio.

| Category | Score | Notes |
|---|---|---|
| Character consistency | 4 | One shared asset; proportions are locked by the script |
| Silhouette | 4 | Reads clearly at 180 px wide on the contact sheet; the hydrant overlaps Pip's legs in frames 1–15 |
| Motion mechanics | 3 | Planted feet, bob, squash, overshoot and eyes-lead-head are all present, but there is no knee bend (rigid capsule legs) and the turn steps are small shuffles |
| Genuine parallax | 5 | Measured; the lamp post and bollard wipe through the foreground |
| Composition | 4 | The end frame frames Pip against the OPEN sign. The mid-shot bollard briefly covers Pip's lower body (frames 78–90) |
| Lighting | 4 | Motivated warm and cool lights, pink neon spill on the face; the far facades' lit windows are flat emissive cards |
| Materials | 4 | Wet asphalt reflections and glass reflections (Pip is reflected in the window) |
| Environment detail | 3 | Box buildings; no puddle ripples or rain splashes; the interior goods are simple primitives |
| Sound sync | 3* | Timing is measured, but **nobody has auditioned it**. Synthesized Foley may sound synthetic |
| Storytelling clarity | 4 | The line asks ("please, still be open"), then the sign answers by flickering on 0.2 s later, and Pip smiles |

**Gate verdict: does NOT meet the "no category below 4" rule.** Motion mechanics, environment detail and sound are at 3. Do not expand to more shots until these are fixed.

## Recommended corrections (fix → rerender affected frames → retest)

1. **Legs:** replace the capsule legs with a 2-bone IK chain (Blender armature with an IK constraint) so the knees bend during stance and swing. This rerenders every frame where the legs are visible.
2. **Turn:** make the body turn 5 frames longer with a visible weight shift onto the planted foot (frames 70–92).
3. **Rain interaction:** add ring ripples in puddles and drips off the awning valance and hat brim.
4. **Bollard overlap (frames 78–90):** move the bollard 0.3 m toward +x, or lower the camera path at frame 80.
5. **Audio:** a human should listen to `assets/audio/p01/mix.wav`. Replace the synthetic footsteps with recorded, licensed Foley if they sound buzzy.
6. **Resolution:** delivery is 1080×1920, but this proof is 540×960. Either upscale it or re-render at about 130 s/frame on CPU (see `docs/render_budget.md`).
