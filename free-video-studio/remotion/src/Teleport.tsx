// Teleport sample (reference-style remake): 4 scenes, parallax camera, word-by-word captions.
import React from 'react';
import {AbsoluteFill, Easing, interpolate, Sequence, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import script from '../../compare/script.json';

const INK = '#1d1b2e';
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const ease = Easing.bezier(0.45, 0, 0.2, 1);

// ---------- shared pieces ----------
export const Character: React.FC<{x: number; y: number; scale?: number; walk?: boolean; face?: 'happy' | 'wow' | 'confused'; flip?: boolean}> =
  ({x, y, scale = 1, walk = false, face = 'happy', flip = false}) => {
    const f = useCurrentFrame();
    const step = walk ? Math.sin(f / 3.2) : 0;
    const bob = walk ? -Math.abs(step) * 10 : Math.sin(f / 18) * 3;
    const blink = f % 75 < 4;
    return (
      <svg width={300} height={620} viewBox="0 0 300 620"
        style={{position: 'absolute', left: x - 150 * scale, top: y - 620 * scale + bob, transform: `scale(${scale}) scaleX(${flip ? -1 : 1})`, transformOrigin: 'top left', overflow: 'visible'}}>
        <ellipse cx={150} cy={612} rx={80} ry={12} fill="rgba(0,0,0,.25)" />
        <g stroke={INK} strokeWidth={9} strokeLinecap="round" fill="none">
          <line x1={128} y1={430} x2={128 - step * 26} y2={600} />
          <line x1={172} y1={430} x2={172 + step * 26} y2={600} />
          <line x1={95} y1={300} x2={70 + step * 20} y2={420} />
          <line x1={205} y1={300} x2={230 - step * 20} y2={420} />
        </g>
        <defs>
          <linearGradient id="shirt" x1="0" x2="1"><stop offset="0" stopColor="#7d4fd8" /><stop offset="1" stopColor="#5b34b0" /></linearGradient>
          <radialGradient id="head" cx=".4" cy=".35" r=".7"><stop offset="0" stopColor="#ffffff" /><stop offset="1" stopColor="#e7e4f2" /></radialGradient>
        </defs>
        <rect x={88} y={250} width={124} height={200} rx={60} fill="url(#shirt)" stroke={INK} strokeWidth={8} />
        <rect x={140} y={300} width={22} height={30} rx={4} fill="#f1e6ff" stroke={INK} strokeWidth={4} />
        <circle cx={150} cy={160} r={98} fill="url(#head)" stroke={INK} strokeWidth={8} />
        <path d="M70 120 Q100 40 160 52 Q215 60 232 118 Q190 92 150 96 Q110 96 70 120Z" fill="#3a2a2a" stroke={INK} strokeWidth={6} />
        {[118, 182].map((ex) => (
          <g key={ex}>
            <ellipse cx={ex} cy={165} rx={22} ry={blink ? 2 : face === 'wow' ? 26 : 20} fill="#fff" stroke={INK} strokeWidth={5} />
            {!blink && <circle cx={ex + (face === 'confused' ? -6 : 3)} cy={167} r={8} fill={INK} />}
          </g>
        ))}
        {face === 'happy' && <path d="M128 212 Q150 232 172 212" stroke={INK} strokeWidth={6} fill="none" strokeLinecap="round" />}
        {face === 'wow' && <ellipse cx={150} cy={220} rx={12} ry={15} fill={INK} />}
        {face === 'confused' && <path d="M130 222 Q142 214 152 222 T172 220" stroke={INK} strokeWidth={6} fill="none" strokeLinecap="round" />}
      </svg>
    );
  };

export const Booth: React.FC<{x: number; y: number; label: string; scale?: number; door?: number; glow?: number}> =
  ({x, y, label, scale = 1, door = 0, glow = 0}) => (
    <svg width={340} height={700} viewBox="0 0 340 700"
      style={{position: 'absolute', left: x - 170 * scale, top: y - 700 * scale, transform: `scale(${scale})`, transformOrigin: 'top left', overflow: 'visible'}}>
      <defs>
        <linearGradient id="glass" x1="0" x2="1">
          <stop offset="0" stopColor="#7fd3ff" stopOpacity=".55" /><stop offset=".35" stopColor="#c9f0ff" stopOpacity=".25" />
          <stop offset=".7" stopColor="#4fa8e0" stopOpacity=".45" /><stop offset="1" stopColor="#2a6fb0" stopOpacity=".6" />
        </linearGradient>
        <linearGradient id="metal" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stopColor="#dfe6ef" /><stop offset="1" stopColor="#8d99ab" /></linearGradient>
        <filter id="blur"><feGaussianBlur stdDeviation="18" /></filter>
      </defs>
      {glow > 0 && <rect x={20} y={80} width={300} height={560} rx={50} fill="#9ff0ff" opacity={glow} filter="url(#blur)" />}
      <rect x={30} y={90} width={280} height={540} rx={40} fill="url(#glass)" stroke="#2b4d73" strokeWidth={8} />
      <rect x={30} y={90 + 540 * (1 - door)} width={280} height={540 * door} rx={20} fill="#9fdcff" opacity={0.55} />
      <rect x={60} y={110} width={18} height={480} rx={9} fill="#fff" opacity={0.35} />
      <rect x={10} y={30} width={320} height={80} rx={18} fill="url(#metal)" stroke="#2b4d73" strokeWidth={7} />
      <text x={170} y={86} textAnchor="middle" fontFamily="Poppins, Arial" fontWeight={800} fontSize={40} fill="#20344f">{label}</text>
      <rect x={0} y={620} width={340} height={60} rx={14} fill="url(#metal)" stroke="#2b4d73" strokeWidth={7} />
      <rect x={130} y={638} width={80} height={22} rx={4} fill="#20344f" />
    </svg>
  );

export const Captions: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = f / fps;
  const cur = [...script.words].reverse().find((w) => t >= w.t);
  if (!cur) return null;
  const local = (t - cur.t) * fps;
  const pop = spring({frame: local, fps, config: {damping: 10, stiffness: 260}});
  return (
    <AbsoluteFill style={{alignItems: 'center', top: 1180}}>
      <div style={{fontFamily: 'Poppins, Arial Black, sans-serif', fontWeight: 800, fontSize: 92, color: '#fff',
        WebkitTextStroke: '14px #111', paintOrder: 'stroke fill', textShadow: '0 8px 0 rgba(0,0,0,.35)',
        transform: `scale(${0.7 + 0.3 * pop})`}}>{cur.w}</div>
    </AbsoluteFill>
  );
};

