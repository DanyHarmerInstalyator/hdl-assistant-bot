# bot/handlers/admin.py

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup  # ← НЕ НУЖЕН, если используешь внешний states.py

# ✅ Правильный импорт:
from bot.utils.states import AdminState
from config.config import ADMINS, BROADCAST_RECIPIENTS

router = Router()

@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        await message.answer("❌ Доступ запрещён.")
        return
    await message.answer("Введите текст рассылки:")
    await state.set_state(AdminState.waiting_for_broadcast_text)

@router.message(AdminState.waiting_for_broadcast_text)
async def process_broadcast(message: Message, state: FSMContext, bot):
    if message.from_user.id not in ADMINS:
        await state.clear()
        return
    text = message.text
    if not text or not text.strip():
        await message.answer("Текст не может быть пустым.")
        return
    for user_id in BROADCAST_RECIPIENTS:
        try:
            await bot.send_message(user_id, text)
        except Exception as e:
            print(f"Ошибка отправки {user_id}: {e}")
    await message.answer("✅ Рассылка отправлена!")
    await state.clear()