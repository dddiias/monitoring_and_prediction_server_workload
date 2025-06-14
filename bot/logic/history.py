from logic.influx_metrics import get_metrics_history, analyze_metrics



def analyze_metrics(token: str) -> dict:
    data = load_all_metrics()
    history = data.get(token, [])

    metrics_result = {
        "CPU": {"User": [], "System": [], "Idle": []},
        "Memory": {"Used": []},
        "Disk": {"Used": []},
    }

    for record in history:
        for metric in record.get("metrics", []):
            name = metric.get("name", "")
            tags = metric.get("tags", {})
            fields = metric.get("fields", {})

            if name == "cpu" and tags.get("cpu") == "cpu-total":
                metrics_result["CPU"]["User"].append(fields.get("usage_user", 0))
                metrics_result["CPU"]["System"].append(fields.get("usage_system", 0))
                metrics_result["CPU"]["Idle"].append(fields.get("usage_idle", 0))

            elif name == "mem":
                available = fields.get("available_percent", 0)
                used = 100 - available
                metrics_result["Memory"]["Used"].append(used)

            elif name == "disk" and tags.get("path") == "/":
                metrics_result["Disk"]["Used"].append(fields.get("used_percent", 0))

    for section in metrics_result:
        for metric_name, values in metrics_result[section].items():
            if isinstance(values, list):
                avg = round(sum(values) / len(values), 2) if values else 0
                mx = round(max(values), 2) if values else 0
                metrics_result[section][metric_name] = {
                    "avg": avg,
                    "max": mx,
                    "values": values
                }

    return metrics_result
