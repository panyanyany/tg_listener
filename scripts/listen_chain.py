# main()
import asyncio
import logging
from signal import SIGTERM, SIGINT

from hanging_threads import start_monitoring

from tg_listener.repo.block_handler import BlockHandler
from tg_listener.repo.chain_listener import ChainListener
from util.log_util import setup3, default_ignore_names

start_monitoring(seconds_frozen=20, test_interval=1000)

setup3(ignore_names=['web3.*', 'asyncio'] + default_ignore_names)

# asyncio.run(main())

if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    listerner = ChainListener()
    worker = BlockHandler(listerner.queue)

    listerner.start()
    worker.start()


    def cancel():
        logging.info('stopping listener')
        listerner.stop()
        logging.info('stopping worker')
        worker.stop()


    for signal in [SIGINT, SIGTERM]:
        loop.add_signal_handler(signal, cancel)

    try:
        main_task = asyncio.ensure_future(worker.main())
        loop.run_until_complete(main_task)
        logging.info('run completed')
    # except asyncio.exceptions.CancelledError as e:
    #     pass
    except BaseException as e:
        logging.exception('run failed', e)
    finally:
        logging.info('finally')
        loop.close()
