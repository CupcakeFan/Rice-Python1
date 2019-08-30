# Mini-project #6 - Blackjack
#============================================================

import simplegui
import random

# ===========================================================
# load card sprite - 936x384 - source: jfitz.com
CARD_SIZE = (72, 96)
CARD_CENTER = (36, 48)
card_images = simplegui.load_image("http://storage.googleapis.com/codeskulptor-assets/cards_jfitz.png")

# number of card backs (we try to use more than one)
CARD_NUM_OF_BACKS = 2
CARD_BACK_SIZE = (72, 96)
CARD_BACK_CENTER = (36, 48)
card_back = simplegui.load_image("http://storage.googleapis.com/codeskulptor-assets/card_jfitz_back.png")    

# draw things a bit larger
SCALE = 11 / 10
DRAW_SIZE = (CARD_SIZE[0] * SCALE, CARD_SIZE[1] * SCALE)
DRAW_CENTER = (CARD_CENTER[0] * SCALE, CARD_CENTER[1] * SCALE)

# calculate a fair seperation of cards
MAX_CARD_SPACING_X = DRAW_SIZE[0] * 11 / 10

# thumbsuck a nice canvas/table size
TABLE_WIDTH = DRAW_SIZE[0] * 6
TABLE_HEIGHT = DRAW_SIZE[1] * 6

# define some draw positions so we can easily tweak the look
DRAW_DEALER = (TABLE_WIDTH / 20, TABLE_HEIGHT * 2 / 12)
DRAW_OUTCOME = (TABLE_WIDTH / 20, TABLE_HEIGHT * 6 / 12)
DRAW_SCORE = (TABLE_WIDTH - DRAW_OUTCOME[0], TABLE_HEIGHT / 12)
DRAW_PLAYER = (TABLE_WIDTH / 20, TABLE_HEIGHT * 8 / 12)
DRAW_MESSAGE = (TABLE_WIDTH / 20, TABLE_HEIGHT * 11 /12)

# Constants for easy game adjustment
SCORE_SIZE = 24
OUTCOME_SIZE = 32
MAX_DELAY_TIMER = 90

DEBUG = True

#=====================================================
# Rules
DEALER_DRAWS_TO = 17
# worst case number of cards in a single game is 17:
# A, A, A, A, 2, 2, 2, 2, 3, 3, 3 = 21 (11 low cards)
# 3, 4, 4, 4, 4, 5 = 24 (6 next cards)
DECK_LOW_LIMIT = 17 # deck lower than this, get a new one to make sure we can see the game out

#=====================================================
# initialize some useful global variables
in_play = False
outcome = ""
score = 0
player_message = "Hit or Stand ?"
dealer_play = False

# slow down the auto-play action
delay_timer = 0
dealer_play_time = MAX_DELAY_TIMER + 1

#======================================================
# define globals for cards
SUITS = ('C', 'S', 'H', 'D')
RANKS = ('A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K')
VALUES = {'A':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'T':10, 'J':10, 'Q':10, 'K':10}

