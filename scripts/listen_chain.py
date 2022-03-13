import time

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

    chain_listener.start()
    block_handler.start()
    swap_handler.start()
    liq_handler.start()
    log_handler.start()


    def cancel():
        logging.info('stopping listener')
        chain_listener.stop()
        logging.info('stopping worker')
        block_handler.stop()
        logging.info('stopping swap_handler')
        swap_handler.stop()
        logging.info('stopping liq_handler')
        liq_handler.stop()
        logging.info('stopping log_handler')
        log_handler.stop()


    for signal in [SIGINT, SIGTERM]:
        loop.add_signal_handler(signal, cancel)


    async def main():
        await asyncio.gather(
            chain_listener.run(),
            block_handler.run(),
            swap_handler.run(),
            liq_handler.run(),
            log_handler.run(),
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
