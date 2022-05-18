from .. import *
from pyrogram import Client,filters
from pyrogram.types import Message
from asyncio import create_subprocess_shell
from asyncio.subprocess import PIPE


async def runbash(cmd):
    shell = await create_subprocess_shell(cmd,stdin=PIPE,stderr=PIPE)
    stdout,stderr = await shell.communicate()
    if stdout:
        return stdout
    return stderr
# Some gay handlers

@userbot.on_message(
    filters.command('alive',prefixes=UB_PREFIXES) & filters.me
    & ~filters.edited
    )
async def alive_msg(client,message):
    msg='''
**Nebulus Userbot**

**Status**: `Running`
    '''
    inf = sys_info()
    msg += inf
    await message.edit_text(msg,'md')


@userbot.on_message(
    filters.command('restart',prefixes=UB_PREFIXES) &
    filters.me
)
async def rest(client,message):
    m = await message.edit_text('Restarting slave bot and userbot, please wait...')
    restart(message=m)

@userbot.on_message(
    filters.command('help',prefixes=UB_PREFIXES) &
    filters.me
)
async def sendHelp(client: Client,message: Message):
    if len(message.command) != 2:
        results = await client.get_inline_bot_results(SLAVE_USERNAME,'help')
    else:
        module = message.command[1]
        results = await client.get_inline_bot_results(SLAVE_USERNAME,f'hm:{module}')
    await client.send_inline_bot_result(
            chat_id=message.chat.id,
            query_id=results.query_id,
            result_id=results.results[0].id
    )

@userbot.on_message(
    filters.command('.update') &
    filters.me &
    ~filters.edited &
    ~filters.via_bot
)
async def update_(c, m: Message):
    a = await m.reply_text('**Updating Nebulus...**','md')
    out = await runbash('git pull -f origin alpha')
    if 'not a git repository' in out:
        await runbash('git init . && git remote add origin https://github.com/greplix/nebulus.git && git fetch origin alpha && git checkout -f alpha')
        out = await runbash('git pull -f origin alpha')
    if 'Already up to date' in out:
        await a.edit_text('`Nebulus is already up-to-date`','md')
    else:
        await a.edit_text(f'**Updated Nebulus**\n`{out}`')


