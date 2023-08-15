import asyncio
import calendar
import random
import re
import time
from datetime import datetime, timezone, date
from functools import reduce
from itertools import islice

from dateutil.relativedelta import relativedelta
from pyrogram import Client
from pyrogram.types import Message

from models.enums.reply_type import ReplyType
from services.datetime_service import get_unix_date
from settings_provider import mat_stat_increase_item, get_mat_stat_chats, get_mat_stat_all, mat_stat_init_if_not_exists, \
    get_mat_stat_by_chat_id_and_date


is_replied_message = False

warnings = [
    "Не выражаться!!! :)",
    "Я запрещаю вам материться!!! :)",
    "Сколько уже можно материться!!! :)",
    "Пожалуйста, хватит так матюкаться :)))",
    "Нецензурные выражения – угроза для нации",
    "Старайтесь не использовать ненормативную лексику",
    "Некрасиво материться"
]

patterns = [
    'су+(к|чк|ча+р|че+к)', 'пид[оа]+р(а+с)?([аы]|о+в)?', 'у[её]б(к|очк)?([аы]|ов|ище)?',
    'еба(ть|л)', 'еби', 'еб(ан)?(ут|еш|ёш|уч)', 'в[ыьъ]еб([аеиу])', 'д[оа]лб[оа][её]б', r'(?<!ру)(?<!влю)бля',
    'ху(([йя]|ита)|([её]([кв]|(чек)|т))|(йн([её]й|ей)?))', r'(на)?хер', 'пизд([аà]|е|ят)', 'gghh'
]
compiled_patterns = [re.compile(p, re.IGNORECASE | re.MULTILINE) for p in patterns]
_re_step1 = re.compile(r"[^а-яА-ЯёЁ]+")
_re_step2 = re.compile(r"(.)\1+")
_re_except_symbols = re.compile(r"[🇷🇺🇺🇦]+")

replace_maps = [
    (('x', 'X'), 'х'),
    (('c', 'C'), 'с'),
    (('a', 'A'), 'а'),
    (('y', 'Y'), 'у'),
    (('x', 'X'), 'х'),
    (('k', 'K'), 'к'),
    (('Р',), 'Р'),
    (('H',), 'Н'),
    (('B',), 'В'),
    (('t', 'T'), 'т'),
]


def is_mat(msg: Message):
    text = msg.text if msg.text is not None else ''

    text = reduce(
        lambda text, pattern: reduce(lambda t, w: t.replace(w, pattern[1]), pattern[0], text),
        replace_maps,
        text)

    text = _re_step1.sub('', text)
    text = _re_step2.sub(r'\1', text)

    match_groups = [[*pattern.finditer(text)] for pattern in compiled_patterns]
    mat_count = sum([len(matches) for matches in match_groups])

    setattr(msg, 'mat_count', mat_count)

    return mat_count > 0


def get_random_warning():
    return random.choice(warnings)


async def mat_stat_increase(msg: Message):
    if msg.from_user is not None:
        who_id = msg.from_user.id
        first_name = msg.from_user.first_name
        last_name = msg.from_user.last_name
        username = msg.from_user.username
    else:
        who_id = msg.sender_chat.id
        first_name = msg.sender_chat.title
        last_name = None
        username = msg.sender_chat.username
    await mat_stat_init_if_not_exists(msg.chat.id, who_id, username, first_name, last_name)
    unix_time = calendar.timegm(datetime.today().date().timetuple())
    await mat_stat_increase_item(msg.chat.id, who_id, unix_time, msg.mat_count)


async def reply_handler(client: Client, msg: Message, reply_type: ReplyType):
    global is_replied_message

    if reply_type in (ReplyType.reaction, ReplyType.reactionTemp):
        full_chat = await client.get_chat(msg.chat.id)
        available_reactions = full_chat.available_reactions or ['🤬']
        try:
            await client.send_reaction(msg.chat.id, msg.id, available_reactions[-1])  # 🤬 👍
            if reply_type == ReplyType.reactionTemp:
                await asyncio.sleep(10)
                await client.send_reaction(msg.chat.id, msg.id, '')
        except Exception:
            pass
    elif reply_type == ReplyType.message:
        if not is_replied_message:
            msg2 = await mat_reply(client, msg)
            is_replied_message = True
            await asyncio.sleep(2)
            is_replied_message = False
            await msg2.delete()


async def mat_reply(client: Client, msg: Message):
    if msg.reply_to_message is not None and msg.reply_to_message.forward_from_chat is not None:
        disc_message = await client.get_discussion_message(msg.reply_to_message.forward_from_chat.id,
                                                           msg.reply_to_message.forward_from_message_id)
        reply_to_message_id = disc_message.id
        return await disc_message.reply(get_random_warning(), reply_to_message_id=reply_to_message_id,
                                        disable_notification=True, parse_mode=None)
    else:
        return await client.send_message(msg.chat.id, get_random_warning(),
                                         disable_notification=True, parse_mode=None)


async def get_matstat_result(chat_id: int = None, days: int = None, is_get_link_username: bool = None):
    utc_time = datetime.today().date() - relativedelta(days=days - 1)
    unix_time = get_unix_date(utc_time)
    mat_stats = await get_mat_stat_by_chat_id_and_date(chat_id, unix_time)

    word = ''
    if days == 30:
        word = 'месяц'
    elif days in (11, 12, 13, 14):
        word = f'{days} дней'
    elif days % 10 == 1:
        word = 'день'
    elif days % 10 in (2, 3, 4):
        word = f'{days} дня'
    else:
        word = f'{days} дней'

    text = f'Cтатистика количества мата за {word}\n\n'
    for mat_stat in islice(mat_stats, 10 if days < 30 else 20):
        try:
            if is_get_link_username:
                text += f'{mat_stat.firstname} {(mat_stat.username and "@" + mat_stat.username) or mat_stat.lastname or ""} = {mat_stat.count}\n'
            else:
                text += f'{mat_stat.firstname} {mat_stat.lastname or mat_stat.username or ""} = {mat_stat.count}\n'
            if days >= 30 and mat_stat.count < 10:
                break
        except Exception as e:
            print(f"error mat_stat_show: {mat_stat.chat_id}")
    text += '...'
    text = _re_except_symbols.sub('.', text)
    print(text)
    return text
    # print(text, end='\n\n')



async def mat_stat_show_all(app: Client, user_id: int = None):
    chats = await get_mat_stat_chats()

    date = datetime.today().date()

    for chat_id in chats:
        text = await get_matstat_result(app, chat_id, date)
        await app.send_message(chat_id, text, disable_notification=False)



async def mat_stat_notify(app: Client):
    chats = await get_mat_stat_chats(get_unix_date())
    for chat_id in chats:
        try:
            await app.send_message(chat_id, """Что-бы узнать статистику мата за день, напишите .matstat""")
        except Exception as e:
            print(f"mat_stat_notify error: chat_id={chat_id}")
