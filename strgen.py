from pyrogram import Client

api_id = int(input('Enter your API ID: '))
api_hash = input('Enter your API HASH: ')
phone = input('Enter your phone number: ')

c = Client(
    session_name=":memory:",
    api_id=api_id,
    api_hash=api_hash,
    phone_number=phone
)

c.start()
first = c.get_me().first_name

print(f"User: {first}")
session = c.export_session_string()
c.send_message("me",text=f'**Session string for Nebulus**\n\n`{session}`\n\n**Do not share it with anyone!**',parse_mode='markdown')
c.stop()
print("Check Saved Messages for the session string.")