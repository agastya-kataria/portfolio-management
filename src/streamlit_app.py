import streamlit as st
import pandas as pd
import numpy as np
from fixed_income import Bond, bootstrap_yield_curve, simulate_yield_shift
from portfolio import Portfolio
from analysis import simulate_portfolio_paths, calculate_var
import plotly.express as px
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Fixed Income Portfolio Dashboard", layout="wide")

# --- User Preferences ---
if 'default_trade_size' not in st.session_state:
    st.session_state['default_trade_size'] = 1
if 'theme_pref' not in st.session_state:
    st.session_state['theme_pref'] = 'Light'

with st.sidebar.expander("Getting Started", expanded=True):
    st.markdown("""
    **Welcome to the Portfolio Management Dashboard!**
    - **1. Upload** your bond portfolio CSV in the Data Input tab.
    - **2. Explore** your portfolio, risk, and scenarios in the tabs.
    - **3. Use the sidebar** for trading, feedback, and preferences.
    - **4. Check diversification and reinvest excess cash in the Reinvestable Money tab.**
    - **5. Export/Import** your portfolio state for backup or transfer.
    """)

with st.sidebar.expander("User Preferences", expanded=False):
    st.markdown('<style>label, .stRadio > label, .stButton > button, .stTextInput > div > input {font-size: 1.1em !important;}</style>', unsafe_allow_html=True)
    st.session_state['default_trade_size'] = st.number_input("Default Trade Size", min_value=1, value=st.session_state['default_trade_size'])
    st.session_state['theme_pref'] = st.radio("Theme Preference", ["Light", "Dark"], index=0 if st.session_state['theme_pref']=="Light" else 1)

# --- Theme toggle ---
theme = st.session_state['theme_pref']
if theme == "Dark":
    st.markdown("""
        <style>
        body, .stApp { background-color: #222; color: #eee; }
        .stDataFrame, .stMetric, .stTextArea { background-color: #222 !important; color: #eee !important; }
        </style>
    """, unsafe_allow_html=True)

st.title("Fixed Income Portfolio Analytics")

# --- Real-time log ---
log = []
def log_step(msg):
    log.append(msg)
    st.session_state['log'] = '\n'.join(log)

if 'log' not in st.session_state:
    st.session_state['log'] = ''

# --- Activity Feed State ---
if 'activity_feed' not in st.session_state:
    st.session_state['activity_feed'] = []

def log_activity(msg):
    st.session_state['activity_feed'].append(f"{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')} - {msg}")

# --- Trade Simulation Sidebar ---
st.sidebar.header("Trade Simulation")
if 'portfolio' not in st.session_state:
    st.session_state['portfolio'] = None
if 'bonds' not in st.session_state:
    st.session_state['bonds'] = None
if 'trade_history' not in st.session_state:
    st.session_state['trade_history'] = []
trade_action = st.sidebar.selectbox("Action", ["Buy", "Sell"])
trade_bond = st.sidebar.text_input("Bond Index (row #)", value="0")
trade_qty = st.sidebar.number_input("Quantity", min_value=1, value=st.session_state['default_trade_size'])
import json as _json

def autosave_session():
    export_state = {
        'positions': [
            {
                'bond': f"Bond #{i}",
                'maturity': getattr(b, 'maturity', '?'),
                'coupon_rate': getattr(b, 'coupon_rate', '?'),
                'quantity': st.session_state['portfolio'].assets.get(b, {}).get('quantity', 0),
                'avg_cost': st.session_state['portfolio'].assets.get(b, {}).get('price_per_unit', '?'),
                'sector': None
            }
            for i, b in enumerate(st.session_state.get('bonds', []))
        ],
        'reinvestable_money': st.session_state.get('reinvestable_money', 0.0),
        'auto_sale_log': st.session_state.get('auto_sale_log', []),
        'reinvestment_log': st.session_state.get('reinvestment_log', []),
        'activity_feed': st.session_state.get('activity_feed', []),
        'trade_history': st.session_state.get('trade_history', [])
    }
    with open("autosave_session.json", "w", encoding="utf-8") as f:
        _json.dump(export_state, f, default=str)

if st.sidebar.button("Execute Trade"):
    try:
        idx = int(trade_bond)
        if st.session_state['bonds'] is not None and 0 <= idx < len(st.session_state['bonds']):
            bond = st.session_state['bonds'][idx]
            if st.session_state['portfolio'] is not None:
                if trade_action == "Buy":
                    st.session_state['portfolio'].add_asset(bond, trade_qty, bond.price)
                else:
                    st.session_state['portfolio'].remove_asset(bond, trade_qty)
                st.session_state['trade_history'].append({
                    'Time': pd.Timestamp.now(),
                    'Action': trade_action,
                    'Bond': f"Bond #{idx}",
                    'Maturity': getattr(bond, 'maturity', '?'),
                    'Coupon': getattr(bond, 'coupon_rate', '?'),
                    'Quantity': trade_qty,
                    'Price': bond.price
                })
                log_activity(f"{trade_action} {trade_qty} of Bond #{idx} at {bond.price}")
                autosave_session()
                st.sidebar.success(f"{trade_action} {trade_qty} of bond #{idx} executed.")
                # Notification for large trade
                if trade_qty >= 100:
                    st.sidebar.warning(f"Large trade: {trade_action} {trade_qty} units of bond #{idx}")
            else:
                st.sidebar.error("Portfolio not loaded.")
        else:
            st.sidebar.error("Invalid bond index.")
    except Exception as e:
        st.sidebar.error(f"Trade error: {e}")
