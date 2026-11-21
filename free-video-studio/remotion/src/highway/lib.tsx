// Shared, detailed 2D drawings for the "Highway" film (1440x2560 canvas).
import React from 'react';
import {Easing, interpolate, random, useCurrentFrame, useVideoConfig} from 'remotion';
import tl from '../../../projects/highway/timeline.json';

export const W = 1440, H = 2560;
export const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
export const ease = Easing.bezier(0.45, 0, 0.2, 1);
export const beats = tl.beats as Record<string, number>;
export const sceneOf = (id: string) => tl.scenes.find((s) => s.id === id)!;

/** seconds since scene start */
export const useT = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  return f / fps;
};
/** local time of a named beat inside a scene */
export const bt = (scene: string, beat: string) => beats[beat] - sceneOf(scene).start;
export const ramp = (t: number, a: number, b: number, from = 0, to = 1, e = ease) =>
  interpolate(t, [a, b], [from, to], {...clamp, easing: e});
export const pop = (t: number, at: number, dur = 0.35) => {
  if (t < at) return 0;
  const x = (t - at) / dur;
  return 1 - Math.exp(-6 * x) * Math.cos(10 * x);
};

// ---------------------------------------------------------------- sky & atmosphere
export const Sky: React.FC<{top: string; mid: string; bottom: string; sun?: {x: number; y: number; r: number; color: string}}> =
  ({top, mid, bottom, sun}) => (
    <svg width={W} height={H} style={{position: 'absolute'}}>
      <defs>
        <linearGradient id="sky" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0" stopColor={top} /><stop offset=".55" stopColor={mid} /><stop offset="1" stopColor={bottom} />
        </linearGradient>
        {sun && <radialGradient id="sun"><stop offset="0" stopColor="#fff" /><stop offset=".25" stopColor={sun.color} />
          <stop offset="1" stopColor={sun.color} stopOpacity="0" /></radialGradient>}
      </defs>
      <rect width={W} height={H} fill="url(#sky)" />
      {sun && <circle cx={sun.x} cy={sun.y} r={sun.r * 4} fill="url(#sun)" opacity={0.9} />}
    </svg>
  );

export const Clouds: React.FC<{y: number; color?: string; opacity?: number; speed?: number; seed?: string}> =
  ({y, color = '#fff', opacity = 0.7, speed = 6, seed = 'c'}) => {
    const t = useT();
    return (
      <svg width={W} height={H} style={{position: 'absolute', filter: 'blur(6px)'}}>
        {[...Array(6)].map((_, i) => {
          const x = ((random(seed + i) * 1800 + t * speed * (1 + i * 0.2)) % 2000) - 300;
          const yy = y + random(seed + 'y' + i) * 300;
          const s = 0.6 + random(seed + 's' + i) * 0.8;
          return (
            <g key={i} transform={`translate(${x} ${yy}) scale(${s})`} opacity={opacity}>
              <ellipse cx={0} cy={0} rx={190} ry={60} fill={color} />
              <ellipse cx={-80} cy={-30} rx={100} ry={70} fill={color} />
              <ellipse cx={60} cy={-50} rx={120} ry={85} fill={color} />
            </g>
          );
        })}
      </svg>
    );
  };

