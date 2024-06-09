import asyncio
import calendar
import datetime
from time import sleep
import random
import sys
from pprint import pprint
from collections import OrderedDict
from typing import Union

import pickledb
from dateutil.relativedelta import relativedelta
from pyrogram.enums import ChatType
from pyrogram.raw.functions.messages import GetAvailableReactions
from tabulate import tabulate

from pyrogram import Client, filters, utils

from services.datetime_service import get_unix_date
from settings_provider import get_mat_stat_by_chat_id_and_date
from config import api_id, api_hash

max_title_string = 50

loop = asyncio.get_event_loop()


def members(dialogs):
    ar2 = list(filter(lambda x: x.chat.type == ChatType.PRIVATE, dialogs))
    ar3 = list(map(lambda x: OrderedDict(id=x.chat.id, first_name=x.chat.first_name, last_name=x.chat.last_name,
                                         username=x.chat.username), ar2))
    with open('dialogs/members.txt', 'w', encoding="utf-8") as f:
        # print(*ar3, sep='\n', file=f)
        print(tabulate(ar3, headers='keys', tablefmt='pretty'), file=f)


def bots(dialogs):
    ar2 = list(filter(lambda x: x.chat.type == ChatType.BOT, dialogs))
    ar3 = list(map(lambda x: OrderedDict(id=x.chat.id, first_name=x.chat.first_name, last_name=x.chat.last_name,
                                         username=x.chat.username), ar2))
    with open('dialogs/bots.txt', 'w', encoding="utf-8") as f:
        # print(*ar3, sep='\n', file=f)
        print(tabulate(ar3, headers='keys', tablefmt='pretty'), file=f)


def groups(dialogs):
    ar2 = list(filter(lambda x: x.chat.type == ChatType.GROUP, dialogs))
    ar3 = list(
        map(lambda x: OrderedDict(id=x.chat.id, title=x.chat.title[:max_title_string], username=x.chat.username), ar2))
    with open('dialogs/groups.txt', 'w', encoding="utf-8") as f:
        # print(*ar3, sep='\n', file=f)
        print(tabulate(ar3, headers='keys', tablefmt='pretty'), file=f)


def supergroups(dialogs):
    ar2 = list(filter(lambda x: x.chat.type == ChatType.SUPERGROUP, dialogs))
    ar3 = list(
        map(lambda x: OrderedDict(id=x.chat.id, title=x.chat.title[:max_title_string], username=x.chat.username), ar2))
    with open('dialogs/supergroups.txt', 'w', encoding="utf-8") as f:
        # print(*ar3, sep='\n', file=f)
        print(tabulate(ar3, headers='keys', tablefmt='pretty'), file=f)


def channels(dialogs):
    ar2 = list(filter(lambda x: x.chat.type == ChatType.CHANNEL, dialogs))
    ar3 = list(
        map(lambda x: OrderedDict(id=x.chat.id, title=x.chat.title[:max_title_string], username=x.chat.username), ar2))
    with open('dialogs/channels.txt', 'w', encoding="utf-8") as f:
        # print(*ar3, sep='\n', file=f)
        print(tabulate(ar3, headers='keys', tablefmt='pretty'), file=f)


async def save_dialogs(app: Client):
    dialogs = [item async for item in app.get_dialogs()]
    members(dialogs)
    bots(dialogs)
    groups(dialogs)
    supergroups(dialogs)
    channels(dialogs)


async def me(app):
    pprint(await app.get_me())
    # id = 424269317


async def test1(app: Client):
    chat_id = -1001322601787
    posts = await app.get_chat_history(chat_id)
    disc_mes = await app.get_discussion_message(chat_id, posts[1].message_id)
    print(disc_mes)


async def test2(app: Client):
    chat_id = -1001790121117
    chat = await app.get_chat(chat_id)
    reactions = await app.invoke(
            GetAvailableReactions(
                hash=0,
            ),
            sleep_threshold=60
        )
    print(chat)


async def async_main(app: Client):
    await save_dialogs(app)
    # await test1(app)
    # await test2(app)
    # await me(app)
    # await channel_comment_test(app)
    # await mat_stat_show_all(app)

    utc_time = datetime.datetime.today().date() - relativedelta(days=356 - 1)
    unix_time = get_unix_date(utc_time)
    mat_stats = await get_mat_stat_by_chat_id_and_date(-1001428293909, unix_time)
    users = [item async for item in app.get_chat_members(-1001706794006)]


    print("end - " + str(app.is_connected))


def main():
    app: Client = Client("my_account", api_id=api_id, api_hash=api_hash)

    with app:
        loop.run_until_complete(async_main(app))
        # asyncio.run(async_main(app))


# def kek():
#     import asyncio
#     import random
#
#     async def coro(tag):
#         print(">", tag)
#         await asyncio.sleep(random.uniform(0.5, 5))
#         print("<", tag)
#         return tag
#
#     loop = asyncio.get_event_loop()
#
#     tasks = [coro(i) for i in range(1, 11)]
#
#     print("Get first result:")
#     finished, unfinished = loop.run_until_complete(
#         asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED))
#
#     for task in finished:
#         print(task.result())
#     print("unfinished:", len(unfinished))
#
#     print("Get more results in 2 seconds:")
#     finished2, unfinished2 = loop.run_until_complete(
#         asyncio.wait(unfinished, timeout=2))
#
#     for task in finished2:
#         print(task.result())
#     print("unfinished2:", len(unfinished2))
#
#     print("Get all other results:")
#     finished3, unfinished3 = loop.run_until_complete(asyncio.wait(unfinished2))
#
#     for task in finished3:
#         print(task.result())
#
#     loop.close()

def kek():
    x = random.randint(1, 10000)
    print(f"try: {x}")
    db1 = pickledb.load('test.db', False)
    db2 = pickledb.load('test.db', False)

    db1.set('key1', x)
    db1.dump()

    sleep(3)
    print(db2.get('key1'))


if __name__ == '__main__':
    # backgroundJobMain(app)
    main()
    # kek()

    # import datetime
    # import time
    #
    # # dt = datetime.datetime(2016, 2, 25, 23, 23)
    # date = datetime.datetime.today().date()
    # utc_time = calendar.timegm(date.timetuple())
    # print(utc_time)
    # print()
    # print("Unix Timestamp: ", utc_time)
    # print()