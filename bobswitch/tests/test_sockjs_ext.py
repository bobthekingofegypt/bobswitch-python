import json

from unittest2 import TestCase, main, skip

from bobswitch.sockjs_ext import event, EventMagicMeta, EventSocketConnection

class TestMeta(TestCase):

    def test_event_detection(self):

        class TestReg(object):

            __metaclass__ = EventMagicMeta

            @event
            def test1(self, message):
                pass

        testReg = TestReg()

        self.assertEquals(1, len(testReg._events))

    def test_multiple_event_detection(self):

        class TestReg(object):

            __metaclass__ = EventMagicMeta

            @event
            def test1(self, message):
                pass

            @event
            def test2(self, message):
                pass

        testReg = TestReg()

        self.assertEquals(2, len(testReg._events))
        
    def test_normal_methods_ignored(self):

        class TestReg(object):

            __metaclass__ = EventMagicMeta

            @event
            def test1(self, message):
                pass

            def test2(self, message):
                pass

        testReg = TestReg()

        self.assertEquals(1, len(testReg._events))
            
    def test_name_passing(self):

        class TestReg(object):

            __metaclass__ = EventMagicMeta

            @event("test2")
            def test1(self, message):
                pass

            def test2(self, message):
                pass

        testReg = TestReg()

        self.assertEquals(1, len(testReg._events))
        self.assertEquals(testReg.test1._event_name, "test2")
        
    def test_on_message(self):
        called = {"called": False,} 
        def update_called():
            called["called"] = True

        class TestMessage(EventSocketConnection):

            def __init__(self, session, update_called):
                self.update_called = update_called
                super(TestMessage, self).__init__(session)

            @event
            def test1(self, room, message):
                self.update_called()

        testMessage = TestMessage(None, update_called)

        testMessage.on_message('{"name":"test1", "message":"a message"}')

        self.assertTrue(called["called"])
            
    def test_on_message_invalid_event_no_crash(self):
        
        class TestMessage(EventSocketConnection):

            @event
            def test1(self, message):
                pass

        testMessage = TestMessage(None)

        testMessage.on_message('{"name":"test2", "message":"a message"}')

    def test_None_message_when_no_message(self):
        called = {"called": False,} 
        def update_called(message):
            called["called"] = True
            called["message"] = message

        
        class TestMessage(EventSocketConnection):

            def __init__(self, session, update_called):
                self.update_called = update_called
                super(TestMessage, self).__init__(session)

            @event
            def test1(self, room, message):
                self.update_called(message)

        testMessage = TestMessage(None, update_called)

        testMessage.on_message('{"name":"test1"}')
        
        self.assertTrue(called["called"])
        self.assertEquals(None, called["message"])

    def test_send_event(self):
        called = {"message": None,} 

        class TestMessage(EventSocketConnection):
            def send(self, message):
                called["message"] = message
                
        test_message = TestMessage(None)

        test_message.send_event("bob", "hello")

        self.assertEquals('{"message": "hello", "type": "event", "name": "bob"}', called["message"])



