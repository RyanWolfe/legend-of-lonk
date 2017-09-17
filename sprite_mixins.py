from game_model import *


class AnimationMixin(pygame.sprite.Sprite):
    """
    mixin that provides animation functionality
    images must be within the same folder, and that folder must be within resources
    images must be in the format 'basename{}.extension' where {} is the index of the frame of animation (start at 0)
    """
    def __init__(self, image_base_name, image_extension, number_of_frames, images_path=None, persistent=True):
        """
        initialize
        :param image_base_name: (string)    base name of the animation images
        :param image_extension: (string)    file extension for images (i.e. 'png', 'jpg')
        :param number_of_frames: (int)      the number of frames in the animation
        :param images_path: (string)        subpath from resources folder to folder containing animations if there is any
        :param persistent: (boolean)        false if sprite should die after animation is completed
        """
        self.image_base_name = image_base_name
        self.image_extension = image_extension
        self.images_path = images_path
        self.number_of_frames = number_of_frames
        self.persistent = persistent
        self.current_frame = 0
        self.image = None
        self.set_image()

    def update(self):
        """
        change image to that for next frame of animation. loops animation if persistent,
         kills sprite otherwise.
        :return:
        """
        self.current_frame = (self.current_frame + 1) % self.number_of_frames
        self.set_image()
        if self.current_frame >= self.number_of_frames and not self.persistent:
            self.kill()

    def set_image(self):
        """
        ensure image matches current frame
        :return:
        """
        self.image = load_image(self.image_base_name + str(self.current_frame) + "." + self.image_extension, self.images_path)


