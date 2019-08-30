# Spaceship

import simplegui
import math
import random

#================================================
# globals for user interface
WIDTH = 800
HEIGHT = 600
FRAMES_PER_SEC = 60
ANGLE_STEPS = math.pi
ACCEL_STEPS = 7
#FRIC_STEPS = FRAMES_PER_SEC - ACCEL_STEPS
FRIC_STEPS = FRAMES_PER_SEC - (ACCEL_STEPS - 2)

#================================================
# game play constants
ROTATE_STEPS = 2 * math.pi
VELOCITY_RANGE = FRAMES_PER_SEC

DEFAULT_ROCK_SPEED = 7

MISSILE_SPEED = 2 * DEFAULT_ROCK_SPEED

#================================================
# game states
my_ship_rotates = 0
my_ship_accelerates = 0

max_rock_speed = DEFAULT_ROCK_SPEED

score = 0
lives = 3
time = 0

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
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
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
        #canvas.draw_circle(self.pos, self.radius, 1, "White", "White")
        if self.thrust:
            image_center = (self.image_center[0] + self.image_size[0], self.image_center[1])
            canvas.draw_image(self.image, image_center, self.image_size, self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)
            
    def get_pos(self):
        return self.pos
    
    def get_vel(self):
        return self.vel
    
    def shoot(self):
        global a_missile
        
        vel0 = angle_to_vector(self.angle)
        pos0 = angle_to_vector(self.angle)
        x = int(pos0[0] * ship_info.get_radius()) + self.pos[0]
        y = int(pos0[1] * ship_info.get_radius()) + self.pos[1]
        dx = int(vel0[0] * MISSILE_SPEED) + self.vel[0]
        dy = int(vel0[1] * MISSILE_SPEED) + self.vel[1]
        
        a_missile = Sprite([x,y],[dx,dy],0,0,missile_image,missile_info,missile_sound)
    
    def update(self, rotate, accelerate):
        self.angle += rotate / float(FRAMES_PER_SEC)
        self.angle %= (2 * math.pi)
        
        self.angle_vel += accelerate / float(FRAMES_PER_SEC)
        if accelerate > 0:
            if self.thrust == False:
                ship_thrust_sound.play()
                
            self.thrust = True
            velocity_vector = angle_to_vector(self.angle)
            self.vel[0] += self.angle_vel * velocity_vector[0]
            self.vel[1] += self.angle_vel * velocity_vector[1]
        else:
            self.thrust = False
            ship_thrust_sound.rewind()
            
        self.angle_vel *= FRIC_STEPS / float(FRAMES_PER_SEC)
        
        self.vel[0] *= FRIC_STEPS / float(FRAMES_PER_SEC)
        self.vel[1] *= FRIC_STEPS / float(FRAMES_PER_SEC)
        
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.pos[0] %= WIDTH
        self.pos[1] %= HEIGHT
        
        #print self.vel, self.angle_vel
    
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
   
    def draw(self, canvas):
        #canvas.draw_circle(self.pos, self.radius, 1, "Red", "Red")
        canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)
    
    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.pos[0] %= WIDTH
        self.pos[1] %= HEIGHT
        
        self.angle += self.angle_vel / math.pi
        
#=============================================================
# helper: calculate rock_x
def put_rock_on_horizontal_edge(dir_vect):
    rock_radius = asteroid_info.get_radius()
    
    # where is ship
    pos1 = my_ship.get_pos()
    
    # if moving to right (or not)
    if dir_vect[0] >= 0:
        # get position in left section of screen
        x1 = rock_radius
        x2 = int(pos1[0] / 2)
        if x1 >= x2 - rock_radius:
            x2 = x1 + 2 * rock_radius
    # else moving left ...
    else:
        # get position in right section of the screen
        x1 = int((pos1[0] + WIDTH) / 2)
        x2 = WIDTH - rock_radius
        if x1 >= x2 - rock_radius:
            x1 = x2 - 2 * rock_radius
    
    x_start = random.randrange(x1, x2)
    
    # if moving down
    if dir_vect[1] > 0:
        # start at top edge
        y_start = rock_radius
    # if moving up
    else:
        # start at bottom edge
        y_start = HEIGHT - rock_radius
    
    return [x_start, y_start]

