import json
from pathlib import Path

from beeprint import pp
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
        {'input': '0xa7d8e9dfe5a4d53bce5e08d36415660b1f8f25401545c998e5cc6fc4dc959bb5',
         'name': 'swapETHForExactTokens',
         'data': 'tx01',
         'result': Trade(operator='0xfcd40e251e387ee9e1829ca0c882d5b7a6078a38',
                         token_in='0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c',
                         token_out='0x52419258E3fa44DEAc7E670eaDD4c892B480A805', amount_in=12571431557544302,
                         amount_out=12600000000)

         },
        {'input': '0x929e23445858fa6fbb56d73bc81dd799980f27f28721b0629d16016e6aadec96',
         'name': 'swapETHForExactTokens',
         'data': 'tx01',
         'result': None
         },
        # 会用到 router2
        {'input': '0xfcd695e238155d01a42e7fe0a3e668e32a8932e8df81b4e657910d4df08e3016',
         'name': 'swapExactTokensForETHSupportingFeeOnTransferTokens',
         'data': 'tx01',
         'result': Trade(operator='0x9dc37743319ffdeecfe5cd925e125a2a7252898d',
                         token_in='0xA9776B590bfc2f956711b3419910A5Ec1F63153E',
                         token_out='0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c',
                         amount_in=71000000000000000,
                         amount_out=19019168878003732, hash='')
         },
        # 其他 router
        {'input': '0x105e3130bf0027eceeeabaf52db3f63f4a08f7b4da4718c5326f26b56a1f97a4',
         'name': 'swapExactTokensForETHSupportingFeeOnTransferTokens',
         'data': 'tx01',
         'result': Trade(operator='0xfc0e59008d817fd57d90a7b1bab6ffb92cbadb07',
                         token_in='0x15104336cf1C5BB4281eD1E12fecc5A1197e5E36',
                         token_out='0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c', amount_in=540000000000000000000000000,
                         amount_out=191021198742087862,
                         hash='')
         },
        # 分红币
        {'input': '0xac367c95db801129797f9f30a1f7e99beb2a9c594f20761aaee262c6df0fb139',
         'name': 'swapExactTokensForTokensSupportingFeeOnTransferTokens',
         'data': 'tx01',
         'result': Trade(operator='0x4334cd7f02d826bcd87c40fca6c0502f1d34baf2',
                         token_in='0x55d398326f99059fF775485246999027B3197955',
                         token_out='0x38AE40D9F1897BA20aEbf37Bf6a9D36778aac3f3', amount_in=5000000000000000000,
                         amount_out=14684305240671903553278779239,
                         hash='')
         },
        {'input': '0x4d78ba4f991028b06a715a2809ea2ba0fee43d0fcb9e8d854ce476f8ecdef679',
         'name': 'swapETHForExactTokens',
         'data': 'tx01',
         'result': Trade(operator='0xc29057b7fa51bbbe3d100255eaf07c4eaa550952',
                         token_in='0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c',
                         token_out='0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d', amount_in=2522916503436603191,
                         amount_out=964000000000000000000, hash='')
         },
        {'input': '0xb3e6c2dd010d6f0dd833184b0c5034b862ecc98953de556ffa4898cac287d23d',
         'name': 'swapETHForExactTokens',
         'data': 'tx01',
         'result': Trade(operator='0xbe4b18882cd168a99653f852d9278d6d1d0e7634',
                         token_in='0x0efb5FD2402A0967B92551d6AF54De148504A115',
                         token_out='0xC9882dEF23bc42D53895b8361D0b1EDC7570Bc6A', amount_in=98423455848077094, amount_out=20000000,
                         hash='')
         },
        {'input': '0x533f42756301aa1e26a6a50c836706e2e748e381020ebab524f17295406cbcc7',
         'name': 'swapETHForExactTokens',
         'data': 'tx01',
         'result': Trade(operator='0x5d9c02df43eee4dcd943a8ff40e870a2ce39779f',
                         token_in='0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c',
                         token_out='0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56', amount_in=18665459964044354,
                         amount_out=7000000000000000000,
                         hash='0x533f42756301aa1e26a6a50c836706e2e748e381020ebab524f17295406cbcc7')
         },
        # 有点奇怪，amount_out 是 0
        # {'input': '0x21d95c96c408f76e6f2ac57274818c474343bfc916d9ba18b335a048c1f730a4',
        #  'name': 'swapETHForExactTokens',
        #  'data': 'tx01',
        #  'result': Trade(operator='0xc29057b7fa51bbbe3d100255eaf07c4eaa550952',
        #                  token_in='0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c',
        #                  token_out='0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d', amount_in=2523462800000000000,
        #                  amount_out=964000000000000000000, hash='')
        #  },
    ]
    cur_dir = Path(__file__).parent
    # print()
    for testdata in testdata_list[:]:
        txh = testdata['input']
        tx = w3.eth.get_transaction(txh)
        rec: TxReceipt = w3.eth.get_transaction_receipt(txh)

        # print()
        # pp(dict(tx))
        # print()
        # pp(dict(rec))

        trade = Trade.from_transaction(tx, rec)
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
