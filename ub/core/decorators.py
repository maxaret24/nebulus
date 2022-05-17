from pyrogram import Client
from pyrogram.types import Message
from .. import slave_bot,USERBOT_ID,LOG_GROUP_ID
import traceback

def admin(permission):
    def inner(func):
        async def subfunc(client: Client, message: Message):
            if message.chat.type not in ['private','group','bot']:
                member = await client.get_chat_member(chat_id=message.chat.id,user_id=USERBOT_ID)
                permdict = member.__dict__
                if permdict[permission]:
                    await func(client,message)
                else:
                    await message.edit_text(f'**Missing permissions to perform requested action:** `{permission}`','md')
            else: await func(client,message)
        return subfunc
    return inner

def log_errors(func):
    async def inner(*args,**kwargs):
        try:
            await func(*args,**kwargs)
        except:
            error = traceback.format_exc()
            await slave_bot.send_message(
                chat_id=LOG_GROUP_ID,
                text=f'**Error in Application:**\n`{error}`',
                parse_mode='markdown',
                disable_web_page_preview=True
            )
    return inner
