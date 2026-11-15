# Studio: 2D-characters-in-3D-worlds vertical video pipeline

Goal: make 9:16 story videos in the style of the reference
(see `reference/STYLE_ANALYSIS.md`), driven from a phone through a Claude Code
cloud session, with **Blender (bpy)** for all 3D and rendering.

```
studio/
  setup.sh                 one-command environment setup (re-run each fresh session)
  requirements.txt
  reference/               style breakdown + caption timing of the reference video
  assets/fonts/            Montserrat (OFL), the caption font
  pipeline/
    make_character.py      2D cartoon character sprite generator (PNG)
    render_shot.py         JSON shot -> Blender scene -> rendered MP4 (+ .blend)
    sfx.py                 procedural sound effects (rain, whoosh, riser, ...)
    post.py                join shots + transitions, grade, captions, audio mix
  shots/                   shot specs (JSON)
  renders/                 output (git-ignored)
```

## Workflow
1. `bash studio/setup.sh`
2. Write a shot spec (`shots/*.json`), then preview it: `render_shot.py shot.json out --preview --still`
3. Render the shot: `render_shot.py shot.json out [--preview]`
4. Write `edit.json` (shots, transitions, captions, audio), then run `post.py edit.json final.mp4`
5. Download `final.mp4` to your phone.

## Shot spec
```jsonc
{
  "id": "s01", "duration": 3.0, "fps": 30, "samples": 32,
  "world_color": "#0B1028", "world_strength": 0.6, "exposure": 0,
  "objects":   [{"name":"counter","type":"box|plane|cylinder|sphere|cone",
                 "loc":[x,y,z], "rot":[deg,deg,deg], "size":[x,y,z],
                 "color":"#hex", "roughness":0.5, "metallic":0, "bevel":0.03,
                 "emission":"#hex", "emission_strength":4,
                 "pattern":"checker", "color2":"#hex", "texture":"assets/..png"}],
  "lights":    [{"type":"POINT|SPOT|AREA|SUN", "loc":[..], "aim":[..],
                 "energy":800, "color":"#FFB866", "spot_deg":60, "size":2}],
  "characters":[{"name":"hero", "loc":[..], "height":1.75, "flat":0.55,
                 "look": {"hair":"tuft","hair_color":"#C8582A","shirt":"#E0A23A",
                          "expression":"worried","badge":"#5DBB63"},
                 "image": "optional/path/to/your/own/sprite.png"}],
  "fog":       {"density":0.04, "color":"#8FA8FF", "size":[14,10,6], "loc":[0,0,3]},
  "camera":    {"keys":[{"frame":1,"loc":[..],"look_at":[..],"lens":30},
                        {"frame":90,"loc":[..],"look_at":[..],"lens":32}],
                "fstop":1.8, "focus":"hero"}
}
```
Units are metres, Z is up, and the camera looks toward +Y. Characters are camera-facing
2D planes (`flat` = how much of the drawing stays self-lit versus picking up scene light).

## Render speed (this cloud container: 4 CPU cores, no GPU)
| Setting | Per frame | 78 s video (2,340 frames) |
|---|---|---|
| `--preview` 540×960, 8 spp + denoise | ~12 s | ~8 h |
| final 1080×1920, 32 spp | ~50 s | ~32 h |
| *A desktop GPU (e.g. RTX 3060+), EEVEE or Cycles OptiX* | *~0.5–2 s* | *~0.5–1.5 h* |

The cloud container is fine for look development, stills, short tests and
assembly. For full episodes, render on a GPU machine. The same scripts run
unchanged there (`pip install bpy` or Blender's own Python).

## Known limits in this cloud environment
- The network policy blocks blender.org, Hugging Face, GitHub releases, TTS APIs
  (ElevenLabs/OpenAI/Edge) and Freesound. Blender comes from PyPI (`bpy`) instead.
- Voice-over: record on your phone and upload it, or allow a TTS host in the environment's network settings.
- Music and SFX: `sfx.py` synthesises the basics; licensed tracks can be uploaded.
