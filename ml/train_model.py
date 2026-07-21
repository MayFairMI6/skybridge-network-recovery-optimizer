"""Train delay/cancellation models from a joined aviation CSV.

Expected columns are documented in training_schema.csv. The script writes
model artifacts that the service can load in a later deployment step.
"""
import argparse, json
from pathlib import Path

MAX_TRAINING_ITERATIONS = 1000

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("csv"); parser.add_argument("--out", default="ml/model.json"); args = parser.parse_args()
    try:
        import pandas as pd
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler
        from sklearn.pipeline import make_pipeline
    except ImportError as exc:
        raise SystemExit("Install the ML extras first: pip install -r ml/requirements-ml.txt") from exc
    df = pd.read_csv(args.csv)
    features = ["weather_risk", "airspace_risk", "ash_risk", "slot_pressure", "last_minute_demand", "legs"]
    missing = [c for c in features + ["cancelled"] if c not in df]
    if missing: raise SystemExit("Missing columns: " + ", ".join(missing))
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=MAX_TRAINING_ITERATIONS)).fit(df[features], df["cancelled"])
    payload = {"features": features, "intercept": float(model[-1].intercept_[0]), "coefficients": model[-1].coef_[0].tolist(), "mean": model[0].mean_.tolist(), "scale": model[0].scale_.tolist()}
    Path(args.out).write_text(json.dumps(payload, indent=2)); print(args.out)

if __name__ == "__main__": main()
