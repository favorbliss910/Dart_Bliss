"""
Teleport sample in Manim (same script/timing as compare/script.json).
Render:  .venv/bin/manim -qh --fps 30 -r 1080,1920 manim_demo/teleport.py Teleport
"""
import json
import os
from pathlib import Path
from manim import *

ROOT = Path(__file__).resolve().parent.parent
S = json.loads((ROOT / "compare" / "script.json").read_text())
config.frame_height = 16
config.frame_width = 9
INK = "#1d1b2e"
U = 9 / 1080  # pixels -> manim units


def px(x, y):
    """Convert Remotion-style pixel coords (center origin, y down) to manim units."""
    return np.array([x * U, -y * U, 0])


def character(shirt="#6b42c4"):
    g = VGroup()
    shadow = Ellipse(width=1.4, height=0.2, fill_color=BLACK, fill_opacity=0.25, stroke_width=0).shift(DOWN * 2.6)
    leg_l = Line([-0.2, -1.15, 0], [-0.2, -2.55, 0], color=INK, stroke_width=9)
    leg_r = Line([0.2, -1.15, 0], [0.2, -2.55, 0], color=INK, stroke_width=9)
    arm_l = Line([-0.5, 0, 0], [-0.72, -1.05, 0], color=INK, stroke_width=9)
    arm_r = Line([0.5, 0, 0], [0.72, -1.05, 0], color=INK, stroke_width=9)
    body = RoundedRectangle(corner_radius=0.5, width=1.1, height=1.75, fill_color=shirt, fill_opacity=1,
                            stroke_color=INK, stroke_width=8).shift(DOWN * 0.45)
    head = Circle(0.87, fill_color="#f5f3fb", fill_opacity=1, stroke_color=INK, stroke_width=8).shift(UP * 1.25)
    hair = RoundedRectangle(corner_radius=0.2, width=1.5, height=0.42, fill_color="#3a2a2a", fill_opacity=1,
                            stroke_color=INK, stroke_width=6).shift(UP * 1.9)
    eyes = VGroup(*[VGroup(Circle(0.2, fill_color=WHITE, fill_opacity=1, stroke_color=INK, stroke_width=5),
                           Dot(radius=0.07, color=INK).shift(RIGHT * 0.03)).shift([x, 1.2, 0]) for x in (-0.28, 0.28)])
    mouth = RoundedRectangle(corner_radius=0.03, width=0.36, height=0.07, fill_color=INK, fill_opacity=1,
                             stroke_width=0).shift(UP * 0.73)
    g.add(shadow, leg_l, leg_r, arm_l, arm_r, body, head, hair, eyes, mouth)
    g.legs, g.eyes, g.mouth = (leg_l, leg_r), eyes, mouth
    return g


def booth(label):
    glow = RoundedRectangle(corner_radius=0.45, width=2.7, height=5.0, fill_color="#9ff0ff", fill_opacity=0,
                            stroke_width=0)
    glass = RoundedRectangle(corner_radius=0.35, width=2.5, height=4.8, fill_color="#7fd3ff", fill_opacity=0.35,
                             stroke_color="#2b4d73", stroke_width=8)
    shine = RoundedRectangle(corner_radius=0.08, width=0.16, height=4.2, fill_color=WHITE, fill_opacity=0.35,
                             stroke_width=0).shift(LEFT * 0.85)
    sign = RoundedRectangle(corner_radius=0.15, width=2.85, height=0.7, fill_color="#d5dde8", fill_opacity=1,
                            stroke_color="#2b4d73", stroke_width=7).shift(UP * 2.65)
    txt = Text(label, font="Poppins", weight=BOLD, font_size=30, color="#20344f").move_to(sign)
    base = RoundedRectangle(corner_radius=0.12, width=3.0, height=0.55, fill_color="#aab4c3", fill_opacity=1,
                            stroke_color="#2b4d73", stroke_width=7).shift(DOWN * 2.65)
    back = VGroup(glow, glass, shine)
    front = VGroup(sign, txt, base)
    back.glow = glow
    return back, front


