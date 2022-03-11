# main()
import asyncio
import logging
from datetime import datetime
from signal import SIGTERM, SIGINT

from hanging_threads import start_monitoring
from web3 import Web3
from web3.eth import AsyncEth
from web3.middleware import async_geth_poa_middleware
from web3.types import BlockData

from helper.block_handler import extract_router_transactions, load_receipts
from tg_listener.repo.chain_listener import ChainListener
from util.log_util import setup3, default_ignore_names
from util.uniswap.trade import Trade
from util.web3.http_providers import AsyncConcurrencyHTTPProvider

# start_monitoring(seconds_frozen=20, test_interval=1000)


setup3(ignore_names=['web3.*', 'asyncio'] + default_ignore_names)

w3 = Web3(AsyncConcurrencyHTTPProvider(), modules={'eth': (AsyncEth,)}, middlewares=[])
w3.middleware_onion.inject(async_geth_poa_middleware, layer=0)  # 注入poa中间件

listerner = ChainListener()
block_queue = listerner.start()


async def main():
    while True:
        # 等待新的区块
        block: BlockData = block_queue.get()

        # 提取 uniswap 相关交易: swap & liq
        swap_transactions, liq_transactions = extract_router_transactions(block['transactions'])
        # 加载交易结果
        txs = await load_receipts(w3, swap_transactions + liq_transactions)
        # 不成功的不要
        txs = filter(lambda e: e.receipt and e.receipt.status == 1, txs)
        # 再次提取 uniswap 相关交易: swap & liq
        swap_transactions, liq_transactions = extract_router_transactions(txs)

        dt = datetime.fromtimestamp(block['timestamp'])
        now = datetime.now()
        logging.info(
            f"{now}"
            f", len(txs)={len(block['transactions'])}"
            f", swap_cnt={len(swap_transactions)}, liq_cnt={len(liq_transactions)}"
            f", {block['hash'].hex()}, {block['number']}, {dt}"
            f", delta={(now - dt).total_seconds()}"
            f", queue={block_queue.qsize()}"
        )

        # 把结果转换成可读交易类型
        trades = []
        for tx in swap_transactions:
            trade = Trade.from_transaction(tx.to_tx_data(), tx.receipt)
            if not trade:
                continue
            if trade.amount_in == 0 or trade.amount_out == 0:
                print(trade)


# asyncio.run(main())

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    main_task = asyncio.ensure_future(main())
    for signal in [SIGINT, SIGTERM]:
        loop.add_signal_handler(signal, main_task.cancel)
    try:
        loop.run_until_complete(main_task)
    finally:
        loop.close()
