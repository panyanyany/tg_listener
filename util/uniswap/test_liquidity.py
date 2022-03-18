import json
from pathlib import Path

from beeprint import pp
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.types import TxData, TxReceipt

from util.uniswap.liquidity import Liquidity
from util.uniswap.trade import Trade


def test_from_transaction():
    provider = "https://bsc-dataseed1.binance.org/"  # can also be set through the environment variable `PROVIDER`
    w3 = Web3(Web3.HTTPProvider(provider))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)  # 注入poa中间件

    testdata_list = [
        {'input': '0xe7f15771a3cfaca86dd109edd801ad83f1ca3e526e59ae5a370433032874d539',
         'name': 'addLiquidityETH',
         'result': None
         },
        {'input': '0x535303462f40ec3254eb4eb51fa6c903a248502dd0c375696ec6773401c613c7',
         'name': 'removeLiquidityWithPermit',
         'result': None
         },
        {'input': '0x18bcc7d8f1eec73df648bb64298e9e49c2f888fe1367f1aa15c4d3ec52c7fb5f',
         'name': 'removeLiquidityETHWithPermitSupportingFeeOnTransferTokens',
         'result': None
         },
        {'input': '0x42f7880d5cc25d60147551965a218f4c736340c62e247f5340b3a2d5986d015c',
         'name': 'removeLiquidityETHWithPermit',
         'result': None
         },
    ]
    cur_dir = Path(__file__).parent
    for testdata in testdata_list[1:]:
        txh = testdata['input']
        tx = w3.eth.get_transaction(txh)
        # print(txh)
        rec: TxReceipt = w3.eth.get_transaction_receipt(txh)

        # print()
        # pp(dict(tx))
        # print()
        # pp(dict(rec))

        trade = Liquidity.from_transaction(tx, rec)
        print()
        print(trade)
        print()
        # if trade:
        #     trade.hash = ''
        # if testdata['result']:
        #     testdata['result'].hash = ''
        # assert trade == testdata['result']


if __name__ == '__main__':
    test_from_transaction()
