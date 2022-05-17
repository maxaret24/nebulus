import os, aiohttp,yaml
from pyrogram import Client,__version__
from pyrogram.types import Message,CallbackQuery
import logging, asyncio
import json,sys,psutil,pickle
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from telegraph import Telegraph
from time import time
from typing import Union


with open('nebulus.yml','r') as f:
    config = yaml.safe_load(f)
    f.close()

STARTUP = time()

LOCAL_DEPLOY = config['localdeploy'] 

if LOCAL_DEPLOY:
    CONSOLE_VERBOSE = config['backend']['verbose']
    API_ID = config['nebulus']['api_id']
    API_HASH = config['nebulus']['api_hash']
    PHONE_NUMBER = config['nebulus']['phone_number']
    SESSION_STR = config['nebulus']['session_str']
    SLAVE_BOT_TOKEN = config['slave']['bot_token']
    LOG_GROUP_ID = config['nebulus']['log_grp_id']
    MONGODB_URI = config['database']['mongo']
    MAX_USERWARNS = config['dmpermit']['max_userwarns']
else:
    CONSOLE_VERBOSE = bool(int(os.environ.get('CONSOLE_VERBOSE',0)))
    API_ID = int(os.environ.get('API_ID'))
    API_HASH = str(os.environ.get('API_HASH'))
    PHONE_NUMBER = str(os.environ.get('PHONE_NUMBER'))
    SESSION_STR = str(os.environ.get('SESSION_STR'))
    SLAVE_BOT_TOKEN = str(os.environ.get('SLAVE_BOT_TOKEN'))
    LOG_GROUP_ID = os.environ.get('LOG_GROUP_ID',None)
    if not LOG_GROUP_ID:
        LOG_GROUP_ID = config['nebulus']['log_grp_id']
    MONGODB_URI = str(os.environ.get('MONGODB_URI'))
    MAX_USERWARNS = int(os.environ.get('MAX_USERWARNS',5))


if CONSOLE_VERBOSE:
    logging.basicConfig(level=logging.INFO)

client_session = aiohttp.ClientSession()
UB_PREFIXES = ['.','>']

loop = asyncio.get_event_loop()

# DMPERMIT is enabled by default
with open('settings.json','r') as f:
    val = json.load(f)
    DM_PERMIT = val['dmpermit']
    f.close()

if SESSION_STR:
    userbot = Client(
    SESSION_STR,
    api_id=API_ID,
    api_hash=API_HASH,
    phone_number=PHONE_NUMBER
)
else:
    userbot = Client(
    "USERBOT",
    api_id=API_ID,
    api_hash=API_HASH,
    phone_number=PHONE_NUMBER
)

slave_bot = Client(
    "SLAVE",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=SLAVE_BOT_TOKEN
)

print('=== NEBULUS ===')
print()
print('[ INFO ] Initialized Userbot and Slave bot Clients')
print('[ INFO ] Starting userbot and slavebot...')

userbot.start()
slave_bot.start()
me = userbot.get_me()
sme = slave_bot.get_me()

USERBOT_ID = me.id
USERBOT_USERNAME = me.username
USERBOT_MENTION = me.mention
SLAVE_ID = sme.id
SLAVE_USERNAME = sme.username
SLAVE_MENTION = sme.mention

print('[INFO] Initialising MongoDB Client...')
mongo = AsyncIOMotorClient(MONGODB_URI)
db = mongo.nebulus

print('[INFO] Creating Telegraph account')
graph = Telegraph()
graph.create_account(short_name=SLAVE_USERNAME)



def restart(message: Message):
    chatid = message.chat.id
    msgid = message.message_id
    with open('restartlog.dat','wb') as f:
        pickle.dump({"chat_id":chatid,"message_id":msgid},f)
    f.close()
    os.execv(sys.executable,"python3 -m ub".split(" "))

def get_uptime():
    now = time()
    delta = int(now-STARTUP)
    m,s = divmod(delta,60)
    h,m = divmod(m,60)
    d,h = divmod(h,24)
    return f'{d}d:{h}h:{m}m:{s}s'

def sys_info():
    t1,t2,t3 = psutil.getloadavg()
    cu = psutil.cpu_percent()
    cc = os.cpu_count()
    r = psutil.virtual_memory()[2]
    up = get_uptime()
    msg = f'''
**Bot Uptime**: `{up}`
**Load Avg**: `{t1} {t2} {t3}`
**CPU Usage**: `{cu}%`
**CPUs**: `{cc}`
**RAM Usage**: `{r}%` 
**Pyrogram Version**: `{__version__}`
    '''
    return msg

async def create_log_grp():
    print('[INFO] No log group ID found, creating a log group')
    chat = await userbot.create_group('Nebulus Logs',SLAVE_ID)
    chatid = chat.id
    await userbot.set_chat_photo(chat_id=chatid,photo=f'{__package__}/res/nebulus.jpg')
    await userbot.set_chat_description(chatid,'Logs by Nebulus Userbot')
    print(f'[INFO] Log group created (Nebulus Logs, chat_id:{chatid})')
    return chatid

async def progress(
    current: int,
    total: int,
    task: str,
    obj: Union[Message,CallbackQuery]
    ):

    t = round((current*100/total),1)
    if t % 50 == 0.0 and total >= 10**7:
        bar = "█"*int(t/10)
        space = " "*int(10-(t/10))
        cmbs = round((current/10**6),2); tmbs = round((total/10**6),2)
        text = f'''
**{task}**
`|{bar}{space}|` **{t}%**

**{cmbs}/{tmbs} MB**
'''
        try:
            if isinstance(obj,Message):
                await obj.edit_text(text,'md')
            elif isinstance(obj,CallbackQuery):
                await obj.edit_message_text(text,'md')
        except:
            pass
    else: pass

if not LOG_GROUP_ID:
    LOG_GROUP_ID = loop.run_until_complete(create_log_grp())
    config['nebulus']['log_grp_id'] = LOG_GROUP_ID
    with open('nebulus.yml','w') as f:
        yaml.dump(config,f)
        f.close()
