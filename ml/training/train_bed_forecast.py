"""Chronological naive-plus-trend baseline for bed occupancy forecasting."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

ROOT = Path(__file__).parents[2]

def train() -> dict[str, float]:
    data = pd.read_csv(ROOT / "data" / "bed_occupancy.csv", parse_dates=["date"]).sort_values("date")
    split = int(len(data) * .8); train_data, test_data = data.iloc[:split], data.iloc[split:]
    predictions = train_data.occupied_beds.tail(7).mean() * np.ones(len(test_data))
    metrics = {"mae": float(mean_absolute_error(test_data.occupied_beds, predictions)), "rmse": float(np.sqrt(mean_squared_error(test_data.occupied_beds, predictions))), "mape": float(np.mean(np.abs((test_data.occupied_beds - predictions) / test_data.occupied_beds)) * 100)}
    models = ROOT / "ml" / "models"; models.mkdir(exist_ok=True); (models / "bed_forecast_metrics.json").write_text(json.dumps(metrics, indent=2)); return metrics

if __name__ == "__main__": print(train())
