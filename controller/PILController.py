from time import sleep
import random, io, os
from operator import itemgetter, attrgetter
import textwrap

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message
from PIL import Image, ImageDraw, ImageFont

font_text = ImageFont.truetype("fonts/MarckScript-Regular.ttf", 50, encoding='UTF-8')
WIDTH = 40
MARGIN = 5, 2


def get_size(lines, font_text):
    width = max(font_text.getsize(line)[0] for line in lines) + 2 * MARGIN[0]
    height = sum(font_text.getsize(line)[1] for line in lines) + 2 * MARGIN[1]
    return width, height


def get_image(text, message_id):
    lines = textwrap.wrap(text, width=WIDTH)
    size = get_size(lines, font_text)

    image = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(image)

    offset_y = 0  # margin[1]
    for line in lines:
        draw.text((MARGIN[0], offset_y), line, font=font_text, fill="black")
        offset_y += font_text.getsize(line)[1]

    image_filename = f"temp/{message_id}.png"
    f = io.BytesIO()
    # setattr(buffer, 'name', 'temp')
    image.save(f, format='PNG')
    # f.seek(io.SEEK_SET)

    return f


def pil_controller(app):
    @app.on_message(filters.command("", prefixes=",") & filters.me)
    def type_handler(client: Client, msg: Message):
        msg.delete()
        orig_text = msg.text.split(" ", maxsplit=1)[1]

        with get_image(orig_text, msg.message_id) as f:
            client.send_photo(msg.chat.id, f)

        # os.remove(image_filename)
