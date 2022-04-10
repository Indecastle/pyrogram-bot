from time import sleep
import random

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

import my_filters

delete_chat_messages = set()


def delete_messages_controller(app):

    @app.on_message(filters.command("delete", prefixes=".") & filters.me)
    def detele_handler(_, msg: Message):
        delete_chat_messages.add(msg.chat.id)
        msg.delete()

    @app.on_message(filters.command("undelete", prefixes=".") & filters.me)
    def undetele_handler(_, msg: Message):
        delete_chat_messages.remove(msg.chat.id)
        msg.delete()

    # @app.on_message()
    # def on_detele_handler(_, msg: Message):
    #     if msg.chat.id in delete_chat_messages:
    #         msg.delete()

    @app.on_message(filters.regex(r'^\. .+'))
    def on_detele_handler(_, msg: Message):
        msg.delete()

    @app.on_message(~filters.regex(r'^\..+') & my_filters.chats(delete_chat_messages))
    def on_detele_handler(_, msg: Message):
        msg.delete()
