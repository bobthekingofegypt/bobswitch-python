from inspect import ismethod, getmembers

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

