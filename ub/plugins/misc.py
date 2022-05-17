from .. import (
    userbot,
    UB_PREFIXES,
    SLAVE_USERNAME,
    )
from pyrogram import Client,filters
from pyrogram.types import Message
from datetime import datetime
import asyncio
from deep_translator import GoogleTranslator
from ..core.decorators import log_errors


NAME = "Tools"

WIKI = '''
💢 **Module**: `Tools`

-`.alive`
    __Checks bot status__

-`.ping`
    __Checks bot response time__

-`.translate|.tr LANG`
    __Translate to a specified language(Default: EN), Reply to a message to translate__

-`.reserve @username`
    __Reserve a username__

-`.ud WORD`
    __Get the meaning of a word from UrbanDictionary__
'''



@userbot.on_message(
    filters.command("ping",prefixes=UB_PREFIXES) &
    filters.me
)
async def pong(client,message):
    s = datetime.now()
    m = await message.edit_text('**🏓 Pong!**','md')
    e = datetime.now()
    tm = round((e-s).microseconds/1000,1)
    await asyncio.sleep(0.8)
    await m.edit_text(f"**Pong : {tm} ms**",'md')



@userbot.on_message(
        filters.command(["translate","tr"],prefixes=UB_PREFIXES) &
        filters.me
)
async def trans(client,message):
    if message.reply_to_message:
        print(message.text.split(" "))
        text = message.reply_to_message.text.strip()
        if len(message.text.split(" ")) == 2:
            lang = message.text.split(" ")[1]
        else:lang = "english"
        try:
            translated = GoogleTranslator(source="auto",target=lang).translate(text)
            await message.reply_text(f"**Translated to {lang}** : \n`{translated}`",'md')
        except Exception as e:
            await message.reply_text(f"**Exception during translation :** `{e}`",'md')
    else:
        await message.edit_text("`Reply to a message to translate`",'md')



@userbot.on_message(
    filters.command('reserve',UB_PREFIXES) &
    filters.me & ~filters.edited
)
async def reserve(c: Client,m):
    if len(m.command) != 2:
        return await m.edit_text('`Provide a username to reserve it`','md')
    username = m.command[1].replace('@','').strip()
    try:
        chat = await userbot.create_channel('Reserved')
        await userbot.update_chat_username(chat_id=chat.id,username=username)
        await m.reply_text(f'**Reserved** @{username} **successfully**','md')
    except:
        await m.reply_text(f'**Couldn\'t reserve username**','md')
        try:await userbot.delete_channel(chat.id)
        except:pass
  

@userbot.on_message(
    filters.command('ud',prefixes=UB_PREFIXES) &
    filters.me
)
async def define(client: Client,message):
    splitted = message.command
    cid = message.chat.id
    if len(splitted) != 2 or splitted[1] == "":
        await message.reply_text("`A query is required to search UrbanDictionary.`",'md')
    else:
        query = 'ud ' + splitted[1]
        results = await client.get_inline_bot_results(SLAVE_USERNAME,query)
        await client.send_inline_bot_result(
            cid,
            results.query_id,
            results.results[0].id
        )

'''
async def get_sticker(client: Client,chat,messages: list):
    resp = None #TODO: Add a replacement of ARQ for quotly
    if resp.ok:
        sticker = resp.result
        sio = BytesIO(sticker)
        sio.name='sticker.webp'
        await client.send_sticker(chat_id=chat,sticker=sio)
    else:await client.send_message(chat,'`Oops! Something went wrong`','md')


@userbot.on_message(
    filters.command('q',prefixes=UB_PREFIXES) &
    filters.me &
    ~filters.edited &
    ~filters.via_bot
)
@log_errors
async def respond(client: Client, message: Message):
    repliedmsg = message.reply_to_message
    if not repliedmsg:
        return await message.edit_text('`Reply to a message to quote`')
    if repliedmsg.media or repliedmsg.empty:
        return await message.edit_text('`You can quote only text messages`')
    if len(message.command) == 1:
        a=await message.edit_text('`Quoting message...`','md')
        msgs = [repliedmsg]
    elif message.command[1] == 'r':
        a=await message.edit_text('`Quoting messages...`','md')
        rmsgs = await client.get_messages(
            message.chat.id,
            repliedmsg.message_id,
            1)
        msgs = [rmsgs]
    elif message.command[1].isdigit():
        a=await message.edit_text('`Quoting messages...`','md')
        msgids = [*range(
            repliedmsg.message_id,
            repliedmsg.message_id + int(message.command[1])
        )]
        msgs = [
            m for m in await client.get_messages(
                message.chat.id,
                msgids,replies=0
            )
            if not m.empty and not m.media
        ]
    else:
        return await message.edit('Invalid argument provided. Use `.help Misc` for help.')
    try:
        await get_sticker(client,a.chat.id,msgs)
        await a.delete()
    except:
        await a.edit_text('`Something went wrong in quoting messages.`','md')

'''

