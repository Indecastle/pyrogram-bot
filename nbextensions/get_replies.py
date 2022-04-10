from typing import Union

from pyrogram import Client, utils
from pyrogram.raw.functions.messages import GetReplies
from pyrogram.raw.types import UpdateMessageReactions


async def get_replies(app: Client, chat_id: Union[int, str], message_id: int, offset_id: int = 0, offset_date: int = 0,
                      add_offset: int = 0, limit: int = 100, max_id: int = 0, min_id: int = 0, hash: int = 0):
    messages = await utils.parse_messages(
        app,
        await app.send(
            GetReplies(
                peer=await app.resolve_peer(chat_id),
                msg_id=message_id,
                offset_id=offset_id,
                offset_date=offset_date,
                add_offset=add_offset,
                limit=limit,
                max_id=max_id,
                min_id=min_id,
                hash=hash,
            ),
            sleep_threshold=60
        )
    )
    return messages


# async def update_message_reactions(app: Client, chat_id: Union[int, str], message_id: int):
#     x = await app.send(
#         UpdateMessageReactions(
#             peer=await app.resolve_peer(chat_id),
#             msg_id=message_id,
#             reactions=[],
#         ),
#         sleep_threshold=60
#     )
