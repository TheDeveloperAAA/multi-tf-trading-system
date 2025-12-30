#Quantitative Developer Assignment (Numatix)

Multi-Timeframe Trading System (Quantitative Developer Assignment)
Overview

This project implements a deterministic multi-timeframe trading system designed to demonstrate engineering parity between backtesting and live execution.
The system uses a single strategy implementation shared across environments, ensuring that any differences in results arise only from execution mechanics—not strategy logic.

The focus of this assignment is correctness, determinism, and clean system design, not performance optimization.

Strategy Logic

Entry timeframe: 5-minute candles

Confirmation timeframe: 15-minute candles

Rules

Long Entry

5m EMA(8) crosses above EMA(21)

15m EMA(50) > EMA(200)

Short Entry

5m EMA(8) crosses below EMA(21)

15m EMA(50) < EMA(200)

Exit

Opposite EMA(8/21) crossover on the 5m timeframe

All signals are generated only on closed candles to avoid look-ahead bias.

Architecture
strategy/        → Pure strategy logic (environment-agnostic)
utils/           → Candle alignment & data handling
backtesting/     → Deterministic backtest engine
trading/         → Live execution engine (Binance Testnet)
data/            → Generated data artifacts (ignored by git)

Design Principles

Single source of truth: One strategy class shared by backtest and live

Deterministic processing: No randomness, no time-based logic

Strict separation of concerns: Strategy ≠ execution ≠ data acquisition

Determinism

Historical BTCUSDT 5-minute candles are fetched once from Binance REST and persisted to CSV.

A fixed candle window is replayed during backtesting.

The strategy state is reset before each run.

Repeated backtest executions on the same input produce identical trade outputs, verified via file diff.

This guarantees deterministic behavior for the backtest engine.

Backtest ↔ Live Parity

The same strategy implementation (MultiTFEMAStrategy) is used for:

Backtesting

Live execution

Candle alignment and signal generation occur identically in both paths.

Trade decisions (ENTER_LONG, ENTER_SHORT, EXIT) are generated in the same way.

The only difference is the execution sink:

Backtest → CSV trade log

Live → exchange interface (Binance Testnet)

Trade Schema (Identical in Both Paths)
direction, entry_time, entry_price, exit_time, exit_price


This ensures that any discrepancy between backtest and live results can only arise from execution mechanics, not strategy logic.

Data Source

Market: BTCUSDT (Binance Spot)

Timeframe: 5 minutes

Data acquisition is performed once via Binance REST API.

Generated CSV files are not committed to the repository to keep it clean and reproducible.

How to Run
Deterministic Backtest
python -m backtesting.run_backtest

Live Execution (Binance Testnet)
python -m trading.live_executor


The live executor supports a dry-run mode, allowing parity validation without placing real orders.

Key Takeaways

Deterministic backtesting is enforced by construction.

Strategy logic is fully decoupled from execution.

Backtest and live environments share identical decision logic.

The system prioritizes correctness, reproducibility, and clarity over optimization.

Notes

This project is intentionally minimal and focused on engineering quality rather than trading performance.
It is designed to be easy to reason about, review, and extend.
