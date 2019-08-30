# Spaceship

import simplegui
import math
import random

#================================================
# globals for user interface
WIDTH = 800
HEIGHT = 600
FRAMES_PER_SEC = 60
INFO_UPDATE = FRAMES_PER_SEC / 8
INFO_POS = [WIDTH / 8, 5 * HEIGHT / 6]
INFO_LENGTH = 45

# reaction constants (taken from example / template)
ANGLE_STEPS = math.pi * 1.5
ACCEL_STEPS = 0.10
FRIC_STEPS = 0.99

#================================================
# game play constants
ROTATE_STEPS = 2 * math.pi
VELOCITY_RANGE = FRAMES_PER_SEC

MAX_ROCK_SPEED = 7
MAX_ROCKS_ALLOWED = 12
MAX_NOF_LIVES = 5

DFT_MISSILE_SPEED = 1.0 * MAX_ROCK_SPEED
DEFAULT_NOF_LIVES = 3

INSTRUCTIONS = "CONTROLS:              <Left Arrow> turns left                          <Right Arrow> turns right                        <Up Arrow> accelerates forward                   <Space> fires a missile                          High Score: "

#================================================
# game states
current_rock_speed = 1
missile_speed = DFT_MISSILE_SPEED

score = 0
high_score = 0
lives = 3
time = 0
started = False
level = 0
level_up_score = MAX_ROCKS_ALLOWED

ticker = 0
display_pos = 0

#================================================
# image data
class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.f2014.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_info_tiny = ImageInfo([45, 45], [90, 90], 12)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_info_small = ImageInfo([45, 45], [90, 90], 20)
asteroid_info_tiny = ImageInfo([45, 45], [90, 90], 10)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 64, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

#====================================================
# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)

#====================================================
# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        
    def draw(self,canvas):
        draw_size = [self.radius * 2, self.radius * 2]
        image_center = list(self.image_center)
        if self.thrust:
            image_center[0] += self.image_size[0]
            
        canvas.draw_image(self.image, 
                          image_center, 
                          self.image_size, 
                          self.pos, 
                          draw_size, 
                          self.angle
                         )
            
    def get_pos(self):
        return self.pos
    
    def get_vel(self):
        return self.vel
    
    def get_radius(self):
        return self.radius
    
    def rotates(self, angle_vel):
        self.angle_vel += angle_vel
        
    def accelerates(self, acceleration):
        if acceleration > 0:
            if self.thrust == False:
                ship_thrust_sound.rewind()
                ship_thrust_sound.play()
                
            self.thrust = True
        else:
            self.thrust = False
            ship_thrust_sound.pause()
            
        
    def shoot(self):
        global missile_group
        
        vel0 = angle_to_vector(self.angle)
        pos0 = angle_to_vector(self.angle)
        x = int(pos0[0] * ship_info.get_radius()) + self.pos[0]
        y = int(pos0[1] * ship_info.get_radius()) + self.pos[1]
        dx = int(vel0[0] * missile_speed) + self.vel[0]
        dy = int(vel0[1] * missile_speed) + self.vel[1]
        
        a_missile = Sprite([x,y],
                           [dx,dy],
                           0,
                           0,
                           missile_image,
                           missile_info,
                           missile_sound
                          )
        missile_group.add(a_missile)
    
    def update(self):
        # orientation update
        self.angle += self.angle_vel / float(FRAMES_PER_SEC)
        self.angle %= (2 * math.pi)
        
        # horizontal update and wrap
        self.pos[0] += self.vel[0]
        self.pos[0] %= WIDTH
        
        #vertical update and wrap
        self.pos[1] += self.vel[1]
        self.pos[1] %= HEIGHT
        
        # apply friction (negative acceleration) to velocity to slow down
        self.vel[0] *= FRIC_STEPS #/ float(FRAMES_PER_SEC)
        self.vel[1] *= FRIC_STEPS #/ float(FRAMES_PER_SEC)
        
        # apply acceleration to speed up
        if self.thrust:
            forward_vector = angle_to_vector(self.angle)
            self.vel[0] += ACCEL_STEPS * forward_vector[0]
            self.vel[1] += ACCEL_STEPS * forward_vector[1]
        
    
