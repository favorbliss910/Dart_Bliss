"""
"Highway" scenes drawn with Manim: Weird (the paradox setup) and Braess (network explainer).
Render: .venv/bin/manim -qh --fps 60 -r 1440,2560 manim_demo/highway.py Weird Braess
"""
import json
from pathlib import Path
from manim import *

ROOT = Path(__file__).resolve().parent.parent
TL = json.loads((ROOT / "projects" / "highway" / "timeline.json").read_text())
config.frame_height = 16
config.frame_width = 9
FONT = "Poppins"
BG = "#0b1a33"


def sc(i):
    return next(s for s in TL["scenes"] if s["id"] == i)


def at(scene, beat):
    return TL["beats"][beat] - sc(scene)["start"]


def bg_grid():
    g = VGroup(Rectangle(width=9, height=16, fill_color=BG, fill_opacity=1, stroke_width=0))
    g.add(NumberPlane(x_range=[-5, 5, 0.5], y_range=[-9, 9, 0.5],
                      background_line_style={"stroke_color": "#4fc3ff", "stroke_opacity": 0.08, "stroke_width": 2},
                      axis_config={"stroke_opacity": 0}))
    g.add(Circle(6, fill_color="#1d3b6b", fill_opacity=0.35, stroke_width=0).shift(UP * 2))
    return g


def car_icon(color="#e74c3c", s=1.0):
    body = RoundedRectangle(corner_radius=0.18, width=1.6, height=0.5, fill_color=color, fill_opacity=1, stroke_color="#111", stroke_width=4)
    roof = RoundedRectangle(corner_radius=0.16, width=0.9, height=0.42, fill_color=color, fill_opacity=1, stroke_color="#111", stroke_width=4).shift(UP * 0.36 + RIGHT * 0.05)
    win = RoundedRectangle(corner_radius=0.08, width=0.7, height=0.24, fill_color="#bfe3ff", fill_opacity=1, stroke_width=0).move_to(roof).shift(DOWN * 0.02)
    wheels = VGroup(*[Circle(0.17, fill_color="#111", fill_opacity=1, stroke_width=0).shift([x, -0.27, 0]) for x in (-0.48, 0.5)])
    return VGroup(roof, win, body, wheels).scale(s)


def bus_icon(s=1.0):
    body = RoundedRectangle(corner_radius=0.15, width=2.4, height=1.0, fill_color="#f4b400", fill_opacity=1, stroke_color="#111", stroke_width=4)
    wins = VGroup(*[RoundedRectangle(corner_radius=0.05, width=0.38, height=0.32, fill_color="#bfe3ff", fill_opacity=1, stroke_width=0).shift([-0.85 + i * 0.48, 0.18, 0]) for i in range(5)])
    wheels = VGroup(*[Circle(0.18, fill_color="#111", fill_opacity=1, stroke_width=0).shift([x, -0.5, 0]) for x in (-0.7, 0.7)])
    return VGroup(body, wins, wheels).scale(s)


def bike_icon(s=1.0):
    w1 = Circle(0.42, stroke_color="#e9f5ff", stroke_width=8).shift(LEFT * 0.6)
    w2 = Circle(0.42, stroke_color="#e9f5ff", stroke_width=8).shift(RIGHT * 0.6)
    frame = VMobject(stroke_color="#4ade80", stroke_width=9).set_points_as_corners([[-0.6, 0, 0], [-0.1, 0.55, 0], [0.45, 0.55, 0], [0.6, 0, 0], [0, 0, 0], [-0.1, 0.55, 0]])
    return VGroup(w1, w2, frame).scale(s)


def title(txt, color="#ffffff", size=72):
    t = Text(txt, font=FONT, weight=BOLD, font_size=size, color=color)
    return t.scale_to_fit_width(8.2) if t.width > 8.2 else t


def fit(m, w=8.2):
    return m.scale_to_fit_width(w) if m.width > w else m


