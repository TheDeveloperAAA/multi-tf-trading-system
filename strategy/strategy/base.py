
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
    Timestamp represents candle CLOSE time (UTC).
    """
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


class Strategy(ABC):
    """
    Single source of truth for strategy decisions.
    Environment-agnostic and deterministic.
    """

    def __init__(self) -> None:
        self._position: PositionState = PositionState.FLAT
        self._last_timestamp: Optional[int] = None

    @property
    def position(self) -> PositionState:
        return self._position

    def reset(self) -> None:
        """Reset internal state (used by backtesting)."""
        self._position = PositionState.FLAT
        self._last_timestamp = None

    @abstractmethod
    def on_candle_close(
        self,
        candle_5m: Candle,
        candle_15m: Candle,
        history_5m_closes: list[float],
        history_15m_closes: list[float],
    ) -> Decision:
        """
        Called exactly once per new CLOSED 5m candle.
        Must return a deterministic decision.
        """
        raise NotImplementedError

