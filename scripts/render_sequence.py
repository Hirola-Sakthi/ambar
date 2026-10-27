"""Render the scroll film from the three generated scene masters.
Run: python -m pip install pillow; python scripts/render_sequence.py
The 240 frames animate camera moves and scene dissolves, not a 3D simulation.
"""
from pathlib import Path
from PIL import Image, ImageOps
from concurrent.futures import ThreadPoolExecutor
ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'public' / 'scenes'
OUT = ASSETS / 'sequence'
OUT.mkdir(exist_ok=True)
SIZE = (1440, 758)
images = {name: ImageOps.fit(Image.open(ASSETS / f'{name}.webp').convert('RGB'), SIZE) for name in ('hero', 'serum', 'skin')}
def clamp(x): return max(0, min(1, x))
def ease(x):
    x=clamp(x)
    return x*x*(3-2*x)
def camera(name, zoom, cx=.59, cy=.52):
    image=images[name]
    w,h=SIZE
    cw,ch=w/zoom,h/zoom
    x=max(0,min(w-cw,cx*w-cw/2));y=max(0,min(h-ch,cy*h-ch/2))
    return image.transform(SIZE,Image.Transform.EXTENT,(x,y,x+cw,y+ch),Image.Resampling.BICUBIC)
def render(i):
    p=i/239
    if p<.26:
        image=camera('hero',1+.2*ease(p/.26))
    elif p<.36:
        t=ease((p-.26)/.1)
        image=Image.blend(camera('hero',1.2+.9*t),camera('serum',1.65-.25*t),t)
    elif p<.47:
        image=camera('serum',1.4-.4*ease((p-.36)/.11))
    elif p<.53:
        t=ease((p-.47)/.06)
        image=Image.blend(camera('serum',1+.45*t),camera('skin',1.85),t)
    else:
        image=camera('skin',1.85-.5*ease((p-.53)/.47),.58,.61)
    image.save(OUT/f'frame_{i+1:04d}.webp',quality=80,method=4)
with ThreadPoolExecutor(max_workers=6) as pool:
    list(pool.map(render,range(240)))
# A portrait crop of the same bottle for the product section.
hero=Image.open(ASSETS/'hero.webp')
w,h=hero.size
ImageOps.fit(hero.crop((int(w*.37),0,int(w*.82),h)),(1000,1100)).save(ASSETS/'product.webp',quality=91)
print(f'Rendered 240 frames: {sum(p.stat().st_size for p in OUT.glob("*.webp"))/1024/1024:.1f} MiB')
