import json

from mock import MagicMock, Mock
from unittest2 import TestCase, main, skip

from bobswitch import engine
from bobswitch import models 
from bobswitch import bobswitch

def create_test_socket(name, room):
    sc = bobswitch.SocketConnection("")
    sc.on_open(None)
    sc.name = name 
    sc.active_room = room 
    sc.active_room.participants.add(sc)
    sc.active_room.players[name] = bobswitch.RoomPlayer(name, sc, 
            models.Player(name))

    return sc

def create_test_game(player_names):
    deck = engine.create_deck()
    deck.shuffle()
    players = [models.Player(name) for name in player_names]
    game = engine.Game(players, 7, deck)

    return game

class TestMeta(TestCase):

    def test_wrap_chat_message(self):
        message = bobswitch.wrap_chat_message("bob", "message")

        self.assertEquals({'text': 'message', 'name': 'bob'}, message)

    def test_create_game(self):
        players = [models.Player("bob"), models.Player("scott")]

        game = bobswitch.create_game(players)

        #number of cards is equal to 52 minus one face up and 7 per player
        self.assertEquals(52 - (2*7) - 1, game.deck.number_of_cards())
        self.assertEquals("bob", game.players[0].name)
        self.assertEquals("scott", game.players[1].name)

    def test_convert_move_type_pick(self):
        move_type = bobswitch.convert_move_type("pick")
        self.assertEquals(engine.MoveType.pick, move_type)
    
    def test_convert_move_type_play(self):
        move_type = bobswitch.convert_move_type("play")
        self.assertEquals(engine.MoveType.play, move_type)

    def test_convert_move_type_wait(self):
        move_type = bobswitch.convert_move_type("wait")
        self.assertEquals(engine.MoveType.wait, move_type)

    def test_convert_card(self):
        card = bobswitch.convert_card(1,1)

        self.assertEquals(card.rank, models.Rank.ace)
        self.assertEquals(card.suit, models.Suit.clubs)
    
    def test_convert_card_2(self):
        card = bobswitch.convert_card(3,2)

        self.assertEquals(card.rank, models.Rank.three)
        self.assertEquals(card.suit, models.Suit.diamonds)

    def test_convert_suit(self):
        self.assertEquals(models.Suit.clubs, bobswitch.convert_suit(1))
        

