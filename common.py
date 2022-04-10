from typing import Optional
from pyrogram import Client
from pyrogram.client import User

ME_ID: int = 0
ME_USER: Optional[User] = None


def init_common(app: Client):
    global ME_USER, ME_ID
    ME_USER = app.get_me()
    ME_ID = ME_USER.id
