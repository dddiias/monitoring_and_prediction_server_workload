from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from config.config import MODEL_DIR

from keyboards.inline import get_main_inline_menu
from logic.influx_metrics import get_aggregated_metrics_history
from ml.lstm_model import forecast_next_hour, train_lstm_model

router = Router()

@router.callback_query(F.data.startswith("predict:"))
async def handle_predict(callback: CallbackQuery):
    try:
        await callback.answer()
        token = callback.data.split(":", 1)[1]
        await callback.message.answer(f"📅 Загружаю данные для токена: {token}...")

        history = get_aggregated_metrics_history(token)
        if not history:
            await callback.message.answer("❌ Нет истории метрик для этого сервера.")
            return

        model_file = os.path.join(MODEL_DIR, f"lstm_{token}.keras")
        # Обучение модели при первом запросе прогноза, если модели ещё нет
        if not os.path.exists(model_file):
            if len(history) < 80:
                await callback.message.answer("❌ Недостаточно данных для обучения модели прогноза.")
                return
            await callback.message.answer("⏳ Обучение модели прогнозирования, пожалуйста подождите...")
            train_lstm_model(history_data=history, window_size=20, horizon=60, epochs=50, batch_size=16, model_path=model_file)
            await callback.message.answer("✅ Модель обучена. Выполняю прогноз...")

        forecast_data, comment = forecast_next_hour(history, window_size=20, horizon=60, model_path=model_file)
        if forecast_data is None:
            await callback.message.answer(comment)
            return

        preds_dict, values, timestamps = forecast_data

        # Подготовка данных для графиков
        real_times = [datetime.fromtimestamp(ts) for ts in timestamps]
        if len(real_times) > 100:
            real_times = real_times[-100:]
            values     = values[-100:]
        pred_horizon = len(next(iter(preds_dict.values())))
        pred_times = [real_times[-1] + timedelta(seconds=60 * (i + 1)) for i in range(pred_horizon)]

        # Отправка графиков с фактическими и прогнозными значениями
        first = True
        for idx, metric in enumerate(["CPU", "RAM", "Disk", "Network"]):
            preds     = preds_dict[metric]
            real_vals = [v[idx] for v in values]

            fig, ax = plt.subplots()
            ax.plot(real_times, real_vals, label=f"{metric} (факт)")
            ax.plot(pred_times, preds,     label=f"{metric} (прогноз)", linestyle="--")
            ax.set_title(metric)
            ax.set_ylabel("%" if metric != "Network" else "Bytes recv")
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            fig.autofmt_xdate()
            ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0))
            plt.tight_layout()

            img_path = f"/tmp/{token}_forecast_{metric}.png"
            fig.savefig(img_path)
            plt.close(fig)

            if first:
                await callback.message.answer_photo(
                    FSInputFile(img_path),
                    caption=comment,
                    reply_markup=get_main_inline_menu()
                )
                first = False
            else:
                await callback.message.answer_photo(
                    FSInputFile(img_path),
                    reply_markup=get_main_inline_menu()
                )

    except Exception as e:
        await callback.message.answer(f"❌ Ошибка прогноза: {e}")
