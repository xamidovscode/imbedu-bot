import asyncio

import requests

from app.utils import ChatRef
from aiogram.enums import ChatMemberStatus


async def is_member(bot, chat_id: ChatRef, user_id: int) -> bool:
    try:
        m = await bot.get_chat_member(chat_id, user_id)
        return m.status in {
            ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR,
        }
    except Exception as e:
        print("[_is_member] ERROR:", e)
        return False


async def post_credentials(username: str, password: str, from_user, timeout: int = 10):
    def sync_post():
        api_url = "https://demo.xamidovcoder.uz/api/v1/webhooks/bot-updates/"
        return requests.post(
            api_url,
            json={
                "username": username,
                "password": password,
                'tg_id': from_user.id,
                'full_name': from_user.full_name,
            },
            timeout=timeout
        )

    try:
        resp = await asyncio.to_thread(sync_post)

        if resp.status_code == 200:
            return True, resp.json(), None
        else:
            return False, None, resp.json()
    except Exception as e:
        return False, None, f"API ERROR: {e}"