#======================================================
# define card class
class Card:
    def __init__(self, suit, rank, back):
        if (suit in SUITS) and (rank in RANKS):
            self.suit = suit
            self.rank = rank
            self.back = back
            # card defaults to face-down
            self.face = False
        else:
            self.suit = None
            self.rank = None
            self.back = None
            self.face = None
            print "Invalid card: ", suit, rank
    
    def __str__(self):
        # when card is face up, return face value
        if self.face:
            return self.suit + self.rank
        # when card is face down, return face value marked
        else:
            return "/" + self.suit + self.rank + "/"
    
    # get the card suit value
    def get_suit(self):
        return self.suit
    
    # get the card rank value
    def get_rank(self):
        return self.rank
    
    # get the card face-up / face-down state
    def get_face(self):
        return self.face
    
    # change the card face-up / face-down state
    def flip(self):
        self.face = not self.face
    
    # force the card face-up
    def show(self):
        self.face = True
    
    # force the card face-down
    def hide(self):
        self.face = False
    
    # display the card at the given pos
    def draw(self, canvas, pos):
        # calculate the drawing position
        draw_loc = (pos[0] + DRAW_CENTER[0], 
                    pos[1] + DRAW_CENTER[1])
        # if face-up, select from card_face tiled image
        if self.face:
            card_loc = (CARD_CENTER[0] + CARD_SIZE[0] * RANKS.index(self.rank), 
                        CARD_CENTER[1] + CARD_SIZE[1] * SUITS.index(self.suit))
            canvas.draw_image(card_images, card_loc, CARD_SIZE, draw_loc, DRAW_SIZE)
        # if face-down, select from the card-back tiled image
        else:
            card_loc = (CARD_BACK_CENTER[0] + CARD_BACK_SIZE[0] * self.back, 
                        CARD_BACK_CENTER[1])
            canvas.draw_image(card_back, card_loc, CARD_BACK_SIZE, draw_loc, DRAW_SIZE)

#==========================================================
# define hand class
class Hand:
    def __init__(self):
        # create Hand object with empty card list
        self.cards = []
    
    def __str__(self):
        # return a string representation of a hand
        string = "Hand (" + str(self.get_value()) + "):"
        for i in range(len(self.cards)):
            string = string + " " + str(self.cards[i])
        return string
    
    def add_card(self, card):
        # if passing in no card, empty the card list
        if card == None:
            self.cards = []
        # add the card object to the hand
        else:
            self.cards.append(card)
    
    def get_value(self):
        # count aces as 1 initially
        # if the hand has an ace, then add 10 to hand value if it won't bust
        # compute the value of the hand, see Blackjack video
        value = 0
        # remember if there was an Ace in the hand
        has_ace = False
        # do for all cards in the hand
        for card in self.cards:
            # add value from dict lookup
            value += VALUES[card.get_rank()]
            # if this is an Ace, mark there is at least one Ace
            if card.get_rank() == 'A':
                has_ace = True
        # Done adding values, can we use Ace as an 11 value ?
        if has_ace:
            # if we are 11 or less, counting Ace as 11 wont pass 21 yet
            if value < 12:
                # So use (an) Ace as value 11
                value += 10
        return value
    
    # make the hand visible (cards face-up)
    def show(self):
        # Go through all cards in hand
        for card in self.cards:
            card.show()
    
    # make hand hidden (cards face-down)
    def hide(self):
        # Go through all cards in the hand
        for card in self.cards:
            card.hide()
    
    # draw a hand (series of cards) from start_pos going right
    def draw(self, canvas, start_pos):
        # Can take up to 11 cards to get to 21, so do some overlapping 
        # (A, A, A, A, 2, 2, 2, 2, 3, 3, 3)
        # 90% of canvas can be cards
        draw_overlap = TABLE_WIDTH * 18 / 20
        # calculate the spacing for the cards in the hand
        draw_overlap /= len(self.cards)
        # limit to a reasonable number
        if draw_overlap > MAX_CARD_SPACING_X:
            draw_overlap = MAX_CARD_SPACING_X
        # tuple -> list for mutating
        pos = list(start_pos)
        # draw a hand on the canvas, use the draw method for cards
        for card in self.cards:
            card.draw(canvas, pos)
            # move to next draw position (might overlap for a long hand)
            pos[0] += draw_overlap

