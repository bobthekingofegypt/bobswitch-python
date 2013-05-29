import random

from unittest2 import TestCase, main, skip

from engine import models

class TestPlayer(TestCase):

    def test_init(self):
        player = models.Player("bob")

        self.assertEquals("bob", player.name)

class TestCard(TestCase):
    
    def test_init_valid(self):
        card = models.Card(models.Suit.hearts, models.Rank.ace) 

        self.assertEquals(models.Suit.hearts, card.suit, 
                "card should be a heart")
        self.assertEquals(models.Rank.ace, card.rank,
                "card should be an ace")

    def test_init_invalid_suit(self):
        card = models.Card(models.Suit.hearts, models.Rank.ace) 
        self.failUnlessRaises(TypeError, models.Card, 1, models.Rank.ace)

    def test_init_invalid_rank(self):
        card = models.Card(models.Suit.hearts, models.Rank.ace) 
        self.failUnlessRaises(TypeError, models.Card, models.Suit.hearts, 1)

    def test_repr(self):
        card = models.Card(models.Suit.hearts, models.Rank.ace) 
        self.assertEquals("Card: suit - 'hearts', rank - 'ace'", card.__repr__())

    def test_eq(self):
        card = models.Card(models.Suit.hearts, models.Rank.ace) 
        card2 = models.Card(models.Suit.hearts, models.Rank.ace) 

        self.assertEquals(card, card2)

    def test_neq_suit(self):
        card = models.Card(models.Suit.hearts, models.Rank.ace) 
        card2 = models.Card(models.Suit.clubs, models.Rank.ace) 

        self.assertNotEquals(card, card2)
    
    def test_neq_rank(self):
        card = models.Card(models.Suit.hearts, models.Rank.ace) 
        card2 = models.Card(models.Suit.hearts, models.Rank.two) 

        self.assertNotEquals(card, card2)
    
    def test_neq_both(self):
        card = models.Card(models.Suit.hearts, models.Rank.ace) 
        card2 = models.Card(models.Suit.spades, models.Rank.two) 

        self.assertNotEquals(card, card2)


class TestCardGroup(TestCase):

    def test_init(self):
        card_group = models.CardGroup()
        self.assertEquals(0, len(card_group.cards))

    def test_add_card(self):
        card_group = models.CardGroup()
        card_group.add_card(models.Card(models.Suit.hearts, models.Rank.ace))

        self.assertEquals(1, len(card_group.cards))

    def test_add_cards(self):
        card_group = models.CardGroup()
        cards = [models.Card(models.Suit.hearts, models.Rank.ace),
                 models.Card(models.Suit.hearts, models.Rank.two)]
        card_group.add_cards(cards)

        self.assertEquals(2, len(card_group.cards))

    def test_card_count_empty(self):
        card_group = models.CardGroup()

        self.assertEquals(0, card_group.number_of_cards())

    def test_card_count_not_empty(self):
        card_group = models.CardGroup()

        card = models.Card(models.Suit.clubs, models.Rank.ace)
        card_group.add_card(card)

        self.assertEquals(1, card_group.number_of_cards())


class TestHand(TestCase):

    def test_init(self):
        hand = models.Hand()
        self.assertEquals(0, len(hand.cards))

    def test_contains(self):
        hand = models.Hand()
        hand.add_card(models.Card(models.Suit.hearts, models.Rank.ace))

        card = models.Card(models.Suit.hearts, models.Rank.ace)
        self.assertTrue(hand.contains_card(card))

    def test_doesnt_contains(self):
        hand = models.Hand()
        hand.add_card(models.Card(models.Suit.hearts, models.Rank.ace))

        card = models.Card(models.Suit.clubs, models.Rank.ace)
        self.assertFalse(hand.contains_card(card))

    def test_remove_card(self):
        hand = models.Hand()
        hand.add_card(models.Card(models.Suit.hearts, models.Rank.ace))

        card = models.Card(models.Suit.hearts, models.Rank.ace)
        result = hand.remove_card(card)
        self.assertTrue(result)
        self.assertEquals(0, len(hand.cards))

    def test_remove_card_failure(self):
        hand = models.Hand()
        hand.add_card(models.Card(models.Suit.hearts, models.Rank.ace))

        card = models.Card(models.Suit.clubs, models.Rank.ace)
        result = hand.remove_card(card)
        self.assertFalse(result)
        self.assertEquals(1, len(hand.cards))


