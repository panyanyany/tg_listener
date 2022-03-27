import asyncio
from asyncio import Queue
from threading import Thread

from tg_listener.repo.log_handler import SyncHandler
from tg_listener.services import lp_service
from util.log_util import setup3, default_ignore_names
from util.uniswap.trade import Trade
from util.web3.util import bsc_web3

setup3(ignore_names=list(set(['web3.*', 'asyncio'] + default_ignore_names) - {'util.*'}))


def daemon():
    asyncio.run(
        lp_service.inst.run()
    )


def test_log_handler():
    Thread(target=daemon).start()

    handler = SyncHandler(Queue(), w3=bsc_web3)
    txh = '0x327a7a75e0f372847209878650d59078a1fc14ba6baa5003e5d8b3c2e745bd86'
    tx = bsc_web3.eth.get_transaction(txh)
    receipt = bsc_web3.eth.get_transaction_receipt(txh)

    trade = Trade.from_transaction(tx, receipt)
    asyncio.run(
        handler.handle_swap(trade)
    )
    print()
    print(trade.price_pair)


if __name__ == '__main__':
    test_log_handler()
