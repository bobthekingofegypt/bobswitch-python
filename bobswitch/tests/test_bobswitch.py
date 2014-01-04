import json

from mock import MagicMock
from unittest2 import TestCase, main, skip

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
        

class TestSocketConnection(TestCase):

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

    

