# Real-Time Multifamily Property Analytics Platform

A production-minded full-stack portfolio project for exploring multifamily housing data, public property records, and real loan-performance panel observations.

This project is designed to demonstrate full-stack engineering readiness for housing-finance software engineering roles: clean backend architecture, real-data ingestion, SQL-backed analytics, transparent provenance, and a recruiter-friendly React dashboard.

## What the MVP does

- Ingests real public HUD Multifamily Properties Assisted records.
- Ingests real Freddie Mac Multifamily Loan Performance Database CSV panel observations from local files.
- Stores ingestion provenance and run metadata.
- Exposes SQL-backed FastAPI analytics endpoints.
- Presents a clean React dashboard with charts, metrics, source labels, and ingestion run history.

## Data provenance and realism

This MVP is **real-data-only**.

- **HUD property data:** real public HUD Multifamily Properties Assisted data.
- **Freddie Mac data:** real Freddie Mac Multifamily Loan Performance Database loan-quarter observations from locally downloaded CSV files.
- **No synthetic loan data:** the app does not generate fake loan records, fake balances, fake LTV, fake DCR/DSCR, fake rates, or fake delinquency values.
- **No assumed join:** HUD property records and Freddie Mac MLPD observations are separate datasets. The dashboard does not imply that Freddie Mac observations are linked to HUD properties.
- **No proprietary data claim:** this project does not claim access to private Freddie Mac production systems or proprietary loan-level records beyond public MLPD files supplied locally by the developer.

## Architecture summary

```text
HUD ArcGIS API ─┐
                ├─ FastAPI ingestion/services ─ Supabase Postgres ─ SQL views/RPCs ─ FastAPI analytics ─ React dashboard
Freddie Mac CSV ┘
```

### Backend

- FastAPI
- Pydantic schemas
- Supabase Python client
- Async HUD ArcGIS client
- Local CSV Freddie Mac MLPD ingestion
- SQL-backed analytics via Supabase/Postgres views and RPC functions
- Environment-driven CORS for local frontend development

### Frontend

- React
- TypeScript
- Vite
- Recharts
- Plain CSS
- Fetch-based API client

### Database/Auth platform

- Supabase hosted PostgreSQL
- Supabase service role key used only on the backend for local/admin ingestion workflows
- SQL migration file for analytics views/RPCs

## Repository structure

```text
backend/
  app/
    api/routes/
    core/
    db/repositories/
    schemas/
    services/
    tests/
  sql/
    001_analytics_views_and_rpc_functions.sql
  .env.example
  pyproject.toml
  README.md

frontend/
  src/
    api/
    components/
    pages/
  .env.example
  package.json
  README.md

data/raw/freddie_mac_mlp/
  mlpd_y1994q1_y2021q4.csv       # local only, gitignored
  mlpd_y2022q1_y2025q3.csv       # local only, gitignored
```

## Data sources

### HUD Multifamily Properties Assisted

Primary endpoint:

```text
https://services.arcgis.com/VTyQ9soqVukalItT/arcgis/rest/services/Multifamily_Properties_Assisted/FeatureServer/0/query
```

The backend handles JSON requests, pagination, null-safe mapping, geocode quality preservation, raw payload preservation, and idempotent property upserts.

### Freddie Mac Multifamily Loan Performance Database

Expected local files:

```text
data/raw/freddie_mac_mlp/mlpd_y1994q1_y2021q4.csv
data/raw/freddie_mac_mlp/mlpd_y2022q1_y2025q3.csv
```

The CSV files are local-only and intentionally gitignored because they are large downloaded datasets.

## Supabase setup notes

Create/apply your database schema separately, then apply the analytics SQL:

```text
backend/sql/001_analytics_views_and_rpc_functions.sql
```

Apply it in the Supabase SQL Editor or a migration workflow. It creates:

- quarter sort helper
- read-performance indexes
- analytics views
- API-shaped RPC functions
- explicit `security invoker` functions
- `grant execute` statements for `authenticated`

## Backend setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
copy .env.example .env.local
```

For local development, keep real credentials in ignored local env files only. Prefer
`backend/.env.local`:

```env
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
FREDDIE_MAC_MLPD_DATA_DIR="../data/raw/freddie_mac_mlp"
CORS_ALLOWED_ORIGINS="http://localhost:5173,http://127.0.0.1:5173"
```

`backend/.env.example` is committed for placeholders only. Do not commit `.env`,
`.env.local`, Supabase service role keys, Gemini keys, JWTs, or downloaded datasets.

Start the backend:

```bash
cd backend
uvicorn app.main:app --reload
```

## Frontend setup

```bash
cd frontend
npm install
copy .env.example .env.local
npm run dev
```

Default frontend URL:

```text
http://localhost:5173
```

Default API base URL:

```env
VITE_API_BASE_URL="http://127.0.0.1:8000"
```

## Local Freddie Mac CSV placement

Place downloaded Freddie Mac MLPD CSVs here:

```text
data/raw/freddie_mac_mlp/mlpd_y1994q1_y2021q4.csv
data/raw/freddie_mac_mlp/mlpd_y2022q1_y2025q3.csv
```

The `data/raw/` folder is gitignored.

## Small ingestion tests

Start the backend first, then run:

```bash
curl -X POST http://127.0.0.1:8000/ingestion/freddie-mac/mlpd \
  -H "Content-Type: application/json" \
  -d "{\"limit\": 10, \"batch_size\": 5}"
```

Larger smoke test used during development:

```bash
curl -X POST http://127.0.0.1:8000/ingestion/freddie-mac/mlpd \
  -H "Content-Type: application/json" \
  -d "{\"limit\": 1000, \"batch_size\": 500}"
```

## Available API endpoints

```http
GET  /health
POST /ingestion/hud/properties
POST /ingestion/freddie-mac/mlpd
GET  /analytics/hud/summary
GET  /analytics/freddie-mac/summary
GET  /analytics/freddie-mac/status-codes
GET  /analytics/freddie-mac/latest-quarter
GET  /analytics/ingestion-runs/recent
```

## Developer workflow

See [`DEVELOPING.md`](DEVELOPING.md) for a concise command reference covering
backend startup, frontend startup, validation, and Supabase SQL application.

### Backend validation

```bash
cd backend
python -m pytest app/tests -q
python -m ruff check app
python -m compileall app -q
```

### Frontend validation

```bash
cd frontend
npm run build
```

### Apply SQL files in Supabase

1. Open Supabase SQL Editor.
2. Paste contents of `backend/sql/001_analytics_views_and_rpc_functions.sql`.
3. Run the SQL.
4. If RPC endpoints return a schema-cache error, wait briefly and retry.

## Dashboard screenshots

Screenshots will be added after the first deployed or locally captured dashboard demo.

```text
docs/screenshots/dashboard-overview.png       # placeholder
docs/screenshots/freddie-mac-analytics.png   # placeholder
docs/screenshots/hud-analytics.png           # placeholder
```

## Future work

- Supabase Auth integration and route protection.
- Gemini-powered AI risk reports with compact, validated structured output.
- AI report provenance and prompt/version tracking.
- More detailed filtering and drill-down pages.
- Deployment workflow and hosted demo.
- Optional chart code-splitting if bundle size becomes a priority.
