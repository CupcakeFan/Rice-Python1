# Spaceship

import simplegui
import math
import random

#================================================
# globals for user interface
WIDTH = 800
HEIGHT = 600
FRAMES_PER_SEC = 60

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

DFT_MISSILE_SPEED = 1.0 * MAX_ROCK_SPEED

#================================================
# game states
current_rock_speed = 1
missile_speed = DFT_MISSILE_SPEED

score = 0
lives = 3
time = 0
started = False

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
        self.angle_vel = angle_vel
        
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
# helper: create a list of lives
def add_live():
    global lives, lives_group
    if 5 > lives:
        offset = 100 + lives * ship_info_tiny.get_radius() * 2
        live_ship = Ship([offset, 18], [0,0], 3 * math.pi / 2, ship_image, ship_info_tiny)
        lives_group.append(live_ship)
        lives += 1

# helper: start new game - reset all game states
def start_new_game():
    global started
    global score, upgrade_score
    global lives, lives_group
    global my_ship, missile_speed
    global rocks_rolling
    
    started = True
    score = 0
    upgrade_score = 2 * MAX_ROCKS_ALLOWED
    rocks_rolling = False
    lives = 0
    lives_group = []
    soundtrack.rewind()
    soundtrack.play()
    my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
    missile_speed = DFT_MISSILE_SPEED
    for i in range(3):
        add_live()
    
# helper: handle sprite group (draw and update)
def process_sprite_group(canvas, sprite_group):
    copy_group = set(sprite_group)
    for sprite in copy_group:
        sprite.draw(canvas)
        if sprite.update():
            sprite_group.remove(sprite)

# helper: create an explosion sprite with the properties of the passed sprite
def new_explosion(sprite_info):
    global explosion_group
    
    pos = sprite_info.get_pos()
    vel = sprite_info.get_vel()
    expl = Sprite(pos, vel, 0, 0, explosion_image, explosion_info, explosion_sound)
    explosion_group.add(expl)
    
# helper: detect collision between a group and an object
def group_collide(sprite_group, an_object):
    copy_group = set(sprite_group)
    collided = False
    for sprite in copy_group:
        if sprite.collide(an_object):
            new_explosion(sprite)
            sprite_group.remove(sprite)
            collided = True
    return collided

def group_group_collide(sprite_group1, sprite_group2):
    copy_group1 = set(sprite_group1)
    number_of_collides = 0
    for sprite in copy_group1:
        if group_collide(sprite_group2, sprite):
            number_of_collides += 1
            sprite_group1.remove(sprite)
    return number_of_collides

# helper: calculate rock_x
def put_rock_on_horizontal_edge(dir_vect):
    rock_radius = asteroid_info.get_radius()
    
    # where is ship
    pos1 = my_ship.get_pos()
    
    # if moving to right (or not)
    if dir_vect[0] >= 0:
        # get position in left section of screen
        x1 = 0
        x2 = int(pos1[0] / 2)
        if x1 >= x2 - rock_radius:
            x2 = x1 + 2 * rock_radius
    # else moving left ...
    else:
        # get position in right section of the screen
        x1 = int((pos1[0] + WIDTH) / 2)
        x2 = WIDTH
        if x1 >= x2 - rock_radius:
            x1 = x2 - 2 * rock_radius
    
    x_start = random.randrange(x1, x2)
    
    # if moving down
    if dir_vect[1] > 0:
        # start at top edge
        y_start = 0
    # if moving up
    else:
        # start at bottom edge
        y_start = HEIGHT
    
    return [x_start, y_start]

# helper: calculate rock_y
def put_rock_on_vertical_edge(dir_vect):
    rock_radius = asteroid_info.get_radius()
    
    # where is ship
    pos1 = my_ship.get_pos()
    
    # if moving to down (or not)
    if dir_vect[1] >= 0:
        # get a position in top section of screen
        y1 = 0
        y2 = int(pos1[1] / 2)
        if y1 >= y2 - rock_radius:
            y2 = y1 + 2 * rock_radius
    # else moving up ...
    else:
        # get a position in bottom section of screen
        y1 = int((pos1[1] + HEIGHT) / 2)
        y2 = HEIGHT
        if y1 >= y2 - rock_radius:
            y1 = y2 - 2 * rock_radius
    
    y_start = random.randrange(y1, y2)
    
    # if moving right
    if dir_vect[0] > 0:
        # start on left edge
        x_start = 0
    # else moving left
    else:
        # start on right edge
        x_start = WIDTH
    
    return [x_start, y_start]

