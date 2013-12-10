# -*- coding: utf-8 -*-
"""
    BobSwitch 
    ~~~~~~~~~~~~~~

    Online HTML5 version of the backpackers card game switch, also known as crazy eights 
    and a lot of different names.  This version follows the rules that I know.

    :copyright: (c) Copyright 2013 by Bob
    :license: BSD, see LICENSE for more details.
"""

import tornado.ioloop
import sockjs.tornado
import engine

from sockjs_ext import EventSocketConnection, event


class SocketConnection(EventSocketConnection):
    participants = set()

    def on_open(self, info):
        #self.broadcast(self.participants, "Someone joined.")
        self.name = None 

        # Add client to the clients list
        self.participants.add(self)

    def on_close(self):
        # Remove client from the clients list and broadcast leave message
        self.participants.remove(self)

        #self.broadcast(self.participants, "Someone left.")

    @event("chat:message")
    def chat_message(self, message):
        c = {
            "name": self.name,
            "text": message
        }
        self.broadcast_event(self.participants, "chat:message", c)
        print message

    @event("account:login")
    def login(self, message):
        self.name = message
        #self.broadcast_event(self.participants, "chat:message", message + " has joined")
        self.broadcast_event(self.participants, "players:added", message)

    @event("account:listing")
    def listing(self, message):
        print "ACCOUNT LISTING"
        #names = ', '.join(s.name for s in self.participants if s.name is not None)
        names = [s.name for s in self.participants if s.name is not None]
        self.send_event("players:listing", names)
        #self.broadcast_event(self.participants, "chat:message", message + " has joined")

if __name__ == "__main__":
    import logging
    logging.getLogger().setLevel(logging.DEBUG)

    BobSwitchRouter = sockjs.tornado.SockJSRouter(SocketConnection, '/bobswitch')

    app = tornado.web.Application(
            BobSwitchRouter.urls,
            debug=True
    )

    app.listen(8080)

    tornado.ioloop.IOLoop.instance().start()
