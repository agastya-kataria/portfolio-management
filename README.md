# Fixed Income Portfolio Management Dashboard

A modern, open-source Streamlit dashboard for fixed income portfolio analytics, scenario analysis, and risk management. Supports vanilla, callable, and inflation-protected (TIPS) bonds, scenario-based yield curve shocks, Monte Carlo simulation, and Value-at-Risk (VaR) analysis.

---

## Features
- **Flexible Bond Analytics:** Price vanilla, callable, and TIPS bonds with risk metrics.
- **Yield Curve Bootstrapping:** Build and visualize spot curves from market data.
- **Scenario Analysis:** Apply parallel and steepening yield curve shocks.
- **Portfolio Management:** Upload, analyze, and summarize bond portfolios.
- **Monte Carlo & VaR:** Simulate portfolio P&L and compute Value-at-Risk.
- **Streamlit UI:** Tabbed interface, real-time logging, CSV validation, and theme toggle.
- **Export:** (Coming soon) Export summary reports to PDF.

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/portfolio-management.git
   cd portfolio-management
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the app:**
   ```bash
   streamlit run src/streamlit_app.py
   ```

---

## Usage Example

1. **Upload your bond portfolio CSV** (columns: `maturity`, `coupon_rate`, `price`, `position_notional`).
2. **Navigate tabs:**
   - Data Input: Upload and validate data.
   - Curves: View bootstrapped and interpolated spot curves.
   - Portfolio: See summary metrics and risk.
   - Scenarios: Apply yield curve shocks and compare.
   - Risk & VaR: Run Monte Carlo simulation and view VaR.
3. **Export:** (Coming soon) Export summary to PDF.

![Dashboard Screenshot](docs/screenshot.png)

---

## Contributing

Contributions are welcome! Please:
- Fork the repo and create a feature branch.
- Write clear commit messages and add docstrings/comments.
- Ensure all tests pass (`pytest`).
- Open a pull request with a clear description.

---

## License
MIT License

---

## Badges
[![Streamlit Cloud](https://img.shields.io/badge/Streamlit-Live-green)](https://share.streamlit.io/yourusername/portfolio-management)
[![Tests](https://github.com/yourusername/portfolio-management/actions/workflows/python-app.yml/badge.svg)](https://github.com/yourusername/portfolio-management/actions)

---

## Deployment

You can deploy this app for free on [Streamlit Cloud](https://streamlit.io/cloud) or [Render](https://render.com/):
- Push your repo to GitHub
- Connect your repo on Streamlit Cloud or Render
- Set the entrypoint to `src/streamlit_app.py`

---

## Contact
For questions or support, open an issue or contact the maintainer at [your.email@example.com].
