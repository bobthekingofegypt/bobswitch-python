from unittest2 import TestCase, main, skip

from bobswitch import models
from bobswitch import json_convert

class TestConvert(TestCase):

    def test_convert_card(self):
        card = models.Card(models.Suit.hearts, models.Rank.ace)

        card_converted = json_convert.convert_card(card)

        self.assertEquals(0, card_converted["suit"])
        self.assertEquals(1, card_converted["rank"])

    def test_convert_hand(self):
        card = models.Card(models.Suit.hearts, models.Rank.ace)
        card2 = models.Card(models.Suit.spades, models.Rank.four)

        hand = models.Hand()
        hand.add_card(card)
        hand.add_card(card2)

        hand_converted = json_convert.convert_hand(hand)

        self.assertEquals(0, hand_converted[0]["suit"])
        self.assertEquals(1, hand_converted[0]["rank"])
        self.assertEquals(3, hand_converted[1]["suit"])
        self.assertEquals(4, hand_converted[1]["rank"])