// procedural skyline with lit windows and atmospheric perspective
export const Skyline: React.FC<{y: number; color: string; window?: string; seed: string; height?: number; litRatio?: number; scale?: number; count?: number}> =
  ({y, color, window = '#ffd98a', seed, height = 900, litRatio = 0.35, scale = 1, count = 14}) => {
    let x = -60;
    const items: React.ReactNode[] = [];
    for (let i = 0; i < count && x < W + 100; i++) {
      const w = (110 + random(seed + 'w' + i) * 170) * scale;
      const h = (height * (0.35 + random(seed + 'h' + i) * 0.65)) * scale;
      const top = y - h;
      const cols = Math.max(2, Math.floor(w / 34)), rows = Math.floor(h / 46);
      items.push(
        <g key={i}>
          <rect x={x} y={top} width={w} height={h + 400} fill={color} />
          <rect x={x + w * 0.72} y={top} width={w * 0.28} height={h + 400} fill="#000" opacity={0.12} />
          {random(seed + 'ant' + i) > 0.6 && <rect x={x + w / 2 - 3} y={top - 70 * scale} width={6} height={70 * scale} fill={color} />}
          {[...Array(rows * cols)].map((_, k) => {
            const r = Math.floor(k / cols), c = k % cols;
            if (random(seed + i + '-' + k) > litRatio) return null;
            return <rect key={k} x={x + 12 + c * ((w - 24) / cols)} y={top + 24 + r * 46} width={(w - 24) / cols - 10} height={22}
              fill={window} opacity={0.55 + random(seed + 'o' + k) * 0.45} />;
          })}
        </g>,
      );
      x += w + 8 * scale;
    }
    return <svg width={W} height={H} style={{position: 'absolute', overflow: 'visible'}}>{items}</svg>;
  };

export const Haze: React.FC<{y: number; h: number; color: string; opacity?: number}> = ({y, h, color, opacity = 0.6}) => (
  <div style={{position: 'absolute', left: 0, top: y, width: W, height: h, opacity,
    background: `linear-gradient(transparent, ${color} 60%, transparent)`}} />
);

export const Vignette: React.FC<{strength?: number}> = ({strength = 0.55}) => (
  <div style={{position: 'absolute', inset: 0, background: `radial-gradient(ellipse at 50% 45%, transparent 45%, rgba(0,0,0,${strength}) 100%)`}} />
);

export const Glow: React.FC<{x: number; y: number; r: number; color: string; opacity?: number}> = ({x, y, r, color, opacity = 1}) => (
  <div style={{position: 'absolute', left: x - r, top: y - r, width: r * 2, height: r * 2, borderRadius: '50%', opacity,
    background: `radial-gradient(circle, ${color} 0%, transparent 70%)`, mixBlendMode: 'screen'}} />
);

