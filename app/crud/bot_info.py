from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.bot_info import BotInfo

async def get_all_tokens(session: AsyncSession):
    result = await session.execute(select(BotInfo.token))
    tokens = [row[0] for row in result.all()]
    return tokens

async def add_token(session: AsyncSession, token: str):
    result = await session.execute(select(BotInfo).where(BotInfo.token == token))
    if result.scalars().first():
        return False
    session.add(BotInfo(token=token))
    await session.commit()
    return True

async def remove_token(session: AsyncSession, token: str):
    await session.execute(delete(BotInfo).where(BotInfo.token == token))
    await session.commit()
    return True
