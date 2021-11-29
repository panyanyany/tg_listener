from telethon.sync import TelegramClient, events
from telethon.tl.custom.message import Message
from telethon.tl.types import Channel

import settings
import re

ptn = re.compile(r'0x[a-z0-9]{40}', re.IGNORECASE | re.MULTILINE)

with TelegramClient('./storage/bot', settings.app_id, settings.app_id_hash, proxy=("socks5", '127.0.0.1', 1081)) as client:
    client.send_message('me', 'Hello, myself!')
    # print(client.download_profile_photo('me'))


    @client.on(events.NewMessage(incoming=True))
    async def handler(event: events.NewMessage.Event):
        msg: Message = event.message
        chat: Channel = msg.chat

        text = msg.message.replace('\n', '\t\n')
        m = ptn.search(text)
        if m:
            print('{title}({id}): {msg}'.format(title=chat.title, id=chat.id, msg=text))


    client.run_until_disconnected()
