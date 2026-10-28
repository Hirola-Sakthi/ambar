"""Render the 1,200-frame Aurum film from the slower reference recording.

pip install pillow imageio-ffmpeg
python scripts/render_sequence.py --reference "path/to/slow-reference.mp4"
# Or reuse the extracted frames:
python scripts/render_sequence.py --source-frames .tools/slow-source

The bottle retains its original 156 camera samples and scroll duration. Extra
samples concentrate on impact, liquid-to-skin motion, finger contact and spreading.
"""
import argparse
from bisect import bisect_left
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
from PIL import Image, ImageOps, ImageChops, ImageStat
from splash_scene import SplashScene
from skin_framing import SkinFraming, reference_width

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'public' / 'scenes'
OUT = ASSETS / 'sequence-v4'
SIZE = (1440, 758)
COUNT = 1200
SEGMENTS = [
    ('bottle', 0, 155, 0, .26),
    ('pool-transition', 156, 179, .26, .29),
    ('falling-drop', 180, 251, .29, .347),
    ('splash', 252, 431, .347, .46),
    ('ripples', 432, 527, .46, .535),
    ('cheek', 528, 767, .535, .7),
    ('massage', 768, 1031, .7, .86),
    ('finish', 1032, 1199, .86, 1),
]
SOURCE_RANGES = {
    'ripples': (32, 44), 'cheek': (44, 56),
    'massage': (56, 66.8), 'finish': (66.8, 80),
}

def clamp(value):
    return max(0.0, min(1.0, value))

def ease(value):
    value = clamp(value)
    return value * value * (3 - 2 * value)

def extract(reference, destination, wide_destination, header_destination):
    import imageio_ffmpeg
    destination.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-ss', '32', '-i', str(reference),
        '-t', '48', '-an', '-vf',
        'fps=30,crop=1230:648:670:110,delogo=x=232:y=319:w=26:h=30:show=0,'
        'scale=1440:758:flags=lanczos', '-q:v', '2',
        str(destination / 'source-%04d.jpg'),
    ], check=True)

    wide_destination.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-ss', '32', '-i', str(reference),
        '-t', '48', '-an', '-vf',
        'fps=30,crop=1902:756:0:110,delogo=x=902:y=319:w=26:h=30:show=0',
        '-q:v', '2', str(wide_destination/'source-%04d.jpg'),
    ], check=True)

    header_destination.mkdir(parents=True,exist_ok=True)
    subprocess.run([
        imageio_ffmpeg.get_ffmpeg_exe(),'-y','-ss','32','-i',str(reference),
        '-t','48','-an','-vf','fps=30,crop=1902:110:0:0','-q:v','2',
        str(header_destination/'source-%04d.jpg'),
    ],check=True)


def motion_curve(paths):
    """Allocate samples by visible motion, so recorded scroll pauses do not stall playback."""
    thumbnails = []
    for path in paths:
        with Image.open(path) as image:
            thumbnails.append(image.convert('L').resize((96, 50)))
    cumulative = [0.0]
    for before, after in zip(thumbnails, thumbnails[1:]):
        difference = ImageStat.Stat(ImageChops.difference(before, after)).mean[0]
        cumulative.append(cumulative[-1] + max(0.0, min(12, difference) - .22))
    if cumulative[-1] < .01:
        cumulative = list(range(len(paths)))
    return cumulative

