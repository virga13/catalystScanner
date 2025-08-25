from pydantic import BaseModel, ConfigDict
from datetime import datetime

class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    provider_id: str | None
    source: str
    headline: str
    body: str | None
    tickers: str
    url: str | None
    event_type: str
    sentiment: float | None
    published_at: datetime
    created_at: datetime

class SignalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    event_id: int | None
    event_type: str
    headline: str
    tickers: str
    score: int
    playbook_hint: str | None
    url: str | None
    source: str
    created_at: datetime
