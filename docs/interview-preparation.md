# Interview preparation

**Project:** A hospital operations console exposes operational workflows through FastAPI and a React dashboard, with SQLAlchemy persistence and offline ML artifacts for no-show and capacity signals.

**Double booking:** The API validates related records, while a database unique constraint on doctor/date/time provides atomic protection under concurrent requests.

**No-show model:** Pre-appointment behavior and scheduling features are compared across balanced Logistic Regression and Random Forest. Precision, recall, F1, and ROC-AUC matter more than accuracy alone because missed appointments are the minority class.

**Forecasting:** Occupancy is time ordered; the baseline validates on the future rather than randomly shuffling history. A production version can add exogenous admissions, discharges, holidays, and model monitoring.

**Scaling and privacy:** Add indexes and cursor pagination, read replicas, background jobs, structured audit logs, least-privilege roles, encryption, retention controls, and monitoring. Outputs are operational decision support only, never medical diagnoses.
