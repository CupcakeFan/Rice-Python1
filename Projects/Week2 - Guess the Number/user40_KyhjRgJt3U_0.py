# template for "Guess the number" mini-project
# input will come from buttons and an input field
# all output for the game will be printed in the console

import simplegui
import random
import math

secret_number = 0
selected_range = 100
remaining_guesses = 0

# helper function to start and restart the game
def new_game():
    # initialize global variables used in your code here
    global secret_number, remaining_guesses
    
    # remove this when you add your code    
    secret_number = random.randrange(0, selected_range)
    remaining_guesses = int(math.log(selected_range)/math.log(2)) + 1
    
    print ""
    print "Guess the number in the range 0 to", selected_range
    print remaining_guesses, "remaining guesses"

# define event handlers for control panel
def range100():
    # button that changes the range to [0,100) and starts a new game 
    global selected_range
    
    selected_range = 100
    new_game()

def range1000():
    # button that changes the range to [0,1000) and starts a new game     
    global selected_range
    
    selected_range = 1000
    new_game()
    
def input_guess(guess):
    # main game logic goes here	
    global remaining_guesses
    start_new_game = False
    
    guess_number = int(guess)
    remaining_guesses -= 1
    
    if guess_number < secret_number:
        response = ": Higher ..."
    elif guess_number > secret_number:
        response = ": Lower ..."
    else:
        response = "= Correct !"
        start_new_game = True
        
    print guess, response
    
    if not start_new_game:
        if remaining_guesses > 0:
            print remaining_guesses, "remaining guesses"
        else:
            print "Hard luck ! Try again ..."
            start_new_game = True
        
    if start_new_game:
        new_game()
        
# create frame
frame = simplegui.create_frame("Guess the Number", 200, 200)

# register event handlers for control elements and start frame
frame.add_button("[0-100)", range100, 150)
frame.add_button("[0-1000)", range1000, 150)
frame.add_input("Enter your guess:", input_guess, 150)

# call new_game 
new_game()

frame.start()

# always remember to check your completed program against the grading rubric
