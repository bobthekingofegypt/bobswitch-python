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
    Represents a card from a standard deck of cards, eg- ace of clubs
    """

    def __init__(self, suit, rank):
        """
        suit and rank must be of the enum type Rank and Card, if they
        are not a TypeError will be raised.
        """
        if suit not in Suit:
            raise TypeError("suit argument must be off type Suit")
        if rank not in Rank:
            raise TypeError("rank argument must be off type Rank")

        self.suit = suit
        self.rank = rank

    def __eq__(self, other):
        return (self.suit == other.suit and self.rank == other.rank)

    def __neq__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "Card: suit - %r, rank - %r" % (self.suit.name, self.rank.name)


class Hand(object):
    """
    Represents a set of cards 
    """

    def __init__(self):
        self.cards = []


    def add_card(self, card):
        """
        adds the given card to the hand
        """
        self.cards.append(card)

    def contains_card(self, card):
        """
        Returns True if hand contains passed card
        """
        return card in self.cards

    def remove_card(self, card):
        """
        Returns True if the card was removed from the hand, returns
        False if the card was not present
        """
        if self.contains_card(card):
            self.cards.remove(card)
            return True
        
        return False


class Deck(object):
    """
    represents the cards still to play and their order
    """
    def banana(self):
        print "test"


class PlayedCards(object):
    """
    represents the played cards
    """
    pass


