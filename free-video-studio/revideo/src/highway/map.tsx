/** @jsxImportSource @revideo/2d/lib */
// Top-down city map scenes for "Highway" (Revideo). Canvas 1440x2560, origin at center.
import {Circle, Line, makeScene2D, Node, Rect, Txt} from '@revideo/2d';
import {all, createRef, createSignal, easeOutBack, easeOutCubic, linear, waitFor} from '@revideo/core';
import tl from '../../../projects/highway/timeline.json';

const W = 1440, H = 2560;
const FONT = 'Poppins';
const beats = tl.beats as Record<string, number>;
const sc = (id: string) => tl.scenes.find((s) => s.id === id)!;
const at = (scene: string, beat: string) => beats[beat] - sc(scene).start;

// deterministic random
const rnd = (n: number) => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };

const SKY_X = 0, SKY_W = 300;
const V_STREETS = [-560, -330, 330, 560];
const H_STREETS = [-1080, -660, -240, 180, 600, 1020];
const CAR_COLORS = ['#e74c3c', '#3498db', '#ecf0f1', '#2c3e50', '#f1c40f', '#2ecc71', '#9b59b6', '#e67e22', '#95a5a6'];

function topCar(color: string, w = 46, h = 84) {
  return (
    <Rect width={w} height={h} radius={12} fill={color} stroke={'#111'} lineWidth={3} shadowColor={'rgba(0,0,0,.45)'} shadowBlur={10} shadowOffset={[6, 8]}>
      <Rect y={-h * 0.18} width={w - 12} height={h * 0.22} radius={5} fill={'#a9d3ee'} />
      <Rect y={h * 0.26} width={w - 14} height={h * 0.14} radius={4} fill={'#7fa9c4'} />
    </Rect>
  );
}

function cityBase(view: Node) {
  view.add(<Rect width={W} height={H} fill={'#3d7a3a'} />);
  // blocks with building roofs
  const xs = [-720, ...V_STREETS, 720];
  const sky = [SKY_X - SKY_W / 2 - 40, SKY_X + SKY_W / 2 + 40];
  const colEdges = [-720, -560, -330, sky[0], sky[1], 330, 560, 720];
  const rowEdges = [-1280, ...H_STREETS, 1280];
  for (let c = 0; c < colEdges.length - 1; c++) {
    for (let r = 0; r < rowEdges.length - 1; r++) {
      const x0 = colEdges[c] + 40, x1 = colEdges[c + 1] - 40, y0 = rowEdges[r] + 40, y1 = rowEdges[r + 1] - 40;
      if (x1 - x0 < 60 || (colEdges[c] === sky[0])) continue;
      const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
      view.add(<Rect x={cx} y={cy} width={x1 - x0} height={y1 - y0} radius={10} fill={'#c9c3b6'} />);
      const n = 2 + Math.floor(rnd(c * 31 + r) * 3);
      for (let k = 0; k < n; k++) {
        const bw = (x1 - x0 - 30) / n;
        const hue = ['#8d99ae', '#b08968', '#6d6875', '#a3b18a', '#9c6644', '#7f8c8d'][Math.floor(rnd(c * 7 + r * 13 + k) * 6)];
        view.add(<Rect x={x0 + 15 + bw * (k + 0.5)} y={cy} width={bw - 14} height={y1 - y0 - 40} radius={6} fill={hue}
          shadowColor={'rgba(0,0,0,.5)'} shadowBlur={18} shadowOffset={[14, 18]}>
          <Rect width={bw * 0.4} height={(y1 - y0) * 0.25} radius={4} fill={'rgba(255,255,255,.18)'} />
        </Rect>);
      }
    }
  }
  void xs;
  // side streets
  for (const x of V_STREETS) {
    view.add(<Rect x={x} width={90} height={H} fill={'#55595f'} />);
    view.add(<Line points={[[x, -H / 2], [x, H / 2]]} stroke={'#e9e3c9'} lineWidth={4} lineDash={[30, 30]} />);
  }
  for (const y of H_STREETS) {
    view.add(<Rect y={y} width={W} height={90} fill={'#55595f'} />);
    view.add(<Line points={[[-W / 2, y], [W / 2, y]]} stroke={'#e9e3c9'} lineWidth={4} lineDash={[30, 30]} />);
  }
  // the skyway (elevated, with shadow)
  const sky_ = createRef<Rect>();
  view.add(<Rect x={SKY_X + 30} y={0} width={SKY_W} height={H} fill={'rgba(0,0,0,.35)'} />);
  view.add(<Rect ref={sky_} x={SKY_X} width={SKY_W} height={H} fill={'#767b82'} stroke={'#c9ced4'} lineWidth={10} />);
  for (const lx of [-50, 50]) view.add(<Line points={[[lx, -H / 2], [lx, H / 2]]} stroke={'#e9e9e9'} lineWidth={5} lineDash={[40, 40]} />);
  view.add(<Line points={[[0, -H / 2], [0, H / 2]]} stroke={'#f1c40f'} lineWidth={6} />);
  view.add(<Rect x={-560} y={-1180} width={260} height={70} radius={12} fill={'#1f8a4c'} stroke={'#fff'} lineWidth={4}>
    <Txt text={'SIDE ST'} fontFamily={FONT} fontWeight={800} fontSize={34} fill={'#fff'} /></Rect>);
  view.add(<Rect x={0} y={-1180} width={260} height={70} radius={12} fill={'#1f8a4c'} stroke={'#fff'} lineWidth={4}>
    <Txt text={'SKYWAY'} fontFamily={FONT} fontWeight={800} fontSize={34} fill={'#fff'} /></Rect>);
  return sky_;
}

