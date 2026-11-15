# APPENDIX B — ENVIRONMENT SETUP (Claude Code cloud session)

```bash
# 1. Python packages
pip install skia-python numpy pillow sherpa-onnx
# 2. Skia needs EGL/GL system libraries
apt-get update && apt-get install -y libegl1 libgl1
python3 -c "import skia; print(skia.__version__)"
# 3. Speech model (GitHub release; Hugging Face may be blocked)
mkdir -p models && cd models
curl -sSL -o p.tar.bz2 https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8.tar.bz2
tar xjf p.tar.bz2 && cd ..
# 4. Tools present in the base image: ffmpeg/ffprobe (libx264), fonts Inter, Inter Display, JetBrains Mono
fc-list : family | grep -E "Inter|JetBrains"
nproc   # cores -> parallel render jobs
```

# APPENDIX C — COMMAND REFERENCE (one project, end to end)

```bash
ENGINE=prompt_book/engine ; PROJ=projects/<slug> ; OUT=$PROJ/out ; mkdir -p $PROJ
python3 $ENGINE/transcribe.py <voiceover.mp3> models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8 $PROJ
python3 -c "import sys;sys.path.insert(0,'$ENGINE');import sfxlib;print(sfxlib.music_energy('<track.mp3>'))"
cp $ENGINE/scenes_TEMPLATE.py $PROJ/scenes1.py          # write shots; add scenes2.py ...
cd $ENGINE
JV_PROJECT=../../$PROJ python3 render.py contact 0 60 1.5 /tmp/sheet.png 5   # QA loop
JV_PROJECT=../../$PROJ python3 render.py bench 5 60 200
./render_all.sh ../../$PROJ ../../$OUT 8 $(nproc) 60          # run in the background + monitor
JV_PROJECT=../../$PROJ python3 ../../$PROJ/mix.py <vo> <music1> <music2> <music3> ../../$OUT
ffmpeg -i $OUT/video_only.mp4 -i $OUT/mix_final.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k \
       -shortest -movflags +faststart $OUT/<Title>.mp4
ffprobe -v error -show_entries format=duration:stream=width,height,r_frame_rate,nb_frames -of compact $OUT/<Title>.mp4
```

**SRT generation (from words.json):** group words into captions of ≤ 38 characters, break after sentence punctuation (when the text is > 18 characters) or at pauses > 0.9 s, end each caption at the next caption's start (or +0.9 s after sentence ends), minimum 0.6 s.

# APPENDIX D — GLOSSARY

- **Micro-beat:** one animated development within a shot (label pop, counter, glance, reframe).
- **Visual peak:** a planned standout moment with extra production effort (3–5 per film).
- **Honesty tag:** the top-left pill that classifies a shot as historical / fictional / model / concept.
- **Contact sheet:** a grid of downscaled frames at regular times, used for QA before rendering.
- **Ducking:** automatic lowering of music and ambience under the voice.
- **LUFS / dBTP:** integrated loudness (EBU R128) / true-peak level.
- **Multiplane:** separating layers by depth so that parallax produces depth.
- **Cutaway:** a cross-section showing interior layers through a removed wedge.
- **END_T:** the program end time (voiceover end + end card), defined in the last scenes file.
