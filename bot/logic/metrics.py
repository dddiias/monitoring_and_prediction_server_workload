import httpx

def get_metrics_from_server(token: str, server_ip: str) -> dict:
    url = f"http://{server_ip}:8000/data?token={token}"
    try:
        response = httpx.get(url, timeout=5)
        return response.json()
    except Exception:
        return {"error": "Ошибка при запросе к серверу."}
