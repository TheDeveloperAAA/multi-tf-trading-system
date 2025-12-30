import csv
from typing import List, Dict, Optional

from strategy.base import Candle, Decision, PositionState
from strategy.multi_tf_strategy import MultiTFEMAStrategy
from utils.data_handler import MarketDataHandler


class BacktestRunner:
    """
    Deterministic backtesting engine.
    Replays candles sequentially and records completed trades.
    """

    def __init__(self) -> None:
        self.strategy = MultiTFEMAStrategy()
        self.data_handler = MarketDataHandler()
        self.trades: List[Dict] = []

        self._open_trade: Optional[Dict] = None

    def run(self, candles_5m: List[Candle]) -> None:
        """
        Run backtest over historical 5m candles.
        """
        self.strategy.reset()

        for candle in candles_5m:
            result = self.data_handler.on_new_5m_candle(candle)

            if result is None:
                continue

            candle_5m, candle_15m = result

            decision = self.strategy.on_candle_close(
                candle_5m=candle_5m,
                candle_15m=candle_15m,
                history_5m_closes=self.data_handler.get_5m_close_history(),
                history_15m_closes=self.data_handler.get_15m_close_history(),
            )

            self._handle_decision(decision, candle_5m)

    # ----------------------------------
    # Trade handling
    # ----------------------------------

    def _handle_decision(self, decision: Decision, candle: Candle) -> None:
        if decision == Decision.ENTER_LONG:
            self._open_trade = {
                "direction": "LONG",
                "entry_time": candle.timestamp,
                "entry_price": candle.close,
            }

        elif decision == Decision.ENTER_SHORT:
            self._open_trade = {
                "direction": "SHORT",
                "entry_time": candle.timestamp,
                "entry_price": candle.close,
            }

        elif decision == Decision.EXIT and self._open_trade:
            self._open_trade.update(
                {
                    "exit_time": candle.timestamp,
                    "exit_price": candle.close,
                }
            )
            self.trades.append(self._open_trade)
            self._open_trade = None

    # ----------------------------------
    # Output
    # ----------------------------------

    def export_trades(self, filepath: str) -> None:
        """
        Export completed trades to CSV.
        """
        if not self.trades:
            return

        fieldnames = list(self.trades[0].keys())

        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.trades)