class MovementMixin(pygame.sprite.Sprite):
    """
    Mixin for handling sprite movement.
    Two main movement modes: by destination and by velocity.
    destination:
        sprite will move towards destination in a straight line until its center is at the center of the destination.
        If it encounters an impassable object it will most likely get stuck. may add pathfinding to avoid this later.
        Performance issues wouldn't be too bad if I stored a path and had it follow it, but storing the path might be
        a problem if there are a lot of moving obstacles...
    destination sequence:
        a destination sequence (list of tiles) can be set.
        This sequence can be used as a loop/patrol, or as a one-time path.
        when the sprite collides with an obstacle, it will stop trying to reach its current destination and move on to the next one.
    velocity:
        sprite will move with that velocity (in pixels per frame) until it gets stuck or killed.

    """
    def __init__(self):
        """
        :param destination: (int, int)  destination tile.  indices from left to right, top to bottom.
        :param speed: (int)             movement speed in pixels per frame
        :param velocity: (int, int)     velocity vector in pixels per frame, left to right, top to bottom.
        :param tile_sequence: (list(int, int))  list of tiles to be traveled to
        :param sequence_idx: (int)              which tile in the sequence to travel to
        :param sequence_repeats: (boolean)      whether the tile sequence should be repeated (whether the sprite should go in a loop)

        """
        self.speed = 0
        self.destination_tile = None
        self.destination_pixel = None
        self.velocity = None
        self.tile_sequence = None
        self.sequence_index = None
        self.sequence_repeats = None
        self.has_hit_obstacle = False

    def clear_fields(self):
        """
        use this to clean up fields when using setters
        :return:
        """
        self.destination_tile = None
        self.destination_pixel = None
        self.velocity = None
        self.tile_sequence = None
        self.sequence_index = None
        self.sequence_repeats = None

    def set_tile_destination(self, x_tile, y_tile, movement_speed):
        """

        :param x_tile:      (int)        horizontal index for destination tile (left to right)
        :param y_tile:      (int)        vertical index for destination tile (top to bottom)
        :param movement_speed:  (int)    pixels per frame
        :return:
        """
        self.clear_fields()
        self.destination_tile = (x_tile, y_tile)
        self.speed = movement_speed

    def set_pixel_destination(self, x_pixel, y_pixel, movement_speed):
        """

        :param x_pixel:     (int)   horizontal index for destination pixel
        :param y_pixel:     (int)   vertical index for destination pixel
        :param movement_speed: (int)    pixels per frame
        :return:
        """
        self.clear_fields()
        self.destination_pixel = (x_pixel, y_pixel)
        self.speed = movement_speed

    def set_tile_sequence(self, sequence, movement_speed, sequence_repeats):
        """

        :param sequence:            List(int, int)  list of tiles the sprite should travel to
        :param movement_speed:      (int)            max horizontal/vertical speed of sprite in pixels per frame
        :param sequence_repeats:    (boolean)       true if the sprite should cycle between destinations in a loop. False to make it stop upon reaching last destination.
        :return: None
        """
        self.clear_fields()
        self.tile_sequence = sequence
        self.speed = movement_speed
        self.sequence_index = 0
        self.sequence_repeats = sequence_repeats
        self.destination_tile = sequence[0]

    def increment_destination_tile(self):
        """
        Increment current destination to next tile in the sequence
        :return:
        """
        self.sequence_index += 1
        if self.sequence_index >= len(self.tile_sequence):
            if self.sequence_repeats:
                self.sequence_index = 0
            else:
                self.clear_fields()
                return
        self.destination_tile = self.tile_sequence[self.sequence_index]

    def set_velocity(self, x_velocity, y_velocity):
        """

        :param x_velocity: pixels per frame? or
        :param y_velocity:
        :return:
        """
        self.clear_fields()
        self.velocity = (x_velocity, y_velocity)

    def update(self):
        """

        :return:
        """

        if StatusSprite.affected_by(self, PauseStatus) or StatusSprite.affected_by(self, IceStatus):
            return

        x_pixel, y_pixel = self.rect.center
        old_x, old_y = x_pixel, y_pixel
        new_x, new_y = None, None
        if self.velocity:
            x_velocity, y_velocity = self.velocity
            x_pixel += x_velocity
            y_pixel += y_velocity
            new_x, new_y = (x_pixel, y_pixel)

        elif self.destination_tile or self.destination_pixel:
            if self.destination_pixel:
                x_destination_pixel, y_destination_pixel = self.destination_pixel
            else:
                x_destination_tile, y_destination_tile = self.destination_tile
                x_destination_pixel, y_destination_pixel = get_center_pixel(x_destination_tile, y_destination_tile)
            x_cur_pixel, y_cur_pixel = self.rect.center

            if abs(x_destination_pixel - x_cur_pixel) < self.speed:
                x_cur_pixel = x_destination_pixel
            else:
                x_cur_pixel += self.speed if x_cur_pixel < x_destination_pixel else -self.speed

            if abs(y_destination_pixel - y_cur_pixel) < self.speed:
                y_cur_pixel = y_destination_pixel
            else:
                y_cur_pixel += self.speed if y_cur_pixel < y_destination_pixel else -self.speed
            new_x, new_y = x_cur_pixel, y_cur_pixel


        self.rect.center = (new_x, new_y)
        # in any case, check for collisions
        if pygame.sprite.spritecollide(self, obstacles, False):
            self.has_hit_obstacle = True
            if self.tile_sequence:
                self.increment_destination_tile()
            # try just moving in one dimension instead of both at the same time
            self.rect.center = (new_x, old_y)
            if pygame.sprite.spritecollide(self, obstacles, False):
                self.rect.center = (old_x, new_y)
                if pygame.sprite.spritecollide(self, obstacles, False):
                    self.rect.center = (old_x, old_y)




        if self.tile_sequence:
            if self.rect.center == get_center_pixel(self.destination_tile[0], self.destination_tile[1]):
                self.increment_destination_tile()


