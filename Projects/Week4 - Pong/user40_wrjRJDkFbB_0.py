# Implementation of classic arcade game Pong

import simplegui
import random

# initialize globals - pos and vel encode vertical info for paddles
# canvas size (playfield)
WIDTH = 600
HEIGHT = 400

# ball size
BALL_RADIUS = 20

# paddle dimensions
PAD_WIDTH = 8
PAD_HEIGHT = 80
HALF_PAD_WIDTH = PAD_WIDTH / 2
HALF_PAD_HEIGHT = PAD_HEIGHT / 2

#default paddle speed: cover top-to-bottom move in the time ball moves between mid-line and gutter
PADDLE_START_SPEED = 240 * (HEIGHT - PAD_HEIGHT) / (WIDTH / 2 - PAD_WIDTH - BALL_RADIUS)

# ball directions
LEFT = False
RIGHT = True

# ball position and velocity
ball_pos = [WIDTH / 2, HEIGHT / 2]
ball_vel = [-5, -1]

# left paddle position and velocity
paddleL_pos = [0, HEIGHT / 2]
paddleL_vel = [0, 0]

# right paddle position and velocity
paddleR_pos = [WIDTH - PAD_WIDTH - 1, HEIGHT / 2]
paddleR_vel = [0, 0]

paddle_speed = PADDLE_START_SPEED

# left player score
scoreL = 0

# right player score
scoreR = 0

# initialize ball_pos and ball_vel for new bal in middle of table
# if direction is RIGHT, the ball's velocity is upper right, else upper left
def spawn_ball(direction):
    global ball_pos, ball_vel # these are vectors stored as lists
    global paddle_speed
    
    # pick a random position on midline from center half of playfield width
    y = random.randrange(HEIGHT / 4, HEIGHT * 3 / 4)
    ball_pos[1] = y
    # set start position on midline horizontally
    ball_pos[0] = WIDTH / 2
    
    # set the horizontal speedvector in the range 120-240 pixels/second to start with
    dx = random.randrange(120, 241)
    if direction == LEFT:
        ball_vel[0] = -dx
    else:
        ball_vel[0] = dx
    
    # set the vertical speedvector in the range 60-180 pixels/second to start with
    dy = random.randrange(60, 181)
    ball_vel[1] = -dy
    
    paddle_speed = PADDLE_START_SPEED

def ball_collides_with_paddle(paddle_pos):
    #update paddle speed if it reflects a ball
    global paddle_speed
    
    #if ball centre is lower than paddle top
    if ball_pos[1] >= (paddle_pos[1] - HALF_PAD_HEIGHT):
        # distance is paddle_centre - ball_centre
        dy = ball_pos[1] - paddle_pos[1]
        
    # ball centre is higher than paddle bottom
    else:
        # distance is ball_centre - paddle_centre
        dy = paddle_pos[1] - ball_pos[1]
    
    #if ball centre is no more than half pad width away from paddle centre, it is collision
    if dy <= HALF_PAD_HEIGHT:
        collision = True
        #update paddle speed to match ball speed
        paddle_speed = paddle_speed * 110 / 100
    else:
        collision = False
        
    return collision
        
def move_ball_vertical():
    global ball_pos, ball_vel
    
    # scale vertical velocity for 60fps update rate
    dy = ball_vel[1] / 60
    
    # update the vertical position with the scaled vertical velocity
    ball_pos[1] = ball_pos[1] + dy
    
    # If ball edge moves off the playfield, 
    if (ball_pos[1] < BALL_RADIUS) or (ball_pos[1] > (HEIGHT - BALL_RADIUS)):
        # move it back
        ball_pos[1] = ball_pos[1] - dy
        # reverse the velocity
        ball_vel[1] = -ball_vel[1]
        dy = ball_vel[1] / 60
        # move in the new direction instead
        ball_pos[1] = ball_pos[1] + dy
    
