// Copies Blender frames + mix into public/ and validates them against the shot manifest.
// Fails (exit 1) on: missing frames, wrong dimensions, wrong frame count, audio length drift > 1 frame.
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';

const repo = path.resolve(import.meta.dirname, '..', '..');
const shot = JSON.parse(fs.readFileSync(path.join(repo, 'manifests/p01_shot.json'), 'utf8'));
const errors = [];
const srcDir = path.join(repo, shot.media.frames_dir);
const dst = path.join(import.meta.dirname, '..', 'public', 'p01');
fs.mkdirSync(path.join(dst, 'frames'), {recursive: true});

const expected = shot.frame_out - shot.frame_in + 1;
let ok = 0;
for (let f = shot.frame_in; f <= shot.frame_out; f++) {
	const name = `${String(f).padStart(4, '0')}.png`;
	const p = path.join(srcDir, name);
	if (!fs.existsSync(p)) { errors.push(`missing frame ${name}`); continue; }
	const buf = fs.readFileSync(p);
	if (buf.toString('ascii', 1, 4) !== 'PNG') { errors.push(`${name} is not a PNG`); continue; }
	const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20);
	if (w !== shot.resolution.width || h !== shot.resolution.height) errors.push(`${name} is ${w}x${h}, expected ${shot.resolution.width}x${shot.resolution.height}`);
	if (buf.length < 20000) errors.push(`${name} is suspiciously small (${buf.length} B) - blank frame?`);
	fs.copyFileSync(p, path.join(dst, 'frames', name));
	ok++;
}
const mix = path.join(repo, shot.media.audio_mix);
let audioSeconds = null;
if (!fs.existsSync(mix)) errors.push('missing audio mix');
else {
	audioSeconds = parseFloat(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', mix]).toString());
	const videoSeconds = expected / shot.fps;
	if (Math.abs(audioSeconds - videoSeconds) > 1 / shot.fps) errors.push(`audio ${audioSeconds}s vs video ${videoSeconds}s drift > 1 frame`);
	fs.copyFileSync(mix, path.join(dst, 'mix.wav'));
}
console.log(JSON.stringify({shot: shot.id, frames_ok: ok, frames_expected: expected, audio_seconds: audioSeconds, color: shot.render.color_space_out, errors}, null, 2));
process.exit(errors.length ? 1 : 0);
