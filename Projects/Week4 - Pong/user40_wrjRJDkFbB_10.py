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

BALL_MAX_X_SPEED = 240
BALL_MIN_X_SPEED = 120
BALL_MAX_Y_SPEED = 180
BALL_MIN_Y_SPEED = 60

#default paddle speed: cover top-to-bottom move in the time ball moves between mid-line and gutter
PADDLE_SPEED = BALL_MAX_X_SPEED * (HEIGHT - PAD_HEIGHT) / (WIDTH / 2 - PAD_WIDTH - BALL_RADIUS)

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

# left player score
scoreL = 0

# right player score
scoreR = 0

game_over = False
score_timer = 0

# first to WIN_SCORE wins
WIN_SCORE = 9

# left score position
LX = WIDTH / 4
LY = HEIGHT / 5

# right score position
RX = 3 * WIDTH / 4
RY = HEIGHT / 5

# digit dimenstion
DW = WIDTH / 16
DH = HEIGHT / 10

# digit polylines
L0 = ((LX, LY - DH), (LX, LY + DH), (LX + DW, LY + DH), (LX + DW, LY - DH), (LX, LY - DH))
R0 = ((RX, RY - DH), (RX, RY + DH), (RX + DW, RY + DH), (RX + DW, RY - DH), (RX, RY - DH))
L1 = ((LX, LY - DH), (LX, LY + DH))
R1 = ((RX, RY - DH), (RX, RY + DH))
L2 = ((LX, LY - DH), (LX + DW, LY - DH), (LX + DW, LY), (LX, LY), (LX, LY + DH), (LX + DW, LY + DH))
R2 = ((RX, RY - DH), (RX + DW, RY - DH), (RX + DW, RY), (RX, RY), (RX, RY + DH), (RX + DW, RY + DH))
L3 = ((LX, LY - DH), (LX + DW, LY - DH), (LX + DW, LY), (LX, LY), (LX + DW, LY), (LX + DW, LY + DH), (LX, LY + DH))
R3 = ((RX, RY - DH), (RX + DW, RY - DH), (RX + DW, RY), (RX, RY), (RX + DW, RY), (RX + DW, RY + DH), (RX, RY + DH))
L4 = ((LX, LY - DH), (LX, LY), (LX + DW, LY), (LX + DW, LY - DH), (LX + DW, LY + DH))
R4 = ((RX, RY - DH), (RX, RY), (RX + DW, RY), (RX + DW, RY - DH), (RX + DW, RY + DH))
L5 = ((LX + DW, LY - DH), (LX, LY - DH), (LX, LY), (LX + DW, LY), (LX + DW, LY + DH), (LX, LY + DH))
R5 = ((RX + DW, RY - DH), (RX, RY - DH), (RX, RY), (RX + DW, RY), (RX + DW, RY + DH), (RX, RY + DH))
L6 = ((LX + DW, LY - DH), (LX, LY - DH), (LX, LY + DH), (LX + DW, LY + DH), (LX + DW, LY), (LX, LY))
R6 = ((RX + DW, RY - DH), (RX, RY - DH), (RX, RY + DH), (RX + DW, RY + DH), (RX + DW, RY), (RX, RY))
L7 = ((LX, LY - DH), (LX + DW, LY - DH), (LX + DW, LY + DH))
R7 = ((RX, RY - DH), (RX + DW, RY - DH), (RX + DW, RY + DH))
L8 = ((LX, LY), (LX, LY + DH), (LX + DW, LY + DH), (LX + DW, LY - DH), (LX, LY - DH), (LX, LY), (LX + DW, LY))
R8 = ((RX, RY), (RX, RY + DH), (RX + DW, RY + DH), (RX + DW, RY - DH), (RX, RY - DH), (RX, RY), (RX + DW, LY))
L9 = ((LX, LY + DH), (LX + DW, LY + DH), (LX + DW, LY - DH), (LX, LY - DH), (LX, LY), (LX + DW, LY))
R9 = ((RX, RY + DH), (RX + DW, RY + DH), (RX + DW, RY - DH), (RX, RY - DH), (RX, RY), (RX + DW, RY))

LEFT_DIGITS = (L0, L1, L2, L3, L4, L5, L6, L7, L8, L9)
RIGHT_DIGITS = (R0, R1, R2, R3, R4, R5, R6, R7, R8, R9)

