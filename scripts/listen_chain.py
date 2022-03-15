import time

from tg_listener.repo.dividend_handler import DividendHandler
from util.log_util import setup3, default_ignore_names
from util.web3.http_providers import AsyncConcurrencyHTTPProvider

import asyncio
import logging
from signal import SIGTERM, SIGINT

from tg_listener.repo.block_handler import BlockHandler
from tg_listener.repo.chain_listener import ChainListener
from tg_listener.repo.log_handler import SyncHandler
from tg_listener.repo.transaction_handler import SwapHandler, LiqHandler
from util.web3.util import async_bsc_web3

setup3(ignore_names=list(set(['web3.*', 'asyncio'] + default_ignore_names) - set(['util.*'])))

# start_monitoring(seconds_frozen=20, test_interval=1000)

w3 = async_bsc_web3

if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    chain_listener = ChainListener(w3=w3)
    block_handler = BlockHandler(chain_listener.queue, w3=w3)

    swap_handler = SwapHandler(block_handler.swap_queue, w3=w3)
    liq_handler = LiqHandler(block_handler.liq_queue, w3=w3)
    log_handler = SyncHandler(swap_handler.trade_queue, w3=w3)
    div_handler = DividendHandler(log_handler.extended_trade_queue, w3=w3)

    handlers = [
        chain_listener,
        block_handler,
        swap_handler,
        liq_handler,
        log_handler,
        div_handler,
    ]

    for h in handlers:
        h.start()


    def cancel():
        for h in handlers:
            logging.info(f'stopping {h.__class__.__name__}')
            h.stop()


    for signal in [SIGINT, SIGTERM]:
        loop.add_signal_handler(signal, cancel)


    async def main():
        await asyncio.gather(
            *[h.run() for h in handlers],
        )


    try:
        # main_task = asyncio.ensure_future(block_handler.main())
        # loop.run_until_complete(main_task)
        loop.run_until_complete(main())
        logging.info('run completed')
    # except asyncio.exceptions.CancelledError as e:
    #     pass
    finally:
        logging.info('finally')
        loop.close()
