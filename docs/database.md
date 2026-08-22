# Database design

The current schema includes users, departments, doctors, patients, appointments, wards, medicines, and notifications. Foreign keys connect doctors to departments and appointments to patients/doctors. The appointment table has a unique `(doctor_id, appointment_date, appointment_time)` constraint, making double-booking prevention atomic at the database boundary. Production extensions add beds, admissions, medical records, prescriptions, billing, payments, suppliers, and prediction audit records.
