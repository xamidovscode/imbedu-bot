import asyncio

import requests
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from ..utils import is_member, post_credentials
from uuid import uuid4

from app.utils import ChatRef
from ..utils.states import LoginStates


def build_start_router(channel: ChatRef, channel_link: str) -> Router:
    r = Router(name=f"start_{uuid4().hex[:6]}")

    async def _ask_username(message: types.Message, state: FSMContext):
        await message.answer("✅ Salom! Bot ishlayapti 🚀")
        await message.answer("👤 Iltimos, IMB EDU platformasidagi loginingizni kiriting! (yoki /cancel).")
        await state.set_state(LoginStates.waiting_username)

    async def _ask_username_from_cb(cb: types.CallbackQuery, state: FSMContext):
        await cb.message.answer("👤 Iltimos, foydalanuvchi nomini yuboring (yoki /cancel).")
        await state.set_state(LoginStates.waiting_username)

    @r.message(Command("start"))
    async def start_handler(message: types.Message, state: FSMContext):
        print("[start_handler] /start received from", message.from_user.id)
        bot = message.bot
        user_id = message.from_user.id

        if not await is_member(bot, channel, user_id):
            kb = InlineKeyboardBuilder()
            kb.button(text="📢 Kanalga obuna bo‘lish", url=channel_link)
            kb.button(text="✅ Tekshirish", callback_data="check_sub")
            kb.adjust(1)
            await message.answer(
                "❗️ Iltimos, kanalga obuna bo‘ling. So‘ng “Tekshirish” tugmasini bosing.",
                reply_markup=kb.as_markup(),
            )
            return

        await _ask_username(message, state)

    @r.callback_query(lambda c: c.data == "check_sub")
    async def check_subscription(cb: types.CallbackQuery, state: FSMContext):
        print("[check_subscription] callback from", cb.from_user.id, "data=", cb.data)
        bot = cb.bot
        user_id = cb.from_user.id

        if not await is_member(bot, channel, user_id):
            await cb.answer("Hali obuna bo‘lmagansiz. Avval kanalga qo‘shiling.", show_alert=True)
            kb = InlineKeyboardBuilder()
            kb.button(text="📢 Kanalga obuna bo‘lish", url=channel_link)
            kb.button(text="✅ Tekshirish", callback_data="check_sub")
            kb.adjust(1)
            try:
                await cb.message.edit_reply_markup(reply_markup=kb.as_markup())
            except Exception as e:
                print("[check_subscription] edit_reply_markup error:", e)
            return

        try:
            await cb.message.edit_text("✅ Rahmat! Obuna tasdiqlandi.")
        except Exception as e:
            print("[check_subscription] edit_text error:", e)

        await cb.answer()
        await _ask_username_from_cb(cb, state)

    @r.message(Command("login"))
    async def manual_login(message: types.Message, state: FSMContext):
        await _ask_username(message, state)

    @r.message(Command("cancel"))
    async def cancel_flow(message: types.Message, state: FSMContext):
        await state.clear()
        await message.answer("❎ Jarayon bekor qilindi. /login orqali qayta boshlashingiz mumkin.")

    @r.message(LoginStates.waiting_username, F.text.len() > 0)
    async def got_username(message: types.Message, state: FSMContext):
        username = message.text.strip()
        await state.update_data(username=username)
        await message.answer("🔒 Endi parolni yuboring (yoki /cancel).")
        await state.set_state(LoginStates.waiting_password)

    @r.message(LoginStates.waiting_password, F.text.len() > 0)
    async def got_password(message: types.Message, state: FSMContext):
        data = await state.get_data()
        username = data.get("username")
        password = message.text.strip()

        await message.answer("⏳ Tekshirilmoqda...")
        ok, payload, err = await post_credentials(username, password, message.from_user)

        if ok:
            token = payload.get("token") if isinstance(payload, dict) else None
            await message.answer(
                "✅ Muvaffaqiyatli kirdingiz!\n"
                f"👤 <b>{username}</b>\n"
                f"🔑 <code>{token or '—'}</code>",
                parse_mode="HTML",
            )
        else:
            await message.answer(
                "❌ Login amalga oshmadi.\n"
                f"Sabab: {err or 'Noma’lum xatolik'}\n"
                "Iltimos, /login orqali qayta urinib ko‘ring."
            )

        await state.clear()

    @r.message(LoginStates.waiting_password)
    async def pw_fallback(message: types.Message):
        await message.answer("Parolni oddiy matn ko‘rinishida yuboring, iltimos. (yoki /cancel)")

    return r
