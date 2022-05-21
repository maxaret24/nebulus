from sqlite3 import Timestamp
from typing import Tuple
from .. import *
from pyrogram import Client,filters
from asyncio import sleep
from ..core.decorators import *
from pyrogram.types import ChatPermissions,ChatPrivileges
from pyrogram.enums import ParseMode,ChatMembersFilter
from datetime import datetime, timedelta


NAME = 'Admins'

WIKI = f'''
💢 **Module:** `Admins`

Moderate groups with ease

**Commands**

-`.kick`
    __Kicks member(Reply to user or provide username/ID)__

-`.skick`
    __Silently kicks user__

-`.dkick`
    __Kicks user while deleting the user\'s message you replied to__

-`.ban`
    __Bans the user(Reply to user or provide username/ID)__

-`.sban`
    __Silently bans user__

-`.dban`
    __Bans user while deleting the replied-to message__

-`.tban INTEGER[h|m|d|w]`
    __Temporarily bans user(h:hours,m:minutes,d:days,w:weeks)__

-`.unban`
    __Unbans user(Reply to user or provide username/ID)__

-`.mute`
    __Mutes user(Reply to user to provide username/ID)__

-`.tmute INTEGER[h|m|d|w]`
    __Temporarily mutes user(h:hours,m:minutes,d:days,w:weeks)__

-`.smute`
    __Silently mutes user__

-`.dmute`
    __Mutes user while deleting the replied-to message__

-`.unmute`
    __Unmutes user__

-`.promote`
    __Promotes user__

-`.demote`
    __Demotes user__

-`.del`
    __Delete replied-to message__

-`.purge`
    __Purge messages from replied-to message__

-`.purge [n]`
    __Purge "n" messages from replied-to message__

-`.slowmode|.sm [off,10s,30s,60s,300s,900s,3600s]`
    __Set chat slow-mode__

-`.pin`
    __Pins message__

-`.lpin`
    __Pins message while notifying members__

-`.chatpic`
    __Reply to a photo or video to set as chat photo__

-`.chattitle TITLE`
    __Set a chat title__
'''

async def get_admins(client: Client,chat_id):
    admins = [x.user.id async for x in client.get_chat_members(chat_id,filter=ChatMembersFilter.ADMINISTRATORS)]
    return admins

def get_until_date(timing,mode):
    now = datetime.now()
    if mode == 'h':
        then = now + timedelta(hours=int(timing))
        m = 'hours'
    elif mode == 'm':
        then = now + timedelta(minutes=int(timing))
        m = 'minutes'
    elif mode == 'w':
        days = int(timing) * 7
        then = now + timedelta(days=days)
        m = 'weeks'
    else:
        then = now + timedelta(days=int(timing))
        m = 'days'
    return then,m

async def get_id_and_reason(message: Message) -> Tuple[int,str,str]:
    if message.reply_to_message:
        userid = message.reply_to_message.from_user.id or message.reply_to_message.sender_chat.id
        mention = message.reply_to_message.from_user.mention if \
            message.reply_to_message.from_user else message.reply_to_message.sender_chat.title
        reason = ' '.join(message.command[1:]) if len(message.command) > 1 \
            else 'None'
    else:
        useriden = message.command[1].strip()
        user = await userbot.get_users(useriden) if not \
            useriden.isdigit() else await userbot.get_users(int(useriden))
        mention,userid = user.mention, user.id
        reason = ' '.join(message.command[2:]) if len(message.command) > 2 \
            else 'None'
    return userid, mention, reason


@userbot.on_message(
    filters.command(['kick','dkick','skick'],prefixes=UB_PREFIXES) &
    filters.me &
    ~filters.private
)
@log_errors
@admin('can_restrict_members')
async def kick_member(client: Client, message: Message):

    if message.text[1] == 's': await message.delete()

    if not message.reply_to_message and len(message.command) == 1:
        return await message.reply_text('`Reply to a user or provide username to kick`')

    try:
        userid, mention, reason = await get_id_and_reason(message)
        if userid == message.chat.id:
            return await message.edit_text('`Error in resolving the user`')
    except:
        return await message.edit_text('`Error in resolving the user`','md')

    if userid in await get_admins(client, message.chat.id):
        return await message.reply_text('`Bad Request: The user you\'re trying to kick is an admin '+
        'or you\'re not using the cmd in a supergroup`')
    try:
        if message.reply_to_message and message.text[1] == 'd':
            await message.reply_to_message.delete()

        await message.chat.ban_member(userid)
        await message.reply_text(
            text=f'''
<b>👤 User:</b> {mention}
<b>⚙️ Action: 🚫 Kicked</b>
<b>🗒 Reason:</b> <code>{reason}</code>
''',parse_mode=ParseMode.HTML
        ) if message.text[1] != 's' else print(0)
        await sleep(1)
        await message.chat.unban_member(userid)
    except Exception as e:
        await message.edit_text(f'**Exception:** `{e}`')



