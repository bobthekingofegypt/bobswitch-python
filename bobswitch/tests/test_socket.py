from unittest2 import TestCase, main, skip

from bobswitch.socket import event, EventMagicMeta

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
        
            
