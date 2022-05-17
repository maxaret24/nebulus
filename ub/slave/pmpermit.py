from pyrogram import Client, filters 
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    CallbackQuery
)
from .. import USERBOT_ID,userbot,slave_bot,MAX_USERWARNS
from ..core.db import *

pmtext = f'''
**Automated DM security**

Hi there, my DM has been secured by Nebulus UB in order to avoid spams.
Please wait until I am online.

**Sending more than {MAX_USERWARNS} messages will get you blocked.**
'''

@slave_bot.on_inline_query(
    filters.regex('^pmp:.+')
)
async def send_msg(client: Client, query: InlineQuery):
    if query.from_user.id != USERBOT_ID:
        await query.answer(
            [
                InlineQueryResultArticle(
                    "Not for you",
                    InputTextMessageContent("Not for you")
                )
            ]
        )
        return

    userid = query.matches[0].group().split(":")[1]

    await query.answer(
        [
            InlineQueryResultArticle(
                "pmtext",
                InputTextMessageContent(
                    message_text=pmtext,
                    parse_mode='markdown'
                ),reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("Approve",f"a:{userid}"),
                        InlineKeyboardButton('Block',f'b:{userid}')
                    ]
                ])
            )
        ],is_personal=True
    )

@slave_bot.on_callback_query(
    filters.regex('^a:.+')
)
async def approveu(client: Client, query: CallbackQuery):
    if query.from_user.id != USERBOT_ID:
        await query.answer('Sorry, this button is not for you',
        cache_time=300)
        return
    userid = int(query.data.split(':')[1])
    res = await approve_user(userid)
    if res:await query.edit_message_text('**User has been approved to DM**','md')
    else:await query.edit_message_text('**User is already approved**','md')

@slave_bot.on_callback_query(
    filters.regex('^b:.+')
)
async def bluck(client: Client, query: CallbackQuery):
    if query.from_user.id != USERBOT_ID:
        await query.answer('Sorry, this button is not for you',
        cache_time=300)
        return
    userid = int(query.data.split(':')[1])
    await query.edit_message_text('**User has been blocked**','md')
    await userbot.block_user(userid)
