from unittest import TestCase
from calculate import total
from status import status

class Tests(TestCase):
    def test_calculation(self):
        self.assertEqual(total(3, 4), 7)
    def test_status(self):
        self.assertEqual(status(), "ready")
