'''
ADMINFINDER.PY : Used to find possible admin panels of a site by concentating suffixes to the
base URL one by one. Uses asyncio.
This file is a part of the Witch Project
By Cryptonian007[greplix] [24|11|21::08:43]
'''

#from core.formatting import *
from urllib.parse import urlparse
import asyncio,aiohttp,sys
#import progressbar (lawde ka progressbar)

def check_suffixes(lst):
    # yeah ik it's stupid
    lol = []
    for i in lst:
        if i[0] == '/':lol.append(i)
        else:lol.append('/'+i)
    return lol

async def checkadm(url,suffix,client,boolean):
    if boolean:
        if url.endswith('/'):
            url = url[0:-1]
            nurl = url + suffix
        else:
            nurl = url + suffix
    else:nurl = urlparse(url).scheme + '://' + urlparse(url).netloc + suffix
    try:
        resp = await client.get(nurl)
        code = resp.status
        if code == 200:
            return nurl
        else:
            return ''#minus(f'{nurl}')
    except:
        return ''#minus(f'{nurl}')
