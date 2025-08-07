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