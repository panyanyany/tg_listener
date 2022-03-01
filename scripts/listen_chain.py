import asyncio
import datetime
import time
from threading import Thread
from typing import Union, Sequence

from hexbytes import HexBytes
from web3 import Web3
from web3.middleware import geth_poa_middleware
from beeprint import pp
from web3.types import BlockData, TxData, LogReceipt

from util.eth.abi_force_decoder.decoder import Decoder, pancake_swap_router_signatures

provider = "https://bsc-dataseed1.binance.org/"  # can also be set through the environment variable `PROVIDER`
w3 = Web3(Web3.HTTPProvider(provider))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)  # 注入poa中间件

# print(pancake_swap_router_signatures)
decoder = Decoder(pancake_swap_router_signatures, w3)


# print(w3.eth.get_block('0x69c85120e58c6a24bd5e9f0969708edbb4132ccf37593a0b4d32b1113ffe9772'))
# print(w3.eth.get_block('0x2f90039e10886c14abd4360188a2dc31033ac8255dd035c34302e0abcc3ee348'))
# exit(0)


async def handle_event(i: HexBytes):
    # block_hash = i.hex()
    while True:
        try:
            block: BlockData = w3.eth.get_block(i, full_transactions=True)
            break
        except:
            await asyncio.sleep(0.2)
    dt = datetime.datetime.fromtimestamp(block['timestamp'])
    print('===== Block hash:  ', i.hex(), block['number'], dt)
    # and whatever


async def log_loop(event_filter, poll_interval):
    while True:
        for event in event_filter.get_new_entries():
            await handle_event(event)
        await asyncio.sleep(poll_interval)


def main():
    block_filter = w3.eth.filter('latest')
    # tx_filter = w3.eth.filter('pending')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                log_loop(block_filter, 0.25),
                # log_loop(tx_filter, 2),
            ),
        )
    finally:
        loop.close()


# worker = Thread(target=main, args=(), daemon=True)
# worker.start()
# while True:
#     time.sleep(1)

main()
exit(0)

block: BlockData = w3.eth.get_block('latest', True)
for tx in block.transactions:
    tx: Union[HexBytes, TxData]
    print(tx)
    exit()
    fn = decoder.decode(tx.input)
    if not fn:
        continue
    print(fn)