#================================================================================
# bounce ball off paddle
def reverse_ball_x_speed():
    dx = ball_vel[0] / 60
    
# move the ball back
    ball_pos[0] = ball_pos[0] - dx
    
# reverse the velocity
    ball_vel[0] = -ball_vel[0]
    
# increase the velocity by 10%
    ball_vel[0] = (ball_vel[0] * 110) / 100
    dx = ball_vel[0] / 60
    
# move the ball in the new direction
    ball_pos[0] = ball_pos[0] + dx

#================================================================================
# move ball in x direction
def move_ball_horizontal():
    global ball_pos, ball_vel, scoreR, scoreL
    
# scale horizontal velocity for 60fps update rate
    dx = ball_vel[0] / 60
    
# update ball horizontal position with scaled horizontal velocity
    ball_pos[0] = ball_pos[0] + dx

#================================================================================
def check_ball_horizontal_hits():
    global scoreL, scoreR
    
# If ball edge moves off the left-side of the playfield, 
    if (ball_pos[0] - BALL_RADIUS) <= PAD_WIDTH:
        
# if there is a paddle in the way, reverse x speed, else score
        if ball_collides_with_paddle(paddleL_pos) == True:
            reverse_ball_x_speed()
        
        else:
            scoreR = scoreR + 1
            
# start a new game to right player
            spawn_ball(RIGHT)
        
# if the ball edge moves off the right-side of the playfield
    if (ball_pos[0] + BALL_RADIUS) >= (WIDTH - PAD_WIDTH - 1):
        
# if there is a paddle in the way, reverse x speed, else score
        if ball_collides_with_paddle(paddleR_pos) == True:
            reverse_ball_x_speed()
        else:
            scoreL = scoreL + 1
            
# start a new game to left player
            spawn_ball(LEFT)

#================================================================================
# move the ball in the y direction
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
    
#================================================================================
# adjust paddle y position by paddle speed in y direction
def move_paddle_position(paddle_pos, paddle_vel):
    
# move paddle centre
    paddle_pos[1] = paddle_pos[1] + paddle_vel[1]
    
# if moving off screen, reverse
    if paddle_pos[1] < HALF_PAD_HEIGHT:
        paddle_pos[1] = paddle_pos[1] - paddle_vel[1]
        
    if paddle_pos[1] > (HEIGHT - HALF_PAD_HEIGHT):
        paddle_pos[1] = paddle_pos[1] - paddle_vel[1]
        
    return paddle_pos

#================================================================================
def ball_collides_with_paddle(paddle_pos):

# if ball centre is lower than paddle centre
    if ball_pos[1] >= paddle_pos[1]:
        dy = ball_pos[1] - paddle_pos[1]
        
    else:
        dy = paddle_pos[1] - ball_pos[1]
    
# if ball centre is no more than half pad height away from paddle centre, it is collision
    if dy <= HALF_PAD_HEIGHT:
        collision = True
        
    else:
        collision = False
        
    return collision
  
#================================================================================
def stop_game():
    global game_over
    
    ball_vel[0] = 0
    ball_vel[1] = 0
    ball_pos[0] = WIDTH / 2
    ball_pos[1] = HEIGHT / 2
    
    game_over = True
    
#================================================================================
# initialize ball_pos and ball_vel for new bal in middle of table
# if direction is RIGHT, the ball's velocity is upper right, else upper left
def spawn_ball(direction):
    global ball_pos, ball_vel # these are vectors stored as lists
    
# pick a random position on midline from center half of playfield width
    ball_pos[1] = random.randrange(HEIGHT / 4, HEIGHT * 3 / 4)
    
# set start position on midline horizontally
    ball_pos[0] = WIDTH / 2
    
# set the horizontal speedvector in the range 120-240 pixels/second to start with
    dx = random.randrange(BALL_MIN_X_SPEED, BALL_MAX_X_SPEED + 1)
    
    if direction == LEFT:
        ball_vel[0] = -dx
    else:
        ball_vel[0] = dx
    
# set the vertical speedvector in the range 60-180 pixels/second to start with
    dy = random.randrange(BALL_MIN_Y_SPEED, BALL_MAX_Y_SPEED + 1)
    
    ball_vel[1] = -dy
    
