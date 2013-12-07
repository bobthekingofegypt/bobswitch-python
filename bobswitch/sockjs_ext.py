# -*- coding: utf-8 -*-
"""
    Socket
    ~~~~~~~~~~~~

    Contains a subclass of the socks tornado Socket class that
    implements the use of event decorators on your SockJSConnection.

    This code is all based on the event mechanism from tornadio2
    https://github.com/MrJoes/tornadio2
    license is contained in the licenses folder
"""

from inspect import ismethod, getmembers

import sockjs.tornado
import json

import logging

logger = logging.getLogger()

def event(name_or_func):
    """Event handler decorator.

    Can be used with event name or will automatically use function name
    if not provided::

        # Will handle 'foo' event
        @event('foo')
        def bar(self):
            pass

        # Will handle 'baz' event
        @event
        def baz(self):
            pass
    """

    if callable(name_or_func):
        name_or_func._event_name = name_or_func.__name__
        return name_or_func

    def handler(f):
        f._event_name = name_or_func
        return f

    return handler


class EventMagicMeta(type):
    """Event handler metaclass"""
    def __init__(cls, name, bases, attrs):
        # find events, also in bases
        is_event = lambda x: ismethod(x) and hasattr(x, '_event_name')
        events = [(e._event_name, e) for _, e in getmembers(cls, is_event)]
        setattr(cls, '_events', dict(events))

        # Call base
        super(EventMagicMeta, cls).__init__(name, bases, attrs)


class EventSocketConnection(sockjs.tornado.SockJSConnection):
    """
    ``EventSocketConnection`` has useful ``event`` decorator. Wrap method with it::

        class MyConnection(EventSocketConnection):
            @event('test')
            def test(self, msg):
                print msg

    and then, when client will emit 'test' event, you should see 'Hello World' printed::

        sock.emit('test', {msg:'Hello World'});

    """
    __metaclass__ = EventMagicMeta

    def on_message(self, message):
        decoded_json = json.loads(message)
        name = decoded_json["name"];
        handler = self._events.get(name)

        if handler:
            message = None
            if "message" in decoded_json:
                message = decoded_json["message"]

            return handler(self, message)
        else:
            logger.error('Invalid event name: %s' % name)

    def broadcast_event(self, participants, name, message):

        data = {
            "type": "event",
            "name": name,
            "message": message
        }

        self.broadcast(self.participants, json.dumps(data))