// ---------------------------------------------------------------- vehicles (side view)
const CAR_COLORS = ['#c0392b', '#2c7fb8', '#e8e8e8', '#2d2d2d', '#f1c40f', '#27ae60', '#8e44ad', '#d35400', '#7f8c8d', '#1abc9c'];
export const Car: React.FC<{x: number; y: number; s?: number; color?: string; seed?: string; lights?: boolean; brake?: boolean; flip?: boolean; type?: 'sedan' | 'suv' | 'van'}> =
  ({x, y, s = 1, color, seed = 'car', lights = false, brake = false, flip = false, type}) => {
    const c = color ?? CAR_COLORS[Math.floor(random(seed) * CAR_COLORS.length)];
    const kind = type ?? (['sedan', 'suv', 'van'] as const)[Math.floor(random(seed + 'k') * 3)];
    const roof = kind === 'sedan' ? 'M70 60 Q95 18 150 14 L215 14 Q255 18 280 60 Z' : kind === 'suv' ? 'M60 62 L80 10 L270 10 Q290 14 300 62 Z' : 'M40 62 L52 0 L300 0 L318 62 Z';
    const gid = 'cg' + seed.replace(/\W/g, '');
    return (
      <svg width={380 * s} height={170 * s} viewBox="0 0 380 170"
        style={{position: 'absolute', left: x, top: y - 160 * s, transform: flip ? 'scaleX(-1)' : undefined, overflow: 'visible'}}>
        <defs>
          <linearGradient id={gid} x1="0" x2="0" y1="0" y2="1">
            <stop offset="0" stopColor="#fff" stopOpacity=".55" /><stop offset=".25" stopColor={c} /><stop offset=".8" stopColor={c} />
            <stop offset="1" stopColor="#000" stopOpacity=".55" />
          </linearGradient>
          <linearGradient id={gid + 'w'} x1="0" x2="1"><stop offset="0" stopColor="#9fc3d9" /><stop offset=".5" stopColor="#e9f5ff" /><stop offset="1" stopColor="#6f93ab" /></linearGradient>
        </defs>
        <ellipse cx={190} cy={150} rx={175} ry={12} fill="#000" opacity={0.35} />
        <path d={roof} fill={`url(#${gid})`} stroke="#111" strokeWidth={3} />
        <path d={kind === 'van' ? 'M60 56 L66 10 L170 10 L170 56Z M180 56 L180 10 L290 10 L300 56Z' : kind === 'suv' ? 'M84 56 L98 20 L180 20 L180 56Z M190 56 L190 20 L262 20 L284 56Z' : 'M88 56 Q104 26 150 22 L172 22 L172 56Z M182 56 L182 22 L212 22 Q244 26 264 56Z'}
          fill={`url(#${gid}w)`} stroke="#222" strokeWidth={2} />
        <path d="M12 70 Q14 56 60 56 L320 56 Q366 60 372 86 L374 118 Q374 132 360 132 L20 132 Q6 132 8 116 Z" fill={`url(#${gid})`} stroke="#111" strokeWidth={3} />
        <rect x={20} y={92} width={340} height={4} fill="#000" opacity={0.25} />
        <rect x={150} y={78} width={22} height={5} rx={2} fill="#222" /><rect x={250} y={78} width={22} height={5} rx={2} fill="#222" />
        {[90, 290].map((wx) => (
          <g key={wx}>
            <circle cx={wx} cy={132} r={30} fill="#141414" /><circle cx={wx} cy={132} r={17} fill="#9aa3ab" />
            <circle cx={wx} cy={132} r={6} fill="#555" />
          </g>
        ))}
        <rect x={358} y={74} width={16} height={16} rx={4} fill={lights ? '#fff7cc' : '#e9e2c5'} />
        <rect x={6} y={74} width={14} height={18} rx={4} fill={brake ? '#ff2a2a' : '#a01818'} />
        {brake && <circle cx={10} cy={83} r={34} fill="#ff2020" opacity={0.35} style={{filter: 'blur(8px)'}} />}
        {lights && <path d="M374 82 L560 40 L560 130 Z" fill="#fff7cc" opacity={0.18} />}
      </svg>
    );
  };

export const Ambulance: React.FC<{x: number; y: number; s?: number; t: number}> = ({x, y, s = 1, t}) => {
  const on = Math.floor(t * 6) % 2 === 0;
  return (
    <div style={{position: 'absolute', left: x, top: y - 230 * s}}>
      <svg width={460 * s} height={240 * s} viewBox="0 0 460 240" style={{overflow: 'visible'}}>
        <defs><linearGradient id="amb" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stopColor="#fff" /><stop offset=".85" stopColor="#e3e6ea" /><stop offset="1" stopColor="#9aa1a8" /></linearGradient></defs>
        <ellipse cx={230} cy={226} rx={220} ry={12} fill="#000" opacity={0.35} />
        <rect x={10} y={30} width={300} height={170} rx={14} fill="url(#amb)" stroke="#222" strokeWidth={3} />
        <path d="M310 80 L390 80 Q420 84 440 130 L446 200 L310 200 Z" fill="url(#amb)" stroke="#222" strokeWidth={3} />
        <path d="M322 92 L384 92 Q404 96 418 132 L322 132 Z" fill="#9fc3d9" stroke="#222" strokeWidth={2} />
        <rect x={10} y={120} width={436} height={18} fill="#d62828" />
        <rect x={120} y={60} width={60} height={20} fill="#d62828" /><rect x={140} y={40} width={20} height={60} fill="#d62828" />
        <text x={160} y={175} textAnchor="middle" fontFamily="Poppins" fontWeight={800} fontSize={30} fill="#d62828">AMBULANCE</text>
        {[90, 370].map((wx) => <g key={wx}><circle cx={wx} cy={200} r={30} fill="#141414" /><circle cx={wx} cy={200} r={16} fill="#9aa3ab" /></g>)}
        <rect x={40} y={14} width={50} height={18} rx={4} fill={on ? '#ff2b2b' : '#5a0f0f'} />
        <rect x={230} y={14} width={50} height={18} rx={4} fill={on ? '#3b2bff' : '#151057'} />
      </svg>
      <div style={{position: 'absolute', left: (on ? 65 : 255) * s - 160, top: 23 * s - 160, width: 320, height: 320, borderRadius: '50%',
        background: `radial-gradient(circle, ${on ? 'rgba(255,40,40,.75)' : 'rgba(60,60,255,.75)'}, transparent 70%)`, mixBlendMode: 'screen'}} />
    </div>
  );
};

