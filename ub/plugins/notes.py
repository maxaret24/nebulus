from pyrogram import Client,filters
from pyrogram.types import Message
from .. import UB_PREFIXES,userbot
from ..core.db import *
import io

NAME = 'Notes'

WIKI = '''
💢 **Module: ** `Notes`

Save messages as notes

**Commands**

-`.save NOTENAME`
    __Saves a note__

-`.get NOTENAME`
    __Gets a saved note__

-`.delnote NOTENAME`
    __Deletes a note__

-`.notes`
    __Lists out saved notes__
'''



@userbot.on_message(
    filters.command('save',prefixes=UB_PREFIXES) &
    filters.me &
    ~filters.via_bot
)
async def savenote(client,message: Message):
    if not message.reply_to_message:
        return await message.reply_text('`Reply to a message to save it`')
    splitted = message.command
    if len(splitted) != 2:
        return await message.reply_text('`Provide a notename to save it`')
    notename = splitted[1].lower().strip()
    rep = message.reply_to_message
    if rep.video:
        data = f'video:{rep.video.file_id}'
    elif rep.audio:
        data = f'audio:{rep.audio.file_id}'
    elif rep.photo:
        data = f'photo:{rep.photo.file_id}'
    elif rep.document:
        data = f'document:{rep.document.file_id}'
    elif rep.sticker:
        data = f'sticker:{rep.sticker.file_id}'
    elif rep.text:
        data = f'text:{rep.text.markdown}'
    else:
        return await message.reply_text('`Couldn\'t save note, invalid data type`')
    await save_note(notename,data)
    await message.reply_text(f'**Saved note:** `{notename}`')



@userbot.on_message(
    filters.command('notes',prefixes=UB_PREFIXES) &
    filters.me &
    ~filters.via_bot
)
async def getnotes(client,message: Message):
    notes = await get_notes()
    if not notes:
        return await message.reply_text('`There are no saved notes`')
    text='**List of saved notes:**\n'
    for x in notes:
        text+=f'-`{x}\n`'
    if len(text) > 4096:
        file = io.BytesIO(text.encode('utf-8'))
        file.name = 'Notes.txt'
        await message.reply_document(file); return
    await message.reply_text(text)



@userbot.on_message(
    filters.command('get',prefixes=UB_PREFIXES) &
    filters.me &
    ~filters.via_bot
)
async def getnote(client: Client,message: Message):
    splitted = message.command
    if len(splitted) != 2:
        return await message.reply_text('`Please provide a Notename`')
    notename = splitted[1].lower().strip()
    data = await get_a_note(notename)
    if not data:
        return await message.reply_text(f'**Note** `{notename}` **not found**')
    ds = data.split(':')
    tpe = ds[0] # note type
    meta = ':'.join(ds[1:])

    if tpe == 'video':
        await message.reply_video(meta,caption=f'**Note:** `{notename}`\n')
    elif tpe == 'audio':
        await message.reply_audio(meta,caption=f'**Note:** `{notename}`\n')
    elif tpe == 'sticker':
        await message.reply_sticker(meta)
    elif tpe == 'photo':
        await message.reply_photo(meta,caption=f'**Note:** `{notename}`\n')
    elif tpe == 'text':
        msg = f'**Note:** `{notename}`\n'
        msg += meta
        await message.reply_text(msg)
    elif tpe == 'document':
        await message.reply_document(meta,caption=f'**Note:** `{notename}`\n')



@userbot.on_message(
    filters.command('delnote',prefixes=UB_PREFIXES) &
    filters.me &
    ~filters.via_bot
)
async def delete_note(c,m: Message):
    if len(m.command) != 2:
        return await m.reply_text('`Please provide a notename`')
    notename = m.command[1]
    resp = await del_note(notename)
    if resp:
        await m.reply_text(f'**Note** `{notename}` **deleted**')
    else:
        await m.reply_text(f'**Note** `{notename}` **doesn\'t exist**')