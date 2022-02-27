import re

from telethon import TelegramClient, TelegramClient as TC, events
from telethon.tl import functions
from telethon.tl.custom import Dialog, Message
from telethon.tl.types import Chat, DialogFilter, Channel, User

import settings
from tg_listener.models.AddressStat import make_stat
from tg_listener.models.models import AddressRecord

address_ptn = re.compile(r'(0x[a-z0-9]{40})', re.IGNORECASE | re.MULTILINE)
words_ptn = re.compile("[^\u4e00-\u9fa5^a-z^A-Z^0-9]")  # 匹配不是中文、大小写、数字的其他字符
multi_space = re.compile(r"\s+")


class Listener:
    def run(self):
        with TelegramClient('./storage/bot', settings.app_id, settings.app_id_hash,
                            proxy=settings.proxy) as client:
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
                m = address_ptn.search(text)
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

                    text = words_ptn.sub(' ', text)
                    text = multi_space.sub(' ', text)

                    print('{title}({id}): msg={msg}, username={username}'.format(title=chat.title, id=chat.id, msg=text,
                                                                                 username=sender.username))
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