class RotationMixin(pygame.sprite.Sprite):
    # TODO: add option to rotate around particular point in the sprite rather than only the center
    # TODO: improve image quality by rotating original image rather than incrementally
    """
    class to handle sprite rotation
    Angles are measured from standard position: i.e. right is 0 degrees, up is 90 degrees, left is 180 degrees, down is 270 degrees.
    Intuitively, it can only be used in sprites which have images.

    Be careful about combining this with AnimationMixin.
    It'll only work properly if the sprite's animation images all face in the same direction

    set_direction and set_angle immediately rotate a sprite to a particular orientation
    set_angular velocity causes the sprite to spin until angular velocity is changed again
    set_rotation_path will causes the sprite to gradually rotate from one angle to another
    """
    def __init__(self, src_image, image_direction='right', initial_angle=None):
        """
        :param image_direction: (string) the direction the sprite's base image faces
        :param initial_angle: initial angle of the sprite's base image
        """
        self.src_image = src_image
        self.initial_angle = initial_angle if initial_angle else RotationMixin.directions_to_angles[image_direction]
        if initial_angle:
            self.current_angle = initial_angle

        self.current_angle = self.initial_angle
        self.angular_velocity = None
        self.start_angle = None
        self.end_angle = None
        self.should_die = False

    directions_to_angles = {"right": 0, "up": 90, "left": 180, "down": 270}

    def clear_rotation_state(self):
        """
        clears rotation mode fields so that a new rotation mode can be set
        :return: None
        """
        self.current_angle = self.initial_angle
        self.angular_velocity = None
        self.start_angle = None
        self.end_angle = None

    def set_direction(self, direction):
        """
        Immediately sets orientation of sprite to the direction specified by the input string.
        :param direction: (string)  'up', 'down', 'left', or 'right'
        :return: None
        """
        self.current_angle = RotationMixin.directions_to_angles[direction]

    def set_angle(self, angle):
        """
        Immediately sets orientation of sprite to the angle (from standard position) specified by the input string.
        :param angle:   (int)       angle from standard position to set sprite.
        :return: None
        """
        self.current_angle = angle

    def set_angular_velocity(self, angular_velocity):
        """
        Make sprite spin at a particular angular velocity until another rotation mode is set
        :param angular_velocity: (int)  angular velocity with which the sprite should spin, in degrees per frame
        :return: None
        """
        self.clear_rotation_state()
        self.angular_velocity = angular_velocity

    def set_rotation_path(self, start_angle, end_angle, angular_velocity, should_die=False):
        """
        Cause sprite to rotate from the start angle to the end angle at a rate of angular_speed degrees per frame
        :param start_angle:     (int) angle to start rotation at
        :param end_angle:       (int) angle to end rotation at
        :param angular_velocity:   (int) degrees of rotation per frame. signed to indicate direction of rotation (positive for counterclockwise, negative for clockwise)
        :param should_die:      (bool)      whether sprite should die on completion of the rotation path
        :return:
        """
        self.clear_rotation_state()
        self.start_angle = start_angle
        self.current_angle = start_angle
        self.end_angle = end_angle
        self.angular_velocity = angular_velocity
        self.should_die = should_die

    def update(self):
        """
        update orientation of image
        :return:
        """
        if self.end_angle and abs(self.current_angle - self.end_angle) < self.angular_velocity:
            self.current_angle = self.end_angle
            if self.should_die:
                self.kill()
            self.clear_rotation_state()

        if self.angular_velocity:
            self.current_angle += self.angular_velocity

        # might want to improve rotation about a point.
        x, y = self.rect.center
        self.image = pygame.transform.rotate(self.src_image, self.current_angle - self.initial_angle)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class HealthMixin(pygame.sprite.Sprite):
    """
    class to handle health updates.
    Gives player and mobs short grace period during which they cannot take damage again
    if knock_back_factor is greater than 0, the sprite will be forced to move away from the sprite for a short time
    """
    def __init__(self, max_health, grace_period, knock_back_factor=0):
        """

        :param max_health:      (int)   Max health of the sprite
        :param grace_period:    (int)   Number of frames after taking damage during which sprite is invulnerable
        :param knock_back_factor: (int) measure of how far sprite should be knocked back by damage. should only be used by sprites with MovementMixin.
        """
        self.max_health = max_health
        self.health = self.max_health
        self.grace_period = grace_period
        self.damage_timer = 0  # ticks remaining until sprite exits the grace period
        self.knock_back_factor = knock_back_factor

    def max_damage_from_group(self, damaging_group):
        """
        :param group:   sprite group to check for collisions with
        :return:        Maximum damage of any item that this sprite touches in the group
        """
        contact = pygame.sprite.spritecollide(self, damaging_group, False)
        if contact:
            damage = max([element.get_damage() for element in damaging_group])
            return damage
        return 0

    def max_damage_from_group_list(self, group_list):
        """
        :param groups: list of groups this sprite should take damage from
        :return:
        """
        return max([self.max_damage_from_group(group) for group in group_list])

    def update(self):
        """
        updates health
        :return:
        """
        if self.damage_timer:
            self.damage_timer -= 1
        else:
            if self in enemies:
                damaging_groups = [hazards, player_weapons]
            else:
                damaging_groups = [hazards, enemies, enemy_weapons]
            damage = self.max_damage_from_group_list(damaging_groups)
            self.health -= damage
            self.damage_timer = self.grace_period
            if damage and self.knock_back_factor:
                # TODO: MOVE SPRITE AWAY FROM WHATEVER CAUSED THE DAMAGE
                pass

            if StatusSprite.affected_by(self, FireStatus):
                self.health <= 1
        if self.health <= 0:
            self.kill()