# --- Restore Last Session ---
if st.sidebar.button("Restore Last Session"):
    try:
        with open("autosave_session.json", "r", encoding="utf-8") as f:
            import_state = _json.load(f)
        # Restore positions
        if 'positions' in import_state:
            bonds = []
            assets = {}
            for pos in import_state['positions']:
                bond = Bond(100, float(pos['coupon_rate']), float(pos['maturity']), 1)
                bonds.append(bond)
                assets[bond] = {
                    'quantity': int(pos['quantity']),
                    'price_per_unit': float(pos['avg_cost']),
                    'total_investment': int(pos['quantity']) * float(pos['avg_cost'])
                }
            st.session_state['bonds'] = bonds
            st.session_state['portfolio'] = Portfolio([])
            st.session_state['portfolio'].assets = assets
        st.session_state['reinvestable_money'] = import_state.get('reinvestable_money', 0.0)
        st.session_state['auto_sale_log'] = import_state.get('auto_sale_log', [])
        st.session_state['reinvestment_log'] = import_state.get('reinvestment_log', [])
        st.session_state['activity_feed'] = import_state.get('activity_feed', [])
        st.session_state['trade_history'] = import_state.get('trade_history', [])
        st.sidebar.success("Last session restored.")
    except Exception as e:
        st.sidebar.error(f"Restore failed: {e}")
# --- Activity Feed ---
st.sidebar.markdown("---")
st.sidebar.subheader("Activity Feed")
if st.session_state['activity_feed']:
    st.sidebar.text_area("Activity Feed", value="\n".join(st.session_state['activity_feed'][-20:]), height=200)
else:
    st.sidebar.info("No activity yet.")
# --- Feedback Form ---
st.sidebar.markdown("---")
st.sidebar.subheader("Feedback / Contact")
feedback = st.sidebar.text_area("Your feedback, suggestions, or issues:")
if st.sidebar.button("Submit Feedback"):
    with open("user_feedback.txt", "a", encoding="utf-8") as f:
        f.write(f"{pd.Timestamp.now().isoformat()} - {feedback}\n")
    st.sidebar.success("Thank you for your feedback!")
# --- Trade Blotter ---
st.sidebar.markdown("---")
st.sidebar.subheader("Order History / Trade Blotter")
if st.session_state['trade_history']:
    trade_df = pd.DataFrame(st.session_state['trade_history'])
    st.sidebar.dataframe(trade_df.tail(10), use_container_width=True)
    csv_trades = trade_df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("Download Trade History (CSV)", csv_trades, "trade_history.csv", "text/csv")
else:
    st.sidebar.info("No trades yet.")

# --- Reinvestable Money State ---
if 'reinvestable_money' not in st.session_state:
    st.session_state['reinvestable_money'] = 0.0
if 'auto_sale_log' not in st.session_state:
    st.session_state['auto_sale_log'] = []

# --- Tabs ---
tabs = st.tabs(["Data Input", "Curves", "Portfolio", "Scenarios", "Risk & VaR", "Reinvestable Money"])

# --- Data Input Tab ---
with tabs[0]:
    st.header("Data Input")
    data_file = st.file_uploader("Upload bond portfolio CSV (columns: maturity, coupon_rate, price, position_notional)", type=["csv"])
    df = None
    bonds = None
    portfolio = None
    if data_file is not None:
        try:
            df = pd.read_csv(data_file)
            required_cols = {"maturity", "coupon_rate", "price", "position_notional"}
            if not required_cols.issubset(df.columns):
                st.error(f"CSV must contain columns: {required_cols}")
                log_step("CSV missing required columns.")
                st.stop()
            # Check numeric types
            for col in required_cols:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    st.error(f"Column '{col}' must be numeric.")
                    log_step(f"Column '{col}' is not numeric.")
                    st.stop()
            # Build Bond objects
            bonds = []
            for _, row in df.iterrows():
                bond = Bond(100, row["coupon_rate"], row["maturity"], 1)  # Assume face=100, annual
                bond.price = row["price"]  # Assign market price
                bonds.append(bond)
            notionals = df["position_notional"].values
            portfolio = Portfolio(list(zip(bonds, notionals)))
            st.session_state['portfolio'] = portfolio
            st.session_state['bonds'] = bonds
            log_step("Portfolio and bonds loaded successfully.")
        except Exception as e:
            st.error(f"Error loading CSV: {e}")
            log_step(f"Error loading CSV: {e}")
    st.text_area("Log", st.session_state['log'], height=100)

# --- Curves Tab ---
with tabs[1]:
    st.header("Curves")
    if bonds is not None:
        spot_df = bootstrap_yield_curve(bonds)
        st.subheader("Bootstrapped Spot Curve")
        st.line_chart(spot_df.set_index("maturity")["spot_rate"], use_container_width=True)
        st.line_chart(spot_df.set_index("maturity")["interpolated_spot_rate"], use_container_width=True)
        log_step("Spot curve bootstrapped and plotted.")
    else:
        st.info("Upload data in 'Data Input' tab.")

