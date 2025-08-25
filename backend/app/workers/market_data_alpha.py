import httpx
from datetime import datetime, timezone

BASE = "https://www.alphavantage.co/query"

async def fetch_intraday_1min(api_key: str, symbol: str, points: int = 20):
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": "1min",
        "outputsize": "compact",
        "apikey": api_key,
    }
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(BASE, params=params)
        r.raise_for_status()
        data = r.json().get("Time Series (1min)", {})
        items = sorted(data.items(), key=lambda x: x[0])[-points:]
        bars = []
        for ts, row in items:
            vol = float(row.get("5. volume", "0"))
            close = float(row.get("4. close", "0"))
            t = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            bars.append({"time": t, "volume": vol, "close": close})
        return bars

def calc_rvol(bars: list[dict]) -> float | None:
    if not bars or len(bars) < 2:
        return None
    last = bars[-1]["volume"]
    prev = [b["volume"] for b in bars[:-1]][-10:] or [b["volume"] for b in bars[:-1]]
    avg = sum(prev) / max(1, len(prev))
    return (last / avg) if avg > 0 else None

def last_price(bars: list[dict]) -> float | None:
    return bars[-1]["close"] if bars else None

def is_us_premarket(ts: datetime) -> bool:
    # Mark "premarket" if before 13:30 UTC on a weekday
    return ts.weekday() < 5 and (ts.hour < 13 or (ts.hour == 13 and ts.minute < 30))