// ---------------------------------------------------------------- elevated highway (side view)
export const Skyway: React.FC<{y: number; deck?: number; build?: number; lanesLabel?: string; color?: string; pillarEvery?: number}> =
  ({y, deck = 120, build = 1, color = '#a7adb5', pillarEvery = 300}) => (
    <svg width={W} height={H} style={{position: 'absolute', overflow: 'visible'}}>
      <defs>
        <linearGradient id="deck" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stopColor="#d9dde2" /><stop offset=".3" stopColor={color} /><stop offset="1" stopColor="#5b6168" /></linearGradient>
        <linearGradient id="pillar" x1="0" x2="1"><stop offset="0" stopColor="#7a8088" /><stop offset=".4" stopColor="#c5cad0" /><stop offset="1" stopColor="#6a7077" /></linearGradient>
      </defs>
      {[...Array(Math.ceil(W / pillarEvery) + 1)].map((_, i) => {
        const px = 80 + i * pillarEvery;
        const ph = (H - y) * Math.min(1, Math.max(0, build * 1.6 - i * 0.12));
        return <g key={i}>
          <rect x={px} y={H - ph} width={90} height={ph} fill="url(#pillar)" />
          <rect x={px - 20} y={y + deck - 10} width={130} height={40} fill="#6a7077" opacity={ph > 0 ? 1 : 0} />
        </g>;
      })}
      <rect x={0} y={y} width={W * Math.min(1, Math.max(0, build * 1.3 - 0.3))} height={deck} fill="url(#deck)" />
      <rect x={0} y={y - 26} width={W * Math.min(1, Math.max(0, build * 1.3 - 0.3))} height={26} fill="#c9ced4" />
      {[...Array(48)].map((_, i) => i * 32 < W * Math.min(1, build * 1.3 - 0.3) && <rect key={i} x={i * 32} y={y - 26} width={4} height={26} fill="#8b9198" />)}
      <rect x={0} y={y + deck} width={W * Math.min(1, Math.max(0, build * 1.3 - 0.3))} height={14} fill="#000" opacity={0.3} />
    </svg>
  );

