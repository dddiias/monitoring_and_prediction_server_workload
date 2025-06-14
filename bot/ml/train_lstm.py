import os
import sys
from logic.influx_metrics import get_aggregated_metrics_history, get_all_tokens
from ml.lstm_model import train_lstm_model
from config.config import MODEL_DIR

def train_all_models(
    window_size: int = 20,
    horizon: int = 60,
    epochs: int = 140, 
    batch_size: int = 16,
):

    tokens = get_all_tokens()
    for token in tokens:
        history = get_aggregated_metrics_history(token)
        if not history or len(history) < window_size + horizon:
            print(f"❌ Нет данных для токена {token} или данных слишком мало.")
            continue
        model_path = os.path.join(MODEL_DIR, f"lstm_{token}.keras")
        train_lstm_model(
            history_data=history,
            window_size=window_size,
            horizon=horizon,
            epochs=epochs,
            batch_size=batch_size,
            model_path=model_path,
        )

if __name__ == "__main__":
    train_all_models()
