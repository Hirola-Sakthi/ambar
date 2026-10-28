"""Deterministic, scroll-reversible liquid impact compositor.

Photoreal transparent crown/jet artwork is generated with imagegen. This renderer
provides the timed fall, crown rise/collapse, delayed rebound, ballistic satellite
drops and outward surface waves. All geometry is centered on one impact point.
"""
import math
from PIL import Image, ImageOps, ImageDraw, ImageFilter


def clamp(value):
    return max(0.0, min(1.0, value))


def ease(value):
    value = clamp(value)
    return value * value * (3 - 2 * value)


def cutout(path):
    image = Image.open(path).convert('RGBA')
    bounds = image.getchannel('A').point(lambda a: 255 if a > 12 else 0).getbbox()
    if not bounds:
        raise ValueError(f'Empty cutout: {path}')
    return image.crop(bounds)


class SplashScene:
    def __init__(self, assets, size):
        self.size = size
        self.pool = ImageOps.fit(Image.open(assets / 'splash-pool.png').convert('RGB'), size)
        self.drop = cutout(assets / 'falling-drop.png')
        self.crown = cutout(assets / 'splash-crown.png')
        self.jet = cutout(assets / 'splash-jet.png')
        self.center = size[0] / 2
        self.surface = size[1] * .735

    def place(self, image, asset, width, height, center, bottom, opacity=1):
        if width < 1 or height < 1 or opacity <= 0:
            return
        sprite = asset.resize((max(1, round(width)), max(1, round(height))), Image.Resampling.LANCZOS)
        if opacity < 1:
            sprite.putalpha(sprite.getchannel('A').point(lambda a: round(a * opacity)))
        image.alpha_composite(sprite, (round(center - sprite.width / 2), round(bottom - sprite.height)))

    def waves(self, age):
        layer = Image.new('RGBA', self.size)
        draw = ImageDraw.Draw(layer)
        for delay in (0, 9, 19, 31):
            time = age - delay
            if time < 0:
                continue
            radius = 75 + 9 * time
            depth = radius * .16
            alpha = round(105 * clamp(time / 5) * (1 - clamp(time / 100)))
            bounds = (self.center-radius, self.surface-depth, self.center+radius, self.surface+depth)
            draw.ellipse(bounds, outline=(123, 48, 3, alpha), width=6)
            draw.arc((bounds[0], bounds[1]-2, bounds[2], bounds[3]-2), 12, 168,
                     fill=(255, 231, 156, alpha), width=2)
        return layer.filter(ImageFilter.GaussianBlur(.65))

    def render(self, index):
        image = self.pool.copy().convert('RGBA')
        if index < 208:
            time = clamp((index - 174) / 33)
            flight = clamp(time/.93)
            contact = ease((time-.93)/.07)
            bottom = -18 + (self.surface + 18) * flight * flight
            self.place(image, self.drop, 84*(1+.8*contact), 142*(1-.68*contact), self.center, bottom)
            return image.convert('RGB')

        age = index - 208
        image.alpha_composite(self.waves(age))
        if age < 10:
            depression = Image.new('RGBA', self.size)
            draw = ImageDraw.Draw(depression)
            radius = 38 + 8 * age
            draw.ellipse((self.center-radius, self.surface-12, self.center+radius, self.surface+12),
                         fill=(119, 44, 3, round(90 * (1 - age / 10))))
            image.alpha_composite(depression.filter(ImageFilter.GaussianBlur(6)))
        if age < 6:
            # Keep the fluid at contact while its volume expands into the crown.
            self.place(image, self.drop, 151+age*8, 45*(1-age/6), self.center,
                       self.surface, 1-age/6)

        # Rebound follows the crown, rather than appearing at the instant of contact.
        rebound = ease((age-11)/17) * (1-ease((age-35)/26))
        jet_height = 340 * rebound
        if rebound > .01:
            self.place(image, self.jet, 108 * (.65 + .35 * rebound), jet_height,
                       self.center, self.surface, min(1, rebound * 4))
        crown = ease(age/13) * (1-ease((age-30)/30))
        crown_width = 390 + 300 * ease(age/30)
        self.place(image, self.crown, crown_width, 220 * crown,
                   self.center, self.surface + 9, min(1, crown * 5))

        # Small droplets leave the rim and return under gravity; no random jitter.
        for side, delay, velocity, height in ((-1, 14, 3.1, 10.8), (1, 16, 3.6, 12.2),
                                               (-1, 20, 5.0, 8.7), (1, 22, 5.5, 9.3)):
            time = age - delay
            if not 0 < time < 34:
                continue
            x = self.center + side * (185 + velocity * time)
            y = self.surface - 125 - height * time + .42 * time * time
            if y > self.surface:
                continue
            diameter = 12 + 3 * math.sin(time / 34 * math.pi)
            opacity = min(1, time/3, (34-time)/5)
            self.place(image, self.drop, diameter, diameter * 1.12, x, y, opacity)
        return image.convert('RGB')
