from pygame.locals import *
from sprite_mixins import *


class StaticTile(pygame.sprite.Sprite):
    """
    background tile, never changes.
    """
    def __init__(self, position, image):
        """

        :param tile_position: tuple(int, int) indices of tile. left to right, top to bottom. border tiles (black space) don't count in this case
        :param image: (pygame image)    the image to use for this tile
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()

        x_tile, y_tile = position
        x_pixel = (left_border_tiles + x_tile) * tile_size
        y_pixel = (top_border_tiles + y_tile) * tile_size
        self.rect.topleft = (x_pixel, y_pixel)


class Fire(AnimationMixin, pygame.sprite.Sprite):
    """
    class for stationary fire hazards
    """
    def __init__(self, position_tile):
        """

        :param position_tile: tuple(int, int) location tile
        """
        pygame.sprite.Sprite.__init__(self)
        AnimationMixin.__init__(self, 'fire', 'png', 9, 'fire', True)
        self.image = load_image('fire0.png', 'fire')
        self.rect = self.image.get_rect()
        self.rect.center = get_center_pixel(position_tile[0], position_tile[1])
        hazards.add(self)

        # now create an infectious fire status
        fire = FireStatus(self)
        fire.remaining_time = 100000000000000

    def get_damage(self):
        """

        :return: damage fire does per 'attack'
        """
        return 5

    def update(self):
        """
        updates fire's state (in this case, swaps out image for animation)
        also spawns fire statuses on anything that touches it
        :return: None
        """
        AnimationMixin.update(self)

        # might want to do a status spawner mixin or something



class PlayerSprite(HealthMixin, RotationMixin, MovementMixin, pygame.sprite.Sprite):
    """
    Player character's sprite. There should only be one of these...
    I guess a possible powerup could be making a 'shadow' that mirrors moves.
    """
    def __init__(self, initial_tile):
        """

        :param position: tuple(int, int)   (x,y) position in tiles
        """
        pygame.sprite.Sprite.__init__(self)

        self.image = load_image("magic.png")

        MovementMixin.__init__(self)
        RotationMixin.__init__(self, self.image, image_direction='down')
        HealthMixin.__init__(self, 100, 15, 0)
        self.rect = self.image.get_rect()
        self.rect.center = get_center_pixel(initial_tile[0], initial_tile[1])
        self.health = 100
        self.speed = 8
        # up, down, left, or right
        self.direction = "down"

        self.add(player_group)

    def update_direction(self):
        """
        update direction of player
        :return: None
        """
        keys = pygame.key.get_pressed()
        if keys[K_DOWN]:
            self.direction = "down"
        elif keys[K_RIGHT]:
            self.direction = "right"
        elif keys[K_LEFT]:
            self.direction = "left"
        elif keys[K_UP]:
            self.direction = "up"
        RotationMixin.set_direction(self, self.direction)
        RotationMixin.update(self)

    def update_position(self):
        """
        Moves player to a new position
        :return: None
        """
        keys = pygame.key.get_pressed()
        x = 1 if keys[K_RIGHT] else -1 if keys[K_LEFT] else 0
        y = 1 if keys[K_DOWN] else -1 if keys[K_UP] else 0
        MovementMixin.set_velocity(self, x*self.speed, y*self.speed)
        MovementMixin.update(self)


    def update_held_weapon(self):
        """
        spawns a held weapon next to player, according to player's direction.
        Right now, only uses sword. will add other weapons later.
        :return: None
        """
        keys = pygame.key.get_pressed()

        if keys[K_SPACE]:
            test_sword = Sword(self, self.direction)
            PauseStatus(self, 7)

        if keys[K_1]:
            test_sword = Sword(self, self.direction)
            PauseStatus(self, 7)
        if keys[K_2]:
            player_shield = Shield(self, self.direction)

        if keys[K_3]:
            player_boomerang = Boomerang(self, self.direction)
        if keys[K_4]:
            Bow(self, self.direction)
        if keys[K_5]:
            FireRod(self, self.direction)
        if keys[K_6]:
            IceRod(self, self.direction)


    def update(self):
        """
        performs all updates to player character
        (updates state by handling button presses)
        :return:
        """
        HealthMixin.update(self)

        if not StatusSprite.affected_by(self, PauseStatus):
            self.update_direction()
            self.update_position()
            self.update_held_weapon()


class Weapon(RotationMixin, NaturalDeathMixin, pygame.sprite.Sprite):
    """
    class for weapons
    """
    def __init__(self, user, image, orientation='right'):
        """

        :param user:
        :param orientation:
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = image

        self.user = user

        NaturalDeathMixin.__init__(self, 20)
        RotationMixin.__init__(self, image, orientation)
        angle = RotationMixin.directions_to_angles[orientation]
        RotationMixin.set_rotation_path(self, angle - 70, angle + 70, 20, should_die=True)
        self.rect = self.image.get_rect()
        user_center = user.rect.center
        dx = 1 if orientation =='right' else -1 if orientation =='left' else 0
        dy = 1 if orientation =='down' else -1 if orientation =='up' else 0
        x = user_center[0] + tile_size * dx
        y = user_center[1] + tile_size * dy
        self.rect.center = (x, y)
        if user in player_group:
            self.add(player_weapons)
            self.affected_group = enemies

        if user in enemies:
            self.add(enemy_weapons)
            self.affected_group = player_group

        PauseStatus(user, 7)

    def get_damage(self):
        return 5

    def update(self):
        RotationMixin.update(self)
        NaturalDeathMixin.update(self)


