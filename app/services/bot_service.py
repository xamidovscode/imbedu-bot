import os
import traceback
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Update
from aiogram.exceptions import TelegramUnauthorizedError

# token -> {"bot": Bot, "dp": Dispatcher}
bots: dict[str, dict] = {}

# register handlers (use dp.message.register for aiogram 3.x)
async def register_handlers(dp: Dispatcher):
    async def start_handler(message: types.Message):
        # qattiq logging — terminalga chiqaradi
        username = getattr(message.from_user, "username", None) or message.from_user.id
        print(f"📩 Message from {username}: {message.text}")
        # javob yuborish
        await message.answer("✅ Salom! Bot ishlayapti 🚀")

    dp.message.register(start_handler, Command("start"))


async def create_bot(token: str, domain: str):
    """
    Create bot, register handlers, set webhook and store in memory.
    Returns dict with status or error.
    """
    try:
        # agar allaqachon bor bo'lsa, qayt
        if token in bots:
            return {"status": "already_started", "webhook": f"{domain}/webhook/{token}"}

        bot = Bot(token=token)
        dp = Dispatcher()

        # register handlers
        await register_handlers(dp)

        # clear previous webhook & drop pending updates to avoid backlog
        try:
            await bot.delete_webhook(drop_pending_updates=True)
        except Exception:
            # ignore if delete webhook fails
            pass

        webhook_url = f"{domain}/webhook/{token}"
        await bot.set_webhook(webhook_url)

        bots[token] = {"bot": bot, "dp": dp}
        print(f"✅ Bot ishga tushdi: {webhook_url}")
        return {"status": "started", "webhook": webhook_url}

    except TelegramUnauthorizedError:
        return {"error": "Invalid bot token"}
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}


async def handle_webhook(token: str, data: dict):
    """
    Process incoming webhook update for given token.
    Uses dp.update.update(...) if available, otherwise falls back to dp.feed_update(...) for compatibility.
    """
    if token not in bots:
        print("❌ Bot not registered:", token)
        return {"error": "Bot not registered"}

    bot = bots[token]["bot"]
    dp = bots[token]["dp"]

    try:
        print(f"📨 Webhook received for token: {token[:10]}..., payload keys: {list(data.keys())}")
        update = Update(**data)

        # Try modern method first (aiogram 3.x)
        if hasattr(dp, "update") and hasattr(dp.update, "update"):
            # dp.update.update(bot=bot, update=update) is recommended by some aiogram versions
            await dp.update.update(bot=bot, update=update)
            print("✅ Update processed via dp.update.update()")
        else:
            # fall back to feed_update (older or compatible)
            await dp.feed_update(bot, update)
            print("✅ Update processed via dp.feed_update()")

        return {"ok": True}
    except Exception as e:
        print("❌ Exception while processing update:", e)
        traceback.print_exc()
        return {"error": str(e)}