@userbot.on_message(
   filters.command('chatpic',prefixes=UB_PREFIXES) &
    filters.me &
    ~filters.private 
)
@log_errors
@admin('can_change_info')
async def setpic_(c,m: Message):
    if not m.reply_to_message.photo:
        return await m.edit_text('`Reply to a photo to set as chatpic`')
    try:
        await m.edit_text('`Processing...`')
        pic = await m.reply_to_message.download(in_memory=True)
        await userbot.set_chat_photo(chat_id=m.chat.id,photo=pic)
        await m.edit_text('`Chatpic has been set successfully`')
    except Exception as e:
        await m.edit_text(f'**Exception:** `{e}`')



@userbot.on_message(
    filters.command('chattitle',prefixes=UB_PREFIXES) &
    filters.me &
    ~filters.private
)
@log_errors
@admin('can_change_info')
async def tit_(c,m: Message): # yes tit(didn't get a better name than this)
    if len(m.command) == 1:
        return await m.reply_text('`Provide a chat title`')
    title = ' '.join(m.command[1:])
    try:
        await m.chat.set_title(title)
        await m.reply_text(f'**Chat title changed to:** `{title}`')
    except:
        await m.reply_text('`Failed to set chat title`')



@userbot.on_message(
    filters.command(['ban','dban','sban'],prefixes=UB_PREFIXES) &
    filters.me &
    ~filters.private
)
@log_errors
@admin('can_restrict_members')
async def ban_(c,m: Message):
    if m.text[1] == 's': await m.delete()
    if not m.reply_to_message and len(m.command) == 1:
        return await m.reply_text('`Reply to a user or provide username to ban`')
    try:
        userid, mention, reason = await get_id_and_reason(m)
        if userid == m.chat.id:
            return await m.edit_text('`Error in resolving the user`')
    except:
        return await m.reply_text('`Error in resolving the user`')
    if userid in await get_admins(c,m.chat.id):
        return await m.reply_text('`Bad Request: The user you\'re trying to ban is an admin '+
        'or you\'re not using the cmd in a supergroup`')
    if m.reply_to_message and m.text[1] == 'd':
        await m.reply_to_message.delete()
    try:
        await m.chat.ban_member(userid)

        await m.reply_text(
            f'''
<b>👤 User:</b> {mention}
<b>⚙️ Action: 🚫 Banned</b>
<b>🗒 Reason:</b> <code>{reason}</code>
''', parse_mode=ParseMode.HTML) if m.text[1] != 's' else print(0)

    except Exception as e:
        await m.reply_text(f'**Exception:** `{e}`')



@userbot.on_message(filters.command('unban',UB_PREFIXES) &
    filters.me &
    ~filters.private
)
@log_errors
@admin('can_restrict_members')
async def unban_(c,m: Message):
    if not m.reply_to_message and len(m.command) == 1:
        return await m.reply_text('`Reply to a user or provide username to unban`')
    try:
        userid, mention, reason = await get_id_and_reason(m)
        if userid == m.chat.id:
            return await m.edit_text('`Error in resolving the user`')
    except:
        return await m.reply_text('`Error in resolving the user`')
    try:
        await m.chat.unban_member(userid)
        await m.reply_text(f'''
<b>👤 User:</b> {mention}
<b>⚙️ Action: ✅ Unbanned</b>
<b>🗒 Reason:</b> <code>{reason}</code>
''',parse_mode=ParseMode.HTML)
    except Exception as e:
        await m.reply_text(f'**Exception:** `{e}`')



