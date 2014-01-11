# -*- coding: utf-8 -*-
"""
    BobSwitch 
    ~~~~~~~~~~~~~~

    Online HTML5 version of the backpackers card game switch, also known as 
    crazy eights and a lot of different names.  This version follows the rules
    that I know.

    :copyright: (c) Copyright 2013 by Bob
    :license: BSD, see LICENSE for more details.
"""

import tornado.ioloop
import sockjs.tornado

from json_convert import convert_hand, convert_state_start
from engine import create_deck, Game
from models import Player
from sockjs_ext import EventSocketConnection, event

import logging
log = logging.getLogger()

def wrap_chat_message(name, message):
    return {
        "name": name,
        "text": message
    }

def create_game(names):
    players = [Player(name) for name in names]
    deck = create_deck()
    deck.shuffle()
    
    game = Game(players, 7, deck)

    return game


class SocketConnection(EventSocketConnection):
    participants = set()

    def on_open(self, info):
        #user remains annonymous until they register, so they get no name
        self.name = None 
        self.ready = False
        self.position = len(self.participants)

        self.participants.add(self)

    def on_close(self):
        self.participants.remove(self)


    ########
    # chat functions
    ########

    @event("chat:message")
    def chat_message(self, message):
        log.debug("Chat message recieved: %s: %s", self.name, message)

        wrapped_message = wrap_chat_message(self.name, message)
        self.broadcast_event(self.participants, "chat:message", wrapped_message)



    ########
    # account functions
    ########

    @event("account:login")
    def login(self, name):
        log.debug("user '%s' logged in", name)

        self.name = name 
        self.broadcast_event(self.participants, "players:added", name)

    @event("account:listing")
    def listing(self, message):
        log.debug("request for registered users")

        #client only expects registered names to be returned
        names = [{"name":s.name, "ready":s.ready} 
                for s in self.participants if s.name is not None]

        self.send_event("players:listing", names)

    
    #######
    # game functions
    #######

    @event("game:player:ready")
    def player_ready(self, message):
        log.debug("%s ready to start game", self.name)
        
        self.ready = True

        self.broadcast_event(self.participants, "game:player:ready", self.name)

        all_ready = all([s.ready and s.name is not None 
                            for s in self.participants])

        player_count = len(self.participants)
        enough_players = player_count > 1 and player_count < 5
        if not all_ready or not enough_players:
            return

        #start the game
        #send the game initial state to all players
        names = [s.name for s in self.participants if s.name is not None]

        game = create_game(names)

        for participant in self.participants:
            hand = game.player_hand(participant.name)
            participant.send_event("game:state:start", 
                    convert_state_start(game.players, game.current_player,
                        game.played_cards.top_card, hand))


class ClearHandler(tornado.web.RequestHandler):
    def get(self):
        print SocketConnection.participants.clear()


if __name__ == "__main__":
    import logging
    logging.getLogger().setLevel(logging.DEBUG)

    BobSwitchRouter = sockjs.tornado.SockJSRouter(SocketConnection, 
            '/bobswitch')

    app = tornado.web.Application(
            BobSwitchRouter.urls,
            debug=True
    )

    app.listen(8080)

    debug_application = tornado.web.Application([
        (r"/clear", ClearHandler),
    ])                    
    debug_application.listen(9433)

    tornado.ioloop.IOLoop.instance().start()
