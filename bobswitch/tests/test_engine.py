from engine import engine, models
from unittest2 import TestCase, main, skip
from mock import Mock


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


class TestValidPlays(TestCase):

    def test_pick_have_suit(self):
        hand = engine.Hand()
        hand.add_card(models.Card(models.Suit.clubs, models.Rank.seven))

        top_card = models.Card(models.Suit.clubs, models.Rank.four)

        self.assertFalse(engine.valid_pick(hand, top_card, engine.GameState.NORMAL))

    def test_pick_dont_have_suit(self):
        hand = engine.Hand()
        hand.add_card(models.Card(models.Suit.clubs, models.Rank.seven))
        hand.add_card(models.Card(models.Suit.clubs, models.Rank.four))

        top_card = models.Card(models.Suit.hearts, models.Rank.five)

        self.assertTrue(engine.valid_pick(hand, top_card, engine.GameState.NORMAL))

    def test_pick_have_rank(self):
        hand = engine.Hand()
        hand.add_card(models.Card(models.Suit.clubs, models.Rank.seven))
        hand.add_card(models.Card(models.Suit.clubs, models.Rank.four))

        top_card = models.Card(models.Suit.hearts, models.Rank.seven)

        self.assertFalse(engine.valid_pick(hand, top_card, engine.GameState.NORMAL))

    def test_pick_dont_have_rank(self):
        hand = engine.Hand()
        hand.add_card(models.Card(models.Suit.clubs, models.Rank.seven))
        hand.add_card(models.Card(models.Suit.clubs, models.Rank.four))

        top_card = models.Card(models.Suit.clubs, models.Rank.seven)

        self.assertFalse(engine.valid_pick(hand, top_card, engine.GameState.NORMAL))

    def test_pick_have_ace(self):
        hand = engine.Hand()
        hand.add_card(models.Card(models.Suit.clubs, models.Rank.ace))
        hand.add_card(models.Card(models.Suit.clubs, models.Rank.four))

        top_card = models.Card(models.Suit.hearts, models.Rank.seven)

        self.assertFalse(engine.valid_pick(hand, top_card, engine.GameState.NORMAL))

    def test_pick_when_in_wait(self):
        hand = engine.Hand()
        hand.add_card(models.Card(models.Suit.clubs, models.Rank.ace))
        hand.add_card(models.Card(models.Suit.clubs, models.Rank.four))

        top_card = models.Card(models.Suit.clubs, models.Rank.eight)

        self.assertFalse(engine.valid_pick(hand, top_card, engine.GameState.WAIT))


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
        self.assertEquals(models.Card(models.Suit.clubs, models.Rank.two), 
                game.played_cards.top_card)

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

        deck = models.Deck(None)
        deck.add_card(models.Card(models.Suit.hearts, models.Rank.seven))
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.five))
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.six))
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.three))
        deck.add_card(models.Card(models.Suit.diamonds, models.Rank.two))

        game = engine.Game(players, 1, deck)

        move = engine.GameMove(engine.MoveType.pick)

        play_response = game.play("bob", move)

        self.assertEquals(True, play_response.success)


    def test_valid_move_pick_two(self):
        player = models.Player("bob")
        player_two = models.Player("john")

        players = [player, player_two,]

        deck = models.Deck(None)
        deck.add_card(models.Card(models.Suit.hearts, models.Rank.seven))
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.five))
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.two))
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.three))
        deck.add_card(models.Card(models.Suit.diamonds, models.Rank.king))

        game = engine.Game(players, 1, deck)

        move = engine.GameMove(engine.MoveType.pick)

        play_response = game.play("bob", move)

        self.assertTrue(play_response.success)
        self.assertEquals(3, game.player_hand("bob").number_of_cards())

    def test_valid_move_pick_four(self):
        player = models.Player("bob")
        player_two = models.Player("john")

        players = [player, player_two,]

        deck = models.Deck(None)
        deck.add_card(models.Card(models.Suit.spades, models.Rank.seven))
        deck.add_card(models.Card(models.Suit.spades, models.Rank.five))
        deck.add_card(models.Card(models.Suit.hearts, models.Rank.seven))
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.five))
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.four))
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.three))
        deck.add_card(models.Card(models.Suit.diamonds, models.Rank.king))

        game = engine.Game(players, 1, deck)

        move = engine.GameMove(engine.MoveType.pick)

        play_response = game.play("bob", move)

        self.assertTrue(play_response.success)
        self.assertEquals(5, game.player_hand("bob").number_of_cards())

    def test_start_state_with_two(self):
        player = models.Player("bob")
        player_two = models.Player("john")

        players = [player, player_two,]

        deck = models.Deck(None)
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.two))
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.three))
        deck.add_card(models.Card(models.Suit.diamonds, models.Rank.two))

        game = engine.Game(players, 1, deck)

        self.assertEquals(2, game.accumulated_count)
        self.assertEquals(engine.GameState.PICK, game.state)

    def test_start_state_with_four(self):
        player = models.Player("bob")
        player_two = models.Player("john")

        players = [player, player_two,]

        deck = models.Deck(None)
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.four))
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.three))
        deck.add_card(models.Card(models.Suit.diamonds, models.Rank.two))

        game = engine.Game(players, 1, deck)

        self.assertEquals(4, game.accumulated_count)
        self.assertEquals(engine.GameState.PICK, game.state)

    def test_start_state_with_eight(self):
        player = models.Player("bob")
        player_two = models.Player("john")

        players = [player, player_two,]

        deck = models.Deck(None)
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.eight))
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.three))
        deck.add_card(models.Card(models.Suit.diamonds, models.Rank.two))

        game = engine.Game(players, 1, deck)

        self.assertEquals(0, game.accumulated_count)
        self.assertEquals(engine.GameState.WAIT, game.state)

    def test_pick_card(self):
        player = models.Player("bob")
        player_two = models.Player("john")

        players = [player, player_two,]

        deck = populate_known_deck()
        deck.shuffle = Mock(name="shuffle")

        game = engine.Game(players, 2, deck)

        hand = models.Hand()

        game.pick(hand)

        self.assertEquals(3, deck.number_of_cards())
        self.assertEquals(1, hand.number_of_cards())

        self.assertFalse(deck.shuffle.called)

    def test_pick_card_causes_shuffle(self):
        player = models.Player("bob")
        player_two = models.Player("john")

        players = [player, player_two,]

        deck = models.Deck(None)
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.seven))
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.five))
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.four))
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.three))
        deck.add_card(models.Card(models.Suit.clubs, models.Rank.two))
        deck.shuffle = Mock(name="shuffle")

        game = engine.Game(players, 2, deck)

        game.played_cards.add_card(models.Card(models.Suit.clubs, models.Rank.jack))

        hand = models.Hand()

        game.pick(hand)

        self.assertEquals(0, deck.number_of_cards())
        self.assertEquals(1, hand.number_of_cards())

        self.assertTrue(deck.shuffle.called)

