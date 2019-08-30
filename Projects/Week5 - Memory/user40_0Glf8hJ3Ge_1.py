# implementation of card game - Memory

import simplegui
import random

# constants to define play area and look of the game
CARD_W = 50 # pixels in x direction
CARD_H = 100 # pixels in y direction
TOTAL_CARDS = 16 # total cards in play
CARDS_PER_ROW = 4 # number of cards to place in a row (make sure it is a factor of total)
WIDTH = CARDS_PER_ROW * CARD_W # canvas width is number of cards per row
HEIGHT = (TOTAL_CARDS / CARDS_PER_ROW) * CARD_H # canvas height is number of card rows

# variables to keep card value and flips: total cards / 2 because it keeps pairs of values
cards = list(range(TOTAL_CARDS / 2))
cards.extend(range(TOTAL_CARDS / 2))
index1 = len(cards) # point somewhere invalid initially
index2 = len(cards) # point somewhere invalid initially

# helper function to initialize globals
def new_game():
    global cards
    global exposed
    global state
    global turn_counter
    
    state = 0
    random.shuffle(cards)
    # make all the cards unflipped in this list
    exposed = [False for card in cards]
    #reset and display the turns counter
    turn_counter = 0
    label.set_text("Turns =" + str(turn_counter))
        
# define event handlers
def mouseclick(pos):
    global exposed
    global state
    global index1
    global index2
    global turn_counter
    
    # add game state logic here
    # calculate the index number from the mouse position
    idx_y = pos[1] / CARD_H
    idx_x = pos[0] / CARD_W
    idx = idx_y * CARDS_PER_ROW + idx_x
    
    # we are not clicking on a previously exposed card
    if False == exposed[idx]:
        # start state, like 2 cards exposed state
        if 0 == state:
            # one card exposed after this click
            state = 1
            # expose the selected card
            exposed[idx] = True
            # remember this card is exposed
            index1 = idx
            
        # another card being exposed
        elif 1 == state:
            # 2 cards exposed after this click
            state = 2
            # expose the selected card
            exposed[idx] = True
            # remember this card is exposed
            index2 = idx
            
            # 2 cards exposed = 1 turn taken
            turn_counter += 1
            # show the new number of turns
            label.set_text("Turns =" + str(turn_counter))
            
        # new pair being selected
        else:
            # shall we hide card pair that did not match ?
            if cards[index1] != cards[index2]:
                # hide first selection
                exposed[index1] = False
                # hide second selection
                exposed[index2] = False
            
            # only 1 card exposed after this click
            state = 1
            # remember this selection
            index1 = idx
            # remove the old second selection
            index2 = len(cards)
            # expose the selected card
            exposed[idx] = True
        

# cards are logically 50x100 pixels in size    
def draw(canvas):
    # loop over all the cards in the list
    for idx in range(len(exposed)):
        # calculate the card corners for this card
        x1 = (idx % CARDS_PER_ROW) * CARD_W
        y1 = (idx / CARDS_PER_ROW) * CARD_H
        x2 = x1 + (CARD_W - 1)
        y2 = y1 + CARD_H
        
        # if exposed, we draw the face and the edges
        if True == exposed[idx]:
            # show the face, which is just the number as a string
            canvas.draw_text(str(cards[idx]), (20 + x1, y1 + 5 + CARD_H / 2), 24, "White")
            # frame the number showing the edge of the card
            canvas.draw_polyline([(x1, y1),(x2, y1),(x2, y2),(x1, y2),(x1, y1)],1,"White")
        # if hidden, we draw the card back
        else:
            canvas.draw_polygon([(x1, y1),(x2, y1),(x2, y2),(x1, y2),(x1, y1)],1,"Black","Green")


# create frame and add a button and labels
frame = simplegui.create_frame("Memory", WIDTH, HEIGHT)
frame.add_button("Reset", new_game)
label = frame.add_label("Turns = 0")

# register event handlers
frame.set_mouseclick_handler(mouseclick)
frame.set_draw_handler(draw)

# get things rolling
new_game()
frame.start()

# Always remember to review the grading rubric