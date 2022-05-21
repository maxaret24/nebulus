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

-`.rm`
    __Delete a file existing locally__
'''

@userbot.on_message(
    filters.command(['dl','download'],prefixes=UB_PREFIXES) &
    filters.me &
    ~filters.via_bot
)
async def dldoc(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text('`Reply to a message with document/media to download`')
    try:
        name = message.command[1] if len(message.command) > 1 else None
        m = await message.edit_text('`Downloading...`')
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
            return await m.edit_text('`Download unsuccessful`')
        await m.edit_text(f'`Download successful`\n**Path:** `{path}`')
    except:
        await m.edit_text('`Something went wrong`')


@userbot.on_message(
    filters.command(['ul','upload'],prefixes=UB_PREFIXES) &
    filters.me &
    ~filters.via_bot
)
async def ul_(c: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text('`Please provide a file path`')
    path = (' '.join(message.command[1:])).strip()
    if not os.path.exists(path):
        return await message.reply_text('`The path provided doesn\'t exist`')
    a = await message.edit_text('`Uploading...`')
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
    ~filters.via_bot
)
async def read_(c: Client,m: Message):
    if not m.reply_to_message or not m.reply_to_message.document:
        return await m.edit_text('`Reply to a document to read its contents`')
    a = await m.reply_text('`Downloading...`')
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
            await a.edit_text(f'`{content}`')
    except:
        await a.edit_text(f'`Something went wrong`')
    os.remove(path)


@userbot.on_message(
    filters.command(['rm'],prefixes=UB_PREFIXES) &
    filters.me &
    ~filters.via_bot
)
async def rm_(c, m: Message):
    if len(m.command) != 2:
        return await m.reply_text('`Provide a file path to delete it`')
    path = m.command[1]
    if os.path.isfile(path):
        os.remove(path)
        text = f'**Deleted:** `{path}`'
    else:
        text = f'**Error:** `Bad file path`'
    await m.reply_text(text)

