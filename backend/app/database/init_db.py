from datetime import date, timedelta

from sqlalchemy import select

from app.core.security import hash_password
from app.database.database import Base, SessionLocal, engine
from app.models.models import Appointment, Department, Doctor, Medicine, Notification, Patient, User, Ward


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.scalar(select(User).limit(1)):
            return
        cardiology = Department(name="Cardiology", color="#d67c5f")
        emergency = Department(name="Emergency", color="#2f7d76")
        db.add_all([cardiology, emergency])
        db.flush()
        db.add(User(email="admin@northstar.health", full_name="Avery Morgan", role="ADMIN", password_hash=hash_password("Admin123!")))
        doctors = [Doctor(name="Dr. Maya Chen", specialty="Cardiology", department_id=cardiology.id), Doctor(name="Dr. Elias Reed", specialty="Emergency Medicine", department_id=emergency.id)]
        patients = [Patient(patient_code="PT-10482", name="Nadia Williams", date_of_birth=date(1988, 4, 12), gender="Female", phone="+1 555 0182"), Patient(patient_code="PT-10483", name="Marcus Bell", date_of_birth=date(1974, 9, 3), gender="Male", phone="+1 555 0194"), Patient(patient_code="PT-10484", name="Sofia Patel", date_of_birth=date(1996, 1, 28), gender="Female", phone="+1 555 0136")]
        db.add_all(doctors + patients)
        db.flush()
        today = date.today()
        db.add_all([Appointment(patient_id=patients[0].id, doctor_id=doctors[0].id, appointment_date=today, appointment_time="09:30", status="CONFIRMED"), Appointment(patient_id=patients[1].id, doctor_id=doctors[1].id, appointment_date=today, appointment_time="10:15", status="SCHEDULED"), Appointment(patient_id=patients[2].id, doctor_id=doctors[0].id, appointment_date=today + timedelta(days=1), appointment_time="14:00", status="SCHEDULED")])
        db.add_all([Ward(name="General Ward", total_beds=32, occupied_beds=25), Ward(name="Critical Care", total_beds=12, occupied_beds=10), Ward(name="Pediatrics", total_beds=20, occupied_beds=11)])
        db.add_all([Medicine(name="Amoxicillin 500mg", category="Antibiotic", quantity=18, reorder_level=25, expiry_date=today + timedelta(days=190)), Medicine(name="Atorvastatin 20mg", category="Cardiovascular", quantity=142, reorder_level=40, expiry_date=today + timedelta(days=22)), Medicine(name="Insulin Glargine", category="Diabetes", quantity=9, reorder_level=15, expiry_date=today + timedelta(days=75))])
        db.add_all([Notification(title="Capacity watch", description="Critical Care is at 83% occupancy. Review tomorrow's admissions.", severity="HIGH"), Notification(title="Inventory attention", description="3 medicines are below their reorder level.", severity="MEDIUM"), Notification(title="No-show risk", description="2 appointments have elevated predicted no-show probability.", severity="MEDIUM")])
        db.commit()


if __name__ == "__main__":
    seed()
