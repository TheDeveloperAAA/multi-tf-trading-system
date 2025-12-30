from collections import deque
from typing import Optional, Tuple, List

from strategy.base import Candle


class MarketDataHandler:
    """
    Maintains aligned 5m and 15m candle data.
    Ensures:
    - Closed-candle only semantics
    - Proper 5m / 15m alignment
    - No lookahead bias
    """

    def __init__(
        self,
        max_5m_history: int = 500,
        max_15m_history: int = 500,
    ) -> None:
        self._candles_5m: deque[Candle] = deque(maxlen=max_5m_history)
        self._candles_15m: deque[Candle] = deque(maxlen=max_15m_history)

        self._buffer_15m_builder: List[Candle] = []

    # -------------------------------
    # Public API
    # -------------------------------

    def on_new_5m_candle(self, candle_5m: Candle) -> Optional[Tuple[Candle, Candle]]:
        """
        Called whenever a NEW closed 5m candle arrives.

        Returns:
            (latest_5m_candle, latest_15m_candle) if strategy can be evaluated
            None if not enough data yet
        """

        # Enforce strictly increasing timestamps
        if self._candles_5m:
            if candle_5m.timestamp <= self._candles_5m[-1].timestamp:
                return None

        self._candles_5m.append(candle_5m)

        # Build 15m candles from 3 consecutive 5m candles
        self._buffer_15m_builder.append(candle_5m)

        if len(self._buffer_15m_builder) == 3:
            candle_15m = self._aggregate_15m(self._buffer_15m_builder)
            self._candles_15m.append(candle_15m)
            self._buffer_15m_builder = []

        # Strategy can run only if at least one 15m candle exists
        if not self._candles_15m:
            return None

        return candle_5m, self._candles_15m[-1]

    # -------------------------------
    # Data accessors
    # -------------------------------

    def get_5m_close_history(self) -> List[float]:
        return [c.close for c in self._candles_5m]

    def get_15m_close_history(self) -> List[float]:
        return [c.close for c in self._candles_15m]

    # -------------------------------
    # Internal helpers
    # -------------------------------

    @staticmethod
    def _aggregate_15m(candles_5m: List[Candle]) -> Candle:
        """
        Aggregates exactly 3 consecutive 5m candles into a 15m candle.
        Timestamp is the CLOSE time of the last 5m candle.
        """

        first = candles_5m[0]
        last = candles_5m[-1]

        return Candle(
            timestamp=last.timestamp,
            open=first.open,
            high=max(c.high for c in candles_5m),
            low=min(c.low for c in candles_5m),
            close=last.close,
            volume=sum(c.volume for c in candles_5m),
        )
