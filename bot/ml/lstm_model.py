import os
import json    
import numpy as np
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Input 
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping 
from tensorflow.keras.layers import Dropout
from config.config import MODEL_DIR
from tensorflow.keras import backend as K

MODEL_PATH = os.path.join(MODEL_DIR, "lstm_forecast.keras")

def prepare_sequences_from_records(history_data: list, window_size: int, horizon: int):
    values = [[rec['cpu'], rec['ram'], rec['disk'], rec['net']] for rec in history_data]
    arr = np.array(values, dtype=np.float32)
    if np.isnan(arr).any() or np.isinf(arr).any():
        print("[LSTM] ВНИМАНИЕ: В данных есть NaN или inf!", arr)
        arr = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)
    max_vals = arr.max(axis=0)
    max_vals[max_vals == 0] = 1.0
    arr_norm = arr / max_vals
    X, y = [], []
    for i in range(len(arr_norm) - window_size - horizon + 1):
        X.append(arr_norm[i : i + window_size])
        y.append(arr_norm[i + window_size : i + window_size + horizon].flatten())
    return np.array(X), np.array(y), max_vals

def rmse(y_true, y_pred):
    return K.sqrt(K.mean(K.square(y_pred - y_true)))

def train_lstm_model(
    history_data: list,
    window_size: int = 20,
    horizon: int = 60,
    epochs: int = 140,
    batch_size: int = 16,
    model_path: str = None,
):
    X, y, max_vals = prepare_sequences_from_records(history_data, window_size, horizon)
    if X.shape[0] == 0:
        print(f"❌ Недостаточно данных: нужно ≥{window_size + horizon}, получено {len(history_data)}.")
        return
    model = Sequential([
       Input(shape=(window_size, X.shape[2])),
       LSTM(128, return_sequences=True),
       Dropout(0.2),
       LSTM(64, return_sequences=True),
       Dropout(0.2),
       LSTM(32),
       Dense(horizon * X.shape[2], activation="linear"),
   ])
    model.compile(optimizer="adam", loss="mse", metrics=["mae", rmse])

    save_path = model_path or MODEL_PATH
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    callbacks = [
        ModelCheckpoint(save_path, monitor="loss", save_best_only=True),
        EarlyStopping(monitor="loss", patience=5, restore_best_weights=True),
    ]
    model.fit(X, y, epochs=epochs, batch_size=batch_size, callbacks=callbacks, verbose=1)

    max_vals_file = os.path.splitext(save_path)[0] + "_max_vals.json"
    with open(max_vals_file, "w") as f:
        json.dump(max_vals.tolist(), f)

    print(f"✅ Модель сохранена: {save_path}")
    print(f"✅ Параметры масштабирования сохранены: {max_vals_file}")

    train_metrics = model.evaluate(X, y, verbose=0)
    metric_names = model.metrics_names  # ['loss', 'mae', 'rmse']
    print("=== Ошибки на обучающей выборке (в реальных единицах) ===")
    for i, name in enumerate(metric_names):
        if name == 'loss':
            continue 
        real_errors = train_metrics[i] * max_vals
        print(f"{name}: {[round(float(e), 2) for e in real_errors]} (CPU, RAM, Disk, Net)")

def forecast_next_hour(
    history_data: list,
    window_size: int = 20,
    horizon: int = 60,
    model_path: str = None,
):
    if len(history_data) < window_size + 1:
        return None, f"Недостаточно данных: нужно ≥{window_size + horizon} замеров, а есть только {len(history_data)}."
    try:
        X_batch, _, _ = prepare_sequences_from_records(history_data, window_size, horizon)
        if X_batch.shape[0] == 0:
            return None, f"Недостаточно данных для прогноза: нужно ≥{window_size + horizon} замеров, а есть только {len(history_data)}."
        last_seq = X_batch[-1:].astype(np.float32)
        model_file = model_path or MODEL_PATH
        model = load_model(model_file, custom_objects={'rmse': rmse})
        max_vals_file = model_file.replace(".keras", "_max_vals.json")
        max_vals = np.array(json.load(open(max_vals_file)), dtype=np.float32)
        y_pred = model.predict(last_seq)
        preds = y_pred.reshape(horizon, X_batch.shape[2]) * max_vals
        if np.isnan(preds).any() or np.isinf(preds).any():
            print("[LSTM] ВНИМАНИЕ: В прогнозе есть NaN или inf!", preds)
            preds = np.nan_to_num(preds, nan=0.0, posinf=0.0, neginf=0.0)
        result = {
            "CPU":    preds[:, 0].tolist(),
            "RAM":    preds[:, 1].tolist(),
            "Disk":   preds[:, 2].tolist(),
            "Network":preds[:, 3].tolist(),
        }
        values     = [[rec['cpu'], rec['ram'], rec['disk'], rec['net']] for rec in history_data]
        timestamps = [rec.get("timestamp", 0) for rec in history_data]
        avg_cpu, max_cpu = float(np.mean(result["CPU"])), float(np.max(result["CPU"]))
        avg_mem, max_mem = float(np.mean(result["RAM"])), float(np.max(result["RAM"]))
        avg_disk, max_disk = float(np.mean(result["Disk"])), float(np.max(result["Disk"]))
        avg_net, max_net = float(np.mean(result["Network"])), float(np.max(result["Network"]))
        comment = (
            f"🔮 Прогноз на следующий час:\n"
            f"🖥️ CPU: средн {avg_cpu:.1f}%, макс {max_cpu:.1f}%\n"
            f"💾 RAM: средн {avg_mem:.1f}%, макс {max_mem:.1f}%\n"
            f"📀 Disk: средн {avg_disk:.1f}%, макс {max_disk:.1f}%\n"
            f"🌐 Network: средн {avg_net/1e6:.1f} MB, макс {max_net/1e6:.1f} MB"
        )
        if max_cpu > 80:
            comment += "\n🚨 Возможна перегрузка CPU!"
        if max_mem > 80:
            comment += "\n🚨 Возможна нехватка ОЗУ!"
        if max_disk > 90:
            comment += "\n⚠️ Жёсткий диск почти заполнен!"
        if avg_net > 1e8:
            comment += "\n⚠️ Высокая сетeвая активность!"
        return (result, values, timestamps), comment
    except Exception as e:
        import traceback
        print("[LSTM] Ошибка прогноза:", e)
        traceback.print_exc()
        return None, f"Ошибка прогноза: {e}"
