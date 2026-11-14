"""QC: render one frame per phrase-scene (middle of its first shot) into contact sheets of 30."""
import os, sys
os.environ.setdefault("ASPECT", "landscape")
os.environ["OUT_W"], os.environ["OUT_H"] = "960", "540"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
import engine
import fourth_dimension as m
st = m.story
st.finalize()
engine._STORY = st
out = os.path.join(os.path.dirname(engine.HERE), "renders", "qc")
os.makedirs(out, exist_ok=True)
plan = m.story.plan
a = int(sys.argv[1]) if len(sys.argv) > 1 else 0
b = int(sys.argv[2]) if len(sys.argv) > 2 else len(plan)
ims = []
for p in plan[a:b]:
    t = p["t0"] + min(0.45, (p["t1"] - p["t0"]) * 0.6)
    data = engine.render_frame(int(t * engine.FPS))
    arr = np.frombuffer(data, np.uint8).reshape(engine.OUT_H, engine.OUT_W, 4)[:, :, 2::-1].copy()
    im = Image.fromarray(arr).resize((480, 270))
    ImageDraw.Draw(im).text((6, 4), f"{p['idx']} {p['tpl'].__name__[2:]}", fill=(255, 255, 0))
    ims.append(im)
cols = 5
for s0 in range(0, len(ims), 30):
    chunk = ims[s0:s0 + 30]
    rows = (len(chunk) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 480, rows * 270), (20, 20, 20))
    for k, im in enumerate(chunk):
        sheet.paste(im, ((k % cols) * 480, (k // cols) * 270))
    path = f"{out}/qc_{a + s0:03d}.jpg"
    sheet.save(path, quality=80)
    print(path)
