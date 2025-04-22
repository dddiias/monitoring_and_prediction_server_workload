import json
import os
from logic.config import TOKENS_FILE


def load_tokens() -> dict:
    if not os.path.exists(TOKENS_FILE):
        return {}
    with open(TOKENS_FILE, "r") as f:
        return json.load(f)


def save_tokens(tokens: dict) -> None:
    with open(TOKENS_FILE, "w") as f:
        json.dump(tokens, f, indent=2)