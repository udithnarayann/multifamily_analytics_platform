# Real-Time Multifamily Property Analytics API

FastAPI backend for the Real-Time Multifamily Property Analytics Platform.

## Data provenance

- Property records are ingested from the public HUD Multifamily Properties - Assisted ArcGIS FeatureServer.
- Freddie Mac loan-quarter observations are ingested from real local Freddie Mac Multifamily Loan Performance Database CSV files supplied by the developer.
- This project uses a real-data-only design for the MVP and does not generate estimated loan records.
- Future AI analysis must distinguish HUD property data, Freddie Mac observation data, deterministic backend metrics, and AI-generated commentary.

## First implemented slice

This backend foundation includes:

- FastAPI app scaffold.
- Typed environment configuration.
- Health route.
- HUD ArcGIS async client with `resultOffset` / `resultRecordCount` pagination.
- Pure HUD property mapping logic.
- Supabase repositories for `properties` and `ingestion_runs`.
- Limited HUD ingestion route for development/testing.
- Local Freddie Mac MLPD CSV ingestion route for development/testing.

## Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
copy .env.example .env.local
```

Fill in `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` in `.env.local`. The backend
loads `.env.local` first and `.env` second for local compatibility. Both files are
gitignored; only `.env.example` should be committed.

For Gemini AI risk reports, optionally set:

```env
# Optional: paste your Gemini API key locally only.
GEMINI_API_KEY=""
GEMINI_MODEL_PRIMARY=gemini-3.1-flash-lite
GEMINI_MODEL_FALLBACK=gemini-3.5-flash
```

The backend starts without `GEMINI_API_KEY`; only risk-report generation fails with
a configuration error until the key is set.

Place the Freddie Mac MLPD CSV files at:

```text
data/raw/freddie_mac_mlp/mlpd_y1994q1_y2021q4.csv
data/raw/freddie_mac_mlp/mlpd_y2022q1_y2025q3.csv
```

From the `backend/` directory, the default relative data path is:

```env
FREDDIE_MAC_MLPD_DATA_DIR="../data/raw/freddie_mac_mlp"
```

## Run locally

```bash
uvicorn app.main:app --reload
```

## Routes

```http
GET /health
POST /ingestion/hud/properties
POST /ingestion/freddie-mac/mlpd
GET /freddie-mac/observations/sample
POST /risk-reports/freddie-mac/{observation_id}
GET /risk-reports/freddie-mac/{observation_id}
GET /analytics/hud/summary
GET /analytics/freddie-mac/summary
GET /analytics/freddie-mac/status-codes
GET /analytics/freddie-mac/latest-quarter
GET /analytics/ingestion-runs/recent
```

Example limited ingestion request:

```json
{
  "limit": 100,
  "page_size": 50
}
```

Example limited Freddie Mac MLPD ingestion request:

```json
{
  "limit": 1000,
  "batch_size": 500
}
```

## Security note

The Supabase service role key is backend-only. Never expose it to the frontend or commit it to source control.

Gemini risk report prompts are constrained to whitelisted Freddie Mac MLPD observation
fields only. They do not send Supabase credentials, JWTs, `.env` contents, raw row
payloads, synthetic data, or any assumed HUD/Freddie Mac joins.
