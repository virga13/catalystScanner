import asyncio
import os
from datetime import datetime, timezone
from dateutil import parser as dtparser
from sqlalchemy.orm import Session
from ..config import settings
from ..db import SessionLocal, Base, engine
from ..models import NewsEvent, Signal
from ..services.classify import classify_event, playbook_for
from ..services.scoring import score_event
from ..utils.normalizer import NormalizedEvent, tickers_to_str
from .alpha_vantage import fetch_alpha_news
import json
import contextlib

Base.metadata.create_all(bind=engine)

WATCHLIST = [s.strip().upper() for s in settings.WATCHLIST.split(",") if s.strip()]

async def ingest_alpha_vantage(db: Session):
    if not settings.ALPHA_VANTAGE_API_KEY:
        return 0
    try:
        data = await fetch_alpha_news(settings.ALPHA_VANTAGE_API_KEY, WATCHLIST, limit=100)
        feed = data.get("feed", [])
        inserted = 0
        for item in feed:
            headline = item.get("title") or item.get("headline") or ""
            url = item.get("url")
            time_str = item.get("time_published")  # e.g. 20250120T134500
            published_at = dtparser.parse(time_str) if time_str else datetime.now(timezone.utc)
            tickers = [x.get("ticker") for x in item.get("ticker_sentiment", []) if x.get("ticker")]
            sentiment = None
            with contextlib.suppress(Exception):
                # crude aggregate sentiment from Alpha Vantage
                sentiment = sum(float(x.get("ticker_sentiment_score", 0)) for x in item.get("ticker_sentiment", [])) / max(1, len(tickers))

            event_type = classify_event(headline, item.get("summary"))
            ev = NewsEvent(
                provider_id=item.get("url"),
                source="AlphaVantage",
                headline=headline,
                body=item.get("summary") or None,
                tickers=tickers_to_str(tickers or WATCHLIST[:1]),
                url=url,
                event_type=event_type,
                sentiment=sentiment,
                published_at=published_at,
            )
            # avoid duplicates by provider_id+source+headline
            exists = db.query(NewsEvent).filter(NewsEvent.provider_id==ev.provider_id, NewsEvent.source==ev.source).first()
            if exists:
                continue
            db.add(ev)
            db.commit()
            db.refresh(ev)

            score = score_event(event_type, sentiment, published_at, rvol=None, premarket=False)
            sig = Signal(
                event_id=ev.id,
                event_type=event_type,
                headline=headline,
                tickers=ev.tickers,
                score=score,
                playbook_hint=playbook_for(event_type),
                url=ev.url,
                source=ev.source,
            )
            db.add(sig)
            db.commit()
            inserted += 1
        return inserted
    except Exception as e:
        print("Alpha Vantage ingestion error:", e)
        return 0

def load_demo_events():
    path = os.path.join(os.path.dirname(__file__), "../../sample_data/sample_events.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

async def ingest_demo(db: Session):
    # Replay sample events slowly for demo
    events = load_demo_events()
    inserted = 0
    for item in events:
        headline = item["headline"]
        event_type = classify_event(headline, item.get("body"))
        published_at = dtparser.parse(item["published_at"])
        ev = NewsEvent(
            provider_id=item.get("id"),
            source=item.get("source", "Demo"),
            headline=headline,
            body=item.get("body"),
            tickers=tickers_to_str(item.get("tickers", [])),
            url=item.get("url"),
            event_type=event_type,
            sentiment=item.get("sentiment"),
            published_at=published_at,
        )
        exists = db.query(NewsEvent).filter(NewsEvent.provider_id==ev.provider_id, NewsEvent.source==ev.source).first()
        if exists:
            continue
        db.add(ev)
        db.commit()
        db.refresh(ev)

        score = score_event(event_type, ev.sentiment, published_at, rvol=None, premarket=False)
        sig = Signal(
            event_id=ev.id,
            event_type=event_type,
            headline=headline,
            tickers=ev.tickers,
            score=score,
            playbook_hint=playbook_for(event_type),
            url=ev.url,
            source=ev.source,
        )
        db.add(sig)
        db.commit()
        inserted += 1
        await asyncio.sleep(0.8)  # simulate streaming
    return inserted

async def main_loop():
    interval = 10  # seconds
    print(f"Starting ingestion loop. Watchlist: {WATCHLIST}. Demo: {settings.DEMO_MODE}")
    while True:
        with SessionLocal() as db:
            total = 0
            if settings.ALPHA_VANTAGE_API_KEY:
                total += await ingest_alpha_vantage(db)
            if settings.DEMO_MODE:
                total += await ingest_demo(db)
            if total:
                print(f"Inserted {total} signals.")
        await asyncio.sleep(interval)

if __name__ == "__main__":
    asyncio.run(main_loop())
