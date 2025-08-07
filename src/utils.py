def load_data(file_path):
    # Function to load data from a CSV file
    import pandas as pd
    return pd.read_csv(file_path)

def format_currency(value):
    # Function to format a number as currency
    return "${:,.2f}".format(value)

def calculate_percentage(part, whole):
    # Function to calculate the percentage of a part relative to the whole
    if whole == 0:
        return 0
    return (part / whole) * 100

def validate_asset(asset):
    # Function to validate asset data
    required_keys = ['name', 'amount', 'price']
    return all(key in asset for key in required_keys)