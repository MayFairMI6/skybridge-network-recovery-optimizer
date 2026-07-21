"""Small, dependency-light prediction service for the classroom prototype.

It accepts normalized aviation features and returns calibrated disruption
probabilities. Replace the heuristic coefficients with a fitted model trained
from BTS/NOAA/OpenSky records when those datasets are available.
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, math, os

SIGMOID_DENOMINATOR = 1
SIGMOID_MIN = -30
SIGMOID_MAX = 30
DEFAULT_RISK = 0.0
DEFAULT_DEMAND = 0.5
DEFAULT_LEGS = 2

def sigmoid(x): return SIGMOID_DENOMINATOR / (SIGMOID_DENOMINATOR + math.exp(-max(SIGMOID_MIN, min(SIGMOID_MAX, x))))

DELAY_INTERCEPT = -1.6
DELAY_WEATHER_WEIGHT = 2.5
DELAY_AIRSPACE_WEIGHT = 2.2
DELAY_ASH_WEIGHT = 1.8
DELAY_SLOT_WEIGHT = 1.5
DELAY_LEG_WEIGHT = .35
CANCEL_INTERCEPT = -3.0
CANCEL_WEATHER_WEIGHT = 2.8
CANCEL_AIRSPACE_WEIGHT = 3.4
CANCEL_ASH_WEIGHT = 2.8
CANCEL_SLOT_WEIGHT = 1.2
BASE_FARE = 420
FARE_DEMAND_WEIGHT = .32
FARE_AIRSPACE_WEIGHT = .18
FARE_WEATHER_WEIGHT = .12

MODEL = {
    "delay": {"intercept": DELAY_INTERCEPT, "weather": DELAY_WEATHER_WEIGHT, "airspace": DELAY_AIRSPACE_WEIGHT, "ash": DELAY_ASH_WEIGHT, "slots": DELAY_SLOT_WEIGHT, "legs": DELAY_LEG_WEIGHT},
    "cancel": {"intercept": CANCEL_INTERCEPT, "weather": CANCEL_WEATHER_WEIGHT, "airspace": CANCEL_AIRSPACE_WEIGHT, "ash": CANCEL_ASH_WEIGHT, "slots": CANCEL_SLOT_WEIGHT},
    "fare": {"base": BASE_FARE, "demand": FARE_DEMAND_WEIGHT, "airspace": FARE_AIRSPACE_WEIGHT, "weather": FARE_WEATHER_WEIGHT},
}

def predict(x):
    weather = float(x.get("weather_risk", DEFAULT_RISK)); news = float(x.get("airspace_risk", DEFAULT_RISK))
    ash = float(x.get("ash_risk", DEFAULT_RISK)); slots = float(x.get("slot_pressure", DEFAULT_RISK))
    demand = float(x.get("last_minute_demand", DEFAULT_DEMAND)); legs = float(x.get("legs", DEFAULT_LEGS))
    d, c, f = MODEL["delay"], MODEL["cancel"], MODEL["fare"]
    delay = sigmoid(d["intercept"] + d["weather"]*weather + d["airspace"]*news + d["ash"]*ash + d["slots"]*slots + d["legs"]*legs)
    cancel = sigmoid(c["intercept"] + c["weather"]*weather + c["airspace"]*news + c["ash"]*ash + c["slots"]*slots)
    fare = round(f["base"] * (1 + f["demand"]*demand + f["airspace"]*news + f["weather"]*weather), 2)
    return {"delay_probability": round(delay, 4), "cancellation_probability": round(cancel, 4), "predicted_last_minute_fare": fare}

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/predict": self.send_error(404); return
        body = self.rfile.read(int(self.headers.get("content-length", 0)))
        result = predict(json.loads(body or "{}")); payload = json.dumps(result).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(payload))); self.end_headers(); self.wfile.write(payload)
    def log_message(self, *_): pass

if __name__ == "__main__":
    HTTPServer(("0.0.0.0", int(os.getenv("PORT", "8090"))), Handler).serve_forever()
