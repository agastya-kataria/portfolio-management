def calculate_return(portfolio, initial_investment):
    total_value = portfolio.calculate_value()
    return (total_value - initial_investment) / initial_investment


def calculate_risk(portfolio, historical_prices):
    returns = historical_prices.pct_change().dropna()
    return returns.std()


def generate_report(portfolio):
    report = {
        'total_value': portfolio.calculate_value(),
        'assets': portfolio.assets,
        'risk': calculate_risk(portfolio, portfolio.historical_prices),
        'return': calculate_return(portfolio, portfolio.initial_investment)
    }
    return report

import numpy as np
import pandas as pd

def simulate_portfolio_paths(portfolio, zero_curve_df, n_scenarios: int, vol: float, dt: float) -> np.ndarray:
    """
    Simulate portfolio values under yield curve scenarios (GBM for each spot rate).
    Args:
        portfolio: Portfolio object with .assets (dict of asset_name: {quantity, ...})
        zero_curve_df: DataFrame with ['maturity', 'spot_rate']
        n_scenarios: number of Monte Carlo scenarios
        vol: annualized volatility (applied to each spot rate, decimal)
        dt: time step (years)
    Returns:
        np.ndarray of simulated portfolio values (shape: [n_scenarios])
    """
    maturities = zero_curve_df['maturity'].values
    spot_rates = zero_curve_df['spot_rate'].values
    n_bonds = len(portfolio.assets)
    portfolio_values = np.zeros(n_scenarios)
    for i in range(n_scenarios):
        # Simulate shocked spot rates for each maturity
        shocks = np.random.normal(loc=0, scale=vol * np.sqrt(dt), size=len(spot_rates))
        shocked_spots = spot_rates * np.exp(shocks)
        shocked_curve = pd.DataFrame({'maturity': maturities, 'spot_rate': shocked_spots})
        # For each bond, reprice using shocked curve (assume asset_name is Bond object)
        total_value = 0.0
        for asset_name, asset_info in portfolio.assets.items():
            bond = asset_name if hasattr(asset_name, 'price') else None
            if bond is not None:
                # Interpolate yield for bond maturity
                y = np.interp(bond.maturity, shocked_curve['maturity'], shocked_curve['spot_rate'])
                price = bond.price(y)
                total_value += asset_info['quantity'] * price
        portfolio_values[i] = total_value
    return portfolio_values

def calculate_var(portfolio_values: np.ndarray, alpha: float) -> float:
    """
    Calculate Value-at-Risk (VaR) at confidence level alpha (e.g. 0.95 or 0.99).
    Returns the VaR as a positive number (loss).
    """
    pnl = portfolio_values - np.mean(portfolio_values)
    var = -np.percentile(pnl, 100 * (1 - alpha))
    return var