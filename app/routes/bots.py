from fastapi import APIRouter, Depends, HTTPException

from app.schemas.bot_info import BotTokenSchema
from app.services.bot_service import create_bot, remove_bot_token
from app.core.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.bot_info import add_token, remove_token

router = APIRouter(prefix="/bots", tags=["Bots"])

@router.post("/create")
async def start_bot(
        body: BotTokenSchema, session: AsyncSession = Depends(get_db)
):
    token = body.token.strip()

    if not token:
        return {"error": "token required"}


    result = await create_bot(token)
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    try:
        await add_token(session, token)
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail="Failed to save token") from e

    return result

@router.post("/remove")
async def remove_bot(
        body: BotTokenSchema, session: AsyncSession = Depends(get_db)
):
    token = body.token.strip()
    if not token:
        return {"error": "token required"}

    result = await remove_bot_token(token)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    await remove_token(session, token)

    return result


