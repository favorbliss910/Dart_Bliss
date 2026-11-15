# PART IV — THE 2D ANIMATION ENGINE (HOW THE FILM IS BUILT)

This part documents exactly how the Jupiter film was animated: the architecture, every technique, the reasons behind the choices, and the mistakes to avoid. The complete source is in **Appendix A**. A new film **reuses the engine unchanged** and only writes new `scenes*.py` files, plus new hero assets if the topic needs them (Part X).

## 4.1 Philosophy: the film is a pure function of time

Every frame is drawn from scratch by code: `frame = draw(t)`, where `t` is the **global program time in seconds** (the same clock as the voiceover). There is no timeline editor, no keyframe file and no stored animation state. This gives:

- **Perfect narration sync**: every event is written as `at('exact words')`, so timings come from the transcript, not from guesses.
- **Free parallel rendering**: any frame can be rendered independently, so the film splits into segments across CPU cores.
- **Instant iteration**: change a number, re-render one still or a contact sheet in seconds.
- **Resolution independence**: everything is vector drawing (Skia) plus procedural textures (NumPy), crisp at 1080p.

## 4.2 Toolchain

| Tool | Role |
|---|---|
| **Python 3** | Everything |
| **skia-python** | Anti-aliased 2D vector rendering: paths, gradients, blur mask filters, image draws, text (Google's Skia, the Chrome renderer) |
| **NumPy** | Procedural textures (noise, planet bands, clouds), sphere projection, audio DSP |
| **Pillow** | Bicubic upsampling for value noise; contact sheets |
| **ffmpeg / libx264** | Encoding raw BGRA frames piped from Python; concatenation; muxing |
| **sherpa-onnx + Parakeet TDT 0.6B v2 (int8)** | Offline word-level transcription of the voiceover |
| **Fonts** | Inter / Inter Display (all weights), JetBrains Mono |

## 4.3 Architecture (module map)

```
engine/
  core.py        timing (at), easing, tweening, shake, colors, palette, fonts, text, paints,
                 gradients, image conversion (premultiplied BGRA), value noise, cache
  assets.py      procedural textures + renderers: Jupiter band texture with Great Red Spot,
                 Earth texture, lit textured sphere renderer, cloud & haze sprites,
                 starfield, vignette, film grain, additive glow sprite
  elements.py    vector props & UI: arrows, animated X/check, dashed paths, honesty tags,
                 callout labels (auto-clamped), cards, big numbers, chapter cards,
                 HUD panels/readouts/gauges/thermometer/signal bars, Galileo entry probe,
                 parachute + descent module, Juno, explorer face/bust rig, capsule,
                 Jupiter cutaway cross-section, dipole field lines, H2 molecules
  common.py      environments: gradient backgrounds (cached), space(), multiplane
                 cloud_world(), speed_lines(), particles(), flash, depth ruler, texture strips
  render.py      timeline assembly (auto-discovers scenes*.py), transitions, post (vignette,
                 grain, final fade), still/contact/bench/segment-encode commands
  transcribe.py  voiceover -> words.json / words.txt
  sfxlib.py      the sound engine (Part V)
  render_all.sh  parallel segment render + concat
  scenes_TEMPLATE.py
  example_jupiter/  scenes1-3.py (54 shots), mix.py (cue sheet), words.json
```

A project folder (`JV_PROJECT`) contains `words.json`, `scenes1.py … scenesN.py`, `mix.py`, and a `cache/` directory created automatically for textures.

## 4.4 Narration-locked timing: `at()`

`core.at(phrase, after=0, end=False)` normalizes words (lowercase, alphanumerics only) and returns the **start time of the first occurrence of the phrase at or after `after`**. With `end=True` it returns the start of the word after the phrase, which is useful for "right after X is said".

```python
T_DECEL  = at('Then the deceleration hits')     # 168.82 s
T_228B   = at('two hundred and twenty eight')   # 180.54 s
T_NO     = at('No', after=649)                  # disambiguate repeated words with after=
T_LOST   = at('the signal was lost', end=True) - .15
```

**Rules:**

- Define all phrase constants at the top of each scenes file. They double as **the sound-effect cue points** (the mixer imports the same constants), so picture and sound can never drift apart.
- Numbers are transcribed as spoken words ("two hundred twenty eight"), except where the model writes digits ("3000"). Always check `words.txt`.
- A missing phrase raises `KeyError` at import, so bad sync fails loudly.

## 4.5 Motion vocabulary (core.py)

| Function | Purpose |
|---|---|
| `prog(t, t0, t1)` | 0→1 progress, clamped |
| `e_in, e_out, e_io, e_sine, e_back, e_expo_out` | Easing curves (cubic in/out, sine, back-overshoot) |
| `tw(t, t0, t1, a, b, ease)` | Tween a value |
| `keys(t, [(t, v), …], ease)` | Multi-keyframe interpolation (numbers or tuples) |
| `fade_window(t, t0, t1, fin, fout)` | 0→1→0 visibility window for labels and cards |
| `shake(t, t0, dur, amp, freq, seed)` | Damped camera shake (exponential decay + tail fade) |
| `wobble(t, amp, f)` | Organic idle sway (two sines) |
| `text_pop(...)`, `big_number(...)` | Text that scales in with back-overshoot (0.35–0.4 s) |

**Pattern: a micro-beat is one line.**

```python
k = prog(t, T_GRS, T_GRS + .6)                       # starts on the spoken word
label_line(c, x0, y0, x1, y1, 'GREAT RED SPOT', k=k, sub='A GIANT STORM · WIDER THAN EARTH')
```

## 4.6 Rendering fundamentals and performance lessons

- **Canvas:** `skia.Surface(1920, 1080)`. Each shot draws onto `c` (a `skia.Canvas`). Use `c.save()/c.restore()` around transforms.
- **Images must be premultiplied BGRA** (`to_img()`): drawing an unpremultiplied RGBA image cost about 23 ms per full frame versus about 1 ms for premultiplied BGRA (native byte order). Scaled draws were about 67 ms versus 6 ms. **This was the single biggest performance win.**
- **Readback:** `surface.toarray()` (native BGRA, about 4 ms), piped straight to ffmpeg with `-pix_fmt bgra`.
- **Full-screen gradients are slow (~20 ms).** Cache them as small images (64×256) and stretch-draw them (`grad_img` / `bg()`).
- **Blur mask filters** are fine on small shapes; for glows use the cached additive sprite (`glow()`, plus blend).
- **Sphere renders cost 20–100 ms.** Cap the compute grid (`max_grid≈1150`) and let Skia upscale with linear filtering.
- **Measured average:** about 190 ms per frame per core (range 100–650 ms). 44,892 frames on 4 cores took about 60 min including x264 encoding.

## 4.7 Procedural textures (assets.py)

### Value noise
`noise2(h, w, cells_y, cells_x, seed, wrap_x, octaves, persistence)` builds smooth noise by **bicubic-upsampling random grids** (Pillow) and summing octaves (fractal). `wrap_x=True` copies the first grid columns to the end so the texture tiles around a planet's longitude. Using **more cells in Y than X** stretches the features horizontally, which gives the banded, wind-sheared look of a gas giant.

### Gas-giant band texture (equirectangular, 2048×4096)
1. A **band table** of (latitude, color) control points, interpolated per channel (`_band_lookup`): zones are cream (`#FFF1D6`, `#F2DFBD`), belts are brown (`#B9773E`, `#8A4E2B`), poles are grey-brown.
2. **Turbulent latitude:** `lat_e = lat + n1·amp·2.2 + n2·2`, with turbulence amplitude larger near belt edges (`|sin(9·lat)|`).
3. **Festoons** at the equatorial-belt edge: `exp(-((lat-7)/3.5)²) · sin(13·lon + noise)^12 · 2.6`. Keep the amplitude small; large values look like drips.
4. **Vortex (Great Red Spot)** at lat −22°, lon 180°: rotate local coordinates by `2.6·exp(−0.8 r²)` (a swirl), then paint a core / rim / light collar with spiral streaks. **Size it realistically** (semi-axes 7.6° × 4.7°, about 17,000 × 11,000 km) so an Earth comparison is honest.
5. White ovals and dark barges as small elliptical stamps; fine streak noise multiplies brightness ±8%.
6. Cache as float16 `.npy` (first build about 12 s).

**For other worlds:** change the band table (ice giants: pale cyan bands with low contrast; hot Jupiters: dark red with a glowing night side), the vortex list and the noise anisotropy.

### Lit sphere renderer (`sphere_layer` / `draw_sphere`)
For each pixel of the on-screen bounding box (computed on a capped grid):

```
nx, ny = (x-cx)/R, (y-cy)/R ;  inside = nx²+ny² < 1 ;  nz = sqrt(1 - nx² - ny²)
lat = asin(-ny) ;  lon = atan2(nx, nz) + rot        # rot animates rotation
texel = tex[(0.5 - lat/π)·H, (lon/2π)·W]            # bilinear when magnified
lit   = clip(n·L·1.15 + 0.05)^0.85                  # L = upper-left light
shade = lit·(1 - limb + limb·nz^0.5) + ambient      # limb darkening
+ warm terminator scatter;  alpha = 1-px anti-aliased edge
```

Then add a **thin atmospheric rim** (radial gradient ring at about 0.95 R, `#ffd9a0` for Jupiter, `#7fb8ff` for Earth). The longitude facing the camera is `rot`, so to center a feature at texture longitude λ, set `rot = λ`. Its screen y is `cy + sin(−lat)·R`.

**Do not zoom a low-resolution texture too far** (the Earth zoom went blocky at R = 2400 px). Cap the zoom or switch to a dedicated close-up drawing.

### Clouds and haze sprites
- **Cloud sprite (512×300):** 16–24 Gaussian blobs arranged in an arch (bigger in the middle), modulated by low-frequency noise, a flat-ish base, `smoothstep` alpha, shading = brighter top + **top-edge rim highlight** (from the vertical alpha gradient) + darker underside. Eight variants, drawn tinted with a color-matrix filter (`tint_cf`).
- **Haze sprite (1024×220):** horizontally tiled noise in a Gaussian vertical profile, used for deep-fluid streaks.
- **Starfield:** 900 stars with a power-law magnitude, three tints, per-star twinkle phase and parallax depth. The brightest get a soft halo.
- **Overlays:** a quarter-resolution vignette image and six half-resolution grain frames (overlay blend at 4.5% opacity, cycled at 24 fps).

## 4.8 Environments (common.py)

- **`space(c, t, zoom, ox, oy)`**: cached navy gradient + radial nebula wash + parallax starfield.
- **`cloud_world(c, t, fall, drift, tint, bg_top, bg_bot, bg_mid, depth_dark, haze, ox, oy)`**: the core descent environment. Four depth layers; each sprite's position is `(base + velocity·depth·t) mod span`, so the motion is infinite and seamless. `fall` > 0 makes clouds rise past the camera (the viewer is falling). Tint and background shift with depth. **This one function produced about 40% of the film's shots.**
- **`deep_env(c, t, depth)`** (scenes3): gradient interpolates amber → dark red → violet as `depth` 0→1, with drifting haze sprites.
- **`speed_lines`** (entry streaks, hyperspace), **`particles`** (dust, snow, sparks), **`flash`**, **`depth_ruler`** (scrolling ticks).
- **Texture strip flow (`s12`):** horizontal slices of the planet texture scrolled at alternating speeds per latitude, which reads as **jet streams shearing**.

## 4.9 Props and characters (elements.py)

All vector, built from paths with linear/radial gradient shaders, for a "premium 2D illustration" look:

- **Galileo entry probe** (side view): blunt-cone heat shield + gold conical afterbody with blanket seams. The `heat` parameter blends the shield to orange and adds shock-layer glows.
- **Parachute + descent module:** canopy cubic path with scalloped hem, stripes clipped to the canopy, suspension lines; `openk` uses `e_back` for the bloom; `transmit` draws expanding radio arcs upward.
- **Juno:** hexagonal bus + three blue solar arrays (one shorter with a magnetometer boom).
- **Capsule and explorer:** see Part III §3.3. The explorer is drawn *inside* the capsule window through a circular clip, so the character acts during exterior shots.
- **Cross-section (`draw_cross_section`)**: draw the textured sphere, then clip to a **pie wedge** (`wedge=(a0, a1)` in degrees) and paint layered radial gradients: molecular envelope (amber → red-brown), metallic region (indigo, with animated glow blobs), and core (`core_fuzz` 0 = sharp compact ball with a rim, 1 = broad diffuse gradient + 160 scattered "heavy element" dots). `dark_unknown` blacks out the interior for "unexplored". `highlight` outlines a layer. **Animating `core_fuzz` 0→1 produced the fuzzy-core peak.** Prefer a half cutaway (`(-90, 90)`); narrow wedges make a distracting apex.
- **Dipole field lines:** `r = L·R·sin²θ` per L-shell, dashed with an animated phase (flow), plus a blurred glow pass; `stroke_path_k` animates the drawing-on.
- **Labels:** `label_line` (dot + ring + leader line drawn with follow-through, then text and sub-text). **Auto-clamps inside the frame.** `draw_tag` (honesty pills), `card`, `chapter_card`, `big_number`, `draw_x` / `draw_check` (two-stroke animated marks with glow).

## 4.10 Shot authoring pattern

```python
def s20(c, t):                                   # SHOT 20 — 228 g (visual peak)
    bg(c, '#1a0806', '#4a140a')                  # 1. environment
    k = 1 - e_out(prog(t, T_DECEL, T_DECEL + 3.5))
    speed_lines(c, t, .2 + .5*k, direction=(.5, .86), speed=600 + 3000*k)   # 2. motion layer
    sx, sy = shake(t, T_DECEL, 2.2, 38, freq=16)                            # 3. camera
    c.save(); c.translate(sx, sy)
    draw_galileo_entry(c, 520, 560, .9, 55, heat=.7*k + .2, t=t)            # 4. subject
    g = 228 * e_out(prog(t, T_228 - 1.2, T_228 + 1.6))                     # 5. data synced to speech
    draw_gauge(c, 1300, 470, 230, g/260, 'DECELERATION', f'{int(g)} g', warn_from=.35)
    c.restore()
    flash(c, (1 - e_out(prog(t, T_DECEL, T_DECEL + .5))) * .6, '#ff6040')  # 6. accent
    draw_tag(c, 'GALILEO PROBE · MEASURED PEAK ≈ 228 g', 40, 36, 'hist')    # 7. honesty tag
```

**Order inside every shot:** environment → motion layers → camera transform → subject/character → data, labels and instruments synced to speech → accents (flash, glow) → honesty tag (always last, always top-left).

**Registering shots:**

```python
SHOTS2 = [ (T_HIT, s18, ('flash', .35)), (T_DARKNESS, s19, ('fade', .6)), (T_DECEL, s20, ('cut', 0)), ... ]
```

A shot runs from its start time until the next shot's start. During a transition, `render.py` draws the previous shot at the current `t` too, so both keep moving through the transition.

## 4.11 Transitions and post (render.py)

- `fade`: render both shots, alpha-blend the new one with `e_sine`.
- `black`: first half fades the old shot to black, second half fades the new one in.
- `flash`: new shot plus a warm-white overlay decaying with `e_out`.
- `whip`: old shot slides out / new slides in by 60% of the frame width, with 7 offset copies at decreasing alpha for motion blur.
- **Post on every frame:** vignette → film grain (overlay 4.5%) → global fade-out in the last 1.6 s before `END_T`.

## 4.12 Rendering and encoding

```bash
python3 render.py still 650.6 frame.png              # one frame
python3 render.py contact 0 60 1.5 sheet.png 5       # QA grid: t0, t1, step, cols
python3 render.py bench 2 30 160 450 610             # ms per frame at sample times
./render_all.sh <project> <out> 8 4 60               # segments, parallel jobs, fps
```

Each segment worker pipes raw BGRA into `ffmpeg -f rawvideo -pix_fmt bgra -s 1920x1080 -r 60 -i - -c:v libx264 -preset faster -crf 18 -pix_fmt yuv420p -tune animation -threads 2`. Then `concat` with `-c copy` and mux the audio: `-c:a aac -b:a 256k -movflags +faststart`. Jupiter: 8 segments × about 5,600 frames, 186 MB final at about 2 Mbps (flat 2D compresses very well).

**Monitor long renders** with a background job plus a progress monitor that also matches failure strings (`Traceback|Error|FAIL`). Spot-check a finished segment's frame **before** the others finish.

## 4.13 The contact-sheet QA loop (the most important habit)

1. After writing a batch of shots, render a contact sheet across its time range (5 columns, 25% scale, timestamps on each tile).
2. Inspect every tile: focal point, safe area, **label clipping**, overlaps, wrong tag, sync (is the number already on screen before it is spoken?), empty or black frames, blocky textures, unreadable small text.
3. Fix and re-render the sheet. Only then render the film.

**Bugs this loop caught on Jupiter:** labels running off the right edge (fixed by auto-clamping in `label_line`), a title overlapping a callout, a blocky Earth zoom (zoom capped), a distracting cutaway apex (switched to a half cutaway), a tint passed as a float instead of an RGB tuple (crash), and black frames that were only the provisional end fade (`END_T` before the final scenes file existed).

## 4.14 Building assets for a new topic

Reuse first: space, stars, cloud world, deep environment, explorer, capsule, all instruments, labels, tags, transitions, cross-section (re-colored), field lines, particles. Then build only the topic's **hero assets** using the same techniques (Part X gives recipes):

- **New celestial bodies:** new band table or texture recipe → `draw_sphere(tex, …)`.
- **Galaxies:** a particle-based spiral (logarithmic arms, `r = a·e^(bθ)`, thousands of additive dots with color by age) and a bulge glow.
- **Black holes / lensing:** black disk + photon ring + accretion disk as a squashed ellipse ring with a Doppler brightness asymmetry; background stars displaced radially near the hole.
- **Universe-scale:** a cosmic-web filament network (random points + nearest-neighbor lines with glow), expanding grids for spacetime.
- **Parallel universes:** split-screen mirrors, branching timelines (tree of paths drawn on with `stroke_path_k`), bubble universes (translucent spheres with internal starfields).