#================================================================================
# define event handlers
def new_game():
    global paddleL_pos, paddleR_pos, paddleL_vel, paddleR_vel  # these are numbers
    global scoreL, scoreR  # these are ints
    global game_over
    
    paddleL_pos = [0, HEIGHT / 2]
    paddleL_vel = [0, 0]
    paddleR_pos = [WIDTH - PAD_WIDTH - 1, HEIGHT / 2]
    paddleR_vel = [0, 0]
    
    scoreL = 0
    scoreR = 0
    
    game_over = False
    
    if random.randrange(0, 10) < 5:
        spawn_ball(LEFT)
    else:
        spawn_ball(RIGHT)

#================================================================================
def draw(canvas):
    global scoreL, scoreR, score_timer
    global paddleL_pos, paddleR_pos, ball_pos, ball_vel
    
# draw mid line and gutters
    canvas.draw_line([WIDTH / 2, 0],[WIDTH / 2, HEIGHT], 1, "Silver")
    canvas.draw_line([PAD_WIDTH, 0],[PAD_WIDTH, HEIGHT], 1, "Silver")
    canvas.draw_line([WIDTH - PAD_WIDTH - 1, 0],[WIDTH - PAD_WIDTH - 1, HEIGHT], 1, "Silver")
        
# update ball
    move_ball_vertical()
    move_ball_horizontal()
    
# draw ball
    canvas.draw_circle(ball_pos, BALL_RADIUS, 1, "White", "White")
    
# in game, update paddle's vertical position, keep paddle on the screen
    if game_over == False:
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
    check_ball_horizontal_hits()
    
# draw scores
# at winning score
    if scoreL == WIN_SCORE:

        # make paddle bounce up and down, while flashing winning score. because it looks cool !
        if score_timer < 60:
# in first second counts, calculate Y position going from bottom to top
            paddleY = (60 - score_timer) * (HEIGHT - 1 - PAD_HEIGHT) / 60
        else:
# flash winning score by showing it every other second 
            canvas.draw_polyline(LEFT_DIGITS[scoreL], HALF_PAD_WIDTH, "white")
# in second second counts, calculate Y position going from top to bottom
            paddleY = (score_timer - 60) * (HEIGHT - 1 - PAD_HEIGHT) / 60

# put paddle at bouncy position for next draw
        paddleL_pos = [WIDTH - PAD_WIDTH - 1, HALF_PAD_HEIGHT + paddleY]
# and stop playing (until game reset)
        stop_game()
    
    else:
# not a winning score, just draw the digit
        canvas.draw_polyline(LEFT_DIGITS[scoreL], HALF_PAD_WIDTH, "white")

# if at a winning score ...
    if scoreR == WIN_SCORE:
        
        if score_timer < 60:
# in first second counts, calculate Y position going from bottom to top
            paddleY = (60 - score_timer) * (HEIGHT - 1 - PAD_HEIGHT) / 60
        else:
# flash winning score by showing it every other second 
            canvas.draw_polyline(RIGHT_DIGITS[scoreR], HALF_PAD_WIDTH, "white")
# in second second counts, calculate Y position going from top to bottom
            paddleY = (score_timer - 60) * (HEIGHT - 1 - PAD_HEIGHT) / 60

# put paddle at bouncy position for next draw
        paddleR_pos = [WIDTH - PAD_WIDTH - 1, HALF_PAD_HEIGHT + paddleY]
# and stop playing (until game reset)
        stop_game()

    else:
# not a winning score, just draw the digit
        canvas.draw_polyline(RIGHT_DIGITS[scoreR], HALF_PAD_WIDTH, "white")
    
# if score_timer is running, update, else reset
    if score_timer > 0:
        score_timer = score_timer - 1
    else:
        score_timer = 120
    

#================================================================================
def keydown(key):
    global paddleL_vel, paddleR_vel
    
    if key == simplegui.KEY_MAP["w"]:
        paddleL_vel[1] = -PADDLE_SPEED / 60
    if key == simplegui.KEY_MAP["s"]:
        paddleL_vel[1] = PADDLE_SPEED / 60
    if key == simplegui.KEY_MAP["up"]:
        paddleR_vel[1] = -PADDLE_SPEED / 60
    if key == simplegui.KEY_MAP["down"]:
        paddleR_vel[1] = PADDLE_SPEED / 60
   
#================================================================================
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

#================================================================================
# create frame
frame = simplegui.create_frame("Pong", WIDTH, HEIGHT)
frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
frame.add_button("Reset Game", new_game, 125)

# start frame
new_game()
frame.start()
