from pyrogram import Client,filters
from pyrogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

from .. import slave_bot,USERBOT_ID,client_session

results = {} #TODO: Improve the way to manage results

udquery = None

string='''
**Query: ** `{}`
**Definition: ** `{}`
**Example: ** `{}`
'''


def rt_keyboard(index):
    lst = [
            InlineKeyboardButton(f"Previous",f"ud:p={index}"),
            InlineKeyboardButton("Next",f'ud:n={index}')
        ]
    keyboard = InlineKeyboardMarkup([
        lst,
        [
            InlineKeyboardButton('Close','ud:close')
        ]
    ])
    return keyboard

@slave_bot.on_inline_query(
    filters.regex("ud.+") 
)
async def respond(client: Client, query: InlineQuery):
    global udquery,results,string
    if results != {}:
        results = {}
    if query.from_user.id != USERBOT_ID:
        await query.answer(
            [
                InlineQueryResultArticle(
                    "Not for you",
                    InputTextMessageContent("Not for you"))
            ],is_personal=True
        )
    else:
        udquery = ' '.join(query.matches[0].group().split(" ")[1:]).strip().lower()
        resp = await client_session.get(f"https://api.urbandictionary.com/v0/define?term={udquery}")
        data = await resp.json()
        if data["list"] == []:
            text="**No results found**"
            return await query.answer(
                [
                    InlineQueryResultArticle(
                        udquery,
                        InputTextMessageContent(
                        message_text=text,disable_web_page_preview=True
                    ))
                ],is_personal=True
            )
        else:
            for x,d in enumerate(data['list']):
                results[x] = {
                    'definition':d['definition'],
                    'example':d['example']
                }
            text = string.format(udquery,results[0]['definition'],results[0]['example'])
            kb = rt_keyboard(0)
        await query.answer(
            [
                InlineQueryResultArticle(udquery,InputTextMessageContent(
                    message_text=text,disable_web_page_preview=True
                ),reply_markup=kb)
            ],is_personal=True
        )


@slave_bot.on_callback_query(
    filters.regex('ud:.*'),
)
async def menustuffs(client,query: CallbackQuery):
    global string
    if query.from_user.id != USERBOT_ID:
        await query.answer("This button is not for you",show_alert=True,cache_time=300)
        return

    d = query.data.split(':')[1]

    if d =='close':
        await slave_bot.edit_inline_text(
            query.inline_message_id,
            "**Closed**"
        )
        return

    index = d.split('=')[1]

    if 'n' in d:
        nindex = int(index) + 1
    else:
        nindex = int(index) - 1

    kb = rt_keyboard(nindex)
    try:
        msg = string.format(udquery, results[nindex]['definition'], results[nindex]['example'])
    except KeyError:
        if nindex < int(index):
            key = list(results.keys())[-1]
        elif nindex > int(index):
            key = list(results.keys())[0]
        msg = string.format(udquery, results[key]['definition'], results[key]['example'])
        kb = rt_keyboard(key)
    await slave_bot.edit_inline_text(
        query.inline_message_id,
        msg,
        reply_markup=kb
    )