#=====================================================
# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()
        
    def get_radius(self):
        return self.radius
    
    def get_pos(self):
        return self.pos
    
    def get_vel(self):
        return self.vel
    
    def draw(self, canvas):
        draw_size = [self.radius * 2, self.radius * 2]
        anim_center = list(self.image_center)
        if self.animated:
            anim_center[0] += self.age * self.image_size[0]
        canvas.draw_image(self.image, 
                          anim_center, 
                          self.image_size, 
                          self.pos, 
                          draw_size, 
                          self.angle)
    
    def collide(self, another_object):
        brush_distance = self.radius + another_object.get_radius()
        another_object_pos = another_object.get_pos()
        return (brush_distance > dist(self.pos, another_object_pos))
    
    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.pos[0] %= WIDTH
        self.pos[1] %= HEIGHT
        
        self.angle += self.angle_vel / math.pi
        
        self.age += 1
        
        return self.age >= self.lifespan
        
#=============================================================
# helper: display info
def show_instructions(canvas):
    global ticker, display_pos
    
    string1 = INSTRUCTIONS + str(high_score)
    source_string = string1.rjust(INFO_LENGTH + len(string1), ' ')
    ticker += 1
    if ticker > INFO_UPDATE:
        ticker = 0
        display_pos += 1
        display_pos %= len(source_string)
    display_string = ""
    display_offset = display_pos
    for i in range(INFO_LENGTH):
        display_string += source_string[display_offset]
        display_offset += 1
        display_offset %= len(source_string)
    canvas.draw_text(display_string, INFO_POS, 24, "Yellow", "monospace")
            
# helper: create a list of levels
def add_level():
    global level, level_group
    rock_size = asteroid_info_tiny.get_radius() * 2
    level += 1
    offset = (level * rock_size) + (rock_size / 2)
    level_rock = Sprite([offset, HEIGHT - 1.5 * rock_size], 
                        [0,0], 
                        0, 
                        math.pi / 120, 
                        asteroid_image, 
                        asteroid_info_tiny
                       )
    level_group.append(level_rock)

#---------------------------------------------------------
# helper: create a list of lives
def add_live():
    global lives, lives_group
    if MAX_NOF_LIVES > lives:
        offset = 100 + lives * ship_info_tiny.get_radius() * 2
        live_ship = Ship([offset, 18], [0,0], 3 * math.pi / 2, ship_image, ship_info_tiny)
        lives_group.append(live_ship)
        lives += 1

#---------------------------------------------------------
# helper: start new game - reset all game states
def start_new_game():
    global started
    global level, level_group
    global score, upgrade_score
    global lives, lives_group
    global my_ship, missile_speed
    global rocks_been_around
    
    # start slow
    level = 0
    level_group = []
    add_level()
    
    # clear score
    score = 0
    
    # next point it gets harder
    upgrade_score = MAX_ROCKS_ALLOWED
    
    # can we do somethong special yet ?
    rocks_been_around = False
    
    # start the background music up
    soundtrack.rewind()
    soundtrack.play()
    
    # reset the player ship to the center of the screen
    my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
    missile_speed = DFT_MISSILE_SPEED
    
    # set number of lives and draw the number of lives
    lives = 0
    lives_group = []
    for i in range(DEFAULT_NOF_LIVES):
        add_live()
        
    # game on
    started = True
    
#---------------------------------------------------------
# helper: handle sprite group (draw and update)
def process_sprite_group(canvas, sprite_group):
    # copy the group so we can iterate over the non-mutating copy
    copy_group = set(sprite_group)
    # iterate over the non-mutating copy
    for sprite in copy_group:
        # draw the sprite
        sprite.draw(canvas)
        # do an update, and be ready to remove it from the set
        if sprite.update():
            # sprite aged beyond lifetime, remove from original set
            sprite_group.remove(sprite)

