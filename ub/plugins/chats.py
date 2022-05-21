import pyrogram
from pyrogram.enums import ParseMode,ChatType
from pyrogram import Client, filters
from .. import UB_PREFIXES,userbot,USERBOT_ID
from ..core.decorators import *
from time import time
from pyrogram.enums import ChatType

NAME = "Chats"

WIKI = '''
💢 **Module**: `Chats`

Manage chats

**Commands**

-`.purge`
    __Purges messages. Reply to a message to purge from__

-`.spurge`
    __Silently purges messages__

-`.pin`
    __Pins messages__

-`.lpin`
    __Pins messages and notifies users__

-`.id`
    __Gets IDs of yours,the chat,and the user you\'re replying to__

-`.info USERID/USERNAME`
    __Get information about a user or a chat__

-`.block`
    __Reply to a user to block__

-`.unblock`
    __Reply to a user to unblock__

-`.leave`
    __Leave a chat__
'''


def lookup(u: pyrogram.types.User):
    text = f'''
**User Info**

**FullName** : `{(str(u.first_name) + ' ' + str(u.last_name or '')).strip()}`
**Username** : `{u.username}` (@{u.username})
**User ID** : `{u.id}`
**Is Scam** : `{u.is_scam}`
**Is Fake** : `{u.is_fake}`
**DC ID** : `{u.dc_id}`
**Link** : [This](tg://user?id={u.id})
    '''
    return text

def lookupchat(chat: pyrogram.types.Chat):
    if chat.type not in [ChatType.SUPERGROUP,ChatType.GROUP]:
        return "**Usage**\n`.whois (Reply to a message or supply username|userID or empty for chat info)`"
    text=f'''
**Chat Info**

**Title** : `{chat.title}`
**Chat ID** : `{chat.id}`
**Members Count** : `{chat.members_count}`
**Chat Type** : `{chat.type}`
**Username** : `{chat.username}`
**DC ID** : `{chat.dc_id}`
**Is Scam** : `{chat.is_scam}`
'''
    return text


@userbot.on_message(
    filters.command(["purge","spurge"],prefixes=UB_PREFIXES) &
    filters.me
)
@log_errors
@admin('can_delete_messages')
async def purgemsgs(client: Client,message: pyrogram.types.Message):
    # function name says its purpose
    await message.delete()
    rep = message.reply_to_message
    if not rep:
        return await message.edit_text('`Reply to a message to purge from`')
    cmd = message.command
    if len(cmd) > 1 and cmd[1].isdigit():
        purgeto = rep.id + int(cmd[1])
        if purgeto > message.id:
            purgeto = message.id
    else:
        purgeto = message.id
    messages = list(range(rep.id,purgeto))
    s = time()
    while len(messages) != 0:
        chunk = []
        for m in messages[:100]:
            chunk.append(m)
            messages.remove(m)
        count = await client.delete_messages(
            chat_id=message.chat.id,
            message_ids=chunk,
            revoke=True
        )
    e = time()
    delta = round(e-s,2)
    if message.text[1] != 's':
        await message.reply_text(f"`Purged {count} messages in {delta}s`")



@userbot.on_message(
    filters.command(["pin","lpin"],prefixes=UB_PREFIXES) &
    filters.me
)
@log_errors
@admin('can_pin_messages')
async def pinmsg(c: Client, m: Message):
    if m.reply_to_message:
        await c.pin_chat_message(
            chat_id = m.chat.id,
            message_id = m.reply_to_message.id,
            disable_notification = False if m.text[1] == 'l' else True,
            both_sides = True if m.chat.type == ChatType.PRIVATE else False
        )
        await m.edit_text(f'[Message]({m.reply_to_message.link}) `has been pinned`',ParseMode.MARKDOWN)
    else:
        await m.edit_text("`Reply to a message to pin it`")


@userbot.on_message(
    filters.command('id',prefixes=UB_PREFIXES) &
    filters.me
)
async def get_id(client: Client, message: Message):
    if message.reply_to_message:
        text=f'''
**Your ID** : `{message.from_user.id}`
**Chat ID** : `{message.chat.id}`
**Replied User ID** : `{message.reply_to_message.from_user.id or message.reply_to_message.sender_chat.id}`
**Message ID** : `{message.id}`
**Replied message ID** : `{message.reply_to_message.id}`
        '''
    else:
        text=f'''
**Your ID** : `{message.from_user.id}`
**Chat ID** : `{message.chat.id}`
**Message ID** : `{message.id}`
        '''
    await message.edit_text(text)


@userbot.on_message(
    filters.command('block',prefixes=UB_PREFIXES) &
    filters.me &
    ~filters.via_bot
)
async def block_(c,m: Message):
    if not m.reply_to_message:
        return await m.edit_text('`Reply to a user to block`')
    if m.reply_to_message.from_user.id == USERBOT_ID:
        return await m.edit_text('`You\'re trying to block yourself`')
    await m.reply_text('**User has been blocked!**')
    await c.block_user(m.reply_to_message.from_user.id)



@userbot.on_message(
    filters.command('unblock',prefixes=UB_PREFIXES) &
    filters.me &
    ~filters.via_bot
)
async def unblock_(c,m: Message):
    if not m.reply_to_message:
        return await m.edit_text('`Reply to a user to unblock`')
    if m.reply_to_message.from_user.id == USERBOT_ID:
        return await m.edit_text('`You\'re trying to unblock yourself`')
    await m.reply_text('**User has been unblocked**')
    await c.unblock_user(m.reply_to_message.from_user.id)


@userbot.on_message(
    filters.command('leave',prefixes=UB_PREFIXES) &
    filters.me &
    ~filters.private
)
async def l_(c,m: Message):
    await m.delete()
    await m.chat.leave()

@userbot.on_message(filters.command("info",prefixes=UB_PREFIXES) &
    filters.me &
    ~filters.via_bot
)
@log_errors
async def lukup(client: Client,message: Message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        msg = lookup(user)
        await message.edit_text(msg)
    else:
        if len(message.command) > 1:
            identifier = message.command[1]
            try:
                user = await client.get_users([identifier])
                msg = lookup(user[0])
                await message.edit_text(msg)
            except Exception as e:
                ex = f'**Exception :** `{e}`'
                await message.edit_text(ex)
        else:
            text = lookupchat(message.chat)
            await message.edit_text(text)