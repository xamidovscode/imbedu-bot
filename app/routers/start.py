from aiogram import Router, types
from aiogram.filters import Command
from uuid import uuid4

def build_start_router() -> Router:
    r = Router(name=f"start_{uuid4().hex[:6]}")

    @r.message(Command("start"))
    async def start_handler(message: types.Message):
        await message.answer("✅ Salom! Bot ishlayapti 🚀")

    return r