def city(night):
    g = VGroup(Rectangle(width=9, height=16, fill_color="#4a2f72" if night else "#d6efff", fill_opacity=1, stroke_width=0))
    if night:
        g.add(Rectangle(width=9, height=6, fill_color="#b06a8c", fill_opacity=0.6, stroke_width=0).shift(DOWN * 1.2))
    far = VGroup()
    for i in range(9):
        b = Rectangle(width=1.08, height=7.5, fill_color="#3b2b63" if night else "#cfd9e6", fill_opacity=0.95,
                      stroke_width=0).move_to(px(-560 + i * 150, 300 - (i % 3) * 120))
        if night:
            for k in range(12):
                b.add(Rectangle(width=0.17, height=0.25, fill_color="#ffd27a" if (k * 7 + i) % 4 else "#4b3a75",
                                fill_opacity=1, stroke_width=0).move_to(b.get_center() + px(-36 + (k % 3) * 36, -400 + (k // 3) * 70)))
        far.add(b)
    g.add(far)
    if night:
        g.add(Circle(0.38, fill_color="#fff4c9", fill_opacity=1, stroke_width=0).move_to(px(260, -720)))
        g.add(Line(px(-320, -800), px(-390, 140), color="#ff3b2f", stroke_width=12),
              Line(px(-320, -800), px(-250, 140), color="#ff3b2f", stroke_width=12),
              *[Line(px(-360 + i * 12, yy), px(-280 - i * 12, yy), color="#ff3b2f", stroke_width=10)
                for i, yy in enumerate((-500, -300, -100))])
    trees = [(300, -260, "#ffb7d5"), (460, -200, "#ff9fc6")] if night else [(-470, -300, "#7cc95a"), (450, -260, "#6cbb4a")]
    for tx, ty, c in trees:
        g.add(Rectangle(width=0.22, height=3.5, fill_color="#6b4a3a", fill_opacity=1, stroke_width=0).move_to(px(tx, ty + 300)))
        for dx, dy, r in [(0, 0, 220), (-90, 80, 170), (90, 70, 190), (0, 140, 200)]:
            g.add(Circle(r * U / 2, fill_color=c, fill_opacity=1, stroke_width=0).move_to(px(tx + dx, ty + dy)))
    g.add(Rectangle(width=9, height=140 * U, fill_color="#6c6080" if night else "#d9d4cc", fill_opacity=1, stroke_width=0).move_to(px(0, 180)))
    g.add(Rectangle(width=9, height=720 * U, fill_color="#3c3552" if night else "#7a7a86", fill_opacity=1, stroke_width=0).move_to(px(0, 600)))
    if night:
        for i in range(7):
            g.add(Rectangle(width=90 * U, height=260 * U, fill_color="#e8e4f0", fill_opacity=0.85, stroke_width=0).move_to(px(-450 + i * 150, 520)))
    return g, far


class Teleport(MovingCameraScene):
    def setup_captions(self):
        self.cap_words = []
        for w in S["words"]:
            base = Text(w["w"], font="Poppins", weight=BOLD, font_size=80, color=WHITE)
            outline = base.copy().set_stroke("#111111", width=16).set_fill("#111111", 1)
            t = VGroup(outline, base).move_to(px(0, 260))
            t.set_z_index(100)
            self.cap_words.append((w["t"], t))
        self.cap_holder = VMobject().set_z_index(100)
        self.cap_shown = None

        def upd(m, dt):
            now = self.renderer.time
            cur = None
            for t0, txt in self.cap_words:
                if now >= t0:
                    cur = (t0, txt)
            if cur is None:
                return
            t0, txt = cur
            pop = min(1, (now - t0) / 0.12)
            new = txt.copy().scale(0.7 + 0.3 * (1 - (1 - pop) ** 3))
            new.move_to(self.camera.frame.get_center() + px(0, 260) * (self.camera.frame.height / 16))
            new.scale(self.camera.frame.height / 16)
            m.become(new)

        self.cap_holder.add_updater(upd)

    def clear_all(self):
        self.remove(*[m for m in self.mobjects if m is not self.cap_holder])
        self.camera.frame.set(height=16).move_to(ORIGIN)

    def construct(self):
        self.setup_captions()
        if os.environ.get('CAPS', '1') != '0':
            self.add(self.cap_holder)
        frame = self.camera.frame

        # ---- 1. counter (0-4s)
        bg = VGroup(Rectangle(width=9, height=16, fill_color="#2a070c", fill_opacity=1, stroke_width=0),
                    Circle(5.8, fill_color="#5a0d16", fill_opacity=0.8, stroke_width=0).move_to(px(0, -500)),
                    Rectangle(width=1.42, height=16, fill_color="#6a0e1a", fill_opacity=1, stroke_width=0).move_to(px(-455, 0)),
                    Rectangle(width=1.42, height=16, fill_color="#6a0e1a", fill_opacity=1, stroke_width=0).move_to(px(455, 0)))
        panel = RoundedRectangle(corner_radius=0.2, width=5.8, height=3.0, fill_color="#120306", fill_opacity=1,
                                 stroke_color="#3a0a10", stroke_width=10).move_to(px(0, -360))
        title = Text("TELEPORTS TODAY", font="Poppins", weight=BOLD, font_size=38, color="#ff5050").move_to(px(0, -470))
        bar = Rectangle(width=5.2, height=0.22, fill_color="#ffcc00", fill_opacity=1, stroke_width=0).move_to(px(0, -240))
        n = ValueTracker(1204557000)
        num = always_redraw(lambda: Text(f"{int(n.get_value()):,}", font="Monospace", weight=BOLD, font_size=58,
                                         color="#ff2b2b").move_to(px(0, -350)))
        booths = VGroup(*[RoundedRectangle(corner_radius=0.17, width=1.08, height=2.1, fill_color="#7fd3ff", fill_opacity=0.4,
                                           stroke_color="#9fb4c8", stroke_width=5).move_to(px(-430 + i * 172, 420)) for i in range(6)])
        floor = Rectangle(width=9, height=3.5, fill_color="#120305", fill_opacity=1, stroke_width=0).move_to(px(0, 760))
        self.add(bg, panel, title, num, bar, booths, floor)
        frame.set(height=16 / 1.15)
        self.play(n.animate(rate_func=rate_functions.ease_out_cubic).set_value(1204557881),
                  frame.animate(rate_func=rate_functions.ease_in_out_cubic).set(height=16), run_time=3.6)
        self.wait(0.4)

        # ---- 2. new york (4-8.5s)
        self.clear_all()
        scene_city, far = city(False)
        back, front = booth("NEW YORK")
        back.shift(px(0, 30)); front.shift(px(0, 30))
        guy = character().scale(0.9).move_to(px(-640, 0))
        door = Rectangle(width=2.5, height=0.01, fill_color="#9fdcff", fill_opacity=0.6, stroke_width=0).move_to(px(0, 300), aligned_edge=DOWN)
        self.add(scene_city, back, guy, door, front)
        target_h = 16 / 1.18
        walk = guy.animate(rate_func=rate_functions.ease_out_cubic).shift(RIGHT * 640 * U)
        self.play(walk, far.animate(rate_func=linear).shift(LEFT * 0.25), frame.animate(rate_func=linear).set(height=16 - (16 - target_h) * 0.45), run_time=2.0)
        self.wait(0.3)
        wow_mouth = Ellipse(width=0.24, height=0.28, fill_color=INK, fill_opacity=1, stroke_width=0).move_to(guy.mouth)
        self.play(door.animate.stretch_to_fit_height(4.6, about_edge=DOWN), Transform(guy.mouth, wow_mouth),
                  guy.eyes.animate.scale(1.25), frame.animate.set(height=16 - (16 - target_h) * 0.6), run_time=0.5)
        self.wait(0.5)
        fl = Rectangle(width=20, height=30, fill_color="#e9fbff", fill_opacity=0, stroke_width=0).set_z_index(50)
        self.add(fl)
        self.play(fl.animate.set_fill(opacity=1), back.glow.animate.set_fill(opacity=1), run_time=0.2)
        self.remove(guy)
        self.play(fl.animate.set_fill(opacity=0), back.glow.animate.set_fill(opacity=0), frame.animate.set(height=target_h), run_time=1.0)

        # ---- 3. blueprint (8.5-12.5s)
        self.clear_all()
        self.add(Rectangle(width=9, height=16, fill_color="#0d3e86", fill_opacity=1, stroke_width=0))
        self.add(NumberPlane(x_range=[-5, 5, 0.5], y_range=[-9, 9, 0.5], background_line_style={"stroke_color": WHITE, "stroke_opacity": 0.08, "stroke_width": 2},
                             axis_config={"stroke_opacity": 0}))
        for i, x in enumerate((-290, 290)):
            self.add(RoundedRectangle(corner_radius=0.25, width=220 * U, height=420 * U, stroke_color="#dff1ff", stroke_width=5).move_to(px(x, 150)),
                     RoundedRectangle(corner_radius=0.08, width=260 * U, height=50 * U, stroke_color="#dff1ff", stroke_width=5).move_to(px(x, -80)),
                     RoundedRectangle(corner_radius=0.08, width=280 * U, height=44 * U, stroke_color="#dff1ff", stroke_width=5).move_to(px(x, 380)),
                     Text("TOKYO" if i else "NEW YORK", font="Poppins", weight=BOLD, font_size=40, color="#eaf6ff").move_to(px(x, 480)),
                     Text("PRINTER" if i else "SCANNER", font="Poppins", font_size=20, color="#eaf6ff").move_to(px(x, -130)))
        footer = RoundedRectangle(corner_radius=0.02, width=800 * U, height=120 * U, stroke_color="#dff1ff", stroke_width=4).move_to(px(0, 600))
        self.add(footer, Text("TELEPORT MK II · HOW IT WORKS", font="Poppins", font_size=17, color="#dff1ff").move_to(px(-90, 600)),
                 Text("CLASSIFIED", font="Poppins", weight=BOLD, font_size=17, color="#ff6b6b").move_to(px(300, 600)))
        arc = ArcBetweenPoints(px(-290, -110), px(290, -110), angle=-PI * 0.75, color="#7fd9ff", stroke_width=7)
        dashed = DashedVMobject(ArcBetweenPoints(px(-180, 190), px(180, 190), angle=-PI / 3, color="#dff1ff", stroke_width=5), num_dashes=12)
        label = Text("DATA ONLY", font="Poppins", weight=BOLD, font_size=50, color="#eaf6ff").move_to(px(0, -540))
        a, b = character().scale(0.5).move_to(px(-290, 160)), character().scale(0.5).move_to(px(290, 160))
        b.set_opacity(0)
        dot = Dot(radius=0.13, color="#bff4ff")
        self.add(dashed, a, b)
        self.wait(0.3)
        self.play(Create(arc), MoveAlongPath(dot, arc), FadeIn(label), a.animate.set_opacity(0), b.animate.set_opacity(1),
                  run_time=1.5, rate_func=rate_functions.ease_in_out_cubic)
        self.remove(dot)
        self.wait(0.6)
        x = VGroup(Line(px(-60, -60), px(60, 60), color="#ff4d4d", stroke_width=22),
                   Line(px(60, -60), px(-60, 60), color="#ff4d4d", stroke_width=22)).move_to(px(0, 120))
        self.play(GrowFromCenter(x), run_time=0.35, rate_func=rate_functions.ease_out_back)
        self.wait(1.25)

        # ---- 4. tokyo (12.5-16s)
        self.clear_all()
        scene_city, _ = city(True)
        back, front = booth("TOKYO")
        back.shift(px(0, 30)); front.shift(px(0, 30))
        guy = character().scale(0.9).move_to(px(0, 0))
        door = Rectangle(width=2.5, height=4.6, fill_color="#9fdcff", fill_opacity=0.6, stroke_width=0).move_to(px(0, 300), aligned_edge=DOWN)
        self.add(scene_city, back, door, front)
        frame.set(height=16 / 1.12)
        fl = Rectangle(width=20, height=30, fill_color="#e9fbff", fill_opacity=0, stroke_width=0).set_z_index(50)
        self.add(fl)
        self.wait(0.15)
        self.play(fl.animate.set_fill(opacity=1), back.glow.animate.set_fill(opacity=0.9), run_time=0.2)
        self.add(guy)
        self.bring_to_front(door, front, fl)
        wow_mouth = Ellipse(width=0.24, height=0.28, fill_color=INK, fill_opacity=1, stroke_width=0).move_to(guy.mouth)
        self.play(Transform(guy.mouth, wow_mouth), guy.eyes.animate.scale(1.25), run_time=0.15)
        self.play(fl.animate.set_fill(opacity=0), back.glow.animate.set_fill(opacity=0), frame.animate.set(height=16 / 1.08), run_time=0.6)
        self.play(door.animate.stretch_to_fit_height(0.01, about_edge=DOWN), frame.animate.set(height=16 / 1.05), run_time=0.5)
        self.play(guy.animate(rate_func=rate_functions.ease_out_cubic).shift(RIGHT * 220 * U), frame.animate.set(height=16 / 1.02), run_time=1.1)
        q = Text("?", font="Poppins", weight=BOLD, font_size=130, color=WHITE, stroke_color="#111111", stroke_width=10).move_to(px(300, -420))
        self.play(GrowFromCenter(q), frame.animate.set(height=16), run_time=0.35, rate_func=rate_functions.ease_out_back)
        self.wait(0.45)