def move_ball_horizontal():
    global ball_pos, ball_vel, scoreR, scoreL
    
    # scale horizontal velocity for 60fps update rate
    dx = ball_vel[0] / 60
    
    # update ball horizontal position with scaled horizontal velocity
    ball_pos[0] = ball_pos[0] + dx
    
    # If ball edge moves off the left-side of the playfield, 
    if (ball_pos[0] - BALL_RADIUS) <= PAD_WIDTH:
        #if there is a paddle in the way
        if ball_collides_with_paddle(paddleL_pos) == True:
            # move the ball back
            ball_pos[0] = ball_pos[0] - dx
            # reverse the velocity
            ball_vel[0] = -ball_vel[0]
            # increase the velocity by 10%
            ball_vel[0] = (ball_vel[0] * 110) / 100
            dx = ball_vel[0] / 60
            # move the ball in the new direction
            ball_pos[0] = ball_pos[0] + dx
            
        # else there is a score zone
        else:
            # add a point to the right player score
            scoreR = scoreR + 1
            # start a new game
            spawn_ball(RIGHT)
        
    # if the ball edge moves off the right-side of the playfield
    if (ball_pos[0] + BALL_RADIUS) >= (WIDTH - PAD_WIDTH - 1):
        #if there is a paddle in the way
        if ball_collides_with_paddle(paddleR_pos) == True:
            #move the ball back
            ball_pos[0] = ball_pos[0] - dx
            # reverse the velocity
            ball_vel[0] = -ball_vel[0]
            # increase the velocity by 10%
            ball_vel[0] = (ball_vel[0] * 110) / 100
            dx = ball_vel[0] / 60
            # move the ball in the new direction
            ball_pos[0] = ball_pos[0] + dx
            
        # else there is a score zone
        else:
            # add a point to the left player score
            scoreL = scoreL + 1
            # start a new game
            spawn_ball(LEFT)
            
def move_paddle_position(paddle_pos, paddle_vel):
    # move paddle centre
    paddle_pos[1] = paddle_pos[1] + paddle_vel[1]
    
    # if moving off screen, reverse
    if paddle_pos[1] < HALF_PAD_HEIGHT:
        paddle_pos[1] = paddle_pos[1] - paddle_vel[1]
        
    if paddle_pos[1] > (HEIGHT - HALF_PAD_HEIGHT):
        paddle_pos[1] = paddle_pos[1] - paddle_vel[1]
        
    return paddle_pos

def draw_zero(canvas, left_pos, top_pos):
    dy = HEIGHT / 10
    dx = WIDTH / 16
    pt0 = [left_pos, top_pos - dy]
    pt1 = [left_pos, top_pos + dy]
    pt2 = [left_pos + dx, top_pos + dy]
    pt3 = [left_pos + dx, top_pos - dy]
    canvas.draw_polyline((pt0,pt1,pt2,pt3,pt0),HALF_PAD_WIDTH,"White")
    
def draw_one(canvas, left_pos, top_pos):
    dy = HEIGHT / 10
    dx = WIDTH / 16
    pt0 = [left_pos, top_pos - dy]
    pt1 = [left_pos, top_pos + dy]
    canvas.draw_polyline((pt0,pt1),HALF_PAD_WIDTH,"White")
    
def draw_two(canvas, left_pos, top_pos):
    dy = HEIGHT / 10
    dx = WIDTH / 16
    pt0 = [left_pos, top_pos - dy]
    pt1 = [left_pos + dx, top_pos - dy]
    pt2 = [left_pos + dx, top_pos]
    pt3 = [left_pos, top_pos]
    pt4 = [left_pos, top_pos + dy]
    pt5 = [left_pos + dx, top_pos + dy]
    canvas.draw_polyline((pt0,pt1,pt2,pt3,pt4,pt5),HALF_PAD_WIDTH,"White")
    
def draw_three(canvas, left_pos, top_pos):
    dy = HEIGHT / 10
    dx = WIDTH / 16
    pt0 = [left_pos, top_pos - dy]
    pt1 = [left_pos + dx, top_pos - dy]
    pt2 = [left_pos + dx, top_pos]
    pt3 = [left_pos, top_pos]
    pt4 = [left_pos + dx, top_pos]
    pt5 = [left_pos + dx, top_pos + dy]
    pt6 = [left_pos, top_pos + dy]
    canvas.draw_polyline((pt0,pt1,pt2,pt3,pt4,pt5,pt6),HALF_PAD_WIDTH,"White")
    
