"""Reference-width cheek framing with a cleaned text area.

Only the former recorded-copy region uses generated clean background plates.
The serum, fingers and surrounding unmasked pixels remain the recorded footage.
"""
from PIL import Image, ImageDraw, ImageFilter, ImageStat, ImageChops
from threading import Lock


def clamp(value):
    return max(0, min(1, value))


def reference_width(image, size, header=None):
    # Restore the 110px header crop above the footage, then retain the complete
    # horizontal view inside the existing 1440x758 sequence canvas.
    full = Image.new('RGB', (image.width, image.height+110))
    if header is None:
        header=image.crop((0,0,image.width,110)).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    full.paste(header,(0,0))
    full.paste(image, (0,110))
    height = round(size[0]*full.height/full.width)
    photo = full.resize((size[0],height), Image.Resampling.LANCZOS)
    top = (size[1]-height)//2
    frame = Image.new('RGB',size)
    frame.paste(photo,(0,top))
    if top>0:
        frame.paste(photo.crop((0,0,photo.width,top)).transpose(Image.Transpose.FLIP_TOP_BOTTOM),(0,0))
    bottom = size[1]-top-height
    if bottom>0:
        frame.paste(photo.crop((0,photo.height-bottom,photo.width,photo.height)).transpose(Image.Transpose.FLIP_TOP_BOTTOM),(0,top+height))
    return frame


class SkinFraming:
    def __init__(self, assets, size):
        self.size = size
        self.cache={}
        self.lock=Lock()
        self.plates = [Image.open(assets/f'clean-{name}-plate.png').convert('RGB').resize((1902,756),Image.Resampling.LANCZOS)
                       for name in ('cheek','hand','finish')]
        self.mask=Image.new('L',(1902,756))
        ImageDraw.Draw(self.mask).rectangle((70,105,650,540),fill=255)
        self.mask=self.mask.filter(ImageFilter.GaussianBlur(18))
        self.header_plate=Image.open(assets/'clean-header-plate.png').convert('RGB').resize((1902,866),Image.Resampling.LANCZOS).crop((0,0,1902,110))
        self.header_mask=Image.new('L',(1902,110))
        ImageDraw.Draw(self.header_mask).rectangle((550,8,1350,109),fill=255)
        self.header_mask=self.header_mask.filter(ImageFilter.GaussianBlur(8))
        # The recorded pill ends above this boundary. Preserve the genuine last
        # header rows so a moving fingertip continues into the body without a seam.
        fade=Image.new('L',(1902,110),255)
        draw=ImageDraw.Draw(fade)
        for row in range(95,110):
            draw.line((0,row,1901,row),fill=round(255*(109-row)/14))
        self.header_mask=ImageChops.multiply(self.header_mask,fade)

    def render(self, image, time, header):
        key=round(time*30)
        with self.lock:
            if key in self.cache:
                return self.cache[key]
        header=header.copy()
        header.paste(header.crop((0,1,header.width,2)),(0,0))
        if time<=60:
            plate=Image.blend(self.plates[0],self.plates[1],clamp((time-48)/12))
        else:
            plate=Image.blend(self.plates[1],self.plates[2],clamp((time-60)/16))
        # Match lighting to an untouched strip above the recorded copy.
        anchor=(80,40,620,90)
        current=ImageStat.Stat(image.crop(anchor)).mean
        clean=ImageStat.Stat(plate.crop(anchor)).mean
        channels=[]
        for channel,actual,base in zip(plate.split(),current,clean):
            offset=round(actual-base)
            channels.append(channel.point(lambda value: max(0,min(255,value+offset))))
        plate=Image.merge('RGB',channels)
        cleaned=Image.composite(plate,image,self.mask)
        original=ImageStat.Stat(header.crop((80,10,500,90))).mean
        generated=ImageStat.Stat(self.header_plate.crop((80,10,500,90))).mean
        channels=[]
        for channel,actual,base in zip(self.header_plate.split(),original,generated):
            offset=round(actual-base)
            channels.append(channel.point(lambda value:max(0,min(255,value+offset))))
        header=Image.composite(Image.merge('RGB',channels),header,self.header_mask)
        result=reference_width(cleaned,self.size,header)
        with self.lock:
            self.cache[key]=result
            while len(self.cache)>40:
                self.cache.pop(next(iter(self.cache)))
        return result
