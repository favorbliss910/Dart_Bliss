// Remotion-drawn scenes for "Highway". Each scene receives local time via useT().
import React from 'react';
import {random} from 'remotion';
import {
  Ambulance, bt, Cam, Car, Clouds, Engineer, Glow, H, Haze, Label, pop, ramp, sceneOf, Shake, Sky, Skyline, Skyway, useT, Vignette, W,
} from './lib';

const dur = (id: string) => sceneOf(id).end - sceneOf(id).start;
const full: React.CSSProperties = {position: 'absolute', inset: 0, overflow: 'hidden'};

// a row of jammed cars on a deck (side view)
const Traffic: React.FC<{y: number; s: number; seed: string; speed?: number; jam?: boolean; t: number; gap?: number; brake?: boolean}> =
  ({y, s, seed, speed = 0, jam = true, t, gap = 40, brake = true}) => {
    const step = 380 * s + gap * s;
    const n = Math.ceil(W / step) + 2;
    const off = jam ? Math.sin(t * 0.8 + s) * 6 : (t * speed) % step;
    return <>{[...Array(n)].map((_, i) => (
      <Car key={i} x={-step + i * step + off + (random(seed + i) - 0.5) * 30 * s} y={y + (jam ? Math.sin(t * 7 + i) * 1.2 : 0)} s={s}
        seed={seed + i} brake={brake && jam && random(seed + 'b' + i) > 0.25} lights={!jam} />
    ))}</>;
  };

// ================================================================= 1. HOOK
export const Hook: React.FC = () => {
  const t = useT();
  const cut = bt('hook', 'blowup');
  if (t < cut) {
    return (
      <div style={full}>
        <Cam t={t} dur={cut} from={1.0} to={1.12} y1={-40}>
          <Sky top="#1b1440" mid="#c2456b" bottom="#ffb070" sun={{x: 1050, y: 1180, r: 90, color: '#ffcf7a'}} />
          <Clouds y={300} color="#ff9fb0" opacity={0.35} seed="hk" />
          <Skyline y={1500} color="#3a2547" seed="hk1" litRatio={0.25} window="#ffc46b" scale={0.8} />
          <Haze y={1150} h={500} color="#ff9a7a" opacity={0.45} />
          <Skyline y={1650} color="#24182f" seed="hk2" litRatio={0.4} window="#ffcf80" height={1100} />
          <Skyway y={1600} color="#5b5568" />
          <Traffic y={1590} s={0.62} seed="hka" t={t} />
          <div style={{position: 'absolute', left: 0, top: 1760, width: W, height: H, background: 'linear-gradient(#140d1d,#07040a)'}} />
          {[...Array(26)].map((_, i) => <Glow key={i} x={(i * 97 + 30) % W} y={2050 + (i % 4) * 90} r={50} color="#ff3030" opacity={0.6 + Math.sin(t * 3 + i) * 0.2} />)}
        </Cam>
        <Vignette strength={0.7} />
      </div>
    );
  }
  const lt = t - cut;
  const pulse = 0.5 + 0.5 * Math.sin(lt * 10);
  return (
    <div style={full}>
      <Cam t={lt} dur={dur('hook') - cut} from={1.15} to={1.0}>
        <div style={{...full, background: 'radial-gradient(circle at 50% 40%, #3a2d2a, #0d0a09 75%)'}} />
        {/* concrete pillar */}
        <div style={{position: 'absolute', left: 420, top: 0, width: 600, height: H, background: 'linear-gradient(90deg,#5d5b58,#b9b5ae 40%,#7d7a75 75%,#4e4c49)'}} />
        {[...Array(30)].map((_, i) => <div key={i} style={{position: 'absolute', left: 420 + random('pc' + i) * 580, top: random('pt' + i) * H, width: 6 + random('pw' + i) * 14,
          height: 4 + random('ph' + i) * 10, borderRadius: 4, background: '#00000030'}} />)}
        {/* dynamite bundle */}
        <svg width={W} height={H} style={{position: 'absolute'}}>
          <defs><linearGradient id="dyn" x1="0" x2="1"><stop offset="0" stopColor="#7d0f0f" /><stop offset=".45" stopColor="#e23b2e" /><stop offset="1" stopColor="#6b0c0c" /></linearGradient></defs>
          {[0, 1, 2, 3, 4].map((i) => <g key={i}><rect x={470 + i * 100} y={1050} width={92} height={560} rx={20} fill="url(#dyn)" stroke="#2a0505" strokeWidth={5} />
            <rect x={478 + i * 100} y={1100} width={76} height={40} fill="#f2e6c9" opacity={0.85} /><text x={516 + i * 100} y={1129} textAnchor="middle" fontFamily="Poppins" fontWeight={900} fontSize={26} fill="#5a0a0a">TNT</text></g>)}
          {[1180, 1480].map((yy) => <rect key={yy} x={450} y={yy} width={540} height={46} fill="#2b2b2b" stroke="#111" strokeWidth={4} />)}
          <rect x={620} y={1300} width={200} height={120} rx={14} fill="#1c1c1c" stroke="#444" strokeWidth={5} />
          <text x={720} y={1378} textAnchor="middle" fontFamily="monospace" fontWeight={900} fontSize={66} fill={`rgba(255,40,40,${0.5 + pulse * 0.5})`}>00:05</text>
          <path d="M820 1340 C1000 1300 1100 1500 1250 1700" stroke="#d62828" strokeWidth={14} fill="none" />
          <path d="M820 1380 C980 1380 1050 1580 1200 1780" stroke="#2b6cd6" strokeWidth={14} fill="none" />
        </svg>
        <Glow x={720} y={1360} r={360} color="rgba(255,40,40,.6)" opacity={pulse} />
        {/* fuse sparks */}
        {[...Array(24)].map((_, i) => {
          const a = random('sa' + i) * Math.PI * 2, life = (lt * 3 + random('sl' + i)) % 1;
          return <div key={i} style={{position: 'absolute', left: 560 + Math.cos(a) * life * 160, top: 1010 + Math.sin(a) * life * 160 - life * 40,
            width: 10, height: 10, borderRadius: 5, background: '#ffd36b', opacity: 1 - life, boxShadow: '0 0 18px #ffb000'}} />;
        })}
        <Glow x={560} y={1010} r={140} color="rgba(255,200,80,.9)" opacity={0.6 + pulse * 0.4} />
      </Cam>
      <Vignette strength={0.75} />
    </div>
  );
};