// ---------------------------------------------------------------- the engineer (semi-realistic 2D)
export const Engineer: React.FC<{x: number; y: number; s?: number; walk?: boolean; pose?: 'stand' | 'stopwatch' | 'notebook' | 'smile' | 'sit' | 'sad'; look?: number}> =
  ({x, y, s = 1, walk = false, pose = 'stand', look = 0}) => {
    const t = useT();
    const st = walk ? Math.sin(t * 9) : 0;
    const bob = walk ? -Math.abs(st) * 8 : Math.sin(t * 2) * 2;
    const blink = (t * 60) % 230 < 6;
    const sit = pose === 'sit';
    const armR = pose === 'stopwatch' ? -115 : pose === 'notebook' ? -60 : st * 18;
    const armL = pose === 'notebook' ? -40 : -st * 18;
    return (
      <svg width={320 * s} height={760 * s} viewBox="0 0 320 760"
        style={{position: 'absolute', left: x - 160 * s, top: y - 760 * s + bob * s, overflow: 'visible'}}>
        <defs>
          <linearGradient id="skin" x1="0" x2="1"><stop offset="0" stopColor="#f2c9a5" /><stop offset="1" stopColor="#d9a47f" /></linearGradient>
          <linearGradient id="vest" x1="0" x2="1"><stop offset="0" stopColor="#ff8a1f" /><stop offset="1" stopColor="#e0650a" /></linearGradient>
          <linearGradient id="pants" x1="0" x2="1"><stop offset="0" stopColor="#3a4250" /><stop offset="1" stopColor="#262c36" /></linearGradient>
        </defs>
        <ellipse cx={160} cy={752} rx={110} ry={12} fill="#000" opacity={sit ? 0 : 0.3} />
        {/* legs */}
        {sit ? (
          <g>
            <path d="M118 470 L118 520 L250 520 L250 470 Z" fill="url(#pants)" />
            <path d="M230 500 L250 690 L218 690 L200 520 Z" fill="url(#pants)" /><path d="M150 500 L170 690 L138 690 L120 520 Z" fill="url(#pants)" />
            <path d="M210 688 L262 688 Q270 700 262 708 L210 708Z M130 688 L182 688 Q190 700 182 708 L130 708Z" fill="#1d1d1d" />
          </g>
        ) : (
          <g>
            <g transform={`rotate(${st * 16} 140 470)`}><path d="M118 470 L162 470 L156 720 L124 720 Z" fill="url(#pants)" /><path d="M116 716 L168 716 Q180 730 170 742 L116 742Z" fill="#1d1d1d" /></g>
            <g transform={`rotate(${-st * 16} 180 470)`}><path d="M158 470 L202 470 L196 720 L164 720 Z" fill="url(#pants)" /><path d="M156 716 L208 716 Q220 730 210 742 L156 742Z" fill="#1d1d1d" /></g>
          </g>
        )}
        {/* torso */}
        <path d="M98 250 Q160 228 222 250 L232 480 L88 480 Z" fill="#f4f6f8" stroke="#2a2a2a" strokeWidth={3} />
        <path d="M98 250 L140 250 L150 480 L88 480 Z M222 250 L180 250 L170 480 L232 480 Z" fill="url(#vest)" stroke="#2a2a2a" strokeWidth={3} />
        <rect x={92} y={380} width={56} height={14} fill="#e8f0f2" opacity={0.9} /><rect x={172} y={380} width={56} height={14} fill="#e8f0f2" opacity={0.9} />
        <path d="M150 252 L160 300 L170 252" fill="#2b4c7e" />
        <rect x={186} y={290} width={26} height={34} rx={3} fill="#fff" stroke="#999" strokeWidth={2} />
        {/* arms */}
        <g transform={`rotate(${armL} 100 270)`}>
          <path d="M84 262 Q98 254 112 264 L104 420 L80 420 Z" fill="#f4f6f8" stroke="#2a2a2a" strokeWidth={3} />
          <circle cx={92} cy={430} r={18} fill="url(#skin)" />
          {pose === 'notebook' && <g transform="translate(60 400) rotate(20)"><rect width={90} height={110} rx={6} fill="#f6e7b0" stroke="#3a3a3a" strokeWidth={3} />
            {[0, 1, 2, 3, 4].map((k) => <rect key={k} x={12} y={20 + k * 18} width={66 - (k % 2) * 20} height={4} fill="#6b6b6b" />)}</g>}
        </g>
        <g transform={`rotate(${armR} 220 270)`}>
          <path d="M208 264 Q222 254 236 262 L240 420 L216 420 Z" fill="#f4f6f8" stroke="#2a2a2a" strokeWidth={3} />
          <circle cx={228} cy={430} r={18} fill="url(#skin)" />
          {pose === 'stopwatch' && <g transform="translate(228 470)"><circle r={38} fill="#d9dee3" stroke="#333" strokeWidth={5} /><circle r={30} fill="#fff" />
            <rect x={-8} y={-52} width={16} height={14} fill="#888" /><line x1={0} y1={0} x2={Math.sin(t * 6) * 24} y2={-Math.cos(t * 6) * 24} stroke="#d62828" strokeWidth={4} /></g>}
        </g>
        {/* head */}
        <rect x={142} y={196} width={36} height={40} fill="url(#skin)" />
        <g transform={`translate(${look * 6} 0)`}>
          <ellipse cx={160} cy={150} rx={64} ry={74} fill="url(#skin)" stroke="#5a3b2a" strokeWidth={2} />
          <ellipse cx={98} cy={156} rx={10} ry={18} fill="#d9a47f" /><ellipse cx={222} cy={156} rx={10} ry={18} fill="#d9a47f" />
          <path d="M96 128 Q100 66 162 64 Q222 66 226 126 Q214 96 186 92 Q150 104 118 98 Q102 108 96 128Z" fill="#3b2a20" />
          <g stroke="#222" strokeWidth={4} fill="rgba(200,230,255,.25)">
            <rect x={112} y={136} width={40} height={30} rx={8} /><rect x={168} y={136} width={40} height={30} rx={8} />
            <line x1={152} y1={150} x2={168} y2={150} />
          </g>
          {blink ? <g stroke="#2a1a10" strokeWidth={4}><line x1={122} y1={152} x2={142} y2={152} /><line x1={178} y1={152} x2={198} y2={152} /></g>
            : <g fill="#2a1a10"><circle cx={133 + look * 3} cy={151} r={6} /><circle cx={189 + look * 3} cy={151} r={6} /></g>}
          <path d="M116 126 Q132 118 148 124 M172 124 Q188 118 204 126" stroke="#3b2a20" strokeWidth={5} fill="none" strokeLinecap="round" />
          <path d="M158 160 Q154 178 162 182" stroke="#b7835f" strokeWidth={3} fill="none" />
          {pose === 'smile' ? <path d="M136 192 Q160 212 184 192" stroke="#6b2b1f" strokeWidth={5} fill="#fff" strokeLinecap="round" />
            : pose === 'sad' ? <path d="M140 202 Q160 190 180 202" stroke="#6b2b1f" strokeWidth={5} fill="none" strokeLinecap="round" />
            : <path d="M142 196 Q160 202 178 196" stroke="#6b2b1f" strokeWidth={5} fill="none" strokeLinecap="round" />}
        </g>
      </svg>
    );
  };

