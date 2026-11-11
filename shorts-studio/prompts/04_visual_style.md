# Prompt 4: Visual Style Bible + per-beat image/video prompts

Use this with whatever image or video generator you prefer (Midjourney, Flux, Ideogram, GPT-image, Leonardo; or image-to-video tools like Kling, Runway, Veo, Hailuo or Pika). The goal is one consistent "channel look", matching what the reference videos use: **simple 2D stickman characters inside rich, softly lit 3D or 2.5D worlds.**

---

## A. House style block (prepend to every image prompt)

```
Vertical 9:16 frame. Cute 2D cartoon stickman characters: large perfectly round white heads with a thick black outline, simple dot or oval eyes with expressive eyebrows, small mouth, thin black stick limbs, each character wearing one bold signature clothing item. Characters are flat-shaded 2D with clean thick outlines, composited into a soft stylized 3D environment (clay / low-poly diorama feel, rounded shapes, tilt-shift depth of field). Cinematic lighting with warm key light and cool shadows, rich saturated colors, gentle bloom, high detail in the environment, uncluttered composition. Main subject in the upper two-thirds of the frame; the lower third is calm and uncluttered (captions go there). No text, no letters, no watermark.
```

**Negative prompt** (if your tool supports one):
`text, letters, captions, watermark, logo, realistic human, photorealistic skin, extra limbs, distorted face, blurry subject, cluttered lower third, horizontal frame`

## B. Character sheet (generate once per character, reuse as a reference image)

```
Character reference sheet, white background, front view, 3/4 view, side view and 3 facial expressions (neutral, shocked, smirking) of: {{CHARACTER DESCRIPTION}}. House style: 2D cartoon stickman, large round white head, thick black outline, thin black stick limbs, flat colors.
```
Pass this sheet as a reference image or character reference (`--cref` in Midjourney, "character reference" or "ingredients" in most video tools) for every shot with that character. This consistency is what makes V1's red-cap hero instantly recognisable.

## C. Per-beat prompt template

```
[HOUSE STYLE BLOCK]
Shot: {{shot size — extreme wide / wide / medium / close-up / macro insert / top-down / POV / cross-section diagram}}, {{camera angle — low angle / eye level / high angle / over-the-shoulder}}.
Subject: {{CHARACTER NAME + description}} {{action, with a clear readable facial expression}}.
Setting: {{location}}, {{time of day}}, {{weather or atmosphere}}.
Light & mood: {{e.g. eerie moonlight with warm lamp glow / golden hour / harsh desert sun / neon night}}.
Key detail to make readable: {{the clue or object that matters in this beat}}.
```

Use the `visual` field of each beat in the spec as the source. `shotlist.md` (written by the renderer) lists every beat with its **exact duration**, so you know how long each clip needs to be.

## D. Image-to-video motion prompts (if animating stills)
Keep motion subtle and readable; 3–5s clips are plenty (the renderer trims them to fit).
- Character beats: `the character blinks and shifts weight, slight head turn, subtle idle animation, camera slowly pushes in`
- Action beats: `{{action}}, quick snappy cartoon motion, motion blur on fast movement, camera follows`
- Environment beats: `slow cinematic dolly forward, drifting particles (dust / snow / embers), gentle light flicker`
- Reveal beats: `camera rapidly pulls back to reveal scale` or `fast push-in on {{detail}}`

## E. Shot-size rhythm (from the references)
A good 13-beat run looks like this:
`WIDE establishing → MEDIUM character → CLOSE-UP reaction → INSERT clue → WIDE new location (whip) → MEDIUM action → POV → INSERT → CLOSE-UP shock → TOP-DOWN reveal → DIAGRAM/cutaway → CLOSE-UP → WIDE ending`

## F. Thumbnail / first frame
The first frame **is** the thumbnail in the Shorts feed. Make beat 1 the most striking composition in the video: the anomaly is visible (the forbidden button under glass, the lighthouse beam in an empty sea), with a single clear focal point and high contrast.

## G. Saving files
Save each result as `assets/<slug>/beat_01.png` (or `.jpg`, `.webp`, `.mp4`, `.mov`). Missing files render as labelled placeholder cards, so you can preview the edit before all the art is done.
