from .. import *
from pyrogram import Client,filters
from pyrogram.types import Message
import subprocess
from pyrogram.types import Message

# Some gay handlers

@userbot.on_message(
    filters.command('alive',prefixes=UB_PREFIXES) & filters.me
    )
async def alive_msg(client,message: Message):
    msg='''
**Nebulus Userbot**

**Status**: `Running`
    '''
    inf = sys_info()
    msg += inf
    await message.edit_text(msg,disable_web_page_preview=True)


@userbot.on_message(
    filters.command('restart',prefixes=UB_PREFIXES) &
    filters.me
)
async def rest(client,message):
    m = await message.edit_text('`Restarting slave bot and userbot, please wait...`')
    restart(message=m)

@userbot.on_message(
    filters.command('help',prefixes=UB_PREFIXES) &
    filters.me
)
async def sendHelp(client: Client,message: Message):
    if len(message.command) != 2:
        results = await client.get_inline_bot_results(SLAVE_USERNAME,'help')
    else:
        module = message.command[1]
        results = await client.get_inline_bot_results(SLAVE_USERNAME,f'hm:{module}')
    await client.send_inline_bot_result(
            chat_id=message.chat.id,
            query_id=results.query_id,
            result_id=results.results[0].id
    )
