# Optimized Smart Money Concept (SMC) Gold Backtester

This repository contains a specialized Python-based backtesting engine designed for **Gold (XAU/USD)**. It implements an automated strategy based on **Smart Money Concepts (SMC)**, specifically focusing on session-based liquidity sweeps, Fair Value Gaps (FVG), and trend-alignment with the 20-period Exponential Moving Average (EMA).

## 🚀 Strategy Overview
The strategy identifies potential trade setups during major market sessions (London & New York). It uses a rule-based logic to determine high-probability entries:

* **Trend Filter:** 20-period EMA to ensure trades are aligned with the short-term trend.
* **Liquidity Logic:** Checks for price interaction with recent 24-hour highs/lows.
* **Imbalance Filter:** Detects Fair Value Gaps (FVG) as confirmation for entry.
* **Trade Management:**
    * **TP1 (30% partial):** Locked in at 10 points.
    * **Break Even (BE):** Automatically shifts stop-loss to entry price after TP1 is hit.
    * **TP2 (70% partial):** Target profit exit at 30 points.
    * **Risk:** Fixed at 10 points for initial stop-loss.

## 🛠️ Technical Stack
* **Language:** Python 3.x
* **Data Source:** `yfinance` (Yahoo Finance API)
* **Data Analysis:** `pandas`, `numpy`

## 📂 Project Structure
```text
/smc-gold-backtester
├── main.py           # Core logic, signal generation, and backtesting engine
└── README.md         # Documentation
