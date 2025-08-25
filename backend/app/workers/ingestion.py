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
from .market_data_alpha import fetch_intraday_1min, calc_rvol, last_price, is_us_premarket


import json
import contextlib

Base.metadata.create_all(bind=engine)

WATCHLIST = [s.strip().upper() for s in settings.WATCHLIST.split(",") if s.strip()]

async def ingest_alpha_vantage():
    if not settings.ALPHA_VANTAGE_API_KEY:
        return 0
    from sqlalchemy.orm import Session
    with SessionLocal() as db:                      # <-- open per run
        try:
            data = await fetch_alpha_news(settings.ALPHA_VANTAGE_API_KEY, WATCHLIST, limit=100)
            feed = data.get("feed", [])
            inserted = 0
            for item in feed:
                # ... (unchanged parsing)
                exists = db.query(NewsEvent).filter(
                    NewsEvent.provider_id == ev.provider_id,
                    NewsEvent.source == ev.source
                ).first()
                if exists:
                    continue
                db.add(ev)
                db.commit()
                db.refresh(ev)

                primary = (tickers or WATCHLIST[:1])[0]
                ctx_rvol = None
                ctx_price = None
                ctx_premarket = is_us_premarket(published_at)
                if tickers and settings.ALPHA_VANTAGE_API_KEY:
                    try:
                        bars = await fetch_intraday_1min(settings.ALPHA_VANTAGE_API_KEY, tickers[0], points=20)
                        ctx_rvol = calc_rvol(bars)
                    except Exception as e:
                        print("RVOL fetch error:", e)

                score = score_event(event_type, sentiment, published_at, rvol=ctx_rvol, premarket=ctx_premarket)


                sig = Signal(
                    event_id=ev.id,
                    event_type=event_type,
                    headline=headline,
                    tickers=ev.tickers,
                    score=score,
                    playbook_hint=playbook_for(event_type),
                    url=ev.url,
                    source=ev.source,
                    price_at_publish=ctx_price,
                    rvol=ctx_rvol,
                    premarket=ctx_premarket,
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

async def ingest_demo():
    events = load_demo_events()
    inserted = 0
    for item in events:
        with SessionLocal() as db:                  # <-- open per event (safest with awaits)
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
            exists = db.query(NewsEvent).filter(
                NewsEvent.provider_id == ev.provider_id,
                NewsEvent.source == ev.source
            ).first()
            if not exists:
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

        await asyncio.sleep(0.8)  # simulate streaming without holding a session open
    return inserted

async def main_loop():
    print("Worker boot: entering main loop")
    interval = 10  # seconds
    print(f"Starting ingestion loop. Watchlist: {WATCHLIST}. Demo: {settings.DEMO_MODE}")
    while True:
        total = 0
        if settings.ALPHA_VANTAGE_API_KEY:
            total += await ingest_alpha_vantage()   # no db arg
        if settings.DEMO_MODE:
            total += await ingest_demo()           # no db arg
        if total:
            print(f"Inserted {total} signals.")
        await asyncio.sleep(interval)

if __name__ == "__main__":
    asyncio.run(main_loop())