// cars on a vertical lane, reactive to time t
function laneCars(view: Node, t: () => number, x: number, count: number, speed: number, dir: 1 | -1, spacing: number, seed: number, visible: () => number = () => 1) {
  for (let i = 0; i < count; i++) {
    const c = topCar(CAR_COLORS[Math.floor(rnd(seed + i) * CAR_COLORS.length)]) as Rect;
    const base = i * spacing + rnd(seed * 3 + i) * 20;
    c.x(x);
    c.rotation(dir === 1 ? 180 : 0);
    c.y(() => {
      const span = H + 200;
      let p = (base + t() * speed) % span;
      return dir === 1 ? -H / 2 - 100 + p : H / 2 + 100 - p;
    });
    c.opacity(visible);
    view.add(c);
  }
}
function rowCars(view: Node, t: () => number, y: number, count: number, speed: number, dir: 1 | -1, spacing: number, seed: number, visible: () => number = () => 1) {
  for (let i = 0; i < count; i++) {
    const c = topCar(CAR_COLORS[Math.floor(rnd(seed + i) * CAR_COLORS.length)]) as Rect;
    const base = i * spacing + rnd(seed * 5 + i) * 30;
    c.y(y);
    c.rotation(dir === 1 ? 90 : -90);
    c.x(() => {
      const span = W + 200;
      const p = (base + t() * speed) % span;
      return dir === 1 ? -W / 2 - 100 + p : W / 2 + 100 - p;
    });
    c.opacity(visible);
    view.add(c);
  }
}

function notebook(view: Node, lines: string[]) {
  const nb = createRef<Rect>();
  const txts = lines.map(() => createRef<Txt>());
  view.add(<Rect ref={nb} y={1600} width={1100} height={700} radius={20} fill={'#f6e7b0'} stroke={'#3a3a3a'} lineWidth={6} rotation={-3}
    shadowColor={'rgba(0,0,0,.5)'} shadowBlur={40} shadowOffset={[0, 20]}>
    {[...Array(8)].map((_, i) => <Line points={[[-500, -230 + i * 70], [500, -230 + i * 70]]} stroke={'#9fc3d9'} lineWidth={3} />)}
    <Line points={[[-430, -330], [-430, 330]]} stroke={'#e57373'} lineWidth={4} />
    {lines.map((l, i) => <Txt ref={txts[i]} x={-390} y={-200 + i * 140} offsetX={-1} text={l} fontFamily={FONT} fontWeight={800} fontStyle={'italic'}
      fontSize={76} fill={'#1d2a6b'} />)}
  </Rect>);
  return {nb, txts};
}

