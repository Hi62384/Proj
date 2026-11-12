from unittest import TestCase
from calculate import product
from status import status

class Tests(TestCase):
    def test_calculation(self):
        self.assertEqual(product(3, 4), 12)
    def test_status(self):
        self.assertEqual(status(), "ready")
