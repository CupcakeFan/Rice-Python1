# Mini-project #6 - Blackjack

import simplegui
import random
import time

# load card sprite - 936x384 - source: jfitz.com
CARD_SIZE = (72, 96)
CARD_CENTER = (36, 48)
card_images = simplegui.load_image("http://storage.googleapis.com/codeskulptor-assets/cards_jfitz.png")

CARD_BACK_SIZE = (72, 96)
CARD_BACK_CENTER = (36, 48)
card_back = simplegui.load_image("http://storage.googleapis.com/codeskulptor-assets/card_jfitz_back.png")    

SCORE_SIZE = 24
OUTCOME_SIZE = 32
MAX_DELAY_TIMER = 90

# initialize some useful global variables
in_play = False
outcome = ""
score = 0
hide_dealer = False
delay_timer = 0
dealer_play_time = MAX_DELAY_TIMER + 1
selected_back = 0

# define globals for cards
SUITS = ('C', 'S', 'H', 'D')
RANKS = ('A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K')
VALUES = {'A':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'T':10, 'J':10, 'Q':10, 'K':10}

def switch_backs():
    global selected_back
    
    selected_back = 1 - selected_back

# define card class
class Card:
    def __init__(self, suit, rank):
        if (suit in SUITS) and (rank in RANKS):
            self.suit = suit
            self.rank = rank
        else:
            self.suit = None
            self.rank = None
            print "Invalid card: ", suit, rank

    def __str__(self):
        return self.suit + self.rank

    def get_suit(self):
        return self.suit

    def get_rank(self):
        return self.rank

    def draw(self, canvas, pos):
        card_loc = (CARD_CENTER[0] + CARD_SIZE[0] * RANKS.index(self.rank), 
                    CARD_CENTER[1] + CARD_SIZE[1] * SUITS.index(self.suit))
        canvas.draw_image(card_images, card_loc, CARD_SIZE, [pos[0] + CARD_CENTER[0], pos[1] + CARD_CENTER[1]], CARD_SIZE)
        
# define hand class
class Hand:
    def __init__(self):
        # create Hand object
        self.drop_cards()
        
    def drop_cards(self):
        self.cards = []

    def __str__(self):
        # return a string representation of a hand
        string = "Hand: " + str(self.get_value())
        for i in range(len(self.cards)):
            string = string + " " + str(self.cards[i])
        return string

    def add_card(self, card):
        # add a card object to a hand
        self.cards.append(card)
        
    def get_value(self):
        # count aces as 1, if the hand has an ace, then add 10 to hand value if it doesn't bust
        # compute the value of the hand, see Blackjack video
        value = 0
        has_ace = False
        for card in self.cards:
            value += VALUES[card.get_rank()]
            if card.get_rank() == 'A':
                has_ace = True
        if has_ace:
            if value < 12:
                value += 10
        return value
    
    def draw(self, canvas, pos):
        # draw a hand on the canvas, use the draw method for cards
        offset = 100
        for card in self.cards:
            card.draw(canvas, pos)
            pos[0] += offset
            offset = CARD_SIZE[0] * 3 / 4

        
# define deck class 
class Deck:
    def __init__(self):
        # create a Deck object
        self.refresh_deck()
        
    def refresh_deck(self):
        self.cards = []
        switch_backs()
        for suit in SUITS:
            for rank in RANKS:
                self.cards.append(Card(suit, rank))
        
    def shuffle(self):
        # shuffle the deck 
        # use random.shuffle()
        random.shuffle(self.cards)

    def deal_card(self):
        # deal a card object from the deck
        if len(self.cards) < 1:
            self.refresh_deck()
            self.shuffle()
        return self.cards.pop(-1)
            
    def __str__(self):
        # return a string representing the deck
        string = "Deck: " + str(self.cards[0])
        for i in range(1, len(self.cards)):
            string = string + " " + str(self.cards[i])
        return string


# test bits
card = Card("S", "A")
deck = Deck()
print deck
deck.shuffle()
print deck

