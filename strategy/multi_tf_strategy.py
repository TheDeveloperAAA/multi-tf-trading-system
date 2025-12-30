from typing import List
from strategy.base import Strategy, Candle, Decision, PositionState


def ema(values: List[float], period: int) -> float:
    """
    Deterministic EMA calculation.
    Assumes len(values) >= period.
    """
    k = 2 / (period + 1)
    ema_value = values[0]
    for v in values[1:]:
        ema_value = v * k + ema_value * (1 - k)
    return ema_value


class MultiTFEMAStrategy(Strategy):
    """
    Deterministic multi-timeframe EMA crossover strategy.
    """

    def on_candle_close(
        self,
        candle_5m: Candle,
        candle_15m: Candle,
        history_5m_closes: List[float],
        history_15m_closes: List[float],
    ) -> Decision:

        # Enforce strictly increasing closed candles
        if self._last_timestamp is not None:
            if candle_5m.timestamp <= self._last_timestamp:
                return Decision.HOLD

        self._last_timestamp = candle_5m.timestamp

        # Ensure enough data for EMAs
        if len(history_5m_closes) < 21 or len(history_15m_closes) < 200:
            return Decision.HOLD

        # --- Compute EMAs ---
        ema8_now = ema(history_5m_closes[-8:], 8)
        ema21_now = ema(history_5m_closes[-21:], 21)

        ema8_prev = ema(history_5m_closes[-9:-1], 8)
        ema21_prev = ema(history_5m_closes[-22:-1], 21)

        ema50_15m = ema(history_15m_closes[-50:], 50)
        ema200_15m = ema(history_15m_closes[-200:], 200)

        bullish = ema50_15m > ema200_15m
        bearish = ema50_15m < ema200_15m

        # --- Exit logic ---
        if self._position == PositionState.LONG:
            if ema8_prev >= ema21_prev and ema8_now < ema21_now:
                self._position = PositionState.FLAT
                return Decision.EXIT

        if self._position == PositionState.SHORT:
            if ema8_prev <= ema21_prev and ema8_now > ema21_now:
                self._position = PositionState.FLAT
                return Decision.EXIT

        # --- Entry logic ---
        if self._position == PositionState.FLAT:
            if bullish and ema8_prev <= ema21_prev and ema8_now > ema21_now:
                self._position = PositionState.LONG
                return Decision.ENTER_LONG

            if bearish and ema8_prev >= ema21_prev and ema8_now < ema21_now:
                self._position = PositionState.SHORT
                return Decision.ENTER_SHORT

        return Decision.HOLD
