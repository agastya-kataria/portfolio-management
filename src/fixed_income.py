import math
from typing import List

import pandas as pd
import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt


def price_bond(face_value: float, coupon_rate: float, maturity: float, yield_rate: float, frequency: int = 1) -> float:
    '''
    Returns the present value of a fixed-coupon bond with given annual or semi-annual coupon frequency.
    face_value: principal repaid at maturity
    coupon_rate: annual coupon rate (as decimal, e.g. 0.05 for 5%)
    maturity: years to maturity (can be fractional)
    yield_rate: annual yield to maturity (as decimal)
    frequency: number of coupon payments per year (1=annual, 2=semi-annual)
    '''
    # Calculate the coupon payment per period
    coupon = face_value * coupon_rate / frequency
    n_periods = int(maturity * frequency)
    pv = 0.0
    for t in range(1, n_periods + 1):
        # Discount each coupon payment to present value
        pv += coupon / (1 + yield_rate / frequency) ** t
    # Discount the face value to present value
    pv += face_value / (1 + yield_rate / frequency) ** n_periods
    return pv


class Bond:
    def __init__(self, face_value: float, coupon_rate: float, maturity: float, frequency: int = 1,
                 callable: bool = False, call_date: float = None, cpi_series: pd.Series = None):
        '''
        face_value: principal repaid at maturity
        coupon_rate: annual coupon rate (as decimal)
        maturity: years to maturity
        frequency: number of coupon payments per year
        callable: True if bond is callable
        call_date: years to call (if callable)
        cpi_series: pd.Series of CPI index (for TIPS)
        '''
        self.face_value = face_value
        self.coupon_rate = coupon_rate
        self.maturity = maturity
        self.frequency = frequency
        self.callable = callable
        self.call_date = call_date
        self.cpi_series = cpi_series

    def price(self, yield_rate: float, real_yield: float = None) -> float:
        '''
        Return the present value of the bond for a given yield.
        For callable: price at worst yield (maturity or call date).
        For TIPS: use real_yield and inflation-adjusted principal/coupons.
        '''
        # TIPS logic
        if self.cpi_series is not None and real_yield is not None:
            # Assume cpi_series index is payment period (int), value is CPI
            n_periods = int(self.maturity * self.frequency)
            base_cpi = self.cpi_series.iloc[0]
            pv = 0.0
            for t in range(1, n_periods + 1):
                # Adjust principal for inflation
                cpi_t = self.cpi_series.iloc[min(t, len(self.cpi_series)-1)]
                inflated_principal = self.face_value * (cpi_t / base_cpi)
                coupon = inflated_principal * self.coupon_rate / self.frequency
                pv += coupon / (1 + real_yield / self.frequency) ** t
            # Final principal payment
            cpi_T = self.cpi_series.iloc[min(n_periods, len(self.cpi_series)-1)]
            inflated_principal = self.face_value * (cpi_T / base_cpi)
            pv += inflated_principal / (1 + real_yield / self.frequency) ** n_periods
            return pv
        # Callable logic
        if self.callable and self.call_date is not None:
            # Price to maturity and to call date, return worst (lowest) price
            price_maturity = price_bond(self.face_value, self.coupon_rate, self.maturity, yield_rate, self.frequency)
            price_call = price_bond(self.face_value, self.coupon_rate, self.call_date, yield_rate, self.frequency)
            return min(price_maturity, price_call)
        # Vanilla bond
        return price_bond(self.face_value, self.coupon_rate, self.maturity, yield_rate, self.frequency)


def bootstrap_yield_curve(bond_list: List[Bond]) -> pd.DataFrame:
    '''
    Given a list of Bond objects with known market prices, returns a DataFrame with columns ['maturity', 'spot_rate', 'interpolated_spot_rate'].
    Assumes annual coupon bonds and that bond.face_value, bond.coupon_rate, bond.maturity, and bond.price(yield) are available.
    '''
    # Sort bonds by maturity
    bond_list = sorted(bond_list, key=lambda b: b.maturity)
    maturities = []
    spot_rates = []
    prices = []
    for bond in bond_list:
        maturities.append(bond.maturity)
        prices.append(bond.price)

    # Bootstrapping: solve for spot rates iteratively
    for i, bond in enumerate(bond_list):
        C = bond.face_value * bond.coupon_rate  # annual coupon
        F = bond.face_value
        P = bond.price
        n = int(bond.maturity)
        if n == 1:
            # Zero-coupon: P = F/(1+z1)^1 => z1 = F/P - 1
            z = (F / P) - 1
            spot_rates.append(z)
        else:
            # Coupon bond: P = sum_{t=1}^{n-1} C/(1+z_t)^t + (C+F)/(1+z_n)^n
            # All z_t for t < n are already solved
            pv_coupons = 0.0
            for t in range(1, n):
                pv_coupons += C / (1 + spot_rates[t-1]) ** t
            # Solve for z_n:
            # P - pv_coupons = (C+F)/(1+z_n)^n
            # (1+z_n)^n = (C+F)/(P - pv_coupons)
            # z_n = ((C+F)/(P - pv_coupons))**(1/n) - 1
            z = ((C + F) / (P - pv_coupons)) ** (1 / n) - 1
            spot_rates.append(z)

    # Interpolate spot rates at 0.5-year intervals using cubic spline
    maturities_arr = np.array(maturities)
    spot_arr = np.array(spot_rates)
    spline = CubicSpline(maturities_arr, spot_arr)
    interp_maturities = np.arange(maturities_arr[0], maturities_arr[-1] + 0.5, 0.5)
    interp_spots = spline(interp_maturities)

    # Build DataFrame
    df = pd.DataFrame({
        'maturity': maturities_arr,
        'spot_rate': spot_arr
    })
    interp_df = pd.DataFrame({
        'maturity': interp_maturities,
        'interpolated_spot_rate': interp_spots
    })
    # Merge for output
    out = pd.merge(df, interp_df, on='maturity', how='outer').sort_values('maturity').reset_index(drop=True)
    return out

