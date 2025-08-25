from dataclasses import dataclass
from datetime import datetime

@dataclass
class NormalizedEvent:
    provider_id: str | None
    source: str
    headline: str
    body: str | None
    tickers: list[str]
    url: str | None
    event_type: str | None
    sentiment: float | None
    published_at: datetime
    premarket: bool = False

def tickers_to_str(tickers: list[str]) -> str:
    return ",".join(sorted(set([t.upper() for t in tickers])))
