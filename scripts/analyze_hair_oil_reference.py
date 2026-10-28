"""Build an exhaustive review of the decoded hair-oil reference frames.

Uses the workspace's existing Pillow installation; never interpolates frames.
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.tools' / 'python'))
from PIL import Image, ImageChops, ImageDraw, ImageStat

OUT = ROOT / 'analysis' / 'hair-oil-reference'
frames = sorted((OUT / 'frames').glob('frame_*.png'))
assert frames, 'Extract frames with ffmpeg first.'
(OUT / 'contacts').mkdir(exist_ok=True)
records = []
previous = None
for index, path in enumerate(frames):
    with Image.open(path) as source:
        small = source.convert('RGB').resize((160, 90))
        delta = sum(ImageStat.Stat(ImageChops.difference(small, previous)).mean) / 3 if previous else 0
        records.append(dict(frame=index + 1, time_seconds=round(index / 24, 6),
                            file='frames/' + path.name,
                            mean_rgb_change=round(delta, 4),
                            sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        previous = small

for start in range(0, len(frames), 30):
    sheet = Image.new('RGB', (1600, 1050), '#111917')
    draw = ImageDraw.Draw(sheet)
    for offset, path in enumerate(frames[start:start + 30]):
        x, y = (offset % 5) * 320, (offset // 5) * 175
        with Image.open(path) as source:
            sheet.paste(source.resize((312, 150)), (x + 4, y + 4))
        draw.text((x + 8, y + 156), f'Frame {start+offset+1:03d} | {(start+offset)/24:.3f}s', fill='white')
    sheet.save(OUT / 'contacts' / f'sheet_{start//30+1:02d}.jpg', quality=94)

with (OUT / 'frames.csv').open('w', newline='', encoding='utf-8') as handle:
    writer = csv.DictWriter(handle, fieldnames=records[0].keys())
    writer.writeheader()
    writer.writerows(records)
manifest = dict(source='gemini_generated_video_a0926e99.mp4', fps=24,
                width=1280, height=720, frameCount=len(frames),
                videoDurationSeconds=len(frames)/24, frames=records)
(OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print(json.dumps({k:v for k,v in manifest.items() if k != 'frames'}))
print('Largest adjacent-frame changes:', sorted(records[1:], key=lambda r:r['mean_rgb_change'], reverse=True)[:8])