#=====================================================
# define deck class 
class Deck:
    def __init__(self):
        # create a Deck object
        # start with first card back in tiled image
        self.selected_back = 0
        # reset the deck
        self.refresh_deck()
        # automatically shuffle the deck
        self.shuffle()
    
    # discard the current deck, rebuild full deck for all suites and ranks
    def refresh_deck(self):
        # can we select another card-back ?
        if CARD_NUM_OF_BACKS > 1:
            # toggle card-backs between first two
            self.selected_back = 1 - self.selected_back
        # empty deck
        self.cards = []
        # build for all ranks in all suits
        for suit in SUITS:
            for rank in RANKS:
                # create a card object with rank, suit and card-back
                self.cards.append(Card(suit, rank, self.selected_back))
    
    # random.shuffle the deck
    def shuffle(self):
        # shuffle the deck 
        # use random.shuffle()
        random.shuffle(self.cards)
    
    # take a card from the deck - we deal from the end of the list, not the from
    def deal_card(self):
        # if our deck runs low, get a fresh deck
        if len(self.cards) < DECK_LOW_LIMIT:
            # new deck
            self.refresh_deck()
            # shuffle the new deck
            self.shuffle()
        # deal a card object from the back of the deck
        return self.cards.pop(-1)
    
    # Show the object
    def __str__(self):
        # return a string representing the deck
        string = "Deck " + str(self.selected_back) + ":"
        for i in range(len(self.cards)):
            string = string + " " + str(self.cards[i])
        return string

#====================================================
#define event handlers for buttons
def deal():
    global outcome, player_message, score
    global in_play, hide_dealer, dealer_play_time
    global player_hand, dealer_hand, deck
    
    # dealing on an in_play player_hand loses player a point
    if in_play:
        score -= 1
    
    # drop any cards currently in each hand
    player_hand.add_card(None)
    dealer_hand.add_card(None)
    
    # 1. deal a flipped card to player
    card = deck.deal_card()
    card.flip()
    player_hand.add_card(card)
    # 2. deal a flipped card to dealer
    card = deck.deal_card()
    card.flip()
    dealer_hand.add_card(card)
    # 3. deal a flipped card to player
    card = deck.deal_card()
    card.flip()
    player_hand.add_card(card)
    # 4. deal a card to dealer, but do not flip this card
    dealer_hand.add_card(deck.deal_card())
    
    #DEBUG
    if DEBUG:
        print "Player", player_hand
    
    # do not hit dealer until we stand
    dealer_play = False
    # default delay between dealer hits (so we can follow action)
    dealer_play_time = MAX_DELAY_TIMER + 1
    
    # player_hand is in play
    in_play = True
    
    # outcome is an invite
    outcome = "Let's Play !"
    player_message = "Hit or Stand ?"

def hit():
    global score, in_play
    global outcome, player_message
    global player_hand, dealer_hand
    
    # if the hand is in play, hit the player with a face-up card
    if in_play:
        card = deck.deal_card()
        card.flip()
        player_hand.add_card(card)
        
        # outcome is a reminder message
        #outcome = "You got " + str(player_hand.get_value())
        outcome = "Dealer draws to " + str(DEALER_DRAWS_TO) + "..."
        
        # Show hand value
        if DEBUG:
            print "Player", player_hand
    else:
        player_message = "No game on table. New Deal ?"
    
    # if busted, assign a message to outcome, update in_play and score
    if in_play and (player_hand.get_value() > 21):
        in_play = False
        score -= 1
        outcome = "You busted !!"
        player_message = "New Deal ?"
        dealer_hand.show()

def stand():
    global dealer_play, dealer_play_time
    global outcome, player_message
    
    # if still in play, we can opt to stand
    if in_play:
        # reveal dealer initial cards
        dealer_hand.show()
        # set up slower play so we can follow what happens
        dealer_play_time = delay_timer
        # outcome is set to a reminder message
        outcome = "Dealer draws to " + str(DEALER_DRAWS_TO) + "..."
        # enable dealer to be hit
        dealer_play = True
        player_message = ""
        
        # Show hand value
        if DEBUG:
            print "Player", player_hand

