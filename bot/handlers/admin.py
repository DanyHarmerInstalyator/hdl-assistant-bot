# bot/handlers/admin.py

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config.config import ADMINS, BROADCAST_RECIPIENTS

router = Router() 


class AdminState(StatesGroup):
    waiting_for_broadcast_text = State()


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if message.from_user.id not in ADMINS:
        await message.answer("🔒 У вас нет доступа к этой команде.")
        return
    await message.answer("📬 Введите текст рассылки для выбранных пользователей:")
    await state.set_state(AdminState.waiting_for_broadcast_text)


@router.message(AdminState.waiting_for_broadcast_text)
async def process_broadcast_text(message: Message, state: FSMContext, bot):
    if message.from_user.id not in ADMINS:
        await state.clear()
        return

    text = message.text
    if not text or not text.strip():
        await message.answer("❌ Текст не может быть пустым. Попробуйте снова:")
        return

    success_count = 0
    for user_id in BROADCAST_RECIPIENTS:
        try:
            await bot.send_message(chat_id=user_id, text=text)
            success_count += 1
        except Exception as e:
            print(f"❗ Не удалось отправить сообщение пользователю {user_id}: {e}")

    await message.answer(f"✅ Рассылка отправлена {success_count} из {len(BROADCAST_RECIPIENTS)} получателей.")
    await state.clear()