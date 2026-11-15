import React from 'react';
import {Composition} from 'remotion';
import {P01} from './P01';
import {durationInFrames, shot} from './shot';

export const Root: React.FC = () => (
	<Composition
		id={shot.id}
		component={P01}
		fps={shot.fps}
		width={shot.resolution.width}
		height={shot.resolution.height}
		durationInFrames={durationInFrames}
	/>
);
