import asyncio
import io
import time
import torch
import sounddevice as sd
import torchaudio

from pyrogram import Client, filters
from pyrogram.raw.functions.messages import GetAvailableReactions
from pyrogram.types import Message

import common
import my_filters
from models.enums.tts_speaker import TtsSpeaker

from settings_provider import set_or_update_setting_value, get_setting_value

language = 'ru'
model_id = 'ru_v3'
sample_rate = 48000  # 48000
speaker = 'aidar'  # aidar, baya, kseniya, xenia, random
put_accent = True
put_yo = True
device = torch.device('cpu')  # cpu или gpu

model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                          model='silero_tts',
                          language=language,
                          speaker=model_id)
model.to(device)


TTS_speaker = TtsSpeaker(get_setting_value("TTS_speaker", int) or TtsSpeaker.aidar)


def init_TTS_controller(app: Client):
    ...


def TTS_controller(app: Client):
    @app.on_message(filters.command("tspeaker", prefixes=".") & filters.me)
    async def mat_handler(_, msg: Message):
        global TTS_speaker
        try:
            cmd = msg.command[1]
            if cmd.isnumeric():
                TTS_speaker = TtsSpeaker(int(cmd))
            else:
                TTS_speaker = TtsSpeaker[cmd]
            await set_or_update_setting_value('TTS_speaker', TTS_speaker.value)
            await msg.edit(f"TTS_speaker = {TTS_speaker.name}")
            await asyncio.sleep(2)
        except Exception as e:
            print("Failed to change a setting: " + str(e))

        await msg.delete()


    @app.on_message(filters.command('', prefixes=['*', '**']) & filters.me)
    async def TTS_handler(client: Client, msg: Message):
        await msg.delete()

        pref, orig_text = msg.text.split(" ", maxsplit=1)
        if len(pref) == 2 and pref == '**':
            pref, sec_str, orig_text = msg.text.split(" ", maxsplit=2)
            seconds = int(sec_str) if sec_str.isnumeric() else 0
            slep = asyncio.sleep(seconds)
        else:
            slep = asyncio.sleep(0)

        audio = model.apply_tts(text=orig_text + "..",
                                speaker=TTS_speaker.name,
                                sample_rate=sample_rate,
                                put_accent=put_accent,
                                put_yo=put_yo)

        with io.BytesIO() as buffer_:
            setattr(buffer_, 'name', 'temp')
            torchaudio.save(buffer_,
                            audio.unsqueeze(0),
                            sample_rate=sample_rate,
                            format="wav")
            buffer_.seek(0)

            await slep
            await client.send_voice(msg.chat.id, buffer_, reply_to_message_id=msg.reply_to_message_id)


    @app.on_message(filters.command("", prefixes="###") & filters.me)
    async def TTS2_handler(client: Client, msg: Message):
        msg.chat.available_reactions = GetAvailableReactions
        await msg.delete()
        print(msg.text)
