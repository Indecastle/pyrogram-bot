from pyrogram import Client, filters
from pyrogram.types import Message

import helper

def chats(my_chats):
    async def func(flt, _, msg):
        return msg.chat.id in flt.my_chats

    return filters.create(
        func,
        "my_chats",
        my_chats=my_chats
    )


def is_true(action):
    async def func(flt, _, msg):
        return flt.action(msg)

    return filters.create(
        func,
        "is_true",
        action=staticmethod(action)
    )


def is_favorite_chat():
    async def func(flt: Client, _, msg: Message):
        return helper.is_favorite_chat(msg)

    return filters.create(
        func,
        "is_favorite_chat",
    )
