import unittest
from src.portfolio import Portfolio
from src.analysis import calculate_return, calculate_risk

class TestAnalysis(unittest.TestCase):

    def setUp(self):
        self.portfolio = Portfolio()
        self.portfolio.add_asset('AAPL', 10, 150)  # 10 shares of Apple at $150 each
        self.portfolio.add_asset('GOOGL', 5, 1000)  # 5 shares of Google at $1000 each

    def test_calculate_return(self):
        expected_return = (10 * 150 + 5 * 1000) / self.portfolio.calculate_value()
        self.assertAlmostEqual(calculate_return(self.portfolio), expected_return)

    def test_calculate_risk(self):
        # Assuming some mock data for risk calculation
        expected_risk = 0.05  # Placeholder for expected risk value
        self.assertAlmostEqual(calculate_risk(self.portfolio), expected_risk)

if __name__ == '__main__':
    unittest.main()