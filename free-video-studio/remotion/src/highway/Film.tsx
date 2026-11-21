// "Highway" master composition: Remotion scenes + parts rendered by Revideo / Motion Canvas / Manim.
import React from 'react';
import {AbsoluteFill, interpolate, OffthreadVideo, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig, getStaticFiles} from 'remotion';
import tl from '../../../projects/highway/timeline.json';
import {REMOTION_SCENES} from './scenes';

const KEY = /^(skyway|shortcut|45|15|160,000|ambulances?|dynamite|faster|paradox|braess's|seoul|never|weird|same|fewer|tear|nobody's)/i;

const Captions: React.FC = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = f / fps;
  const words = tl.words as {w: string; t: number; e: number}[];
  let i = -1;
  for (let k = 0; k < words.length; k++) { if (words[k].t <= t) i = k; else break; }
  if (i < 0 || t > words[i].e + 0.6) return null;
  const w = words[i];
  const p = spring({frame: f - Math.round(w.t * fps), fps, config: {damping: 11, stiffness: 300, mass: 0.6}});
  const hot = KEY.test(w.w.replace(/[^\w',]/g, ''));
  return (
    <AbsoluteFill style={{alignItems: 'center', top: 1660}}>
      <div style={{fontFamily: 'Poppins', fontWeight: 900, fontSize: 132, color: hot ? '#ffd23f' : '#fff', WebkitTextStroke: '20px #0b0b0b',
        paintOrder: 'stroke fill', textShadow: '0 12px 0 rgba(0,0,0,.45)', transform: `scale(${0.75 + 0.25 * p}) translateY(${(1 - p) * 30}px)`,
        letterSpacing: 1}}>{w.w}</div>
    </AbsoluteFill>
  );
};

const Transition: React.FC<{children: React.ReactNode}> = ({children}) => {
  const f = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const z = interpolate(f, [0, 12], [1.12, 1], {extrapolateRight: 'clamp'});
  const o = interpolate(f, [0, 6], [0, 1], {extrapolateRight: 'clamp'}) * interpolate(f, [durationInFrames - 5, durationInFrames], [1, 0.6], {extrapolateLeft: 'clamp'});
  const blur = interpolate(f, [0, 10], [14, 0], {extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o, transform: `scale(${z})`, filter: blur > 0.3 ? `blur(${blur}px)` : undefined}}>{children}</AbsoluteFill>;
};

const Placeholder: React.FC<{id: string; engine: string}> = ({id, engine}) => (
  <AbsoluteFill style={{background: '#222', color: '#fff', fontFamily: 'Poppins', fontSize: 80, alignItems: 'center', justifyContent: 'center'}}>{id} ({engine})</AbsoluteFill>
);

const Grain: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{mixBlendMode: 'overlay', opacity: 0.16, pointerEvents: 'none'}}>
      <svg width="100%" height="100%"><filter id="gr"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={f % 12} /></filter>
        <rect width="100%" height="100%" filter="url(#gr)" /></svg>
    </AbsoluteFill>
  );
};

export const Film: React.FC<{only?: string}> = ({only}) => {
  const {fps} = useVideoConfig();
  const files = new Set(getStaticFiles().map((s) => s.name));
  return (
    <AbsoluteFill style={{background: '#000'}}>
      {tl.scenes.map((s) => {
        if (only && s.id !== only) return null;
        const from = Math.round(s.start * fps), d = Math.round((s.end - s.start) * fps);
        const C = REMOTION_SCENES[s.id];
        const file = `highway/${s.id}.mp4`;
        return (
          <Sequence key={s.id} from={from} durationInFrames={d} name={`${s.id} · ${s.engine}`}>
            <Transition>
              {C ? <C /> : files.has(file) ? <OffthreadVideo src={staticFile(file)} muted /> : <Placeholder id={s.id} engine={s.engine} />}
            </Transition>
          </Sequence>
        );
      })}
      <Grain />
      <Captions />
    </AbsoluteFill>
  );
};
