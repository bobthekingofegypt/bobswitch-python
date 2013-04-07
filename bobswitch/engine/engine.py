import random
import os

from models import Deck, Card, Suit, Rank, Hand
from flufl.enum import Enum


class MoveType(Enum):
    pick = 0
    play = 1


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
    
    def __init__(self, players, number_of_cards, deck, starting_player=1):
        self.deck = deck 

        self.current_player = starting_player 
        self.player_hands = deal_player_hands(number_of_cards, players, deck)
        self.players = players

        self.top_card = self.deck.deal_card()

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
        current_player = self.players[self.current_player]
        if current_player.name != player_name:
            return invalid_play_response(("Not player %s's turn" % (player_name,)))

        #is move valid
        if not self._valid_move(move, current_player):
            return invalid_play_response("Not a valid move")


    def _valid_pick(self, player, top_card):
        return False

    def _valid_move(self, move, player, top_card):
        #check pick vs play
        if move.move_type == MoveType.pick:
            return _valid_pick(player, top_card)
        
        return False

         


    
    