// ================================================================= 2. SKYWAY BUILT
export const SkywayScene: React.FC = () => {
  const t = useT();
  const D = dur('skyway');
  const build = ramp(t, 0.1, 2.6, 0, 1);
  const sign = pop(t, bt('skyway', 'shortcut1'), 0.6);
  return (
    <div style={full}>
      <Cam t={t} dur={D} from={1.08} to={1.0} x0={40} x1={-40}>
        <Sky top="#4f9de0" mid="#a9d6f5" bottom="#e9f4fb" sun={{x: 1150, y: 420, r: 70, color: '#fff3c4'}} />
        <Clouds y={250} opacity={0.85} seed="sk" speed={12} />
        <Skyline y={1650} color="#9fb3c8" seed="sk1" litRatio={0.15} window="#dbe8f5" scale={0.75} />
        <Haze y={1300} h={500} color="#e6f1fa" opacity={0.6} />
        <Skyline y={1900} color="#5d7290" seed="sk2" litRatio={0.2} window="#c9dcef" height={1300} />
        <Skyway y={1520} build={build} deck={140} />
        {build > 0.9 && <Traffic y={1508} s={0.55} seed="ska" t={t} jam={false} speed={420} gap={260} brake={false} />}
        <div style={{position: 'absolute', left: 0, top: 2050, width: W, height: 600, background: 'linear-gradient(#59606a,#33383f)'}} />
        <Label x={720} y={1300} text="6 LANES" t={t} at={bt('skyway', 'sixlanes')} bg="#1d3557" />
        {/* highway sign */}
        <div style={{position: 'absolute', left: 260, top: 560, width: 920, height: 360, transform: `translateY(${(1 - sign) * -1500}px) rotate(${(1 - sign) * 6}deg)`,
          background: 'linear-gradient(#1f8a4c,#136b39)', border: '10px solid #f4f4f4', borderRadius: 26, boxShadow: '0 30px 60px rgba(0,0,0,.4)',
          fontFamily: 'Poppins', color: '#fff', textAlign: 'center'}}>
          <div style={{fontSize: 70, fontWeight: 800, marginTop: 40, letterSpacing: 6}}>SKYWAY ➜</div>
          <div style={{fontSize: 110, fontWeight: 900, lineHeight: 1.1}}>DOWNTOWN</div>
          <div style={{fontSize: 64, fontWeight: 700, opacity: 0.9}}>5 MIN</div>
        </div>
      </Cam>
      <Vignette strength={0.35} />
    </div>
  );
};

