from pyrogram import Client
from pyrogram.types import Message


def is_favorite_chat(msg: Message) -> bool:
    return msg.from_user and msg.from_user.is_self and not msg.outgoing
