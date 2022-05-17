from .. import db

gbans = db.gbans
notes = db.notes
warns = db.warns
approved = db.approved


async def log_warn(userid: int,count: int):
    await warns.update_one(
        {'USERID':userid},
        {'$set':{
            'WARNCOUNT':count
        }},upsert=True
    )

async def get_warn(userid):
    data = await warns.find_one({'USERID':userid})
    return data

async def del_warn(userid):
    if await get_warn(userid):
        await warns.delete_one({'USERID':userid})
    else:pass

async def is_approved(userid):
    data = await approved.find_one({'USERID':userid})
    return True if data else False

async def approve_user(userid):
    if await is_approved(userid):return False
    await approved.insert_one({'USERID':userid})
    return True

async def disapprove_user(userid):
    if not await is_approved(userid):return False
    await approved.delete_one({'USERID':userid})
    return True

async def save_note(notename,data):
    notename = notename.lower().strip()
    await notes.update_one(
        {'NOTENAME':notename},
        {'$set':{
            'META':data
        }},upsert=True
    )

async def del_note(notename):
    data = await notes.find_one({'NOTENAME':notename})
    if not data:return False
    await notes.delete_one({'NOTENAME':notename})
    return True

async def get_notes():
    names = []
    async for x in notes.find({}):
        names.append(x['NOTENAME'])
    return names

async def get_a_note(notename):
    notename = notename.lower().strip()
    data = await notes.find_one({'NOTENAME':notename})
    return data['META'] if data else None

