import os
import json
from datetime import datetime, timedelta
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from config.config import INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET, TOKENS_FILE
import numpy as np

INFLUX_TIMEOUT = int(os.getenv("INFLUX_TIMEOUT", "30000"))


def get_influx_client():
    return InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG, timeout=INFLUX_TIMEOUT)


def get_latest_metrics(token: str) -> dict:
    client = get_influx_client()
    query_api = client.query_api()
    result = {}

    # CPU
    cpu_query = f'''
from(bucket: "{INFLUX_BUCKET}")
  |> range(start: -10m)
  |> filter(fn: (r) => r["token"] == "{token}")
  |> filter(fn: (r) => r["_measurement"] == "cpu")
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> sort(columns: ["_time"], desc: true)
  |> group(columns: ["cpu"])
  |> limit(n:1)
'''
    cpu_tables = query_api.query(cpu_query)
    cpu_data = {}
    for table in cpu_tables:
        for record in table.records:
            cpu_name = record.values.get("cpu", "cpu-total")
            cpu_data[cpu_name] = {
                "Idle": round(record.values.get("usage_idle", 0), 2),
                "System": round(record.values.get("usage_system", 0), 2),
                "User": round(record.values.get("usage_user", 0), 2)
            }
    if cpu_data:
        result["CPU"] = cpu_data.get("cpu-total", next(iter(cpu_data.values())))

    # Memory
    mem_query = f'''
from(bucket: "{INFLUX_BUCKET}")
  |> range(start: -10m)
  |> filter(fn: (r) => r["token"] == "{token}")
  |> filter(fn: (r) => r["_measurement"] == "mem")
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n:1)
'''
    mem_tables = query_api.query(mem_query)
    for table in mem_tables:
        for record in table.records:
            used = record.values.get("used", 0)
            available = record.values.get("available", 0)
            total = record.values.get("total", None)
       
            if used is not None and available is not None:
                if total is None:
                    total = used + available
                result["Memory"] = {
                    "Used_bytes": used,
                    "Available_bytes": available,
                    "Total_bytes": total
                }

    # Disk
    disk_query = f'''
from(bucket: "{INFLUX_BUCKET}")
  |> range(start: -10m)
  |> filter(fn: (r) => r["token"] == "{token}")
  |> filter(fn: (r) => r["_measurement"] == "disk")
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> sort(columns: ["_time"], desc: true)
  |> group(columns: ["device", "path"])
  |> limit(n:1)
'''
    disk_tables = query_api.query(disk_query)
    disk_data = {}
    for table in disk_tables:
        for record in table.records:
            device = record.values.get("device", "unknown")
            path = record.values.get("path", "")
            used = record.values.get("used", 0)
            total = record.values.get("total", 0)
            used_percent = record.values.get("used_percent", 0)
            
            if used >= 0 and total > 0 and used <= total:
                disk_data[f"{device}:{path}"] = {
                    "Used_bytes": used,
                    "Total_bytes": total,
                    "Used_percent": used_percent
                }
    if disk_data:

        root_disk = None
        for k, v in disk_data.items():
            if k.endswith(":/") or k.endswith(":/root"):
                root_disk = v
                break
        if not root_disk:
            root_disk = next(iter(disk_data.values()))
        result["Disk"] = root_disk

    net_query = f'''
from(bucket: "{INFLUX_BUCKET}")
  |> range(start: -10m)
  |> filter(fn: (r) => r["token"] == "{token}")
  |> filter(fn: (r) => r["_measurement"] == "net" and r["interface"] != "lo")
  |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> sort(columns: ["_time"], desc: true)
  |> group(columns: ["interface"])
  |> limit(n:1)
'''
    net_tables = query_api.query(net_query)
    net_data = {}
    for table in net_tables:
        for record in table.records:
            iface = record.values.get("interface", "unknown")
            net_data[iface] = {
                "Bytes_sent": record.values.get("bytes_sent", 0),
                "Bytes_recv": record.values.get("bytes_recv", 0),
                "Err_in": record.values.get("err_in", 0),
                "Err_out": record.values.get("err_out", 0)
            }
    if net_data:
        result["Network"] = net_data

    client.close()
    return result

def get_metrics_history(token: str, period: str = "24h") -> list:
    client = get_influx_client()
    query_api = client.query_api()
    query = f'''
from(bucket: "{INFLUX_BUCKET}")
  |> range(start: -{period})
  |> filter(fn: (r) => r["token"] == "{token}")
  |> sort(columns: ["_time"], desc: false)
'''
    try:
        tables = query_api.query(query)
    except Exception as e:
        print(f"[InfluxDB] Ошибка при запросе истории метрик: {e}")
        return []
    history = []
    for table in tables:
        for record in table.records:
            name = record.get_measurement()
            tags = record.values
            fields = {record.get_field(): record.get_value()}
            time = record.get_time()
            history.append({
                "name": name,
                "tags": tags,
                "fields": fields,
                "time": time
            })
    client.close()
    return history

def analyze_metrics(token: str, period: str = "24h") -> dict:
    history = get_metrics_history(token, period)
    metrics_result = {
        "CPU": {"User": [], "System": [], "Idle": []},
        "Memory": {"Used": []},
        "Disk": {"Used": []},
    }
    for record in history:
        name = record.get("name", "")
        tags = record.get("tags", {})
        fields = record.get("fields", {})
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

def get_all_tokens() -> list:
    if not os.path.exists(TOKENS_FILE):
        return []
    with open(TOKENS_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)
    tokens = []
    for user in users.values():
        for server in user.get("servers", []):
            tokens.append(server["token"])
    return tokens