#---------------------------------------------------------
# helper: create an explosion sprite with the properties of the passed sprite
def new_explosion(sprite_info):
    global explosion_group
    
    # where must explosion start
    pos = sprite_info.get_pos()
    # in which direction must explosion travel
    vel = sprite_info.get_vel()
    # create an explosion sprite
    expl = Sprite(pos, vel, 0, 0, explosion_image, explosion_info, explosion_sound)
    # add this explosion to a set of explosion to do
    explosion_group.add(expl)
    
#---------------------------------------------------------
# helper: detect first collision between a group and an object
def group_collide(sprite_group, an_object):
    # make a copy we can iterate over
    copy_group = sprite_group.copy()
    # initially we had no collisions
    collided = False
    # index to iterate with
    sprite_index = 0
    # check each sprite in the group until collision
    while (0 < len(copy_group)) and not collided:
        sprite = copy_group.pop()
        # collision with the object ?
        if sprite.collide(an_object):
            # collisions = explosions
            new_explosion(sprite)
            # and remove the sprite object from the original set
            sprite_group.discard(sprite)
            # and we had at least one collision from the set
            collided = True
    # report to the caller if any of the set collided with the object
    return collided

#---------------------------------------------------------
# helper: check if any of group1 collided with any of group2
def group_group_collide(sprite_group1, sprite_group2):
    # make a copy of group1 so we can iterate over the non-mutating copy
    copy_group1 = sprite_group1.copy()
    # the number of collisions is none yet
    number_of_collides = 0
    # iterate over each item in set 1
    for sprite in copy_group1:
        # Check if set 2 collided with this item/object
        if group_collide(sprite_group2, sprite):
            # oh it did ! one more collision to the total
            number_of_collides += 1
            # remove this item/object from the original set 1
            sprite_group1.remove(sprite)
    # report the number of collisions to the caller
    return number_of_collides

#---------------------------------------------------------
# helper: calculate rock_x
def put_rock_on_horizontal_edge(dir_vect):
    # find rock size
    rock_radius = asteroid_info.get_radius()
    # determine the unfairness of the spawn
    if 4 > level:
        limit = 5 - level
    else:
        limit = 2
    # where is ship at
    pos = my_ship.get_pos()
    # if rock is not moving left
    if dir_vect[0] >= 0:
        # get position between left edge of screen ..
        x1 = 0
        # .. and somewhere halfway to the ship
        x2 = int(pos[0] / 2)
        # if ship is too close to where the rock will launch, switch to other half
        if x1 >= x2 - rock_radius:
            x1 = int((WIDTH + pos[0]) / 2)
            x2 = WIDTH
    # else moving left ...
    else:
        # get position from midway between ship and right edge of the screen ..
        x1 = int((pos[0] + WIDTH) / 2)
        # .. to right edge of the screen
        x2 = WIDTH
        # if the ship is too close to where rock may spawn, switch to other half
        if x1 >= x2 - rock_radius:
            x1 = 0
            x2 = int(pos[0] / 2)
    
    x_start = random.randrange(x1, x2)
    
    # if moving down
    if dir_vect[1] > 0:
        # start at top edge
        y_start = 0
        # if ship too close to top edge, switch starting edge
        if pos[1] < (limit * rock_radius):
            y_start = HEIGHT
    # if moving up
    else:
        # start at bottom edge
        y_start = HEIGHT
        # if ship too close to bottom edge, switch starting edge
        if pos[1] < (limit * rock_radius):
            y_start = HEIGHT
    
    return [x_start, y_start]

