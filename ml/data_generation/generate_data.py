"""Generate synthetic, de-identified operational data for local model training."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).parents[2] / "data"
RNG = np.random.default_rng(42)

def generate() -> None:
    ROOT.mkdir(exist_ok=True)
    n = 1200
    booked = pd.date_range("2025-01-01", periods=n, freq="D")
    appointments = pd.DataFrame({"appointment_id": range(1, n + 1), "patient_id": RNG.integers(1, 220, n), "age": RNG.integers(18, 86, n), "gender": RNG.choice(["Female", "Male"], n), "previous_appointments": RNG.integers(0, 14, n), "previous_no_shows": RNG.integers(0, 4, n), "previous_cancellations": RNG.integers(0, 3, n), "days_between_booking_and_appointment": RNG.integers(0, 45, n), "appointment_hour": RNG.choice([8, 9, 10, 11, 13, 14, 15, 16], n), "appointment_day": booked.dayofweek, "distance_km": RNG.gamma(2, 4, n).round(1)})
    probability = .05 + appointments.previous_no_shows * .13 + (appointments.days_between_booking_and_appointment > 21) * .08 + (appointments.appointment_hour < 9) * .04
    appointments["no_show"] = RNG.binomial(1, np.clip(probability, 0.03, .65))
    appointments.to_csv(ROOT / "appointments.csv", index=False)
    dates = pd.date_range("2025-01-01", periods=365)
    occupancy = pd.DataFrame({"date": dates, "department": RNG.choice(["Emergency", "Cardiology", "Pediatrics"], len(dates)), "total_beds": 64})
    occupancy["occupied_beds"] = np.clip((43 + 8 * np.sin(np.arange(len(dates)) / 18) + RNG.normal(0, 3, len(dates))).round(), 25, 63).astype(int)
    occupancy.to_csv(ROOT / "bed_occupancy.csv", index=False)

if __name__ == "__main__": generate()