// ================================================================= 3. TRAFFIC JAM
export const Jam: React.FC = () => {
  const t = useT();
  const D = dur('jam');
  const amb = bt('jam', 'ambulance'), pz = bt('jam', 'pizza'), mar = bt('jam', 'marriage');
  const clockMin = Math.min(45, ramp(t, 0.2, 2.2, 5, 45));
  return (
    <div style={full}>
      <Cam t={t} dur={D} from={1.0} to={1.15} y1={-60}>
        <Sky top="#e9a35a" mid="#f3cf8e" bottom="#f8e6c2" sun={{x: 300, y: 600, r: 80, color: '#fff0b0'}} />
        <Skyline y={1300} color="#c09a78" seed="jm1" litRatio={0.05} scale={0.8} />
        <Haze y={900} h={700} color="#f2d3a0" opacity={0.7} />
        <div style={{position: 'absolute', left: 0, top: 1250, width: W, height: H, background: 'linear-gradient(#6d6f73,#4a4c50)'}} />
        {[1420, 1700, 2000].map((yy) => <div key={yy} style={{position: 'absolute', left: 0, top: yy + 20, width: W, height: 10,
          background: 'repeating-linear-gradient(90deg,#f2f2f2 0 90px,transparent 90px 170px)'}} />)}
        <Traffic y={1430} s={0.75} seed="j1" t={t} />
        <Traffic y={1720} s={0.9} seed="j2" t={t} />
        {t > amb && <Ambulance x={ramp(t, amb, amb + 0.8, W, 520)} y={1715} s={0.95} t={t} />}
        <Traffic y={2050} s={1.08} seed="j3" t={t} />
        {/* heat haze shimmer */}
        <div style={{position: 'absolute', left: 0, top: 1200, width: W, height: 300, background: 'linear-gradient(transparent, rgba(255,230,180,.25), transparent)',
          transform: `skewX(${Math.sin(t * 3) * 2}deg)`}} />
      </Cam>
      {/* clock overlay */}
      {t < amb && (
        <div style={{position: 'absolute', left: 720, top: 640, transform: `translate(-50%,-50%) scale(${pop(t, 0.1)})`, textAlign: 'center',
          background: 'rgba(15,15,20,.86)', borderRadius: 40, padding: '40px 70px', border: '6px solid #fff', fontFamily: 'Poppins', color: '#fff'}}>
          <div style={{fontSize: 70, fontWeight: 700, opacity: 0.85}}>5 MILES</div>
          <div style={{fontSize: 200, fontWeight: 900, color: clockMin > 30 ? '#ff4d4d' : '#fff', lineHeight: 1}}>{Math.round(clockMin)} MIN</div>
        </div>
      )}
      {/* pizza card */}
      {t > pz && t < mar && (
        <div style={{position: 'absolute', left: 720, top: 760, transform: `translate(-50%,-50%) scale(${pop(t, pz)}) rotate(-4deg)`}}>
          <svg width={760} height={620} viewBox="0 0 760 620">
            <path d="M60 220 L700 220 L660 560 L100 560Z" fill="#c8955a" stroke="#6b4a2a" strokeWidth={8} />
            <path d="M60 220 L380 60 L700 220Z" fill="#dcae73" stroke="#6b4a2a" strokeWidth={8} />
            <circle cx={380} cy={390} r={140} fill="#f0c25e" stroke="#b5652a" strokeWidth={14} />
            {[[330, 350], [430, 360], [380, 440], [320, 430], [450, 430]].map(([x, y], i) => <circle key={i} cx={x} cy={y} r={22} fill="#b8322a" />)}
            <rect x={60} y={200} width={640} height={380} fill="#bfe6ff" opacity={0.35} />
            <text x={380} y={610} textAnchor="middle" fontFamily="Poppins" fontWeight={900} fontSize={70} fill="#9ad8ff" stroke="#123" strokeWidth={6} paintOrder="stroke">COLD</text>
          </svg>
          {[...Array(14)].map((_, i) => <div key={i} style={{position: 'absolute', left: random('sn' + i) * 760, top: ((t - pz) * 120 + random('sy' + i) * 600) % 620,
            color: '#e9f8ff', fontSize: 40, textShadow: '0 0 8px #9cf'}}>❄</div>)}
        </div>
      )}
      {/* marriage */}
      {t > mar && (
        <div style={{position: 'absolute', left: 720, top: 760, transform: `translate(-50%,-50%) scale(${pop(t, mar)})`, textAlign: 'center'}}>
          <svg width={600} height={520} viewBox="0 0 600 520">
            <defs><linearGradient id="hrt" x1="0" x2="1"><stop offset="0" stopColor="#ff5c7a" /><stop offset="1" stopColor="#c8193c" /></linearGradient></defs>
            <g transform={`translate(${-Math.min(40, (t - mar) * 120)} ${Math.min(30, (t - mar) * 60)}) rotate(${-Math.min(14, (t - mar) * 40)} 300 260)`}>
              <path d="M300 470 L90 260 Q20 160 110 90 Q210 30 300 140 L270 230 L320 300 L280 380Z" fill="url(#hrt)" stroke="#5a0a1a" strokeWidth={8} /></g>
            <g transform={`translate(${Math.min(40, (t - mar) * 120)} ${Math.min(30, (t - mar) * 60)}) rotate(${Math.min(14, (t - mar) * 40)} 300 260)`}>
              <path d="M300 470 L510 260 Q580 160 490 90 Q390 30 300 140 L270 230 L320 300 L280 380Z" fill="url(#hrt)" stroke="#5a0a1a" strokeWidth={8} /></g>
          </svg>
          <div style={{fontFamily: 'Poppins', fontWeight: 900, fontSize: 80, color: '#fff', WebkitTextStroke: '10px #111', paintOrder: 'stroke fill'}}>LEFT LANE</div>
        </div>
      )}
      <Vignette strength={0.45} />
    </div>
  );
};

