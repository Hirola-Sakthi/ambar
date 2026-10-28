"""Render 1,400 source-derived 1080p frames with motion interpolation.

Video filtering removes the fixed corner mark before interpolation. The two
shots are processed independently so optical flow never bridges the hard cut.
This is a video remaster, not 1,400 independently AI-generated photographs.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FFMPEG = ROOT / '.tools/python/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
OUT = ROOT / 'public/scenes/hair-oil-hq'
WORK = ROOT / '.tools/hair-oil-hq'
COUNT = 1400


def render_shot(source, start, duration, first, count, native_count):
    # Match first/last source samples in each shot, preserving both endpoints.
    rate = f'{(count-1)*24}/{native_count-1}'
    filters = (
        'delogo=x=1129:y=568:w=64:h=65,'
        'tpad=stop_mode=clone:stop_duration=0.15,'
        f'minterpolate=fps={rate}:mi_mode=mci:mc_mode=aobmc:'
        'me_mode=bilat:me=epzs:mb_size=16:search_param=24:vsbmc=1,'
        f'trim=end_frame={count},'
        'scale=1920:1080:flags=lanczos,unsharp=5:5:0.3:5:5:0'
    )
    command = [str(FFMPEG), '-y', '-hide_banner', '-loglevel', 'warning',
               '-ss', str(start), '-t', str(duration), '-i', str(source),
               '-an', '-vf', filters, '-fps_mode', 'passthrough',
               '-frames:v', str(count), '-c:v', 'libwebp', '-quality', '95',
               '-compression_level', '4', '-start_number', str(first),
               '-progress', str(WORK / f'shot-{first}.progress'),
               str(OUT / 'frame_%04d.webp')]
    with (WORK / f'shot-{first}.log').open('w') as log:
        subprocess.run(command, stderr=log, stdout=log, check=True)
    print(f'Completed shot: {first}..{first+count-1}', flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', default=r'C:\Users\balaa\Downloads\gemini_generated_video_a0926e99.mp4')
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=2) as pool:
        jobs = [pool.submit(render_shot, args.source, 0, 3.375, 1, 473, 81),
                pool.submit(render_shot, args.source, 3.375, 6.625, 474, 927, 159)]
        for job in jobs:
            job.result()
    frames = sorted(OUT.glob('frame_*.webp'))
    assert len(frames) == COUNT, f'Expected {COUNT}, found {len(frames)}'
    assert all(path.name == f'frame_{i+1:04d}.webp' for i, path in enumerate(frames))
    shutil.copyfile(frames[0], ROOT / 'public/scenes/hair-oil-poster-hq.webp')
    # Only switch the live manifest after the entire new sequence exists.
    phases = [('ingredients', 0, 313), ('bowl-pour', 314, 472),
              ('bottle-fill', 473, 771), ('packaging', 772, 947),
              ('hero', 948, 1399)]
    manifest = dict(frameCount=COUNT, width=1920, height=1080,
                    directory='scenes/hair-oil-hq', revision='hair-oil-hq-v2',
                    sourceFrameCount=240, sourceFps=24,
                    processing='shot-separated motion interpolation, corner-mark removal, Lanczos upscale',
                    phases=[dict(name=n, start=s, end=e) for n,s,e in phases])
    (ROOT / 'src/sequenceManifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Ready: {len(frames)} frames, {sum(p.stat().st_size for p in frames)/1024**2:.1f} MiB', flush=True)


if __name__ == '__main__':
    main()
