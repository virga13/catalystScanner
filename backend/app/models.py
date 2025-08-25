from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from sqlalchemy.sql import func
from .db import Base
from sqlalchemy import Boolean


class NewsEvent(Base):
    __tablename__ = "news_events"
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(String(128), index=True, nullable=True)
    source = Column(String(64), index=True)
    headline = Column(Text, nullable=False)
    body = Column(Text, nullable=True)
    tickers = Column(String(512), index=True)  # comma-separated
    url = Column(String(1024), nullable=True)
    event_type = Column(String(32), index=True)  # earnings, filing, fda, mna, ratings, other
    sentiment = Column(Float, nullable=True)     # -1..+1 if provided
    published_at = Column(DateTime(timezone=True), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Signal(Base):
    __tablename__ = "signals"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, index=True, nullable=True)
    event_type = Column(String(32), index=True)
    headline = Column(Text, nullable=False)
    tickers = Column(String(512), index=True)
    score = Column(Integer, index=True)
    playbook_hint = Column(String(256), nullable=True)
    url = Column(String(1024), nullable=True)
    source = Column(String(64), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    price_at_publish = Column(Float, nullable=True)
    rvol = Column(Float, nullable=True)
    premarket = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
