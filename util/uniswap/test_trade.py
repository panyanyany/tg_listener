import json
from pathlib import Path

from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.types import TxData, TxReceipt

from util.uniswap.trade import Trade


def test_from_transaction():
    provider = "https://bsc-dataseed1.binance.org/"  # can also be set through the environment variable `PROVIDER`
    w3 = Web3(Web3.HTTPProvider(provider))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)  # 注入poa中间件

    testdata_list = [
        {'input': '0x8a47ae500e41ea481289fba363a2bd5cb10295c6a84e61b4fb07e7013ecd0065',
         'name': 'swapExactETHForTokens',
         'data': 'tx01',
         'result': Trade(operator='0xace0551614efd9e6b39d472b8fbd596ead5ac66d',
                         token_in='0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c',
                         token_out='0x62175af6D9B045D8435CDeDd9Bf542c7bcc56dCC', amount_in=1400000000000000000,
                         amount_out=3897884394388782861290)
         },
        {'input': '0xe4aa32946a1019fb8924bd91f3abef4e84c08d71540502217b45cf7912a58179',
         'name': 'swapExactTokensForETHSupportingFeeOnTransferTokens',
         'data': 'tx01',
         'result': Trade(operator='0x4fa40e5dd24eede393c7ddf53fcdb6ca887e096c',
                         token_in='0x4a72AF9609d22Bf2fF227AEC333c7d0860f3dB36',
                         token_out='0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c', amount_in=174662476028127148025,
                         amount_out=26898000225360219)
         },
        {'input': '0xe4502e017582a3786545d6b6a5b84c1e21a5c4fd1ac22266a4e304a9fa3a1853',
         'name': 'swapExactTokensForTokens',
         'data': 'tx01',
         'result': Trade(operator='0xb4cdb76c29ae0386885b1b33e4f14db5b1d16fc2',
                         token_in='0x0b15Ddf19D47E6a86A56148fb4aFFFc6929BcB89',
                         token_out='0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56', amount_in=5974633401444704152,
                         amount_out=4120002233909364804)
         },
        {'input': '0xb64f4dca8e981b1efd18c4265677dd8838e402a76e78b0f69bdd42557cd963d7',
         'name': 'swapTokensForExactTokens',
         'data': 'tx01',
         'result': Trade(operator='0x70e4995ef0b0730fe9a0ad711f4adeb6557c3fb3',
                         token_in='0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56',
                         token_out='0x3B3691d4C3EC75660f203F41adC6296a494404d0', amount_in=50027534254641814483,
                         amount_out=1241013201)
         },
    ]
    cur_dir = Path(__file__).parent
    for testdata in testdata_list:
        txh = testdata['input']
        tx = w3.eth.get_transaction(txh)
        rec: TxReceipt = w3.eth.get_transaction_receipt(txh)

        trade = Trade.from_transaction(tx, rec)
        assert trade == testdata['result']


if __name__ == '__main__':
    test_from_transaction()
