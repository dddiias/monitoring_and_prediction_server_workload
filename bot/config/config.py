import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN    = os.getenv("BOT_TOKEN")
SERVER_IP    = os.getenv("SERVER_IP")
TOKENS_FILE  = "/app/data/user_tokens.json"
METRICS_FILE = "/app/data/user_metrics.json"
DATA_DIR = os.getenv("DATA_DIR", "/app/data")
MODEL_DIR = os.path.join(DATA_DIR, "models")
INFLUX_URL = os.getenv("INFLUX_URL", "https://us-east-1-1.aws.cloud2.influxdata.com")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "zpBn3XHjYBTSI4ssitgbV6Lujsi18qtY6ydiFhbvfZfdZ5_iQG6hmmHVJTHgQ-IJ5oD0BDgrnTJ-aHAOZdvzlg==")
INFLUX_ORG = os.getenv("INFLUX_ORG", "dev team")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "server_metrics")