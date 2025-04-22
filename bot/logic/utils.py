import httpx

def generate_telegraf_config(token: str, server_ip: str) -> str:
    return f"""
[agent]
  interval = \"10s\"

[[inputs.cpu]]
  percpu = true
  totalcpu = true
  collect_cpu_time = false

[[inputs.mem]]

[[outputs.http]]
  url = \"http://{server_ip}:8000/telegraf\"
  method = \"POST\"
  data_format = \"json\"

  [outputs.http.headers]
    token = \"{token}\"
"""

def format_metrics(data: dict) -> str:
    if "error" in data:
        return "❌ Метрики не найдены. Попробуйте позже."

    result = ["🖥️ Последние метрики:"]
    if "CPU" in data:
        result.append("\nCPU:")
        for k, v in data["CPU"].items():
            result.append(f"  {k}: {v}%")
    if "Memory" in data:
        result.append("\nMemory:")
        for k, v in data["Memory"].items():
            result.append(f"  {k}: {v}%")
    return "\n".join(result)


def get_metrics_from_server(token: str, server_ip: str) -> dict:
    url = f"http://{server_ip}:8000/data?token={token}"
    try:
        response = httpx.get(url, timeout=5)
        return response.json()
    except Exception:
        return {"error": "Ошибка при запросе к серверу."}