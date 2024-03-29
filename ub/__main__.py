import os,pickle
from pyrogram import idle,filters
from importlib import import_module
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    CallbackQuery,
    InputTextMessageContent,
)
from pyrogram.enums import ParseMode
from time import sleep
from . import *


modules = [x[:-3]for x in os.listdir(f'{__package__}/plugins') if x.endswith(".py")]

print(f'[USERBOT] DM-Permit : {DM_PERMIT}')

maintext= \
'''
**Nebulus Userbot help menu**

An easy to use, minimalistic userbot with useful features

**Repo** : [GitHub](https://github.com/greplix/nebulus)
**Made with <3 by** : [Greplix](https://t.me/greplix)
'''

mwiki = {}


for i in modules:
    s = import_module('.plugins.'+i,__package__)
    if hasattr(s,'NAME') and hasattr(s,'WIKI'):
        mwiki[s.NAME] = s.WIKI
    else:
        pass
    print(f'[USERBOT] Loaded module: {i}.py from plugins')
    sleep(0.1)

print(f'[USERBOT] {len(modules)} modules loaded successfully.')

keys = list(mwiki.keys())
markup = [] # Help Menu buttons
while len(keys) != 0:
    lel = []
    for x in keys[:3]:
        lel.append(
            InlineKeyboardButton(text=x,callback_data=f'help:{x}')
        )
        keys.remove(x)
    markup.append(lel)
markup.append(
    [
    InlineKeyboardButton(text="Close",callback_data="help:close")
    ]
)

for x in os.listdir(f'{__package__}/slave'):
    if x.endswith('.py'):
        import_module(f'.slave.{x[:-3]}',__package__)
        print(f'[SLAVE] Loaded module: {x} from slave')
print('[SLAVE] Modules loaded successfully')


@slave_bot.on_inline_query(
    filters.regex('help')
)
async def respond(client: Client, query: InlineQuery):
    if query.from_user.id != USERBOT_ID:
        await query.answer([
            InlineQueryResultArticle("Not for You",
            InputTextMessageContent("Not for You"))],
            is_personal=True
        )
        return
    keyboard = InlineKeyboardMarkup(markup)
    await query.answer(
        [
            InlineQueryResultArticle(
                "help",
                InputTextMessageContent(
                    message_text=maintext,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True
            ),
            reply_markup=keyboard
            )
        ],
        is_personal=True
    )


@slave_bot.on_callback_query(
    filters.regex('help:.+'),
)
async def editHelp(client: Client, query: CallbackQuery):
    if query.from_user.id != USERBOT_ID:
        await query.answer(text="Sorry, this button is not for you",cache_time=300)
        return
    d = query.data.split(":")[1]
    if d == "close":
        await slave_bot.edit_inline_text(
            query.inline_message_id,
            "**Help Menu Closed**",
            ParseMode.MARKDOWN
        )
        return
    if d != "back":
        wiki = mwiki[d]
        await slave_bot.edit_inline_text(
            inline_message_id = query.inline_message_id,
            text = wiki,
            reply_markup = 
            InlineKeyboardMarkup([
                [InlineKeyboardButton(text="Back",callback_data='help:back'),
                InlineKeyboardButton(text="Close",callback_data='help:close')]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        keyboard = InlineKeyboardMarkup(markup)
        await slave_bot.edit_inline_text(
            inline_message_id=query.inline_message_id,
            text=maintext,parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=keyboard
        )


@slave_bot.on_inline_query(
    filters.regex('^hm:.+')
)
async def irespond(client, inline: InlineQuery):
    if inline.from_user.id != USERBOT_ID:
        await inline.answer([
            InlineQueryResultArticle("Not for you",
            InputTextMessageContent("Not for you"))],
            is_personal=True
        )
        return
    module = inline.query.split(':')[1]
    w = mwiki.get(module.title(),'❌ Invalid module provided')
    await inline.answer([
        InlineQueryResultArticle(
            'Help',
            InputTextMessageContent(w,parse_mode=ParseMode.MARKDOWN)
        )
    ],
    is_personal=True
    )



async def MainStartup():

    deploy=f'''
<b>= Nebulus Userbot =</b>

<code>Userbot is up and running</code>

<b>User:</b> {USERBOT_MENTION}
<b>Slave Bot:</b> @{SLAVE_USERNAME}

<b>Updates:</b> <code>Up to date</code>
'''
    if UPDATE:
        deploy = UPDATE
    print('[ INFO ] Senfing startup status')

    if os.path.exists('restartlog.dat'):
        f = open('restartlog.dat','rb')
        data = pickle.load(f)

        try:
            text = '<b>Restart successful</b>\n'
            if UPDATE:
                text = UPDATE
            await userbot.send_message(
                chat_id=int(data["chat_id"]),
                text=text,
                reply_to_message_id=int(data["message_id"]),
                parse_mode=ParseMode.HTML
            )
            await slave_bot.send_message(
                LOG_GROUP_ID,
                deploy,
                parse_mode=ParseMode.HTML
            )
        except:
            print('[ERROR] Could not send restart status')

        f.close()
        os.remove('restartlog.dat')
    else:
        try:
            await slave_bot.send_message(
                chat_id=LOG_GROUP_ID,
                text=deploy,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            print('[SLAVE] Could not send startup status. Am I in the log group?')
            print(e)

    print('[ INFO ] All set up. Idling')
    await idle()

    print('[ INFO ] Stopping userbot and slavebot')
    await userbot.stop()
    await slave_bot.stop()
    await client_session.close()
    print('[INFO] Cancelling all asyncio tasks')
    for task in asyncio.all_tasks():
        task.cancel()
    print('[EXIT] Exiting')



if __name__=='__main__':
    try:
        loop.run_until_complete(MainStartup())
        loop.close()
    except:
        pass
# phew