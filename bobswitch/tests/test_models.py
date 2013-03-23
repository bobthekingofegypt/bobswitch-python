from unittest2 import TestCase, main, skip

from engine import models

class TestCard(TestCase):
    
    def test_init_valid(self):
        card = models.Card(models.Suit.hearts, models.Rank.ace) 

        self.assertEquals(card.suit, models.Suit.hearts, 
                "card should be a heart")
        self.assertEquals(card.rank, models.Rank.ace, 
                "card should be an ace")

    def test_init_invalid_suit(self):
        card = models.Card(models.Suit.hearts, models.Rank.ace) 
        self.failUnlessRaises(TypeError, models.Card, 1, models.Rank.ace)

    def test_init_invalid_rank(self):
        card = models.Card(models.Suit.hearts, models.Rank.ace) 
        self.failUnlessRaises(TypeError, models.Card, models.Suit.hearts, 1)

