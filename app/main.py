import os
import asyncio
from fastapi import FastAPI, Request
from app.core.db import Base, engine, async_session_maker
from app.models.bot_info import BotInfo
from app.crud.bot_info import get_all_tokens
from app.services.bot_service import create_bot, handle_webhook
from app.routes import bots as bot_routes
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI(title="Imbedu Dynamic Bots")

# include API router (for /bots/start)
app.include_router(bot_routes.router)

DOMAIN = os.getenv("DOMAIN")

# Create DB tables on startup
@app.on_event("startup")
async def startup_event():
    # create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # load tokens from DB and create bots
    async with async_session_maker() as session:
        tokens = await get_all_tokens(session)
        print(f"♻️ Found {len(tokens)} tokens in DB — starting bots...")
        for token in tokens:
            res = await create_bot(token, DOMAIN)
            print(" ->", res)

# Webhook endpoint that Telegram will call: /webhook/{token}
@app.post("/webhook/{token}")
async def telegram_webhook(token: str, request: Request):
    data = await request.json()
    return await handle_webhook(token, data)
