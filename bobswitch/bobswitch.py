# -*- coding: utf-8 -*-
"""
    BobSwitch 
    ~~~~~~~~~~~~~~

    Online HTML5 version of the backpackers card game switch, also known as crazy eights 
    and a lot of different names.  This version follows the rules that I know.

    :copyright: (c) Copyright 2013 by Bob
    :license: BSD, see LICENSE for more details.
"""

import logging
import tornado.escape
import tornado.ioloop
import tornado.websocket
import os.path
import uuid

import tornadio2

 
#class MainHandler(tornado.web.RequestHandler):
#    def get(self):
#        self.render("index.html", messages=ChatSocketHandler.cache)
 
class UserSessionConnection(tornadio2.SocketConnection):
    open_connections = {}

    def __init__(self, *args, **kwargs):
        super(UserSessionConnection, self).__init__(*args, **kwargs)
        self.key = None

    def on_open(self, request):
        print "BANANA"

    @tornadio2.event
    def banana(self, session_id):
        print "OMG A BANANA EVENT YEAH BABY"

    def on_close(self, ):
        if self.key in self.open_connections:
            del self.open_connections[self.key]

    @staticmethod
    def _make_key(session_id, game_id):
        return (unicode(session_id), unicode(game_id))

    @classmethod
    def lookup(cls, session_id, game_id):
        return cls.open_connections.get(cls._make_key(session_id, game_id))

    @classmethod
    def send_stop_positions(cls, session_id, game_id, stop_positions):
        inst = cls.lookup(session_id, game_id)
        if inst:
            inst.emit('stop_positions', stop_positions)

class SocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    cache = []
    cache_size = 200
 
    def allow_draft76(self):
        # for iOS 5.0 Safari
        return True
 
    def open(self):
        print 'connection opened'
 
    def on_close(self):
        print 'connection closed'
 
 
from flask import Flask
from flask.ext.scss import Scss

app = Flask(__name__)
app.debug = True
Scss(app, static_dir='static', asset_dir='static')
 
@app.route('/')
def index():
    return "ok"
 
from werkzeug import SharedDataMiddleware
import os
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
  '/': os.path.join(os.path.dirname(__file__), 'static')
})
 
import time
import tornado.web
from tornado.websocket import WebSocketHandler
from tornado.ioloop import PeriodicCallback,IOLoop
import tornado.wsgi
 
from tornado import wsgi, httpserver, ioloop, web

import tornadio2

http_server = httpserver.HTTPServer(wsgi.WSGIContainer(app))
http_server.listen(9001)

tornadio_router = tornadio2.TornadioRouter(UserSessionConnection)
application = web.Application(tornadio_router.urls, debug=True)
socket_io_server = httpserver.HTTPServer(application)
socket_io_server.listen(9090)
 
#PeriodicCallback(NowHandler.echo_now,1000).start()
IOLoop.instance().start()
