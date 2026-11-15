# P02 decisions (choices the form did not specify, or changes to the quality lock)

1. **Render budget (quality-lock deviation, written reason).** The narration measures 151.8 s = 3,643 frames. At the locked 540×960 / 24 spp (~31 s/frame on this 4-vCPU container) that is ~31 h. The user asked for the finished video in this session, so P02 renders at **360×640, 16 spp, animation on twos** (every 2nd frame rendered and held for 2 frames; camera moves are also on twos). Remotion upscales to 1080×1920. Every other setting in section 3.1 is unchanged. A full-rate, higher-resolution re-render is the same command with `RES=540x960 SPP=24 STEP=1`.
2. **Shot count.** The form's shot 22 was split into S22 to S24 at the voice stage so each holds one action. Several shots run past 7 s because their narration is long; words were never cut.
3. **Cast size 4, no extras.** A locked private lab; extras would break the story.
4. **TTS respelling.** The all-caps warning line is spoken from a lower-case copy so Kokoro does not read it letter by letter; captions keep the original caps.
5. **Arms.** Rigid arm + toon stretch along the arm (`arm_dir`) instead of a 2-bone IK, so hands can reach the chest disc and the lever.
6. **Sound.** Everything is synthesized in `tools/p02/sound.py`; the alarm is near-silent from the corridor because the lab is soundproof.
