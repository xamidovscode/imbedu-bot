from fastapi import APIRouter
from app.schemas.bot_info import BotTokenSchema
from app.services.bot_service import create_bot, remove_bot_token
from app.core.db import async_session_maker
from app.crud.bot_info import add_token, remove_token
import os

router = APIRouter(prefix="/bots", tags=["Bots"])

@router.post("/create")
async def start_bot(body: BotTokenSchema):
    token = body.token.strip()

    if not token:
        return {"error": "token required"}

    result = await create_bot(token)
    if "error" in result:
        return result

    async with async_session_maker() as session:
        await add_token(session, token)

    return result

@router.post("/remove")
async def remove_bot(body: BotTokenSchema):

    token = body.token.strip()
    if not token:
        return {"error": "token required"}

    result = await remove_bot_token(token)

    if "error" in result:
        return result

    async with async_session_maker() as session:
        await remove_token(session, token)

    return result