#---------------------------------------------------------
# helper: calculate rock_y
def put_rock_on_vertical_edge(dir_vect):
    # find rock size
    rock_radius = asteroid_info.get_radius()
    # where is ship at
    pos = my_ship.get_pos()
    # determine the unfairness of the spawn
    if 4 > level:
        limit = 5 - level
    else:
        limit = 2
    # if not moving up
    if dir_vect[1] >= 0:
        # get a position between top edge of screen ..
        y1 = 0
        # .. and halfway to ship
        y2 = int(pos[1] / 2)
        # if ship too close to where rock may spawn, switch to other side
        if y1 >= y2 - rock_radius:
            y1 = int(pos[1] / 2)
            y2 = HEIGHT
    # else moving up ...
    else:
        # get a position between bottom edge of screen ..
        y2 = HEIGHT
        # .. and halfway to ship
        y1 = int((HEIGHT + pos[1]) / 2)
        # if ship too close to wher rock may spawn, switch to the other side
        if y1 >= y2 - rock_radius:
            y1 = 0
            y2 = int((HEIGHT + pos[1]) / 2)
    
    y_start = random.randrange(y1, y2)
    
    # if moving right
    if dir_vect[0] > 0:
        # start on left edge
        x_start = 0
        # if ship too close to leet edge, switch starting edge
        if pos[0] < (limit * rock_radius):
            x_start = WIDTH
    # else moving left
    else:
        # start on right edge
        x_start = WIDTH
        # if ship too close to right edge, switch starting edge
        if pos[0] > (WIDTH - (limit * rock_radius)):
            x_start = 0
    
    return [x_start, y_start]

#---------------------------------------------------------
# helper: get random velocity in direction given
def get_rock_velocity(dir_vect):
    # level determine the ferociousness of the rocks
    current_rock_speed = level
    # but limit it to some semi-sane values
    if MAX_ROCK_SPEED < current_rock_speed:
        current_rock_speed = MAX_ROCK_SPEED
    # if it gets harder, no pulling punches ! rocks are FLYING everywhere
    min_rock_speed = (level / MAX_ROCKS_ALLOWED) + 1
    # if no range to select from, select hardest option in the world
    if current_rock_speed <= min_rock_speed:
        vel = current_rock_speed
    # else pick from the range we calculated
    else:
        vel = random.randrange(1, 10 * current_rock_speed) / 10.0
    # set the rock velocity, and return the vector to the caller
    init_vel = [vel * dir_vect[0], vel * dir_vect[1]]
    return init_vel

#=======================================================
# handlers
# timer handler that spawns a rock    
def rock_spawner():
    global rock_group
    global missile_speed
    global score
    
    # can only create rocks if game is on
    if started:
        # is there room for another rock on screen ?
        if len(rock_group) < MAX_ROCKS_ALLOWED:
            # start rock travelling in a random direction
            dir_angle = math.pi * 2 * random.random()
            # get a vector to calculate the speed and starting positions
            dir_vect = angle_to_vector(dir_angle)
            # if travelling (mostly) horizontally, start on a vertical edge
            if dir_vect[0] >= dir_vect[1]:
                rock_pos = put_rock_on_vertical_edge(dir_vect)
            # travelling (mostly) vertically, start on a horizontal edge
            else:
                rock_pos = put_rock_on_horizontal_edge(dir_vect)
            # calculate a rock velocity according to the current level
            rock_vel = get_rock_velocity(dir_vect)
            # pick a random spin value
            rotation = random.random() * math.pi * 2 / FRAMES_PER_SEC
            # higher levels create smaller rocks (is this harder or not ?)
            if level > (MAX_ROCKS_ALLOWED * 2):
                info = asteroid_info_tiny
            elif level > MAX_ROCKS_ALLOWED:
                info = asteroid_info_small
            else:
                info = asteroid_info
            # create a rock from those properties
            rock = Sprite(rock_pos, 
                          rock_vel, 
                          dir_angle, 
                          rotation, 
                          asteroid_image, 
                          info
                         )
            # and put the rock into our rock set
            rock_group.add(rock)

#---------------------------------------------------------
# handler: key is down
def key_pressed(key):
    # left key starts turning ship left
    if key == simplegui.KEY_MAP['left']:
        my_ship.rotates(-ANGLE_STEPS)
    # right key starts turning ship right
    if key == simplegui.KEY_MAP['right']:
        my_ship.rotates(ANGLE_STEPS)
    # up key moves ship forward
    if key == simplegui.KEY_MAP['up']:
        my_ship.accelerates(ACCEL_STEPS)
    # space key fires another missile
    if key == simplegui.KEY_MAP['space']:
        my_ship.shoot()

