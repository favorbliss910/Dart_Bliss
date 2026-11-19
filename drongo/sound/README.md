# Sound design

| File | What it is |
|---|---|
| `PRINCIPLES_1000.md` | The 1,000 sound-design principles (all five parts merged). Sources are in `principles/`. |
| `SPEC.md` | How those principles apply to this video: targets measured from the references, character sound identities, music plan, SFX rules and delivery. |
| `sfxlib.py` | Procedural SFX library (seeded and adjustable). Run it to render the audition bank to `bank/`. |
| `score.py` | Synthesized instruments, a humanized sequencer and the character motifs (drongo, meerkat, sentinel, hawk, alarm). |
| `design.py` | Cue sheet plus mixer: music ducking, speech-safe filtering, loudness of −14 LUFS and a −2 dB peak ceiling, and stems. |
| `align.py` | Offline forced alignment of a voiceover to the script, producing word timings. |

## When the voiceover arrives

```bash
# 1. word timings from the real read (script.txt = the exact words read)
python3 sound/align.py VOICEOVER.wav script.txt --out words.json
# 2. re-render the picture so the cuts and captions lock to the new timings
python3 render.py /path/frames --fps 15
# 3. sound design + final mix around the voice
python3 sound/design.py --voice VOICEOVER.wav --out out/mix.wav
# 4. mux
ffmpeg -framerate 15 -i /path/frames/f%05d.png -i out/mix.wav -c:v libx264 -pix_fmt yuv420p \
       -crf 18 -c:a aac -b:a 192k -ar 48000 -shortest out/final.mp4
```
