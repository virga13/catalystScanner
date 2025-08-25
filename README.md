# Catalyst Scanner (MVP)

A minimal **News/Catalyst Scanner** to support **day trading** workflows:
- Ingests headlines from **Alpha Vantage News & Sentiment** (free) and provides a plug-in slot for SEC filings.
- **Normalizes**, **classifies**, **scores** events, stores them in **Postgres**.
- Serves a **REST API** via **FastAPI**.
- Includes a lightweight **React** UI showing a live **Catalyst Tape**.
- Designed for **manual trading first**; later, a bot can consume `/api/signals`.

> ⚠️ This is an MVP for research. Not investment advice. Use at your own risk.

---

## Quick Start (Docker)

1) Copy the example env and edit API keys / settings:
```bash
cp .env.example .env
# edit .env
```

2) Start everything:
```bash
docker compose up --build
```
- API at http://localhost:8000/docs
- Frontend at http://localhost:5173

3) To stop:
```bash
docker compose down -v
```

---

## Without Docker (dev)

- **Backend**:
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **Worker** (ingestion loop):
```bash
cd backend
source .venv/bin/activate
python app/workers/ingestion.py
```

- **Frontend**:
```bash
cd frontend
npm install
npm run dev
```

---

## Environment (.env)

```
# Common
WATCHLIST=AAPL,MSFT,NVDA,TSLA,META,AMD
ENVIRONMENT=dev

# Alpha Vantage (free key from https://www.alphavantage.co/support/#api-key)
ALPHA_VANTAGE_API_KEY=YOUR_KEY

# Postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=catalyst
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Backend
BACKEND_PORT=8000
CORS_ORIGINS=http://localhost:5173

# Demo mode (if no keys or network issues, worker replays sample events)
DEMO_MODE=true

# Optional: SEC user agent for polite crawling of EDGAR endpoints
SEC_USER_AGENT=YourName you@example.com
```

---

## Architecture

```
             +--------------------+
             |  Alpha Vantage API |
             +----------+---------+
                        |
                        v
+-----------+    +-------------+     +-----------+
|  Worker   +--> |  Classify   + --> |  Score    |
| ingestion |    |  (rules)    |     | (formula) |
+-----------+    +------+------+     +-----+-----+
                         |                  |
                         v                  v
                      PostgreSQL  <----  FastAPI
                         ^                  |
                         |                  v
                         |             React UI
```

### Signal Model
- **event_type**: `earnings/guidance`, `filing`, `ratings`, `mna`, `fda`, `other`
- **score**: 0–100
- **tickers**: list
- **headline**, **source**, **url**
- **rvod/abnormal_vol**, **premarket**, **minutes_since** (context)
- **playbook_hint**: textual cheat sheet

---

## API

- `GET /api/signals?limit=100&min_score=70&tickers=AAPL,TSLA`
- `GET /api/events?limit=100`
- `GET /healthz`

Open API docs: `/docs`

---

## Scoring (simple baseline)

```
base_by_type = {"earnings": 30, "filing": 25, "fda": 35, "mna": 40, "ratings": 20, "other": 10}

score = base_by_type[type]
      + 15 * provider_sentiment        # -1..+1 scaled
      + 12 * freshness_factor          # 1 / (1 + minutes_since/30)
      + 18 * abnormal_volume_factor    # rvol normalized 0..1
      + 10 * premarket_flag            # 0 or 1
      + 15 * proximity_to_levels       # 0..1 (placeholder in MVP)
```

---

## Playbooks

Attached hints per event type to guide manual action (VWAP reclaims, PM high break/retest, etc.).

---

## Extending

- Add **SEC filings** in `app/workers/sec.py` (8-K, S-1, 13D, Form 4).
- Add **FDA** in `app/workers/fda.py` (approvals, CRLs, PDUFA).
- Wire **Redis pub/sub** for push updates or keep frontend polling.
- Add broker bridge (paper trading only) once edge is proven.

---

## License

MIT (see LICENSE)
