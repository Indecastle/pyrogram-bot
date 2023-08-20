import asyncio
import time

from pyrogram import Client, filters
from pyrogram.enums import ChatType, ParseMode
from pyrogram.types import Message

import common
import my_filters
from models.enums.reply_type import ReplyType
from services.logger_service import log_mat
from services.mats_service import is_mat, get_random_warning, mat_reply, mat_stat_increase, get_matstat_result, \
    reply_handler
from settings_provider import set_or_update_setting_value, get_setting_value_async, get_setting_value


mats_chat_messages = set()

mat_on = True
old_mes = None

mat_delay = 2
last_time_mated = time.time()



reply_type = ReplyType(get_setting_value("reply_type", int))


def init_mats_chat_messages_controller(app: Client):
    global mats_chat_messages
    mats_chat_messages = set([d.chat.id for d in app.get_dialogs(limit=1000) if d.chat.type in (ChatType.CHANNEL, ChatType.PRIVATE, ChatType.SUPERGROUP)])
    mats_chat_messages.add(common.ME_ID)


def mats_messages_controller(app: Client):
    @app.on_message(filters.command("mat_channel_on", prefixes=".") & my_filters.is_favorite_chat())
    async def mat_handler(client: Client, msg: Message):
        try:
            chanel_mat_on = msg.command[1] == '1'
            await msg.edit(f"mat_channel_on = {chanel_mat_on}")
            await set_or_update_setting_value('is_enable_channel_mats', chanel_mat_on)
        except Exception as e:
            print("Failed to change a setting: " + str(e))

        await asyncio.sleep(2)
        await msg.delete()

    @app.on_message(filters.command("mat_on", prefixes=".") & my_filters.is_favorite_chat())
    async def mat_handler(client: Client, msg: Message):
        global mat_on
        mat_on = msg.command[1] == '1'

        await msg.edit(f"mat_on = {mat_on}")
        await asyncio.sleep(2)
        await msg.delete()

    @app.on_message(filters.command("mat_schedule_on", prefixes=".") & my_filters.is_favorite_chat())
    async def mat_handler(client: Client, msg: Message):
        try:
            mat_schedule_on = msg.command[1] == '1'
            await set_or_update_setting_value('is_enable_schedule_show_mat_stat', mat_schedule_on)
            await msg.edit(f"mat_schedule_on = {mat_schedule_on}")
        except Exception as e:
            print("Failed to change a setting: " + str(e))

        await asyncio.sleep(2)
        await msg.delete()

    @app.on_message(filters.command("mat", prefixes=".") & filters.me)
    async def mat_handler(_, msg: Message):
        mats_chat_messages.add(msg.chat.id)
        await msg.delete()

    @app.on_message(filters.command("unmat", prefixes=".") & filters.me)
    async def unmat_handler(_, msg: Message):
        mats_chat_messages.remove(msg.chat.id)
        await msg.delete()

    @app.on_message(filters.command(["matstat", "matstat2", "matstat3"], prefixes=".") & filters.me)
    async def show_mat_stats_handler(client: Client, msg: Message):
        is_before = len(msg.command) > 1 and msg.command[1] == 'd'
        is_get_link_username = msg.command[0] == 'matstat2'
        is_except_symbols = msg.command[0] == 'matstat3'

        days = 1
        if is_before:
            days = 30
            if len(msg.command) > 2 and msg.command[2]:
                days = int(msg.command[2])

        text = await get_matstat_result(msg.chat.id, days, is_get_link_username, is_except_symbols)

        parse_mode = ParseMode.DISABLED if is_except_symbols else ParseMode.DEFAULT

        if msg.from_user and msg.from_user.is_self or msg.sender_chat and msg.sender_chat.is_creator:
            # await asyncio.sleep(7)
            await msg.edit(text, parse_mode=parse_mode)
        else:
            await app.send_message(msg.chat.id, text, disable_notification=False, parse_mode=parse_mode)

    @app.on_message(filters.command("replytype", prefixes=".") & filters.me)
    async def mat_handler(_, msg: Message):
        global reply_type
        try:
            reply_type = ReplyType(int(msg.command[1]))
            await set_or_update_setting_value('reply_type', msg.command[1])
            await msg.edit(f"reply_type = {reply_type.name}")
            await asyncio.sleep(2)
        except Exception as e:
            print("Failed to change a setting: " + str(e))

        await msg.delete()

    @app.on_message(my_filters.is_true(lambda _: mat_on) & my_filters.chats(mats_chat_messages) & my_filters.is_true(is_mat))
    async def on_mat_handler(client: Client, msg: Message):
        try:
            log_mat(msg.chat.type, msg)
        except Exception as e:
            # print(str(e))
            print("on_mat_handler Error")
        await reply_handler(client, msg, reply_type)
        await mat_stat_increase(msg)
