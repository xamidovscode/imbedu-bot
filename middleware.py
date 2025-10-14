from aiogram.types import Update


class SimpleLoggingMiddleware:
    async def __call__(self, handler, event: Update, data: dict):
        if event.message:
            user = event.message.from_user
            text = event.message.text
            print(f"[BOT] {user.id} ({user.username}): {text}")
        return await handler(event, data)
