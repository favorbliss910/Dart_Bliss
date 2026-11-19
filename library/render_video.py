"""Render the library short straight to video in parallel chunks, then mux the mix.
    python3 render_video.py --ss 2.25 --size 1440x2560 --fps 30 --jobs 4 --out out/blank_library_2k.mp4
"""
import argparse, json, math, os, subprocess, sys, tempfile
from multiprocessing import Process
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def chunk(i0, i1, fps, ss, size, path):
    import numpy as np
    from PIL import Image
    import scenes, render as R
    meta = json.load(open(os.path.join(HERE, 'words.json')))
    words, total = meta['words'], meta['duration']
    R.SS = ss
    bounds = scenes.install(words, total)
    ow, oh = size
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{ow}x{oh}',
                          '-r', str(fps), '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '15',
                          '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-tune', 'animation', path], stdin=subprocess.PIPE)
    for i in range(i0, i1):
        arr = R.render_frame(i / fps, words, bounds)
        if arr.shape[1] != ow or arr.shape[0] != oh:
            arr = np.asarray(Image.fromarray(arr).resize((ow, oh), Image.LANCZOS))
        p.stdin.write(arr.tobytes())
    p.stdin.close()
    p.wait()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ss', type=float, default=2.25)
    ap.add_argument('--size', default='1440x2560')
    ap.add_argument('--fps', type=int, default=30)
    ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('--audio', default=os.path.join(HERE, 'out', 'library_mix.wav'))
    ap.add_argument('--out', default=os.path.join(HERE, 'out', 'blank_library_2k.mp4'))
    a = ap.parse_args()
    total = json.load(open(os.path.join(HERE, 'words.json')))['duration']
    n = int(math.ceil(total * a.fps))
    size = tuple(map(int, a.size.split('x')))
    tmp = tempfile.mkdtemp(dir=os.path.join(HERE, 'out'))
    per = math.ceil(n / a.jobs)
    parts, procs = [], []
    for j in range(a.jobs):
        i0, i1 = j * per, min(n, (j + 1) * per)
        path = os.path.join(tmp, f'part{j}.mp4')
        parts.append(path)
        pr = Process(target=chunk, args=(i0, i1, a.fps, a.ss, size, path))
        pr.start()
        procs.append(pr)
    for pr in procs:
        pr.join()
    lst = os.path.join(tmp, 'list.txt')
    open(lst, 'w').write(''.join(f"file '{p}'\n" for p in parts))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-i', a.audio,
                    '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000',
                    '-movflags', '+faststart', '-shortest', a.out], check=True)
    for p in parts:
        os.remove(p)
    os.remove(lst)
    os.rmdir(tmp)
    print('->', a.out)


if __name__ == '__main__':
    main()
