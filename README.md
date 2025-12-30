#Quantitative Developer Assignment (Numatix)

Multi-Timeframe Trading System

Quantitative Developer Assignment – Institutional-Grade Design

Overview

This project implements a deterministic, multi-timeframe trading system designed with institutional engineering standards.
The system cleanly separates strategy logic, market data alignment, backtesting, and live execution, ensuring no lookahead bias, no environment leakage, and full reproducibility.

The architecture supports:

Offline backtesting

Live execution on Binance Spot Testnet

Strategy parity between backtest and live trading

Core Design Principles

Closed-candle only decisions

Strict timestamp monotonicity

Deterministic strategy outputs

Single Source of Truth for decision logic

Environment-agnostic strategy layer

No exchange-specific logic inside strategy

Strategy Logic
Multi-Timeframe EMA Strategy

Execution timeframe: 5-minute candles

Regime timeframe: 15-minute candles

Indicators
Timeframe	Indicator
5m	EMA(8), EMA(21)
15m	EMA(50), EMA(200)
Regime Filter

Bullish: EMA50(15m) > EMA200(15m)

Bearish: EMA50(15m) < EMA200(15m)

Entry Conditions

Long

Bullish regime

EMA8 crosses above EMA21 on 5m

Short

Bearish regime

EMA8 crosses below EMA21 on 5m

Exit Conditions

Opposite EMA cross on 5m timeframe

All decisions are purely deterministic and depend only on historical candle data.

Project Structure
multi-tf-trading-system/
│
├── strategy/
│   ├── base.py                  # Strategy interface & domain models
│   └── multi_tf_strategy.py     # Multi-TF EMA strategy
│
├── utils/
│   └── data_handler.py          # 5m ↔ 15m candle alignment
│
├── backtesting/
│   └── backtest_runner.py       # Deterministic backtesting engine
│
├── trading/
│   ├── exchange.py              # Binance Testnet wrapper
│   └── live_executor.py         # Live execution engine
│
├── data/
│   ├── BTCUSDT_5m.csv
│   ├── backtest_trades.csv
│   └── live_trades.csv
│
├── .env                         # API keys (ignored)
├── .gitignore
└── README.md

Market Data Handling
Candle Alignment

Only closed 5-minute candles are processed

Every 3 × 5m candles → 1 × 15m candle

Timestamp = close time of last 5m candle

Guarantees no lookahead bias

Implemented in:

utils/data_handler.py

Backtesting
Features

Sequential replay of historical candles

Strategy reset before each run

Trade-by-trade recording

CSV export for analysis

Run Backtest
python backtesting/run_backtest.py


Output:

data/backtest_trades.csv

Live Execution (Binance Spot Testnet)
Key Characteristics

Uses same strategy & data pipeline as backtest

Polls only closed 5m candles

Supports dry-run mode (no real orders)

Market orders only (for execution clarity)

Environment Setup

Create .env file:

BINANCE_API_KEY=your_testnet_api_key
BINANCE_API_SECRET=your_testnet_api_secret


Ensure .env is ignored:

.env

Test API Connectivity
python test_binance_testnet.py


Expected output:

Connected. Balances: [...]

Live Execution
Dry-Run Mode (Recommended First)
executor = LiveExecutor(
    exchange=exchange,
    symbol="BTCUSDT",
    quantity=0.001,
    dry_run=True
)
executor.run()

Real Testnet Trading
executor = LiveExecutor(
    exchange=exchange,
    symbol="BTCUSDT",
    quantity=0.001,
    dry_run=False
)
executor.run()


Trades recorded in:

data/live_trades.csv

Determinism & Safety Guarantees

No randomness

No forward-looking data

No mutable shared state across layers

Strategy unaware of:

Exchange

Orders

Fills

Slippage

Environment variables

Engineering Quality Checklist

✔ Clean separation of concerns
✔ Deterministic logic
✔ Multi-timeframe confirmation
✔ Backtest ↔ live parity
✔ Exchange abstraction
✔ Environment-safe credential handling
✔ Institutional-grade architecture

Extension-Ready Design

This system can be extended with:

Risk-based position sizing

Slippage & fee modeling

WebSocket market data

Portfolio-level execution

PnL analytics

Strategy ensemble support

Final Notes

This project demonstrates production-grade quantitative engineering, not retail scripting.
The focus is on correctness, determinism, and architectural discipline, aligning with institutional trading system design.

Author:
Aditya Raj
Quantitative Developer Candidate