class TestSocketConnection(TestCase):

    def setUp(self):
        bobswitch.SocketConnection.participants = set()
        bobswitch.SocketConnection.room = bobswitch.Room()

    def test_on_open(self):
        sc = bobswitch.SocketConnection("")
        sc.on_open(None)

        self.assertEquals(None, sc.name)
        self.assertTrue(sc in sc.participants)

    def test_on_close(self):
        sc = bobswitch.SocketConnection("")
        sc.on_open(None)

        self.assertTrue(sc in sc.participants)
    
        sc.on_close()

        self.assertFalse(sc in sc.participants)

    def test_chat_message(self):
        sc = create_test_socket("bob", bobswitch.Room())

        sc.broadcast_event = MagicMock()

        sc.chat_message("room", "Hello")

        sc.broadcast_event.assert_called_with(sc.participants, "chat:message", 
                {"name": "bob", "text": "Hello"})
        
    def test_login(self):
        sc = bobswitch.SocketConnection("")
        sc.on_open(None)
        sc.active_room = bobswitch.Room()
        sc.active_room.participants.add(sc)

        sc.broadcast_event = MagicMock()
        sc.login("room", "bob")

        sc.broadcast_event.assert_called_with(sc.participants, "players:added", 
                "bob")



    def test_listing(self):
        room = bobswitch.Room()
        sc = create_test_socket("bob", room)
        sc2 = create_test_socket("Scott", room)

        sc.rooms["room"] = room

        sc.send_event = MagicMock()
        sc.listing("room", None)

        args, kargs = sc.send_event.call_args
        key, listing = args
        self.assertEquals("players:listing", key)

        names = [s["name"] for s in listing if s["name"] is not None]

        self.assertTrue("Scott" in names)
        self.assertTrue("bob" in names)

    def test_two_players_ready_one_not_ready(self):
        room = bobswitch.Room()
        sc = create_test_socket("bob", room)
        sc2 = create_test_socket("Scott", room)

        sc3 = bobswitch.SocketConnection("")
        sc3.on_open(None)
        sc3.active_room = sc.active_room
        sc3.active_room.participants.add(sc3)
        sc3.send_event = MagicMock()
    
        sc.broadcast_event = MagicMock()
        sc.send_event = MagicMock()
        sc.player_ready("room", None)
        sc.broadcast_event.assert_called_with(sc.active_room.participants, 
                "game:player:ready", "bob")

        sc2.broadcast_event = MagicMock()
        sc2.send_event = MagicMock()
        sc2.player_ready("room", None)
        sc2.broadcast_event.assert_called_with(sc2.active_room.participants, 
                "game:player:ready", "Scott")

        self.assertTrue(sc3.send_event.called)

        self.assertTrue(sc.send_event.called)

    def test_player_ready_not_all_ready(self):
        room = bobswitch.Room()
        sc = create_test_socket("bob", room)
        sc2 = create_test_socket("Scott", room)
    
        sc.broadcast_event = MagicMock()
        sc.send_event = MagicMock()
        sc.player_ready("room", None)
        sc.broadcast_event.assert_called_with(sc.participants, 
                "game:player:ready", "bob")

        self.assertFalse(sc.send_event.called)

    def test_player_ready_all_ready(self):
        room = bobswitch.Room()
        sc = create_test_socket("bob", room)
        sc2 = create_test_socket("Scott", room)
        sc.active_room.players["bob"].ready = True

        sc2.active_room.players["Scott"].ready = True
    
        sc.broadcast_event = MagicMock()
        sc.send_event = MagicMock()
        sc2.send_event = MagicMock()

        sc.player_ready("room", None)

        sc.broadcast_event.assert_called_with(sc.participants, 
                "game:player:ready", "bob")

        args, kargs = sc.send_event.call_args
        key, state = args
        self.assertEquals("game:state:start", key)
        self.assertEquals(2, state["number_of_players"])
        self.assertEquals(7, len(state["hand"]))

        args, kargs = sc2.send_event.call_args
        key, state = args
        self.assertEquals("game:state:start", key)
        self.assertEquals(2, state["number_of_players"])
        self.assertEquals(7, len(state["hand"]))

    def test_player_ready_only_one(self):
        sc = create_test_socket("bob", bobswitch.Room())

        sc.broadcast_event = MagicMock()
        sc.send_event = MagicMock()
        sc.player_ready("room", None)
        sc.broadcast_event.assert_called_with(sc.participants, 
                "game:player:ready", "bob")
        
        self.assertFalse(sc.send_event.called)

    def test_player_move_wait(self):
        sc = create_test_socket("bob", bobswitch.Room())
        sc.active_room.active_players = sc.active_room.players.copy()

        sc.send_event = MagicMock()

        game = create_test_game(["bob"])
        game.play = MagicMock(return_value=engine.PlayResponse(True))
        sc.active_room.active_game = game

        sc.player_move("room", {
            "type": "wait",
        })
        
        args, kargs = sc.active_room.active_game.play.call_args
        name, move = args
        self.assertEquals("bob", name)
        self.assertEquals(engine.MoveType.wait, move.move_type)

        name, call_args, c = sc.send_event.mock_calls[0]
        key, message = call_args 
        self.assertEquals("game:player:response", key) 
        self.assertEquals(True, message["success"]) 

        name, call_args, c = sc.send_event.mock_calls[1]
        key, message = call_args 
        self.assertEquals("game:state:update", key) 

    def test_player_move_pick(self):
        sc = create_test_socket("bob", bobswitch.Room())
        sc.active_room.active_players = sc.active_room.players.copy()

        sc.send_event = MagicMock()

        game = create_test_game(["bob"])
        game.play = MagicMock(return_value=engine.PlayResponse(True))
        sc.active_room.active_game = game

        sc.player_move("room", {
            "type": "pick",
        })
        
        args, kargs = sc.active_room.active_game.play.call_args
        name, move = args
        self.assertEquals("bob", name)
        self.assertEquals(engine.MoveType.pick, move.move_type)

        name, call_args, c = sc.send_event.mock_calls[0]
        key, message = call_args 
        self.assertEquals("game:player:response", key) 
        self.assertEquals(True, message["success"]) 

        name, call_args, c = sc.send_event.mock_calls[1]
        key, message = call_args 
        self.assertEquals("game:state:update", key) 

    def test_player_move_play(self):
        sc = create_test_socket("bob", bobswitch.Room())
        sc.active_room.active_players = sc.active_room.players.copy()

        sc.send_event = MagicMock()

        game = create_test_game(["bob"])
        game.play = MagicMock(return_value=engine.PlayResponse(True))
        sc.active_room.active_game = game

        sc.player_move("room", {
            "type": "play",
            "card": { 
                "rank": 4,
                "suit": 2
            }
        })

        args, kargs = sc.active_room.active_game.play.call_args
        name, move = args
        self.assertEquals("bob", name)
        self.assertEquals(engine.MoveType.play, move.move_type)
        self.assertEquals(models.Rank.four, move.card.rank)

        name, call_args, c = sc.send_event.mock_calls[0]
        key, message = call_args 
        self.assertEquals("game:player:response", key) 
        self.assertEquals(True, message["success"]) 

        name, call_args, c = sc.send_event.mock_calls[1]
        key, message = call_args 
        self.assertEquals("game:state:update", key) 

    def test_player_move_fail(self):
        sc = create_test_socket("bob", bobswitch.Room())
        sc.active_room.active_players = sc.active_room.players.copy()

        sc.send_event = MagicMock()

        game = create_test_game(["bob"])
        game.play = MagicMock(return_value=engine.PlayResponse(False))
        sc.active_room.active_game = game

        sc.player_move("room", {
            "type": "wait",
            "card": { 
                "rank": 4,
                "suit": 2
            }
        })

        args, kargs = sc.send_event.call_args
        key, state = args
        self.assertEquals("game:player:response", key) 
        self.assertEquals(False, state["success"]) 
