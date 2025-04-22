from aiogram import Router, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

router = Router()

class CpuLimitForm(StatesGroup):
    waiting_for_cpu_limit = State()

@router.message(F.text.regexp(r"^\d{1,3}$"))
async def cpu_limit_entered(message: Message, state: FSMContext):
    value = int(message.text)
    if 10 <= value <= 100:
        await message.answer(f"✅ Установлен лимит по CPU: {value}%")
        await state.clear()
    else:
        await message.answer("❗ Введите значение от 10 до 100.")
