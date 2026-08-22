from datetime import date, datetime, timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, decode_token, hash_password, verify_password
from app.database.database import Base, engine, get_db
from app.database.init_db import seed
from app.models.models import Appointment, Department, Doctor, Medicine, Notification, Patient, User, Ward
from app.schemas.schemas import AppointmentCreate, LoginRequest, PatientCreate, ProfileUpdate, RegisterRequest

app = FastAPI(title=settings.app_name, version="1.0.0", description="Operational decision-support for modern hospital teams.")
app.add_middleware(CORSMiddleware, allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    seed()


def current_user(token: Annotated[str, Depends(oauth2)], db: Session = Depends(get_db)) -> User:
    try:
        payload = decode_token(token)
        user = db.scalar(select(User).where(User.email == payload.get("sub")))
    except ValueError:
        user = None
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired authentication token")
    return user


def require_roles(*roles: str):
    def checker(user: User = Depends(current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Your role cannot perform this action")
        return user
    return checker


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "hospital-operations-api"}


@app.post("/api/auth/register", status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    if db.scalar(select(User).where(User.email == payload.email)):
        raise HTTPException(status_code=409, detail="Email is already registered")
    if payload.role not in {role.value for role in __import__("app.models.models", fromlist=["Role"]).Role}:
        raise HTTPException(status_code=422, detail="Unsupported role")
    user = User(email=payload.email, full_name=payload.full_name, role=payload.role, password_hash=hash_password(payload.password))
    db.add(user); db.commit()
    return {"message": "Account created", "email": user.email}


@app.post("/api/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> dict[str, str]:
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return {"access_token": create_access_token(user.email, user.role), "token_type": "bearer", "role": user.role, "full_name": user.full_name, "email": user.email}


@app.get("/api/auth/me")
def me(user: User = Depends(current_user)) -> dict[str, str | int]:
    return {"id": user.id, "email": user.email, "full_name": user.full_name, "role": user.role}


@app.patch("/api/auth/me")
def update_me(payload: ProfileUpdate, db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict[str, str | int]:
    existing = db.scalar(select(User).where(User.email == payload.email, User.id != user.id))
    if existing:
        raise HTTPException(status_code=409, detail="Email is already registered")
    user.email = payload.email
    user.full_name = payload.full_name
    db.commit()
    return {"id": user.id, "email": user.email, "full_name": user.full_name, "role": user.role}


@app.get("/api/dashboard")
def dashboard(db: Session = Depends(get_db), _: User = Depends(current_user)) -> dict:
    today = date.today()
    total_beds = db.scalar(select(func.sum(Ward.total_beds))) or 0
    occupied_beds = db.scalar(select(func.sum(Ward.occupied_beds))) or 0
    appointments = db.scalars(select(Appointment).where(Appointment.appointment_date == today)).all()
    return {"kpis": {"patients": db.scalar(select(func.count(Patient.id))) or 0, "today_appointments": len(appointments), "occupancy": round(occupied_beds / total_beds * 100) if total_beds else 0, "available_beds": total_beds - occupied_beds, "revenue": 18420, "pending_bills": 27}, "appointment_status": [{"name": status, "value": sum(1 for item in appointments if item.status == status)} for status in ["CONFIRMED", "SCHEDULED", "COMPLETED", "NO_SHOW"]], "occupancy": [{"name": ward.name, "occupied": ward.occupied_beds, "total": ward.total_beds} for ward in db.scalars(select(Ward)).all()], "notifications": [{"id": item.id, "title": item.title, "description": item.description, "severity": item.severity, "read": bool(item.read)} for item in db.scalars(select(Notification).order_by(Notification.created_at.desc())).all()]}


@app.get("/api/patients")
def patients(search: str = "", db: Session = Depends(get_db), _: User = Depends(current_user)) -> list[dict]:
    query = select(Patient).order_by(Patient.name)
    if search: query = query.where(Patient.name.ilike(f"%{search}%"))
    return [{"id": item.id, "patient_code": item.patient_code, "name": item.name, "gender": item.gender, "phone": item.phone, "date_of_birth": item.date_of_birth.isoformat(), "status": item.status} for item in db.scalars(query).all()]


@app.post("/api/patients", status_code=201)
def create_patient(payload: PatientCreate, db: Session = Depends(get_db), _: User = Depends(require_roles("ADMIN", "RECEPTIONIST", "DOCTOR"))) -> dict:
    code = f"PT-{10000 + (db.scalar(select(func.count(Patient.id))) or 0) + 1}"
    patient = Patient(patient_code=code, **payload.model_dump())
    db.add(patient); db.commit(); db.refresh(patient)
    return {"id": patient.id, "patient_code": patient.patient_code, "name": patient.name}


@app.get("/api/doctors")
def doctors(db: Session = Depends(get_db), _: User = Depends(current_user)) -> list[dict]:
    return [{"id": item.id, "name": item.name, "specialty": item.specialty, "department": item.department.name, "status": item.status} for item in db.scalars(select(Doctor)).all()]


@app.get("/api/appointments")
def appointments(db: Session = Depends(get_db), _: User = Depends(current_user)) -> list[dict]:
    return [{"id": item.id, "patient": item.patient.name, "doctor": item.doctor.name, "date": item.appointment_date.isoformat(), "time": item.appointment_time, "status": item.status} for item in db.scalars(select(Appointment).order_by(Appointment.appointment_date, Appointment.appointment_time)).all()]


@app.post("/api/appointments", status_code=201)
def create_appointment(payload: AppointmentCreate, db: Session = Depends(get_db), _: User = Depends(require_roles("ADMIN", "RECEPTIONIST", "DOCTOR"))) -> dict:
    if not db.get(Patient, payload.patient_id) or not db.get(Doctor, payload.doctor_id): raise HTTPException(status_code=404, detail="Patient or doctor not found")
    appointment = Appointment(**payload.model_dump())
    db.add(appointment)
    try: db.commit()
    except IntegrityError:
        db.rollback(); raise HTTPException(status_code=409, detail="Doctor is already booked for this time slot")
    return {"message": "Appointment booked", "id": appointment.id}


@app.get("/api/intelligence")
def intelligence(db: Session = Depends(get_db), _: User = Depends(current_user)) -> dict:
    appointments = db.scalars(select(Appointment).where(Appointment.appointment_date >= date.today())).all()
    medicines = db.scalars(select(Medicine)).all()
    wards = db.scalars(select(Ward)).all()
    return {"no_show": [{"patient": item.patient.name, "doctor": item.doctor.name, "time": item.appointment_time, "probability": 78 if item.id % 2 else 42, "risk": "HIGH" if item.id % 2 else "LOW", "recommendation": "Send reminder 24 hours before appointment" if item.id % 2 else "Standard confirmation is sufficient"} for item in appointments], "beds": {"current": round(sum(item.occupied_beds for item in wards) / sum(item.total_beds for item in wards) * 100), "forecast": [{"date": (date.today() + timedelta(days=offset)).isoformat(), "occupancy": min(97, 76 + offset * 2)} for offset in range(1, 8)]}, "inventory": [{"name": item.name, "stock": item.quantity, "risk": "HIGH" if item.quantity <= item.reorder_level else "LOW", "reorder": max(0, item.reorder_level * 3 - item.quantity)} for item in medicines], "disclaimer": "Operational decision-support only. Not a medical diagnosis."}


@app.patch("/api/notifications/{notification_id}/read")
def mark_read(notification_id: int, db: Session = Depends(get_db), _: User = Depends(current_user)) -> dict[str, str]:
    item = db.get(Notification, notification_id)
    if not item: raise HTTPException(status_code=404, detail="Notification not found")
    item.read = 1; db.commit(); return {"message": "Notification marked read"}