def simulate_yield_shift(zero_curve_df: pd.DataFrame, scenario: str, shift_bp: float) -> pd.DataFrame:
    """
    Apply a yield curve shock scenario to the zero curve DataFrame.
    Args:
        zero_curve_df: DataFrame with at least columns ['maturity', 'spot_rate']
        scenario: 'parallel' or 'steepening'
        shift_bp: shift in basis points (float)
    Returns:
        DataFrame with shocked spot rates (same structure as input)
    """
    shocked = zero_curve_df.copy()
    shift = shift_bp / 10000  # convert bp to decimal
    if scenario == "parallel":
        shocked["spot_rate"] = shocked["spot_rate"] + shift
        if "interpolated_spot_rate" in shocked.columns:
            shocked["interpolated_spot_rate"] = shocked["interpolated_spot_rate"] + shift
    elif scenario == "steepening":
        # For maturities <= 2y: subtract half shift; >2y: add half shift
        shocked["spot_rate"] = shocked.apply(
            lambda row: row["spot_rate"] - 0.5 * shift if row["maturity"] <= 2 else row["spot_rate"] + 0.5 * shift,
            axis=1
        )
        if "interpolated_spot_rate" in shocked.columns:
            shocked["interpolated_spot_rate"] = shocked.apply(
                lambda row: row["interpolated_spot_rate"] - 0.5 * shift if row["maturity"] <= 2 else row["interpolated_spot_rate"] + 0.5 * shift,
                axis=1
            )
    else:
        raise ValueError(f"Unknown scenario: {scenario}")
    return shocked


if __name__ == "__main__":
    # Unit tests for price_bond and Bond class
    # Example 1: 5-year, 5% annual coupon, face 100, yield 5%, annual
    bond1 = Bond(100, 0.05, 5, 1)
    price1 = bond1.price(0.05)
    print(f"Bond 1 (annual): Price = {price1:.2f} (should be 100.00)")

    # Example 2: 5-year, 5% annual coupon, face 100, yield 4%, annual
    bond2 = Bond(100, 0.05, 5, 1)
    price2 = bond2.price(0.04)
    print(f"Bond 2 (annual): Price = {price2:.2f} (should be > 100.00)")

    # Example 3: 3-year, 6% semi-annual coupon, face 100, yield 5%, semi-annual
    bond3 = Bond(100, 0.06, 3, 2)
    price3 = bond3.price(0.05)
    print(f"Bond 3 (semi-annual): Price = {price3:.2f} (should be > 100.00)")

    # Callable bond example
    callable_bond = Bond(100, 0.05, 10, 1, callable=True, call_date=5)
    price_callable = callable_bond.price(0.04)
    print(f"Callable Bond (worst of 10y/5y): Price = {price_callable:.2f} (should be min of 10y/5y price)")

    # TIPS example
    # Simulate CPI index for 5 years (annual payments)
    cpi_series = pd.Series([250, 255, 260, 265, 270, 275])  # base + 2%/yr approx
    tips_bond = Bond(100, 0.01, 5, 1, cpi_series=cpi_series)
    price_tips = tips_bond.price(yield_rate=0.005, real_yield=0.005)
    print(f"TIPS Bond: Price = {price_tips:.2f} (inflation-adjusted, real yield 0.5%)")

    # Vanilla for comparison
    vanilla_bond = Bond(100, 0.01, 5, 1)
    price_vanilla = vanilla_bond.price(0.005)
    print(f"Vanilla Bond: Price = {price_vanilla:.2f} (no inflation, yield 0.5%)")

    # Example for bootstrapping: 3 annual bonds with known prices
    # Assume market prices (not par):
    bonds = [
        Bond(100, 0.0, 1, 1),  # zero-coupon 1y
        Bond(100, 0.05, 2, 1), # 2y 5% coupon
        Bond(100, 0.06, 3, 1)  # 3y 6% coupon
    ]
    # Assign market prices (simulate as attributes for demo)
    bonds[0].price = 97.0
    bonds[1].price = 101.5
    bonds[2].price = 104.0
    spot_df = bootstrap_yield_curve(bonds)
    print("\nBootstrapped spot curve:")
    print(spot_df[['maturity', 'spot_rate']])

    # Plotting
    plt.figure(figsize=(8,5))
    plt.plot(spot_df['maturity'], spot_df['spot_rate'], 'o-', label='Bootstrapped Spot Rate')
    plt.plot(spot_df['maturity'], spot_df['interpolated_spot_rate'], 'x--', label='Interpolated (Cubic Spline)')
    plt.xlabel('Maturity (years)')
    plt.ylabel('Spot Rate')
    plt.title('Bootstrapped and Interpolated Spot Curve')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
