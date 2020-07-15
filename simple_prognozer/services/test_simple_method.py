import unittest
import datetime

from simple_method import simple_method


class TestSimpeMethod(unittest.TestCase):
    def setUp(self):
        self.with_admin2 = {
                            'country': 'us',
                            'subdivision': 'new-york',
                            'admin2': 'new-york-city'
                            }

        self.without_admin2 = {
                               'country': 'russia',
                               'subdivision': 'moscow',
                               'admin2': None
                               }
        self.only_country = {
                               'country': 'afghanistan',
                               'subdivision': None,
                               'admin2': None
                               }
        self.neverland = {
                          'country': 'neverland',
                          'subdivision': None,
                          'admin2': None
                          }

    def test_with_admin2(self):
        self.assertIsInstance(simple_method(self.with_admin2),
                              datetime.datetime)

    def test_without_admin2(self):
        self.assertIsInstance(simple_method(self.without_admin2),
                              datetime.datetime)

    def test_only_country(self):
        self.assertIsInstance(simple_method(self.without_admin2),
                              datetime.datetime)

    def test_neverland(self):
        self.assertEqual(simple_method(self.neverland), 'Country not found')


if __name__ == "__main__":
    unittest.main()
