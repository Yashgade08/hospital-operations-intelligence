from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=160)
    password: str = Field(min_length=8)
    role: str = "RECEPTIONIST"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ProfileUpdate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=160)


class PatientCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    date_of_birth: date
    gender: str
    phone: str


class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: date
    appointment_time: str = Field(pattern=r"^([0-1][0-9]|2[0-3]):[0-5][0-9]$")


class ModelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