// ================================================================= 4. ENGINEER ON THE BRIDGE
export const EngineerScene: React.FC = () => {
  const t = useT();
  const D = dur('engineer');
  const sitAt = bt('engineer', 'bridge'), swAt = bt('engineer', 'stopwatch');
  const x = ramp(t, 0.2, sitAt - 0.3, -200, 720);
  const pose = t < sitAt ? 'stand' : t < swAt ? 'sit' : Math.floor((t - swAt) / 1.4) % 2 === 0 ? 'stopwatch' : 'notebook';
  return (
    <div style={full}>
      <Cam t={t} dur={D} from={1.05} to={1.18} y1={60}>
        <Sky top="#2a3d6b" mid="#f08a5d" bottom="#ffd59a" sun={{x: 380, y: 1300, r: 110, color: '#ffd27a'}} />
        <Clouds y={500} color="#ffc1a1" opacity={0.45} seed="en" />
        <Skyline y={1500} color="#5a4e6e" seed="en1" litRatio={0.18} window="#ffd28c" scale={0.7} />
        <Haze y={1200} h={500} color="#ffb98a" opacity={0.55} />
        {/* skyway below, seen from the bridge */}
        <div style={{position: 'absolute', left: 0, top: 1700, width: W, height: H, background: 'linear-gradient(#5d6068,#3c3f45)'}} />
        <Traffic y={1880} s={0.6} seed="en2" t={t} />
        <Traffic y={2150} s={0.72} seed="en3" t={t} />
        <Traffic y={2450} s={0.86} seed="en4" t={t} />
        {/* pedestrian bridge */}
        <div style={{position: 'absolute', left: 0, top: 1490, width: W, height: 120, background: 'linear-gradient(#9aa0a8,#5b6068)', boxShadow: '0 30px 40px rgba(0,0,0,.45)'}} />
        <svg width={W} height={400} style={{position: 'absolute', top: 1180}}>
          <rect x={0} y={300} width={W} height={14} fill="#3e434a" />
          <rect x={0} y={170} width={W} height={12} fill="#3e434a" />
          {[...Array(20)].map((_, i) => <line key={i} x1={i * 80} y1={182} x2={i * 80 + 80} y2={300} stroke="#3e434a" strokeWidth={8} />)}
          {[...Array(20)].map((_, i) => <rect key={'p' + i} x={i * 80} y={170} width={8} height={140} fill="#3e434a" />)}
        </svg>
        <Engineer x={x} y={pose === 'stand' ? 1500 : 1560} s={0.95} walk={t < sitAt - 0.3} pose={pose as any} />
      </Cam>
      <Glow x={380} y={1300} r={500} color="rgba(255,190,110,.35)" />
      <Vignette strength={0.45} />
    </div>
  );
};

// ================================================================= 9. CITY DOUBLES DOWN -> BASEMENT
const Crane: React.FC<{x: number; y: number; t: number; seed: string}> = ({x, y, t, seed}) => {
  const swing = Math.sin(t * 0.7 + random(seed) * 6) * 18;
  return (
    <svg width={900} height={1500} style={{position: 'absolute', left: x - 450, top: y - 1400, overflow: 'visible'}}>
      <g stroke="#e3a312" strokeWidth={10} fill="none">
        <rect x={420} y={250} width={60} height={1150} fill="#f2b31a" />
        {[...Array(18)].map((_, i) => <line key={i} x1={420} y1={260 + i * 64} x2={480} y2={292 + i * 64} stroke="#9a6a05" strokeWidth={6} />)}
      </g>
      <g transform={`rotate(${swing} 450 260)`}>
        <rect x={60} y={230} width={820} height={44} fill="#f2b31a" stroke="#9a6a05" strokeWidth={6} />
        <rect x={420} y={180} width={90} height={60} fill="#e8e8e8" stroke="#555" strokeWidth={5} />
        <line x1={140} y1={274} x2={140} y2={620} stroke="#333" strokeWidth={5} />
        <rect x={90} y={620} width={100} height={60} fill="#7c8590" stroke="#333" strokeWidth={4} />
        <rect x={760} y={274} width={100} height={110} fill="#8d8d8d" />
      </g>
    </svg>
  );
};