const Camera: React.FC<{from?: number; to?: number; panX?: number; children: React.ReactNode}> = ({from = 1, to = 1.12, panX = 0, children}) => {
  const f = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const p = interpolate(f, [0, durationInFrames], [0, 1], {...clamp, easing: ease});
  return <AbsoluteFill style={{transform: `scale(${from + (to - from) * p}) translateX(${panX * p}px)`}}>{children}</AbsoluteFill>;
};
const Par: React.FC<{d: number; children: React.ReactNode}> = ({d, children}) => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{transform: `translateX(${-f * d}px)`}}>{children}</AbsoluteFill>;
};
const FadeIn: React.FC<{children: React.ReactNode}> = ({children}) => {
  const f = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const o = Math.min(interpolate(f, [0, 6], [0, 1], clamp), interpolate(f, [durationInFrames - 4, durationInFrames], [1, 0], clamp));
  const z = interpolate(f, [0, 8], [1.08, 1], {...clamp, easing: ease});
  return <AbsoluteFill style={{opacity: o, transform: `scale(${z})`}}>{children}</AbsoluteFill>;
};

// ---------- scenes ----------
const Counter: React.FC = () => {
  const f = useCurrentFrame();
  const n = Math.floor(interpolate(f, [0, 120], [1204557000, 1204557881], {...clamp, easing: Easing.out(Easing.cubic)}));
  return (
    <Camera from={1.15} to={1}>
      <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 30%, #5a0d16, #1a0508 70%)'}} />
      {[0, 1].map((i) => <div key={i} style={{position: 'absolute', top: 0, [i ? 'right' : 'left']: 0, width: 170, height: 1920,
        background: 'repeating-linear-gradient(90deg,#7a0f1c 0 30px,#4e0912 30px 60px)'}} />)}
      <div style={{position: 'absolute', left: 190, top: 420, width: 700, height: 360, borderRadius: 24, background: '#120306',
        border: '10px solid #3a0a10', boxShadow: '0 0 80px rgba(255,40,40,.35)', textAlign: 'center', fontFamily: 'Poppins, Arial'}}>
        <div style={{color: '#ff5050', fontWeight: 800, fontSize: 48, marginTop: 40, letterSpacing: 4}}>TELEPORTS TODAY</div>
        <div style={{color: '#ff2b2b', fontFamily: 'monospace', fontWeight: 900, fontSize: 104, marginTop: 30, textShadow: '0 0 24px #ff0000'}}>
          {n.toLocaleString('en-US')}</div>
        <div style={{height: 26, margin: '34px 40px 0', background: 'repeating-linear-gradient(45deg,#ffcc00 0 22px,#111 22px 44px)'}} />
      </div>
      {[...Array(6)].map((_, i) => <Booth key={i} x={110 + i * 172} y={1500} label="" scale={0.45} glow={0.4 + 0.3 * Math.sin(f / 6 + i)} />)}
      <AbsoluteFill style={{background: 'conic-gradient(from 160deg at 50% -5%, transparent 0deg, rgba(255,240,200,.18) 20deg, transparent 40deg)'}} />
      <div style={{position: 'absolute', left: 0, top: 1500, width: 1080, height: 420, background: 'linear-gradient(#24070b,#0b0204)'}} />
    </Camera>
  );
};

