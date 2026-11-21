/** @jsxImportSource @motion-canvas/2d/lib */
// "Highway" scenes drawn in Motion Canvas: City Hall + "Famous". Canvas 1440x2560, origin center.
import {Circle, Line, makeScene2D, Node, Rect, Txt, Gradient} from '@motion-canvas/2d';
import {all, createRef, easeInOutCubic, easeOutBack, easeOutCubic, linear, loop, waitFor, Reference} from '@motion-canvas/core';
import tl from '../../../projects/highway/timeline.json';

const W = 1440, H = 2560, FONT = 'Poppins';
const beats = tl.beats as Record<string, number>;
const sc = (id: string) => tl.scenes.find((s) => s.id === id)!;
const at = (scene: string, b: string) => beats[b] - sc(scene).start;
const SKIN = new Gradient({type: 'linear', from: [-60, 0], to: [60, 0], stops: [{offset: 0, color: '#f2c9a5'}, {offset: 1, color: '#d9a47f'}]});

function* waitUntil(clock: {t: number}, target: number) {
  if (target > clock.t) { yield* waitFor(target - clock.t); clock.t = target; }
}

// semi-realistic engineer bust/full figure
function engineer(ref: Reference<Node>, x: number, y: number, s = 1, mouthRef?: Reference<Line>) {
  return (
    <Node ref={ref} x={x} y={y} scale={s}>
      <Rect y={420} width={70} height={300} fill={'#2f3642'} x={-40} radius={10} />
      <Rect y={420} width={70} height={300} fill={'#262c36'} x={40} radius={10} />
      <Rect y={580} x={-46} width={96} height={30} radius={10} fill={'#1d1d1d'} /><Rect y={580} x={46} width={96} height={30} radius={10} fill={'#1d1d1d'} />
      <Rect y={130} width={260} height={360} radius={[90, 90, 20, 20]} fill={'#f4f6f8'} stroke={'#2a2a2a'} lineWidth={4} />
      <Rect y={140} x={-85} width={90} height={340} radius={[60, 0, 10, 20]} fill={'#ff7a12'} />
      <Rect y={140} x={85} width={90} height={340} radius={[0, 60, 20, 10]} fill={'#ff7a12'} />
      <Rect y={210} x={-85} width={90} height={18} fill={'#eef4f6'} /><Rect y={210} x={85} width={90} height={18} fill={'#eef4f6'} />
      <Rect y={-60} width={60} height={60} fill={SKIN} />
      <Circle y={-170} width={180} height={205} fill={SKIN} stroke={'#5a3b2a'} lineWidth={3} />
      <Rect y={-258} width={186} height={70} radius={[90, 90, 20, 20]} fill={'#3b2a20'} />
      <Rect x={-42} y={-165} width={58} height={42} radius={10} stroke={'#222'} lineWidth={6} fill={'rgba(200,230,255,.25)'} />
      <Rect x={42} y={-165} width={58} height={42} radius={10} stroke={'#222'} lineWidth={6} fill={'rgba(200,230,255,.25)'} />
      <Circle x={-40} y={-165} size={14} fill={'#2a1a10'} /><Circle x={44} y={-165} size={14} fill={'#2a1a10'} />
      <Line ref={mouthRef} points={[[-28, -105], [0, -98], [28, -105]]} stroke={'#6b2b1f'} lineWidth={7} lineCap={'round'} radius={20} />
    </Node>
  );
}

function councilMember(x: number, y: number, suit: string, hair: string, seed: number) {
  const mouth = createRef<Rect>();
  const body = createRef<Node>();
  const node = (
    <Node ref={body} x={x} y={y}>
      <Rect y={150} width={250} height={240} radius={[100, 100, 10, 10]} fill={suit} />
      <Rect y={110} width={60} height={160} fill={'#f4f4f4'} />
      <Rect y={150} width={24} height={130} fill={['#b23a48', '#2b4c7e', '#3a7d44'][seed % 3]} />
      <Circle y={-20} width={150} height={175} fill={SKIN} stroke={'#5a3b2a'} lineWidth={3} />
      <Rect y={-95} width={156} height={50} radius={[70, 70, 10, 10]} fill={hair} />
      <Circle x={-30} y={-25} size={14} fill={'#2a1a10'} /><Circle x={30} y={-25} size={14} fill={'#2a1a10'} />
      <Rect ref={mouth} y={30} width={44} height={8} radius={4} fill={'#5a1f1f'} />
    </Node>
  );
  return {node, mouth, body};
}

