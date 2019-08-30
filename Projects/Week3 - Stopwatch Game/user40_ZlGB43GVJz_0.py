# template for "Stopwatch: The Game"

import simplegui

# define global variables
time = 0
stop_counter = 0
zero_counter = 0

# define helper function format that converts time
# in tenths of seconds into formatted string A:BC.D
def format(t):
    timer_min = t / 600
    timer_sec10 = t % 600
    timer_msec = timer_sec10 % 10
    timer_sec_one = (timer_sec10 % 100) / 10
    timer_sec_ten = timer_sec10 / 100
    timer_string = str(timer_min) + ":"
    timer_string += str(timer_sec_ten) + str(timer_sec_one) + "."
    timer_string += str(timer_msec)
    return timer_string

def format_score(zeroes, stops):
    zeroes_ten = zeroes / 10
    zeroes_one = zeroes % 10
    stops_ten = stops / 10
    stops_one = stops % 10
    return str(zeroes_ten) + str(zeroes_one) + "/" + str(stops_ten) + str(stops_one)
    
# define event handlers for buttons; "Start", "Stop", "Reset"
def start_timer():
    timer.start()

def stop_timer():
    global stop_counter, zero_counter
    timer.stop()
    stop_counter += 1
    if (time % 10) == 0:
        zero_counter += 1
    print "Hit rate:", str(((zero_counter * 1000) / stop_counter) / 10.0) + "%"
    
def reset_timer():
    global time, stop_counter, zero_counter
    timer.stop()
    time = 0
    stop_counter = 0
    zero_counter = 0
    
# define event handler for timer with 0.1 sec interval
def timer_event():
    global time
    time = time + 1
    if 6000 <= time:
        time = 0

# define draw handler
def draw_handler(canvas):
    canvas.draw_text(format(time), (25, 150), 100, "White")
    canvas.draw_text(format_score(zero_counter, stop_counter), (220, 25), 24, "White")
    
# create frame
frame = simplegui.create_frame("Stopwatch Game", 300, 200)

# register event handlers
frame.add_button("Start", start_timer, 100)
frame.add_button("Stop", stop_timer, 100)
frame.add_button("Reset", reset_timer, 100)

timer = simplegui.create_timer(100, timer_event)

frame.set_draw_handler(draw_handler)

# start frame
frame.start()

# Please remember to review the grading rubric