export const Doubles: React.FC = () => {
  const t = useT();
  const cut = bt('doubles', 'basement');
  if (t < cut) {
    return (
      <div style={full}>
        <Cam t={t} dur={cut} from={1.0} to={1.1}>
          <Sky top="#7aa6c9" mid="#c8d9e3" bottom="#e7ddc9" />
          <Clouds y={300} opacity={0.6} seed="db" />
          <Skyline y={1600} color="#8fa0b2" seed="db1" litRatio={0.1} scale={0.8} />
          <Haze y={1250} h={500} color="#e2d6c0" opacity={0.6} />
          <Crane x={400} y={1700} t={t} seed="c1" />
          <Crane x={1150} y={1650} t={t} seed="c2" />
          <Skyway y={1560} deck={200} color="#b9a990" />
          <Traffic y={1548} s={0.55} seed="db2" t={t} />
          <div style={{position: 'absolute', left: 0, top: 2100, width: W, height: 600, background: 'linear-gradient(#8a7a63,#5b4f40)'}} />
          {[...Array(7)].map((_, i) => {
            const at = bt('doubles', 'cranes') + i * 0.18;
            return t > at && <div key={i} style={{position: 'absolute', left: 80 + i * 195, top: 2180 + (i % 2) * 120, transform: `scale(${pop(t, at)})`,
              background: '#ff7b00', border: '6px solid #111', borderRadius: 14, padding: '10px 18px', fontFamily: 'Poppins', fontWeight: 900, fontSize: 40, color: '#111'}}>
              DETOUR {i % 2 ? '⬅' : '➡'}</div>;
          })}
          {[...Array(16)].map((_, i) => <div key={i} style={{position: 'absolute', left: (i * 113 + t * 40) % W, top: 1980 + random('du' + i) * 140, width: 160, height: 90,
            borderRadius: '50%', background: 'rgba(200,180,150,.35)', filter: 'blur(14px)'}} />)}
        </Cam>
        <Label x={720} y={1150} text="8 LANES" t={t} at={bt('doubles', 'widen')} bg="#e76f51" size={110} />
        <Vignette strength={0.4} />
      </div>
    );
  }
  const lt = t - cut;
  const boxAt = bt('doubles', 'box') - cut, wonAt = bt('doubles', 'skywaywon') - cut;
  const flick = (Math.floor(lt * 14) % 9 === 0 || Math.floor(lt * 5) % 13 === 0) ? 0.55 : 1;
  const boxY = lt < boxAt ? -600 : Math.min(1745, -600 + (lt - boxAt) ** 2 * 9000);
  const landed = lt > boxAt + 0.27;
  return (
    <div style={full}>
      <Shake t={lt} at={boxAt + 0.27} amp={20}>
        <Cam t={lt} dur={dur('doubles') - cut} from={1.1} to={1.0}>
          <div style={{...full, background: 'linear-gradient(#55595c,#3c3f42 70%,#2b2d2f)'}} />
          {[...Array(40)].map((_, i) => <div key={i} style={{position: 'absolute', left: (i % 8) * 190 - 20, top: Math.floor(i / 8) * 260 + 80, width: 180, height: 250,
            border: '3px solid rgba(0,0,0,.18)', background: random('bw' + i) > 0.85 ? 'rgba(0,0,0,.08)' : 'transparent'}} />)}
          {/* pipes */}
          <div style={{position: 'absolute', left: 0, top: 120, width: W, height: 50, background: 'linear-gradient(#8a8f94,#4d5155)'}} />
          {/* fluorescent tube */}
          <div style={{position: 'absolute', left: 420, top: 240, width: 600, height: 30, borderRadius: 15, background: `rgba(235,255,240,${flick})`, boxShadow: `0 0 120px rgba(220,255,230,${flick * 0.8})`}} />
          <div style={{...full, background: `radial-gradient(ellipse at 50% 10%, rgba(220,255,230,${0.22 * flick}), transparent 60%)`}} />
          <div style={{position: 'absolute', left: 0, top: 1900, width: W, height: 700, background: 'linear-gradient(#3a3532,#22201e)'}} />
          {/* copier */}
          <div style={{position: 'absolute', left: 980, top: 1380, width: 380, height: 560, borderRadius: 18, background: 'linear-gradient(90deg,#c9c6bd,#efece4 50%,#b7b3aa)', border: '5px solid #333'}}>
            <div style={{margin: 30, height: 70, background: '#2f3336', borderRadius: 8, color: '#ff4b4b', fontFamily: 'monospace', fontSize: 40, fontWeight: 900, padding: 12}}>ERR 47</div>
            <div style={{margin: '0 30px', height: 26, background: '#555', borderRadius: 6}} />
            <div style={{position: 'absolute', left: -60, top: 160, width: 140, height: 90, background: '#fff', transform: `rotate(${-20 + Math.sin(lt * 4) * 4}deg)`, border: '2px solid #aaa'}} />
          </div>
          {[...Array(8)].map((_, i) => {
            const life = (lt * 0.6 + i / 8) % 1;
            return <div key={i} style={{position: 'absolute', left: 1140 + Math.sin(life * 6 + i) * 40, top: 1360 - life * 520, width: 120 + life * 140, height: 120 + life * 140,
              borderRadius: '50%', background: 'rgba(90,90,90,.35)', opacity: 1 - life, filter: 'blur(12px)'}} />;
          })}
          {/* desk */}
          <Engineer x={520} y={1990} s={1.05} pose={landed ? 'sad' : 'sit'} look={landed ? 1 : 0} />
          <div style={{position: 'absolute', left: 120, top: 1690, width: 820, height: 50, background: 'linear-gradient(#8a6a4a,#5e4530)', borderRadius: 8, boxShadow: '0 20px 30px rgba(0,0,0,.5)'}} />
          <div style={{position: 'absolute', left: 150, top: 1740, width: 40, height: 300, background: '#4a3626'}} /><div style={{position: 'absolute', left: 870, top: 1740, width: 40, height: 300, background: '#4a3626'}} />
          {/* cardboard box */}
          <div style={{position: 'absolute', left: 560, top: boxY - 300, width: 340, height: 300, transform: `rotate(${landed ? -3 : 8}deg)`}}>
            <div style={{width: '100%', height: '100%', background: 'linear-gradient(90deg,#b98a52,#d9a96b 50%,#a8794a)', border: '5px solid #5e4024', borderRadius: 6}}>
              <div style={{position: 'absolute', left: 0, right: 0, top: 120, height: 40, background: '#c9a06b', borderTop: '3px dashed #5e4024', borderBottom: '3px dashed #5e4024'}} />
              <div style={{position: 'absolute', left: 30, top: 190, fontFamily: 'Poppins', fontWeight: 800, fontSize: 34, color: '#5e4024'}}>PERSONAL ITEMS</div>
            </div>
          </div>
        </Cam>
      </Shake>
      {lt > wonAt && (
        <div style={{position: 'absolute', left: 720, top: 700, transform: `translate(-50%,-50%) scale(${pop(lt, wonAt)}) rotate(-5deg)`, width: 1100,
          background: '#f3efe3', padding: '40px 50px', boxShadow: '0 30px 60px rgba(0,0,0,.6)', fontFamily: 'Georgia, serif', color: '#111', textAlign: 'center'}}>
          <div style={{fontSize: 46, borderBottom: '4px solid #111', paddingBottom: 10, letterSpacing: 8}}>THE DAILY COMMUTER</div>
          <div style={{fontSize: 140, fontWeight: 900, lineHeight: 1.05, marginTop: 20}}>THE SKYWAY WON</div>
        </div>
      )}
      <Vignette strength={0.7} />
    </div>
  );
};

