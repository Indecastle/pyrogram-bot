import os, datetime

from pyrogram.types import Message


os.environ["PYTHONIOENCODING"] = "UTF-8"
os.environ["PYTHONUNBUFFERED"] = "1"
# print('- ' + (os.getenv('PYTHONIOENCODING') or ''))
# print('- ' + (os.getenv('PYTHONUNBUFFERED') or ''))


def get_time():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def log_mat(chat_type: str, message: Message):


    if chat_type in ('channel', 'supergroup', 'group'):
        if message.reply_to_message is not None and message.reply_to_message.forward_from_chat is not None:
            title = message.reply_to_message.forward_from_chat.title
            chat_type = 'channel'

        elif message.chat.title is not None:
            title = message.chat.title
        else:
            title = message.reply_to_message.sender_chat.title

        if message.from_user is not None:
            name = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}"
            who = 'user'
        else:
            name = f"{message.sender_chat.title or ''} {message.sender_chat.username or ''}"
            who = 'channel'
        # localtime = get_time()
        # print(f'{localtime}: In {chat_type}: "{title or ""}", by {who or ""}: "{name or ""}", start reply to message with text: "{message.text or ""}"')
        print("{0}: In {1}: '{2}', by {3}: '{4}', sent message with curse words: '{5}'"
              .format(get_time(),
                      chat_type,
                      title or "",
                      who or "",
                      name or "",
                      message.text or ""))
    elif chat_type == 'group':
        title = message.chat.title
    elif chat_type == 'private':
        title = message.chat.title
        print(f'{get_time()}: at user "{title}", sent message with curse words: "{message.text}" ')


