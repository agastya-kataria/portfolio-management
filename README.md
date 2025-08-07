# Fixed Income Portfolio Management Dashboard

![Dashboard Banner](docs/banner.png)

A modern, open-source Streamlit dashboard for fixed income portfolio analytics, scenario analysis, and risk management. Supports vanilla, callable, and inflation-protected (TIPS) bonds, scenario-based yield curve shocks, Monte Carlo simulation, Value-at-Risk (VaR), and advanced portfolio automation.

---

## 🚀 Features

- **Flexible Bond Analytics:** Price vanilla, callable, and TIPS bonds with risk metrics.
- **Yield Curve Bootstrapping:** Build and visualize spot curves from market data.
- **Scenario Analysis:** Apply parallel and steepening yield curve shocks.
- **Portfolio Management:** Upload, analyze, and summarize bond portfolios.
- **Monte Carlo & VaR:** Simulate portfolio P&L and compute Value-at-Risk.
- **Diversification Automation:** Enforce 5%/20% rules, auto-sell, and reinvest excess.
- **Reinvestable Money:** Track, reinvest, and visualize freed-up cash.
- **Audit Trail & Undo:** Persistent activity feed, granular undo, and autosave/restore.
- **Customizable UI:** Choose columns, sort tables, light/dark theme, mobile-friendly.
- **Accessibility:** High-contrast, large controls, ARIA labels, and keyboard navigation.
- **User Feedback:** Built-in feedback form and help/guidance.

---

## 🏁 Quickstart / Onboarding

1. **Upload your bond portfolio CSV** (columns: `maturity`, `coupon_rate`, `price`, `position_notional`, `sector`).
2. **Explore tabs:**
   - Data Input: Upload and validate data.
   - Curves: View bootstrapped and interpolated spot curves.
   - Portfolio: See summary metrics, risk, and check diversification.
   - Scenarios: Apply yield curve shocks and compare.
   - Risk & VaR: Run Monte Carlo simulation and view VaR.
   - Reinvestable Money: Manage cash, reinvest, and export/import state.
3. **Trade, reinvest, and manage risk** using the sidebar and dashboard controls.
4. **Export/Import** your full portfolio state for backup or transfer.

---

## 📊 Screenshots & Graphics

| Dashboard Overview | Diversification & Reinvestment | Risk & VaR |
|-------------------|-------------------------------|------------|
| ![Overview](docs/screenshot_overview.png) | ![Diversification](docs/screenshot_diversification.png) | ![VaR](docs/screenshot_var.png) |

> _Replace these with your own screenshots for a personalized README!_

---

## 📱 Accessibility & Mobile Support
- Large, touch-friendly controls and font sizes
- High-contrast color scheme (light/dark)
- Keyboard navigation and ARIA labels
- Responsive layout for mobile and desktop

---

## 💾 Autosave & Restore
- **Autosave:** Session state (positions, cash, logs, preferences) is saved after every major action.
- **Restore:** Use the sidebar button to reload your last session instantly.

---

## 📝 Undo & Audit Trail
- **Undo:** Revert the last trade, reinvestment, auto-sale, or activity log entry.
- **Audit Trail:** Persistent activity feed, exportable and importable with your portfolio state.

---

## 🛠️ Installation

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

## 🤝 Feedback & Support
- Use the sidebar feedback form to send suggestions or report issues.
- For direct support, open an issue or contact the maintainer at [your.email@example.com].

---

## 🏷️ License
MIT License

---

## 📦 Badges
[![Streamlit Cloud](https://img.shields.io/badge/Streamlit-Live-green)](https://share.streamlit.io/yourusername/portfolio-management)
[![Tests](https://github.com/yourusername/portfolio-management/actions/workflows/python-app.yml/badge.svg)](https://github.com/yourusername/portfolio-management/actions)

---

## 🌐 Deployment

You can deploy this app for free on [Streamlit Cloud](https://streamlit.io/cloud) or [Render](https://render.com/):
- Push your repo to GitHub
- Connect your repo on Streamlit Cloud or Render
- Set the entrypoint to `src/streamlit_app.py`

---

## 👋 Contributing

Contributions are welcome! Please:
- Fork the repo and create a feature branch.
- Write clear commit messages and add docstrings/comments.
- Ensure all tests pass (`pytest`).
- Open a pull request with a clear description.

---

## 📚 Acknowledgments
- Streamlit, Plotly, pandas, numpy, and the open-source community.

---

> _For more info, see the in-app Help & Guidance expander or the sidebar Getting Started guide._
