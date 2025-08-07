class Portfolio:
    def __init__(self):
        self.assets = {}

    def add_asset(self, asset_name, quantity, price_per_unit):
        if asset_name in self.assets:
            self.assets[asset_name]['quantity'] += quantity
            self.assets[asset_name]['total_investment'] += quantity * price_per_unit
        else:
            self.assets[asset_name] = {
                'quantity': quantity,
                'price_per_unit': price_per_unit,
                'total_investment': quantity * price_per_unit
            }

    def remove_asset(self, asset_name, quantity):
        if asset_name in self.assets:
            if self.assets[asset_name]['quantity'] >= quantity:
                self.assets[asset_name]['quantity'] -= quantity
                if self.assets[asset_name]['quantity'] == 0:
                    del self.assets[asset_name]
            else:
                raise ValueError("Not enough quantity to remove.")
        else:
            raise ValueError("Asset not found in portfolio.")

    def calculate_value(self, current_prices):
        total_value = 0
        for asset_name, asset_info in self.assets.items():
            if asset_name in current_prices:
                total_value += asset_info['quantity'] * current_prices[asset_name]
        return total_value

    def get_assets(self):
        return self.assets