import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")
SERVER_IP = os.getenv("SERVER_IP")
TOKENS_FILE = "/app/data/user_tokens.json" 