# --- Portfolio Tab ---
with tabs[2]:
    st.header("Portfolio")
    if portfolio is not None and bonds is not None:
        spot_df = bootstrap_yield_curve(bonds)
        summary = portfolio.summary(spot_df.dropna(subset=["spot_rate"]))
        st.dataframe(summary.style.format({"Market Value": ".2f", "Weight %": ".2f", "Duration %": ".2f", "Convexity %": ".2f", "DV01": ".4f"}))
        orig_value = portfolio.total_value(spot_df.dropna(subset=['spot_rate']))
        orig_dv01 = portfolio.portfolio_dv01(spot_df.dropna(subset=['spot_rate']))
        st.metric("Total Portfolio Value", f"{orig_value:,.2f}")
        st.metric("Portfolio DV01", f"{orig_dv01:.4f}")
        # Panel toggles
        show_pos = st.checkbox("Show Position Table", value=True)
        show_pie = st.checkbox("Show Allocation Pie Chart", value=True)
        show_live = st.checkbox("Show Live Value Chart", value=True)
        # Position Table
        if show_pos:
            st.subheader("Current Positions")
            pos_data = []
            for i, bond in enumerate(bonds):
                asset = bond
                pos = portfolio.assets.get(asset, {})
                qty = pos.get('quantity', 0)
                avg_cost = pos.get('price_per_unit', bond.price)
                mkt_val = qty * bond.price
                pos_data.append({
                    'Bond': f"Bond #{i}",
                    'Maturity': getattr(bond, 'maturity', '?'),
                    'Coupon': getattr(bond, 'coupon_rate', '?'),
                    'Quantity': qty,
                    'Avg Cost': avg_cost,
                    'Market Price': bond.price,
                    'Market Value': mkt_val,
                    'Unrealized PnL': mkt_val - qty * avg_cost
                })
            pos_df = pd.DataFrame(pos_data)
            # Column selector and sort
            all_cols = list(pos_df.columns)
            show_cols = st.multiselect("Show Columns", all_cols, default=all_cols)
            sort_col = st.selectbox("Sort By", all_cols, index=0)
            sort_asc = st.radio("Sort Order", ["Ascending", "Descending"], index=1) == "Ascending"
            st.dataframe(pos_df[show_cols].sort_values(by=sort_col, ascending=sort_asc), use_container_width=True)
            # PnL alert
            total_unrealized_pnl = pos_df['Unrealized PnL'].sum()
            if total_unrealized_pnl < -1000:
                st.warning(f"Portfolio Unrealized PnL is negative: {total_unrealized_pnl:,.2f}")
        # Pie chart for allocation
        if show_pie and "Weight %" in summary.columns:
            fig = px.pie(summary, names=summary.index.astype(str), values="Weight %", title="Portfolio Allocation by Bond")
            st.plotly_chart(fig, use_container_width=True)
        # Simulated live portfolio value chart (random walk for demo)
        if show_live:
            if 'live_value' not in st.session_state:
                st.session_state['live_value'] = [orig_value]
            else:
                # Simulate new value (random walk)
                st.session_state['live_value'].append(st.session_state['live_value'][-1] * (1 + np.random.normal(0, 0.0005)))
                if len(st.session_state['live_value']) > 100:
                    st.session_state['live_value'] = st.session_state['live_value'][-100:]
            fig_live = go.Figure()
            fig_live.add_trace(go.Scatter(y=st.session_state['live_value'], mode='lines+markers', name='Portfolio Value'))
            fig_live.update_layout(title="Live Portfolio Value (Simulated)", xaxis_title="Time (refreshes)", yaxis_title="Value")
            st.plotly_chart(fig_live, use_container_width=True)
        # Diversification Button
        st.markdown("---")
        if st.button("Check Diversification"):
            # Check for sector column
            if "sector" not in df.columns:
                st.warning("Portfolio CSV must include a 'sector' column for sector diversification checks.")
            else:
                # Bond/stock level: no more than 5% (except real estate)
                over_5 = summary[(summary["Weight %"] > 5) & (~df["sector"].str.lower().eq("real estate"))]
                # Sector level: no more than 20% (except real estate)
                sector_weights = df.groupby(df["sector"].str.lower())["position_notional"].sum() / df["position_notional"].sum() * 100
                over_20 = sector_weights[(sector_weights > 20) & (sector_weights.index != "real estate")]
                auto_sale = False
                if not over_5.empty or not over_20.empty:
                    st.error("Diversification rule violated. Selling excess and moving proceeds to Reinvestable Money tab:")
                    # Sell excess in bonds/stocks
                    for idx in over_5.index:
                        bond_row = df.iloc[idx]
                        bond = bonds[idx]
                        # Calculate excess %
                        excess_pct = summary.loc[idx, "Weight %"] - 5
                        excess_notional = excess_pct / 100 * df["position_notional"].sum()
                        price = bond.price
                        qty_to_sell = int(np.floor(excess_notional / price))
                        if qty_to_sell > 0:
                            try:
                                st.session_state['portfolio'].remove_asset(bond, qty_to_sell)
                                proceeds = qty_to_sell * price
                                st.session_state['reinvestable_money'] += proceeds
                                st.session_state['auto_sale_log'].append({
                                    'Time': pd.Timestamp.now(),
                                    'Bond': f"Bond #{idx}",
                                    'Sector': bond_row['sector'],
                                    'Quantity Sold': qty_to_sell,
                                    'Proceeds': proceeds
                                })
                                st.write(f"Sold {qty_to_sell} of Bond #{idx} ({bond_row['sector']}) for ${proceeds:,.2f}")
                                auto_sale = True
                            except Exception as e:
                                st.warning(f"Auto-sale error for Bond #{idx}: {e}")
                    # Sell excess in sectors
                    for sector, pct in over_20.items():
                        sector_mask = df["sector"].str.lower() == sector
                        sector_df = df[sector_mask]
                        sector_bonds = [bonds[i] for i in sector_df.index]
                        sector_notional = sector_df["position_notional"].sum()
                        excess_pct = pct - 20
                        excess_notional = excess_pct / 100 * df["position_notional"].sum()
                        # Sell proportionally from all bonds in sector
                        for i, bond in zip(sector_df.index, sector_bonds):
                            bond_row = df.loc[i]
                            bond_notional = bond_row["position_notional"]
                            sell_notional = min(bond_notional, excess_notional * (bond_notional / sector_notional))
                            price = bond.price
                            qty_to_sell = int(np.floor(sell_notional / price))
                            if qty_to_sell > 0:
                                try:
                                    st.session_state['portfolio'].remove_asset(bond, qty_to_sell)
                                    proceeds = qty_to_sell * price
                                    st.session_state['reinvestable_money'] += proceeds
                                    st.session_state['auto_sale_log'].append({
                                        'Time': pd.Timestamp.now(),
                                        'Bond': f"Bond #{i}",
                                        'Sector': bond_row['sector'],
                                        'Quantity Sold': qty_to_sell,
                                        'Proceeds': proceeds
                                    })
                                    st.write(f"Sold {qty_to_sell} of Bond #{i} ({bond_row['sector']}) for ${proceeds:,.2f}")
                                    auto_sale = True
                                except Exception as e:
                                    st.warning(f"Auto-sale error for Bond #{i}: {e}")
                    if auto_sale:
                        st.info(f"Proceeds from auto-sales: ${st.session_state['reinvestable_money']:,.2f} (see 'Reinvestable Money' tab)")
                else:
                    st.success("Portfolio meets diversification requirements.")
        log_step("Portfolio summary displayed.")
    else:
        st.info("Upload data in 'Data Input' tab.")

