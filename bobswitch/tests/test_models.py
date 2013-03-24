from unittest2 import TestCase, main, skip

from engine import models

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


class TestHand(TestCase):

    def test_init(self):
        hand = models.Hand()
        self.assertEquals(0, len(hand.cards))
        

    def test_add_card(self):
        hand = models.Hand()
        hand.add_card(models.Card(models.Suit.hearts, models.Rank.ace))

        self.assertEquals(1, len(hand.cards))

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
