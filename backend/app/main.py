from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from .config import settings
from .db import get_session, Base, engine
from . import models, schemas
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

app = FastAPI(title="Catalyst Scanner API", version="0.1.0")

# CORS
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB init
Base.metadata.create_all(bind=engine)

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/api/signals", response_model=List[schemas.SignalOut])
def list_signals(
    limit: int = Query(100, ge=1, le=1000),
    min_score: int = Query(0, ge=0, le=100),
    tickers: Optional[str] = Query(None),
    db: Session = Depends(get_session),
):
    stmt = select(models.Signal).where(models.Signal.score >= min_score).order_by(desc(models.Signal.created_at)).limit(limit)
    if tickers:
        syms = [s.strip().upper() for s in tickers.split(",") if s.strip()]
        # Postgres array contains check (fallback simple LIKE filter for MVP)
        # For MVP: simple OR headline contains ticker
        for sym in syms:
            stmt = stmt.where(models.Signal.tickers.ilike(f"%{sym}%"))
    results = db.execute(stmt).scalars().all()
    return [schemas.SignalOut.from_orm(r) for r in results]

@app.get("/api/events", response_model=List[schemas.EventOut])
def list_events(
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_session),
):
    stmt = select(models.NewsEvent).order_by(desc(models.NewsEvent.published_at)).limit(limit)
    results = db.execute(stmt).scalars().all()
    return [schemas.EventOut.from_orm(r) for r in results]
