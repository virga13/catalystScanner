from datetime import datetime, timezone
from math import tanh

BASE = {"earnings": 30, "filing": 25, "fda": 35, "mna": 40, "ratings": 20, "other": 10}

def freshness_factor(published_at: datetime) -> float:
    # minutes → 0..1 using smooth decay (30 min half-ish)
    now = datetime.now(timezone.utc)
    minutes = max(0.0, (now - published_at).total_seconds() / 60.0)
    return 1.0 / (1.0 + minutes / 30.0)

def normalize_sentiment(x: float | None) -> float:
    if x is None: 
        return 0.0
    # provider sentiment often in [-1, +1]
    return max(-1.0, min(1.0, x))

def score_event(event_type: str, provider_sentiment: float | None, published_at: datetime, rvol: float | None = None, premarket: bool = False) -> int:
    base = BASE.get(event_type, 10)
    sent = 15.0 * normalize_sentiment(provider_sentiment)
    fresh = 12.0 * freshness_factor(published_at)
    vol = 18.0 * (tanh((rvol or 0.0) / 2.0))  # rvol ~0..3 → 0..~1
    pm = 10.0 if premarket else 0.0
    levels = 8.0  # placeholder
    total = base + sent + fresh + vol + pm + levels
    return int(round(max(0.0, min(100.0, total))))
