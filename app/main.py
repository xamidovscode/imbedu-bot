import os
from fastapi import FastAPI, Request
from app.core.db import Base, engine, async_session_maker
from app.crud.bot_info import get_all_tokens
from app.services.bot_service import create_bot, handle_webhook
from app.routes import bots as bot_routes
from app.core.config import settings

app = FastAPI(title="Imbedu Dynamic Bots")

app.include_router(bot_routes.router)

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        tokens = await get_all_tokens(session)
        print(f"♻️ Found {len(tokens)} tokens in DB — starting bots...")
        for token in tokens:
            res = await create_bot(token)
            print(" ->", res)

@app.post("/webhook/{token}")
async def telegram_webhook(token: str, request: Request):
    data = await request.json()
    return await handle_webhook(token, data)
