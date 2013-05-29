import random
import os

from models import Deck, Card, Suit, Rank, Hand, PlayedCards
from flufl.enum import Enum


class MoveType(Enum):
    pick = 0
    play = 1


class GameState(Enum):
    NORMAL = 0
    PICK = 1
    WAIT = 2

class GameDirection(Enum):
    clockwise = 0
    anticlockwise = 1


def create_deck():
    """
    Returns a deck populated with the standard 52 cards from a plain deck
    """
    rand = random.Random(os.urandom(4))
    deck = Deck(rand)
    for suit in Suit:
        for rank in Rank:
            deck.add_card(Card(suit, rank))
    
    return deck


def deal_player_hands(number_of_cards, players, deck):
    """
    creates a dictionary of player names to player hand objects and
    deals the number of cards requested one to each player at a time 
    to simulate a fair deal as if it was a real dealer dealing
    """
    player_hands = {}
    for player in players:
        player_hands[player.name] = PlayerHand(player)

    for _ in xrange(0, number_of_cards):
        for name, player_hand in player_hands.items():
            player_hand.hand.add_card(deck.deal_card())

    return player_hands


def valid_pick(hand, top_card, game_state):
    """
    Checks whether a pick would be valid given the hand sent, a pick
    is valid if the user doesn't have any cards of the same suit, rank
    or an ace. Cant pick when waiting due to an eight
    """
    if game_state == GameState.WAIT:
        return False

    matching_cards = [card for card in hand.cards 
            if card.suit == top_card.suit
            or card.rank == top_card.rank
            or card.rank == Rank.ace]

    return not (matching_cards) 


class PlayerHand(object):
    """
    Holder class to keep a link to player and hand together
    """

    def __init__(self, player):
        self.player = player
        self.hand = Hand()

    def __repr__(self):
        return "PlayerHand: player - %r, hand - %r" % (self.player, self.hand)


class GameMove(object):

    def __init__(self, move_type, card=None):
        self.move_type = move_type
        self.card = card


def invalid_play_response(message):
    play_response = PlayResponse(False)
    play_response.message = message

    return play_response

def valid_play_response():
    play_response = PlayResponse(True)

    return play_response


class PlayResponse(object):

    def __init__(self, success):
        self.success = success
        self.message = ""


class Game(object):

    """
    create state machine for game state
    NORMAL
    TWO
    FOUR
    EIGHT

    two, four and eight are blocking states
    """
    
    def __init__(self, players, number_of_cards, deck, starting_player=1):
        self.deck = deck 

        self.current_player = starting_player 
        self.player_hands = deal_player_hands(number_of_cards, players, deck)
        self.players = players

        self.played_cards = PlayedCards()
        self.played_cards.add_card(self.deck.deal_card())

        top_card = self.played_cards.top_card

        #set direction
        if top_card.rank == Rank.jack:
            self.direction = GameDirection.clockwise
        else:
            self.direction = GameDirection.anticlockwise

        #set state machine
        self.state = GameState.NORMAL
        self.accumulated_count = 0

        if top_card.rank == Rank.two:
            self.state = GameState.PICK
            self.accumulated_count = 2
        elif top_card.rank == Rank.four:
            self.state = GameState.PICK
            self.accumulated_count = 4
        elif top_card.rank == Rank.eight:
            self.state = GameState.WAIT



    def player_hand(self, player_name):
        """
        Return a list of a players cards
        """
        return self.player_hands[player_name].hand

    def state(self):
        """
        Return the state of the game
        """

        #game state
        """
        whose turn it is
        top card
        player counts
        """
        pass

    def play(self, player_name, move):
        """
        Take a move, validate it and respond back with a response
        """
        current_player = self.players[self.current_player-1]
        if current_player.name != player_name:
            return invalid_play_response(("Not player %s's turn" % (player_name,)))

        #is move valid
        hand = self.player_hand(current_player.name)
        if not self.valid_move(move, hand, self.played_cards.top_card):
            return invalid_play_response("Not a valid move")

        if move.move_type == MoveType.pick:
            card_count = 1
            if self.state == GameState.PICK:
                card_count = self.accumulated_count
                self.accumulated_count = 0
                self.state = GameState.NORMAL

            for _ in xrange(card_count):
                self.pick(hand)

        return valid_play_response()
            

    def pick(self, hand):
        if not self.deck.has_card():
            cards = self.played_cards.return_played_cards()
            self.deck.add_cards(cards)

            self.deck.shuffle()

        card = self.deck.deal_card()
        hand.add_card(card)

    def valid_play(self, card, hand, top_card):
        #if card is in hand and card is same suit as top_card or rank matches or its a trick card
        if not hand.contains_card(move.card): 
            return False

        #if not in trick card state
        #if card.rank == top_card.rank
        return True

    def valid_move(self, move, hand, top_card):
        #check pick vs play
        if move.move_type == MoveType.pick:
            return valid_pick(hand, top_card, self.state)
        
        return self.valid_play(card, player, top_card)

         


    
    