@userbot.on_message(
    filters.command('tban',prefixes=UB_PREFIXES) &
    filters.me &
    ~filters.private
)
@log_errors
@admin('can_restrict_members')
async def tban_(c,m: Message):
    if not m.reply_to_message:
        return await m.reply_text('`Reply to a user to temp-ban`')
    try:
        userid = m.reply_to_message.from_user.id or m.reply_to_message.sender_chat.id
        if userid == m.chat.id:
            return await m.reply_text('`Error in resolving the user`')
        mention = m.reply_to_message.from_user.mention if \
            m.reply_to_message.from_user else m.reply_to_message.sender_chat.title
    except:
        return await m.reply_text('`Error in resolving the user`')
    if userid in await get_admins(c,m.chat.id):
        return await m.reply_text('`Bad Request: The user you\'re trying to ban is an admin '+
        'or you\'re not using the cmd in a supergroup`')
    if len(m.command) == 1:
        return await m.reply_text('`Provide a timing[h,m,d,w] to temp-ban`')
    timing = m.command[1]
    if timing[-1] not in ['m','h','d','w'] or not timing[:-1].isdigit():
        return await m.reply_text('`Invalid timing provided. Valid ones are- h: hours, m: minutes, d: days, w: weeks`')
    delta,duration = get_until_date(int(timing[:-1]),timing[-1])

    reason = ' '.join(m.command[2:]) if len(m.command) > 2 else 'None'
    try:
        await m.chat.ban_member(
            user_id=userid,
            until_date=delta
        )
        await m.reply_text(f'''
<b>👤 User:</b> {mention}
<b>⚙️ Action: 🚫 Temp-Banned</b>
<b>🕔 Duration:</b> {timing[:-1]} {duration}
<b>🗒 Reason:</b> <code>{reason}</code>
''',parse_mode=ParseMode.HTML)
    except Exception as e:
        await m.reply_text(f'**Exception:** `{e}`')



@userbot.on_message(
    filters.command(['mute','smute','dmute','tmute'],UB_PREFIXES) &
    filters.me &
    ~filters.private
)
@log_errors
@admin('can_restrict_members')
async def mute_(c,m: Message):
    if m.text[1] == 's':await m.delete()
    if not m.reply_to_message and len(m.command) == 1:
        return await m.reply_text('`Reply to a user or provide username to mute`')
    try:
        userid,mention,reason = await get_id_and_reason(m)
        if userid == m.chat.id:
            return await m.edit_text('`Error in resolving the user`')
    except:
        return await m.reply_text('`Error in resolving the user`')
    if userid in await get_admins(c,m.chat.id):
        return await m.reply_text('`Bad Request: The user you\'re trying to mute is an admin '+
        'or you\'re not using the cmd in a supergroup`')
    if m.text[1] == 'd':
        await m.reply_to_message.delete()
    try:
        if m.text[1] == 't':
            if reason == 'None':
                return await m.reply_text('`Provide a duration for temp-mute`')
            splitted = reason.split(' ')
            timing = splitted[0]
            if timing[-1] not in ['m','h','d','w'] or not timing[:-1].isdigit():
                return await m.reply_text('`Invalid timing provided. Valid ones are- h: hours, m: minutes, d: days, w: weeks`')
            delta,duration = get_until_date(int(timing[:-1]),timing[-1])
            reason = ' '.join(splitted[1:]) if len(splitted) > 1 else 'None' 
            await m.chat.restrict_member(
                userid,
                ChatPermissions(),
                delta
            )
            await m.reply_text(f'''
<b>👤 User:</b> {mention}
<b>⚙️ Action: 🔇 Temp-muted</b>
<b>🕔 Duration:</b> {timing[:-1]} {duration}
<b>🗒 Reason:</b> <code>{reason}</code>
''',parse_mode=ParseMode.HTML)
        else:
            await m.chat.restrict_member(
                userid,
                ChatPermissions()
            )
            await m.reply_text(f'''
<b>👤 User:</b> {mention}
<b>⚙️ Action: 🔇 Muted</b>
<b>🗒 Reason:</b> <code>{reason}</code>
''',parse_mode=ParseMode.HTML) if m.text[1] != 's' else print(0)
    except Exception as e:
        await m.reply_text(f'**Exception:** `{e}`')
    