class Weird(Scene):
    def construct(self):
        D = sc("weird")["end"] - sc("weird")["start"]
        self.add(bg_grid())
        clock = [0.0]

        def until(t):
            if t > clock[0]:
                self.wait(t - clock[0])
                clock[0] = t

        def play(*a, run_time=0.5, **k):
            self.play(*a, run_time=run_time, **k)
            clock[0] += run_time

        head = title("THE WEIRD PART", "#ffd23f", 70).shift(UP * 6.2)
        play(FadeIn(head, shift=DOWN * 0.4), run_time=0.4)
        # "everybody figures he hates cars"
        car = car_icon(s=1.8).shift(UP * 2.2)
        heart = Text("♥", font_size=150, color="#ff4d6d").next_to(car, UP, buff=0.3)
        play(FadeIn(car, scale=0.6), run_time=0.4)
        hates = title("HATES CARS?", "#ff6b6b", 84).shift(DOWN * 0.4)
        play(Write(hates), run_time=0.6)
        # buses & bikes
        until(at("weird", "buses"))
        bus, bike = bus_icon(1.3).shift(LEFT * 2 + DOWN * 3.2), bike_icon(1.4).shift(RIGHT * 2 + DOWN * 3.2)
        play(FadeIn(bus, shift=UP * 0.6), FadeIn(bike, shift=UP * 0.6), run_time=0.5)
        # he doesn't
        until(at("weird", "doesnt"))
        x1 = VGroup(Line(UL, DR), Line(UR, DL)).set_stroke("#ff3b3b", 22).scale(1.4).move_to(bus)
        x2 = x1.copy().move_to(bike)
        nope = title("NOPE.", "#ffffff", 120).shift(DOWN * 0.4)
        play(Create(x1), Create(x2), Transform(hates, nope), car.animate.set_color("#4ade80"), run_time=0.4)
        play(FadeIn(heart, scale=0.3), run_time=0.3)
        # same traffic, fewer roads
        until(at("weird", "sametraffic"))
        self.play(*[FadeOut(m) for m in (car, heart, hates, bus, bike, x1, x2)], run_time=0.3); clock[0] += 0.3
        roads3 = VGroup(*[Line(LEFT * 3.8, RIGHT * 3.8, stroke_color="#7a7f86", stroke_width=40).shift(UP * (3.6 - i * 1.0)) for i in range(3)])
        roads2 = VGroup(*[Line(LEFT * 3.8, RIGHT * 3.8, stroke_color="#7a7f86", stroke_width=40).shift(DOWN * (0.6 + i * 1.0)) for i in range(2)])
        cars3 = VGroup(*[car_icon(["#e74c3c", "#3498db", "#f1c40f", "#2ecc71"][k % 4], 0.45).move_to(roads3[k % 3].point_from_proportion(0.1 + (k // 3) * 0.2)) for k in range(12)])
        cars2 = VGroup(*[car_icon(["#e74c3c", "#3498db", "#f1c40f", "#2ecc71"][k % 4], 0.45).move_to(roads2[k % 2].point_from_proportion(0.08 + (k // 2) * 0.16)) for k in range(12)])
        l1 = title("SAME TRAFFIC", "#ffffff", 56).shift(UP * 4.9)
        l2 = title("FEWER ROADS", "#ffd23f", 56).shift(DOWN * 2.4)
        play(Create(roads3), FadeIn(cars3, lag_ratio=0.05), Write(l1), run_time=0.7)
        play(TransformFromCopy(roads3[:2], roads2), TransformFromCopy(cars3, cars2), Write(l2), run_time=0.8)
        # faster?
        until(at("weird", "faster"))
        eq = title("= FASTER?!", "#4ade80", 110).shift(DOWN * 4.4)
        play(FadeIn(eq, scale=1.4), run_time=0.4)
        mover = [ValueTracker(0)]
        cars2.add_updater(lambda m, dt: m.shift(RIGHT * dt * 1.6))
        until(at("weird", "howpossible"))
        q = Text("?", font=FONT, weight=BOLD, font_size=520, color="#ffd23f").set_stroke("#111", 14, background=True)
        play(FadeIn(q, scale=0.2), *[m.animate.set_opacity(0.15) for m in (roads3, roads2, cars3, l1, l2, eq)], run_time=0.35)
        cars2.clear_updaters()
        until(D)


class Braess(Scene):
    def construct(self):
        D = sc("braess")["end"] - sc("braess")["start"]
        self.add(bg_grid())
        clock = [0.0]

        def until(t):
            if t > clock[0]:
                self.wait(t - clock[0])
                clock[0] = t

        def play(*a, run_time=0.5, **k):
            self.play(*a, run_time=run_time, **k)
            clock[0] += run_time

        A, B = np.array([0, 5.2, 0]), np.array([0, -4.6, 0])
        C, Dn = np.array([-3.1, 0.3, 0]), np.array([3.1, 0.3, 0])
        RED, GREEN, GREY, BLUE = "#ff4d4d", "#4ade80", "#8b95a5", "#7fd9ff"
        e = {
            "AC": Line(A, C, stroke_width=26, color=GREY), "CB": Line(C, B, stroke_width=26, color=GREY),
            "AD": Line(A, Dn, stroke_width=26, color=GREY), "DB": Line(Dn, B, stroke_width=26, color=GREY),
            "CD": Line(C, Dn, stroke_width=34, color=BLUE),
        }
        nodes = VGroup(*[VGroup(Circle(0.42, fill_color="#fff", fill_opacity=1, stroke_color="#111", stroke_width=6),
                                Text(n, font=FONT, weight=BOLD, font_size=40, color="#111")).move_to(p)
                         for n, p in (("A", A), ("B", B), ("", C), ("", Dn))])
        home = Text("HOME", font=FONT, weight=BOLD, font_size=34, color="#fff").next_to(A, UP, buff=0.55)
        work = Text("WORK", font=FONT, weight=BOLD, font_size=34, color="#fff").next_to(B, DOWN, buff=0.55)
        sky_lbl = Text("SKYWAY", font=FONT, weight=BOLD, font_size=36, color=BLUE).next_to(e["CD"], UP, buff=0.25)
        play(*[Create(v) for v in e.values()], FadeIn(nodes), FadeIn(home), FadeIn(work), FadeIn(sky_lbl), run_time=0.8)

        # cars as dots flowing along routes, driven by a time tracker
        T = ValueTracker(0)
        mode = {"m": "shortcut"}
        routes = {"shortcut": [A, C, Dn, B], "left": [A, C, B], "right": [A, Dn, B]}

        def path_point(pts, u):
            segs = [np.linalg.norm(pts[i + 1] - pts[i]) for i in range(len(pts) - 1)]
            L = sum(segs)
            d = (u % 1) * L
            for i, s in enumerate(segs):
                if d <= s:
                    return pts[i] + (pts[i + 1] - pts[i]) * (d / s)
                d -= s
            return pts[-1]

        dots = VGroup()
        N = 26
        for i in range(N):
            dot = Dot(radius=0.13, color="#ffd23f").set_stroke("#111", 3, background=True)
            dot.idx = i
            dots.add(dot)

        def upd(m):
            t = T.get_value()
            for d in m:
                i = d.idx
                if mode["m"] == "shortcut":
                    speed = 0.12
                    d.move_to(path_point(routes["shortcut"], t * speed + i / N))
                else:
                    r = routes["left"] if i % 2 == 0 else routes["right"]
                    speed = 0.32
                    d.move_to(path_point(r, t * speed + (i // 2) / (N / 2)))

        dots.add_updater(upd)
        self.add(dots)
        self.add(T)
        T.add_updater(lambda m, dt: m.increment_value(dt))

        lbl = fit(Text("FASTEST FOR ME", font=FONT, weight=BOLD, font_size=60, color="#fff")).to_edge(UP, buff=0.5)
        play(FadeIn(lbl), run_time=0.4)
        until(at("braess", "everyone"))
        lbl2 = fit(Text("SLOWEST FOR EVERYONE", font=FONT, weight=BOLD, font_size=60, color=RED)).to_edge(UP, buff=0.5)
        play(Transform(lbl, lbl2), run_time=0.4)
        until(at("braess", "piles"))
        timer = VGroup(RoundedRectangle(corner_radius=0.3, width=4.6, height=1.5, fill_color="#111", fill_opacity=0.9, stroke_color="#fff", stroke_width=5),
                       Text("45 MIN", font=FONT, weight=BOLD, font_size=80, color=RED)).shift(DOWN * 6.6)
        play(e["AC"].animate.set_color(RED), e["DB"].animate.set_color(RED), e["CD"].animate.set_color(RED), FadeIn(timer, shift=UP), run_time=0.6)
        until(at("braess", "jams"))
        play(e["AC"].animate.set_stroke(width=40), e["DB"].animate.set_stroke(width=40), Indicate(timer, color=RED), run_time=0.6)
        until(at("braess", "takeaway"))
        cut = VGroup(Line(UL, DR), Line(UR, DL)).set_stroke("#fff", 20).scale(0.7).move_to(e["CD"])
        play(Create(cut), run_time=0.3)
        mode["m"] = "spread"
        timer2 = VGroup(RoundedRectangle(corner_radius=0.3, width=4.6, height=1.5, fill_color="#111", fill_opacity=0.9, stroke_color="#fff", stroke_width=5),
                        Text("15 MIN", font=FONT, weight=BOLD, font_size=80, color=GREEN)).shift(DOWN * 6.6)
        lbl3 = fit(Text("SAME CARS, SPREAD OUT", font=FONT, weight=BOLD, font_size=56, color=GREEN)).to_edge(UP, buff=0.5)
        play(FadeOut(e["CD"]), FadeOut(sky_lbl), FadeOut(cut), *[e[k].animate.set_color(GREEN).set_stroke(width=26) for k in ("AC", "CB", "AD", "DB")],
             Transform(timer, timer2), Transform(lbl, lbl3), run_time=0.7)
        self.remove(e["CD"], sky_lbl, cut)

        # stadium analogy
        until(at("braess", "stadium"))
        dots.clear_updaters()
        T.clear_updaters()
        net = VGroup(*[e[k] for k in ("AC", "CB", "AD", "DB")], nodes, home, work, dots, timer, lbl)
        play(FadeOut(net), run_time=0.35)
        wall = VGroup()
        stadium = RoundedRectangle(corner_radius=1.6, width=8.0, height=6.0, stroke_color="#cfd8e3", stroke_width=10, fill_color="#173057", fill_opacity=1).shift(UP * 2.2)
        field = RoundedRectangle(corner_radius=1.0, width=5.6, height=3.8, fill_color="#2e7d32", fill_opacity=1, stroke_color="#fff", stroke_width=4).move_to(stadium)
        gate = Rectangle(width=1.4, height=0.5, fill_color="#ffd23f", fill_opacity=1, stroke_width=0).move_to(stadium.get_bottom())
        doors = VGroup(*[Rectangle(width=0.7, height=0.4, fill_color="#4ade80", fill_opacity=1, stroke_width=0).move_to(p)
                         for p in (stadium.get_left() + UP * 1.2, stadium.get_left() + DOWN * 1.2, stadium.get_right() + UP * 1.2, stadium.get_right() + DOWN * 1.2, stadium.get_bottom() + RIGHT * 2.8)])
        crowd = VGroup(*[Dot(radius=0.11, color=["#ffd23f", "#ff8fab", "#7fd9ff", "#fff"][i % 4]).move_to(
            [(np.random.RandomState(i).rand() - 0.5) * 7, -3.6 - np.random.RandomState(i + 99).rand() * 3.2, 0]) for i in range(90)])
        gtxt = Text("ONE GIANT GATE", font=FONT, weight=BOLD, font_size=54, color="#ffd23f").shift(DOWN * 7.2)
        play(FadeIn(stadium), FadeIn(field), FadeIn(gate), FadeIn(crowd, lag_ratio=0.01), FadeIn(gtxt), run_time=0.6)
        # everyone sprints to the gate and jams
        play(*[d.animate.move_to(gate.get_center() + DOWN * (0.3 + (i % 18) * 0.09) + RIGHT * ((i % 7) - 3) * 0.09 * (1 + (i % 18) * 0.15)) for i, d in enumerate(crowd)],
             run_time=1.6, rate_func=rate_functions.ease_in_quad)
        until(at("braess", "sidedoors"))
        play(FadeIn(doors, scale=1.5), Transform(gtxt, Text("5 SIDE DOORS, WIDE OPEN", font=FONT, weight=BOLD, font_size=50, color="#4ade80").shift(DOWN * 7.2)), run_time=0.4)
        targets = [doors[i % 5].get_center() for i in range(len(crowd))]
        play(*[d.animate.move_to(field.get_center() + np.array([(np.random.RandomState(i + 7).rand() - 0.5) * 5, (np.random.RandomState(i + 3).rand() - 0.5) * 3.2, 0]))
               for i, d in enumerate(crowd)], run_time=1.6, rate_func=rate_functions.ease_in_out_cubic)
        until(D)
