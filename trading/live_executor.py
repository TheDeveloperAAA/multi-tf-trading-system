import csv
import time
from typing import Optional

from strategy.multi_tf_strategy import MultiTFEMAStrategy
from strategy.base import Decision, Candle
from utils.data_handler import MarketDataHandler
from trading.exchange import BinanceTestnetExchange


class LiveExecutor:
    """
    Live execution loop using Binance Testnet.
    Supports dry-run mode for parity validation (no real orders).
    """

    def __init__(
        self,
        exchange: BinanceTestnetExchange,
        symbol: str,
        quantity: float,
        csv_path: str = "data/live_trades.csv",
        poll_interval_sec: int = 5,
        dry_run: bool = True,
    ) -> None:
        self.exchange = exchange
        self.symbol = symbol
        self.quantity = quantity
        self.csv_path = csv_path
        self.poll_interval_sec = poll_interval_sec
        self.dry_run = dry_run

        self.strategy = MultiTFEMAStrategy()
        self.data_handler = MarketDataHandler()

        self._open_trade: Optional[dict] = None
        self._last_candle_ts: Optional[int] = None

        self._init_csv()

    # -----------------------------
    # CSV handling
    # -----------------------------

    def _init_csv(self) -> None:
        with open(self.csv_path, "w", newline="") as f:
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

    def _append_trade(self, trade: dict) -> None:
        with open(self.csv_path, "a", newline="") as f:
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
            writer.writerow(trade)

    # -----------------------------
    # Main loop
    # -----------------------------

    def run(self) -> None:
        """
        Blocking loop. Polls for CLOSED 5m candles only.
        """
        while True:
            candle_5m = self.exchange.get_latest_closed_5m_candle(self.symbol)

            if candle_5m is None:
                time.sleep(self.poll_interval_sec)
                continue

            # Enforce strictly increasing candle timestamps
            if (
                self._last_candle_ts is not None
                and candle_5m.timestamp <= self._last_candle_ts
            ):
                time.sleep(self.poll_interval_sec)
                continue

            self._last_candle_ts = candle_5m.timestamp

            result = self.data_handler.on_new_5m_candle(candle_5m)
            if result is None:
                time.sleep(self.poll_interval_sec)
                continue

            candle_5m_aligned, candle_15m = result

            decision = self.strategy.on_candle_close(
                candle_5m=candle_5m_aligned,
                candle_15m=candle_15m,
                history_5m_closes=self.data_handler.get_5m_close_history(),
                history_15m_closes=self.data_handler.get_15m_close_history(),
            )

            self._handle_decision(decision, candle_5m_aligned)

            time.sleep(self.poll_interval_sec)

    # -----------------------------
    # Decision handling
    # -----------------------------

    def _handle_decision(self, decision: Decision, candle: Candle) -> None:
        if decision == Decision.ENTER_LONG:
            if not self.dry_run:
                self.exchange.place_market_order(
                    self.symbol, "BUY", self.quantity
                )
            self._open_trade = {
                "direction": "LONG",
                "entry_time": candle.timestamp,
                "entry_price": candle.close,
            }

        elif decision == Decision.ENTER_SHORT:
            if not self.dry_run:
                self.exchange.place_market_order(
                    self.symbol, "SELL", self.quantity
                )
            self._open_trade = {
                "direction": "SHORT",
                "entry_time": candle.timestamp,
                "entry_price": candle.close,
            }

        elif decision == Decision.EXIT and self._open_trade:
            side = "SELL" if self._open_trade["direction"] == "LONG" else "BUY"
            if not self.dry_run:
                self.exchange.place_market_order(
                    self.symbol, side, self.quantity
                )

            self._open_trade.update(
                {
                    "exit_time": candle.timestamp,
                    "exit_price": candle.close,
                }
            )
            self._append_trade(self._open_trade)
            self._open_trade = None