function stopwatchBadge(x: number, y: number, label: string) {
  return (
    <Node x={x} y={y} scale={0}>
      <Circle size={150} fill={'#fff'} stroke={'#111'} lineWidth={8} shadowColor={'rgba(0,0,0,.5)'} shadowBlur={20} />
      <Rect y={-88} width={30} height={24} fill={'#555'} />
      <Txt y={6} text={label} fontFamily={FONT} fontWeight={900} fontSize={40} fill={'#111'} />
    </Node>
  );
}

// ======================================================= SIDE STREETS (engineer's observation)
export const sidestreets = makeScene2D('sidestreets', function* (view) {
  const S = sc('sidestreets'), D = S.end - S.start;
  const t = createSignal(0);
  const cam = createRef<Node>();
  view.add(<Node ref={cam} scale={1.25} />);
  cityBase(cam());
  // jammed skyway: dense, crawling
  for (const [lx, dir, seed] of [[-112, -1, 1], [-37, -1, 2], [37, 1, 3], [112, 1, 4]] as const) laneCars(cam(), t, lx, 26, 18, dir as 1 | -1, 102, seed);
  // side streets: almost empty
  laneCars(cam(), t, -560, 2, 260, 1, 1300, 9);
  laneCars(cam(), t, 330, 1, 240, -1, 1300, 10);
  rowCars(cam(), t, 600, 1, 300, 1, 1600, 11);
  // red jam glow along skyway
  const jam = createRef<Rect>();
  cam().add(<Rect ref={jam} width={SKY_W + 60} height={H} fill={'rgba(255,40,40,.0)'} stroke={'rgba(255,60,60,.9)'} lineWidth={0} />);
  const highlight = V_STREETS.map(() => createRef<Rect>());
  V_STREETS.forEach((x, i) => cam().add(<Rect ref={highlight[i]} x={x} width={100} height={H} fill={'rgba(80,200,255,.0)'} />));
  const badges = [stopwatchBadge(-560, -400, '0:42'), stopwatchBadge(330, 300, '0:38'), stopwatchBadge(560, -800, '0:51'), stopwatchBadge(-330, 800, '0:40')];
  badges.forEach((b) => cam().add(b));
  const {nb, txts} = notebook(view, ['Every driver takes', 'the shortcut.', 'Every. Single. Time.']);

  yield* all(
    t(D, D, linear),
    cam().scale(1.05, D, easeOutCubic),
    (function* () {
      yield* jam().fill('rgba(255,40,40,.28)', 0.8);
      yield* waitFor(Math.max(0, at('sidestreets', 'sidestreets') - 0.8));
      yield* all(...highlight.map((h) => h().fill('rgba(80,200,255,.35)', 0.5)));
      for (const b of badges) yield* b.scale(1, 0.25, easeOutBack);
      yield* waitFor(Math.max(0, at('sidestreets', 'weirdthing') - at('sidestreets', 'sidestreets') - 1.5));
      yield* nb().y(700, 0.6, easeOutBack);
      yield* waitFor(Math.max(0, at('sidestreets', 'everydriver') - at('sidestreets', 'weirdthing') - 0.6));
      for (const x of txts) yield* x().scale(1.08, 0.2).to(1, 0.3);
    })(),
  );
});

