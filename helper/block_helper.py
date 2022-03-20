import asyncio
import logging
from datetime import datetime
from typing import List

from web3.exceptions import TransactionNotFound
from web3.types import TxData

from util.uniswap.trade import Trade
from util.web3.transaction import ExtendedTxData

logger = logging.getLogger(__name__)


class BlockHandler:
    pass


def extract_router_transactions(txs: List[ExtendedTxData]):
    # 检索出 swap 类型的交易
    swap_cnt = 0
    swap_transactions: [ExtendedTxData] = []
    liq_transactions: [ExtendedTxData] = []
    for tx in txs:
        tx: ExtendedTxData
        fn_details = Trade.router_decoder.decode(tx.input)
        if not fn_details:
            continue
        tx.fn_details = fn_details
        fn_name = fn_details[0].fn_name
        if 'swap' in fn_name.lower():
            swap_cnt += 1
            swap_transactions.append(tx)
        elif 'liq' in fn_name.lower():
            liq_transactions.append(tx)

    return swap_transactions, liq_transactions


async def load_receipts(w3, txs: List[ExtendedTxData]) -> List[ExtendedTxData]:
    if len(txs) == 0:
        return txs

    # txs2 = []
    # for tx in txs:
    #     tx2 = ExtendedTxData.from_tx_data(tx)
    #     txs2.append(tx2)

    # 请求交易结果
    async def get_receipt(tx: ExtendedTxData):
        start = datetime.now()
        max_secs = 20
        while (datetime.now() - start).total_seconds() < max_secs:
            try:
                tx.receipt = await w3.eth.get_transaction_receipt(tx.hash)
                return
            except TransactionNotFound:
                await asyncio.sleep(1)
                pass
            except BaseException as e:
                logger.warning('get receipt: %s, type=%s', e, type(e))
                await asyncio.sleep(1)

    # await asyncio.sleep(1)
    await asyncio.wait([
        get_receipt(tx) for tx in txs
    ], timeout=21)
    failed_cnt = 0
    for tx in txs:
        if not tx.receipt:
            failed_cnt += 1

    if failed_cnt > 0:
        logger.warning(f"load_receipts fail/total: {failed_cnt}/{len(txs)}")
    return txs
