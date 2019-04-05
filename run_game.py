import pygame
import sys

from sprite_classes import *


pygame.init()
screen = pygame.display.set_mode((tile_size*total_horizontal_width, tile_size*total_vertical_width))
# DOUBLEBUF TO AVOID FLICKERING


def draw_background():
    """
    draws all stationary objects
    :return:
    """

    # TODO: OPTIMIZE THIS. PERFORMANCE PROBLEMS RESULT FROM BLITTING BACKGROUND HERE.
    obstacles.draw(screen)
    floors.draw(screen)


# now initialize background tiles
def initialize_map():
    """
    function to initialize map
    :return:
    """
    for tile_x in range(horizontal_tiles):
        for tile_y in range(vertical_tiles):
            position = (tile_x, tile_y)
            is_obstacle = tile_x == 0 or tile_x == horizontal_tiles-1 or tile_y == 0 or tile_y == vertical_tiles-1
            img = load_image("brick_dark.png" if is_obstacle else "brick_light.png", "roguetiles")
            tile = StaticTile(position, img)
            if is_obstacle:
                tile.add(obstacles)
            else:
                tile.add(floors)



player = PlayerSprite((8, 4))
test_fire = Fire((2, 2))
test_fire2 = Fire((14, 5))
test_enemy = Goblin((3, 4))
test_enemy2 = Goblin((5, 6))
chaser = Chaser((2, 3))
archer = Archer((10, 5))
heart = Heart((4,4))
potion = HastePotion((10, 7))


def draw_health(health):
    """
    draws health bar on bottom of screen.
    :param health: (int) amount of health in domain [1, 100]
    :return: none
    """
    outer_rect = Rect(20, hud_top, 220, 64)
    health_rect = Rect(30, hud_top+8, health*2, 48)
    black_rect = Rect(30+health*2, hud_top+8, 200-health*2, 48)
    pygame.draw.rect(screen, pygame.Color('orange'), outer_rect)
    pygame.draw.rect(screen, pygame.Color('green'), health_rect)
    if health < 100:
        pygame.draw.rect(screen, pygame.Color('black'), black_rect)


def controller_tick():
    """
    This function handles user input
    (takes input from controller and updates model)
    :return:
    """
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit(0)

    player_group.update()
    hazards.update()
    player_weapons.update()
    enemies.update()
    collectibles.update()
    statuses.update()


def view_tick():
    """
    This function updates the display
    :return:
    """
    draw_background()
    player_group.draw(screen)
    draw_health(player.health)
    hazards.draw(screen)
    player_weapons.draw(screen)
    enemies.draw(screen)
    collectibles.draw(screen)
    statuses.draw(screen)
    pygame.display.update()


initialize_map()

# game loop
while get_player() and get_player().health > 0:
    time = clock.tick(FRAMES_PER_SECOND)
    controller_tick()
    view_tick()
    tick_counter += 1




def game_over():
    # game over. clear screen and show game-over
    screen.fill((0, 0, 0))
    """
    for group in groups:
    for sprite in group:
        sprite.kill()
    """
    game_over_screen = load_image("game_over.jpg")
    screen.blit(game_over_screen, (150, 50))
    pygame.display.update()

game_over()

while True:
    controller_tick()
