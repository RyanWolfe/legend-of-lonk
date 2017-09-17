"""
script to crop images from tilesets. Assumes all source images are in the 'resources' directory.
Places cropped images in the 'resources' directory
"""

import os
project_dir = os.path.dirname(__file__)
resources_path = os.path.join(project_dir, "resources")
from PIL import Image



def crop_image(src_image, dest_path, left, top, src_height, src_width, dest_height, dest_width):
    dest_image = src_image.crop((left, top, left+src_height, top+src_width))
    dest_image = dest_image.resize((dest_width, dest_height))
    dest_image.save(dest_path)

def crop_from_command_line():
    print("extract tiles? (yes to extract uniform-sized tiles from an image, no to extract only one crop")
    response = input()
    tiles = response.lower() == 'yes' or response.lower() == 'y'

    print("Name of source image? (please include file extension)")
    src_image_name = input()
    src_image_path = os.path.join(resources_path, src_image_name)
    src_image = Image.open(src_image_path)

    print("Name of cropped image? (please include file extension)")
    dest_image_name = input()
    dest_path = os.path.join(resources_path, dest_image_name)

    print("pixel values increase from left to right and from top to bottom.")

    if not tiles:
        print("left pixel value (inclusive)?")
        left = int(input())

        print("top pixel value (inclusive)?")
        top = int(input())

    print("width in source?")
    src_width = int(input())

    print("height in source?")
    src_height = int(input())

    print("desired width in destination?")
    dest_width = int(input())

    print("desired height in destination?")
    dest_height = int(input())


    if tiles:
        base_tile_name = dest_image_name.split(".")[0]
        tile_extension = dest_image_name.split(".")[1]
        extract_tiles(src_image, base_tile_name, tile_extension, src_width, src_height, dest_width, dest_height)
    else:
        crop_image(src_image, dest_path, left, top, src_width, src_height, dest_width, dest_height)


def extract_tiles(src_image, base_tile_name, tile_extension, src_tile_width, src_tile_height, dest_tile_width, dest_tile_height):
    """
    Extracts uniformly-sized tiles from an image and saves them as separate images in 'resources"
    :return:
    """

    counter = 0
    left = 0
    right = left + src_tile_width
    top = 0
    bottom = top + src_tile_height
    while bottom <= src_image.height:
        while right <= src_image.width:
            tile_name = "{}{}.{}".format(base_tile_name, counter, tile_extension)
            tile_path = os.path.join(resources_path, tile_name)
            tile = src_image.crop((left, top, right, bottom))
            tile = tile.resize((dest_tile_width, dest_tile_height))
            tile.save(tile_path)

            left = right
            right = left + src_tile_width
            counter += 1

        left = 0
        right = left + src_tile_width
        top = bottom
        bottom = top + src_tile_height




crop_from_command_line()