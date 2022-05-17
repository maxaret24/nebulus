from re import L
from .. import *
import asyncio
from asyncio import create_subprocess_shell
from asyncio.subprocess import PIPE
from pyrogram import filters
import io

processes = {}

NAME = "Shell"

WIKI = '''
💢 **Module**: `Shell`

-`.sh CMD`
    __Execute a shell command__

-`.plist`
    __List running processes__

-`.pkill PROCESS_ID`
    __Kill a process[SIGKILL]__
'''


@userbot.on_message(
    filters.command(["sh"],
    prefixes=UB_PREFIXES) &
    filters.me &
    ~filters.edited &
    ~filters.via_bot
)
async def execute_shell_command(client,message):
    text='''
`%s`

**process exited with code %s**
    '''
    splitted = message.text.split(" ")
    if len(splitted) == 1 or splitted[1] == "":
        await message.reply_text("**Usage**\n`.sh|.bash some_bash_command`",'md')
    else:
        command = ' '.join(splitted[1:])
        try:
            process = await create_subprocess_shell(
                cmd=command,
                stdout=PIPE,
                stderr=PIPE
            )
            pid = process.pid
            processes[pid] = process
            m = await message.reply_text(f'**Executing...** `[Process ID: {pid}]`','md')
            await asyncio.sleep(0.5)
            stdout, stderr = await process.communicate()
            if stdout:
                t = text % (stdout.decode().strip(),process.returncode)
            elif stderr:
                t = text % (stderr.decode().strip(),process.returncode)
            else:
                t = text % ('None',process.returncode)
            if len(t) > 4096:
                doc = io.BytesIO(t.encode('utf-8'))
                doc.name = 'output.txt'
                await m.reply_document(doc)
            else:
                await m.edit_text(t)
            try:
                del processes[pid]
            except: pass
        except Exception as e:
            await m.edit_text(f"**Exception :** `{e}`",'md')


@userbot.on_message(
    filters.command(["plist"],
    prefixes=UB_PREFIXES) &
    filters.me &
    ~filters.edited &
    ~filters.via_bot
)
async def plist_(c, m: Message):
    if processes == {}:
        return await m.reply_text('`There are no running processes`','md')
    text = '''
**Process IDs**

'''
    for x in processes.keys():
        text += f'`{x}`\n'
    await m.reply_text(text,'md')

#TODO: Add SIGTERM
@userbot.on_message(
    filters.command(['pkill']) &
    filters.me &
    ~filters.edited &
    ~filters.via_bot
)
async def sigkill(c, m: Message):
    if len(m.command) != 2:
        return await m.reply_text('`Provide a Process ID to kill it`','md')
    try:
        process = processes[int(m.command[1])]
        process.kill()
        del processes[int(m.command[1])]
    except KeyError:
        await m.reply_text('`Provide a valid Process ID`','md')
    except ValueError:
        await m.reply_text('`Provide a valid Process ID`','md')
    except Exception as e:
        await m.reply_text(f'**Exception:** `{e}`','md')
