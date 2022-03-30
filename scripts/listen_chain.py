import asyncio
import logging
from asyncio import Queue
from signal import SIGTERM, SIGINT

from tg_listener.repo.block_handler import BlockHandler
from tg_listener.repo.chain_listener import ChainListener, BlockNumberListener
from tg_listener.repo.db_handler import DbHandler
from tg_listener.repo.log_handler import SyncHandler
from tg_listener.repo.transaction_handler import SwapHandler
from tg_listener.services import lp_service, token_service, price_service
from util.log_util import setup3, default_ignore_names
from util.web3.util import async_bsc_web3

setup3(ignore_names=list(set(['web3.*', 'asyncio'] + default_ignore_names) - {'util.*'}), rm_parents=1)

# start_monitoring(seconds_frozen=20, test_interval=1000)

w3 = async_bsc_web3


def main():
    loop = asyncio.get_event_loop()

    binance_endpoints = [
        'https://bsc-dataseed1.binance.org/',
        "https://bsc-dataseed2.binance.org/",
        "https://bsc-dataseed3.binance.org/",
        "https://bsc-dataseed4.binance.org/",
    ]
    # async_binance_w3 = Web3(AsyncConcurrencyHTTPProvider().set_endpoints(binance_endpoints), modules={'eth': (AsyncEth,)}, middlewares=[])
    async_binance_w3 = async_bsc_web3

    block_number_listener = BlockNumberListener(w3=async_binance_w3)
    block_queue = Queue()
    chain_listener = ChainListener(w3=async_binance_w3, block_number_queue=block_number_listener.queue,
                                   block_queue=block_queue)
    block_handler = BlockHandler(block_queue=chain_listener.block_queue, w3=w3)

    # block_handler 的下游
    swap_handler = SwapHandler(block_handler.swaps_queue, w3=w3)
    # liq_handler = LiqHandler(block_handler.liq_queue, w3=w3)

    log_sync_handler = SyncHandler(swap_handler.trades_queue, w3=w3)

    div_handler = DbHandler(log_sync_handler.price_trades_queue, block_handler.liq_queue, w3=w3)

    handlers = [
        block_number_listener,
        chain_listener,
        block_handler,
        swap_handler,
        # liq_handler,
        log_sync_handler,
        div_handler,
        lp_service.inst,
        token_service.inst,
        price_service.inst,
    ]
    [h.start() for h in handlers]

    def cancel():
        logging.info('Ctrl-C detected! Stopping all handles...')
        for h in handlers:
            logging.info(f'stopping {h.__class__.__name__}')
            h.stop()

    for signal in [SIGINT, SIGTERM]:
        loop.add_signal_handler(signal, cancel)

    async def run_handlers():
        await asyncio.gather(
            *[h.run() for h in handlers],
        )

    logging.info('everything start')
    try:
        # main_task = asyncio.ensure_future(block_handler.main())
        # loop.run_until_complete(main_task)
        loop.run_until_complete(run_handlers())
        logging.info('run completed')
    # except asyncio.exceptions.CancelledError as e:
    #     pass
    finally:
        logging.info('finally')
        loop.close()


if __name__ == "__main__":
    main()
