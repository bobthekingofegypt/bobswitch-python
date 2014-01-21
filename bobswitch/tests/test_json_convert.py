from unittest2 import TestCase, main, skip

from bobswitch import models
from bobswitch import engine 
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

    def test_convert_state_start(self):
        card = models.Card(models.Suit.hearts, models.Rank.ace)
        card2 = models.Card(models.Suit.spades, models.Rank.four)

        hand = models.Hand()
        hand.add_card(card)
        hand.add_card(card2)

        top = models.Card(models.Suit.spades, models.Rank.ace)

        bob_hand = engine.PlayerHand("bob")
        bob_hand.hand.add_card(card)
        bob_hand.hand.add_card(card)
        bob_hand.hand.add_card(card)
        bob_hand.hand.add_card(card)

        scott_hand = engine.PlayerHand("scott")
        scott_hand.hand.add_card(card)
        scott_hand.hand.add_card(card)
        scott_hand.hand.add_card(card)

        players = [models.Player("bob"), models.Player("scott")]
        player_hands = {
                "bob": bob_hand,
                "scott": scott_hand
        }

        state_converted = json_convert.convert_state_start(engine.GameState.WAIT, players,
                                player_hands, 1, top, hand)

        self.assertEquals(2, state_converted["number_of_players"])
        self.assertEquals(2, len(state_converted["hand"]))
        self.assertEquals(0, state_converted["hand"][0]["suit"])
        self.assertEquals(1, state_converted["starting_player"])
        self.assertEquals(3, state_converted["top_card"]["suit"])
        self.assertEquals(1, state_converted["top_card"]["rank"])

        players = state_converted["players"]
        player_one = players[0]
        player_two = players[1]

        self.assertEquals("bob", player_one["name"])
        self.assertEquals(4, player_one["count"])
        
        self.assertEquals("scott", player_two["name"])
        self.assertEquals(3, player_two["count"])

        self.assertEquals("wait", state_converted["state"])