class Boomerang(MovementMixin, Weapon):
    """
    class for boomerang
    """
    def __init__(self, user, orientation='right'):
        image = load_image("boomerang.png")
        Weapon.__init__(self, user, image, orientation)
        RotationMixin.set_angular_velocity(self, 20)
        self.remaining_time = 200
        MovementMixin.__init__(self)
        self.speed = 8

        dx = 1 if orientation =='right' else -1 if orientation =='left' else 0
        dy = 1 if orientation =='down' else -1 if orientation =='up' else 0
        MovementMixin.set_velocity(self, dx * self.speed, dy*self.speed)

        self.returning = False # whether boomerang is coming back

    def get_damage(self):
        return 2

    def update(self):
        Weapon.update(self)
        MovementMixin.update(self)
        if pygame.sprite.spritecollide(self, self.affected_group, False) or self.has_hit_obstacle:
            for sprite in pygame.sprite.spritecollide(self, self.affected_group, False):
                PauseStatus(sprite, 60)
            self.returning = True
            # spawn statuses
        if pygame.sprite.spritecollide(self, obstacles, False):
            self.returning = True
        if self.returning:
            x, y = self.user.rect.center
            MovementMixin.set_pixel_destination(self, x, y, self.speed)
        if pygame.sprite.collide_rect(self, self.user):
            self.kill()


class Shield(Weapon):
    def __init__(self, user, orientation = 'right'):
        image = load_image("shield.png")
        Weapon.__init__(self, user, image, orientation)
        self.add(obstacles)

    def get_damage(self):
        return 0

    def update(self):
        Weapon.update(self)


class Projectile(MovementMixin, Weapon):
    def __init__(self, user, image, orientation, speed, damage):
        Weapon.__init__(self, user, image, orientation)
        RotationMixin.clear_rotation_state(self)
        MovementMixin.__init__(self)
        self.remaining_time = 500
        self.speed = speed
        self.damage = damage
        dx = 1 if orientation == 'right' else -1 if orientation == 'left' else 0
        dy = 1 if orientation == 'down' else -1 if orientation == 'up' else 0
        MovementMixin.set_velocity(self, dx * self.speed, dy * self.speed)

    def get_damage(self):
        return self.damage

    def update(self):
        Weapon.update(self)
        MovementMixin.update(self)
        if self.has_hit_obstacle:
            self.kill()


class Arrow(Projectile):
    def __init__(self, user, orientation):
        image = load_image("arrow_small.png")
        Projectile.__init__(self, user, image, orientation, 8, 5)


class Bow(Weapon):
    def __init__(self, user, orientation):
        image = load_image("bow.png")
        Weapon.__init__(self, user, image, orientation)
        Arrow(user, orientation)


class FireRod(Weapon):
    def __init__(self, user, orientation):
        image = load_image("fire_rod.png")
        Weapon.__init__(self, user, image, orientation)
        carrier = Arrow(user, orientation)
        FireStatus(carrier)

class IceRod(Weapon):
    def __init__(self, user, orientation):
        image = load_image("ice_rod.png")
        Weapon.__init__(self, user, image, orientation)
        carrier = Arrow(user, orientation)
        IceStatus(carrier)
3
class Sword(Weapon):
    def __init__(self, user, orientation="right"):

        pygame.sprite.Sprite.__init__(self)
        image = load_image('sword1_{}.png'.format(orientation), 'sword')
        Weapon.__init__(self, user, image, orientation)


    def get_damage(self):
        """
        :return: damage this weapon does
        """
        return 5

    def update(self):
        """
        updates age, kills self when too old.
        :return: None
        """
        RotationMixin.update(self)


