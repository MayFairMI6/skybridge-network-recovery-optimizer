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

MODEL = {
    "delay": {"intercept": -1.6, "weather": 2.5, "airspace": 2.2, "ash": 1.8, "slots": 1.5, "legs": .35},
    "cancel": {"intercept": -3.0, "weather": 2.8, "airspace": 3.4, "ash": 2.8, "slots": 1.2},
    "fare": {"base": 420, "demand": .32, "airspace": .18, "weather": .12},
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
