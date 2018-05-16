#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
from PIL import Image, ImageEnhance, ImageMath


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


def make_composite_texture(texture_name, textures_folder, destination_folder, maxsize):
    # Get the list of corresponding textures in texture_set var

    texture_set = []

    for texture_file in os.listdir(textures_folder):
        file_extension = os.path.splitext(os.path.basename(texture_file))[1][1:]
        file_basename_no_extension = os.path.splitext(os.path.basename(texture_file))[0]
        if file_extension in['png'] and texture_name in file_basename_no_extension:
            full_texture_path = os.path.join(textures_folder, texture_file)
            texture_set.append(full_texture_path)
    
    # Create the destination image with texture size
    print ('Processing texture_set : {}'.format(texture_set))

    texture_ref = Image.open(texture_set[0])
    (original_width, original_height) = texture_ref.size
    destination_path = os.path.join(destination_folder, texture_name + '.png')

    result_composite = Image.new('RGBA', (original_width, original_height))
    
    columns = len(texture_set)
    column_width = original_width / columns
    top = 0
    left = 0
    bottom = original_height
    
    working_slice = []
    for column in range(columns):
        texture_sliced = Image.open(texture_set[column])
        if texture_sliced.mode == 'I' or texture_sliced.mode == 'L':
            rgba_texture_sliced = ImageMath.eval('texture_sliced/256', {'texture_sliced':texture_sliced}).convert('RGBA')
            texture_sliced = rgba_texture_sliced
            
        left = column_width * column
        if column + 1 == columns:
            right = original_width
        else:
            right = column_width * (column + 1)
        bbox = (int(left), int(top), int(right), int(bottom))
        result_composite.paste(texture_sliced.crop(bbox), bbox)
            
    # Resize the result if needed
    if original_width > maxsize:
        ratio = original_width / maxsize
        width = int(original_width / ratio)
        height = int(original_height / ratio)
    elif original_height > maxsize and original_width <= maxsize:
        ratio = original_height / maxsize
        width = int(original_width / ratio)
        height = int(original_height / ratio)
    else:
        (width, height) = (original_width, original_height)
    
    result_composite = result_composite.resize((width, height))

    # Save the result
    result_composite.save(destination_path)
    
    # Return the image full path
    return destination_path
