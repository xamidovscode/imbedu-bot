import asyncio
from fastapi import FastAPI, Request
from app.core.db import Base, engine, async_session_maker
from app.crud.bot_info import get_all_tokens
from app.services.bot_crud import create_bot, handle_webhook
from app.routes import bots as bot_routes

app = FastAPI(title="Imbedu Dynamic Bots")

app.include_router(bot_routes.router)

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        tokens = await get_all_tokens(session)
    sem = asyncio.Semaphore(5)

    async def start_one(token: str):
        async with sem:
            try:
                res = await asyncio.wait_for(create_bot(token), timeout=15)
                print(f" -> ✅ {token[:6]}… started: {res}")
                return True
            except asyncio.TimeoutError:
                print(f" -> ⏱️ {token[:6]}… timed out")
                return False
            except Exception as e:
                print(f" -> ❌ {token[:6]}… failed: {e}")
                return False

    await asyncio.gather(*(start_one(t) for t in tokens), return_exceptions=True)


@app.post("/webhook/{token}")
async def telegram_webhook(token: str, request: Request):
    data = await request.json()
    return await handle_webhook(token, data)
