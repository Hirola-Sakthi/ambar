"""Publish every native reference frame as lossless WebP, without interpolation."""
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.tools' / 'python'))
from PIL import Image

source = ROOT / 'analysis/hair-oil-reference/frames'
out = ROOT / 'public/scenes/hair-oil'
out.mkdir(parents=True, exist_ok=True)
frames = sorted(source.glob('frame_*.png'))
assert len(frames) == 240

def convert(path):
    with Image.open(path) as image:
        image.save(out / (path.stem + '.webp'), lossless=True, method=3)

with ThreadPoolExecutor(max_workers=4) as pool:
    list(pool.map(convert, frames))
for name, index in [('hair-oil-poster.webp', 0), ('hair-oil-product.webp', 200)]:
    with Image.open(frames[index]) as image:
        image.save(ROOT / 'public/scenes' / name, lossless=True, method=3)

phases = [('ingredients', 0, 53), ('bowl-pour', 54, 80),
          ('bottle-fill', 81, 131), ('packaging', 132, 161), ('hero', 162, 239)]
manifest = dict(frameCount=240, width=1280, height=720,
                directory='scenes/hair-oil', revision='hair-oil-native-v1',
                fps=24, phases=[dict(name=name, start=start, end=end) for name,start,end in phases])
(ROOT / 'src/sequenceManifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(f'Prepared {len(frames)} lossless frames, {sum(p.stat().st_size for p in out.glob("*.webp"))/1024**2:.1f} MiB')
