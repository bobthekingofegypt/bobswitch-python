import json

from mock import MagicMock, Mock
from unittest2 import TestCase, main, skip

from bobswitch import engine
from bobswitch import models 
from bobswitch import bobswitch

class TestMeta(TestCase):

    def test_wrap_chat_message(self):
        message = bobswitch.wrap_chat_message("bob", "message")

        self.assertEquals({'text': 'message', 'name': 'bob'}, message)

    def test_create_game(self):
        names = ["bob", "scott"]

        game = bobswitch.create_game(names)

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
        

class TestSocketConnection(TestCase):

    def setUp(self):
        bobswitch.SocketConnection.participants = set()

    def test_on_open(self):
        sc = bobswitch.SocketConnection("")
        sc.on_open(None)

        self.assertEquals(None, sc.name)
        self.assertEquals(False, sc.ready)
        self.assertTrue(sc in sc.participants)

    def test_on_close(self):
        sc = bobswitch.SocketConnection("")
        sc.on_open(None)

        self.assertTrue(sc in sc.participants)
    
        sc.on_close()

        self.assertFalse(sc in sc.participants)

    def test_chat_message(self):
        sc = bobswitch.SocketConnection("")
        sc.name = "bob"

        sc.broadcast_event = MagicMock()

        sc.chat_message("Hello")

        sc.broadcast_event.assert_called_with(sc.participants, "chat:message", 
                {"name": "bob", "text": "Hello"})
        
    def test_login(self):
        sc = bobswitch.SocketConnection("")
        sc.on_open(None)

        sc.broadcast_event = MagicMock()
        sc.login("bob")

        sc.broadcast_event.assert_called_with(sc.participants, "players:added", 
                "bob")

    def test_listing(self):
        sc = bobswitch.SocketConnection("")
        sc.on_open(None)
        sc.name = "bob"

        sc2 = bobswitch.SocketConnection("")
        sc2.on_open(None)
        sc2.name = "Scott"

        sc.send_event = MagicMock()
        sc.listing(None)

        args, kargs = sc.send_event.call_args
        key, listing = args
        self.assertEquals("players:listing", key)

        names = [s["name"] for s in listing if s["name"] is not None]

        self.assertTrue("Scott" in names)
        self.assertTrue("bob" in names)

    def test_player_ready_not_all_ready(self):
        sc = bobswitch.SocketConnection("")
        sc.on_open(None)
        sc.name = "bob"

        sc2 = bobswitch.SocketConnection("")
        sc2.on_open(None)
        sc2.name = "Scott"
    
        sc.broadcast_event = MagicMock()
        sc.send_event = MagicMock()
        sc.player_ready(None)
        sc.broadcast_event.assert_called_with(sc.participants, 
                "game:player:ready", "bob")

        self.assertFalse(sc.send_event.called)

    def test_player_ready_all_ready(self):
        sc = bobswitch.SocketConnection("")
        sc.on_open(None)
        sc.name = "bob"

        sc2 = bobswitch.SocketConnection("")
        sc2.on_open(None)
        sc2.name = "Scott"
        sc2.ready = True
    
        sc.broadcast_event = MagicMock()
        sc.send_event = MagicMock()
        sc2.send_event = MagicMock()

        sc.player_ready(None)

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
        sc = bobswitch.SocketConnection("")
        sc.on_open(None)
        sc.name = "bob"

        sc.broadcast_event = MagicMock()
        sc.send_event = MagicMock()
        sc.player_ready(None)
        sc.broadcast_event.assert_called_with(sc.participants, 
                "game:player:ready", "bob")
        
        self.assertFalse(sc.send_event.called)

    def test_player_move_wait(self):
        sc = bobswitch.SocketConnection("")
        sc.name = "bob"

        sc.game["active"] = Mock()
        sc.game["active"].play = MagicMock(return_value=engine.PlayResponse(True))
        sc.send_event = MagicMock()

        sc.player_move({
            "type": "wait",
        })
        
        args, kargs = sc.game["active"].play.call_args
        name, move = args
        self.assertEquals("bob", name)
        self.assertEquals(engine.MoveType.wait, move.move_type)

        args, kargs = sc.send_event.call_args
        key, state = args
        self.assertEquals("game:player:response", key) 
        self.assertEquals(True, state["success"]) 

    def test_player_move_pick(self):
        sc = bobswitch.SocketConnection("")
        sc.name = "bob"

        sc.game["active"] = Mock()
        sc.game["active"].play = MagicMock(return_value=engine.PlayResponse(True))
        sc.send_event = MagicMock()

        sc.player_move({
            "type": "pick",
        })
        
        args, kargs = sc.game["active"].play.call_args
        name, move = args
        self.assertEquals("bob", name)
        self.assertEquals(engine.MoveType.pick, move.move_type)

        args, kargs = sc.send_event.call_args
        key, state = args
        self.assertEquals("game:player:response", key) 
        self.assertEquals(True, state["success"]) 

    def test_player_move_play(self):
        sc = bobswitch.SocketConnection("")
        sc.name = "bob"

        sc.game["active"] = Mock()
        sc.game["active"].play = MagicMock(return_value=engine.PlayResponse(True))
        sc.send_event = MagicMock()

        sc.player_move({
            "type": "play",
            "card": { 
                "rank": 4,
                "suit": 2
            }
        })
        
        args, kargs = sc.game["active"].play.call_args
        name, move = args
        self.assertEquals("bob", name)
        self.assertEquals(engine.MoveType.play, move.move_type)
        self.assertEquals(models.Rank.four, move.card.rank)

        args, kargs = sc.send_event.call_args
        key, state = args
        self.assertEquals("game:player:response", key) 
        self.assertEquals(True, state["success"]) 

    def test_player_move_fail(self):
        sc = bobswitch.SocketConnection("")
        sc.name = "bob"

        sc.game["active"] = Mock()
        sc.game["active"].play = MagicMock(return_value=engine.PlayResponse(False))
        sc.send_event = MagicMock()

        sc.player_move({
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
