import random
import os

from models import Deck, Card, Suit, Rank, Hand
from flufl.enum import Enum


class MoveType(Enum):
    pick = 0
    play = 1


class GameState(Enum):
    NORMAL = 0
    TWO = 1
    FOUR = 2
    EIGHT = 3

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

        self.top_card = self.deck.deal_card()

        #set direction
        if self.top_card.rank == Rank.jack:
            self.direction = GameDirection.clockwise
        else:
            self.direction = GameDirection.anticlockwise

        #set state machine
        self.state = GameState.NORMAL
        if self.top_card.rank == Rank.two:
            self.state = GameState.TWO
        else if self.top_card.rank == Rank.four:
            self.state = GameState.FOUR
        else if self.top_card.rank == Rank.eight:
            self.state = GameState.EIGHT


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
        if not self.valid_move(move, hand, self.top_card):
            return invalid_play_response("Not a valid move")


    def valid_pick(self, hand, top_card):
        #if player hand does not contain same suit or rank it is valid
        matching_suits = [card for card in hand.cards if card.suit == top_card.suit]
        matching_values = [card for card in hand.cards if card.rank == top_card.rank]

        return not (matching_suits or matching_values) 

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
            return self.valid_pick(hand, top_card)
        
        return self.valid_play(card, player, top_card)

         


    
    

