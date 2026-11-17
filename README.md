# 📈 SMC Backtester

<div align="center">

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Backtesting](https://img.shields.io/badge/Backtesting-9ECE6A?style=for-the-badge)](https://github.com/Mounib-Chandoul/SMC_Trader_Bot)
[![License: MIT](https://img.shields.io/badge/License-MIT-9ECE6A?style=for-the-badge)](LICENSE)

</div>

A rule-based backtesting engine for **Smart Money Concepts (SMC)** strategies
on Gold (XAU/USD) and EUR/USD. It focuses on session liquidity sweeps, Fair
Value Gaps (FVG) and EMA trend alignment — with explicit partial-exit and
break-even rules.

---

## Strategy

| Component | Rule |
|---|---|
| Session | London and New York windows only |
| Trend filter | Price aligned with the 20-period EMA |
| Liquidity | Interaction with recent 24h highs/lows (sweep) |
| Confirmation | Fair Value Gap (imbalance) present |
| Initial risk | Fixed 10-point stop-loss |
| TP1 | 30% partial at +10 points |
| Break-even | Stop moves to entry after TP1 |
| TP2 | Remaining 70% exited at +30 points |

Two tuned variants are included:

- `backtest_gold_optimized.py` — XAU/USD
- `backtest_eurusd_optimized.py` — EUR/USD

---

## Stack

- Python 3.x
- `yfinance` for historical data
- `pandas` / `numpy` for indicators and the event loop

---

## Run

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python backtest_gold_optimized.py
python backtest_eurusd_optimized.py
```

Each script downloads its instrument, applies the rules bar by bar and prints
performance statistics (trades, win rate, PnL, drawdown).

---

## Layout

```text
SMC_Trader_Bot/
├── backtest_gold_optimized.py    # XAU/USD strategy + engine
├── backtest_eurusd_optimized.py  # EUR/USD variant
├── requirements.txt
└── README.md
```

---

## ⚠️ Disclaimer

Educational research only. Past performance in a backtest does not predict
future results, and nothing here constitutes financial advice. No live order
placement is implemented.

## License

[MIT](LICENSE).
