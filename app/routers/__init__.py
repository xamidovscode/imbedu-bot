from aiogram import Router
from .start import build_start_router

def build_root_router() -> Router:
    root = Router(name="root")
    root.include_router(build_start_router())
    return root
