#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
from PIL import Image, ImageEnhance


def reduce_opacity(im, opacity):
    """Returns an image with reduced opacity."""
    assert opacity >= 0 and opacity <= 1
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    else:
        im = im.copy()
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im

def watermark(image, destination, watermark, scale = 0.1, margin = 0.1, opacity = 1):
    """
    Adds a watermark to an image, copying it to a destination folder
    """
    image_name = os.path.basename(image)
    destination_path = os.path.join(destination, image_name)
    im = Image.open(image)
    mark = Image.open(watermark)
    if opacity < 1:
        mark = reduce_opacity(mark, opacity)
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    # create a transparent layer the size of the image and draw the
    # watermark in that layer.
    layer = Image.new('RGBA', im.size, (0,0,0,0))

    # Preserve the aspect ratio
    ratio = min(float(im.size[0]) / mark.size[0], float(im.size[1]) / mark.size[1])
    logo_w = int(mark.size[0] * ratio * scale)
    logo_h = int(mark.size[1] * ratio * scale)
    mark = mark.resize((logo_w, logo_h))
    logo_position = (int((im.size[0] * (1 - margin) - logo_w)), int((im.size[1] * (1 - margin) - logo_h)))
    layer.paste(mark, logo_position)

    # composite the watermark with the layer
    Image.composite(layer, im, layer).save(destination_path)
    
