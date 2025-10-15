from fastapi import APIRouter, Depends
from app.schemas.bot_info import BotTokenSchema
from app.services.bot_service import create_bot, handle_webhook
from app.core.db import async_session_maker
from app.crud.bot_info import add_token
import os

router = APIRouter(prefix="/bots", tags=["Bots"])
DOMAIN = os.getenv("DOMAIN")

@router.post("/start")
async def start_bot(body: BotTokenSchema):
    token = body.token.strip()
    if not token:
        return {"error": "token required"}

    # create bot (sets webhook and registers handlers)
    result = await create_bot(token, DOMAIN)
    if "error" in result:
        return result

    # save token into DB (use a DB session)
    async with async_session_maker() as session:
        await add_token(session, token)

    return result

# this endpoint is used by Telegram to deliver updates
# note: path is /webhook/{token} but we keep that on root app.router in main.py mapping
# to avoid double prefixes we will mount this route on main app directly via include_router in main.py
