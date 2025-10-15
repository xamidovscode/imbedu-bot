import os
import asyncio
from fastapi import FastAPI, Request
from pydantic import BaseModel
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update

app = FastAPI(title="Dynamic Telegram Bots")

bots = {}


class BotTokenSchema(BaseModel):
    token: str


@app.post("/start-bot")
async def start_bot(data: BotTokenSchema):
    token = data.token

    if token in bots:
        return {"ok": False, "msg": "Bot already started"}

    bot, dp, webhook_path = await create_bot(token)
    bots[token] = (bot, dp, webhook_path)
    return {"ok": True, "webhook_path": webhook_path}


async def create_bot(token: str):
    bot = Bot(token=token)
    dp = Dispatcher()

    @dp.message()
    async def echo_handler(message: types.Message):
        await message.answer(f"Siz yozdingiz: {message.text}")

    webhook_path = f"/webhook/{token}"
    WEBHOOK_URL = f"https://joxacode.uz{webhook_path}"  # o'zingning domain

    await bot.set_webhook(WEBHOOK_URL)

    @app.post(webhook_path)
    async def webhook_handler(request: Request):
        data = await request.json()
        update = Update(**data)
        await dp.feed_update(bot, update)
        return {"ok": True}

    return bot, dp, webhook_path


@app.post("/stop-bot")
async def stop_bot(data: BotTokenSchema):
    token = data.token
    if token not in bots:
        return {"ok": False, "msg": "Bot not found"}

    bot, dp, webhook_path = bots[token]
    await bot.delete_webhook()
    await bot.session.close()
    bots.pop(token)
    return {"ok": True}