# helper: get random velocity in direction given
def get_rock_velocity(dir_vect):
    current_rock_speed = (score / MAX_ROCKS_ALLOWED) + 1
    if MAX_ROCK_SPEED < current_rock_speed:
        current_rock_speed = MAX_ROCK_SPEED
    min_rock_speed = ((score / MAX_ROCKS_ALLOWED) / MAX_ROCKS_ALLOWED) + 1
    if current_rock_speed <= min_rock_speed:
        vel = current_rock_speed
    else:
        vel = random.randrange(1, 10 * current_rock_speed) / 10.0
    init_vel = [vel * dir_vect[0], vel * dir_vect[1]]
    
    return init_vel

#=======================================================
# handlers
# timer handler that spawns a rock    
def rock_spawner():
    global rock_group
    global missile_speed
    global score
    
    if started:
        if len(rock_group) < MAX_ROCKS_ALLOWED:
            dir_angle = math.pi * 2 * random.random()
            dir_vect = angle_to_vector(dir_angle)
            if dir_vect[0] >= dir_vect[1]:
                rock_pos = put_rock_on_vertical_edge(dir_vect)
            else:
                rock_pos = put_rock_on_horizontal_edge(dir_vect)
            
            rock_vel = get_rock_velocity(dir_vect)
            rotation = random.random() * math.pi * 2 / FRAMES_PER_SEC
            rock = Sprite(rock_pos, 
                          rock_vel, 
                          dir_angle, 
                          rotation, 
                          asteroid_image, 
                          asteroid_info
                         )
            rock_group.add(rock)

def key_pressed(key):
    if key == simplegui.KEY_MAP['left']:
        my_ship.rotates(-ANGLE_STEPS)
    if key == simplegui.KEY_MAP['right']:
        my_ship.rotates(ANGLE_STEPS)
    if key == simplegui.KEY_MAP['up']:
        my_ship.accelerates(ACCEL_STEPS)
    if key == simplegui.KEY_MAP['space']:
        my_ship.shoot()

def key_released(key):
    if key == simplegui.KEY_MAP['left']:
        my_ship.rotates(0)
    if key == simplegui.KEY_MAP['right']:
        my_ship.rotates(0)
    if key == simplegui.KEY_MAP['up']:
        my_ship.accelerates(0)

def click(pos):
    if not started:
        splash_size = splash_info.get_size()
        splash_left = (WIDTH - splash_size[0]) / 2
        splash_right = (WIDTH + splash_size[0]) / 2
        splash_top = (HEIGHT - splash_size[1]) / 2
        splash_bottom = (HEIGHT + splash_size[1]) / 2
        
        in_h = (pos[0] < splash_right) and (pos[0] > splash_left)
        in_v = (pos[1] < splash_bottom) and (pos[1] > splash_top)
        
        if in_h and in_v:
            start_new_game()
    
def draw(canvas):
    global time
    global rock_group
    global missile_group
    global lives, lives_group
    global score
    global started
    global rocks_rolling, missile_speed
    global upgrade_score
    
    # animiate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    # draw ship and sprites
    my_ship.draw(canvas)
    # update ship and sprites
    my_ship.update()
    process_sprite_group(canvas, rock_group)
    process_sprite_group(canvas, missile_group)
    process_sprite_group(canvas, explosion_group)
    
    if not started:
        canvas.draw_image(splash_image,
                          splash_info.get_center(),
                          splash_info.get_size(),
                          [WIDTH / 2, HEIGHT / 2],
                          splash_info.get_size())
    else:
        score += group_group_collide(missile_group, rock_group)
        if len(rock_group) > 0:
            rocks_rolling = True
        if rocks_rolling and (len(rock_group) < 1):
            rocks_rolling = False
            missile_speed -= 1
            bonus = score / 12 * 12
            if bonus < 24:
                bonus = 24
            score += bonus
            add_live()
            
        if (score > upgrade_score):
            add_live()
            upgrade_score = 2 * upgrade_score
            
        if group_collide(rock_group, my_ship):
            lives -= 1
            lives_group.pop(-1)
            if 0 == lives:
                started = 0
                copy_group = set(rock_group)
                rock_group.symmetric_difference_update(copy_group)
                soundtrack.pause()
    
    # draw user interface
    lives_string = "Lives: "
    canvas.draw_text(lives_string, ( 24, 24), 24, "Yellow")
    process_sprite_group(canvas, lives_group)
    
    value_string = str(score).rjust(5, '0')
    score_string = "Score: " + value_string
    score_x = WIDTH - 24 - frame.get_canvas_textwidth(score_string, 24)
    canvas.draw_text(score_string, ( score_x, 24), 24, "Yellow")
    

#==========================================================
# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship and two sprites
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
rock_group = set([])
missile_group = set([])
explosion_group = set([])
lives_group = []

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
