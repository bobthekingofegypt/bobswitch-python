from unittest2 import TestCase, main, skip

from engine import models

class TestCard(TestCase):
    
    def test_init(self):
        card = models.Card() 
        self.assertTrue(True)

