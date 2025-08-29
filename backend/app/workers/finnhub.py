import httpx, asyncio
from datetime import datetime, timezone, timedelta

API = "https://finnhub.io/api/v1"

async def fetch_company_news(api_key: str, symbol: str, days: int = 1):
    end = datetime.now(timezone.utc).date()
    start = end - timedelta(days=days)
    params = {"symbol": symbol, "from": str(start), "to": str(end), "token": api_key}
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(f"{API}/company-news", params=params)
        r.raise_for_status()
        return r.json()