@userbot.on_message(filters.command('unmute',UB_PREFIXES) &
    filters.me &
    ~filters.private
)
@log_errors
@admin('can_restrict_members')
async def unmute_(c,m: Message):
    if not m.reply_to_message and len(m.command) == 1:
        return await m.reply_text('`Reply to a user or provide username to unmute`')
    try:
        userid, mention, reason = await get_id_and_reason(m)
        if userid == m.chat.id:
            return await m.edit_text('`Error in resolving the user`')
    except:
        return await m.reply_text('`Error in resolving the user`')
    try:
        await m.chat.unban_member(userid)
        await m.reply_text(f'''
<b>👤 User:</b> {mention}
<b>⚙️ Action: 🔊 Unmuted</b>
<b>🗒 Reason:</b> <code>{reason}</code>
''',parse_mode=ParseMode.HTML)
    except Exception as e:
        await m.reply_text(f'**Exception:** `{e}`')


@userbot.on_message(filters.command(['promote'],UB_PREFIXES) &
    filters.me &
    ~filters.private
)
@log_errors
@admin('can_promote_members')
async def promote_(c,m: Message):
    if not m.reply_to_message and len(m.command) == 1:
        return await m.reply_text('`Reply to a user or provide username to promote`')
    try:
        userid, mention, title = await get_id_and_reason(m)
        if userid == m.chat.id:
            return await m.reply_text('`Error in resolving the user`')
    except:
        return await m.reply_text('`Error in resolving the user`')
    try:
        await m.chat.promote_member(
            userid,
            ChatPrivileges(
            can_change_info=True,
            can_invite_users=True,
            can_delete_messages=True,
            can_restrict_members=True,
            can_pin_messages=True,
            can_promote_members=False,
            can_manage_chat=True,
            can_manage_video_chats=False
            )
        )
        try:
            await userbot.set_administrator_title(
                m.chat.id,
                userid,
                title
            )
        except:
            pass
        await m.reply_text(f'''
<b>👤 User:</b> {mention}
<b>⚙️ Action: 🚀 Promoted with title:</b> <code>{title or 'admin'}</code>
''',parse_mode=ParseMode.HTML)
    except:
        await m.reply_text(f'`Failed to promote user`')



@userbot.on_message(filters.command(['demote'],UB_PREFIXES) &
    filters.me &
    ~filters.private
)
@log_errors
@admin('can_promote_members')
async def demote_(c,m: Message):
    if not m.reply_to_message and len(m.command) == 1:
        return await m.reply_text('`Reply to a user or provide username to demote`')
    try:
        userid, mention, reason = await get_id_and_reason(m)
        if userid == m.chat.id:
            return await m.reply_text('`Error in resolving the user`')
    except:
        return await m.reply_text('`Error in resolving the user`')
    try:
        await m.chat.promote_member(
            userid,
            ChatPrivileges(
            can_change_info=False,
            can_invite_users=False,
            can_delete_messages=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_manage_chat=False,
            can_manage_video_chats=False
            )
        )
        await m.reply_text(f'''
<b>👤 User:</b> {mention}
<b>⚙️ Action: ❌ Demoted</b>  
''', parse_mode=ParseMode.HTML)
    except:
        await m.reply_text(f'`Failed to demote user`')


@userbot.on_message(
    filters.command(['slowmode','sm'],prefixes=UB_PREFIXES) &
    filters.me &
    ~filters.private
)
@log_errors
@admin('can_change_info')
async def sm_(c,m: Message):
    valid_timings = ['10','30','60','300','900','3600']
    if len(m.command) == 1:
        return await m.reply_text('`Provide a slow-mode duration`')
    if m.command[1].lower() == 'off':
        await userbot.set_slow_mode(chat_id=m.chat.id,seconds=0)
        return await m.reply_text('**Chat slow-mode has been disabled**')
    if m.command[1][-1] != 's':
        return await m.reply_text('`Slow-mode must be in seconds`')
    if m.command[1][:-1] not in valid_timings:
        return await m.reply_text('`Invalid slow-mode duration.`')
    try:
        await userbot.set_slow_mode(chat_id=m.chat.id,seconds=int(m.command[1][:-1]))
        await m.reply_text(f'**Chat slow-mode of {m.command[1]} has been enabled**')
    except Exception as e:
        await m.reply_text(f'`Failed to set slow-mode`')


@userbot.on_message(
    filters.command(['del'],prefixes=UB_PREFIXES) &
    filters.me
)
@log_errors
@admin('can_delete_messages')
async def del_(c,m: Message):
    await m.delete()
    if not m.reply_to_message:
        return await m.reply_text('`Reply to a message to delete`')
    await m.reply_to_message.delete()