class NaturalDeathMixin(pygame.sprite.Sprite):
    def __init__(self, lifetime):
        self.remaining_time = lifetime

    def update(self):
        self.remaining_time -=1
        if self.remaining_time <= 0:
            self.kill()



class StatusSprite(NaturalDeathMixin, pygame.sprite.Sprite):
    """
    this sprite will 'attach' itself to another sprite and alter the other sprite's behavior until it dies
    may be invisible.
    has initial function, update function, and cleanup function
    """
    def __init__(self, victim_sprite, image, lifetime, infectious):
        """

        :param victim_sprite:       (sprite)            which sprite the status should attach itself to
        :param image                (image)             image for the status
        :param lifetime:            (int)               how many ticks the status should last
        :param infectious:          int                 how status should spread. 0 for no spreading, 1 for spreading to only 1 target, 2 for unlimited spreading
        """
        pygame.sprite.Sprite.__init__(self)
        self.lifetime = lifetime
        self.infectious = infectious
        NaturalDeathMixin.__init__(self, lifetime)
        self.victim_sprite = victim_sprite
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = self.victim_sprite.rect.center
        self.add(statuses)

    affected_by_status = [player_group, player_weapons, enemies, enemy_weapons]

    def update(self):
        # stay centered on victim
        self.rect.center = self.victim_sprite.rect.center
        NaturalDeathMixin.update(self)

        #check if victim has been killed
        if not any(self.victim_sprite in group for group in groups):
            self.kill()

        # spread to colliding victims
        if self.infectious: # spread to all colliding victims
            for group in StatusSprite.affected_by_status:
                colliding_sprites = pygame.sprite.spritecollide(self, group, False)
                for victim in colliding_sprites:
                    next_infection_arg = 0 if self.infectious == 1 else self.infectious
                    # don't keep stacking statuses.
                    if not StatusSprite.affected_by(victim, type(self)):
                        StatusSprite(victim, self.image, self.lifetime, next_infection_arg)



    @staticmethod
    def get_status_sprites(victim_sprite):
        """
        :param victim_sprite:       the sprite whose status sprites we want
        :return:                    a list of status sprites affecting this sprite
        """
        return [status for status in pygame.sprite.spritecollide(victim_sprite, statuses, False) if status.victim_sprite == victim_sprite]

    @staticmethod
    def affected_by(victim_sprite, status_type):
        """

        :param victim_sprite:
        :param status_type:
        :return:
        """
        return any(isinstance(status, status_type) for status in StatusSprite.get_status_sprites(victim_sprite))

    def get_damage(self):
        """
        default amount of damage is zero. can be overridden.
        :return: amount of damage
        """
        return 0



class FireStatus(StatusSprite):
    """
    class for fire status effect
    """
    def __init__(self, victim):
        image = load_image('fire_status.png', 'fire')
        StatusSprite.__init__(self, victim, image, 10, 2)
        self.add(hazards)

    def get_damage(self):
        return 2


class PauseStatus(StatusSprite):
    """
    class for causing a sprite to pause temporarily
    """
    def __init__(self, victim, pause_length):
        image = load_image('blank.png')
        StatusSprite.__init__(self, victim, image, pause_length, 0)

    def get_damage(self):
        return 0

class IceStatus(StatusSprite):
    def __init__(self, victim):
        image = load_image('ice_status.png', 'ice')
        StatusSprite.__init__(self, victim, image, 40, 1)