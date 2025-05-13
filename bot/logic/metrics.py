import json
import os
from config.config import METRICS_FILE


def get_metrics_from_server(token: str, _: str = None) -> dict:
    if not os.path.exists(METRICS_FILE):
        return {}

    with open(METRICS_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return {}

    history = data.get(token, [])
    if not history or not isinstance(history, list):
        return {}

    latest = history[-1]
    cpu_fields = {}
    mem_fields = {}
    disk_fields = {}
    diskio_fields = {}
    net_fields = {}
    root_device = None

    for m in latest.get("metrics", []):
        name = m.get("name")
        tags = m.get("tags", {})
        fields = m.get("fields", {})

        if name == "cpu" and tags.get("cpu") == "cpu-total":
            cpu_fields = fields

        elif name == "mem":
            mem_fields = fields

        elif name == "disk" and tags.get("path") == "/":
            disk_fields = fields
            root_device = tags.get("device")

        elif name == "diskio" and root_device and tags.get("name") == root_device:
            diskio_fields = fields

        elif name == "net":
            iface = tags.get("interface")
            if iface and iface != "lo":
                net_fields = fields

    result = {}

    if cpu_fields:
        result["CPU"] = {
            "Idle": round(cpu_fields.get("usage_idle", 0), 2),
            "System": round(cpu_fields.get("usage_system", 0), 2),
            "User": round(cpu_fields.get("usage_user", 0), 2)
        }

    if mem_fields:
        result["Memory"] = {
            "Used_bytes": mem_fields.get("used", 0),
            "Available_bytes": mem_fields.get("available", 0)
        }

    if disk_fields:
        disk = {
            "Used_bytes": disk_fields.get("used", 0),
            "Total_bytes": disk_fields.get("total", 0)
        }
        if diskio_fields:
            disk["Read_bytes"] = diskio_fields.get("read_bytes", 0)
            disk["Write_bytes"] = diskio_fields.get("write_bytes", 0)
        result["Disk"] = disk

    if net_fields:
        result["Network"] = {
            "Bytes_sent": net_fields.get("bytes_sent", 0),
            "Bytes_recv": net_fields.get("bytes_recv", 0),
            "Err_in": net_fields.get("err_in", 0),
            "Err_out": net_fields.get("err_out", 0)
        }

    return result