// ================================================================= 10. WATER MAIN BURST
export const Burst: React.FC = () => {
  const t = useT();
  const D = dur('burst');
  const wm = bt('burst', 'watermain'), sd = bt('burst', 'shutdown'), c160 = bt('burst', 'cars160'), ns = bt('burst', 'noshortcut'), br = bt('burst', 'braces');
  const water = ramp(t, wm, wm + 0.6, 0, 1);
  const dark = ramp(t, br, br + 1.5, 0, 1);
  const count = Math.round(ramp(t, c160, c160 + 1.6, 0, 160000));
  return (
    <div style={full}>
      <Shake t={t} at={wm} dur={1.2} amp={30}>
        <Cam t={t} dur={D} from={1.0} to={1.12}>
          <Sky top="#5a8fc4" mid="#a7c7e0" bottom="#dfe9f0" />
          <div style={{...full, background: '#101522', opacity: dark * 0.65}} />
          <Clouds y={200} color={dark > 0.3 ? '#4a4f5c' : '#fff'} opacity={0.5 + dark * 0.4} seed="bs" speed={30} />
          <Skyline y={1600} color="#7f93a8" seed="bs1" litRatio={0.1} scale={0.8} />
          <Haze y={1250} h={500} color="#dfe9f0" opacity={0.5 - dark * 0.3} />
          <Skyway y={1500} deck={150} />
          {t < sd && <Traffic y={1488} s={0.55} seed="bs2" t={t} />}
          <div style={{position: 'absolute', left: 0, top: 2000, width: W, height: 600, background: 'linear-gradient(#6b6f75,#3f4247)'}} />
          {/* crack + geyser */}
          {t > wm && <svg width={W} height={H} style={{position: 'absolute'}}>
            <path d="M560 2000 L620 2080 L590 2160 L660 2260 L640 2400 M620 2080 L700 2120 M590 2160 L520 2230" stroke="#1a1a1a" strokeWidth={10} fill="none" />
          </svg>}
          {t > wm && [...Array(70)].map((_, i) => {
            const life = ((t - wm) * 1.6 + random('w' + i)) % 1;
            const spread = (random('ws' + i) - 0.5) * 300 * life;
            const hgt = water * (900 + random('wh' + i) * 600);
            return <div key={i} style={{position: 'absolute', left: 620 + spread, top: 2050 - Math.sin(life * Math.PI) * hgt, width: 40 + random('wz' + i) * 50,
              height: 40 + random('wz' + i) * 50, borderRadius: '50%', background: 'rgba(170,220,255,.75)', boxShadow: '0 0 20px rgba(200,240,255,.6)'}} />;
          })}
          {t > wm && <div style={{position: 'absolute', left: 520, top: 2050 - water * 1300, width: 200, height: water * 1300, background: 'linear-gradient(rgba(220,245,255,.2), rgba(170,220,255,.85))', borderRadius: 100, filter: 'blur(6px)'}} />}
          {t > wm && <div style={{position: 'absolute', left: 120, top: 1350, width: 1200, height: 900, background: 'radial-gradient(ellipse, rgba(230,245,255,.5), transparent 65%)', opacity: water}} />}
          {/* barricades */}
          {t > sd && [...Array(4)].map((_, i) => <div key={i} style={{position: 'absolute', left: 90 + i * 330, top: 1330, transform: `scale(${pop(t, sd + i * 0.12)})`,
            width: 260, height: 120, background: 'repeating-linear-gradient(45deg,#e63946 0 34px,#fff 34px 68px)', border: '6px solid #111', borderRadius: 10,
            fontFamily: 'Poppins', fontWeight: 900, fontSize: 44, color: '#111', textAlign: 'center', lineHeight: '108px'}}><span style={{background: '#fff', padding: '0 8px'}}>CLOSED</span></div>)}
        </Cam>
      </Shake>
      {t > c160 && t < ns && (
        <div style={{position: 'absolute', left: 720, top: 700, transform: `translate(-50%,-50%) scale(${pop(t, c160)})`, textAlign: 'center', fontFamily: 'Poppins', color: '#fff'}}>
          <div style={{fontSize: 230, fontWeight: 900, WebkitTextStroke: '14px #111', paintOrder: 'stroke fill', textShadow: '0 16px 0 rgba(0,0,0,.4)'}}>{count.toLocaleString('en-US')}</div>
          <div style={{fontSize: 110, fontWeight: 900, WebkitTextStroke: '10px #111', paintOrder: 'stroke fill'}}>CARS</div>
        </div>
      )}
      {t > ns && (
        <div style={{position: 'absolute', left: 720, top: 700, transform: `translate(-50%,-50%) scale(${pop(t, ns)})`}}>
          <div style={{width: 900, height: 330, background: 'linear-gradient(#1f8a4c,#136b39)', border: '10px solid #f4f4f4', borderRadius: 26, fontFamily: 'Poppins', color: '#fff',
            textAlign: 'center', fontSize: 120, fontWeight: 900, lineHeight: '310px', position: 'relative'}}>SKYWAY
            <svg width={900} height={330} style={{position: 'absolute', left: -10, top: -10}}><line x1={60} y1={40} x2={840} y2={290} stroke="#e63946" strokeWidth={40} strokeLinecap="round"
              strokeDasharray={900} strokeDashoffset={900 * (1 - ramp(t, ns + 0.2, ns + 0.5))} /></svg>
          </div>
        </div>
      )}
      {t > br && Math.floor((t - br) * 10) === 6 && <div style={{...full, background: 'rgba(255,255,255,.6)'}} />}
      <Vignette strength={0.45 + dark * 0.3} />
    </div>
  );
};

