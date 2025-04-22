from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from handlers.fsm.cpu_limit import CpuLimitForm
from keyboards.inline import get_main_inline_menu, get_settings_menu

router = Router()

@router.callback_query(F.data == "settings")
async def handle_settings(callback: CallbackQuery):
    await callback.message.edit_text(
        "⚙ Настройки:\n\n"
        "Здесь ты можешь изменить лимиты, частоту уведомлений и другие параметры.",
        reply_markup=get_settings_menu()
    )
    await callback.answer()

@router.callback_query(F.data == "set_cpu_limit")
async def set_cpu_limit(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("🧠 Введите лимит по CPU в процентах (от 10 до 100):")
    await state.set_state(CpuLimitForm.waiting_for_cpu_limit)
    await callback.answer()
    
@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text(
        "🔙 Возврат в главное меню.",
        reply_markup=get_main_inline_menu()
    )
    await callback.answer()
