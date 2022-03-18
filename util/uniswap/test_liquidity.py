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
         'result': Trade(operator='0xace0551614efd9e6b39d472b8fbd596ead5ac66d',
                         token_in='0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c',
                         token_out='0x62175af6D9B045D8435CDeDd9Bf542c7bcc56dCC', amount_in=1400000000000000000,
                         amount_out=3897884394388782861290)
         },
    ]
    cur_dir = Path(__file__).parent
    for testdata in testdata_list[:]:
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
        if trade:
            trade.hash = ''
        if testdata['result']:
            testdata['result'].hash = ''
        assert trade == testdata['result']


if __name__ == '__main__':
    test_from_transaction()
