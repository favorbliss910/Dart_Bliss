// Version 5: all four engines in one video. Remotion is the assembler (transitions, vignette, captions).
import React from 'react';
import {AbsoluteFill, interpolate, OffthreadVideo, Sequence, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import script from '../../compare/script.json';
import {Captions, NewYork} from './Teleport';

// which engine draws each scene
const PARTS: Record<string, {src?: string; engine: string}> = {
  counter: {src: 'parts/motioncanvas_nocaps.mp4', engine: 'Motion Canvas'},
  newyork: {engine: 'Remotion'},
  blueprint: {src: 'parts/manim_nocaps.mp4', engine: 'Manim'},
  tokyo: {src: 'parts/revideo_nocaps.mp4', engine: 'Revideo'},
};

const Transition: React.FC<{children: React.ReactNode}> = ({children}) => {
  const f = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const o = Math.min(interpolate(f, [0, 6], [0, 1], {extrapolateRight: 'clamp'}),
    interpolate(f, [durationInFrames - 4, durationInFrames], [1, 0], {extrapolateLeft: 'clamp'}));
  const z = interpolate(f, [0, 8], [1.08, 1], {extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o, transform: `scale(${z})`}}>{children}</AbsoluteFill>;
};

export const Combined: React.FC = () => {
  const {fps} = useVideoConfig();
  return (
    <AbsoluteFill style={{background: '#000'}}>
      {script.scenes.map((s) => {
        const part = PARTS[s.id];
        const from = Math.round(s.start * fps), dur = Math.round((s.end - s.start) * fps);
        return (
          <Sequence key={s.id} from={from} durationInFrames={dur}>
            <Transition>
              {part.src ? <OffthreadVideo src={staticFile(part.src)} startFrom={from} muted /> : <NewYork />}
            </Transition>
          </Sequence>
        );
      })}
      <AbsoluteFill style={{boxShadow: 'inset 0 0 220px rgba(0,0,0,.45)'}} />
      <Captions />
    </AbsoluteFill>
  );
};
