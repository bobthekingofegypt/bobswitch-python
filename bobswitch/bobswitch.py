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

import logging
log = logging.getLogger()

def wrap_chat_message(name, message):
    return {
        "name": name,
        "text": message
    }


class SocketConnection(EventSocketConnection):
    participants = set()

    def on_open(self, info):
        #user remains annonymous until they register, so they get no name
        self.name = None 

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
        names = [s.name for s in self.participants if s.name is not None]
        self.send_event("players:listing", names)


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