def draw_four(canvas, left_pos, top_pos):
    dy = HEIGHT / 10
    dx = WIDTH / 16
    pt0 = [left_pos, top_pos - dy]
    pt1 = [left_pos, top_pos]
    pt2 = [left_pos + dx, top_pos]
    pt3 = [left_pos + dx, top_pos - dy]
    pt4 = [left_pos + dx, top_pos + dy]
    canvas.draw_polyline((pt0,pt1,pt2,pt3,pt4),HALF_PAD_WIDTH,"White")
    
def draw_five(canvas, left_pos, top_pos):
    dy = HEIGHT / 10
    dx = WIDTH / 16
    pt0 = [left_pos + dx, top_pos - dy]
    pt1 = [left_pos, top_pos - dy]
    pt2 = [left_pos, top_pos]
    pt3 = [left_pos + dx, top_pos]
    pt4 = [left_pos + dx, top_pos + dy]
    pt5 = [left_pos, top_pos + dy]
    canvas.draw_polyline((pt0,pt1,pt2,pt3,pt4,pt5),HALF_PAD_WIDTH,"White")
    
def draw_six(canvas, left_pos, top_pos):
    dy = HEIGHT / 10
    dx = WIDTH / 16
    pt0 = [left_pos + dx, top_pos - dy]
    pt1 = [left_pos, top_pos - dy]
    pt2 = [left_pos, top_pos + dy]
    pt3 = [left_pos + dx, top_pos + dy]
    pt4 = [left_pos + dx, top_pos]
    pt5 = [left_pos, top_pos]
    canvas.draw_polyline((pt0,pt1,pt2,pt3,pt4,pt5),HALF_PAD_WIDTH,"White")
    
def draw_seven(canvas, left_pos, top_pos):
    dy = HEIGHT / 10
    dx = WIDTH / 16
    pt0 = [left_pos, top_pos - dy]
    pt1 = [left_pos + dx, top_pos - dy]
    pt2 = [left_pos + dx, top_pos + dy]
    canvas.draw_polyline((pt0,pt1,pt2),HALF_PAD_WIDTH,"White")
    
def draw_eight(canvas, left_pos, top_pos):
    dy = HEIGHT / 10
    dx = WIDTH / 16
    pt0 = [left_pos, top_pos - dy]
    pt1 = [left_pos + dx, top_pos - dy]
    pt2 = [left_pos + dx, top_pos + dy]
    pt3 = [left_pos, top_pos + dy]
    pt4 = [left_pos, top_pos - dy]
    pt5 = [left_pos, top_pos]
    pt6 = [left_pos + dx, top_pos]
    canvas.draw_polyline((pt0,pt1,pt2,pt3,pt4,pt5,pt6),HALF_PAD_WIDTH,"White")
    
def draw_nine(canvas, left_pos, top_pos):
    dy = HEIGHT / 10
    dx = WIDTH / 16
    pt0 = [left_pos, top_pos + dy]
    pt1 = [left_pos + dx, top_pos + dy]
    pt2 = [left_pos + dx, top_pos - dy]
    pt3 = [left_pos, top_pos - dy]
    pt4 = [left_pos, top_pos]
    pt5 = [left_pos + dx, top_pos]
    canvas.draw_polyline((pt0,pt1,pt2,pt3,pt4,pt5),HALF_PAD_WIDTH,"White")
    
def draw_score(canvas, left_pos, top_pos, score):
    number = score % 10
    if number == 0:
        draw_zero(canvas, left_pos, top_pos)
    elif number == 1:
        draw_one(canvas, left_pos, top_pos)
    elif number == 2:
        draw_two(canvas, left_pos, top_pos)
    elif number == 3:
        draw_three(canvas, left_pos, top_pos)
    elif number == 4:
        draw_four(canvas, left_pos, top_pos)
    elif number == 5:
        draw_five(canvas, left_pos, top_pos)
    elif number == 6:
        draw_six(canvas, left_pos, top_pos)
    elif number == 7:
        draw_seven(canvas, left_pos, top_pos)
    elif number == 8:
        draw_eight(canvas, left_pos, top_pos)
    else:
        draw_nine(canvas, left_pos, top_pos)
        