const City: React.FC<{night?: boolean}> = ({night}) => {
  const f = useCurrentFrame();
  return (
    <>
      <AbsoluteFill style={{background: night ? 'linear-gradient(#2b1f5c 0%, #8a4f8f 55%, #f39a7a 75%)' : 'linear-gradient(#bfe6ff,#eaf6ff 70%)'}} />
      {night && <div style={{position: 'absolute', left: 760, top: 200, width: 90, height: 90, borderRadius: 99, boxShadow: '-22px 10px 0 0 #fff4c9'}} />}
      <Par d={0.15}>
        {[...Array(9)].map((_, i) => (
          <div key={i} style={{position: 'absolute', left: -60 + i * 150, top: 640 - (i % 3) * 120 - (i % 2) * 60, width: 130, height: 900,
            background: night ? '#3b2b63' : '#cfd9e6', opacity: 0.9}}>
            {night && [...Array(14)].map((_, k) => <div key={k} style={{position: 'absolute', left: 18 + (k % 3) * 36, top: 30 + Math.floor(k / 3) * 70,
              width: 20, height: 30, background: (k * 7 + i) % 4 ? '#ffd27a' : '#4b3a75'}} />)}
          </div>
        ))}
        {night && (
          <svg style={{position: 'absolute', left: 220, top: 180}} width={220} height={900} viewBox="0 0 220 900">
            <path d="M110 0 L40 900 M110 0 L180 900 M60 600 L160 600 M75 400 L145 400 M90 220 L130 220" stroke="#ff3b2f" strokeWidth={12} fill="none" />
            {[...Array(18)].map((_, i) => <path key={i} d={`M${110 - i * 3.9} ${i * 50} L${110 + (i + 1) * 3.9} ${(i + 1) * 50}`} stroke="#ffe" strokeWidth={4} opacity={0.5} />)}
          </svg>
        )}
      </Par>
      <Par d={0.45}>
        {(night ? [[760, 640, '#ffb7d5'], [920, 700, '#ff9fc6']] : [[40, 600, '#7cc95a'], [960, 640, '#6cbb4a']]).map(([x, y, c], i) => (
          <div key={i}>
            <div style={{position: 'absolute', left: (x as number) + 70, top: (y as number) + 200, width: 26, height: 420, background: '#6b4a3a'}} />
            {[[0, 0, 150], [-80, 90, 120], [90, 80, 130], [10, 150, 140]].map(([dx, dy, r], k) => (
              <div key={k} style={{position: 'absolute', left: (x as number) + dx - r / 2 + 80, top: (y as number) + dy - r / 2 + 60 + Math.sin(f / 20 + k) * 3,
                width: r * 1.5, height: r * 1.5, borderRadius: 999, background: c as string, boxShadow: 'inset -14px -18px 0 rgba(0,0,0,.12)'}} />
            ))}
          </div>
        ))}
        <div style={{position: 'absolute', left: 0, top: 1010, width: 3000, height: 90,
          background: night ? 'repeating-linear-gradient(90deg,#2a2140 0 10px,transparent 10px 60px)' : 'repeating-linear-gradient(90deg,#333 0 10px,transparent 10px 60px)'}} />
      </Par>
      <div style={{position: 'absolute', left: 0, top: 1100, width: 1080, height: 140, background: night ? '#6c6080' : '#d9d4cc'}} />
      <div style={{position: 'absolute', left: 0, top: 1240, width: 1080, height: 700, background: night ? '#3c3552' : '#7a7a86'}} />
      {night && [...Array(7)].map((_, i) => <div key={i} style={{position: 'absolute', left: 40 + i * 150, top: 1320, width: 90, height: 260, background: '#e8e4f0', opacity: 0.85}} />)}
    </>
  );
};

