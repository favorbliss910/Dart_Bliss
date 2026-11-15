# Style bible: "Last Stop" proof world

Original IP. The reference brief describes only a *type* of look: stylized 3D cartoon, rainy urban night, a lit shop, and contrasting light. No characters, story, dialogue or designs are taken from any existing work.
Source of truth for numbers: `tools/build_proof_scene.py`. If this document and the script disagree, the script wins, and this document should be updated in the same commit.

## 1. Character: Pip, the night courier

| Attribute | Spec |
|---|---|
| Height | ~1.30 m including the hat (hip 0.42 m, neck pivot 0.84 m, head centre 1.01 m) |
| Silhouette | Egg-shaped body, a large round head (≈ 0.5 m wide, about 40% of body height), a wide flat rain-hat brim (r 0.33 m), stubby legs, mitten hands. Must read as a "small round figure with a hat" at a 360 px preview width |
| Proportions lock | Head ellipsoid (0.25, 0.235, 0.23); coat (0.27, 0.23, 0.33); eyes (0.062, 0.05, 0.072) at ±0.085 m |
| Palette | coat teal `#05656B`-ish (0.02, 0.36, 0.40); hat and mittens mustard (0.85, 0.55, 0.05); boots red (0.45, 0.04, 0.03); skin warm tan (0.80, 0.50, 0.33); parcel kraft (0.45, 0.28, 0.12) |
| Materials | Coat, hat and boots are clear-coated (coat weight 0.6–0.8, roughness 0.25–0.32), giving a toy-like wet sheen. Skin is matte (roughness 0.55). Eyes are glossy (0.15) |
| Face | White eyeballs with dark pupils on rotating pivots. Brows are separate pieces. The mouth is a half-torus arc whose z-scale goes 0.25 (neutral) to 1.0 (smile) |
| Acting rules | Eyes lead the head by about 4 frames. The hat lags the head by 3 frames (overlap). Bob is lowest on contact frames. There is a 3.5% squash on contact, an anticipation dip before big head moves, and an overshoot then settle on stops |
| Prop | Parcel tucked under the right arm (the right arm doesn't swing; the left arm does) |

## 2. World palette and value structure

* **Warm vs cool.** Warm sources (shop interior, street lamps) are 2700–3200 K-ish orange (1.0, 0.55–0.72, 0.25–0.45). Ambient sky, rim light and rain are blue (0.45–0.6, 0.6–0.75, 0.9–1.0). The pink neon (1.0, 0.18–0.25, 0.35–0.4) is the story accent and appears only when the sign turns on.
* **Value hierarchy.** The character face and the window are the brightest non-emissive areas. Far facades sit 2–3 stops lower. Sky is darkest at the top (0.006, 0.008, 0.016).
* **Saturation budget.** One saturated accent per region: red/cream awning stripes, teal coat, pink neon. Background bricks are desaturated (0.20, 0.085, 0.06) and slate (0.08, 0.11, 0.15).

## 3. Material roughness ranges

| Surface | Roughness | Notes |
|---|---|---|
| Wet asphalt / sidewalk | 0.03–0.42 | Noise-driven (scale 0.6), so puddles mirror the lights; grain bump strength 0.15 |
| Glass | 0.03, transmission 1.0 | Window shows the interior *and* reflects Pip |
| Clear-coated plastics (character) | 0.25–0.32 + coat | |
| Painted shopfront | 0.35 + coat 0.6 | |
| Brick / plaster | 0.75–0.8 | |
| Lamp metal | 0.3, metallic 1.0 | |

Edge softness: every character part uses Subdivision Surface (level 1–2). Hard-surface props use 2-segment bevels (0.01–0.02 m). Nothing should look razor-sharp.

## 4. Lighting ratios (proof shot)

| Light | Role | Power | Ratio vs. key |
|---|---|---|---|
| `key_window_spill` (area 2.0 × 1.4 m) | key, motivated by the shop | 45 W | 1 |
| `rim_cool` (area 3 m) | rim / separation | 220 W at ~5 m | about 0.7 at the subject |
| `fill_street` (area 4 m) | fill | 35 W at ~6 m | about 0.15 (≈ 3 stops under) |
| Street lamps (spot, 95°) | practicals | 70–80 W | local pools |
| `sign_glow` (point) | story practical | 0 → 32 W, keyed to the flicker | — |

Colour management: **AgX**, look *Medium High Contrast*, exposure +0.35, 8-bit sRGB PNG out.
Rejection rules: no clipped skin, no crushed faces (the fill must keep eye whites readable), no bloom used to hide missing light, and no emitter visible to the camera unless it is a practical (area lights have `visible_camera = False`).

## 5. Camera grammar

* Lenses are 26–35 mm on a 36 mm vertical sensor (portrait 9:16). Wide lenses exaggerate depth for small characters.
* **All movement is real 3D camera movement in Blender.** Remotion only cuts, adds captions, and encodes. It never zooms or pans a flat frame.
* Every hero move needs a **near layer** (lamp post, bollard, rain) that crosses the frame, a **mid layer** (character and shop), and a **far layer** (street blocks, receding lamps, fog). This is verified numerically by `tools/qc_p01.py`; for P01 the near layer shifts 16.8× more than the far layer.
* Depth of field is f/2.2 focused on the character's head. The look-at target is damped (lerp 0.25 per frame) so the camera never snaps.
* Eyeline: the camera stays at or just below character eye level (0.78–1.05 m), so the small character is not looked down on.

## 6. Depth layers (P01)

* **Near (0.5–3 m):** `lamp_near` (pole at x 3.6), `bollard`, `bin`, rain sheets
* **Mid (3–8 m):** Pip, the shop with its real interior (shelves and goods 1.5 m behind the glass), awning, neon sign, neighbour facades, hydrant
* **Far (8–45 m):** `far_block_*`, `opp_block_*` and `lamp_far_*` every 6 m, plus a low-density volume (`fog_far`, density 0.035) that only covers the far street

## 7. Readability checks

* Pip's silhouette must read against the background in every frame at 360 px wide. The warm rim from the window and the cool rim from the street provide edge separation.
* Captions sit at 18% from the top, above the action. Text is cream (#fff8ec) with a dark stroke and shadow, 30 px at 540 px width.
