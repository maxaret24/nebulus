# Mostly kanged from tgytdl
# github.com/greplix/tgytdl
# Credits to myself ;)
from ub.core.decorators import log_errors
from .. import *
from pyrogram import filters,Client
from pyrogram.types import Message
import re


NAME = 'YouTube'

WIKI = '''
💢 **Module**: `YouTube`

Download YT videos and music

**Commands**

-`.ytvid VIDEO_LINK`
    __Reply to a message with URL or provide one to download video__

-`.ytaud VIDEO_LINK`
    __Reply to a message with URL or provide one to download audio-only YouTube vids__
'''


REGEX = re.compile(r'https?://(\S+\.)?\S+\.?be(\.\S+)?/(w\S+|s\S+/)?-?(\?v=)?\w+')


@userbot.on_message(
    filters.command('ytvid',UB_PREFIXES) &
    filters.me &
    ~filters.via_bot
)
@log_errors
async def ytvid_(c: Client, m: Message):
    if not m.reply_to_message and len(m.command) != 2:
        return await m.reply_text('`Reply to a URL or provide one to download YT video`')
    if m.reply_to_message:
        reg = REGEX.search(m.reply_to_message.text.strip())
    else:
        reg = REGEX.search(m.command[1].strip())
    if not reg:
        return await m.reply_text('`Make sure that you provide a valid URL`')
    url = reg.group()
    a = await m.edit_text('**Fetching information...**')
    result = await c.get_inline_bot_results(SLAVE_USERNAME,f'ytv|{url}|{m.chat.id}')
    await c.send_inline_bot_result(
        m.chat.id,
        result.query_id,
        result.results[0].id
    )
    await a.delete()

@userbot.on_message(
    filters.command('ytaud',UB_PREFIXES) &
    filters.me &
    ~filters.via_bot
)
@log_errors
async def ytaud_(c, m: Message):
    if not m.reply_to_message and len(m.command) != 2:
        return await m.reply_text('`Reply to a URL or provide one to download YT video`')
    if m.reply_to_message:
        reg = REGEX.search(m.reply_to_message.text.strip())
    else:
        reg = REGEX.search(m.command[1].strip())
    if not reg:
        return await m.reply_text('`Make sure that you provide a valid URL`')
    url = reg.group()
    a = await m.edit_text('**Fetching information...**')
    result = await c.get_inline_bot_results(SLAVE_USERNAME,f'yta|{url}|{m.chat.id}')
    await c.send_inline_bot_result(
        m.chat.id,
        result.query_id,
        result.results[0].id
    )
    await a.delete()
