# Fixed Income Portfolio Management Dashboard

<img width="1919" height="853" alt="image" src="https://github.com/user-attachments/assets/1ecda756-60da-468c-b438-7033a4198383" />



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

### Portfolio Import & Validation
Upload and validate your bond portfolio data with real-time feedback and error checking.

<img width="1919" height="846" alt="image" src="https://github.com/user-attachments/assets/ee4b1334-f134-4cf6-9eba-77ccc0c0c816" />

### Interest Rate Curves
Visualize bootstrapped spot curves and forward rates with interactive plotting.

<img width="1916" height="855" alt="image" src="https://github.com/user-attachments/assets/be6b4762-2c0b-46f7-b712-9213c0dbf52d" />


### Holdings & Risk Overview
Comprehensive portfolio metrics, risk analysis, and diversification monitoring.

<p align="center"> <img width="45%" alt="Holdings Breakdown" src="https://github.com/user-attachments/assets/43cc8ab1-a39a-489b-9ec5-4a6837bf6c2f" /> <img width="45%" alt="Risk Metrics" src="https://github.com/user-attachments/assets/c27698e2-c9a8-468e-8374-85c3caa8bebd" /> </p>




### Interest Rate Stress Testing
Apply yield curve shocks and analyze portfolio sensitivity to interest rate changes.

<img width="1919" height="775" alt="image" src="https://github.com/user-attachments/assets/5a0a1ae1-d9c0-4a36-8c65-48bb27ed7868" />

### Monte Carlo Simulations & Value-at-Risk (VaR)
Monte Carlo simulation results with Value-at-Risk calculations and P&L distributions.
<img width="1919" height="802" alt="image" src="https://github.com/user-attachments/assets/b5da591f-637e-4ed6-96ce-0d5225f15145" />


### Cash Reinvestment Engine
Cash management, reinvestment automation, and diversification rule enforcement.

<img width="1903" height="842" alt="image" src="https://github.com/user-attachments/assets/f30ad4ad-4633-425a-9d8e-119c366dd002" />

### Session Controls & Audit Log
Portfolio state management, preferences, and data export/import functionality.

<img width="1919" height="867" alt="image" src="https://github.com/user-attachments/assets/de9f5396-08a2-4499-a0f0-e8829881eb3b" />


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
   git clone https://github.com/agastya-kataria/portfolio-management.git
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
- For direct support, open an issue or contact the maintainer at [agastyakataria176@gmail.com].

---

## 🏷️ License
MIT License

---

## 📦 Badges
[![Streamlit Cloud](https://img.shields.io/badge/Streamlit-Live-green)](https://share.streamlit.io/agastya-kataria/portfolio-management)
[![Tests](https://github.com/agastya-kataria/portfolio-management/actions/workflows/python-app.yml/badge.svg)](https://github.com/agastya-kataria/portfolio-management/actions)

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
