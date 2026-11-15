# Reference breakdown: "Every Memory Has a Price"

Source: user-supplied MP4 (not committed: it's someone else's video). 78 s.

## Technical format
| Property | Value |
|---|---|
| Resolution | 1080 × 1920 (9:16 vertical, Shorts/TikTok/Reels) |
| Frame rate | 30 fps |
| Length | 77.9 s |
| Video | H.264, ~3 Mbps |
| Audio | AAC stereo 44.1 kHz, loud master (mean −16.8 dB, peak −2.1 dB), **no silences** |

## The look in one sentence
**Flat 2D cartoon characters standing inside fully lit 3D sets**, filmed by a
cinematic camera that never stops moving, with one or two words of narration
captioned on screen at a time.

## Characters (→ Character Book)
- "Bean" proportions: a huge round head (~40–45 % of height), small rounded torso, stick limbs.
- Off-white skin, thick near-black outline, flat fills, no shading baked in.
- Faces are minimal: circle eyes with small pupils, a single-line mouth, occasional brows, tears, sweat.
- Identity comes from **hair shape + one clothing colour + one prop/badge**
  (hero: orange flame tuft, mustard jacket, green frog badge; villain: dark hood, only a grin and glowing eyes).
- They are 2D, but the 3D scene lights them: warm key on one side, cool rim on the other,
  colour spill from neon signs and screens. That mix is what makes the style.
- Animation is limited: expression swaps, small bobs, head turns. Hardly any walk cycles.

## Environments (→ Environment Book / 3D Book)
About 18–20 locations in 78 s (one every ~4 s):
memory-shop counter (night, hooded keeper) · shop front with neon "MEMORIES pulled while you wait" sign and a checker floor ·
rainy city street with a deli awning, fire escapes and cyclists · aerial shot down a giant wall splitting the city ·
"rich side" Bahamas villa, pool, palm trees · memory-extraction helmet with a mechanical counter ·
"poor side" bench by a chain-link fence with BOUGHT & SOLD sign · HAPPINESS pressure gauge ·
hospital room with brother in bed · polaroid that dissolves into a sunny lake/dock memory ·
operating-theatre corridor · "WE BUY SUMMERS" storefront · bedroom · sale ledger (YEAR 2016–2025 SOLD) · final hospital bedside.

Sets are **stylised low-to-mid-poly 3D**: clean bevelled shapes, simple PBR materials,
painted-looking textures, and plenty of practical lights (lamps, neon, lit windows).

## Lighting and colour (→ Texture Book / 3D Book)
- Dominant palette: **deep ultramarine/indigo night** with **warm amber practicals**
  (complementary blue/orange). Memories and "rich" scenes switch to saturated daylight: turquoise water, yellow sun.
- Volumetric haze or god-rays in nearly every night shot; rain streaks outdoors.
- Very shallow depth of field (f/1.4–2.8 look) with big bokeh from practical lights.
- Bloom on every light source, soft vignette, light film grain.

## Camera and editing
- **Almost no hard cuts.** Scene detection found only one cut above a low threshold. Every change hides inside a move:
  - slow dolly-in or crane while dissolving into the next set,
  - fast **vertical whip-pan with motion blur** (e.g. pool → poor side at 23 s),
  - match-moves into an object (polaroid → memory, ledger → shop).
- The camera always drifts (push-ins, slow orbits, tilts). Static frames are rare.
- Low and slightly wide (24–35 mm) for sets, longer for close-ups of faces.

## Captions
- **1–2 words at a time**, synced to the voice (~0.25–0.5 s each).
- Bold geometric sans in white with a thick black outline and soft drop shadow (Montserrat ExtraBold matches closely).
- Centred horizontally at ~70 % of the frame height, ~70 px tall at 1080 wide.

## Sound (→ Sound Design Book)
- Fast, intimate male narration (~190 words/min, about 250 words in 78 s), storytelling cadence with punchy short sentences.
- Continuous bed under the voice (music plus ambience); the spectrogram shows sustained low tones end to end.
- Dense SFX layer: rain, city, mechanical clunks and counters, whooshes on every whip-pan, hospital beeps.
- Loud, compressed master for phone speakers.

## Story structure (useful for our own scripts)
1. **Hook (0–3 s):** a shocking one-liner ("He sold his happiest memory to a stranger behind a counter.").
2. **World rules (3–31 s):** a fast montage explaining the premise (memories are money, the wall, rich vs poor).
3. **Personal stakes (31–55 s):** the hero sells more and more for someone he loves.
4. **Escalation (55–65 s):** nothing happy left; he sells it anyway.
5. **Twist / gut-punch (65–78 s):** the brother is cured and the hero no longer remembers him.

The timed caption transcript (from OCR of the burned-in captions) is in
`reference/caption_timing.tsv`, for pacing reference only.
