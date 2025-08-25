from datetime import datetime, timezone
from math import tanh

BASE = {"earnings": 30, "filing": 25, "fda": 35, "mna": 40, "ratings": 20, "other": 5}

def freshness_factor(published_at: datetime) -> float:
    now = datetime.now(timezone.utc)
    minutes = max(0.0, (now - published_at).total_seconds() / 60.0)
    return 1.0 / (1.0 + minutes / 30.0)

def normalize_sentiment(x: float | None) -> float:
    if x is None:
        return 0.0
    return max(-1.0, min(1.0, x))

def score_event(event_type: str, provider_sentiment: float | None, published_at: datetime, rvol: float | None = None, premarket: bool = False) -> int:
    base = BASE.get(event_type, 5)
    sent = 12.0 * normalize_sentiment(provider_sentiment)
    fresh = 12.0 * freshness_factor(published_at)
    volboost = 22.0 * (tanh(((rvol or 0.0) - 1.0)))  # >1.0 RVOL starts to matter
    pm = 8.0 if premarket else 0.0
    levels = 8.0  # placeholder

    total = base + sent + fresh + volboost + pm + levels

    # De-prioritize "other" unless RVOL is strong
    if event_type == "other" and (rvol or 0.0) < 1.5:
        total = min(total, 40.0)

    return int(round(max(0.0, min(100.0, total))))
