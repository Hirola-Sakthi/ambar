"""Import every source frame as lossless WebP and verify decoded RGB fidelity.

No resizing, frame-rate conversion, image generation, sharpening or retouching.
The active sequence manifest is changed only after every image passes audit.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.tools/python'))
import imageio_ffmpeg
from PIL import Image, ImageDraw

OUT = ROOT / 'public/scenes/herbal-oil-advertisement'
REVIEW = ROOT / 'analysis/herbal-oil-advertisement'
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path(
        r'C:\Users\balaa\Downloads\Herbal_oil_bottle_advertisement_3860f7b0_1080p_gwr_video_mvp.mp4'))
    parser.add_argument('--resume', action='store_true', help='Reuse verified existing frame files; all RGB pixels are still audited against the video')
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    reader = imageio_ffmpeg.read_frames(str(source))
    metadata = next(reader)
    reader.close()
    width, height = metadata['source_size']
    fps = metadata['fps']
    OUT.mkdir(parents=True, exist_ok=True)
    REVIEW.mkdir(parents=True, exist_ok=True)
    print(f'Extracting every native frame at {width}x{height}, {fps:g} fps as lossless WebP.', flush=True)
    completed = 0
    if args.resume:
        for path in sorted(OUT.glob('frame_*.webp')):
            if path.name != f'frame_{completed + 1:04d}.webp':
                break
            try:
                with Image.open(path) as image:
                    image.load()
                    assert image.size == (width, height)
            except (OSError, AssertionError):
                break
            completed += 1
    filters = f'select=gte(n\\,{completed}),format=rgb24' if completed else 'format=rgb24'
    # Explicit RGB conversion is also used by the independent source audit.
    # BGRA is libwebp's lossless input format; its alpha channel stays opaque.
    with (REVIEW / 'extraction.log').open('w') as log:
        subprocess.run([FFMPEG, '-y', '-hide_banner', '-i', str(source),
            '-map', '0:v:0', '-an', '-vf', filters,
            '-fps_mode', 'passthrough', '-c:v', 'libwebp', '-lossless', '1',
            '-compression_level', '0', '-pix_fmt', 'bgra', '-start_number', str(completed + 1),
            str(OUT / 'frame_%04d.webp')], stdout=log, stderr=log, check=True)
    with (REVIEW / 'audit.log').open('w') as log:
        subprocess.run([FFMPEG, '-y', '-hide_banner', '-i', str(source),
            '-map', '0:v:0', '-an', '-vf', 'format=rgb24',
            '-fps_mode', 'passthrough', '-c:v', 'rawvideo', '-pix_fmt', 'rgb24',
            '-f', 'framemd5', str(REVIEW / 'source-rgb.framemd5')],
            stdout=log, stderr=log, check=True)
    lines = (REVIEW / 'source-rgb.framemd5').read_text().splitlines()
    timebase = next(line.split(':', 1)[1].strip() for line in lines if line.startswith('#tb 0:'))
    numerator, denominator = map(int, timebase.split('/'))
    expected = []
    for line in lines:
        if not line.strip() or line.startswith('#'):
            continue
        stream, dts, pts, duration, size, checksum = [part.strip() for part in line.split(',')]
        assert int(stream) == 0
        expected.append({'pts': int(pts), 'duration': int(duration),
                         'time_seconds': int(pts) * numerator / denominator,
                         'rgbMd5': checksum})
    assert expected, 'No video frames decoded'
    frames = sorted(OUT.glob('frame_*.webp'))
    assert len(frames) == len(expected), (len(frames), len(expected))

    def inspect(item):
        index, path = item
        assert path.name == f'frame_{index + 1:04d}.webp'
        with Image.open(path) as image:
            image.load()
            assert image.size == (width, height), (path, image.size)
            checksum = hashlib.md5(image.convert('RGB').tobytes()).hexdigest()
        assert checksum == expected[index]['rgbMd5'], f'RGB pixels differ: {path.name}'
        return {'frame': index + 1, 'file': path.name,
                'time_seconds': expected[index]['time_seconds'],
                'bytes': path.stat().st_size, 'rgbMd5': checksum,
                'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

    with ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(inspect, enumerate(frames)))
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    duration_seconds = (expected[-1]['pts'] + expected[-1]['duration'] - expected[0]['pts']) * numerator / denominator
    audit = {'source': source.name, 'sourceSha256': source_hash,
             'frameCount': len(frames), 'width': width, 'height': height,
             'fps': fps, 'timebase': timebase, 'durationSeconds': duration_seconds,
             'encoding': 'lossless WebP', 'allRgbHashesMatchSource': True,
             'frames': records}
    (REVIEW / 'manifest.json').write_text(json.dumps(audit, indent=2) + '\n', encoding='utf-8')
    with (REVIEW / 'frames.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)
    for start in range(0, len(frames), 24):
        subset = frames[start:start + 24]
        sheet = Image.new('RGB', (1280, ((len(subset) + 3) // 4) * 204), '#17251c')
        draw = ImageDraw.Draw(sheet)
        for offset, path in enumerate(subset):
            x, y = offset % 4 * 320, offset // 4 * 204
            with Image.open(path) as image:
                sheet.paste(image.resize((320, 180)), (x, y))
            draw.text((x + 8, y + 184), f'{start + offset + 1:04d} / {records[start + offset]["time_seconds"]:.3f}s', fill='white')
        sheet.save(REVIEW / f'sheet_{start // 24 + 1:02d}.jpg', quality=94)
    shutil.copyfile(frames[0], OUT / 'poster.webp')
    shutil.copyfile(frames[-1], OUT / 'product.webp')
    # This video's actions: bowl, ingredients, pour, bottle/label, cap, hero.
    phases = [('empty-bowl', 0, round(fps) - 1),
              ('ingredients', round(fps), round(3 * fps) - 1),
              ('bowl-pour', round(3 * fps), round(4.5 * fps) - 1),
              ('bottle-fill-and-label', round(4.5 * fps), round(7 * fps) - 1),
              ('cap', round(7 * fps), round(8.5 * fps) - 1),
              ('hero', round(8.5 * fps), len(frames) - 1)]
    assert phases[-1][1] <= phases[-1][2]
    active = {'frameCount': len(frames), 'width': width, 'height': height,
              'directory': 'scenes/herbal-oil-advertisement',
              'revision': f'herbal-native-{source_hash[:12]}',
              'fps': fps, 'durationSeconds': duration_seconds, 'source': source.name,
              'processing': 'Every native frame; lossless WebP; all exported RGB hashes match source decode; no retouching or resizing',
              'phases': [{'name': name, 'start': first, 'end': last} for name, first, last in phases]}
    (ROOT / 'src/sequenceManifest.json').write_text(json.dumps(active, indent=2) + '\n', encoding='utf-8')
    index_path = ROOT / 'index.html'
    html = index_path.read_text(encoding='utf-8')
    html = re.sub(r'<link rel="preload" as="image" href="[^"]+" fetchpriority="high" />',
                  f'<link rel="preload" as="image" href="/{active["directory"]}/poster.webp?v={active["revision"]}" fetchpriority="high" />', html)
    index_path.write_text(html, encoding='utf-8')
    print(f'Validated and activated {len(frames)} lossless {width}x{height} frames; every RGB hash matches the video. '
          f'Total {sum(record["bytes"] for record in records) / 1024**2:.1f} MiB.', flush=True)


if __name__ == '__main__':
    main()