#=====================================================
# helper function - hit dealer and check game state
def dealer_draws():
    global dealer_hand
    global score, outcome, player_message, in_play
    
    # assign player hand value for easy comparing
    p_value = player_hand.get_value()
    
    # should dealer take a card ?
    if dealer_hand.get_value() < DEALER_DRAWS_TO:
        card = deck.deal_card()
        card.flip()
        dealer_hand.add_card(card)
    
    # show me what is happening
    if DEBUG:
        print "Dealer", dealer_hand
    
    # assign dealer hand value for easy comparing
    d_value = dealer_hand.get_value()
    
    # game at an end ?
    # assign a message to outcome, update in_play and score
    if d_value >= DEALER_DRAWS_TO:
        # Stop further play
        in_play = False
        player_message = "New Deal ?"
        # Dealer loses to player ?
        if d_value < p_value:
            score += 1
            outcome = "You WON !!!"
        # Dealer beat player ?
        else:
            # ... only if not busted
            if d_value <= 21:
                score -= 1
                outcome = "Dealer won."
            # dealer busted = player wins
            else:
                score += 1
                outcome = "Dealer busted !!"
        
        # Show result
        if DEBUG:
            print "Result: P = " + str(p_value) + " vs D = " + str(d_value) + ")"

#========================================================
# draw handler    
def draw(canvas):
    global delay_timer
    
    # delay auto-play action
    delay_timer += 1
    if delay_timer >= MAX_DELAY_TIMER:
        delay_timer = 0
    
    # auto-play dealer hand
    if in_play and dealer_play:
        if delay_timer == dealer_play_time:
            dealer_draws()
    
    # draw both hands
    dealer_hand.draw(canvas, DRAW_DEALER)
    player_hand.draw(canvas, DRAW_PLAYER)
    
    # draw the outcome message
    # first draw fancy BlackJack: title thingy
    outcome_pos = DRAW_OUTCOME
    canvas.draw_text("Black", outcome_pos, OUTCOME_SIZE, "Black")
    outcome_offset = frame.get_canvas_textwidth("Black", OUTCOME_SIZE)
    outcome_pos = (DRAW_OUTCOME[0] + outcome_offset, DRAW_OUTCOME[1])
    canvas.draw_text("Jack", outcome_pos, OUTCOME_SIZE, "Red")
    outcome_offset = frame.get_canvas_textwidth("BlackJack", OUTCOME_SIZE)
    outcome_pos = (DRAW_OUTCOME[0] + outcome_offset, DRAW_OUTCOME[1])
    canvas.draw_text(": ", outcome_pos, OUTCOME_SIZE, "Black")
    # Now display message behind fancy BlackJack thingy
    outcome_offset = frame.get_canvas_textwidth("BlackJack: ", OUTCOME_SIZE)
    outcome_pos = (DRAW_OUTCOME[0] + outcome_offset, DRAW_OUTCOME[1])
    canvas.draw_text(outcome, outcome_pos, OUTCOME_SIZE, "Black")
    
    # Display score in corner
    score_string = "Score: "+str(score)
    score_width = frame.get_canvas_textwidth(score_string, SCORE_SIZE)
    score_pos = (DRAW_SCORE[0] - score_width, DRAW_SCORE[1])
    canvas.draw_text(score_string, score_pos, SCORE_SIZE, "White")
    
    # Display player_message at bottom
    canvas.draw_text(player_message, DRAW_MESSAGE, OUTCOME_SIZE, "White")

#==================================================
# initialization frame
frame = simplegui.create_frame("Blackjack", TABLE_WIDTH, TABLE_HEIGHT)
frame.set_canvas_background("Green")

#create buttons and canvas callback
frame.add_button("Deal", deal, 200)
frame.add_button("Hit",  hit, 200)
frame.add_button("Stand", stand, 200)
frame.set_draw_handler(draw)

# init objects 
deck = Deck()
player_hand = Hand()
dealer_hand = Hand()

# get things rolling
deal()
frame.start()

#====================================================
# remember to review the gradic rubric
