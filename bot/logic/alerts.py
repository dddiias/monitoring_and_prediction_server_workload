import asyncio
from logic.influx_metrics import analyze_metrics
from logic.storage import load_users
import os
import json

ALERT_THRESHOLDS = {
    "CPU": 90,
    "Memory": 90,
    "Disk": 90,
}

ALERT_STATE_FILE = os.path.join("/app/data", "alerts_state.json")

def load_alert_state():
    if os.path.exists(ALERT_STATE_FILE):
        with open(ALERT_STATE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_alert_state(state):
    with open(ALERT_STATE_FILE, "w") as f:
        json.dump(state, f)

async def alerts_task(bot):
    last_alert_state = load_alert_state()
    while True:
        users = load_users()
        for user_id, user_data in users.items():
            for server in user_data.get("servers", []):
                token = server["token"]
                stats = analyze_metrics(token)
                alerts = []
                # CPU
                cpu_user = stats["CPU"]["User"].get("values", [])
                cpu_system = stats["CPU"]["System"].get("values", [])
                cpu_alert = False
                if (cpu_user and cpu_system
                    and cpu_user[-1] is not None
                    and cpu_system[-1] is not None
                    and (cpu_user[-1] + cpu_system[-1]) > ALERT_THRESHOLDS["CPU"]):
                    cpu_alert = True
                    alerts.append("⚠️ Высокая загрузка CPU!")
                # RAM
                ram_values = stats["Memory"]["Used"].get("values", [])
                ram_alert = False
                if ram_values and ram_values[-1] is not None and ram_values[-1] > ALERT_THRESHOLDS["Memory"]:
                    ram_alert = True
                    alerts.append("⚠️ Высокое использование памяти!")
                # Disk
                disk_values = stats["Disk"]["Used"].get("values", [])
                disk_alert = False
                if disk_values and disk_values[-1] is not None and disk_values[-1] > ALERT_THRESHOLDS["Disk"]:
                    disk_alert = True
                    alerts.append("⚠️ Диск почти заполнен!")

                prev = last_alert_state.get(token, {"cpu": False, "ram": False, "disk": False})
                need_send = False
                text = f"🚨 АЛЕРТ для сервера {server['server_name']} (token: {token}):\n"
                if cpu_alert and not prev["cpu"]:
                    need_send = True
                if ram_alert and not prev["ram"]:
                    need_send = True
                if disk_alert and not prev["disk"]:
                    need_send = True
                if need_send and alerts:
                    text += "\n".join(alerts)
                    try:
                        await bot.send_message(user_id, text)
                    except Exception as e:
                        print(f"Ошибка отправки алерта: {e}")

                last_alert_state[token] = {"cpu": cpu_alert, "ram": ram_alert, "disk": disk_alert}
        save_alert_state(last_alert_state)
        await asyncio.sleep(10)