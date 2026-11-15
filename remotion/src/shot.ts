// Typed view of manifests/p01_shot.json (schema: manifests/shot_schema.json).
// Remotion must match Blender's fps/size exactly; it never adds fake depth (no 2D zooms/parallax).
import raw from '../../manifests/p01_shot.json';

export type Caption = {text: string; start_s: number; end_s: number; timing_source: string};
export type Shot = {
	id: string;
	frame_in: number;
	frame_out: number;
	fps: number;
	resolution: {width: number; height: number};
	media: {frame_count: number; frame_pattern: string; audio_mix: string};
	captions: Caption[];
};

export const shot = raw as unknown as Shot;
export const durationInFrames = shot.frame_out - shot.frame_in + 1;
