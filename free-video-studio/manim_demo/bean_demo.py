"""
Test 2D cartoon in the reference style: a bean character with a big round face,
dot eyes and stick legs walks into a scene, waves, and talks, with
word-by-word captions. Vertical 9:16 for Shorts/TikTok.

Render (from free-video-studio/):
  .venv/bin/manim -qm --fps 30 -r 1080,1920 manim_demo/bean_demo.py BeanDemo
"""
from pathlib import Path
from manim import *

FONTS = Path(__file__).resolve().parent.parent / "assets" / "fonts"
config.background_color = "#8FD3FF"
config.frame_height = 16
config.frame_width = 9


class Bean(VGroup):
    """Bean-style character built from simple shapes."""

    def __init__(self, shirt="#E8473C", **kw):
        super().__init__(**kw)
        ink = "#1E1E1E"
        self.leg_l = Line([-0.25, -1.1, 0], [-0.3, -2.3, 0], color=ink, stroke_width=10)
        self.leg_r = Line([0.25, -1.1, 0], [0.3, -2.3, 0], color=ink, stroke_width=10)
        self.body = RoundedRectangle(corner_radius=0.55, width=1.2, height=1.9, fill_color=shirt,
                                     fill_opacity=1, stroke_color=ink, stroke_width=8).shift(DOWN * 0.3)
        self.arm_l = Line([-0.55, 0.0, 0], [-1.05, -0.9, 0], color=ink, stroke_width=8)
        self.arm_r = Line([0.55, 0.0, 0], [1.05, -0.9, 0], color=ink, stroke_width=8)
        self.head = Circle(radius=0.95, fill_color=WHITE, fill_opacity=1, stroke_color=ink,
                           stroke_width=8).shift(UP * 1.45)
        self.hair = Arc(radius=0.97, start_angle=PI * 0.08, angle=PI * 0.84, color=ink,
                        stroke_width=26).shift(UP * 1.45)
        eye = lambda x: VGroup(Circle(0.22, fill_color=WHITE, fill_opacity=1, stroke_color=ink, stroke_width=6),
                               Dot(radius=0.09, color=ink)).shift([x, 1.55, 0])
        self.eyes = VGroup(eye(-0.32), eye(0.32))
        self.mouth = Arc(radius=0.25, start_angle=PI * 1.15, angle=PI * 0.7, color=ink,
                         stroke_width=7).shift(UP * 1.25)
        self.add(self.leg_l, self.leg_r, self.arm_l, self.arm_r, self.body,
                 self.head, self.hair, self.eyes, self.mouth)


def town():
    ground = Rectangle(width=16, height=6, fill_color="#5BC453", fill_opacity=1, stroke_width=0).shift(DOWN * 6.2)
    road = Rectangle(width=16, height=1.2, fill_color="#6B6B78", fill_opacity=1, stroke_width=0).shift(DOWN * 4.0)
    houses = VGroup()
    for i, (x, c) in enumerate([(-3.2, "#F4D35E"), (0, "#EE964B"), (3.2, "#F95738")]):
        wall = Square(2.0, fill_color=c, fill_opacity=1, stroke_color="#1E1E1E", stroke_width=6)
        roof = Triangle(fill_color="#3D405B", fill_opacity=1, stroke_color="#1E1E1E",
                        stroke_width=6).stretch_to_fit_width(2.5).stretch_to_fit_height(1.2).next_to(wall, UP, buff=0)
        door = Rectangle(width=0.5, height=0.8, fill_color="#3D2C2E", fill_opacity=1, stroke_width=0
                         ).align_to(wall, DOWN)
        houses.add(VGroup(wall, roof, door).move_to([x, -1.9, 0]))
    sun = Circle(0.9, fill_color="#FFE45C", fill_opacity=1, stroke_width=0).move_to([2.8, 5.5, 0])
    clouds = VGroup(*[VGroup(*[Circle(r, fill_color=WHITE, fill_opacity=1, stroke_width=0).shift([dx, 0, 0])
                               for r, dx in [(0.45, -0.5), (0.6, 0), (0.45, 0.55)]]).move_to(p)
                      for p in ([-2.5, 4.6, 0], [1.0, 6.3, 0])])
    return VGroup(sun, clouds, houses, ground, road), clouds


class BeanDemo(Scene):
    def caption(self, words, start_wait=0.0, per_word=0.32):
        with register_font(str(FONTS / "Poppins-ExtraBold.ttf")):
            for w in words:
                t = Text(w, font="Poppins", weight=BOLD, font_size=96, color=WHITE,
                         stroke_color=BLACK, stroke_width=10).move_to([0, 2.4, 0])
                t.set_z_index(10)
                self.add(t)
                self.play(t.animate(rate_func=there_and_back_with_pause).scale(1.12), run_time=per_word)
                self.remove(t)

    def construct(self):
        bg, clouds = town()
        self.add(bg)
        clouds.add_updater(lambda m, dt: m.shift(RIGHT * 0.15 * dt))

        bean = Bean().scale(1.5).move_to([-6.5, -2.6, 0])
        self.add(bean)

        # walk in with a bounce
        for _ in range(4):
            self.play(bean.animate.shift(RIGHT * 1.6 + UP * 0.25), run_time=0.25, rate_func=smooth)
            self.play(bean.animate.shift(DOWN * 0.25), run_time=0.15)

        # wave (rotate right arm up and back)
        self.play(Rotate(bean.arm_r, angle=PI * 0.8, about_point=bean.arm_r.get_start()), run_time=0.3)
        for _ in range(2):
            self.play(Rotate(bean.arm_r, angle=-PI * 0.2, about_point=bean.arm_r.get_start()), run_time=0.15)
            self.play(Rotate(bean.arm_r, angle=PI * 0.2, about_point=bean.arm_r.get_start()), run_time=0.15)

        # talk: captions pop word by word
        self.caption(["This", "town", "has", "one", "weird", "rule..."])

        # surprised face
        surprised = Circle(0.15, stroke_color="#1E1E1E", stroke_width=7, fill_color="#1E1E1E",
                           fill_opacity=1).move_to(bean.mouth)
        self.play(Transform(bean.mouth, surprised), bean.eyes.animate.scale(1.25), run_time=0.25)
        self.play(bean.animate.shift(UP * 0.6), run_time=0.2, rate_func=there_and_back)
        self.caption(["Never", "press", "the", "button!"])
        self.wait(0.5)
