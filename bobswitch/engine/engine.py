import random
import os

from models import Deck, Card, Suit, Rank, Hand

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


def deal_player_hands(number_of_cards, players, deck, starting_player):
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


class Game(object):
    
    def __init__(self, players, number_of_cards, deck, starting_player=1):
        self.current_player = 1
        self.number_of_cards = number_of_cards
        self.deck = deck 

        self.player_hands = deal_player_hands(number_of_cards, players, deck, starting_player)
        self.players = players







    def state(self):
        """
        Return the state of the game
        """
        pass

    def play(self):
        """
        Take a move, validate it and respond back with a response
        """
        pass

    
    

