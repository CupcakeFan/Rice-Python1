# implementation of card game - Memory

import simplegui
import random

cards = list(range(8))
cards.extend(range(8))
index1 = len(cards)
index2 = len(cards)

# helper function to initialize globals
def new_game():
    global cards
    global exposed
    global state
    state = 0
    random.shuffle(cards)  
    exposed = [False for card in cards]
     
# define event handlers
def mouseclick(pos):
    global exposed
    global state
    global index1
    global index2
    # add game state logic here
    idx_y = pos[1] / 100
    idx_x = pos[0] / 50
    idx = idx_y * 1 + idx_x
    print idx, pos
    
    if idx != index1 and idx != index2:
        if 0 == state:
            state = 1
            exposed[idx] = True
            index1 = idx
            print index1, exposed[index1]
        elif 1 == state:
            state = 2
            exposed[idx] = True
            index2 = idx
            print index2, exposed[index2]

        else:
            if cards[index1] != cards[index2]:
                exposed[index1] = False
                exposed[index2] = False
                print index1, exposed[index1]
                print index2, exposed[index2]
            print
            
            state = 1
            index1 = idx
            exposed[idx] = True
            print index1, exposed[index1]
        

# cards are logically 50x100 pixels in size    
def draw(canvas):
    for idx in range(len(exposed)):
        x1 = idx * 50
        y1 = 0
        x2 = x1 + 49
        y2 = 100
        
        if True == exposed[idx]:
            canvas.draw_text(str(cards[idx]), (20 + x1, y2 / 2), 24, "White")
        else:
            canvas.draw_polygon([(x1, y1),(x2, y1),(x2, y2),(x1, y2),(x1, y1)],1,"Black","Green")


# create frame and add a button and labels
frame = simplegui.create_frame("Memory", 800, 100)
frame.add_button("Reset", new_game)
label = frame.add_label("Turns = 0")

# register event handlers
frame.set_mouseclick_handler(mouseclick)
frame.set_draw_handler(draw)

# get things rolling
new_game()
frame.start()

print cards
print exposed

# Always remember to review the grading rubric