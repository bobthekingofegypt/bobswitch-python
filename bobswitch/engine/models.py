from flufl.enum import Enum

class Suit(Enum):
    hearts = 0
    clubs = 1
    diamonds = 2
    spades = 3

class Rank(Enum):
    ace = 1
    two = 2
    three = 3
    four = 4
    five = 5
    six = 6
    seven = 7
    eight = 8
    nine = 9
    ten = 10
    jack = 11
    queen = 12
    king = 13

class Room(object):
    """
    Represents a group of players, and there scores for this session
    """
    pass


class Card(object):
    """
    represents a card
    """
    def __init__(self, suit, rank):
        if suit not in Suit:
            raise TypeError("suit argument must be off type Suit")
        if rank not in Rank:
            raise TypeError("rank argument must be off type Rank")

        self.suit = suit
        self.rank = rank

class Deck(object):
    """
    represents the cards still to play and their order
    """
    def banana(self):
        print "test"

class Hand(object):
    """
    represents a set of cards the player is currently playing
    """
    pass

class PlayedCards(object):
    """
    represents the played cards
    """
    pass


