from typing import Any, Tuple
from pyrogram import types,filters
import os,secrets,logging
from .. import (
    slave_bot,
    USERBOT_ID,
    progress,
    userbot
)
from pytube import YouTube


streamdict = {}

def rmfile(filename):
    if os.path.exists(filename):
        os.remove(filename)

def genkeyboard(sid,streams,typ,chatid):
    kb=[]
    streams = list(streams)
    while len(streams) != 0:
        lel=[]
        for x in streams[:3]:
            lel.append(types.InlineKeyboardButton(
                text=f'{round(x.filesize/10**6,2)}MB' if typ=='audio' else f'{x.resolution}'
                ,callback_data=f'{sid}|{x.itag}|{chatid}'))
            streams.remove(x)
        kb.append(lel)
    return types.InlineKeyboardMarkup(kb)

def get_streams(link,type) -> Tuple[int,Any,Any]:
    p = YouTube(link)
    if type == 'video':
        streams = p.streams.filter(type='video',progressive=True)
    else:
        streams = p.streams.filter(type='audio',mime_type='audio/webm')
    sid = 0 if len(list(streamdict.keys())) == 0 else list(streamdict.keys())[-1] + 1
    streamdict[sid] = streams
    return sid,p

async def dvid(chatid,sid,itag,callback: types.CallbackQuery):
    await callback.edit_message_text(text=f'**Downloading...**',parse_mode='markdown')
    stream = streamdict[sid]
    vid = stream.get_by_itag(itag)
    n = secrets.token_hex(16)
    ext = 'mp4' if vid.type == 'video' else 'webm'
    filename = f'{n}.{ext}'
    logging.info(f'STREAM {itag} FETCHED')
    vid.download(output_path='videos/',filename=filename)
    logging.info('DOWNLOADED')
    try:
        if vid.type == 'video':
            await userbot.send_video(
            chat_id=chatid,
            video=f'videos/{filename}',
            caption=f'**Title:** {vid.title}\n**Resolution:** {vid.resolution}',
            supports_streaming=True,
            progress=progress,
            progress_args=('Uploading...',callback),
            file_name=vid.title
            )
        else:
            os.rename(f'videos/{filename}',f'videos/{n}.mp3')
            await callback.edit_message_text(text=f'**Uploading...**',parse_mode='markdown')
            await userbot.send_audio(
                chat_id=chatid,
                audio=f'videos/{n}.mp3',
                caption=f'**Title:** {vid.title}',
                file_name=vid.title
            )
        await callback.edit_message_text('**Uploaded successfully**','md')
    except Exception as e:
        await callback.edit_message_text(f'**Exception**\n`{e}`','md')
    rmfile(f'videos/{n}.mp3')
    rmfile(f'videos/{filename}')
    logging.info('VIDEO LOCALLY REMOVED')
    del streamdict[sid]


@slave_bot.on_inline_query(
    filters.regex('^yt[a-z]?\|.+\|.+')
)
async def ytv(c,query: types.InlineQuery):
    if query.from_user.id != USERBOT_ID:
        return
    res = query.matches[0].group().strip()
    typ = 'video' if res[2] == 'v' else 'audio'
    link = res.split('|')[1]
    chatid = int(res.split('|')[2])
    try:
        sid,ytobj = get_streams(link,typ)
        stream = streamdict[sid]
    except Exception as e:
        await query.answer(
            [
                types.InlineQueryResultArticle("error",
                types.InputTextMessageContent(f'**Exception:** `{e}`','md'))
            ],is_personal=True
        )
        return
    keyboard = genkeyboard(sid,stream,typ,chatid)
    await query.answer(
        [
            types.InlineQueryResultArticle(
                'result',
                types.InputTextMessageContent(
                    f'**Title:** {ytobj.title}\n**Author:** {ytobj.author}' \
                    if typ == 'video' else \
                        f'**Title:** {ytobj.title}\n\n**Choose a download filesize-**',
                        parse_mode='md'
                ),reply_markup=keyboard
            )
        ],is_personal=True
    )
    

@slave_bot.on_callback_query(
    filters.regex('\d+\|\d+\|[-]?.+\d$'),
)
async def dlvideo_(c,query: types.CallbackQuery):
    if query.from_user.id != USERBOT_ID:
        return await query.answer('Sorry, this button is not for you',cache_time=300)
    s = query.data.split('|')
    sid, itag, chatid = int(s[0]), int(s[1]), int(s[2])
    try:
        await dvid(chatid,sid,itag,query)
    except Exception as e:
        await query.edit_message_text(f'**Exception:** `{e}`','md')
