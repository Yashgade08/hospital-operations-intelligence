# Hospital Operations Intelligence Platform

Northstar Health is a portfolio-grade hospital operations console combining day-to-day capacity workflows with an ML-ready intelligence layer. It is designed around operational visibility: appointments, beds, inventory, revenue signals, risk, and recommended actions.

## Current implementation

- FastAPI REST API with OpenAPI at `/docs`
- SQLAlchemy models with SQLite local default and PostgreSQL configuration support
- JWT login, password hashing, and backend role checks
- Seeded de-identified demo data
- Appointment uniqueness constraint preventing a doctor from being double-booked
- Responsive React/Vite operations dashboard with API-backed KPIs, charts, alerts, and recommendations
- Reproducible synthetic data generation and two evaluated ML training scripts

## Stack

React, TypeScript, Vite, Axios, Recharts, Lucide; Python, FastAPI, SQLAlchemy, Pydantic, JWT; Pandas, NumPy, scikit-learn, Joblib; PostgreSQL-compatible persistence.

## Run locally

### Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH = (Get-Location).Path
uvicorn app.main:app --reload
```

The default local database is `backend/hospital.db`, which makes the demo runnable without a database server. For PostgreSQL, copy `.env.example` to `.env` and set `DATABASE_URL` to a `postgresql+psycopg://...` URL.

Demo login: `admin@northstar.health` / `Admin123!`

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Set `VITE_API_BASE_URL` when the API is not at `http://localhost:8000/api`.

## ML workflow

```powershell
python ml/data_generation/generate_data.py
python ml/training/train_no_show.py
python ml/training/train_bed_forecast.py
```

Training uses only pre-appointment no-show features and a chronological split for occupancy. Metrics are written to `ml/models/*_metrics.json` after execution; no metrics are claimed here before the scripts are run in the target environment.

## Architecture

React -> Axios REST API -> FastAPI -> SQLAlchemy service boundary -> PostgreSQL/SQLite. ML training runs offline, saves artifacts with Joblib, and prediction services can be connected to FastAPI without retraining per request.

## Security and disclaimer

Secrets belong in `.env`, which is ignored by Git. The platform is a software demonstration and operational decision-support system. Machine learning outputs are not medical diagnoses and should not replace professional medical judgment.

## Deployment

Build the frontend with `npm run build` and deploy `frontend/dist` to Vercel. Deploy the FastAPI service to Render or Railway with `uvicorn app.main:app --host 0.0.0.0 --port $PORT` and configure a managed PostgreSQL `DATABASE_URL`. No Docker or Docker Compose is required.

## Roadmap

Complete CRUD pages, admissions/beds transactions, billing and prescription workflows, notification preferences, model prediction endpoints, frontend route-level auth, and CI coverage around the API contract.
