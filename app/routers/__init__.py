from aiogram import Router
from .start import build_start_router

def build_root_router() -> Router:
    root = Router(name="root")

    channel_link = 'https://t.me/imb_edu'
    channel_id = "@imb_edu"

    root.include_router(build_start_router(channel=channel_link, channel_link=channel_link))
    return root
