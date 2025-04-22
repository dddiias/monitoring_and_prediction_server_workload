from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from keyboards.inline import get_help_menu, get_main_inline_menu

router = Router()

@router.message(F.text == "❓ Помощь")
async def help_entry(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "📖 <b>Чем могу помочь?</b>\n\nВыберите интересующий раздел ниже:",
        reply_markup=get_help_menu(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "help_connect")
async def help_connect(callback: CallbackQuery):
    await callback.message.edit_text(
        "<b>📍 Подключение сервера</b>\n\n"
        "1️⃣ Нажмите «📍 Подключить сервер»\n"
        "2️⃣ Введите название и операционную систему\n"
        "3️⃣ Получите <code>telegraf.conf</code> и установите его на сервер\n\n"
        "📥 Метрики начнут поступать после перезапуска Telegraf.\n\n",
        reply_markup=get_help_menu(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "help_metrics")
async def help_metrics(callback: CallbackQuery):
    await callback.message.edit_text(
        "<b>📊 Метрики</b>\n\n"
        "Нажмите «📊 Метрики», выберите нужный сервер и получите загрузку CPU и памяти.\n\n"
        "Метрики обновляются автоматически на сервере с установленным Telegraf.\n",
        reply_markup=get_help_menu(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "help_forecast")
async def help_forecast(callback: CallbackQuery):
    await callback.message.edit_text(
        "<b>🔮 Прогнозирование нагрузки</b>\n\n"
        "В будущем бот будет строить графики на основе моделей машинного обучения (LSTM, ARIMA и т.п.).\n"
        "Скоро появится возможность заранее видеть пики загрузки!\n",
        reply_markup=get_help_menu(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "help_myservers")
async def help_myservers(callback: CallbackQuery):
    await callback.message.edit_text(
        "<b>📄 Мои серверы</b>\n\n"
        "Нажмите кнопку «📄 Мои серверы», чтобы просмотреть список всех серверов, которые вы подключили ранее.\n\n"
        "Для каждого сервера отображается:\n"
        "• Название\n• Операционная система\n• Дата подключения\n• Уникальный токен\n\n"
        "Это удобно, если вы подключили несколько серверов.\n",
        reply_markup=get_help_menu(),
        parse_mode="HTML"
    )
    await callback.answer()
