# Architecture

The frontend is a React TypeScript single-page application. Axios centralizes the API base URL and bearer token. FastAPI owns validation, authentication, authorization, aggregation, and OpenAPI documentation. SQLAlchemy isolates persistence so SQLite is convenient for demos while PostgreSQL is the deployment target.

ML training is offline: synthetic data generation -> preprocessing/training -> saved Joblib artifact and metrics -> prediction service -> FastAPI -> intelligence dashboard. Models must never be retrained for each request.
