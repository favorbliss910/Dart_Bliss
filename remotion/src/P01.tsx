import React from 'react';
import {AbsoluteFill, Audio, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Caption, shot} from './shot';

const pad = (n: number) => String(n).padStart(4, '0');

const CaptionLine: React.FC<{c: Caption}> = ({c}) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const t = frame / fps;
	if (t < c.start_s - 0.05 || t > c.end_s + 0.1) return null;
	const opacity = interpolate(t, [c.start_s - 0.05, c.start_s + 0.08, c.end_s - 0.05, c.end_s + 0.1], [0, 1, 1, 0], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});
	return (
		<div
			style={{
				position: 'absolute',
				left: 24,
				right: 24,
				top: '18%',
				textAlign: 'center',
				opacity,
				fontFamily: '"DejaVu Sans", "Helvetica Neue", Arial, sans-serif',
				fontWeight: 700,
				fontSize: 30,
				lineHeight: 1.2,
				color: '#fff8ec',
				textShadow: '0 2px 0 rgba(0,0,0,0.85), 0 0 12px rgba(0,0,0,0.6)',
				WebkitTextStroke: '1px rgba(0,0,0,0.55)',
			}}
		>
			{c.text}
		</div>
	);
};

export const P01: React.FC = () => {
	const frame = useCurrentFrame();
	// Blender frame numbers start at shot.frame_in; Remotion frames start at 0.
	const src = staticFile(`p01/frames/${pad(frame + shot.frame_in)}.png`);
	return (
		<AbsoluteFill style={{backgroundColor: 'black'}}>
			<Img src={src} style={{width: '100%', height: '100%'}} />
			{shot.captions.map((c) => (
				<CaptionLine key={c.text} c={c} />
			))}
			<Audio src={staticFile('p01/mix.wav')} />
		</AbsoluteFill>
	);
};
