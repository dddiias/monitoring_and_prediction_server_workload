import json
import os
from datetime import datetime
from config.config import TOKENS_FILE

def load_users() -> dict:
    if not os.path.exists(TOKENS_FILE):
        return {}
    with open(TOKENS_FILE, "r") as f:
        return json.load(f)

def save_users(data: dict) -> None:
    with open(TOKENS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_server(user_id: str, token: str, server_name="My Server", os_info="Unknown") -> None:
    users = load_users()

    user_data = users.get(user_id, {"servers": []})
    user_data["servers"].append({
        "token": token,
        "connected_at": datetime.now().isoformat(timespec="seconds"),
        "server_name": server_name,
        "os": os_info
    })

    users[user_id] = user_data
    save_users(users)


def delete_server(user_id: str, token: str) -> bool:
    users = load_users()
    user = users.get(user_id)

    if not user:
        return False

    original_len = len(user["servers"])
    user["servers"] = [srv for srv in user["servers"] if srv["token"] != token]
    
    if len(user["servers"]) < original_len:
        users[user_id] = user
        save_users(users)
        return True
    return False

