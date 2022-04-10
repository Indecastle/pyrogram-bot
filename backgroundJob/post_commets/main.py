import asyncio
import datetime
import time
from typing import Dict

from pyrogram import Client
from pyrogram.errors import MsgIdInvalid
from pyrogram.types import Message, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

from nbextensions.get_replies import get_replies
from services.logger_service import get_time, log_mat
from services.mats_service import is_mat, get_random_warning
from settings_provider import get_setting_value_async, set_setting_value


channels: Dict[int, dict] = {
    -1001322601787: {'name': 'ЧП'},
    -1001460007515: {'name': 'Плохие новости 18+'},
    -1001355046344: {'name': 'Ррп'},
}



is_enable = False


loop = asyncio.get_event_loop()


async def verify_enabling_service():
    while not is_enable:
        await asyncio.sleep(2)


async def check_enabling(app: Client):
    global is_enable
    while True:
        result = get_setting_value_async("is_enable_channel_mats", bool)
        is_enable = result if result is not None else False
        await asyncio.sleep(2)


async def channel_comment_get_valid_last_post(app: Client, channel: int):
    while True:
        await verify_enabling_service()
        # last_post_id = channels[channel].setdefault('last_post_id', -1)
        try:
            posts = await app.get_history(channel, limit=10)

            for post in posts:
                try:
                    disc_message = await app.get_discussion_message(channel, post.message_id)
                except MsgIdInvalid as e:
                    # channels[channel]['last_post_id'] = post.message_id
                    # print(get_time() + f": channel: {channels[channel]['name']}, post_id({post.message_id}) is invalid")
                    ...
                else:
                    channels[channel]['current_discussion_post_id'] = disc_message.message_id
                    channels[channel]['current_post_id'] = post.message_id
                    break

            await asyncio.sleep(5)
        except Exception as e:
            print(get_time() + f": channel: {channels[channel]['name']}, Exception: channel_comment_get_valid_last_post")


async def channel_comment_warning_mat(app: Client, channel: int, comment: Message):
    await comment.delete()
    log_mat('channel', comment)
    current_discussion_post_id = channels[channel].setdefault('current_discussion_post_id', -1)
    msg = await comment.reply(get_random_warning(), reply_to_message_id=current_discussion_post_id)
    # await asyncio.sleep(5)

    # print(f'end replied to message with text: "{comment.text}" ')


async def channel_comment_test(app: Client, channel: int):
    back1 = loop.create_task(channel_comment_get_valid_last_post(app, channel))

    while True:
        await verify_enabling_service()

        current_post_id = channels[channel].setdefault('current_post_id', -1)
        last_comment_id = channels[channel].setdefault('last_comment_id', -1)
        try:
            if current_post_id != -1:
                comments = await get_replies(app, chat_id=channel, message_id=current_post_id, limit=2)
                if len(comments) != 0 \
                        and last_comment_id != comments[0].message_id \
                        and is_mat(comments[0]):
                    channels[channel]['last_comment_id'] = comments[0].message_id
                    loop.create_task(channel_comment_warning_mat(app, channel, comments[0]))
            await asyncio.sleep(1)
        except Exception as e:
            print(get_time() + f" channel: {channels[channel]['name']} - Exception: channel_comment_test: {str(e)}")
            await asyncio.sleep(1)

    print("nice")
    await back1


async def post_comments_main(app):
    tasks = []
    tasks.extend(channel_comment_test(app, channel) for channel in channels.keys())
    tasks.append(check_enabling(app))

    await asyncio.gather(*tasks)
    # for coro in coros:
    #     await coro
    print("end - " + str(app.is_connected))
