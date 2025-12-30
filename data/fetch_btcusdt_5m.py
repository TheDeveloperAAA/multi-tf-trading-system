import requests
import csv
import time

BASE_URL = "https://api.binance.com/api/v3/klines"
SYMBOL = "BTCUSDT"
INTERVAL = "5m"
LIMIT = 1000  # max per request

OUTPUT_PATH = "data/BTCUSDT_5m.csv"


def fetch_klines(start_time=None):
    params = {
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "limit": LIMIT,
    }
    if start_time is not None:
        params["startTime"] = start_time

    r = requests.get(BASE_URL, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def main():
    all_klines = []
    start_time = None

    # Fetch exactly 1000 candles (single batch, deterministic)
    klines = fetch_klines(start_time)
    all_klines.extend(klines)

    with open(OUTPUT_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "open", "high", "low", "close"])

        for k in all_klines:
            writer.writerow(
                [
                    int(k[6]) // 1000,  # close time (seconds)
                    float(k[1]),
                    float(k[2]),
                    float(k[3]),
                    float(k[4]),
                ]
            )

    print(f"Saved {len(all_klines)} BTCUSDT 5m candles to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()


