import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update
from aiogram.filters import Command
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_PATH = "/webhook"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH)
    print(f"✅ Webhook o‘rnatildi: {WEBHOOK_URL + WEBHOOK_PATH}")
    yield
    await bot.delete_webhook()
    print("🧹 Webhook o‘chirildi")

app = FastAPI(lifespan=lifespan)

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Salom! Bot webhook orqali ishlayapti 🚀")

@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update(**data)
    await dp.feed_update(bot, update)
    return {"ok": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)




