from time import sleep
import random
from operator import itemgetter, attrgetter

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message


def other_controller(app):
    @app.on_message(filters.command("type", prefixes=".") & filters.me)
    async def type_handler(_, msg: Message):
        orig_text = msg.text.split(".type ", maxsplit=1)[1]
        text = orig_text
        tbp = ""
        typing_symbol = "-"

        while (tbp != orig_text):
            try:
                await msg.edit(tbp + typing_symbol)
                sleep(0.1)  # 50ms

                tbp = tbp + text[0]
                text = text[1:]

                await msg.edit(tbp)
                sleep(0.1)

            except FloodWait as e:
                sleep(e.x)

        perc = 0


    @app.on_message(filters.command("hack", prefixes=".") & filters.me)
    async def hack_handler(_, msg: Message):
        perc = 0

        while (perc < 100):
            try:
                text = " Взлом пентагона в процессе ..." + str(perc)
                await msg.edit(text)

                perc += random.randint(1, 3)
                sleep(0.1)

            except FloodWait as e:
                sleep(e.x)

        await msg.edit("Пентагон успешно взломан!")
        sleep(3)

        await msg.edit("Поиск секретных данных об НЛО ...")
        sleep(1)

        perc = 0

        while (perc < 100):
            try:
                text = " Взлом секретных данных об НЛО ..." + str(perc)
                await msg.edit(text)

                perc += random.randint(1, 3)
                sleep(0.1)

            except FloodWait as e:
                sleep(e.x)

        await msg.edit("Найдены данные о существовании динозавров на земле!")


    @app.on_message(filters.command("unicode", prefixes=".") & filters.me)
    async def unicode_handler(_, msg: Message):
        for member in app.iter_chat_members("Mylol"):
            if member.user.is_deleted:
                continue
            x = member.user.first_name
            y = member.user.first_name.encode().decode("ascii", "ignore")
            if x != y:
                print(f"{x}\t|\t{y}")


    @app.on_message(filters.command("lol", prefixes=".") & filters.me)
    async def func(_, msg: Message):
        await msg.delete()
        msgs = [(msg.message_id, msg.text) for msg in sorted(app.iter_history(msg.chat.id), key=attrgetter('date'))]
        # msgs.sort(key=itemgetter(0))
        print(msgs)

    @app.on_message(filters.command("chat_id", prefixes=".") & filters.me)
    async def func232(_, msg: Message):
        print(msg.chat.id)
        await msg.delete()

    @app.on_message(filters.command("debug", prefixes="."))
    async def func232(_, msg: Message):
        print(msg.chat.id)
        # await msg.delete()
