from typing import Optional
import os

from dotenv import load_dotenv
from binance.client import Client
from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET

from strategy.base import Candle

# Load environment variables from .env
load_dotenv()


class BinanceTestnetExchange:
    """
    Thin wrapper around Binance Spot Testnet.
    No strategy logic. No data alignment.
    """

    def __init__(self) -> None:
        api_key = os.getenv("BINANCE_API_KEY")
        api_secret = os.getenv("BINANCE_API_SECRET")

        if not api_key or not api_secret:
            raise RuntimeError("BINANCE_API_KEY or BINANCE_API_SECRET not set")

        self.client = Client(api_key, api_secret, testnet=True)
        self.client.API_URL = "https://testnet.binance.vision/api"

    # -----------------------------
    # Market Data
    # -----------------------------

    def get_latest_closed_5m_candle(self, symbol: str) -> Optional[Candle]:
        klines = self.client.get_klines(
            symbol=symbol,
            interval=Client.KLINE_INTERVAL_5MINUTE,
            limit=2,
        )

        if not klines:
            return None

        k = klines[-2]  # last CLOSED candle

        return Candle(
            timestamp=int(k[6]),  # close time (ms)
            open=float(k[1]),
            high=float(k[2]),
            low=float(k[3]),
            close=float(k[4]),
            volume=float(k[5]),
        )

    # -----------------------------
    # Execution
    # -----------------------------

    def place_market_order(self, symbol: str, side: str, quantity: float) -> dict:
        return self.client.create_order(
            symbol=symbol,
            side=SIDE_BUY if side == "BUY" else SIDE_SELL,
            type=ORDER_TYPE_MARKET,
            quantity=quantity,
        )