# --- Reinvestable Money Tab ---
with tabs[5]:
    st.header("Reinvestable Money")
    # Summary dashboard
    st.metric("Available to Reinvest", f"${st.session_state['reinvestable_money']:,.2f}")
    st.write(f"Auto-Sales: {len(st.session_state['auto_sale_log'])} | Reinvestments: {len(st.session_state.get('reinvestment_log', []))}")
    # Diversification status
    diversification_status = "Unknown"
    if 'bonds' in st.session_state and st.session_state['bonds'] and 'portfolio' in st.session_state and st.session_state['portfolio']:
        # Try to get latest weights
        try:
            spot_df = bootstrap_yield_curve(st.session_state['bonds'])
            summary = st.session_state['portfolio'].summary(spot_df.dropna(subset=["spot_rate"]))
            df = None
            for tab in tabs:
                if hasattr(tab, 'data_file') and tab.data_file is not None:
                    df = pd.read_csv(tab.data_file)
                    break
            if df is not None and "sector" in df.columns:
                over_5 = summary[(summary["Weight %"] > 5) & (~df["sector"].str.lower().eq("real estate"))]
                sector_weights = df.groupby(df["sector"].str.lower())["position_notional"].sum() / df["position_notional"].sum() * 100
                over_20 = sector_weights[(sector_weights > 20) & (sector_weights.index != "real estate")]
                if not over_5.empty or not over_20.empty:
                    diversification_status = "Fail"
                else:
                    diversification_status = "Pass"
        except Exception:
            pass
    st.write(f"Diversification Status: **{diversification_status}**")
    # Reinvestment suggestions
    st.subheader("Reinvestment Suggestions")
    suggestions = []
    if 'bonds' in st.session_state and st.session_state['bonds'] and 'portfolio' in st.session_state and st.session_state['portfolio']:
        try:
            spot_df = bootstrap_yield_curve(st.session_state['bonds'])
            summary = st.session_state['portfolio'].summary(spot_df.dropna(subset=["spot_rate"]))
            if 'sector' in df.columns:
                for idx, row in summary.iterrows():
                    sector = df.iloc[idx]["sector"]
                    if row["Weight %"] < 5 and sector.lower() != "real estate":
                        suggestions.append(f"Bond #{idx} ({sector}): {row['Weight %']:.2f}% (underweight)")
        except Exception:
            pass
    if suggestions:
        st.write("Consider reinvesting in:")
        for s in suggestions:
            st.write(f"- {s}")
    else:
        st.write("No underweight bonds found (or missing sector data).")
    # Auto-Reinvest button
    if st.session_state['reinvestable_money'] > 0 and st.session_state.get('bonds'):
        strategy = st.selectbox("Reinvestment Strategy", ["Proportional", "Fill Up Most Underweight First"])
        if st.button("Auto-Reinvest All"):
            try:
                spot_df = bootstrap_yield_curve(st.session_state['bonds'])
                summary = st.session_state['portfolio'].summary(spot_df.dropna(subset=["spot_rate"]))
                if 'sector' in df.columns:
                    # Find eligible bonds
                    eligible = [(i, row) for i, row in summary.iterrows() if row["Weight %"] < 5 and df.iloc[i]["sector"].lower() != "real estate"]
                    if not eligible:
                        st.info("No eligible bonds for reinvestment.")
                    else:
                        cash = st.session_state['reinvestable_money']
                        reinvest_summary = []
                        if strategy == "Proportional":
                            total_weight_gap = sum(5 - row["Weight %"] for i, row in eligible)
                            for i, row in eligible:
                                bond = st.session_state['bonds'][i]
                                price = bond.price
                                gap = 5 - row["Weight %"]
                                alloc = min(cash, cash * (gap / total_weight_gap)) if total_weight_gap > 0 else 0
                                qty = int(np.floor(alloc / price))
                                if qty > 0:
                                    st.session_state['portfolio'].add_asset(bond, qty, price)
                                    used = qty * price
                                    st.session_state['reinvestable_money'] -= used
                                    if 'reinvestment_log' not in st.session_state:
                                        st.session_state['reinvestment_log'] = []
                                    st.session_state['reinvestment_log'].append({
                                        'Time': pd.Timestamp.now(),
                                        'Bond': f"Bond #{i}",
                                        'Quantity Bought': qty,
                                        'Amount Used': used
                                    })
                                    cash = st.session_state['reinvestable_money']
                                    reinvest_summary.append({
                                        'Bond': f"Bond #{i}",
                                        'Quantity Bought': qty,
                                        'Amount Used': used
                                    })
                        else:  # Fill up most underweight first
                            eligible_sorted = sorted(eligible, key=lambda x: x[1]["Weight %"])
                            for i, row in eligible_sorted:
                                bond = st.session_state['bonds'][i]
                                price = bond.price
                                gap = 5 - row["Weight %"]
                                max_alloc = gap / 100 * df["position_notional"].sum()
                                qty = int(np.floor(min(cash, max_alloc) / price))
                                if qty > 0:
                                    used = qty * price
                                    st.session_state['portfolio'].add_asset(bond, qty, price)
                                    st.session_state['reinvestable_money'] -= used
                                    if 'reinvestment_log' not in st.session_state:
                                        st.session_state['reinvestment_log'] = []
                                    st.session_state['reinvestment_log'].append({
                                        'Time': pd.Timestamp.now(),
                                        'Bond': f"Bond #{i}",
                                        'Quantity Bought': qty,
                                        'Amount Used': used
                                    })
                                    cash = st.session_state['reinvestable_money']
                                    reinvest_summary.append({
                                        'Bond': f"Bond #{i}",
                                        'Quantity Bought': qty,
                                        'Amount Used': used
                                    })
                                if cash < price:
                                    break
                        st.success("Auto-reinvestment complete.")
                        if reinvest_summary:
                            st.write("Reinvestment Summary:")
                            st.dataframe(pd.DataFrame(reinvest_summary))
                        if cash > 0:
                            st.info(f"${cash:,.2f} could not be reinvested due to 5% limit.")
            except Exception as e:
                st.warning(f"Auto-reinvest error: {e}")
    # Reinvestment form
    st.subheader("Reinvest Cash")
    if st.session_state['reinvestable_money'] > 0 and st.session_state.get('bonds'):
        reinvest_mode = st.selectbox("Reinvest By", ["Bond", "Sector"])
        if reinvest_mode == "Bond":
            reinvest_bond_idx = st.selectbox("Select Bond to Reinvest In", options=list(range(len(st.session_state['bonds']))), format_func=lambda i: f"Bond #{i}" if st.session_state['bonds'] else "")
            reinvest_amt = st.number_input("Amount to Invest", min_value=1.0, max_value=st.session_state['reinvestable_money'], value=100.0, step=1.0)
            if st.button("Reinvest"):
            # Before allocation
            spot_df = bootstrap_yield_curve(st.session_state['bonds'])
            summary_before = st.session_state['portfolio'].summary(spot_df.dropna(subset=["spot_rate"]))
            bond = st.session_state['bonds'][reinvest_bond_idx]
            price = bond.price
            qty = int(np.floor(reinvest_amt / price))
            # Check if this would breach 5% limit (except real estate)
            if 'sector' in df.columns and df.iloc[reinvest_bond_idx]["sector"].lower() != "real estate":
            total_notional = df["position_notional"].sum() + qty * price
            new_weight = (summary_before.loc[reinvest_bond_idx, "Market Value"] + qty * price) / total_notional * 100
            if new_weight > 5:
            st.warning("This reinvestment would breach the 5% per bond limit.")
            qty = int(np.floor((0.05 * total_notional - summary_before.loc[reinvest_bond_idx, "Market Value"]) / price))
            if qty > 0:
            st.session_state['portfolio'].add_asset(bond, qty, price)
            used = qty * price
            st.session_state['reinvestable_money'] -= used
            if 'reinvestment_log' not in st.session_state:
            st.session_state['reinvestment_log'] = []
            st.session_state['reinvestment_log'].append({
            'Time': pd.Timestamp.now(),
            'Bond': f"Bond #{reinvest_bond_idx}",
            'Quantity Bought': qty,
            'Amount Used': used
            })
            log_activity(f"Reinvested ${used:,.2f} into Bond #{reinvest_bond_idx} ({qty} units)")
            # After allocation
            spot_df = bootstrap_yield_curve(st.session_state['bonds'])
            summary_after = st.session_state['portfolio'].summary(spot_df.dropna(subset=["spot_rate"]))
            st.success(f"Reinvested ${used:,.2f} into Bond #{reinvest_bond_idx} ({qty} units)")
            # Show before/after pie chart
            st.write("Allocation Before:")
            fig_before = px.pie(summary_before, names=summary_before.index.astype(str), values="Weight %", title="Before")
            st.plotly_chart(fig_before, use_container_width=True)
            st.write("Allocation After:")
            fig_after = px.pie(summary_after, names=summary_after.index.astype(str), values="Weight %", title="After")
            st.plotly_chart(fig_after, use_container_width=True)
            else:
            st.warning("Amount too small to buy at least one unit or would breach diversification limit.")
            # Undo last action
            # Undo last action (choose type)
            undo_type = st.selectbox("Undo Last Action Type", ["Reinvestment", "Trade", "Auto-Sale", "Activity Log"])
            if st.button("Undo Last Action"):
            if undo_type == "Reinvestment" and st.session_state.get('reinvestment_log'):
            st.session_state['reinvestment_log'].pop()
            log_activity("Undid last reinvestment.")
            elif undo_type == "Trade" and st.session_state.get('trade_history'):
            st.session_state['trade_history'].pop()
            log_activity("Undid last trade.")
            elif undo_type == "Auto-Sale" and st.session_state.get('auto_sale_log'):
            st.session_state['auto_sale_log'].pop()
            log_activity("Undid last auto-sale.")
            elif undo_type == "Activity Log" and st.session_state.get('activity_feed'):
            st.session_state['activity_feed'].pop()
            st.success(f"Last {undo_type} action undone (note: this only undoes the last entry of the selected type; for full undo, reload previous export).")
        else:  # Sector reinvestment
            sector_choices = sorted(set(df["sector"])) if "sector" in df.columns else []
            sector = st.selectbox("Select Sector", sector_choices)
            reinvest_amt = st.number_input("Amount to Invest", min_value=1.0, max_value=st.session_state['reinvestable_money'], value=100.0, step=1.0, key="sector_amt")
            if st.button("Reinvest in Sector"):
                # Before allocation
                spot_df = bootstrap_yield_curve(st.session_state['bonds'])
                summary_before = st.session_state['portfolio'].summary(spot_df.dropna(subset=["spot_rate"]))
                sector_mask = df["sector"] == sector
                sector_bond_idxs = list(df[sector_mask].index)
                eligible = []
                for idx in sector_bond_idxs:
                    if sector.lower() == "real estate":
                        eligible.append(idx)
                    else:
                        if summary_before.loc[idx, "Weight %"] < 5:
                            eligible.append(idx)
                if not eligible:
                    st.warning("No eligible bonds in this sector for reinvestment.")
                else:
                    total_gap = sum(5 - summary_before.loc[idx, "Weight %"] for idx in eligible) if sector.lower() != "real estate" else len(eligible)
                    cash = reinvest_amt
                    reinvest_summary = []
                    for idx in eligible:
                        bond = st.session_state['bonds'][idx]
                        price = bond.price
                        if sector.lower() == "real estate":
                            alloc = cash / len(eligible)
                        else:
                            gap = 5 - summary_before.loc[idx, "Weight %"]
                            alloc = min(cash, cash * (gap / total_gap)) if total_gap > 0 else 0
                        qty = int(np.floor(alloc / price))
                        # Check sector limit (except real estate)
                        if sector.lower() != "real estate":
                            total_notional = df["position_notional"].sum() + qty * price
                            sector_notional = df[sector_mask]["position_notional"].sum() + qty * price
                            new_sector_weight = sector_notional / total_notional * 100
                            if new_sector_weight > 20:
                                st.warning(f"This reinvestment would breach the 20% sector limit for {sector}.")
                                continue
                        if qty > 0:
                            st.session_state['portfolio'].add_asset(bond, qty, price)
                            used = qty * price
                            st.session_state['reinvestable_money'] -= used
                            if 'reinvestment_log' not in st.session_state:
                                st.session_state['reinvestment_log'] = []
                            st.session_state['reinvestment_log'].append({
                                'Time': pd.Timestamp.now(),
                                'Bond': f"Bond #{idx}",
                                'Sector': sector,
                                'Quantity Bought': qty,
                                'Amount Used': used
                            })
                            cash -= used
                            reinvest_summary.append({
                                'Bond': f"Bond #{idx}",
                                'Sector': sector,
                                'Quantity Bought': qty,
                                'Amount Used': used
                            })
                    if reinvest_summary:
                        st.success(f"Reinvested in sector {sector}.")
                        # After allocation
                        spot_df = bootstrap_yield_curve(st.session_state['bonds'])
                        summary_after = st.session_state['portfolio'].summary(spot_df.dropna(subset=["spot_rate"]))
                        st.write("Allocation Before:")
                        fig_before = px.pie(summary_before, names=summary_before.index.astype(str), values="Weight %", title="Before")
                        st.plotly_chart(fig_before, use_container_width=True)
                        st.write("Allocation After:")
                        fig_after = px.pie(summary_after, names=summary_after.index.astype(str), values="Weight %", title="After")
                        st.plotly_chart(fig_after, use_container_width=True)
                        st.dataframe(pd.DataFrame(reinvest_summary))
                    else:
                        st.warning("No reinvestment performed (limits would be breached or amount too small).")
    # Sector allocation chart (before/after if possible)
    st.subheader("Sector Allocation")
    if 'bonds' in st.session_state and st.session_state['bonds'] and 'portfolio' in st.session_state and st.session_state['portfolio'] and 'sector' in df.columns:
        spot_df = bootstrap_yield_curve(st.session_state['bonds'])
        summary = st.session_state['portfolio'].summary(spot_df.dropna(subset=["spot_rate"]))
        # Map bond index to sector
        sector_map = {i: df.iloc[i]["sector"] for i in range(len(df))}
        sector_alloc = {}
        for i, row in summary.iterrows():
            sector = sector_map.get(i, "Unknown")
            sector_alloc[sector] = sector_alloc.get(sector, 0) + row["Weight %"]
        sector_df = pd.DataFrame(list(sector_alloc.items()), columns=["Sector", "Weight %"])
        # Highlight over/underweight
        sector_df["Status"] = sector_df.apply(lambda r: "Overweight" if r["Sector"].lower() != "real estate" and r["Weight %"] > 20 else ("Underweight" if r["Sector"].lower() != "real estate" and r["Weight %"] < 20 else "OK"), axis=1)
        fig_sector = px.pie(sector_df, names="Sector", values="Weight %", color="Status", color_discrete_map={"Overweight": "red", "Underweight": "orange", "OK": "green"}, title="Sector Allocation (Red: >20%, Orange: <20%, Green: Real Estate or OK)")
        st.plotly_chart(fig_sector, use_container_width=True)
        st.dataframe(sector_df, use_container_width=True)
    # Reinvestment log
    st.subheader("Reinvestment Log")
    if st.session_state.get('reinvestment_log'):
        reinvest_df = pd.DataFrame(st.session_state['reinvestment_log'])
        st.dataframe(reinvest_df, use_container_width=True)
        csv_reinv = reinvest_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Reinvestment Log (CSV)", csv_reinv, "reinvestment_log.csv", "text/csv")
    # Auto-sale log
    st.subheader("Auto-Sale Log")
    if st.session_state['auto_sale_log']:
        auto_sale_df = pd.DataFrame(st.session_state['auto_sale_log'])
        st.dataframe(auto_sale_df, use_container_width=True)
        csv_auto = auto_sale_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Auto-Sale Log (CSV)", csv_auto, "auto_sale_log.csv", "text/csv")
    else:
        st.info("No auto-sales yet.")
    # Export/import/reset/help
    st.subheader("Export/Import/Reset Portfolio State")
    import json
    export_state = {
        'positions': [
            {
                'bond': f"Bond #{i}",
                'maturity': getattr(b, 'maturity', '?'),
                'coupon_rate': getattr(b, 'coupon_rate', '?'),
                'quantity': st.session_state['portfolio'].assets.get(b, {}).get('quantity', 0),
                'avg_cost': st.session_state['portfolio'].assets.get(b, {}).get('price_per_unit', '?'),
                'sector': df.iloc[i]["sector"] if "sector" in df.columns else None
            }
            for i, b in enumerate(st.session_state['bonds'])
        ],
        'reinvestable_money': st.session_state['reinvestable_money'],
        'auto_sale_log': st.session_state['auto_sale_log'],
        'reinvestment_log': st.session_state.get('reinvestment_log', []),
        'activity_feed': st.session_state.get('activity_feed', [])
    }
    st.download_button("Export Portfolio State (JSON)", json.dumps(export_state, default=str).encode('utf-8'), "portfolio_state.json", "application/json")
    import_file = st.file_uploader("Import Portfolio State (JSON)", type=["json"], key="import_json")
    if import_file is not None:
        try:
            import_state = json.load(import_file)
            # Restore positions
            if 'positions' in import_state:
                # Rebuild bonds and portfolio
                bonds = []
                assets = {}
                for pos in import_state['positions']:
                    bond = Bond(100, float(pos['coupon_rate']), float(pos['maturity']), 1)
                    bonds.append(bond)
                    assets[bond] = {
                        'quantity': int(pos['quantity']),
                        'price_per_unit': float(pos['avg_cost']),
                        'total_investment': int(pos['quantity']) * float(pos['avg_cost'])
                    }
                st.session_state['bonds'] = bonds
                st.session_state['portfolio'] = Portfolio([])
                st.session_state['portfolio'].assets = assets
            st.session_state['reinvestable_money'] = import_state.get('reinvestable_money', 0.0)
            st.session_state['auto_sale_log'] = import_state.get('auto_sale_log', [])
            st.session_state['reinvestment_log'] = import_state.get('reinvestment_log', [])
            st.session_state['activity_feed'] = import_state.get('activity_feed', [])
            st.success("Portfolio state imported successfully.")
        except Exception as e:
            st.error(f"Import failed: {e}")
    if st.button("Reset Session"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.experimental_rerun()
    with st.expander("Help & Guidance", expanded=False):
        st.markdown("""
        **Diversification Rules:**
        - No more than 5% in any single bond/stock (except real estate)
        - No more than 20% in any single sector (except real estate)
        
        **Reinvestment Options:**
        - Reinvest by bond or sector, with limits enforced
        - Auto-reinvest distributes cash among underweight bonds
        
        **Tabs:**
        - Portfolio: View positions, allocation, and check diversification
        - Reinvestable Money: Manage cash, reinvest, and export/import state
        - Risk & VaR: Run simulations and view risk metrics
        - Scenarios: Analyze yield curve shocks
        
        **Export/Import:**
        - Export your full portfolio, cash, and logs as JSON
        - Import to restore a previous session
        - Reset clears all data and starts fresh
        """)

# --- Scenarios Tab ---
with tabs[3]:
    st.header("Scenarios")
    if bonds is not None:
        spot_df = bootstrap_yield_curve(bonds)
        scenario = st.selectbox("Scenario", ["parallel", "steepening"], index=0)
        shift_bp = st.slider("Yield curve shift (basis points)", min_value=-200, max_value=200, value=0, step=1)
        shocked_df = simulate_yield_shift(spot_df, scenario, shift_bp)
        # Plotly for scenario curves
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=spot_df["maturity"], y=spot_df["spot_rate"], mode='lines+markers', name='Original'))
        fig.add_trace(go.Scatter(x=shocked_df["maturity"], y=shocked_df["spot_rate"], mode='lines+markers', name='Shocked'))
        fig.update_layout(title="Original vs. Shocked Zero Curves", xaxis_title="Maturity (years)", yaxis_title="Spot Rate")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Compare the original and shocked spot curves under the selected scenario.")
        log_step(f"Scenario '{scenario}' with shift {shift_bp}bp applied.")
    else:
        st.info("Upload data in 'Data Input' tab.")

