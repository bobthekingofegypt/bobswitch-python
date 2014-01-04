import json

from unittest2 import TestCase, main, skip

from bobswitch import bobswitch

class TestMeta(TestCase):

    def test_wrap_chat_message(self):
        message = bobswitch.wrap_chat_message("bob", "message")

        self.assertEquals({'text': 'message', 'name': 'bob'}, message)


