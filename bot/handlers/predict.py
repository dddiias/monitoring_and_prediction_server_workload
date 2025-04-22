from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.inline import get_main_inline_menu

router = Router()

@router.callback_query(F.data == "predict")
async def handle_predict(callback: CallbackQuery):
    await callback.message.edit_text(
        "🔮 Прогнозирование временно недоступно.\n"
        "Скоро здесь появится график на основе ML-модели.",
        reply_markup=get_main_inline_menu()
    )
    await callback.answer()