// ---------------------------------------------------------------- UI overlays
export const Label: React.FC<{x: number; y: number; text: string; t: number; at: number; size?: number; color?: string; bg?: string; rot?: number}> =
  ({x, y, text, t, at, size = 84, color = '#fff', bg = '#d62828', rot = -3}) => {
    const p = pop(t, at);
    if (t < at) return null;
    return (
      <div style={{position: 'absolute', left: x, top: y, transform: `translate(-50%,-50%) rotate(${rot}deg) scale(${p})`,
        padding: '14px 34px', background: bg, color, fontFamily: 'Poppins', fontWeight: 900, fontSize: size, borderRadius: 18,
        boxShadow: '0 14px 0 rgba(0,0,0,.35)', whiteSpace: 'nowrap', border: '6px solid #111'}}>{text}</div>
    );
  };

export const Shake: React.FC<{t: number; at: number; dur?: number; amp?: number; children: React.ReactNode}> = ({t, at, dur = 0.5, amp = 24, children}) => {
  const k = t > at && t < at + dur ? (1 - (t - at) / dur) * amp : 0;
  const dx = Math.sin(t * 90) * k, dy = Math.cos(t * 77) * k;
  return <div style={{position: 'absolute', inset: 0, transform: `translate(${dx}px, ${dy}px)`}}>{children}</div>;
};

export const Cam: React.FC<{t: number; dur: number; from?: number; to?: number; x0?: number; x1?: number; y0?: number; y1?: number; children: React.ReactNode}> =
  ({t, dur, from = 1, to = 1.1, x0 = 0, x1 = 0, y0 = 0, y1 = 0, children}) => {
    const p = ramp(t, 0, dur, 0, 1);
    const s = from + (to - from) * p;
    return <div style={{position: 'absolute', inset: 0, transform: `translate(${x0 + (x1 - x0) * p}px, ${y0 + (y1 - y0) * p}px) scale(${s})`}}>{children}</div>;
  };
