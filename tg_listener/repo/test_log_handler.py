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

    test_cases = [
        {'txh': '0x6842abd55496d13c33302a95f57b6e1801e7c6e4daff8ac977d272aa4e5d9de6',
         'quote_res': 1970738857726136908593356588, 'base_res': 3040978348579810725},
        {'txh': '0x327a7a75e0f372847209878650d59078a1fc14ba6baa5003e5d8b3c2e745bd86',
         'quote_res': 55000000000000, 'base_res': 129263336446045856},
        {'txh': '0xc97f35128576ea0d8e670e46d77f65b2eeab020bc6c34b1c3bf4e3ad9c8fc006',
         'quote_res': 100000000000, 'base_res': 63972},
    ]
    for test_case in test_cases:
        txh = test_case['txh']
        tx = bsc_web3.eth.get_transaction(txh)
        receipt = bsc_web3.eth.get_transaction_receipt(txh)

        trade = Trade.from_transaction(tx, receipt)
        asyncio.run(
            handler.handle_swap(trade)
        )
        print()
        print(trade.price_pair)
        assert trade.price_pair.quote_res == test_case['quote_res']
        assert trade.price_pair.base_res == test_case['base_res']


if __name__ == '__main__':
    test_log_handler()
