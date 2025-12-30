import csv
from backtesting.backtest_runner import BacktestRunner
from strategy.base import Candle


def load_candles_from_csv(path: str, limit: int):
    candles = []
    with open(path, "r") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= limit:
                break
            candles.append(
                Candle(
                    timestamp=int(row["timestamp"]),
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=0.0,
                )
            )
    return candles


def run(output_path: str):
    candles_5m = load_candles_from_csv(
        "data/BTCUSDT_5m.csv", 1000  # 🔒 FIXED WINDOW
    )

    runner = BacktestRunner()
    runner.run(candles_5m)

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "direction",
                "entry_time",
                "entry_price",
                "exit_time",
                "exit_price",
            ],
        )
        writer.writeheader()
        for trade in runner.trades:
            writer.writerow(trade)


if __name__ == "__main__":
    run("data/backtest_trades.csv")