def sample_paths(paths, curve, progress, transform=None):
    target = clamp(progress) * curve[-1]
    high = min(bisect_left(curve, target), len(paths) - 1)
    low = max(0, high - 1)
    span = curve[high] - curve[low]
    mix = (target - curve[low]) / span if span else 0
    with Image.open(paths[low]) as source:
        image = source.convert('RGB')
        if transform:
            image = transform(image, low, progress)
    if mix > .001 and high != low:
        with Image.open(paths[high]) as source:
            other = source.convert('RGB')
            if transform:
                other = transform(other, high, progress)
            image = Image.blend(image, other, mix)
    return image

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path)
    parser.add_argument('--start', type=int, default=0)
    parser.add_argument('--end', type=int, default=COUNT)
    parser.add_argument('--source-frames', type=Path, default=ROOT / '.tools' / 'slow-source')
    parser.add_argument('--wide-source-frames', type=Path, default=ROOT/'.tools'/'wide-liquid')
    parser.add_argument('--header-source-frames',type=Path,default=ROOT/'.tools'/'header-context')
    args = parser.parse_args()
    if args.reference:
        extract(args.reference, args.source_frames, args.wide_source_frames, args.header_source_frames)
    sources = sorted(args.source_frames.glob('source-*.jpg'))
    if len(sources) != 1440:
        raise SystemExit(f'Expected 1440 slow-reference source frames, found {len(sources)}. Supply --reference to extract them.')
    wide_sources = sorted(args.wide_source_frames.glob('source-*.jpg'))
    if len(wide_sources) != 1440:
        raise SystemExit('Expected 1440 wide source frames. Supply --reference to extract them.')
    header_sources=sorted(args.header_source_frames.glob('source-*.jpg'))
    if len(header_sources)!=1440:
        raise SystemExit('Expected 1440 header-context frames. Supply --reference to extract them.')
    OUT.mkdir(parents=True, exist_ok=True)
    hero = ImageOps.fit(Image.open(ASSETS / 'hero.webp').convert('RGB'), SIZE)
    splash = SplashScene(ASSETS, SIZE)
    skin = SkinFraming(ASSETS, SIZE)
    source_phases, analysis = {}, {}
    for name, (start, end) in SOURCE_RANGES.items():
        paths = sources[round((start-32)*30):round((end-32)*30)]
        curve = motion_curve(paths)
        source_phases[name] = (paths, curve)
        analysis[name] = {'sourceStartSeconds': start, 'sourceEndSeconds': end,
                          'sourceFrames': len(paths),
                          'movingIntervals': sum(b>a for a,b in zip(curve,curve[1:]))}
    print('Motion analysis: ' + json.dumps(analysis), flush=True)

    def camera(zoom):
        w, h = SIZE
        cw, ch = w / zoom, h / zoom
        x = max(0, min(w-cw, .59*w-cw/2))
        y = max(0, min(h-ch, .52*h-ch/2))
        return hero.transform(SIZE, Image.Transform.EXTENT, (x,y,x+cw,y+ch), Image.Resampling.BICUBIC)

    hero_end = camera(1.2)
    ripple_paths, ripple_curve = source_phases['ripples']
    # Track the macro bead in the uncropped recording. The last quarter eases
    # into the existing cheek framing so there is no cut at the next phase.
    liquid_centers = [(0,630),(30,600),(60,567),(90,515),(120,478),
                      (180,431),(240,386),(300,340),(359,330)]
    def centered_liquid(image, source_index, progress):
        for (a,x0),(b,x1) in zip(liquid_centers,liquid_centers[1:]):
            if source_index <= b:
                center = x0+(x1-x0)*(source_index-a)/(b-a)
                break
        center = 670 + center*1230/1440
        returning = ease((progress-.75)/.25)
        left=max(0,min(image.width-1436,center-718))
        centered=image.transform(SIZE,Image.Transform.EXTENT,(left,0,left+1436,756),Image.Resampling.BICUBIC)
        return Image.blend(centered,reference_width(image,SIZE),returning)

    def render(index):
        if index < 156:
            image = camera(1 + .2*ease(index/155))
        elif index < 180:
            image = Image.blend(hero_end, splash.pool, ease((index-155)/24))
        elif index < 252:
            image = splash.render(174 + (index-180)/71*33)
        elif index < 432:
            # Evaluate the motion at fractional times rather than duplicating 68 poses.
            image = splash.render(208 + (index-252)/179*68)
        else:
            name, start, end, _, _ = next(segment for segment in SEGMENTS if segment[1] <= index <= segment[2])
            paths, curve = source_phases[name]
            amount = (index-start)/(end-start)
            if name == 'ripples':
                image = sample_paths(wide_sources[:360],curve,amount,centered_liquid)
            else:
                source_start,source_end=SOURCE_RANGES[name]
                wide=wide_sources[round((source_start-32)*30):round((source_end-32)*30)]
                def centered_skin(source,source_index,source_progress):
                    native=round((source_start-32)*30)+source_index
                    with Image.open(header_sources[native]) as context:
                        return skin.render(source,source_start+source_index/30,context.convert('RGB'))
                image=sample_paths(wide,curve,amount,centered_skin)
            if name == 'ripples' and index < start+36:
                settling = splash.render(276+(index-start)*.45)
                image = Image.blend(settling, image, ease((index-start)/35))
        image.save(OUT / f'frame_{index+1:04d}.webp', quality=87, method=4)

    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(render, range(args.start, args.end)))
    if len(list(OUT.glob('*.webp'))) != COUNT:
        raise SystemExit('Incomplete render: run again without --start/--end.')
    manifest = {
        'frameCount': COUNT, 'width': SIZE[0], 'height': SIZE[1],
        'directory': 'scenes/sequence-v4', 'revision': 'reference-cheek-v9',
        'phases': [{'name':name, 'start':start, 'end':end} for name,start,end,_,_ in SEGMENTS],
        'scrollSegments': [{'startFrame':start, 'endFrame':end, 'startProgress':p0, 'endProgress':p1}
                           for _,start,end,p0,p1 in SEGMENTS],
        'sourceAnalysis': analysis,
    }
    (ROOT/'src'/'sequenceManifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    size = sum(p.stat().st_size for p in OUT.glob('*.webp'))
    print(f'Rendered {COUNT} frames, {size/1024/1024:.1f} MiB. Manifest updated.',flush=True)

if __name__ == '__main__':
    main()
