import json
from pathlib import Path

from beeprint import pp
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.types import TxData, TxReceipt

from util.uniswap import test_util
from util.uniswap.liquidity import LiquidityChange
from util.uniswap.trade import Trade


def test_from_transaction():
    provider = "https://bsc-dataseed1.binance.org/"  # can also be set through the environment variable `PROVIDER`
    w3 = Web3(Web3.HTTPProvider(provider))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)  # 注入poa中间件

    testdata_list = [
        {'input': '0xe7f15771a3cfaca86dd109edd801ad83f1ca3e526e59ae5a370433032874d539',
         'name': 'addLiquidityETH',
         'result': LiquidityChange(method_type='add',
                                   token0='0x2054601f4ad0133f0282f3eba0f4a4ef35630930',
                                   amount0=116400000000000000000,
                                   token1='0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c',
                                   amount1=1311626761523279187,
                                   )
         },
        {'input': '0x535303462f40ec3254eb4eb51fa6c903a248502dd0c375696ec6773401c613c7',
         'name': 'removeLiquidityWithPermit',
         'result': LiquidityChange(method_type='remove',
                                   token0='0x54ce9d510cb4687fa52e1932b1803a7ec30edcdb',
                                   amount0=999995389,
                                   token1='0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c',
                                   amount1=554270204413414339,
                                   )
         },
        {'input': '0x18bcc7d8f1eec73df648bb64298e9e49c2f888fe1367f1aa15c4d3ec52c7fb5f',
         'name': 'removeLiquidityETHWithPermitSupportingFeeOnTransferTokens',
         'result': LiquidityChange(method_type='remove',
                                   token0='0x2b89540af369f8a197a5e340d3917216e8cf29aa',
                                   amount0=215222133,
                                   token1='0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c',
                                   amount1=1213635284009321947,
                                   )
         },
        {'input': '0x42f7880d5cc25d60147551965a218f4c736340c62e247f5340b3a2d5986d015c',
         'name': 'removeLiquidityETHWithPermit',
         'result': LiquidityChange(method_type='remove',
                                   token0='0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82',
                                   amount0=18991669037669324474,
                                   token1='0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c',
                                   amount1=313889847727023604,
                                   )
         },
        {'input': '0x4ccce10769cc0950d4f24a3ae1abb349f0fe3acdd91c14ec57e0d99275d6a128',
         'name': 'addLiquidity',
         'result': LiquidityChange(method_type='add',
                                   token0='0x47fb260e384c807c7f365f754239408cd1ff34f2',
                                   amount0=45560379273650879,
                                   token1='0xc9882def23bc42d53895b8361d0b1edc7570bc6a',
                                   amount1=44560778),
         }
    ]
    cur_dir = Path(__file__).parent
    for testdata in testdata_list[:]:
        txh = testdata['input']
        print('------- testing:', txh)
        tx, rec = test_util.get_tx_n_receipt(txh)

        # print()
        # pp(dict(tx))
        # print()
        # pp(dict(rec))

        trade = LiquidityChange.from_transaction(tx, rec)
        print()
        print(trade)
        print()
        if trade:
            trade.amount_in = {}
            trade.hash = ''
            trade.operator = ''
        # if testdata['result']:
        #     testdata['result'].hash = ''
        assert trade == testdata['result']


if __name__ == '__main__':
    test_from_transaction()
