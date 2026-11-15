"""Generate a 2D cartoon character sprite (transparent PNG) in the reference style.

Style rules taken from the reference video:
  * huge round head (~45% of total height), off-white fill, thick dark outline
  * simple facial features: circle eyes with small pupils, tiny mouth line
  * optional hair "flame" tuft on top
  * small rounded torso (hoodie / jacket) with a flat colour
  * stick legs and arms drawn as thick dark lines
These sprites are placed on camera-facing planes inside Blender so the
3D lighting (rim light, colour bounce, depth of field) falls on them.

Usage:
  python make_character.py <spec.json> <out.png>
spec keys (all optional): skin, outline, hair, hair_color, shirt, expression,
  badge, height_px
"""
import json
import math
import sys

from PIL import Image, ImageDraw

DEFAULT = {
    "skin": "#F4EFE6",
    "outline": "#1B1726",
    "hair": "tuft",          # none | tuft | bun | beanie
    "hair_color": "#C8582A",
    "shirt": "#E0A23A",
    "expression": "neutral",  # neutral | happy | sad | worried | shocked | grin
    "badge": None,           # hex colour for a small chest badge, or None
    "height_px": 2048,
}


def draw_character(spec):
    s = {**DEFAULT, **(spec or {})}
    H = int(s["height_px"])
    W = H // 2
    ss = 2  # supersample for smooth edges
    img = Image.new("RGBA", (W * ss, H * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    k = W * ss / 1000.0  # design units: canvas is 1000 x 2000
    lw = int(14 * k)
    ol = s["outline"]

    def P(x, y):
        return (x * k, y * k)

    # legs (stick)
    for x0, x1 in ((450, 430), (550, 570)):
        d.line([P(x0, 1450), P(x1, 1940)], fill=ol, width=int(18 * k))
        d.line([P(x1, 1940), P(x1 + (25 if x1 > 500 else -25), 1945)], fill=ol, width=int(18 * k))
    # torso
    d.rounded_rectangle([P(330, 980), P(670, 1480)], radius=int(90 * k), fill=s["shirt"], outline=ol, width=lw)
    if s.get("badge"):
        d.ellipse([P(520, 1150), P(610, 1240)], fill=s["badge"], outline=ol, width=int(6 * k))
    # arms
    d.line([P(345, 1060), P(250, 1400)], fill=ol, width=int(16 * k))
    d.line([P(655, 1060), P(750, 1400)], fill=ol, width=int(16 * k))

    # head
    cx, cy, r = 500, 600, 400
    d.ellipse([P(cx - r, cy - r), P(cx + r, cy + r)], fill=s["skin"], outline=ol, width=lw)

    # hair
    hc = s["hair_color"]
    if s["hair"] == "tuft":
        pts = []
        n = 7
        for i in range(n * 2 + 1):
            a = math.pi * (1.05 + 0.9 * i / (n * 2))
            rr = r * (1.18 if i % 2 else 0.98)
            pts.append(P(cx + rr * math.cos(a), cy - 40 + rr * math.sin(a) * 0.85))
        pts.append(P(cx + r * 0.9, cy - 120))
        pts.append(P(cx - r * 0.9, cy - 120))
        d.polygon(pts, fill=hc, outline=ol)
        d.line(pts + [pts[0]], fill=ol, width=int(10 * k), joint="curve")
    elif s["hair"] == "bun":
        d.ellipse([P(cx - 90, cy - r - 150), P(cx + 90, cy - r + 20)], fill=hc, outline=ol, width=lw)
        d.chord([P(cx - r, cy - r), P(cx + r, cy + r)], 190, 350, fill=hc, outline=ol, width=lw)
    elif s["hair"] == "beanie":
        d.chord([P(cx - r - 10, cy - r - 30), P(cx + r + 10, cy + r)], 180, 360, fill=hc, outline=ol, width=lw)
        d.rectangle([P(cx - r - 10, cy - 30), P(cx + r + 10, cy + 40)], fill=hc, outline=ol, width=lw)

    # face
    ex = s["expression"]
    eye_y = cy + 40
    for ex_x in (cx - 120, cx + 120):
        er = 70 if ex in ("worried", "shocked") else 58
        if ex == "happy":
            d.arc([P(ex_x - 55, eye_y - 40), P(ex_x + 55, eye_y + 50)], 200, 340, fill=ol, width=int(14 * k))
            continue
        if ex == "grin":
            d.ellipse([P(ex_x - 22, eye_y - 22), P(ex_x + 22, eye_y + 22)], fill=ol)
            continue
        d.ellipse([P(ex_x - er, eye_y - er), P(ex_x + er, eye_y + er)], fill="#FFFFFF", outline=ol, width=int(12 * k))
        pr = 20 if ex != "shocked" else 14
        d.ellipse([P(ex_x - pr, eye_y - pr + 8), P(ex_x + pr, eye_y + pr + 8)], fill=ol)
    if ex in ("sad", "worried"):  # brows
        d.line([P(cx - 190, eye_y - 85), P(cx - 70, eye_y - 125)], fill=ol, width=int(12 * k))
        d.line([P(cx + 190, eye_y - 85), P(cx + 70, eye_y - 125)], fill=ol, width=int(12 * k))
    my = cy + 210
    if ex == "happy":
        d.arc([P(cx - 90, my - 70), P(cx + 90, my + 50)], 20, 160, fill=ol, width=int(13 * k))
    elif ex == "grin":
        d.chord([P(cx - 170, my - 110), P(cx + 170, my + 90)], 0, 180, fill="#FFFFFF", outline=ol, width=int(12 * k))
        for t in range(-120, 140, 40):
            d.line([P(cx + t, my - 10), P(cx + t, my + 70)], fill=ol, width=int(6 * k))
    elif ex == "shocked":
        d.ellipse([P(cx - 40, my - 40), P(cx + 40, my + 50)], fill=ol)
    elif ex in ("sad", "worried"):
        d.arc([P(cx - 70, my), P(cx + 70, my + 90)], 200, 340, fill=ol, width=int(12 * k))
    else:
        d.line([P(cx - 50, my), P(cx + 50, my)], fill=ol, width=int(12 * k))

    return img.resize((W, H), Image.LANCZOS)


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1])) if sys.argv[1] != "-" else {}
    draw_character(spec).save(sys.argv[2])
    print("wrote", sys.argv[2])
