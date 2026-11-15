// Validates the P02 frames + mix against the measured timing, then links them into public/p02.
// Fails on: missing rendered frames, wrong size, near-empty PNGs, audio/video drift > 1 frame.
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';

const repo = path.resolve(import.meta.dirname, '..', '..');
const timing = JSON.parse(fs.readFileSync(path.join(repo, 'manifests/p02_audio_timing.json'), 'utf8'));
const render = JSON.parse(fs.readFileSync(path.join(repo, 'manifests/P02_render.json'), 'utf8'));
const [W, H] = render.res.split('x').map(Number);
const errors = [];
let ok = 0, total = 0;
const pub = path.join(import.meta.dirname, '..', 'public', 'p02');
fs.mkdirSync(pub, {recursive: true});
for (const s of timing.shots) {
	const dir = path.join(repo, 'renders/P02', s.id, 'frames');
	const need = [];
	for (let i = 1; i <= s.frames; i++) if (i === s.frames || (i - 1) % render.step === 0) need.push(i);
	for (const f of need) {
		total++;
		const p = path.join(dir, `${String(f).padStart(4, '0')}.png`);
		if (!fs.existsSync(p)) { errors.push(`${s.id} missing ${f}`); continue; }
		const b = fs.readFileSync(p);
		const w = b.readUInt32BE(16), h = b.readUInt32BE(20);
		if (w !== W || h !== H) errors.push(`${s.id}/${f} is ${w}x${h}`);
		if (b.length < 20000) errors.push(`${s.id}/${f} near-empty (${b.length} B)`);
		ok++;
	}
	const link = path.join(pub, s.id);
	fs.rmSync(link, {recursive: true, force: true});
	fs.symlinkSync(path.join(repo, 'renders/P02', s.id), link);
}
const mix = path.join(repo, 'assets/audio/p02/mix.wav');
const a = parseFloat(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', mix]).toString());
const v = timing.total_frames / 24;
if (Math.abs(a - v) > 1 / 24) errors.push(`audio ${a}s vs video ${v}s`);
fs.copyFileSync(mix, path.join(pub, 'mix.wav'));
console.log(JSON.stringify({frames_ok: ok, frames_needed: total, audio_s: a, video_s: v, errors: errors.slice(0, 20), n_errors: errors.length}, null, 2));
process.exit(errors.length ? 1 : 0);
