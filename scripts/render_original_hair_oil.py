"""Animate newly imagegen-created artwork into 1,400 original scene frames.

No video frames are read. Pillow renders the animation timeline, using six
generated artwork masters, sprite transforms and camera moves. This is a
composited animation, not 1,400 independent image-model calls or fluid simulation.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.tools/python'))
from PIL import Image, ImageChops, ImageDraw, ImageFilter

ART = ROOT / 'public/scenes/hair-oil-original/masters'
OUT = ROOT / 'public/scenes/hair-oil-original/frames'
SIZE = W, H = (1920, 1080)
COUNT = 1400


def clamp(value):
    return max(0, min(1, value))


def ease(value):
    t = clamp(value)
    return t*t*(3-2*t)


def load(name):
    return Image.open(ART / name).convert('RGB').resize(SIZE, Image.Resampling.LANCZOS)


def sprite(image, box):
    part = image.crop(box)
    alpha = part.getchannel('A')
    bounds = alpha.point(lambda value: 255 if value > 30 else 0).getbbox()
    return part.crop(bounds)


EMPTY = load('empty-bowl.png')
POUR = load('pouring.png')
FILLED = load('open-filled.png')
HERO = load('product-hero.png')
atlas = Image.open(ART / 'ingredients-atlas.png').convert('RGBA')
aw, ah = atlas.size
SPRITES = [sprite(atlas, (c*aw//3,r*ah//2,(c+1)*aw//3,(r+1)*ah//2))
           for r in range(2) for c in range(3)]
package = Image.open(ART / 'packaging-atlas.png').convert('RGBA')
pw, ph = package.size
CAP = sprite(package, (0,0,pw//2,ph))
LABEL = sprite(package, (pw//2,0,pw,ph))

# Restore the real photographed front rim over ingredients for proper occlusion.
FRONT = Image.new('L', SIZE)
fd = ImageDraw.Draw(FRONT)
curve=[]
for x in range(round(.22*W),round(.78*W)+1):
    dx=(x/W-.5)/.278
    y=(.54+.081*math.sqrt(max(0,1-dx*dx)))*H
    curve.append((x,round(y)))
fd.polygon(curve+[(round(.78*W),H),(round(.22*W),H)],fill=255)
FRONT = FRONT.filter(ImageFilter.GaussianBlur(.6))

# Cell, first frame, duration, landing x/y, width, initial rotation.
DROPS = [
    (1,120,140,.425,.557,.086,-26),
    (0,158,150,.510,.565,.083,18),
    (2,205,140,.465,.565,.065,-34),
    (5,238,130,.560,.567,.072,42),
    (3,270,150,.615,.545,.145,-22),
    (4,300,155,.550,.515,.115,30),
]


def opening(index):
    frame=EMPTY.convert('RGBA')
    for cell,start,duration,x,end_y,width,angle in DROPS:
        if index < start:
            continue
        t=clamp((index-start)/duration)
        # Gravity accelerates the descent; a short damped rebound settles contact.
        y=-.22+(end_y+.22)*t*t
        if index>start+duration:
            dt=index-start-duration
            y=end_y-.014*abs(math.sin(dt*.11))*math.exp(-dt/22)
        item=SPRITES[cell]
        target_w=round(width*W)
        item=item.resize((target_w,round(target_w*item.height/item.width)),Image.Resampling.LANCZOS)
        turn=angle*(1-t)+math.sin(t*math.pi)*5
        item=item.rotate(turn,resample=Image.Resampling.BICUBIC,expand=True)
        frame.alpha_composite(item,(round(x*W-item.width/2),round(y*H-item.height/2)))
    return Image.composite(EMPTY,frame.convert('RGB'),FRONT)


def pouring(index):
    frame=POUR.copy()
    amount=ease((index-580)/265)
    if amount:
        # Reveal the generated full-oil interior upward inside the glass walls.
        level=round((.48-.215*amount)*H)
        mask=Image.new('L',SIZE)
        ImageDraw.Draw(mask).rectangle((round(.527*W),level,round(.657*W),round(.813*H)),fill=255)
        mask=mask.filter(ImageFilter.GaussianBlur(2))
        frame=Image.composite(FILLED,frame,mask)
    # Dissolve away the bowl/pour after filling, preserving the generated scene.
    return Image.blend(frame,FILLED,ease((index-835)/64))


def packaging(index):
    frame=FILLED.convert('RGBA')
    label_amount=ease((index-910)/95)
    if label_amount:
        width=max(1,round(.139*W*label_amount))
        label=LABEL.resize((width,round(.435*H)),Image.Resampling.LANCZOS)
        frame.alpha_composite(label,(round(.590*W-width/2),round(.337*H)))
    cap_amount=ease((index-960)/85)
    if index>=960:
        cap=CAP.resize((round(.080*W),round(.143*H)),Image.Resampling.LANCZOS)
        frame.alpha_composite(cap,(round(.590*W-cap.width/2),round((.094-(1-cap_amount)*.37)*H)))
    # Resolve sprite assembly to the matching finished generated photograph.
    return Image.blend(frame.convert('RGB'),HERO,ease((index-1045)/34))


def camera(frame,index):
    # Small deterministic dolly keeps all 1,400 samples distinct without morphing.
    if index<500:
        scale=1+.018*index/499
        focus=.5
    elif index<900:
        scale=1.018-.018*(index-500)/399
        focus=.59
    elif index<1080:
        scale=1
        focus=.59
    else:
        scale=1+.018*(index-1080)/319
        focus=.59
    # Fractional sampling avoids stepped integer-pixel camera movement.
    crop_w,crop_h=W/scale,H/scale
    left=(W-crop_w)*focus
    top=(H-crop_h)*.5
    return frame.transform(SIZE,Image.Transform.EXTENT,(left,top,left+crop_w,top+crop_h),Image.Resampling.BICUBIC)


SETTLED = opening(499)


def render(index):
    if index<500:
        frame=opening(index)
    elif index<540:
        frame=Image.blend(SETTLED,pouring(540),ease((index-500)/39))
    elif index<900:
        frame=pouring(index)
    elif index<1080:
        frame=packaging(index)
    else:
        frame=HERO
    frame=camera(frame,index)
    return frame


def write(index):
    frame=render(index)
    frame.save(OUT / f'frame_{index+1:04d}.webp',quality=96,method=3)
    return index


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--preview',action='store_true')
    args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    if args.preview:
        samples=[0,119,175,245,335,450,499,539,680,820,899,960,1010,1079,1399]
        sheet=Image.new('RGB',(1600,975),'#17251c')
        draw=ImageDraw.Draw(sheet)
        for offset,index in enumerate(samples):
            frame=render(index)
            frame.save(OUT.parent / f'preview-{index+1:04d}.webp',quality=97)
            x=(offset%4)*400;y=(offset//4)*244
            sheet.paste(frame.resize((392,220)),(x+4,y+4))
            draw.text((x+8,y+227),f'Frame {index+1:04d}',fill='white')
        sheet.save(OUT.parent / 'contact.jpg',quality=95)
        print('Preview ready',flush=True)
        return
    with ThreadPoolExecutor(max_workers=4) as pool:
        for n,_ in enumerate(pool.map(write,range(COUNT)),1):
            if n%100==0:print(f'Rendered {n}/{COUNT}',flush=True)
    assert len(list(OUT.glob('frame_*.webp')))==COUNT
    render(0).save(OUT.parent/'poster.webp',quality=98)
    HERO.save(OUT.parent/'product.webp',quality=98)
    phases=[('empty-bowl',0,119),('ingredients',120,499),('bowl-pour',500,579),
            ('bottle-fill',580,899),('packaging',900,1079),('hero',1080,1399)]
    manifest=dict(frameCount=COUNT,width=W,height=H,directory='scenes/hair-oil-original/frames',
                  revision='original-art-v1',source='New imagegen artwork; no video frames',
                  processing='Layer animation, ingredient gravity, assembly and camera moves',
                  phases=[dict(name=n,start=s,end=e) for n,s,e in phases])
    (ROOT/'src/sequenceManifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print('All 1,400 original-art frames ready; manifest switched.',flush=True)


if __name__=='__main__':
    main()