# --- Risk & VaR Tab ---
with tabs[4]:
    st.header("Risk & VaR")
    if portfolio is not None and bonds is not None:
        spot_df = bootstrap_yield_curve(bonds)
        n_scenarios = st.number_input("# Scenarios", min_value=100, max_value=10000, value=1000, step=100)
        vol = st.number_input("Yield Curve Volatility (annual, %)", min_value=0.01, max_value=5.0, value=1.0, step=0.01) / 100
        dt = st.number_input("Time Step (years)", min_value=0.01, max_value=1.0, value=0.25, step=0.01)
        alpha = st.slider("VaR Confidence Level", min_value=0.90, max_value=0.99, value=0.95, step=0.01)
        if st.button("Run Simulation"):
            vals = simulate_portfolio_paths(portfolio, spot_df, int(n_scenarios), vol, dt)
            pnl = vals - np.mean(vals)
            # Plotly histogram for PnL
            fig = px.histogram(pd.DataFrame({"PnL": pnl}), x="PnL", nbins=30, title="Simulated Portfolio P&L Distribution")
            st.plotly_chart(fig, use_container_width=True)
            var = calculate_var(vals, alpha)
            st.metric(f"{int(alpha*100)}% VaR", f"{var:,.2f}")
            st.caption("Value-at-Risk (VaR) is the loss not exceeded with the selected confidence level.")
            log_step(f"Monte Carlo simulation run ({n_scenarios} scenarios, vol={vol}, dt={dt}). VaR={var:,.2f}")
            # Notification for VaR breach
            if var > 1000:  # Example threshold
                st.warning(f"VaR exceeds threshold: {var:,.2f}")
        # Candlestick chart for selected bond
        st.subheader("Bond Price Candlestick (Simulated)")
        bond_names = [f"Bond #{i}: {getattr(b, 'maturity', '?')}y {getattr(b, 'coupon_rate', '?')*100:.2f}%" for i, b in enumerate(st.session_state.get('bonds', []))]
        selected_bond_idx = st.selectbox("Select Bond for Candlestick Chart", options=list(range(len(bond_names))), format_func=lambda i: bond_names[i] if bond_names else "", key="candle_bond")
        # Timeframe selector
        timeframe = st.selectbox("Timeframe", options=["1W", "1M", "3M", "6M", "1Y"], index=1)
        n_map = {"1W": 7, "1M": 30, "3M": 90, "6M": 180, "1Y": 365}
        n = n_map[timeframe]
        np.random.seed(selected_bond_idx)
        price = 100 + np.cumsum(np.random.normal(0, 0.2, n))
        open_ = price + np.random.normal(0, 0.1, n)
        close = price + np.random.normal(0, 0.1, n)
        high = np.maximum(open_, close) + np.abs(np.random.normal(0, 0.05, n))
        low = np.minimum(open_, close) - np.abs(np.random.normal(0, 0.05, n))
        dates = pd.date_range(end=pd.Timestamp.today(), periods=n)
        # Technical indicator overlays
        indicator_opts = st.multiselect("Indicators", ["SMA", "EMA", "Bollinger Bands"], default=["SMA"])
        sma_window = st.slider("SMA/EMA Window (days)", min_value=2, max_value=min(30, n//2), value=5)
        close_series = pd.Series(close)
        fig_candle = go.Figure(data=[go.Candlestick(x=dates, open=open_, high=high, low=low, close=close)])
        if "SMA" in indicator_opts:
            sma = close_series.rolling(window=sma_window).mean()
            fig_candle.add_trace(go.Scatter(x=dates, y=sma, mode='lines', name=f'SMA {sma_window}d', line=dict(color='orange')))
        if "EMA" in indicator_opts:
            ema = close_series.ewm(span=sma_window, adjust=False).mean()
            fig_candle.add_trace(go.Scatter(x=dates, y=ema, mode='lines', name=f'EMA {sma_window}d', line=dict(color='blue')))
        if "Bollinger Bands" in indicator_opts:
            sma = close_series.rolling(window=sma_window).mean()
            std = close_series.rolling(window=sma_window).std()
            upper = sma + 2*std
            lower = sma - 2*std
            fig_candle.add_trace(go.Scatter(x=dates, y=upper, mode='lines', name='BB Upper', line=dict(color='green', dash='dot')))
            fig_candle.add_trace(go.Scatter(x=dates, y=lower, mode='lines', name='BB Lower', line=dict(color='red', dash='dot')))
        fig_candle.update_layout(title=f"Simulated Bond Price Candlestick: {bond_names[selected_bond_idx] if bond_names else ''}", xaxis_title="Date", yaxis_title="Price")
        st.plotly_chart(fig_candle, use_container_width=True)
        # Download chart as PNG
        img_bytes = fig_candle.to_image(format="png")
        st.download_button("Download Candlestick Chart (PNG)", img_bytes, file_name="candlestick.png", mime="image/png")
        # RSI chart
        st.subheader("RSI (Relative Strength Index)")
        delta = pd.Series(close).diff()
        up = delta.clip(lower=0)
        down = -delta.clip(upper=0)
        roll_up = up.rolling(window=14).mean()
        roll_down = down.rolling(window=14).mean()
        rs = roll_up / roll_down
        rsi = 100 - (100 / (1 + rs))
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=dates, y=rsi, mode='lines', name='RSI', line=dict(color='purple')))
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
        fig_rsi.update_layout(title="RSI (14-day)", xaxis_title="Date", yaxis_title="RSI", yaxis_range=[0,100])
        st.plotly_chart(fig_rsi, use_container_width=True)
        # PDF export placeholder
        if st.button("Export Summary to PDF"):
            st.info("PDF export feature coming soon.")
    else:
        st.info("Upload data in 'Data Input' tab.")
