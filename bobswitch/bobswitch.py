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

import sys
import argparse

import tornado.ioloop
import sockjs.tornado

from json_convert import convert_hand, convert_state_start, convert_play_response, \
        convert_state_watch
from engine import create_deck, Game, MoveType, GameMove, GameState
from models import Player, Card, Suit, Rank
from sockjs_ext import EventSocketConnection, event

import logging
log = logging.getLogger()

def wrap_chat_message(name, message):
    return {
        "name": name,
        "text": message
    }

def create_game(players):
    deck = create_deck()
    deck.shuffle()
    
    game = Game(players, 7, deck)

    return game

def convert_move_type(move_type):
    if move_type == "pick":
        return MoveType.pick
    elif move_type == "play":
        return MoveType.play
    
    return MoveType.wait

def convert_card(rankId, suitId):
    rank = next(x for x in Rank if int(x) == rankId)
    suit = next(x for x in Suit if int(x) == suitId)

    return Card(suit, rank)

def convert_suit(suitId):
    return next(x for x in Suit if int(x) == suitId)

class Room(object):
    def __init__(self):
        self.active_game = None
        self.active_players = {}
        self.players = {}
    
class RoomPlayer(object):
    def __init__(self, name, socket, player):
        self.name = name
        self.socket = socket
        self.player = player
        self.ready = False


class SocketConnection(EventSocketConnection):
    participants = set()
    room = Room()

    def on_open(self, info):
        #user remains annonymous until they register, so they get no name
        self.name = None 

        self.participants.add(self)

    def on_close(self):
        log.debug("Player disconnected: %s", self.name)

        if self.name in self.room.players:
            self.room.players[self.name].socket = None
            self.broadcast_event(self.room.players, "players:disconnected", self.name)

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

        if name in [s.name for s in self.participants]:
            log.debug("user tried to register already registered name")
            return

        self.name = name 

        if name in self.room.players:
            self.room.players[name].socket = self
            self.broadcast_event(self.room.players, "players:reconnected", self.name)

            game = self.room.active_game
            if game:
                hand = game.player_hand(name)
                self.send_event("game:state:start", 
                    convert_state_start(game.state, game.players, game.player_hands,
                    game.current_player, game.played_cards.top_card, hand))
        else:
            player = Player(name)
            room_player = RoomPlayer(name, self, player)
            self.room.players[name] = room_player
            self.broadcast_event(self.participants, "players:added", name)


    @event("account:listing")
    def listing(self, message):
        log.debug("request for registered users")

        names = [{"name":s.name, "ready":s.ready, "disconnected": s.socket==None} 
                for s in self.room.players.values()]

        self.send_event("players:listing", names)

    
    #######
    # game functions
    #######

    @event("game:player:ready")
    def player_ready(self, message):
        log.debug("%s ready to start game", self.name)
        
        player = self.room.players[self.name]
        player.ready = True

        self.broadcast_event(self.participants, "game:player:ready", self.name)

        all_ready = all([s.ready  
                            for s in self.room.players.values()])

        player_count = len(self.room.players)
        enough_players = player_count > 1 and player_count < 5
        if not all_ready or not enough_players:
            return

        self.room.active_players = self.room.players.copy()
        #start the game
        #send the game initial state to all players
        players = [s.player for s in self.room.players.values()]

        game = create_game(players)

        for participant in self.room.active_players.values():
            socket = participant.socket
            if socket == None:
                #player is currently disconnected, just ignore him he will
                #pick up state on reconnection
                continue
            hand = game.player_hand(socket.name)
            socket.send_event("game:state:start", 
                convert_state_start(game.state, game.players, game.player_hands,
                game.current_player, game.played_cards.top_card, hand))

        for participant in self.participants:
            if participant.name not in self.room.active_players:
                participant.send_event("game:state:watch", 
                    convert_state_watch(game.state, game.players, game.player_hands,
                        game.current_player, game.played_cards.top_card))


        self.room.active_game = game

        for participant in self.room.active_players.values():
            participant.ready = False

    @event("game:player:move")
    def player_move(self, message):
        log.debug("%s plays move", self.name)

        #parse message (wait, pick, play)
        #format
        """
            "type": "play",
            "card": { rank: 4, suit: 4 }
        """
        
        move_type = convert_move_type(message["type"])
        move = None
        if move_type == MoveType.play:
            card = message["card"]
            move = GameMove(MoveType.play,
                    convert_card(card["rank"], card["suit"]))
            if "suit" in message:
                move.suit = convert_suit(message["suit"])
        else:
            move = GameMove(move_type)
        
        game = self.room.active_game

        play_response = game.play(self.name, move)

        self.send_event("game:player:response", 
                convert_play_response(play_response))

        if play_response.success:
            for participant in self.room.active_players.values():
                socket = participant.socket
                if socket == None:
                    continue
                hand = game.player_hand(socket.name)
                socket.send_event("game:state:update", 
                    convert_state_start(game.state, game.players, 
                        game.player_hands,
                        game.current_player, 
                        game.played_cards.top_card, hand))

            for participant in self.participants:
                if participant.name not in self.room.active_players:
                    participant.send_event("game:state:watch", 
                        convert_state_watch(game.state, game.players, game.player_hands,
                            game.current_player, game.played_cards.top_card))

        if game.state == GameState.FINISHED:
            self.room.active_game = None
            self.room.active_players = None
            for participant in self.room.players.values():
                participant.ready = False





        


class ClearHandler(tornado.web.RequestHandler):
    def get(self):
        SocketConnection.participants.clear()
        SocketConnection.room = Room()



def parse_args(argv=sys.argv[1:]):
    description = """
    Python server for playing bobswitch
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-d", "--debug", help="enable debug mode",
                    action="store_true")

    return parser.parse_args(argv)



if __name__ == "__main__":
    import logging
    logging.getLogger().setLevel(logging.DEBUG)

    arguments = parse_args()

    BobSwitchRouter = sockjs.tornado.SockJSRouter(SocketConnection, 
            '/bobswitch')

    app = tornado.web.Application(
            BobSwitchRouter.urls,
            debug=arguments.debug
    )

    app.listen(4500)

    if arguments.debug:
        debug_application = tornado.web.Application([
            (r"/clear", ClearHandler),
        ])                    
        debug_application.listen(9433)

    tornado.ioloop.IOLoop.instance().start()