// ================================================================= 13. OUTRO: PARADOX, SEOUL, BOOM
export const Outro: React.FC = () => {
  const t = useT();
  const se = bt('outro', 'seoul'), st = bt('outro', 'stream'), fw = bt('outro', 'fastestway'), bu = bt('outro', 'blowingup');
  if (t < se) {
    return (
      <div style={{...full, background: 'radial-gradient(circle at 50% 40%, #1d3b6b, #070b16 75%)'}}>
        <svg width={W} height={H} style={{position: 'absolute', opacity: 0.35}}>
          {[...Array(14)].map((_, i) => <line key={i} x1={random('ox' + i) * W} y1={random('oy' + i) * H} x2={random('ox2' + i) * W} y2={random('oy2' + i) * H} stroke="#7fd9ff" strokeWidth={4} />)}
        </svg>
        <div style={{position: 'absolute', left: 720, top: 1000, transform: `translate(-50%,-50%) scale(${pop(t, 0.1, 0.5)})`, textAlign: 'center', fontFamily: 'Poppins', color: '#fff'}}>
          <div style={{fontSize: 80, fontWeight: 700, letterSpacing: 10, opacity: 0.85}}>IT'S CALLED</div>
          <div style={{fontSize: 190, fontWeight: 900, lineHeight: 1, textShadow: '0 0 60px #4fc3ff'}}>BRAESS'S</div>
          <div style={{fontSize: 190, fontWeight: 900, lineHeight: 1, color: '#7fd9ff', textShadow: '0 0 60px #4fc3ff'}}>PARADOX</div>
        </div>
        <Vignette strength={0.6} />
      </div>
    );
  }
  if (t < fw) {
    const wipe = ramp(t, se + 0.6, se + 2.2, 0, 1);
    return (
      <div style={full}>
        <Cam t={t - se} dur={fw - se} from={1.0} to={1.08}>
          <Sky top="#6aa8e0" mid="#bcdcf2" bottom="#eef6fb" />
          <Skyline y={1500} color="#8aa0b6" seed="se1" litRatio={0.15} scale={0.85} />
          <Haze y={1150} h={500} color="#eef6fb" opacity={0.6} />
          <Skyline y={1700} color="#61768f" seed="se2" litRatio={0.2} height={1100} />
          {/* after: stream park */}
          <div style={{position: 'absolute', left: 0, top: 1650, width: W, height: H, background: 'linear-gradient(#5f9e4f,#3f7a37)'}} />
          <div style={{position: 'absolute', left: 0, top: 1950, width: W, height: 360, background: 'linear-gradient(#5fb7e6,#2f86c2)',
            boxShadow: 'inset 0 20px 30px rgba(0,0,0,.25)'}} />
          {[...Array(30)].map((_, i) => <div key={i} style={{position: 'absolute', left: ((i * 97 + (t - se) * 140) % (W + 200)) - 100, top: 1990 + (i % 6) * 52, width: 90, height: 8,
            borderRadius: 4, background: 'rgba(255,255,255,.6)'}} />)}
          {[...Array(9)].map((_, i) => <div key={'t' + i} style={{position: 'absolute', left: i * 170 - 20, top: 1560 + (i % 2) * 40}}>
            <div style={{position: 'absolute', left: 60, top: 160, width: 26, height: 200, background: '#6b4a3a'}} />
            <div style={{width: 180, height: 200, borderRadius: '50%', background: 'radial-gradient(circle at 40% 35%, #8fd16a, #3f8a34)'}} /></div>)}
          {/* before: highway, wiped away */}
          <div style={{position: 'absolute', left: 0, top: 0, width: W * (1 - wipe), height: H, overflow: 'hidden'}}>
            <div style={{position: 'absolute', inset: 0, width: W}}>
              <Sky top="#8c97a3" mid="#b9c0c8" bottom="#d9dde1" />
              <Skyline y={1500} color="#7d8794" seed="se1" litRatio={0.1} scale={0.85} />
              <Skyline y={1700} color="#5a636e" seed="se2" litRatio={0.1} height={1100} />
              <Skyway y={1700} deck={170} />
              <Traffic y={1688} s={0.6} seed="se3" t={t} />
              <div style={{position: 'absolute', left: 0, top: 2100, width: W, height: 600, background: '#4e5359'}} />
            </div>
          </div>
          <div style={{position: 'absolute', left: W * (1 - wipe) - 8, top: 0, width: 16, height: H, background: '#fff', opacity: wipe > 0 && wipe < 1 ? 1 : 0, boxShadow: '0 0 40px #fff'}} />
        </Cam>
        <Label x={720} y={700} text="SEOUL" t={t} at={se + 0.2} bg="#1d3557" size={110} rot={0} />
        {t > st && [...Array(5)].map((_, i) => <div key={i} style={{position: 'absolute', left: ((t - st) * 900 + i * 300) % (W + 400) - 300, top: 1050 + i * 70, width: 260, height: 26,
          borderRadius: 13, background: 'linear-gradient(90deg, transparent, #4ade80)', opacity: 0.85}} />)}
        <Label x={720} y={1250} text="FASTER ✓" t={t} at={st + 1.0} bg="#2a9d55" size={96} rot={2} />
        <Vignette strength={0.35} />
      </div>
    );
  }
  const lt = t - fw, boom = bu - fw;
  const flash = ramp(lt, boom, boom + 0.15, 0, 1) * (1 - ramp(lt, boom + 0.3, boom + 1.6, 0, 1));
  return (
    <div style={full}>
      <Shake t={lt} at={boom} dur={1.2} amp={40}>
        <Cam t={lt} dur={dur('outro') - fw} from={1.15} to={1.0}>
          <Sky top="#1b1440" mid="#c2456b" bottom="#ffb070" sun={{x: 1050, y: 1180, r: 90, color: '#ffcf7a'}} />
          <Skyline y={1500} color="#3a2547" seed="hk1" litRatio={0.25} window="#ffc46b" scale={0.8} />
          <Skyline y={1650} color="#24182f" seed="hk2" litRatio={0.4} window="#ffcf80" height={1100} />
          {lt < boom + 0.2 && <Skyway y={1600} color="#5b5568" />}
          {lt > boom && [...Array(40)].map((_, i) => {
            const a = random('d' + i) * Math.PI * 2, v = 600 + random('dv' + i) * 1400, tt = lt - boom;
            return <div key={i} style={{position: 'absolute', left: 720 + Math.cos(a) * v * tt, top: 1650 + Math.sin(a) * v * tt + 900 * tt * tt, width: 30 + random('dz' + i) * 60,
              height: 20 + random('dz' + i) * 40, background: '#6b6570', transform: `rotate(${tt * 600 * random('dr' + i)}deg)`}} />;
          })}
          {lt > boom && <Glow x={720} y={1650} r={1400 * ramp(lt, boom, boom + 0.5)} color="rgba(255,150,40,.9)" opacity={1 - ramp(lt, boom + 0.5, boom + 2)} />}
          <div style={{position: 'absolute', left: 0, top: 1760, width: W, height: H, background: 'linear-gradient(#140d1d,#07040a)'}} />
        </Cam>
      </Shake>
      <div style={{...full, background: '#fff6e0', opacity: flash}} />
    </div>
  );
};

export const REMOTION_SCENES: Record<string, React.FC> = {
  hook: Hook, skyway: SkywayScene, jam: Jam, engineer: EngineerScene, doubles: Doubles, burst: Burst, outro: Outro,
};