player_hand = Hand()
dealer_hand = Hand()


#define event handlers for buttons
def deal():
    global outcome, in_play, hide_dealer, dealer_play_time

    # your code goes here
    global player_hand, dealer_hand, deck
    
    player_hand.drop_cards()
    dealer_hand.drop_cards()
    
    player_hand.add_card(deck.deal_card())
    dealer_hand.add_card(deck.deal_card())
    player_hand.add_card(deck.deal_card())
    dealer_hand.add_card(deck.deal_card())
    
    print player_hand
    
    hide_dealer = True
    in_play = True
    dealer_play_time = MAX_DELAY_TIMER + 1
    outcome = "Blackjack: Let's Play !"

def hit():
    # replace with your code below
    global score, in_play, outcome
    global player_hand
    
    # if the hand is in play, hit the player
    if in_play:
        player_hand.add_card(deck.deal_card())
    
    outcome = "Blackjack: You got " + str(player_hand.get_value())
    #outcome = "Blackjack: Dealer draws to 17..."
    
    # if busted, assign a message to outcome, update in_play and score
    if in_play and (player_hand.get_value() > 21):
        in_play = False
        score -= 1
        outcome = "BlackJack: You busted !!"

def stand():
    global hide_dealer, outcome, dealer_play_time
    
    if in_play:
        dealer_play_time = delay_timer
        outcome = "Blackjack: Dealer draws to 17..."
        hide_dealer = False
        
    
def dealer_draws():
    # replace with your code below
    global dealer_hand
    global score, outcome, in_play
    
    # if hand is in play, repeatedly hit dealer until his hand has value 17 or more
    if in_play:
        if dealer_hand.get_value() < 17:
            if dealer_hand.get_value() >= player_hand.get_value():
                in_play = False
            else:
                dealer_hand.add_card(deck.deal_card())
                if dealer_hand.get_value() > 21:
                    in_play = False
        else:
            in_play = False
    
    # assign a message to outcome, update in_play and score
    if not in_play:
        if dealer_hand.get_value() < player_hand.get_value():
            score += 1
            outcome = "Blackjack: You WON !!!"
        else:
            if dealer_hand.get_value() <= 21:
                score -= 1
                outcome = "Blackjack: Dealer won."
            else:
                score += 1
                outcome = "BlackJack: Dealer busted !!"
        

# draw handler    
def draw(canvas):
    # test to make sure that card.draw works, replace with your code below
    #global card
    #card.draw(canvas, [300, 300])
    
    global delay_timer
    
    delay_timer += 1
    if delay_timer >= MAX_DELAY_TIMER:
        delay_timer = 0
        
    if in_play and not hide_dealer:
        if delay_timer == dealer_play_time:
            dealer_draws()
    
    
    dealer_hand.draw(canvas, [100 - CARD_CENTER[0], 150 - CARD_CENTER[1]])
    player_hand.draw(canvas, [100 - CARD_CENTER[0], 450 - CARD_CENTER[1]])
    pos = [100, 150]
    if hide_dealer:
        canvas.draw_image(card_back, [CARD_CENTER[0] + selected_back * CARD_SIZE[0], CARD_CENTER[1]], CARD_SIZE, pos, CARD_SIZE)
        
    canvas.draw_text(outcome, (50, 300), OUTCOME_SIZE, "Black")
    score_string = "Score: "+str(score)
    score_width = frame.get_canvas_textwidth(score_string, SCORE_SIZE)
    canvas.draw_text(score_string,(550 - score_width, 50), SCORE_SIZE, "White")

# initialization frame
frame = simplegui.create_frame("Blackjack", 600, 600)
frame.set_canvas_background("Green")

#create buttons and canvas callback
frame.add_button("Deal", deal, 200)
frame.add_button("Hit",  hit, 200)
frame.add_button("Stand", stand, 200)
frame.set_draw_handler(draw)


# get things rolling
deal()
frame.start()


# remember to review the gradic rubric