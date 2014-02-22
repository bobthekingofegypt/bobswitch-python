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
        self.participants = set()
    
class RoomPlayer(object):
    def __init__(self, name, socket, player):
        self.name = name
        self.socket = socket
        self.player = player
        self.ready = False


class SocketConnection(EventSocketConnection):
    participants = set()
    room = Room()

    rooms = {}

    def on_open(self, info):
        #user remains annonymous until they register, so they get no name
        self.name = None 

        self.participants.add(self)

    def on_close(self):
        log.debug("Player disconnected: %s", self.name)

        if hasattr(self, "active_room"):
            if self.name in self.active_room.players:
                self.broadcast_event(self.active_room.participants, "players:disconnected", self.name)
                self.active_room.players[self.name].socket = None

            self.active_room.participants.remove(self)

        self.participants.remove(self)


    ########
    # chat functions
    ########

    @event("chat:message")
    def chat_message(self, room_name, message):
        log.debug("Chat message recieved for room '%s': %s: %s", room_name, self.name, message)

        room = self.active_room

        wrapped_message = wrap_chat_message(self.name, message)
        self.broadcast_event(room.participants, "chat:message", wrapped_message)

    def check_room(self, room):
        if room not in self.rooms:
            log.debug("creating room - '%s'", room)
            self.rooms[room] = Room()

    ########
    # account functions
    ########

    @event("account:login")
    def login(self, room_name, name):
        log.debug("user '%s' logged in to room '%s'", name, room_name)

        room = self.active_room

        self.name = name 

        if name in room.players:
            room.players[name].socket = self
            self.broadcast_event(room.participants, "players:reconnected", self.name)

            game = room.active_game
            if game:
                hand = game.player_hand(name)
                self.send_event("game:state:start", 
                    convert_state_start(game.state, game.players, game.player_hands,
                    game.current_player, game.played_cards.top_card, hand))
        else:
            player = Player(name)
            room_player = RoomPlayer(name, self, player)
            room.players[name] = room_player
            self.broadcast_event(self.active_room.participants, "players:added", name)


    @event("account:listing")
    def listing(self, room_name, message):
        log.debug("request for registered users")

        self.check_room(room_name)
        room = self.rooms[room_name]
        room.participants.add(self)
        self.active_room = room
        

        names = [{"name":s.name, "ready":s.ready, "disconnected": s.socket==None} 
                for s in room.players.values()]

        self.send_event("players:listing", names)

    
    #######
    # game functions
    #######

    @event("game:player:ready")
    def player_ready(self, room_name, message):
        log.debug("%s ready to start game", self.name)

        room = self.active_room
        
        player = room.players[self.name]
        player.ready = True

        self.broadcast_event(room.participants, "game:player:ready", self.name)

        all_ready = all([s.ready  
                            for s in room.players.values()])

        player_count = len(room.players)
        enough_players = player_count > 1 and player_count < 5
        if not all_ready or not enough_players:
            return

        room.active_players = room.players.copy()
        #start the game
        #send the game initial state to all players
        players = [s.player for s in room.players.values()]

        game = create_game(players)

        for participant in room.active_players.values():
            socket = participant.socket
            if socket == None:
                #player is currently disconnected, just ignore him he will
                #pick up state on reconnection
                continue
            hand = game.player_hand(socket.name)
            socket.send_event("game:state:start", 
                convert_state_start(game.state, game.players, game.player_hands,
                game.current_player, game.played_cards.top_card, hand))

        for participant in room.participants:
            if participant.name not in room.active_players:
                participant.send_event("game:state:watch", 
                    convert_state_watch(game.state, game.players, game.player_hands,
                        game.current_player, game.played_cards.top_card))


        room.active_game = game

        for participant in room.active_players.values():
            participant.ready = False

    @event("game:player:move")
    def player_move(self, room_name, message):
        log.debug("%s plays move", self.name)

        #parse message (wait, pick, play)
        #format
        """
            "type": "play",
            "card": { rank: 4, suit: 4 }
        """

        room = self.active_room
        
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
        
        game = room.active_game

        play_response = game.play(self.name, move)

        self.send_event("game:player:response", 
                convert_play_response(play_response))

        if play_response.success:
            for participant in room.active_players.values():
                socket = participant.socket
                if socket == None:
                    continue
                hand = game.player_hand(socket.name)
                socket.send_event("game:state:update", 
                    convert_state_start(game.state, game.players, 
                        game.player_hands,
                        game.current_player, 
                        game.played_cards.top_card, hand))

            for participant in room.participants:
                if participant.name not in room.active_players:
                    participant.send_event("game:state:watch", 
                        convert_state_watch(game.state, game.players, game.player_hands,
                            game.current_player, game.played_cards.top_card))

        if game.state == GameState.FINISHED:
            room.active_game = None
            room.active_players = None
            for participant in room.players.values():
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
