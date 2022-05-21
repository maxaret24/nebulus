from .. import *
from pyrogram import Client, filters
from pyrogram.types import Message
from io import StringIO
import sys,asyncio

NAME = 'Python'

WIKI = '''
💢 **Module**: `Python`

Execute Python statements

**Objects**

`m`: `pyrogram.types.Message`
`c`: `pyrogram.Client`

**Commands**

-`.exec|.py STATEMENT`
    __Executes Python statement__

-`.tasks`
    __Lists running exec tasks__

-`.kill TASK_ID`
    __Kills a running exec task(provide the Task ID)__
'''

tasks = {}


@userbot.on_message(
    filters.command(['exec','py'],prefixes=UB_PREFIXES) &
    filters.me &
    ~filters.via_bot
)
async def pyexc(client: Client, message: Message):

    try:
        statement = " ".join(message.text.split(" ")[1:])
        if statement.endswith('\n'):
            statement = statement[:-1]
    except IndexError:
        await message.edit_text('`Provide a Python statement to execute`')
        return

    async def execute(command: str):
        initials = 'async def _exc(c,m):\n    '
        if command.startswith('\n'):
            command = command[1:]
        if '\n' in command:
            command = '\n    '.join(command.split('\n'))
        initials += command
        exec(initials)
        await locals()['_exc'].__call__(client,message)

    stdout = sys.stdout
    stderr = sys.stderr
    iostdout = StringIO(); iostderr = StringIO()
    m = await message.reply_text('`Executing...`')
    returnval,stdo,stde = None, None, None
    sys.stdout = iostdout; sys.stderr = iostderr
    try:
        task = asyncio.create_task(execute(statement))
        tid = 0 if len(list(tasks.keys())) == 0 else list(tasks.keys())[-1] + 1
        tasks[tid] = task
        await task
    except:
        import traceback
        err = traceback.format_exc()
        returnval = err.splitlines()[-1]
    sys.stdout = stdout;sys.stderr = stderr
    iostdout.seek(0);iostderr.seek(0)
    stdo = iostdout.read();stde = iostdout.read()
    output = '**exec Results**\n'
    if stdo: output += f'`{stdo}`'
    elif stde: output += f'`{stde}`'
    else: output = f'`Executed`'
    if returnval: output = f'\n**Exception:** `{returnval}`'
    await asyncio.sleep(0.5)
    await m.edit_text(output)
    del tasks[tid]



@userbot.on_message(
    filters.command('tasks',prefixes=UB_PREFIXES) &
    filters.me &
    ~filters.via_bot
)
async def list_tasks(client: Client, message: Message):
    output = ''
    if tasks == {}:
        output = '**There are no running tasks**'
    else:
        output += '**SNO**    **Task ID**\n'
        for x,y in enumerate(tasks.keys()):
            output += f'`{x+1}`        `{y}`'
    await message.edit_text(output)



@userbot.on_message(
    filters.command('kill',prefixes=UB_PREFIXES) &
    filters.me &
    ~filters.via_bot
)
async def kill_task(client: Client, message: Message):
    try:
        tid = int(message.text.split(" ")[1])
        task = tasks[tid]
        if task.done() or task.cancelled():
            del tasks[tid]
        else:
            task.cancel()
            del tasks[tid]
        msg = f'**TaskID**: `{tid}`\n**Status**: `Killed`'
    except IndexError:
        msg = f'`Provide a Task ID to kill the task`'
    except KeyError:
        msg = f'`Provide a valid Task ID`'
    except Exception as e:
        msg = f'**Exception:** `{e}`'

    await message.edit_text(msg)