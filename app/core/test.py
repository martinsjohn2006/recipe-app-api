""" sample test"""
from django.test import SimpleTestCase

from . import calc

class CalcTests(SimpleTestCase):
    """ Test the calc module"""

    def test_add_numbers(self):
        """Test adding numbers together """
        res = calc.add(5,6)
        
        self.assertEqual(res, 11)

    def test_subtract_numbers(self):
        """Test subtacting numbers together"""
        res = calc.subtract(12, 10)

        self.assertEqual(res, 2)