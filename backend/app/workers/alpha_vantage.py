import os
from datetime import datetime, timezone
import httpx

API_URL = "https://www.alphavantage.co/query"

async def fetch_alpha_news(api_key: str, tickers: list[str], limit: int = 50):
    # Alpha Vantage NEWS_SENTIMENT supports multi-ticker comma-separated
    params = {
        "function": "NEWS_SENTIMENT",
        "tickers": ",".join(tickers[:50]),
        "sort": "LATEST",
        "limit": str(limit),
        "apikey": api_key,
    }
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(API_URL, params=params)
        r.raise_for_status()
        return r.json()