# helper: calculate rock_y
def put_rock_on_vertical_edge(dir_vect):
    rock_radius = asteroid_info.get_radius()
    
    # where is ship
    pos1 = my_ship.get_pos()
    
    # if moving to down (or not)
    if dir_vect[1] >= 0:
        # get a position in top section of screen
        y1 = rock_radius
        y2 = int(pos1[1] / 2)
        if y1 >= y2 - rock_radius:
            y2 = y1 + 2 * rock_radius
    # else moving up ...
    else:
        # get a position in bottom section of screen
        y1 = int((pos1[1] + HEIGHT) / 2)
        y2 = HEIGHT - rock_radius
        if y1 >= y2 - rock_radius:
            y1 = y2 - 2 * rock_radius
    
    y_start = random.randrange(y1, y2)
    
    # if moving right
    if dir_vect[0] > 0:
        # start on left edge
        x_start = rock_radius
    # else moving left
    else:
        # start on right edge
        x_start = WIDTH - rock_radius
    
    return [x_start, y_start]

# helper: get random velocity in direction given
def get_rock_velocity(dir_vect):
    vel = random.randrange(1, max_rock_speed)
    init_vel = [vel * dir_vect[0], vel * dir_vect[1]]
    
    return init_vel

#=======================================================
# handlers
# timer handler that spawns a rock    
def rock_spawner():
    global a_rock
    
    dir_angle = math.pi * 2 * random.random()
    dir_vect = angle_to_vector(dir_angle)
    if dir_vect[0] >= dir_vect[1]:
        rock_pos = put_rock_on_vertical_edge(dir_vect)
    else:
        rock_pos = put_rock_on_horizontal_edge(dir_vect)
        
    rock_vel = get_rock_velocity(dir_vect) #random.randrange(1, 10)
    rotation = random.random() * math.pi * 2 / FRAMES_PER_SEC
    a_rock = Sprite(rock_pos, rock_vel, dir_angle, rotation, asteroid_image, asteroid_info)

def key_pressed(key):
    global my_ship_rotates, my_ship_accelerates
    if key == simplegui.KEY_MAP['left']:
        my_ship_rotates = -ANGLE_STEPS
    if key == simplegui.KEY_MAP['right']:
        my_ship_rotates = ANGLE_STEPS
    if key == simplegui.KEY_MAP['up']:
        my_ship_accelerates = ACCEL_STEPS
    if key == simplegui.KEY_MAP['space']:
        my_ship.shoot()

def key_released(key):
    global my_ship_rotates, my_ship_accelerates
    if key == simplegui.KEY_MAP['left']:
        my_ship_rotates = 0
    if key == simplegui.KEY_MAP['right']:
        my_ship_rotates = 0
    if key == simplegui.KEY_MAP['up']:
        my_ship_accelerates = 0

def draw(canvas):
    global time
    
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
    a_rock.draw(canvas)
    a_missile.draw(canvas)
    
    # update ship and sprites
    my_ship.update(my_ship_rotates, my_ship_accelerates)
    a_rock.update()
    a_missile.update()
    
    # draw user interface
    score_string = "Score: " + str(score)
    canvas.draw_text(score_string, ( 24, 24), 24, "Yellow")
    lives_string = "Lives: " + str(lives)
    lives_x = WIDTH - 24 - frame.get_canvas_textwidth(lives_string, 24)
    canvas.draw_text(lives_string, ( lives_x, 24), 24, "Yellow")

#==========================================================
# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship and two sprites
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
rock_spawner()
a_missile = Sprite([-missile_info.get_radius(), -missile_info.get_radius()], [0,0], 0, 0, missile_image, missile_info, missile_sound)

# register handlers
frame.set_draw_handler(draw)
frame.set_keydown_handler(key_pressed)
frame.set_keyup_handler(key_released)

timer = simplegui.create_timer(1000.0, rock_spawner)

#==========================================================
# get things rolling
timer.start()
frame.start()

