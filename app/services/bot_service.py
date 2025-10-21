import traceback
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Update
from aiogram.exceptions import TelegramUnauthorizedError
from app.core.config import settings

bots: dict[str, dict] = {}

async def register_handlers(dp: Dispatcher):
    async def start_handler(message: types.Message):
        username = getattr(message.from_user, "username", None) or message.from_user.id
        print(f"📩 Message from {username}: {message.text}")
        await message.answer("✅ Salom! Bot ishlayapti 🚀")

    dp.message.register(start_handler, Command("start"))


async def create_bot(token: str):
    try:
        if token in bots:
            return {"status": "already_started", "webhook": f"{settings.domain}/webhook/{token}"}

        bot = Bot(token=token)
        dp = Dispatcher()

        await register_handlers(dp)

        try:
            await bot.delete_webhook(drop_pending_updates=True)
        except Exception:
            pass

        webhook_url = f"{settings.domain}/webhook/{token}"
        await bot.set_webhook(webhook_url)

        bots[token] = {"bot": bot, "dp": dp}
        print(f"✅ Bot ishga tushdi: {webhook_url}")
        return {"status": "started", "webhook": webhook_url}

    except TelegramUnauthorizedError:
        return {"error": "Invalid bot token"}
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}


async def remove_bot_token(token: str):
    try:
        if token not in bots:
            return {
                "status": "already_removed",
                "webhook": f"{settings.domain}/webhook/{token}"
            }

        bot = Bot(token=token)
        dp = Dispatcher()

        await register_handlers(dp)

        try:
            await bot.delete_webhook(drop_pending_updates=True)
        except Exception:
            pass

        return {"status": "removed"}

    except TelegramUnauthorizedError:
        return {"error": "Invalid bot token"}
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}



async def handle_webhook(token: str, data: dict):
    if token not in bots:
        print("❌ Bot not registered:", token)
        return {"error": "Bot not registered"}

    bot = bots[token]["bot"]
    dp = bots[token]["dp"]

    try:
        print(f"📨 Webhook received for token: {token[:10]}..., payload keys: {list(data.keys())}")
        update = Update(**data)

        if hasattr(dp, "update") and hasattr(dp.update, "update"):
            await dp.update.update(bot=bot, update=update)
            print("✅ Update processed via dp.update.update()")
        else:
            await dp.feed_update(bot, update)
            print("✅ Update processed via dp.feed_update()")

        return {"ok": True}
    except Exception as e:
        print("❌ Exception while processing update:", e)
        traceback.print_exc()
        return {"error": str(e)}
