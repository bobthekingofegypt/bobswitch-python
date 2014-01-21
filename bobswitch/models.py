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

class Player(object):
    """
    Represents a player in the room
    """

    def __init__(self, name):
        """
        name player has chosen for the game
        """
        self.name = name

    def __repr__(self):
        return "Player: name - %r" % (self.name,)


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


class CardGroup(object):
    """
    Base class for a groups of cards such as Hands, Decks etc
    """
    def __init__(self):
        self.cards = []
    
    def add_card(self, card):
        """
        adds the given card to the hand
        """
        self.cards.append(card)

    def add_cards(self, cards):
        """
        adds the given cards to the hand
        """
        self.cards.extend(cards)

    def number_of_cards(self):
        return len(self.cards)

    def contains_card(self, card):
        """
        Returns True if hand contains passed card
        """
        return card in self.cards


class Hand(CardGroup):
    """
    Represents a set of cards 
    """

    def __init__(self):
        super(Hand,self).__init__()

    def remove_card(self, card):
        """
        Returns True if the card was removed from the hand, returns
        False if the card was not present
        """
        if self.contains_card(card):
            self.cards.remove(card)
            return True
        
        return False

    def __repr__(self):
        return "Hand: %r" % (self.cards,)


class Deck(CardGroup):
    """
    represents a deck of cards stored in an order
    """

    def __init__(self, random):
        super(Deck,self).__init__()

        self.random = random

    def deal_card(self):
        return self.cards.pop()

    def shuffle(self):
        self.random.shuffle(self.cards)
        self.random.shuffle(self.cards)
        self.random.shuffle(self.cards)

    def has_card(self):
        return self.number_of_cards() != 0

    def __repr__(self):
        return "Cards: %r" % (self.cards)



class PlayedCards(CardGroup):
    """
    represents the played cards
    """
    def __init__(self):
        super(PlayedCards,self).__init__()

        self.top_card = None

    def add_card(self, card, suit_override=None):
        """
        adds the given card to the hand
        """
        if self.top_card:
            super(PlayedCards, self).add_card(self.top_card)
            self.top_card = card
        else:
            self.top_card = card

        if suit_override:
            self.top_card.suit = suit_override

    def return_played_cards(self):
        old_cards = self.cards
        self.cards = []
        return old_cards






