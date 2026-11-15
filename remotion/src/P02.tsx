// P02 "Be Seen": multi-shot assembly. Blender owns every pixel of depth; Remotion only sequences shots,
// holds rendered frames (animation on twos), draws measured captions and plays the mix.
import React from 'react';
import {AbsoluteFill, Audio, Img, interpolate, Sequence, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import timing from '../../manifests/p02_audio_timing.json';
import render from '../../manifests/P02_render.json';

type Phrase = {text: string; start_s: number; end_s: number};
type ShotT = {id: string; frames: number; film_start_s: number; phrases: Phrase[]};
const shots = (timing as unknown as {shots: ShotT[]}).shots;
const R = render as unknown as {step: number; caption_pos: Record<string, 'top' | 'bottom'>};
const pad = (n: number) => String(n).padStart(4, '0');
let acc = 0;
const starts = shots.map((s) => {
	const a = acc;
	acc += s.frames;
	return a;
});
export const P02_FRAMES = acc;

const Caption: React.FC<{p: Phrase; pos: 'top' | 'bottom'}> = ({p, pos}) => {
	const frame = useCurrentFrame();
	const {fps, width} = useVideoConfig();
	const t = frame / fps;
	if (t < p.start_s - 0.05 || t > p.end_s + 0.12) return null;
	const opacity = interpolate(t, [p.start_s - 0.05, p.start_s + 0.03, p.end_s, p.end_s + 0.12], [0, 1, 1, 0], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});
	const k = width / 540;
	return (
		<div
			style={{
				position: 'absolute',
				left: 24 * k,
				right: 24 * k,
				...(pos === 'top' ? {top: '15%'} : {bottom: '13%'}),
				textAlign: 'center',
				opacity,
				fontFamily: '"DejaVu Sans", "Helvetica Neue", Arial, sans-serif',
				fontWeight: 700,
				fontSize: 30 * k,
				lineHeight: 1.2,
				color: '#fff8ec',
				textShadow: `0 ${2 * k}px 0 rgba(0,0,0,0.85), 0 0 ${12 * k}px rgba(0,0,0,0.6)`,
				WebkitTextStroke: `${k}px rgba(0,0,0,0.55)`,
			}}
		>
			{p.text}
		</div>
	);
};

const ShotView: React.FC<{s: ShotT}> = ({s}) => {
	const frame = useCurrentFrame(); // 0-based inside the shot
	const i = frame + 1;
	const f = i === s.frames ? i : i - ((i - 1) % R.step);
	const pos = R.caption_pos[s.id] ?? 'top';
	return (
		<AbsoluteFill style={{backgroundColor: 'black'}}>
			<Img src={staticFile(`p02/${s.id}/frames/${pad(f)}.png`)} style={{width: '100%', height: '100%'}} />
			{s.phrases.map((p) => (
				<Caption key={p.text + p.start_s} p={p} pos={pos} />
			))}
		</AbsoluteFill>
	);
};

export const P02: React.FC = () => (
	<AbsoluteFill style={{backgroundColor: 'black'}}>
		{shots.map((s, k) => (
			<Sequence key={s.id} from={starts[k]} durationInFrames={s.frames}>
				<ShotView s={s} />
			</Sequence>
		))}
		<Audio src={staticFile('p02/mix.wav')} />
	</AbsoluteFill>
);