// ========================================================= CITY HALL
export const cityhall = makeScene2D(function* (view) {
  const S = sc('cityhall'), D = S.end - S.start;
  const clock = {t: 0};
  const cam = createRef<Node>();
  view.add(<Node ref={cam} />);
  // wood-paneled chamber
  cam().add(<Rect width={W * 3} height={H * 3} fill={new Gradient({type: 'linear', from: [0, -1280], to: [0, 1280], stops: [{offset: 0, color: '#3b2516'}, {offset: 0.6, color: '#6b4429'}, {offset: 1, color: '#2a1a10'}]})} />);
  for (let i = -9; i <= 9; i++) cam().add(<Rect x={i * 170} y={-500} width={150} height={900} radius={8} stroke={'rgba(0,0,0,.25)'} lineWidth={6} fill={'rgba(255,255,255,.03)'} />);
  cam().add(<Circle y={-760} size={380} fill={'#c9a227'} stroke={'#7a5c10'} lineWidth={14}>
    <Circle size={290} stroke={'#7a5c10'} lineWidth={6} /><Txt text={'CITY'} fontFamily={FONT} fontWeight={900} fontSize={70} fill={'#5c440b'} y={-20} />
    <Txt text={'COUNCIL'} fontFamily={FONT} fontWeight={800} fontSize={40} fill={'#5c440b'} y={40} /></Circle>);
  for (const fx of [-560, 560]) cam().add(<Node x={fx} y={-620}><Rect width={12} height={700} fill={'#c9a227'} />
    <Rect x={fx < 0 ? 80 : -80} y={-200} width={160} height={110} fill={'#2b4c7e'} /><Rect x={fx < 0 ? 80 : -80} y={-160} width={160} height={22} fill={'#fff'} /></Node>);
  // council members behind dais
  const members = [
    councilMember(-500, -60, '#2d3142', '#2a1d14', 0), councilMember(-250, -100, '#4f5d75', '#8a8a8a', 1), councilMember(0, -120, '#1d3557', '#111', 2),
    councilMember(250, -100, '#5c4033', '#c9a06b', 3), councilMember(500, -60, '#2d3142', '#3b2a20', 4),
  ];
  members.forEach((m) => cam().add(m.node));
  // dais
  cam().add(<Rect y={260} width={1400} height={320} radius={[60, 60, 0, 0]} fill={new Gradient({type: 'linear', from: [0, -160], to: [0, 160], stops: [{offset: 0, color: '#8a5a35'}, {offset: 1, color: '#4a2e1a'}]})} stroke={'#2a1a10'} lineWidth={8} />);
  members.forEach((m, i) => cam().add(<Rect x={m.node.x()} y={160} width={180} height={50} radius={6} fill={'#d9c27a'}><Txt text={['DIAZ', 'MOORE', 'CHAIR', 'PARK', 'OKAFOR'][i]} fontFamily={FONT} fontWeight={800} fontSize={30} fill={'#3b2a10'} /></Rect>));
  members.forEach((m) => cam().add(<Line points={[[m.node.x() + 60, 140], [m.node.x() + 30, 20]]} stroke={'#222'} lineWidth={8} />));
  // coffee cup + budget papers on dais
  const cup = createRef<Node>(), spill = createRef<Rect>();
  cam().add(<Rect x={330} y={120} width={240} height={160} rotation={-6} fill={'#f6f3ea'} stroke={'#999'} lineWidth={3}><Txt text={'BUDGET'} fontFamily={FONT} fontWeight={800} fontSize={40} fill={'#333'} /></Rect>);
  cam().add(<Rect ref={spill} x={350} y={135} width={0} height={60} radius={30} fill={'rgba(90,50,20,.85)'} />);
  cam().add(<Node ref={cup} x={200} y={90}><Rect width={70} height={90} radius={[4, 4, 16, 16]} fill={'#fff'} stroke={'#555'} lineWidth={4} /><Rect y={-38} width={66} height={14} fill={'#5a3214'} /></Node>);
  // floor
  cam().add(<Rect y={1900} width={W * 3} height={2700} fill={new Gradient({type: 'linear', from: [0, -450], to: [0, 450], stops: [{offset: 0, color: '#5a1f1f'}, {offset: 1, color: '#2e0f0f'}]})} />);
  // engineer + plan
  const eng = createRef<Node>(), mouth = createRef<Line>();
  cam().add(engineer(eng, 900, 900, 1.0, mouth));
  const plan = createRef<Rect>();
  cam().add(<Rect ref={plan} x={0} y={1020} width={0} height={620} opacity={0} fill={'#0d3e86'} stroke={'#dff1ff'} lineWidth={8} clip>
    <Txt y={-210} text={'THE PLAN'} fontFamily={FONT} fontWeight={800} fontSize={60} fill={'#dff1ff'} />
    <Rect y={10} width={760} height={110} fill={'#767b82'} stroke={'#dff1ff'} lineWidth={4} />
    <Line points={[[-420, -90], [420, 110]]} stroke={'#ff4d4d'} lineWidth={34} lineCap={'round'} />
    <Line points={[[420, -90], [-420, 110]]} stroke={'#ff4d4d'} lineWidth={34} lineCap={'round'} />
    <Txt y={220} text={'TEAR IT DOWN'} fontFamily={FONT} fontWeight={900} fontSize={96} fill={'#fff'} />
  </Rect>);
  const ha = createRef<Node>();
  view.add(<Node ref={ha} opacity={0}>{[[-480, -480, -12], [0, -560, 6], [460, -470, 10], [-260, -360, -4], [250, -380, 4]].map(([x, y, r]) =>
    <Txt x={x} y={y} rotation={r} text={'HA HA'} fontFamily={FONT} fontWeight={900} fontSize={96} fill={'#ffd23f'} stroke={'#111'} lineWidth={12} strokeFirst />)}</Node>);
  const bubble = createRef<Rect>(), bubbleTxt = createRef<Txt>();
  view.add(<Rect ref={bubble} x={-60} y={-760} width={1080} height={300} radius={60} fill={'#fff'} stroke={'#111'} lineWidth={10} scale={0}>
    <Txt ref={bubbleTxt} text={'"Great idea!"'} fontFamily={FONT} fontWeight={800} fontSize={84} fill={'#111'} width={980} textAlign={'center'} textWrap />
    <Line points={[[-200, 140], [-280, 280], [-100, 140]]} fill={'#fff'} stroke={'#111'} lineWidth={10} closed />
  </Rect>);
  const card = createRef<Rect>();
  view.add(<Rect ref={card} y={-700} width={1200} height={460} radius={40} fill={'#111'} stroke={'#ffd23f'} lineWidth={12} scale={0}>
    <Txt y={-80} text={'SAME CARS.'} fontFamily={FONT} fontWeight={900} fontSize={130} fill={'#fff'} />
    <Txt y={80} text={'FEWER ROADS.'} fontFamily={FONT} fontWeight={900} fontSize={130} fill={'#ffd23f'} />
  </Rect>);

  const laughing = () => all(...members.map((m, i) => loop(8, () => all(m.mouth().height(40, 0.12).to(8, 0.12), m.body().y(m.body().y() - 14, 0.12).to(m.body().y(), 0.12)))));
  yield* all(
    cam().scale(1.06, D, linear),
    (function* () {
      yield* eng().x(420, 1.6, easeOutCubic); clock.t = 1.6;
      yield* waitUntil(clock, at('cityhall', 'tear'));
      yield* all(plan().opacity(1, 0.1), plan().width(1100, 0.6, easeOutBack)); clock.t += 0.6;
      yield* waitUntil(clock, at('cityhall', 'laughs'));
      yield* all(ha().opacity(1, 0.2), laughing(),
        (function* () { yield* waitFor(at('cityhall', 'coffee') - at('cityhall', 'laughs')); yield* all(cup().rotation(100, 0.3), cup().position([260, 120], 0.3), spill().width(260, 0.6)); })());
      clock.t = at('cityhall', 'laughs') + 1.92;
      yield* ha().opacity(0, 0.3); clock.t += 0.3;
      yield* waitUntil(clock, at('cityhall', 'greatidea'));
      yield* all(cam().scale(1.5, 0.6, easeInOutCubic), cam().position([375, 300], 0.6, easeInOutCubic), plan().opacity(0, 0.3));
      clock.t += 0.6;
      yield* waitUntil(clock, at('cityhall', 'greatidea') + 1.4);
      yield* bubble().scale(1, 0.3, easeOutBack); clock.t += 0.3;
      yield* waitUntil(clock, at('cityhall', 'hunger'));
      bubbleTxt().text('"And to fix hunger, we\'ll close the restaurants."');
      yield* bubble().scale(1.06, 0.1).to(1, 0.15); clock.t += 0.25;
      yield* waitUntil(clock, at('cityhall', 'smiles'));
      yield* all(bubble().scale(0, 0.2), cam().scale(1.7, 0.7, easeInOutCubic), cam().position([-714, -1100], 0.7, easeInOutCubic),
        mouth().points([[-34, -110], [0, -86], [34, -110]], 0.4));
      clock.t += 0.7;
      yield* waitUntil(clock, at('cityhall', 'samecars'));
      yield* card().scale(1, 0.4, easeOutBack); clock.t += 0.4;
      yield* waitUntil(clock, D);
    })(),
  );
});

