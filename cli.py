import arrow
from peewee import fn, EXCLUDED
from telethon.sync import TelegramClient, events
from telethon.tl import functions
from telethon.tl.custom.message import Message
from telethon.tl.types import Channel, User
from telethon.client.telegramclient import TelegramClient as TC
from telethon.tl.custom.dialog import Dialog
from telethon.tl.types import Chat, DialogFilter, InputPeerChannel

import settings
import re
import logging

from tg_listener.db import init_database
from tg_listener.models import AddressRecord, AddressStat

init_database()

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

ptn = re.compile(r'(0x[a-z0-9]{40})', re.IGNORECASE | re.MULTILINE)


def make_stat():
    today = arrow.now().date()
    query = AddressRecord.select().where(
        (AddressRecord.created_at.year == today.year) &
        (AddressRecord.created_at.month == today.month) &
        (AddressRecord.created_at.day == today.day))

    items = []
    stat1 = {}
    for md in query:
        md: AddressRecord
        addr = md.address.lower()
        if addr in settings.BLOCK_ADDRESSES:
            continue

        key = (addr, md.user_id)
        stat1.setdefault(key, 0)
        stat1[key] += 1

    stat2 = {}
    for key, cnt in stat1.items():
        addr = key[0]
        stat2.setdefault(addr, 0)
        stat2[addr] += 1

    for addr, cnt in stat2.items():
        items.append({
            'address': addr,
            'cnt': cnt,
            'day': today.today().strftime('%Y-%m-%d')
        })

    print(arrow.now(), 'insert: ', len(items))
    AddressStat.insert_many(items).on_conflict(preserve=[AddressStat.cnt], update={}).execute()


make_stat()

with TelegramClient('./storage/bot', settings.app_id, settings.app_id_hash,
                    proxy=("socks5", '127.0.0.1', 1081)) as client:
    client: TC
    # client.send_message('me', 'Hello, myself!')
    # print(client.download_profile_photo('me'))
    for d in client.iter_dialogs(folder=1):
        d: Dialog
        chat: Chat = d.entity

    info_peers = {}


    async def get_folders():
        request = await client(functions.messages.GetDialogFiltersRequest())
        for dialog_filter in request:
            if not dialog_filter.title == '币讯':
                continue
            dialog_filter: DialogFilter
            # print(dialog_filter)
            for peer in dialog_filter.include_peers:
                info_peers[peer.channel_id] = peer


    client.loop.run_until_complete(get_folders())


    @client.on(events.NewMessage(incoming=True))
    async def handler(event: events.NewMessage.Event):
        msg: Message = event.message
        chat: Channel = msg.chat
        sender: User = msg.sender

        # print('{title}({id}): {msg}'.format(title=chat.title, id=chat.id, msg=msg.text), sender)

        text = msg.message.replace('\n', ' ')
        m = ptn.search(text)
        if m and chat.id in info_peers:
            beg = text.index('0x')
            beg = max(0, beg - 10)
            text = text[beg:]
            address = m.group(0).lower()
            if address in settings.BLOCK_ADDRESSES:
                return
            # text = text.replace(m.group(0), ' ' + m.group(0) + ' ')
            # sender: User = await msg.get_sender()
            # if not sender:
            #     sender = msg.sender

            print('{title}({id}): {msg}'.format(title=chat.title, id=chat.id, msg=text), sender.username)
            md = AddressRecord()
            md.address = address
            md.text = text[:1024]
            md.chat_id = chat.id
            md.chat_name = chat.title
            md.user_id = msg.sender_id
            md.user_fullname = sender.first_name + ' ' + (sender.last_name or '')
            md.username = sender.username
            md.save()

            make_stat()


    client.run_until_disconnected()
