import pygame
import os


# used for animation
tick_counter = 0

# size of square tiles, in pixels
tile_size = 64

# dimensions of screen, in tiles
left_border_tiles = 0
right_border_tiles = 0
top_border_tiles = 0
bottom_border_tiles = 2
horizontal_tiles = 18
vertical_tiles = 10
total_horizontal_width = left_border_tiles + horizontal_tiles + right_border_tiles
total_vertical_width = top_border_tiles + vertical_tiles + bottom_border_tiles

hud_top = (top_border_tiles + vertical_tiles) * tile_size


clock = pygame.time.Clock()
FRAMES_PER_SECOND = 30


#initialize all sprite groups
obstacles = pygame.sprite.RenderPlain()
floors = pygame.sprite.RenderPlain()
player_group = pygame.sprite.RenderPlain()
enemies = pygame.sprite.RenderPlain()
enemy_weapons = pygame.sprite.RenderPlain()
hazards = pygame.sprite.RenderPlain()
player_weapons = pygame.sprite.RenderPlain()
collectibles = pygame.sprite.RenderPlain() # should only be collectible by player
hud_group = pygame.sprite.RenderPlain()
statuses = pygame.sprite.RenderPlain()
# new groups:
groups = [obstacles, floors, player_group, player_weapons, enemies, enemy_weapons, hazards, collectibles, hud_group, statuses]


def get_player():
    if not player_group:
        game_over()
    else:
        return [player for player in player_group][0] # I'm sorry


def load_image(image_name, sub_path=None):
    """
    This function handles loading an image in pygame
    :param image_name: (string) the name of an image in the resources folder
    :param sub_path: (string) path from resources folder to the folder the image is in. None if the image is in resources
    :return: the image as a pygame image object
    """
    root_dir = os.path.dirname(__file__)
    resources_dir = os.path.join(root_dir, "resources")
    if sub_path:
        resources_dir = os.path.join(resources_dir, sub_path)
    return pygame.image.load(os.path.join(resources_dir, image_name))


def get_center_pixel(x_tile, y_tile):
    """
    get center pixel of a tile
    :param x_tile: (int)    horizontal index of tile (not counting left border)
    :param y_tile: (int)    vertical index of tile (not counting right border)
    :return: (int, int)     pixel location of center of tile
    """
    x_pixel = (left_border_tiles + x_tile + 1/2) * tile_size
    y_pixel = (top_border_tiles + y_tile + 1/2) * tile_size
    return x_pixel, y_pixel

def get_tile_from_pixel(x_pixel, y_pixel):
    """
    get the tile that a pixel is in
    :param x_pixel: (int)   x index of the pixel
    :param y_pixel: (int)   y index of the pixel
    :return:        (int, int)  x-index, y-index of tile
    """
    x_tile = x_pixel//tile_size - left_border_tiles
    y_tile = y_pixel//tile_size - top_border_tiles
    return x_tile, y_tile



