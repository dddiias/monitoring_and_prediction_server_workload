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
        new_metrics = {
            "timestamp": int(time.time()),
            "metrics": body.get("metrics", [])
        }

        history = metrics_by_token.get(token, [])
        if not isinstance(history, list):
            history = []

        history.append(new_metrics)

        metrics_by_token[token] = history
        save_metrics(metrics_by_token)

        return {"status": "ok"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})