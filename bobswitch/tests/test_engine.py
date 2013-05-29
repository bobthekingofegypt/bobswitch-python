from engine import engine, models
from unittest2 import TestCase, main, skip


def populate_known_deck():
    deck = models.Deck(None)
    deck.add_card(models.Card(models.Suit.clubs, models.Rank.seven))
    deck.add_card(models.Card(models.Suit.clubs, models.Rank.five))
    deck.add_card(models.Card(models.Suit.clubs, models.Rank.four))
    deck.add_card(models.Card(models.Suit.clubs, models.Rank.three))
    deck.add_card(models.Card(models.Suit.clubs, models.Rank.two))
    deck.add_card(models.Card(models.Suit.clubs, models.Rank.king))
    deck.add_card(models.Card(models.Suit.clubs, models.Rank.queen))
    deck.add_card(models.Card(models.Suit.clubs, models.Rank.jack))
    deck.add_card(models.Card(models.Suit.clubs, models.Rank.ten))

    return deck


class TestCreateDeck(TestCase):

    def test_create_deck(self):
        deck = engine.create_deck()

        self.assertEquals(52, deck.number_of_cards())


class TestDealPlayerHands(TestCase):

    def test_deal_player_hands(self):
        deck = engine.create_deck()
        player = models.Player("bob")
        player_two = models.Player("john")

        player_hands = engine.deal_player_hands(7, [player, player_two,], 
                deck)

        self.assertEquals(2, len(player_hands))

        player_hand_one = player_hands[player.name]
        self.assertEquals(player, player_hand_one.player)
        self.assertEquals(7, player_hand_one.hand.number_of_cards())

        player_hand_two = player_hands[player_two.name]
        self.assertEquals(player_two, player_hand_two.player)
        self.assertEquals(7, player_hand_two.hand.number_of_cards())

    def test_deal_player_hands_order(self):
        deck = models.Deck(None) 
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.seven))
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.five))
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.four))
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.three))
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.two))
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.king))
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.queen))
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.jack))
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.ten))

        player = models.Player("bob")
        player_two = models.Player("john")

        player_hands = engine.deal_player_hands(3, [player, player_two,], 
                deck)

        self.assertEquals(2, len(player_hands))

        player_hand_one = player_hands[player.name]
        self.assertEquals(player, player_hand_one.player)
        self.assertEquals(3, player_hand_one.hand.number_of_cards())
        self.assertEquals(models.Card(models.Suit.clubs, models.Rank.ten),
                            player_hand_one.hand.cards[0])
        self.assertEquals(models.Card(models.Suit.clubs, models.Rank.queen),
                            player_hand_one.hand.cards[1])
        self.assertEquals(models.Card(models.Suit.clubs, models.Rank.two),
                            player_hand_one.hand.cards[2])


        player_hand_two = player_hands[player_two.name]
        self.assertEquals(player_two, player_hand_two.player)
        self.assertEquals(3, player_hand_two.hand.number_of_cards())
        self.assertEquals(models.Card(models.Suit.clubs, models.Rank.jack),
                            player_hand_two.hand.cards[0])
        self.assertEquals(models.Card(models.Suit.clubs, models.Rank.king),
                            player_hand_two.hand.cards[1])
        self.assertEquals(models.Card(models.Suit.clubs, models.Rank.three),
                            player_hand_two.hand.cards[2])


class TestPlayerHand(TestCase):
    
    def test_init(self):
        player = models.Player("bob")
        player_hand = engine.PlayerHand(player)

        self.assertEquals(player, player_hand.player)
        self.assertEquals(0, player_hand.hand.number_of_cards())


class TestGame(TestCase):

    def test_init(self):
        player = models.Player("bob")
        player_two = models.Player("john")

        players = [player, player_two,]

        deck = populate_known_deck()

        game = engine.Game(players, 2, deck)

        self.assertEquals(1, game.current_player)
        self.assertEquals(players, game.players)

        self.assertEquals(4, game.deck.number_of_cards())
        self.assertEquals(models.Card(models.Suit.clubs, models.Rank.two), game.top_card)

    def test_init_starting_player(self):
        player = models.Player("bob")
        player_two = models.Player("john")

        players = [player, player_two,]

        deck = populate_known_deck()

        game = engine.Game(players, 2, deck, 2)

        self.assertEquals(2, game.current_player)

    def test_player_hand(self):
        player = models.Player("bob")
        player_two = models.Player("john")

        players = [player, player_two,]

        deck = populate_known_deck()

        game = engine.Game(players, 2, deck)

        player_hand = game.player_hand("bob")

        self.assertEquals(models.Card(models.Suit.clubs, models.Rank.ten), player_hand.cards[0])
        self.assertEquals(models.Card(models.Suit.clubs, models.Rank.queen), player_hand.cards[1])

    def test_play_wrong_player(self):
        player = models.Player("bob")
        player_two = models.Player("john")

        players = [player, player_two,]

        deck = populate_known_deck()

        game = engine.Game(players, 2, deck)

        play_response = game.play("john", None)

        self.assertEquals(False, play_response.success)

    def test_valid_move_pick(self):
        player = models.Player("bob")
        player_two = models.Player("john")

        players = [player, player_two,]

        deck = populate_known_deck()

        game = engine.Game(players, 2, deck)

        move = engine.GameMove(engine.MoveType.pick)

        play_response = game.play("bob", move)

        self.assertEquals(True, play_response.success)

