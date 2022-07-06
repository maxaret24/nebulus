from .. import (
    userbot,
    UB_PREFIXES,
    SLAVE_USERNAME,
    client_session
    )
from pyrogram import Client,filters
from pyrogram.types import Message
from datetime import datetime
import asyncio
from deep_translator import GoogleTranslator
from ..core.decorators import log_errors
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from random import choice

NAME = "Tools"

WIKI = '''
💢 **Module**: `Tools`

-`.alive`
    __Checks bot status__

-`.restart`
    __Restarts Nebulus[Also checks for updates]__

-`.ping`
    __Checks bot response time__

-`.translate|.tr LANG`
    __Translate to a specified language(Default: EN), Reply to a message to translate__

-`.reserve @username`
    __Reserve a username__

-`.ud WORD`
    __Get the meaning of a word from UrbanDictionary__

-`.gsearch QUERY`
    __Search Google__
'''



@userbot.on_message(
    filters.command("ping",prefixes=UB_PREFIXES) &
    filters.me
)
async def pong(client,message):
    s = datetime.now()
    m = await message.edit_text('**🏓 Pong!**')
    e = datetime.now()
    tm = round((e-s).microseconds/1000,1)
    await asyncio.sleep(0.8)
    await m.edit_text(f"**Pong : {tm} ms**")



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
        else:
            lang = "english"
        try:
            translated = GoogleTranslator(source="auto",target=lang).translate(text)
            await message.reply_text(f"**Translated to {lang}** : \n`{translated}`")
        except Exception as e:
            await message.reply_text(f"**Exception during translation :** `{e}`")
    else:
        await message.edit_text("`Reply to a message to translate`")



@userbot.on_message(
    filters.command('reserve',UB_PREFIXES) &
    filters.me
)
async def reserve(c: Client,m):
    if len(m.command) != 2:
        return await m.edit_text('`Provide a username to reserve it`')
    username = m.command[1].replace('@','').strip()
    try:
        chat = await userbot.create_channel('Reserved')
        await userbot.set_chat_username(chat_id=chat.id,username=username)
        await m.reply_text(f'**Reserved** @{username} **successfully**')
    except:
        await m.reply_text(f'**Couldn\'t reserve username**')
        await userbot.delete_channel(chat.id)
  

@userbot.on_message(
    filters.command('ud',prefixes=UB_PREFIXES) &
    filters.me
)
async def define(client: Client,message):
    splitted = message.command
    cid = message.chat.id
    if len(splitted) != 2 or splitted[1] == "":
        await message.reply_text("`A query is required to search UrbanDictionary.`")
    else:
        query = 'ud ' + splitted[1]
        results = await client.get_inline_bot_results(SLAVE_USERNAME,query)
        await client.send_inline_bot_result(
            cid,
            results.query_id,
            results.results[0].id
        )


@userbot.on_message(
    filters.command('gsearch',UB_PREFIXES) &
    filters.me
)
async def gsearch(c,m: Message):
    if len(m.command) < 2:
        return await m.reply_text('`Provide a query to search Google`')
    a = await m.edit_text('`Searching...`')
    query = ' '.join(m.command[1:])
    query = quote_plus(query)
    resp = await client_session.get('https://fake-useragent.herokuapp.com/browsers/0.1.11')
    json = await resp.json()
    header = {'User-Agent':choice(json['browsers']['chrome'])}
    rsp = await client_session.get('https://www.google.com/search?q=%s' % query,headers=header)
    data = await rsp.text()
    soup = BeautifulSoup(data,'html.parser')
    results = []
    for x in soup.find_all('div',{'class':'egMi0 kCrYT'}):
        href = x.a['href'].split('&')[4][4:]
        head = x.div.text
        results.append((head,href))
    if results == []:
        return await a.edit_text('`No results. Either due to bad query string or CAPTCHA.`')
    text='''
**Google Results**
'''
    for r in results:
        text+=f'\n\n`{r[0]}`\n{r[1]}'
    await a.edit_text(text,disable_web_page_preview=True)

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

