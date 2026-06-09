# Multifamily Analytics Frontend

React + TypeScript + Vite dashboard for the Real-Time Multifamily Property Analytics Platform.

## Data provenance

The MVP is real-data-only:

- Real HUD Multifamily Properties Assisted public property data.
- Real Freddie Mac Multifamily Loan Performance Database loan-quarter observations.
- No synthetic loan data.
- No assumed join between HUD properties and Freddie Mac records.

## Setup

```bash
cd frontend
npm install
copy .env.example .env.local
npm run dev
```

Default API URL:

```env
VITE_API_BASE_URL="http://127.0.0.1:8000"
```

Make sure the backend is running at the same URL.

## Build

```bash
npm run build
```
