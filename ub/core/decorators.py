from pyrogram import Client
from pyrogram.types import Message,ChatPermissions,ChatPrivileges
from .. import slave_bot,USERBOT_ID,LOG_GROUP_ID
import traceback
from io import BytesIO
from pyrogram.enums import ChatType,ParseMode,ChatMemberStatus

cperms: set = set(ChatPermissions().__dir__()).intersection(set(ChatPrivileges().__dir__()))
special_member: list = [ChatMemberStatus.ADMINISTRATOR,ChatMemberStatus.OWNER]

def admin(permission):
    def inner(func):
        async def subfunc(client: Client, message: Message):

            if message.chat.type in [ChatType.SUPERGROUP,ChatType.CHANNEL]:
                member = await client.get_chat_member(
                    chat_id = message.chat.id,
                    user_id = USERBOT_ID
                    )
                if member.status in special_member:
                    privileges = member.privileges
                    if privileges.__getattribute__(permission):
                        await func(client,message)
                    else:
                        await message.edit_text(f'**Missing administrator \
                            permission:** `{permission}`',
                            ParseMode.MARKDOWN)
                else:
                    # common permissions and privileges
                    if permission in cperms:
                        perms = member.permissions
                        if not perms or not perms.__getattribute__(permission):
                            await message.edit_text(f'**Missing chat permission:** `{permission}`')
                        else:
                            await func(client,message)
                    else:
                        await message.edit_text('`[ERR]:` **You are not an administrator**')
            else:
                await func(client,message)
        return subfunc
    return inner



def log_errors(func):
    async def inner(*args,**kwargs):
        try:
            await func(*args,**kwargs)
        except:
            error = traceback.format_exc()
            text: str = f'''
**Error in Application**

`{error}`
'''
            if len(text) > 4096:
                f = BytesIO(text.encode('utf-8'))
                f.name = 'ErrorLog.txt'
                await slave_bot.send_document(
                    chat_id=LOG_GROUP_ID,
                    document=f,
                    caption='**Error in Application**'
                )
            else:
                await slave_bot.send_message(
                    chat_id=LOG_GROUP_ID,
                    text=text
                )
    return inner
