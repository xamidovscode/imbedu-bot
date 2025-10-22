import traceback
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Update
from aiogram.exceptions import TelegramUnauthorizedError
from app.core.config import settings
from app.routers import setup_routers
from .main import bots
#
#
# async def register_handlers(dp: Dispatcher):
#     async def start_handler(message: types.Message):
#         await message.answer("✅ Salom! Bot ishlayapti 🚀")
#     dp.message.register(start_handler, Command("start"))
#

async def create_bot(token: str):
    try:
        if token in bots:
            return {
                "status": "already_started",
                "webhook": f"{settings.domain}/webhook/{token}",
            }

        bot = Bot(token=token)
        dp = Dispatcher()

        # await register_handlers(dp)
        setup_routers(dp)

        try:
            await bot.delete_webhook(drop_pending_updates=True)
        except Exception:
            pass

        webhook_url = f"{settings.domain}/webhook/{token}"
        await bot.set_webhook(webhook_url)

        bots[token] = {"bot": bot, "dp": dp}
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

        try:
            await bot.delete_webhook(drop_pending_updates=True)
        except Exception:
            pass
        bots.pop(token)
        return {"status": "removed"}

    except TelegramUnauthorizedError:
        return {"error": "Invalid bot token"}
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}



async def handle_webhook(token: str, data: dict):
    if token not in bots:
        return {"error": "Bot not registered"}

    bot = bots[token]["bot"]
    dp = bots[token]["dp"]

    try:
        update = Update(**data)

        if hasattr(dp, "update") and hasattr(dp.update, "update"):
            await dp.update.update(bot=bot, update=update)
        else:
            await dp.feed_update(bot, update)

        return {"ok": True}
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}
