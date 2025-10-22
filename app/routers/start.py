from aiogram import Router, types
from aiogram.filters import Command

start_router = Router(name="start")

@start_router.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("✅ Salom! Bot ishlayapti 🚀")