// ======================================================= FLOW (skyway closed, traffic spreads out)
export const flow = makeScene2D('flow', function* (view) {
  const S = sc('flow'), D = S.end - S.start;
  const t = createSignal(0);
  const spread = createSignal(0);
  const cam = createRef<Node>();
  view.add(<Node ref={cam} scale={1.0} />);
  const sky = cityBase(cam());
  sky().fill('#5d6168');
  // closure barricades + water on skyway
  for (const y of [-900, 0, 900]) {
    cam().add(<Rect y={y} width={SKY_W - 20} height={50} fill={'#e63946'} stroke={'#fff'} lineWidth={6} />);
    cam().add(<Line points={[[-120, y - 60], [120, y + 60]]} stroke={'#fff'} lineWidth={16} lineCap={'round'} />);
    cam().add(<Line points={[[120, y - 60], [-120, y + 60]]} stroke={'#fff'} lineWidth={16} lineCap={'round'} />);
  }
  cam().add(<Circle y={450} size={260} fill={'rgba(120,200,255,.55)'} />);
  // cars spread on every side street, moving briskly
  let seed = 100;
  for (const x of V_STREETS) { laneCars(cam(), t, x - 20, 6, 300, 1, 440, seed++, spread); laneCars(cam(), t, x + 20, 6, 280, -1, 440, seed++, spread); }
  for (const y of H_STREETS) { rowCars(cam(), t, y - 20, 4, 320, 1, 420, seed++, spread); rowCars(cam(), t, y + 20, 4, 300, -1, 420, seed++, spread); }
  // ambulance (top-down)
  const amb = createRef<Node>();
  const lightOn = () => (Math.floor(t() * 6) % 2 === 0 ? 1 : 0);
  cam().add(<Node ref={amb} x={-330} y={1400} opacity={0}>
    <Rect width={70} height={140} radius={14} fill={'#fff'} stroke={'#111'} lineWidth={4} shadowColor={'rgba(0,0,0,.5)'} shadowBlur={14} shadowOffset={[6, 8]}>
      <Rect width={60} height={14} fill={'#d62828'} /><Rect width={14} height={60} fill={'#d62828'} />
      <Rect y={-56} x={-18} width={24} height={14} fill={() => (lightOn() ? '#ff2b2b' : '#5a0f0f')} />
      <Rect y={-56} x={18} width={24} height={14} fill={() => (lightOn() ? '#5a0f0f' : '#3b2bff')} />
    </Rect>
    <Circle size={300} fill={() => (lightOn() ? 'rgba(255,40,40,.25)' : 'rgba(60,60,255,.25)')} />
  </Node>);
  const clock = createRef<Rect>();
  view.add(<Rect ref={clock} y={-850} width={900} height={330} radius={40} fill={'rgba(15,15,20,.88)'} stroke={'#fff'} lineWidth={6} scale={0}>
    <Txt y={-90} text={'5 MILES'} fontFamily={FONT} fontWeight={700} fontSize={64} fill={'#fff'} />
    <Txt y={40} text={'15 MIN'} fontFamily={FONT} fontWeight={900} fontSize={170} fill={'#4ade80'} />
  </Rect>);
  // basement stopwatch inset
  const inset = createRef<Node>();
  const hand = createRef<Line>();
  view.add(<Node ref={inset} y={650} scale={0}>
    <Rect width={900} height={900} radius={40} fill={'#2b2d2f'} stroke={'#fff'} lineWidth={8} shadowColor={'rgba(0,0,0,.6)'} shadowBlur={40} />
    <Circle size={560} fill={'#e9eef2'} stroke={'#222'} lineWidth={22} />
    <Rect y={-330} width={90} height={70} radius={10} fill={'#9aa3ab'} stroke={'#222'} lineWidth={6} />
    {[...Array(12)].map((_, i) => <Line points={[[0, -240], [0, -210]]} stroke={'#222'} lineWidth={8} rotation={i * 30} />)}
    <Line ref={hand} points={[[0, 30], [0, -220]]} stroke={'#d62828'} lineWidth={12} lineCap={'round'} />
    <Circle size={40} fill={'#222'} />
    <Txt y={130} text={'15:00'} fontFamily={'monospace'} fontWeight={900} fontSize={80} fill={'#111'} />
  </Node>);

  yield* all(
    t(D, D, linear),
    cam().scale(1.15, D, linear),
    (function* () {
      yield* waitFor(Math.max(0, at('flow', 'spill') - 0.3));
      yield* spread(1, 1.2);
      yield* waitFor(Math.max(0, at('flow', 'arriveearly') - at('flow', 'spill') - 1.5));
      amb().opacity(1);
      yield* all(amb().y(-1300, 1.4, linear),
        (function* () { yield* waitFor(Math.max(0, at('flow', 'fifteen') - at('flow', 'arriveearly'))); yield* clock().scale(1, 0.35, easeOutBack); })());
      yield* waitFor(Math.max(0, at('flow', 'click') - at('flow', 'arriveearly') - 1.4 - 0.1));
      yield* all(clock().scale(0, 0.2), inset().scale(1, 0.35, easeOutBack));
      yield* hand().rotation(360, 1.2, easeOutCubic);
    })(),
  );
});
