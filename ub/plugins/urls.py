from .. import *
from ..core.adminfinder import *
from pyrogram import Client, filters
from pyrogram.types import Message
from ..core.decorators import log_errors
import io
import re
from urllib.parse import urlparse
from htmlwebshot import WebShot

NAME = "URLs"

WIKI = '''
💢 **Module**: `URL Utils`

**Commands**

-`.cpanel URL`
    __Tries to find the admin panel of a site via suffix concentation__

-`.unshort URL`
    __Unshorts shortened URL__

-`.sqli URL`
    __Tries to find SQLi vulnerabilites via query-based injection__4

-`.webss`
    __Reply to a URL or supply one to get web-screenshot__
'''

ERRORS = {
    "MySQL": (r"SQL syntax.*MySQL", r"Warning.*mysqli_.*", r"MySQL Query fail.*", r"SQL syntax.*MariaDB server",r"Warning.*mysql_.*",r"mysqli_fetch_array*"),
    "PostgreSQL": (r"PostgreSQL.*ERROR", r"Warning.*\Wpg_.*", r"Warning.*PostgreSQL"),
    "Microsoft SQL Server": (r"OLE DB.* SQL Server", r"(\W|\A)SQL Server.*Driver", r"Warning.*odbc_.*", r"Warning.*mssql_", r"Msg \d+, Level \d+, State \d+", r"Unclosed quotation mark after the character string", r"Microsoft OLE DB Provider for ODBC Drivers"),
    "Microsoft Access": (r"Microsoft Access Driver", r"Access Database Engine", r"Microsoft JET Database Engine", r".*Syntax error.*query expression"),
    "Oracle": (r"\bORA-[0-9][0-9][0-9][0-9]", r"Oracle error", r"Warning.*oci_.*", "Microsoft OLE DB Provider for Oracle"),
    "IBM DB2": (r"CLI Driver.*DB2", r"DB2 SQL error"),
    "SQLite": (r"SQLite/JDBCDriver", r"System.Data.SQLite.SQLiteException"),
    "Informix": (r"Warning.*ibase_.*", r"com.informix.jdbc"),
    "Sybase": (r"Warning.*sybase.*", r"Sybase message")
}

MSG = '''
**URL** : `{}`
**Total Suffixes** : `{}`
**Failed Connections** : `{}`
**Possible Admin Panels** : `{}`
'''

def check(data):
    for key,value in ERRORS.items():
        for err in value:
            print(err)
            res = re.findall(err,data)
            if res != []:
                error = res[0]
                dbname = key
                vuln=True
                return vuln,dbname,error
    return False,None,None

f = open("ub/core/suffixes.txt")
lst = f.read().splitlines()
f.close()
total = len(lst)
new_lst = check_suffixes(lst)

# Admin panel finder xD

@userbot.on_message(
    filters.command("cpanel",prefixes=UB_PREFIXES) &
    filters.me
)
@log_errors
async def get_panel(client,message: Message):
    if len(message.command) == 1:
        return await message.edit_text('`Provide a URL`','md')
    global stext,total
    url = message.text.split(" ")[1].strip()
    mid = message.message_id
    meh = await message.reply_text(
    "**Scanning for possible admin panels...**",'md'
    )
    try:
        print(f'LOADED URLS: {total}')
        tasks = [
        checkadm(url,x,client_session,False) for x in new_lst
        ]
        result = await asyncio.gather(*tasks)
        nresult = [x for x in result if x != '']
        print(nresult)
        failed = total - len(nresult)
        if failed == total:
            await meh.edit_text(MSG.format(url,total,failed,'None'),'md')
        else:
            stext = ''
            for _ in nresult:
                stext += f"`{_}`\n"
            fmsg = MSG.format(url,total,failed,stext)
            if len(MSG) > 4096:
                fi = io.BytesIO(fmsg.encode('utf-8'))
                fi.name = 'results.txt'
                await message.reply_document(fi)
            else: await meh.edit_text(fmsg,'md')
    except Exception as e:
        await meh.edit_text(f'**Exception**\n`{e}`','md')

# unshorten url

@userbot.on_message(
    filters.command("unshort",prefixes=UB_PREFIXES) &
    filters.me
)
async def ushort(client,message):
    if len(message.command) == 1:
        return await message.edit_text('`Provide a URL`','md')
    url = message.text.split(" ")[1].strip()
    data = await client_session.get(url)
    u = data.url
    ru = data.real_url
    await message.edit_text(
    f"**URL** : `{url}`\n**Unshortened URL** : `{ru}`",'md'
    )

# SQLi query based injection vuln

@userbot.on_message(
    filters.command("sqli",prefixes=UB_PREFIXES) &
    filters.me &
    ~filters.via_bot &
    ~filters.edited
)
@log_errors
async def detect_sqli(client,message):
    if len(message.command) == 1:
        return await message.edit_text('`Provide a URL`','md')
    try:
        await message.edit_text("**Finding possible SQLi vulnerabilities...**",'md')
        url = message.text.split(" ")[1].strip()
        if urlparse(url).query:
            q = urlparse(url).query
            qs = q.split('&')
            nqs = []
            for x in qs:
                y = x[:-1] + '*'
                nqs.append(y)
            nurl = urlparse(url).scheme + '://'  + urlparse(url).netloc + urlparse(url).path + '?' + '&'.join(nqs)
            logging.info(f'SCAN : {nurl}')
            resp =  await client_session.get(nurl)
            data = await resp.text()
            try:headers = await resp.headers();xxx=headers['x-powered-by']
            except:xxx='None'
            vuln,dbname,error = check(data)
            if vuln:
                await message.reply_text(
                    f'''
**SQLi Vulnerable**

**URL** : `{url}`
**DB** : `{dbname}`
**SQL Error** : `{error}`
**X-Powered-By** : `{xxx}`
''','md'        )
            else:
                await message.reply_text('**Didn\'t get any SQLi vulnerabilities**','md')
        else:
            await message.reply_text('**URL doesn\'t have queries to inject payloads**','md')
    except IndexError:
        await message.edit_text('**Usage**\n`.sqli URL`','md')



@userbot.on_message(
    filters.command("webss",prefixes=UB_PREFIXES) &
    filters.me &
    ~filters.via_bot &
    ~filters.edited
)
async def ss_(c: Client, m: Message):
    if not m.reply_to_message and len(m.command) == 1:
        await m.reply_text('`Provide a URL or reply to a message with URL to capture web-screenshot`')
        return
    if m.reply_to_message:
        url = m.reply_to_message.text.strip()
    else:
        url = m.command[1].strip()
    a = await m.reply_text('`Capturing web-screenshot and uploading...`')
    try:
        ss = WebShot(quality=88, flags=["--enable-javascript", "--no-stop-slow-scripts"])
        img = await ss.create_pic_async(url=url)
        await m.reply_photo(photo=img,caption=f'`{url}`',parse_mode='md')
        await a.delete()
    except Exception as e:
        await a.edit_text(f'**Exception**: `{e}`','md')