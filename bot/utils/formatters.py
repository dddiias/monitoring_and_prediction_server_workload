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
