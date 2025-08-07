import unittest
from src.portfolio import Portfolio
from src.analysis import calculate_return, calculate_risk

class TestAnalysis(unittest.TestCase):

    def setUp(self):
        self.portfolio = Portfolio()
        self.portfolio.add_asset('AAPL', 10, 150)  # 10 shares of Apple at $150 each
        self.portfolio.add_asset('GOOGL', 5, 1000)  # 5 shares of Google at $1000 each
        self.current_prices = {'AAPL': 150, 'GOOGL': 1000}

    def test_calculate_return(self):
        # Assuming initial_investment is the sum of initial purchases
        initial_investment = 10 * 150 + 5 * 1000
        expected_return = 0.0  # No gain/loss, so return should be 0.0
        self.assertAlmostEqual(calculate_return(self.portfolio, initial_investment, self.current_prices), expected_return)

    def test_calculate_risk(self):
        import pandas as pd
        # Mock historical prices DataFrame
        data = {'AAPL': [150, 152, 151, 153], 'GOOGL': [1000, 1005, 995, 1010]}
        historical_prices = pd.DataFrame(data)
        # Calculate expected risk using the same logic as in calculate_risk
        expected_risk = historical_prices.pct_change().dropna().std().mean()
        result = calculate_risk(self.portfolio, historical_prices)
        self.assertAlmostEqual(result.mean(), expected_risk)

if __name__ == '__main__':
    unittest.main()