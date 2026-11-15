import React from 'react';
import {Composition} from 'remotion';
import {P01} from './P01';
import {P02, P02_FRAMES} from './P02';
import {durationInFrames, shot} from './shot';

export const Root: React.FC = () => (
	<>
		<Composition
			id={shot.id}
			component={P01}
			fps={shot.fps}
			width={shot.resolution.width}
			height={shot.resolution.height}
			durationInFrames={durationInFrames}
		/>
		<Composition id="P02" component={P02} fps={24} width={1080} height={1920} durationInFrames={P02_FRAMES} />
	</>
);
