import json

from unittest2 import TestCase, main, skip

import bobswitch.bobswitch

class TestMeta(TestCase):

    def test_wrap_chat_message(self):
        message = bobswitch.wrap_chat_message("bob", "message")

        self.assertEquals('{"name": "bob", "text": "message"}', message)


