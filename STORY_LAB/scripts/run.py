"""usage: python run.py <slug> [stills|preview|full]
  stills  -> QC contact sheet (renders/<slug>_qc.png)
  preview -> 540x960 quick render
  full    -> 2K (1440x2560) final render, renders/<slug>_2K.mp4
"""
import importlib, os, sys
mode = sys.argv[2] if len(sys.argv) > 2 else "full"
if sys.argv[1] in ("fourth_dimension",):
    os.environ.setdefault("ASPECT", "landscape")
if mode == "preview":
    land = os.environ.get("ASPECT") == "landscape"
    os.environ["OUT_W"], os.environ["OUT_H"] = ("960", "540") if land else ("540", "960")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine, audio
mod = importlib.import_module(sys.argv[1])
story = mod.story
out_dir = os.path.join(os.path.dirname(engine.HERE), "renders")
os.makedirs(out_dir, exist_ok=True)
if mode == "stills":
    story.finalize()
    ts = [(a + b) / 2 for a, b, _, _ in story.spans]
    print(engine.render(story, os.path.join(out_dir, f"{story.slug}_qc.png"), stills=ts))
else:
    story.finalize()
    print("mix:", audio.build_mix(story))
    suffix = "_2K" if mode == "full" else "_preview"
    if len(sys.argv) > 4:
        engine.render(story, os.path.join(out_dir, f"{story.slug}_part.mp4"), float(sys.argv[3]), float(sys.argv[4]))
        sys.exit()
    engine.render(story, os.path.join(out_dir, f"{story.slug}{suffix}.mp4"))
