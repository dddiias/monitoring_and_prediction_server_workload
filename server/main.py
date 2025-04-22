from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json
import os
import time

app = FastAPI()
METRICS_FILE = "/app/data/user_metrics.json"

def load_metrics() -> dict:
    if not os.path.exists(METRICS_FILE):
        return {}
    with open(METRICS_FILE, "r") as f:
        return json.load(f)

def save_metrics(data):
    with open(METRICS_FILE, "w") as f:
        json.dump(data, f, indent=2)

metrics_by_token = load_metrics()

@app.post("/telegraf")
async def receive_metrics(request: Request):
    token = request.headers.get("token")
    if not token:
        return JSONResponse(status_code=400, content={"error": "Missing token"})

    try:
        body = await request.json()
        metrics_by_token[token] = {
            "metrics": body.get("metrics", []),
            "timestamp": int(time.time())
        }
        save_metrics(metrics_by_token)
        return {"status": "ok"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/data")
def get_metrics(token: str):
    record = metrics_by_token.get(token)
    if not record:
        return {"error": "No data"}

    cpu_fields = {}
    mem_fields = {}

    for m in record.get("metrics", []):
        if m["name"] == "cpu" and m["tags"].get("cpu") == "cpu-total":
            cpu_fields = m["fields"]
        elif m["name"] == "mem":
            mem_fields = m["fields"]

    response = {}

    if cpu_fields:
        response["CPU"] = {
            "Idle": round(cpu_fields.get("usage_idle", 0), 2),
            "System": round(cpu_fields.get("usage_system", 0), 2),
            "User": round(cpu_fields.get("usage_user", 0), 2)
        }

    if mem_fields:
        available = round(mem_fields.get("available_percent", 0), 2)
        response["Memory"] = {
            "Available": available,
            "Used": round(100 - available, 2)
        }

    return response
