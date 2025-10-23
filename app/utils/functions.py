from app.utils import ChatRef
from aiogram.enums import ChatMemberStatus


async def _is_member(bot, chat_id: ChatRef, user_id: int) -> bool:
    try:
        m = await bot.get_chat_member(chat_id, user_id)
        return m.status in {
            ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR,
        }
    except Exception as e:
        print("[_is_member] ERROR:", e)
        return False