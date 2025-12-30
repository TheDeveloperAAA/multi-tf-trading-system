# strategy/base.py

from abc import ABC, abstractmethod
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional


class PositionState(Enum):
    FLAT = auto()
    LONG = auto()
    SHORT = auto()


class Decision(Enum):
    ENTER_LONG = auto()
    ENTER_SHORT = auto()
    EXIT = auto()
    HOLD = auto()


@dataclass(frozen=True)
class Candle:
    """
    Canonical candle format.
    timestamp MUST represent candle close time (UTC).
    """
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


class Strategy(ABC):
    """
    Single Source of Truth for decision-making.
    - No environment awareness
    - No order/fill knowledge
    - Closed-candle decisions only
    """

    def __init__(self) -> None:
        self._position: PositionState = PositionState.FLAT
        self._last_ts: Optional[int] = None

    @property
    def position(self) -> PositionState:
        return self._position

    def reset(self) -> None:
        """Reset strategy state (used by backtesting)."""
        self._position = PositionState.FLAT
        self._last_ts = None

    @abstractmethod
    def on_candle_close(
        self,
        candle_5m: Candle,
        candle_15m: Candle,
        history_5m_closes: list[float],
        history_15m_closes: list[float],
    ) -> Decision:
        """
        Called exactly once per NEW closed 5m candle.
        Must be deterministic for identical inputs.
        """
        raise NotImplementedError