class TestPlayedCards(TestCase):

    def test_init(self):
        played_cards = models.PlayedCards()
        self.assertEquals(0, len(played_cards.cards))

        self.assertIsNone(played_cards.top_card)

    def test_add_card_first_time(self):
        played_cards = models.PlayedCards()
        
        card = models.Card(models.Suit.hearts, models.Rank.ace) 
        played_cards.add_card(card)

        self.assertEquals(0, len(played_cards.cards))
        self.assertEquals(card, played_cards.top_card)
    
    def test_add_card_second_time(self):
        played_cards = models.PlayedCards()
        
        card = models.Card(models.Suit.hearts, models.Rank.ace) 
        played_cards.add_card(card)

        self.assertEquals(0, len(played_cards.cards))
        self.assertEquals(card, played_cards.top_card)

        card2 = models.Card(models.Suit.clubs, models.Rank.ace) 
        played_cards.add_card(card2)

        self.assertEquals(1, len(played_cards.cards))
        self.assertTrue(played_cards.contains_card(card))
        self.assertEquals(card2, played_cards.top_card)

class TestDeck(TestCase):

    def test_init(self):
        deck = models.Deck(None)

        self.assertEquals(0, len(deck.cards))

    def test_has_card_empty(self):
        deck = models.Deck(None)

        self.assertFalse(deck.has_card())

    def test_has_card(self):
        deck = models.Deck(None)
        deck.add_card(models.Card(models.Suit.hearts, models.Rank.ace))

        self.assertTrue(deck.has_card())

    def test_deal_card_empty(self):
        deck = models.Deck(None)
        
        self.failUnlessRaises(IndexError, deck.deal_card)

    def test_deal_card(self):
        deck = models.Deck(None)
        deck.add_card(models.Card(models.Suit.hearts, models.Rank.ace))
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.ace))
        deck.add_card(models.Card(models.Suit.diamonds, models.Rank.ace))

        card = deck.deal_card()

        self.assertEquals(models.Card(models.Suit.diamonds, models.Rank.ace), card)

    def test_shuffle(self):
        rand = random.Random(64)
        deck = models.Deck(rand)
        
        deck.add_card(models.Card(models.Suit.hearts, models.Rank.ace))
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.ace))
        deck.add_card(models.Card(models.Suit.diamonds, models.Rank.ace))
        deck.add_card(models.Card(models.Suit.hearts, models.Rank.two))
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.two))
        deck.add_card(models.Card(models.Suit.diamonds, models.Rank.two))
        
        Suit = models.Suit
        Rank = models.Rank

        deck.shuffle()

        self.assertEquals(models.Card(Suit.clubs, Rank.ace), deck.deal_card())
        self.assertEquals(models.Card(Suit.hearts, Rank.two), deck.deal_card())
        self.assertEquals(models.Card(Suit.hearts, Rank.ace), deck.deal_card())


    def test_shuffle_deck_isolation(self):
        """
        Playing two decks should not effect each deck
        Redo shuffle test with another decks moves intersperced
        """
        rand = random.Random(64)
        deck = models.Deck(rand)
        
        deck.add_card(models.Card(models.Suit.hearts, models.Rank.ace))
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.ace))
        deck.add_card(models.Card(models.Suit.diamonds, models.Rank.ace))
        deck.add_card(models.Card(models.Suit.hearts, models.Rank.two))
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.two))
        deck.add_card(models.Card(models.Suit.diamonds, models.Rank.two))
        
        rand2 = random.Random(8765)
        deck2 = models.Deck(rand2)

        deck2.add_card(models.Card(models.Suit.hearts, models.Rank.ace))
        deck2.add_card(models.Card(models.Suit.clubs, models.Rank.ace))
        deck2.add_card(models.Card(models.Suit.diamonds, models.Rank.ace))
        deck2.add_card(models.Card(models.Suit.hearts, models.Rank.two))

        deck2.shuffle()
        
        Suit = models.Suit
        Rank = models.Rank

        deck.shuffle()

        self.assertEquals(models.Card(Suit.clubs, Rank.ace), deck.deal_card())
        self.assertEquals(models.Card(Suit.hearts, Rank.two), deck.deal_card())
        self.assertEquals(models.Card(Suit.hearts, Rank.ace), deck.deal_card())
