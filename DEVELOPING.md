# Developer Workflow

Concise local workflow reference for the Real-Time Multifamily Property Analytics Platform.

## Environment files

- Commit only `.env.example` files.
- Keep real local secrets in ignored files such as `backend/.env.local` and `frontend/.env.local`.
- Never commit Supabase service role keys, anon keys, Gemini keys, JWTs, or downloaded data files.

## Start the backend

```bash
cd backend
uvicorn app.main:app --reload
```

The backend loads `.env` and then `.env.local`, so `.env.local` takes precedence
for machine-specific secrets.

## Start the frontend

```bash
cd frontend
npm run dev
```

The Vite dev server defaults to `http://localhost:5173`.

## Run backend tests, lint, and compile checks

```bash
cd backend
python -m pytest app/tests -q
python -m ruff check app
python -m compileall app -q
```

## Run frontend build validation

```bash
cd frontend
npm run build
```

## Apply SQL files in Supabase

1. Open the Supabase dashboard for your project.
2. Go to SQL Editor.
3. Open `backend/sql/001_analytics_views_and_rpc_functions.sql` locally.
4. Paste the SQL into the editor.
5. Run the script.
6. If a newly created RPC function is not immediately visible to the API, wait briefly for the schema cache to refresh and retry.

## Freddie Mac local CSV placement

Place downloaded Freddie Mac Multifamily Loan Performance Database CSVs here:

```text
data/raw/freddie_mac_mlp/mlpd_y1994q1_y2021q4.csv
data/raw/freddie_mac_mlp/mlpd_y2022q1_y2025q3.csv
```

`data/raw/` is gitignored and should remain local-only.