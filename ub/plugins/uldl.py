from .. import *
from pyrogram.types import Message
from pyrogram import Client, filters
import os,aiofiles

NAME = 'Files'
WIKI = '''
💢 **Module**: `Files`

Manage Files

**Commands**

-`.dl|.download`
    __(Reply to a document) Downloads it__

-`.ul|.upload FILE`
    __Uploads document. Provide file path__

-`.read`
    __Read a file and upload content to telegram__
'''

@userbot.on_message(
    filters.command(['dl','download'],prefixes=UB_PREFIXES) &
    filters.me &
    ~filters.via_bot &
    ~filters.edited
)
async def dldoc(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text('`Reply to a message with document/media to download`','md')
    try:
        name = message.command[1] if len(message.command) > 1 else None
        m = await message.edit_text('`Downloading...`','md')
        if name:
            path = await message.reply_to_message.download(
                name,
                progress=progress,
                progress_args=('Downloading...',m)
            )
        else:
            path = await message.reply_to_message.download(
                progress=progress,
                progress_args=('Downloading...',m)
            )
        if not path:
            return await m.edit_text('`Download unsuccessful`','md')
        await m.edit_text(f'`Download successful`\n**Path:** `{path}`','md')
    except:
        await m.edit_text('`Something went wrong`','md')


@userbot.on_message(
    filters.command(['ul','upload'],prefixes=UB_PREFIXES) &
    filters.me &
    ~filters.via_bot &
    ~filters.edited
)
async def ul_(c: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text('`Please provide a file path`','md')
    path = (' '.join(message.command[1:])).strip()
    if not os.path.exists(path):
        return await message.reply_text('`The path provided doesn\'t exist`','md')
    a = await message.edit_text('`Uploading...`','md')
    await c.send_document(
        message.chat.id,
        path,
        progress=progress,
        progress_args=('Uploading...',a)
    )
    await a.delete()


@userbot.on_message(
    filters.command(['read'],prefixes=UB_PREFIXES) &
    filters.me &
    ~filters.via_bot &
    ~filters.edited
)
async def read_(c: Client,m: Message):
    if not m.reply_to_message or not m.reply_to_message.document:
        return await m.edit_text('`Reply to a document to read its contents`','md')
    a = await m.reply_text('`Downloading...`','md')
    path = await m.reply_to_message.download()
    try:
        async with aiofiles.open(path,'r') as f:
            content = await f.read()
        if len(content) > 4096:
            splitted = content.splitlines()
            htmltext = '<br>'.join(splitted)
            page = graph.create_page('File Content',html_content=f'<code>{htmltext}</code>')
            url = page['url']
            await a.edit_text(f'File Contents: {url}',disable_web_page_preview=True)
        else:
            await a.edit_text(f'`{content}`','md')
    except:
        await a.edit_text(f'`Something went wrong`','md')
    os.remove(path)