def stop_game():
    ball_vel[0] = 0
    ball_vel[1] = 0
    ball_pos[0] = WIDTH / 2
    ball_pos[1] = HEIGHT / 2
    
# define event handlers
def new_game():
    global paddleL_pos, paddleR_pos, paddleL_vel, paddleR_vel  # these are numbers
    global scoreL, scoreR  # these are ints
    global paddle_speed
    
    paddleL_pos = [0, HEIGHT / 2]
    paddleL_vel = [0, 0]
    paddleR_pos = [WIDTH - PAD_WIDTH - 1, HEIGHT / 2]
    paddleR_vel = [0, 0]
    
    scoreL = 0
    scoreR = 0
    
    if random.randrange(0, 10) < 5:
        spawn_ball(LEFT)
    else:
        spawn_ball(RIGHT)

def draw(canvas):
    global scoreL, scoreR, paddleL_pos, paddleR_pos, ball_pos, ball_vel
    
    # draw mid line and gutters
    canvas.draw_line([WIDTH / 2, 0],[WIDTH / 2, HEIGHT], 1, "Gray")
    canvas.draw_line([PAD_WIDTH, 0],[PAD_WIDTH, HEIGHT], 1, "Gray")
    canvas.draw_line([WIDTH - PAD_WIDTH - 1, 0],[WIDTH - PAD_WIDTH - 1, HEIGHT], 1, "Gray")
        
    # update ball
    move_ball_vertical()
    move_ball_horizontal()
    
    # draw ball
    canvas.draw_circle(ball_pos, BALL_RADIUS, 1, "White", "White")
    
    # update paddle's vertical position, keep paddle on the screen
    paddleL_pos = move_paddle_position(paddleL_pos, paddleL_vel)
    paddleR_pos = move_paddle_position(paddleR_pos, paddleR_vel)
    
    # draw paddles
    top = paddleL_pos[1] - HALF_PAD_HEIGHT
    bot = paddleL_pos[1] + HALF_PAD_HEIGHT
    left = 1
    right = PAD_WIDTH
    canvas.draw_polygon(([left, top],[right, top],[right, bot], [left, bot], [left, top]), 1, "White", "White")
    top = paddleR_pos[1] - HALF_PAD_HEIGHT
    bot = paddleR_pos[1] + HALF_PAD_HEIGHT
    left = WIDTH - PAD_WIDTH - 1
    right = WIDTH - 1
    canvas.draw_polygon(([left, top],[right, top],[right, bot], [left, bot], [left, top]), 1, "White", "White")
    
    # determine whether paddle and ball collide    
    
    # draw scores
    draw_score(canvas, WIDTH / 4, HEIGHT / 5, scoreL)
    draw_score(canvas, WIDTH / 4 * 3, HEIGHT / 5, scoreR)
    
    if scoreL == 9:
        stop_game()
    if scoreR == 9:
        stop_game()

def keydown(key):
    global paddleL_vel, paddleR_vel
    
    if key == simplegui.KEY_MAP["w"]:
        paddleL_vel[1] = -paddle_speed / 60
    if key == simplegui.KEY_MAP["s"]:
        paddleL_vel[1] = paddle_speed / 60
    if key == simplegui.KEY_MAP["up"]:
        paddleR_vel[1] = -paddle_speed / 60
    if key == simplegui.KEY_MAP["down"]:
        paddleR_vel[1] = paddle_speed / 60
   
def keyup(key):
    global paddleL_vel, paddleR_vel

    if key == simplegui.KEY_MAP["w"]:
        paddleL_vel[1] = 0
    if key == simplegui.KEY_MAP["s"]:
        paddleL_vel[1] = 0
    if key == simplegui.KEY_MAP["up"]:
        paddleR_vel[1] = 0
    if key == simplegui.KEY_MAP["down"]:
        paddleR_vel[1] = 0

# create frame
frame = simplegui.create_frame("Pong", WIDTH, HEIGHT)
frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
frame.add_button("Reset Game", new_game, 125)

# start frame
new_game()
frame.start()
