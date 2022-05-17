from pyrogram import filters,types,Client
from .. import LOG_GROUP_ID, USERBOT_ID,slave_bot,USERBOT_MENTION
import json

with open('settings.json','r') as f:
    config = json.load(f)
    f.close()
# yee haw

MSG_FORWARD = config['msgforward']

msg='''
<b>Hello {}!</b>

I am {}'s personal assistant powered by Nebulus.

'''
helper = '''
You can also contact my master via me!.
For that, use the command below

<code>/msg YOUR_MESSAGE</code>

and I will forward your message to them.

<b>Good Day!</b>
'''

mmsg = '''
Aww hey master! I am your smoll cute assistant.
People can use me to contact to you. Messages of theirs will be forwarded to the log group.

Currently this feature is set to <code>{}</code>

You can turn it off/on by using the command

<code>/forward off/on</code>
'''

@slave_bot.on_message(
    filters.command('start') &
    filters.private &
    ~filters.edited
)
async def s_(c,m: types.Message):
    if m.from_user.id != USERBOT_ID:
        textmsg = msg + helper if MSG_FORWARD else msg
        return await m.reply_text(
            textmsg.format(
                m.from_user.first_name,
                USERBOT_MENTION
            ),
            parse_mode='html',
            reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton(text='Nebulus',url='https://t.me/NebulusUB')]
            ])
        )
    await m.reply_text(mmsg.format(MSG_FORWARD),'html',
    reply_markup=types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton(text='Nebulus',url='https://t.me/NebulusUB')]
            ])) # not with ya :)

@slave_bot.on_message(
    filters.command('msg') &
    ~filters.user(users=[USERBOT_ID]) &
    filters.private &
    ~filters.edited
)
async def forwardmsg(c: Client,m: types.Message):
    if not MSG_FORWARD: return
    if len(m.command) > 1:
        message = m.text.markdown.strip('/msg')
        await c.send_message(
            LOG_GROUP_ID,
f'''
**Message from** {m.from_user.first_name}
**Contents:**

{message[:4000]}
''',parse_mode='md',
    reply_markup=types.InlineKeyboardMarkup(
        [
            [
                types.InlineKeyboardButton("View user",user_id=m.from_user.id)
            ]
        ]
    )
        )
        await m.reply_text('I have forwarded your message to my master.')
    else:
        await m.reply_text('Please provide a message to forward it to my master.')

@slave_bot.on_message(
    filters.command('forward') &
    filters.user(users=[USERBOT_ID]) &
    filters.private &
    ~filters.edited
)
async def setforward(c,m: types.Message):
    global MSG_FORWARD,config
    if len(m.command) > 1:
        if m.command[1].lower() == 'off':
            MSG_FORWARD = False
            text = '**Message forwarding disabled**'
        elif m.command[1].lower() == 'on':
            MSG_FORWARD = True
            text = '**Message forwarding enabled**'
        else:
            text = '**Usage:**\n`/forward off/on`'
            return await m.reply_text(text,'md')
        await m.reply_text(text,'md')
        config['msgforward'] = MSG_FORWARD
        with open('settings.json','w') as f:
            json.dump(config,f)
            f.close()