#---------------------------------------------------------
# handler: key is up
def key_released(key):
    # left key is not pressed, stop turning left
    if key == simplegui.KEY_MAP['left']:
        my_ship.rotates(ANGLE_STEPS)
    # right key is not pressed, stop turning right
    if key == simplegui.KEY_MAP['right']:
        my_ship.rotates(-ANGLE_STEPS)
    # up key is not pressed, we are not accelerating any more
    if key == simplegui.KEY_MAP['up']:
        my_ship.accelerates(0)

#---------------------------------------------------------
# handler: mouse clicked
def click(pos):
    # if not in game
    if not started:
        # determine where the splash screen is
        splash_size = splash_info.get_size()
        splash_left = (WIDTH - splash_size[0]) / 2
        splash_right = (WIDTH + splash_size[0]) / 2
        splash_top = (HEIGHT - splash_size[1]) / 2
        splash_bottom = (HEIGHT + splash_size[1]) / 2
        # check if we clicked inside splash screen
        in_h = (pos[0] < splash_right) and (pos[0] > splash_left)
        in_v = (pos[1] < splash_bottom) and (pos[1] > splash_top)
        # if we clicked in splash screen, start a game
        if in_h and in_v:
            start_new_game()
    
#---------------------------------------------------------
# handler: draw routine
def draw(canvas):
    global time
    global rock_group
    global missile_group
    global lives, lives_group
    global score, high_score
    global level, level_up_score
    global started, display_pos
    global rocks_been_around, missile_speed
    global upgrade_score
    
    # animiate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    # draw ship
    my_ship.draw(canvas)
    # update ship
    my_ship.update()
    # draw and update rock sprites
    process_sprite_group(canvas, rock_group)
    # draw and update missile sprites
    process_sprite_group(canvas, missile_group)
    # draw and update explosion sprites
    process_sprite_group(canvas, explosion_group)
    
    # if in game ..
    if started:
        # if there have spawned any rocks, we are ready to level up
        if len(rock_group) > 0:
            rocks_been_around = True
        # count the many rocks that collided with our missiles
        score += group_group_collide(rock_group, missile_group)
        if score > level_up_score:
            add_level()
            level_up_score += MAX_ROCKS_ALLOWED
        if score > high_score:
            high_score = score
        # if all rocks already destroyed, appreciate bad-assness with level-up
        if rocks_been_around and (len(rock_group) < 1):
            rocks_been_around = False
            add_live()
            add_level()
            level_up_score = score + MAX_ROCKS_ALLOWED
        # if rocks bounced on ship ..
        if group_collide(rock_group, my_ship):
            # ship shows a bit of explosion
            new_explosion(my_ship)
            # lose a life
            lives -= 1
            lives_group.pop(-1)
            # game over already ?
            if 0 == lives:
                # stop game
                started = 0
                display_pos = 0
                # remove the rocks flying all over
                copy_group = set(rock_group)
                rock_group.symmetric_difference_update(copy_group)
                # stop the music
                soundtrack.pause()
    # if not in game
    else:
        # show splash screen
        canvas.draw_image(splash_image,
                          splash_info.get_center(),
                          splash_info.get_size(),
                          [WIDTH / 2, HEIGHT / 2],
                          splash_info.get_size())
        # show some instructions for play ...
        show_instructions(canvas)
        
    # draw level group
    if 0 < len(level_group):
        process_sprite_group(canvas, level_group)
        
    # draw user interface
    lives_string = "Lives: "
    canvas.draw_text(lives_string, ( 24, 24), 24, "Yellow")
    process_sprite_group(canvas, lives_group)
    # draw the score in the upper right corner
    value_string = str(score).rjust(5, '0')
    score_string = "Score: " + value_string
    score_x = WIDTH - 24 - frame.get_canvas_textwidth(score_string, 24)
    canvas.draw_text(score_string, ( score_x, 24), 24, "Yellow")
    

#==========================================================
# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship and sprite groups
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
rock_group = set([])
missile_group = set([])
explosion_group = set([])
lives_group = []
level_group = []

# register handlers
frame.set_draw_handler(draw)
frame.set_keydown_handler(key_pressed)
frame.set_keyup_handler(key_released)
frame.set_mouseclick_handler(click)

timer = simplegui.create_timer(1000.0, rock_spawner)

#==========================================================
# get things rolling
timer.start()
frame.start()