export const NewYork: React.FC = () => {
  const f = useCurrentFrame();
  const walkX = interpolate(f, [0, 60], [-120, 540], {...clamp, easing: Easing.out(Easing.quad)});
  const door = interpolate(f, [70, 85], [0, 1], clamp);
  const flash = interpolate(f, [100, 106, 125], [0, 1, 0], clamp);
  const gone = f > 106;
  return (
    <Camera from={1} to={1.18}>
      <City />
      <Booth x={540} y={1180} label="NEW YORK" glow={flash} />
      {!gone && <Character x={walkX} y={1150} scale={0.9} walk={f < 60} face={f > 85 ? 'wow' : 'happy'} />}
      <Booth x={540} y={1180} label="NEW YORK" door={door} />
      <AbsoluteFill style={{background: '#e9fbff', opacity: flash}} />
    </Camera>
  );
};

const Blueprint: React.FC = () => {
  const f = useCurrentFrame();
  const draw = interpolate(f, [10, 55], [1, 0], {...clamp, easing: ease});
  const x = spring({frame: f - 70, fps: 30, config: {damping: 8}});
  const dot = interpolate(f, [10, 55], [0, 1], clamp);
  const bx = (t: number) => 250 + 580 * t, by = (t: number) => 900 - Math.sin(Math.PI * t) * 520;
  return (
    <Camera from={1.05} to={1}>
      <AbsoluteFill style={{background: '#0d3e86', backgroundImage: 'linear-gradient(rgba(255,255,255,.08) 2px,transparent 2px),linear-gradient(90deg,rgba(255,255,255,.08) 2px,transparent 2px)', backgroundSize: '60px 60px'}} />
      <svg width={1080} height={1920} style={{position: 'absolute'}}>
        <g fill="none" stroke="#dff1ff" strokeWidth={5}>
          {[250, 830].map((cx) => <g key={cx}><rect x={cx - 110} y={900} width={220} height={420} rx={30} /><rect x={cx - 130} y={860} width={260} height={50} rx={10} /><rect x={cx - 140} y={1320} width={280} height={44} rx={10} /></g>)}
          <path d={`M250 860 Q540 -180 830 860`} strokeWidth={7} strokeDasharray={1800} strokeDashoffset={1800 * draw} stroke="#7fd9ff" />
          <path d="M360 1150 Q540 1000 720 1150" strokeDasharray="22 18" opacity={0.7} />
        </g>
        <circle cx={bx(dot)} cy={by(dot) - 40} r={16} fill="#bff4ff" opacity={dot > 0 && dot < 1 ? 1 : 0} />
        <g transform={`translate(540 1080) scale(${x})`} stroke="#ff4d4d" strokeWidth={22} strokeLinecap="round"><line x1={-60} y1={-60} x2={60} y2={60} /><line x1={60} y1={-60} x2={-60} y2={60} /></g>
        <g fontFamily="Poppins, Arial" fill="#eaf6ff" textAnchor="middle" fontWeight={800}>
          <text x={540} y={420} fontSize={64} opacity={1 - draw}>DATA ONLY</text>
          <text x={250} y={1440} fontSize={52}>NEW YORK</text><text x={830} y={1440} fontSize={52}>TOKYO</text>
          <text x={250} y={830} fontSize={26} fontWeight={600}>SCANNER</text><text x={830} y={830} fontSize={26} fontWeight={600}>PRINTER</text>
        </g>
        <rect x={140} y={1500} width={800} height={120} fill="none" stroke="#dff1ff" strokeWidth={4} />
        <text x={170} y={1572} fontFamily="Poppins, Arial" fontSize={30} fill="#dff1ff">TELEPORT MK II · HOW IT WORKS</text>
        <text x={910} y={1572} textAnchor="end" fontFamily="Poppins, Arial" fontSize={30} fill="#ff6b6b" fontWeight={800}>CLASSIFIED</text>
      </svg>
      <div style={{position: 'absolute', left: 180, top: 1130, transform: 'scale(.55)', transformOrigin: 'top left', opacity: 1 - dot}}>
        <Character x={130} y={300} face="wow" />
      </div>
      <div style={{position: 'absolute', left: 760, top: 1130, transform: 'scale(.55)', transformOrigin: 'top left', opacity: dot}}>
        <Character x={130} y={300} face="confused" />
      </div>
    </Camera>
  );
};