class Goblin(HealthMixin, MovementMixin, pygame.sprite.Sprite):
    """
    Basic enemy class. just moves up and down
    """
    def __init__(self, position_tile):
        """
        :param position_tile: tuple(int, int) position of center of sprite in tiles
        """
        pygame.sprite.Sprite.__init__(self)
        MovementMixin.__init__(self)
        HealthMixin.__init__(self, 40, 5, 0)
        x_tile, y_tile = position_tile
        MovementMixin.set_tile_sequence(self, [(x_tile, y_tile), (x_tile, y_tile+3)], 3, True)
        self.src_image = load_image("goblin.png")
        self.image = self.src_image
        self.rect = self.image.get_rect()
        self.rect.center = get_center_pixel(x_tile, y_tile)
        self.add(enemies)


    def get_damage(self):
        """
        :return: (int) amount of damage this enemy does
        """
        return 5

    def update(self):
        """
        update enemy state
        :return: None
        """
        HealthMixin.update(self)
        MovementMixin.update(self)


class Chaser(HealthMixin, MovementMixin, pygame.sprite.Sprite):
    def __init__(self, position_tile):
        """
        :param position_tile: tuple(int, int) position of center of sprite in tiles
        """
        pygame.sprite.Sprite.__init__(self)
        MovementMixin.__init__(self)
        HealthMixin.__init__(self, 40, 5, 0)
        x_tile, y_tile = position_tile
        self.src_image = load_image("zombie.png")
        self.image = self.src_image
        self.rect = self.image.get_rect()
        self.rect.center = get_center_pixel(x_tile, y_tile)
        self.add(enemies)

    def get_damage(self):
        """
        :return: (int) amount of damage this enemy does
        """
        return 5

    def update(self):
        """
        update enemy state
        :return: None
        """
        HealthMixin.update(self)
        player = get_player()
        MovementMixin.set_pixel_destination(self, player.rect.center[0], player.rect.center[1], 3)
        MovementMixin.update(self)


class Archer(HealthMixin, MovementMixin, pygame.sprite.Sprite):
    def __init__(self, position_tile):
        """
        :param position_tile: tuple(int, int) position of center of sprite in tiles
        """
        pygame.sprite.Sprite.__init__(self)
        MovementMixin.__init__(self)
        HealthMixin.__init__(self, 40, 5, 0)
        x_tile, y_tile = position_tile
        self.src_image = load_image("archer_elf.png")
        self.image = self.src_image
        self.rect = self.image.get_rect()
        self.rect.center = get_center_pixel(x_tile, y_tile)
        self.add(enemies)

    def get_damage(self):
        """
        :return: (int) amount of damage this enemy does
        """
        return 5

    def update(self):
        """
        update enemy state
        :return: None
        """
        HealthMixin.update(self)
        x_self, y_self = self.rect.center
        player = get_player()
        x_player, y_player = player.rect.center
        if abs(x_self - x_player) < abs(y_self - y_player):
            x_target = x_player
            y_target = (y_self - y_player)*1000
        else:
            x_target = (x_self - x_player) * 1000
            y_target = y_player
        MovementMixin.set_pixel_destination(self, x_target, y_target, 3)
        MovementMixin.update(self)


class collectible(pygame.sprite.Sprite):
    pass


class Heart(pygame.sprite.Sprite):
    def __init__(self, position_tile):
        pygame.sprite.Sprite.__init__(self)
        x_tile, y_tile = position_tile
        self.src_image = load_image("heart.png")
        self.image = self.src_image
        self.rect = self.image.get_rect()
        self.rect.center = get_center_pixel(x_tile, y_tile)
        self.add(collectibles)
    def update(self):
        player = get_player()
        if pygame.sprite.collide_rect(self, player):
            player.health += 10
            self.kill()


class HastePotion(pygame.sprite.Sprite):
    def __init__(self, position_tile):
        pygame.sprite.Sprite.__init__(self)
        x_tile, y_tile = position_tile
        self.src_image = load_image("haste_potion.png")
        self.image = self.src_image
        self.rect = self.image.get_rect()
        self.rect.center = get_center_pixel(x_tile, y_tile)
        self.add(collectibles)
    def update(self):
        player = get_player()
        if pygame.sprite.collide_rect(self, player):
            player.speed += 4
            self.kill()


"""
implement statuses as sprites that attach themselves to victim sprites (always update their centers to be the same as the victim's
mixins will check for statuses
(not doing functional because they would just have to muck around with mixin internals anyway)
status should die naturally after a certain amount of time.
May also be killable by player or monsters (like ice)



During each tick check for collisions between status sprites

simply have a StatusSprite group
"""



# need a better way to spawn statuses onto affected sprites





"""
add statuses
on fire -- damage over time, spreads
frozen - can't move
stunned - scramble movement?
poisoned -- damage over time, slow
pause -- no image, freezes sprite for a second
knockback -- no image. temporarily forces sprite to move away from a source of damage

speed

probably best to just check for status list in mixins.
implement statuses as sprites in order to use overlay images
check for status collisions
"""