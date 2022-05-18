import json
from pyrogram import Client,filters
from pyrogram.types import \
    Message, InlineKeyboardMarkup, InlineKeyboardButton
from .. import (
    DM_PERMIT,
    LOG_GROUP_ID, 
    UB_PREFIXES,
    MAX_USERWARNS,
    SLAVE_USERNAME,
    userbot,
    restart,
    slave_bot
)
from ..core.db import *


DM_CACHE = []

DM_LOG = '''
**#DM_LOG**

**Direct Message from** [{}](tg://user?id={})

**== Message Content ==**

{}
'''


NAME = "DMpermit"

WIKI = '''
💢 **Module**: `DM Permit`

Avoid spams in DM

-`.a|.approve`
    __Approve a user to DM you. Use in the private chat of the peer__

-`.da|.disapprove`
    __Disapprove a user to DM you. Use in the private chat of the peer__

-`.dmp off/on`
    __Turns DMpermit module ON or OFF__
'''



@userbot.on_message(
    filters.private &
    filters.incoming &
    ~filters.user(users=[777000,1285404899]) &
    ~filters.me &
    ~filters.bot &
    ~filters.service &
    ~filters.edited &
    ~filters.via_bot
)
async def warn(client: Client,message):
    if not DM_PERMIT or message.from_user.id in DM_CACHE: return
    user_id = message.from_user.id
    if not await is_approved(user_id):
        warning = await get_warn(user_id)
        if not warning:
            result = await client.get_inline_bot_results(SLAVE_USERNAME,f"pmp:{user_id}")
            await log_warn(user_id,1)
            await client.send_inline_bot_result(
                chat_id=message.chat.id,
                query_id=result.query_id,
                result_id=result.results[0].id
            )
        else:
            wcount = int(warning['WARNCOUNT'])
            wcount += 1
            if wcount > MAX_USERWARNS:
                await message.reply_text("**Automatically blocked for spam.**",'md')
                await client.block_user(user_id)
                await del_warn(user_id)
                return
            elif wcount == MAX_USERWARNS:
                await message.reply_text('''
`[NEBULUS]`

**Final Warning!**

**Continuing to send further messages will get you blocked.**
**Please wait for my approval**
''','md')
                await log_warn(user_id,wcount)
            else:
                await log_warn(user_id,wcount)
        await slave_bot.send_message(
            chat_id=LOG_GROUP_ID,
            text=DM_LOG.format(
                message.from_user.first_name,
                user_id,
                message.text.markdown if message.text else "`<Non-Text Message>`"
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Approve",f'a:{user_id}'),
                        InlineKeyboardButton("Block",f'b:{user_id}')
                    ],
                    [
                        InlineKeyboardButton('View user',user_id=user_id)
                    ]
                ]
            ),
            parse_mode='md'
        )

    else:
        DM_CACHE.append(user_id)




@userbot.on_message(
    filters.command(["a","approve"],UB_PREFIXES) &
    filters.me &
    filters.private &
    ~filters.edited &
    ~filters.via_bot
    )
async def approve_user_(client,message: Message):
    if not DM_PERMIT: return
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text('Reply to a user or provide user ID to approve')
    userid = message.reply_to_message.from_user.id if \
        message.reply_to_message else message.command[1]
    if not str(userid).isdigit():
        return await message.reply_text('Please provide a user ID or reply to a user\'s message')
    res = await approve_user(int(userid))
    if not res:
        return await message.reply_text("`User is already approved`",'md')
    await message.reply_text(f"**User has been approved to PM.**",'md')
    await del_warn(int(userid))



@userbot.on_message(
    filters.command(["da","disapprove"],prefixes=UB_PREFIXES) &
    filters.me &
    filters.private &
    ~filters.edited &
    ~filters.via_bot
    )
async def disapprove_user_(client,message):
    if not DM_PERMIT: return
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text('Reply to a user or provide user ID to disapprove')

    userid = message.reply_to_message.from_user.id if \
        message.reply_to_message else message.command[1]

    if not str(userid).isdigit():
        return await message.reply_text('Please provide a user ID or reply to a user\'s message')

    res = await disapprove_user(int(userid))

    if not res:
        return await message.reply_text("`User has not been approved yet`",'md')

    await message.reply_text(f"**User has been disapproved to PM.**",'md')
    await del_warn(int(userid))



@userbot.on_message(
    filters.command('dmp',prefixes=UB_PREFIXES) &
    filters.me &
    ~filters.edited &
    ~filters.via_bot
    )
async def set_dmp(client,message):
    f = open('settings.json','w')
    if len(message.command) > 1:
        mode = message.command[1]
        if mode.lower() in ['disable','false','off']:
            json.dump({"dmpermit":False},f)
            m = await message.reply_text("**DM-Permit has been disabled. Restarting...**",'md')
            f.close()
            restart(message=m)
        elif mode.lower() in ['enable','true','on']:
            json.dump({"dmpermit":True},f)
            m = await message.reply_text("**DM-Permit has been enabled. Restarting...**",'md')
            f.close()
            restart(message=m)
    else:
        await message.reply_text("**Usage**\n`.dmp off|on`",'md')