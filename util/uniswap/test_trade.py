import importlib
import json
from pathlib import Path

from beeprint import pp
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.types import TxData, TxReceipt

from util.uniswap import test_util
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
                         token_in='0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c',
                         token_out='0x62175af6d9b045d8435cdedd9bf542c7bcc56dcc', amount_in=1400000000000000000,
                         amount_out=3897884394388782861290)
         },
        {'input': '0xe4aa32946a1019fb8924bd91f3abef4e84c08d71540502217b45cf7912a58179',
         'name': 'swapExactTokensForETHSupportingFeeOnTransferTokens',
         'data': 'tx01',
         'result': Trade(operator='0x4fa40e5dd24eede393c7ddf53fcdb6ca887e096c',
                         token_in='0x4a72af9609d22bf2ff227aec333c7d0860f3db36',
                         token_out='0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c', amount_in=174662476028127148025,
                         amount_out=26898000225360219)
         },
        {'input': '0xe4502e017582a3786545d6b6a5b84c1e21a5c4fd1ac22266a4e304a9fa3a1853',
         'name': 'swapExactTokensForTokens',
         'data': 'tx01',
         'result': Trade(operator='0xb4cdb76c29ae0386885b1b33e4f14db5b1d16fc2',
                         token_in='0x0b15ddf19d47e6a86a56148fb4afffc6929bcb89',
                         token_out='0xe9e7cea3dedca5984780bafc599bd69add087d56', amount_in=5974633401444704152,
                         amount_out=4120002233909364804)
         },
        {'input': '0xb64f4dca8e981b1efd18c4265677dd8838e402a76e78b0f69bdd42557cd963d7',
         'name': 'swapTokensForExactTokens',
         'data': 'tx01',
         'result': Trade(operator='0x70e4995ef0b0730fe9a0ad711f4adeb6557c3fb3',
                         token_in='0xe9e7cea3dedca5984780bafc599bd69add087d56',
                         token_out='0x3b3691d4c3ec75660f203f41adc6296a494404d0', amount_in=50027534254641814483,
                         amount_out=1266340001)
         },
        {'input': '0xa7d8e9dfe5a4d53bce5e08d36415660b1f8f25401545c998e5cc6fc4dc959bb5',
         'name': 'swapETHForExactTokens',
         'data': 'tx01',
         'result': Trade(operator='0xfcd40e251e387ee9e1829ca0c882d5b7a6078a38',
                         token_in='0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c',
                         token_out='0x52419258e3fa44deac7e670eadd4c892b480a805', amount_in=12571431557544302,
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
                         token_in='0xa9776b590bfc2f956711b3419910a5ec1f63153e',
                         token_out='0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c',
                         amount_in=71000000000000000,
                         amount_out=19019168878003732, hash='')
         },
        # 其他 router
        {'input': '0x105e3130bf0027eceeeabaf52db3f63f4a08f7b4da4718c5326f26b56a1f97a4',
         'name': 'swapExactTokensForETHSupportingFeeOnTransferTokens',
         'data': 'tx01',
         'result': Trade(operator='0xfc0e59008d817fd57d90a7b1bab6ffb92cbadb07',
                         token_in='0x15104336cf1c5bb4281ed1e12fecc5a1197e5e36',
                         token_out='0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c', amount_in=600000000000000000000000000,
                         amount_out=191021198742087862,
                         hash='')
         },
        # 分红币
        {'input': '0xac367c95db801129797f9f30a1f7e99beb2a9c594f20761aaee262c6df0fb139',
         'name': 'swapExactTokensForTokensSupportingFeeOnTransferTokens',
         'data': 'tx01',
         'result': Trade(operator='0x4334cd7f02d826bcd87c40fca6c0502f1d34baf2',
                         token_in='0x55d398326f99059ff775485246999027b3197955',
                         token_out='0x38ae40d9f1897ba20aebf37bf6a9d36778aac3f3', amount_in=5000000000000000000,
                         amount_out=14684305240671903553278779239,
                         hash='')
         },
        {'input': '0x4d78ba4f991028b06a715a2809ea2ba0fee43d0fcb9e8d854ce476f8ecdef679',
         'name': 'swapETHForExactTokens',
         'data': 'tx01',
         'result': Trade(operator='0xc29057b7fa51bbbe3d100255eaf07c4eaa550952',
                         token_in='0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c',
                         token_out='0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d', amount_in=2522916503436603191,
                         amount_out=964000000000000000000, hash='')
         },
        {'input': '0xb3e6c2dd010d6f0dd833184b0c5034b862ecc98953de556ffa4898cac287d23d',
         'name': 'swapETHForExactTokens',
         'data': 'tx01',
         'result': Trade(operator='0xbe4b18882cd168a99653f852d9278d6d1d0e7634',
                         token_in='0x0efb5fd2402a0967b92551d6af54de148504a115',
                         token_out='0xc9882def23bc42d53895b8361d0b1edc7570bc6a', amount_in=98423455848077094,
                         amount_out=20000000,
                         hash='')
         },
        {'input': '0x533f42756301aa1e26a6a50c836706e2e748e381020ebab524f17295406cbcc7',
         'name': 'swapETHForExactTokens',
         'data': 'tx01',
         'result': Trade(operator='0x5d9c02df43eee4dcd943a8ff40e870a2ce39779f',
                         token_in='0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c',
                         token_out='0xe9e7cea3dedca5984780bafc599bd69add087d56', amount_in=18665459964044354,
                         amount_out=7000000000000000000,
                         hash='0x533f42756301aa1e26a6a50c836706e2e748e381020ebab524f17295406cbcc7')
         },
        {'input': '0x47e40fc2d5c8b662904c8a00819a0c945fe4def94570e464f38709564e16bc2d',
         'name': 'swapExactTokensForETHSupportingFeeOnTransferTokens',
         'data': 'tx01',
         'result': Trade(operator='0x6cb9cde9a33cd5eaeac2fc4b94571aed8d42d8db',
                         token_in='0xb0dbf009458759b7d5905d889e873b6127567958',
                         token_out='0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c',
                         amount_in=122868206380017714359106479551,
                         amount_out=305475729657822028,
                         )

         },
        {'input': '0x50b2391ef6573d68e4668bf1453c4c32859bf27f4ce5e271b6c5fb846ca1ab15',
         'name': 'swapExactETHForTokens',
         'data': '转给别人了',
         'result': Trade(operator='0xedae50ff773c74d8b7622acc78efb35d2e6c62e6',
                         token_in='0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c',
                         token_out='0xb5bd71d242536dc6b6e39fdde0a134f5db3dd2d7',
                         amount_in=291467591201096034,
                         amount_out=39895802382150,
                         )
         },
        {'input': '0xa51e860834428373abe2295bbfd2f3973f9d5eab70ceaf5f4123d9d13179675b',
         'name': 'swapExactTokensForTokensSupportingFeeOnTransferTokens',
         'data': 'wbnb没有withdrawal',
         'result': Trade(operator='0x8e7d8abc43054baf1d9aa2d5e2e7c1ff6ac08065',
                         token_in='0xd9ea58350bf120e2169a35fa1afc31975b07de01',
                         token_out='0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c', amount_in=869720953980004597760,
                         amount_out=641064815265531439,
                         )
         },
        {'input': '0x1bdba7049a089b5d50daa1afe0ece91eb20f9d2952c5a366fadb9093dd5514b4',
         'name': 'swapTokensForExactETH',
         'data': '山寨wbnb',
         'result': Trade(operator='0xf51b652888967f0331196b60829c78be0e08582c',
                         token_in='0x55d398326f99059ff775485246999027b3197955',
                         token_out='0x0efb5fd2402a0967b92551d6af54de148504a115', amount_in=24638250666181341371,
                         amount_out=60000000000000000,
                         )
         },
        {'input': '0x74cf431de42b6f58a7cb02908033fb05704da2ed55d2a1b87daf957696805ab5',
         'name': 'swapExactTokensForETH',
         'data': '山寨wbnb',
         'result': Trade(operator='0x56c8f040d488d703d67a7e66323a11e9aad0d415',
                         token_in='0x55d398326f99059ff775485246999027b3197955',
                         token_out='0x0efb5fd2402a0967b92551d6af54de148504a115', amount_in=20000000000000000000,
                         amount_out=47731047819855843,
                         )
         },
        # # amount_out 是 0
        # {'input': '0x5b8ee8c28e51e9ddb5f7b5b7b75bfdafbea9030e4ae378ee1210c0027468070f',
        #  'name': 'swapETHForExactTokens',
        #  'data': 'tx01',
        #  'result': Trade(operator='0x7e194da04f528272f479a4ae0932f7ac91dd6220',
        #                  token_in='0xcD9bc85C6b675DA994F172Debb6Db9BDD6727FE7',
        #                  token_out='0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c', amount_in=387142211041309,
        #                  amount_out=0, hash='0x5b8ee8c28e51e9ddb5f7b5b7b75bfdafbea9030e4ae378ee1210c0027468070f')
        #  },
    ]
    cur_dir = Path(__file__).parent
    # print()
    for testdata in testdata_list[:]:
        txh = testdata['input']
        # if txh != '0x105e3130bf0027eceeeabaf52db3f63f4a08f7b4da4718c5326f26b56a1f97a4':
        #     continue
        print('------- testing:', txh)
        tx, rec = test_util.get_tx_n_receipt(txh)

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
            trade.logs_sync = []
            trade.price_pair = None
            trade.is_dividend = False
        if testdata['result']:
            testdata['result'].hash = ''
        assert trade == testdata['result']


if __name__ == '__main__':
    test_from_transaction()
