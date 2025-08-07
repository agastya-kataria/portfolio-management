import unittest
from src.portfolio import Portfolio

class TestPortfolio(unittest.TestCase):

    def setUp(self):
        self.portfolio = Portfolio()

    def test_add_asset(self):
        self.portfolio.add_asset('AAPL', 10, 150)
        self.assertIn('AAPL', self.portfolio.assets)
        self.assertEqual(self.portfolio.assets['AAPL']['quantity'], 10)
        self.assertEqual(self.portfolio.assets['AAPL']['price_per_unit'], 150)

    def test_remove_asset(self):
        self.portfolio.add_asset('AAPL', 10, 150)
        self.portfolio.remove_asset('AAPL', 5)
        self.assertEqual(self.portfolio.assets['AAPL']['quantity'], 5)

        self.portfolio.remove_asset('AAPL', 5)
        self.assertNotIn('AAPL', self.portfolio.assets)

    def test_calculate_value(self):
        self.portfolio.add_asset('AAPL', 10, 150)
        self.portfolio.add_asset('GOOGL', 5, 1000)
        current_prices = {'AAPL': 150, 'GOOGL': 1000}
        total_value = self.portfolio.calculate_value(current_prices)
        self.assertEqual(total_value, 1500 + 5000)

if __name__ == '__main__':
    unittest.main()