// ========================================================= FAMOUS (newspaper, radio, honks)
export const famous = makeScene2D(function* (view) {
  const S = sc('famous'), D = S.end - S.start;
  const clock = {t: 0};
  const bg = createRef<Rect>();
  view.add(<Rect ref={bg} width={W} height={H} fill={new Gradient({type: 'radial', from: 0, to: 0, toRadius: 1600, stops: [{offset: 0, color: '#3a3a44'}, {offset: 1, color: '#111116'}]})} />);
  // calendar flipping: "by the end of the month"
  const cal = createRef<Rect>(), day = createRef<Txt>();
  view.add(<Rect ref={cal} y={-200} width={700} height={760} radius={30} fill={'#fff'} stroke={'#111'} lineWidth={8} shadowColor={'rgba(0,0,0,.6)'} shadowBlur={40}>
    <Rect y={-300} width={700} height={160} radius={[30, 30, 0, 0]} fill={'#d62828'}><Txt text={'MARCH'} fontFamily={FONT} fontWeight={900} fontSize={90} fill={'#fff'} /></Rect>
    <Txt ref={day} y={80} text={'1'} fontFamily={FONT} fontWeight={900} fontSize={360} fill={'#111'} />
  </Rect>);
  // newspaper
  const paper = createRef<Node>();
  view.add(<Node ref={paper} scale={0} rotation={-720}>
    <Rect width={1240} height={1600} fill={'#f3efe3'} shadowColor={'rgba(0,0,0,.6)'} shadowBlur={60} shadowOffset={[0, 30]} />
    <Txt y={-700} text={'THE DAILY COMMUTER'} fontFamily={'Georgia'} fontSize={72} fill={'#111'} letterSpacing={6} />
    <Line points={[[-560, -640], [560, -640]]} stroke={'#111'} lineWidth={6} />
    <Txt y={-520} text={'BLOW IT UP?!'} fontFamily={'Georgia'} fontWeight={900} fontSize={150} fill={'#111'} />
    <Rect y={60} width={1000} height={900} fill={'#fbf8ef'} stroke={'#111'} lineWidth={5} />
    {/* editorial cartoon: engineer with dynamite + cone on head (ink style) */}
    <Node y={140} scale={0.95}>
      <Circle y={-220} width={220} height={250} fill={'#fbf8ef'} stroke={'#111'} lineWidth={8} />
      <Line points={[[-80, -320], [0, -560], [80, -320]]} closed fill={'#ff7a12'} stroke={'#111'} lineWidth={8} />
      <Rect y={-370} width={150} height={30} fill={'#fff'} stroke={'#111'} lineWidth={4} />
      <Rect y={-380} width={230} height={30} fill={'#ff7a12'} stroke={'#111'} lineWidth={6} />
      <Circle x={-45} y={-220} size={34} stroke={'#111'} lineWidth={6} /><Circle x={45} y={-220} size={34} stroke={'#111'} lineWidth={6} />
      <Line points={[[-50, -150], [0, -120], [50, -150]]} stroke={'#111'} lineWidth={8} radius={30} />
      <Rect y={130} width={300} height={420} radius={60} fill={'#fbf8ef'} stroke={'#111'} lineWidth={8} />
      <Line points={[[150, 30], [330, -120]]} stroke={'#111'} lineWidth={10} />
      <Rect x={360} y={-180} width={70} height={240} radius={14} fill={'#e23b2e'} stroke={'#111'} lineWidth={8} rotation={20} />
      <Line points={[[380, -300], [420, -360], [400, -400]]} stroke={'#111'} lineWidth={6} />
      <Txt x={440} y={-430} text={'✸'} fontSize={70} fill={'#ff9f1a'} />
      <Line points={[[-80, 340], [-90, 500]]} stroke={'#111'} lineWidth={10} /><Line points={[[80, 340], [90, 500]]} stroke={'#111'} lineWidth={10} />
    </Node>
    <Txt y={620} text={'"Anti-road guy" wants to destroy the Skyway'} fontFamily={'Georgia'} fontStyle={'italic'} fontSize={44} fill={'#333'} />
  </Node>);
  // radio
  const radio = createRef<Node>();
  const waves = [0, 1, 2].map(() => createRef<Circle>());
  view.add(<Node ref={radio} scale={0}>
    {waves.map((w) => <Circle ref={w} y={-100} size={300} stroke={'#ffd23f'} lineWidth={14} opacity={0} />)}
    <Rect width={900} height={560} radius={60} fill={new Gradient({type: 'linear', from: [0, -280], to: [0, 280], stops: [{offset: 0, color: '#b5651d'}, {offset: 1, color: '#6b3a10'}]})} stroke={'#2a1505'} lineWidth={10} />
    <Circle x={-200} size={360} fill={'#2a2016'} stroke={'#d9b26b'} lineWidth={12} />
    {[...Array(6)].map((_, i) => <Line points={[[-340, -120 + i * 48], [-60, -120 + i * 48]]} stroke={'#4a3a28'} lineWidth={10} />)}
    <Rect x={230} y={-90} width={300} height={120} radius={14} fill={'#f6e7b0'} stroke={'#2a1505'} lineWidth={6}><Txt text={'98.7 FM'} fontFamily={'monospace'} fontWeight={900} fontSize={52} fill={'#3a2a10'} /></Rect>
    <Circle x={160} y={120} size={110} fill={'#d9b26b'} stroke={'#2a1505'} lineWidth={6} /><Circle x={300} y={120} size={110} fill={'#d9b26b'} stroke={'#2a1505'} lineWidth={6} />
    <Rect y={-420} width={720} height={130} radius={20} fill={'#d62828'} stroke={'#fff'} lineWidth={8}><Txt text={'ON AIR: "ANTI-ROAD GUY"'} fontFamily={FONT} fontWeight={900} fontSize={54} fill={'#fff'} /></Rect>
  </Node>);
  // honking street
  const street = createRef<Node>(), walker = createRef<Node>();
  const honks = [...Array(5)].map(() => createRef<Txt>());
  view.add(<Node ref={street} opacity={0}>
    <Rect width={W} height={H} fill={new Gradient({type: 'linear', from: [0, -1280], to: [0, 1280], stops: [{offset: 0, color: '#9cc9ea'}, {offset: 0.5, color: '#dfeef8'}, {offset: 0.51, color: '#7a7f86'}, {offset: 1, color: '#4a4e54'}]})} />
    {[...Array(9)].map((_, i) => <Rect x={-720 + i * 180} y={-300 - (i % 3) * 120} width={160} height={900} fill={'#a9b8c8'} />)}
    <Rect y={260} width={W} height={140} fill={'#cfc9bd'} />
    {[...Array(4)].map((_, i) => <Rect x={-560 + i * 380} y={640} width={300} height={130} radius={30} fill={['#c0392b', '#2c7fb8', '#f1c40f', '#27ae60'][i]} stroke={'#111'} lineWidth={5}>
      <Rect y={-80} width={190} height={80} radius={[30, 30, 0, 0]} fill={'#9fc3d9'} stroke={'#111'} lineWidth={5} />
      <Circle x={-90} y={70} size={80} fill={'#141414'} /><Circle x={90} y={70} size={80} fill={'#141414'} /></Rect>)}
    {honks.map((h, i) => <Txt ref={h} x={-560 + i * 300} y={430 - (i % 2) * 120} rotation={(i % 2 ? 1 : -1) * 10} text={'HONK!'} fontFamily={FONT} fontWeight={900} fontSize={110} fill={'#ffd23f'} stroke={'#111'} lineWidth={12} strokeFirst scale={0} />)}
  </Node>);
  view.add(engineer(walker, -900, -40, 0.8));

  yield* all(
    (function* () {
      for (let d = 1; d <= 31; d += 3) { day().text(String(d)); yield* day().scale(1.1, 0.05).to(1, 0.05); }
      clock.t = 11 * 0.1;
      yield* waitUntil(clock, at('famous', 'newspaper') - 0.2);
      yield* all(cal().opacity(0, 0.2), paper().scale(1, 0.7, easeOutBack), paper().rotation(-4, 0.7, easeOutCubic)); clock.t += 0.7;
      yield* waitUntil(clock, at('famous', 'radio'));
      yield* all(paper().position([0, 2200], 0.4, easeInOutCubic), radio().scale(1, 0.4, easeOutBack)); clock.t += 0.4;
      yield* all(...waves.map((w, i) => (function* () { yield* waitFor(i * 0.25); yield* all(w().size(1400, 1.0), w().opacity(1, 0.1).to(0, 0.9)); })()));
      clock.t += 1.5;
      yield* waitUntil(clock, at('famous', 'honk'));
      yield* all(radio().scale(0, 0.25), street().opacity(1, 0.25)); clock.t += 0.25;
      walker().position([-900, 440]);
      yield* all(walker().x(500, D - clock.t, linear),
        ...honks.map((h, i) => (function* () { yield* waitFor(i * 0.35); yield* h().scale(1, 0.18, easeOutBack); yield* h().scale(0.9, 0.1); })()));
    })(),
  );
});
