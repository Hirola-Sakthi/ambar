"""Import every native video frame, retaining resolution and source timing.

The fixed corner sparkle is removed with a local video filter. No frame-rate
conversion, interpolation, resizing, generated artwork or global sharpening.
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

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.tools/python'))
from PIL import Image, ImageDraw

FFMPEG=ROOT/'.tools/python/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
OUT=ROOT/'public/scenes/cinematic-hair-oil'
REVIEW=ROOT/'analysis/cinematic-hair-oil'


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',default=r'C:\Users\balaa\Downloads\An_ultra-realistic,_continuous_cinematic_hair_df569112_1080p.mp4')
    args=parser.parse_args()
    source=Path(args.source)
    OUT.mkdir(parents=True,exist_ok=True)
    REVIEW.mkdir(parents=True,exist_ok=True)
    logpath=REVIEW/'decode.log'
    command=[str(FFMPEG),'-y','-hide_banner','-i',str(source),'-map','0:v:0','-an',
             '-vf','delogo=x=1696:y=854:w=90:h=91,showinfo',
             '-fps_mode','passthrough','-c:v','libwebp','-lossless','1',
             '-compression_level','3','-start_number','1',str(OUT/'frame_%04d.webp')]
    with logpath.open('w') as log:
        subprocess.run(command,stdout=log,stderr=log,check=True)
    # Record each decoded frame's actual PTS rather than estimating from index.
    log=logpath.read_text()
    times=re.findall(r'\bn:\s*(\d+)\s+pts:\s*\d+\s+pts_time:([\d.]+)',log)
    frames=sorted(OUT.glob('frame_*.webp'))
    assert len(times)==len(frames)==240,(len(times),len(frames))
    # Normalize the final delivery image losslessly, preserving decoded RGB.
    with Image.open(frames[-1]) as image:
        final_rgb=image.convert('RGB')
    temporary=frames[-1].with_suffix('.tmp')
    final_rgb.save(temporary,format='WEBP',lossless=True,method=3)
    temporary.replace(frames[-1])

    def inspect(item):
        i,path=item
        assert path.name==f'frame_{i+1:04d}.webp'
        with Image.open(path) as image:
            image.load()
            assert image.size==(1920,1080)
        assert int(times[i][0])==i
        return dict(frame=i+1,time_seconds=float(times[i][1]),
                    file=path.name,bytes=path.stat().st_size,
                    sha256=hashlib.sha256(path.read_bytes()).hexdigest())

    with ThreadPoolExecutor(max_workers=4) as pool:
        records=list(pool.map(inspect,enumerate(frames)))
    with (REVIEW/'frames.csv').open('w',newline='',encoding='utf-8') as handle:
        writer=csv.DictWriter(handle,fieldnames=records[0].keys())
        writer.writeheader();writer.writerows(records)
    (REVIEW/'manifest.json').write_text(json.dumps(dict(source=source.name,
        sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        frameCount=len(frames),width=1920,height=1080,fps=24,
        watermarkRectangle=dict(x=1696,y=854,width=90,height=91),frames=records),indent=2),encoding='utf-8')
    # Every native frame appears in a numbered sheet for visual review.
    for start in range(0,len(frames),30):
        sheet=Image.new('RGB',(1600,1050),'#17251c')
        draw=ImageDraw.Draw(sheet)
        for offset,path in enumerate(frames[start:start+30]):
            x=(offset%5)*320;y=(offset//5)*175
            with Image.open(path) as image:sheet.paste(image.resize((312,150)),(x+4,y+4))
            draw.text((x+8,y+156),f'Frame {start+offset+1:03d} | {records[start+offset]["time_seconds"]:.3f}s',fill='white')
        sheet.save(REVIEW/f'sheet_{start//30+1:02d}.jpg',quality=94)
    shutil.copyfile(frames[0],OUT/'poster.webp')
    shutil.copyfile(frames[-1],OUT/'product.webp')
    phases=[('empty-bowl',0,23),('ingredients',24,71),('bowl-pour',72,107),
            ('bottle-fill-and-label',108,179),('cap',180,203),('hero',204,239)]
    manifest=dict(frameCount=len(frames),width=1920,height=1080,
                  directory='scenes/cinematic-hair-oil',revision='cinematic-native-v2',
                  fps=24,durationSeconds=10,source=source.name,
                  processing='All native frames; lossless WebP; fixed corner watermark removal',
                  phases=[dict(name=n,start=s,end=e) for n,s,e in phases])
    (ROOT/'src/sequenceManifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(f'Imported and validated every source frame: {len(frames)} lossless 1920x1080 images, {sum(r["bytes"] for r in records)/1024**2:.1f} MiB',flush=True)


if __name__=='__main__':
    main()
