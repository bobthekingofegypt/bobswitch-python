

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
        self.suit = suit
        self.rank = rank

class Deck(object):
    """
    represents the cards still to play and their order
    """
    pass

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