const Tokyo: React.FC = () => {
  const f = useCurrentFrame();
  const flash = interpolate(f, [4, 10, 28], [0, 1, 0], clamp);
  const door = interpolate(f, [30, 45], [1, 0], clamp);
  const out = interpolate(f, [45, 80], [540, 760], {...clamp, easing: Easing.out(Easing.quad)});
  const q = spring({frame: f - 82, fps: 30, config: {damping: 7}});
  return (
    <Camera from={1.12} to={1.0} panX={-30}>
      <City night />
      <Booth x={540} y={1180} label="TOKYO" glow={flash * 0.9} />
      {f > 10 && <Character x={out} y={1150} scale={0.9} walk={f > 45 && f < 80} face={f > 80 ? 'confused' : 'wow'} />}
      <Booth x={540} y={1180} label="TOKYO" door={door} />
      <div style={{position: 'absolute', left: 800, top: 520, fontSize: 150, fontWeight: 900, fontFamily: 'Poppins, Arial', color: '#fff',
        WebkitTextStroke: '10px #111', paintOrder: 'stroke fill', transform: `scale(${q})`}}>?</div>
      <AbsoluteFill style={{background: '#e9fbff', opacity: flash}} />
    </Camera>
  );
};

const SCENES: Record<string, React.FC> = {counter: Counter, newyork: NewYork, blueprint: Blueprint, tokyo: Tokyo};

export const Teleport: React.FC = () => {
  const {fps} = useVideoConfig();
  return (
    <AbsoluteFill style={{background: '#000'}}>
      {script.scenes.map((s) => {
        const C = SCENES[s.id];
        return <Sequence key={s.id} from={Math.round(s.start * fps)} durationInFrames={Math.round((s.end - s.start) * fps)}><FadeIn><C /></FadeIn></Sequence>;
      })}
      <AbsoluteFill style={{boxShadow: 'inset 0 0 220px rgba(0,0,0,.45)'}} />
      <Captions />
    </AbsoluteFill>
  );
};
