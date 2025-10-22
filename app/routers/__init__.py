from aiogram import Router
from .start import build_start_router

def build_root_router() -> Router:
    root = Router(name="root")

    CHANNEL_ID = 1
    CHANNEL_LINK = 'https://t.me/imb_edu'

    root.include_router(build_start_router(channel=CHANNEL_ID, channel_link=CHANNEL_LINK))
    return root
