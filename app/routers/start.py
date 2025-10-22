# app/bot/routers/start.py
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.enums import ChatMemberStatus
from aiogram.utils.keyboard import InlineKeyboardBuilder
from uuid import uuid4
from typing import Union, Optional

ChatRef = Union[int, str]

async def _is_member(bot, chat_id: ChatRef, user_id: int) -> bool:
    try:
        m = await bot.get_chat_member(chat_id, user_id)
        return m.status in {
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR,
        }
    except Exception:
        return False

def build_start_router(
    channel: ChatRef,
    channel_link: str,
    check_button_text: Optional[str] = "✅ Tekshirish",
    join_button_text: Optional[str] = "📢 Kanalga obuna bo‘lish",
) -> Router:
    r = Router(name=f"start_{uuid4().hex[:6]}")
    CH = channel

    @r.message(Command("start"))
    async def start_handler(message: types.Message):
        bot = message.bot
        user_id = message.from_user.id

        is_joined = await _is_member(bot, CH, user_id)
        if not is_joined:
            kb = InlineKeyboardBuilder()
            kb.button(text=join_button_text, url=channel_link)
            kb.button(text=check_button_text, callback_data="check_sub")
            kb.adjust(1)

            await message.answer(
                "❗️ Iltimos, kanalga obuna bo‘ling. So‘ng “Tekshirish” tugmasini bosing.",
                reply_markup=kb.as_markup(),
            )
            return

        await message.answer("✅ Salom! Bot ishlayapti 🚀")

    @r.callback_query(F.data == "check_sub")
    async def check_subscription(cb: types.CallbackQuery):
        bot = cb.bot
        user_id = cb.from_user.id

        print(cb.from_user.full_name)

        if not await _is_member(bot, CH, user_id):
            await cb.answer("Hali obuna bo‘lmagansiz. Avval kanalga qo‘shiling.", show_alert=True)
            kb = InlineKeyboardBuilder()
            kb.button(text=join_button_text, url=channel_link)
            kb.button(text=check_button_text, callback_data="check_sub")
            kb.adjust(1)
            try:
                await cb.message.edit_reply_markup(reply_markup=kb.as_markup())
            except Exception:
                pass
            return

        try:
            await cb.message.edit_text("✅ Rahmat! Obuna tasdiqlandi.")
        except Exception:
            pass
        await cb.message.answer("Endi botdan foydalanishingiz mumkin 🚀")
        await cb.answer()

    return r