def get_aggregated_metrics_history(token: str, period: str = "24h", step: str = "10s") -> list:
    """
    Возвращает список срезов по времени: [{'timestamp': ..., 'cpu': ..., 'ram': ..., 'disk': ..., 'net': ...}]
    Все значения float, пропуски заполняются предыдущим значением, значения ограничены диапазоном.
    """
    client = get_influx_client()
    query_api = client.query_api()
    # CPU
    flux_cpu = f'''
from(bucket: "{INFLUX_BUCKET}")
  |> range(start: -{period})
  |> filter(fn: (r) => r["token"] == "{token}")
  |> filter(fn: (r) => r["_measurement"] == "cpu")
  |> aggregateWindow(every: {step}, fn: mean, createEmpty: false)
  |> pivot(rowKey:["_time"], columnKey: ["_field", "_measurement"], valueColumn: "_value")
  |> sort(columns: ["_time"])
'''
    # MEM
    flux_mem = f'''
from(bucket: "{INFLUX_BUCKET}")
  |> range(start: -{period})
  |> filter(fn: (r) => r["token"] == "{token}")
  |> filter(fn: (r) => r["_measurement"] == "mem")
  |> aggregateWindow(every: {step}, fn: mean, createEmpty: false)
  |> pivot(rowKey:["_time"], columnKey: ["_field", "_measurement"], valueColumn: "_value")
  |> sort(columns: ["_time"])
'''
    # DISK
    flux_disk = f'''
from(bucket: "{INFLUX_BUCKET}")
  |> range(start: -{period})
  |> filter(fn: (r) => r["token"] == "{token}")
  |> filter(fn: (r) => r["_measurement"] == "disk")
  |> aggregateWindow(every: {step}, fn: mean, createEmpty: false)
  |> pivot(rowKey:["_time"], columnKey: ["_field", "_measurement"], valueColumn: "_value")
  |> sort(columns: ["_time"])
'''
    # NET
    flux_net = f'''
from(bucket: "{INFLUX_BUCKET}")
  |> range(start: -{period})
  |> filter(fn: (r) => r["token"] == "{token}")
  |> filter(fn: (r) => r["_measurement"] == "net")
  |> aggregateWindow(every: {step}, fn: mean, createEmpty: false)
  |> pivot(rowKey:["_time"], columnKey: ["_field", "_measurement"], valueColumn: "_value")
  |> sort(columns: ["_time"])
'''

    cpu_tables = query_api.query(flux_cpu)
    mem_tables = query_api.query(flux_mem)
    disk_tables = query_api.query(flux_disk)
    net_tables = query_api.query(flux_net)

    time_dict = {}
    # CPU
    for table in cpu_tables:
        for record in table.records:
            ts = int(record.get_time().timestamp())
            cpu_user = record.values.get("usage_user_cpu", 0.0) or 0.0
            cpu_system = record.values.get("usage_system_cpu", 0.0) or 0.0
            cpu = float(cpu_user) + float(cpu_system)
            cpu = max(0.0, min(cpu, 100.0))
            if ts not in time_dict:
                time_dict[ts] = {}
            time_dict[ts]["cpu"] = cpu
    # MEM
    for table in mem_tables:
        for record in table.records:
            ts = int(record.get_time().timestamp())
            ram = 100.0 - float(record.values.get("available_percent_mem", 0.0) or 0.0)
            ram = max(0.0, min(ram, 100.0))
            if ts not in time_dict:
                time_dict[ts] = {}
            time_dict[ts]["ram"] = ram
    # DISK
    for table in disk_tables:
        for record in table.records:
            ts = int(record.get_time().timestamp())
            device = record.values.get("device", "")
            path = record.values.get("path", "")
            disk_val = float(record.values.get("used_percent", 0.0) or 0.0)
            disk_val = max(0.0, min(disk_val, 100.0))
            if ts not in time_dict:
                time_dict[ts] = {}
            if "_all_disks" not in time_dict[ts]:
                time_dict[ts]["_all_disks"] = []
            time_dict[ts]["_all_disks"].append({"device": device, "path": path, "val": disk_val})
    for ts in time_dict:
        if "_all_disks" in time_dict[ts]:
            root = next((d for d in time_dict[ts]["_all_disks"] if d["path"] == "/"), None)
            c_disk = next((d for d in time_dict[ts]["_all_disks"] if d["device"] == "C:"), None)
            any_disk = time_dict[ts]["_all_disks"][0]
            chosen = root or c_disk or any_disk
            time_dict[ts]["disk"] = chosen["val"]
            del time_dict[ts]["_all_disks"]
    # NET
    for table in net_tables:
        for record in table.records:
            ts = int(record.get_time().timestamp())
            net_abs = float(record.values.get("bytes_recv", 0.0) or 0.0)
            if ts not in time_dict:
                time_dict[ts] = {}

            if "net" not in time_dict[ts]:
                time_dict[ts]["net"] = 0.0
            time_dict[ts]["net"] += net_abs
    result = []
    prev = {"cpu": None, "ram": None, "disk": None, "net": None}
    for ts in sorted(time_dict.keys()):
        cpu = time_dict[ts].get("cpu", prev["cpu"] if prev["cpu"] is not None else 0.0)
        ram = time_dict[ts].get("ram", prev["ram"] if prev["ram"] is not None else 0.0)
        disk = time_dict[ts].get("disk", prev["disk"] if prev["disk"] is not None else 0.0)
        net = time_dict[ts].get("net", prev["net"] if prev["net"] is not None else 0.0)
        result.append({
            "timestamp": ts,
            "cpu": cpu,
            "ram": ram,
            "disk": disk,
            "net": net
        })
        prev = {"cpu": cpu, "ram": ram, "disk": disk, "net": net}
    client.close()
    return result 