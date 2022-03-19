from hexbytes import HexBytes
from web3.datastructures import AttributeDict

tx_data = AttributeDict({'blockHash': HexBytes('0x273004c599db110263aa028ee287578d551d053e3de55fdf0e52dc68dd73c64c'),
                         'blockNumber': 15647639, 'from': '0xaCE0551614efd9e6B39d472b8FbD596EaD5Ac66d', 'gas': 183306,
                         'gasPrice': 5000000000,
                         'hash': HexBytes('0x8a47ae500e41ea481289fba363a2bd5cb10295c6a84e61b4fb07e7013ecd0065'),
                         'input': '0x7ff36ab50000000000000000000000000000000000000000000000d317f8f92dc5b91a7a0000000000000000000000000000000000000000000000000000000000000080000000000000000000000000ace0551614efd9e6b39d472b8fbd596ead5ac66d00000000000000000000000000000000000000000000000000000000621ca2070000000000000000000000000000000000000000000000000000000000000002000000000000000000000000bb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c00000000000000000000000062175af6d9b045d8435cdedd9bf542c7bcc56dcc',
                         'nonce': 1, 'to': '0x10ED43C718714eb63d5aA57B78B54704E256024E', 'transactionIndex': 188,
                         'value': 1400000000000000000, 'type': '0x0', 'v': 147,
                         'r': HexBytes('0x74b43f90900a5f98ff91e8b8be47072f375e6c3d6c36ab2f515bb5516a0d0c56'),
                         's': HexBytes('0x3a99ae4c58bd33206d02790a2b2f0d579ee925ae7c524a685249ab71841d8196')})
receipt_data = AttributeDict(
    {'blockHash': HexBytes('0x273004c599db110263aa028ee287578d551d053e3de55fdf0e52dc68dd73c64c'),
     'blockNumber': 15647639, 'contractAddress': None, 'cumulativeGasUsed': 24853420,
     'from': '0xaCE0551614efd9e6B39d472b8FbD596EaD5Ac66d', 'gasUsed': 140845, 'logs': [AttributeDict(
        {'address': '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c',
         'topics': [HexBytes('0xe1fffcc4923d04b559f4d29a8bfc6cda04eb5b0d3c460751c2402c5c5cc9109c'),
                    HexBytes('0x00000000000000000000000010ed43c718714eb63d5aa57b78b54704e256024e')],
         'data': '0x000000000000000000000000000000000000000000000000136dcc951d8c0000', 'blockNumber': 15647639,
         'transactionHash': HexBytes('0x8a47ae500e41ea481289fba363a2bd5cb10295c6a84e61b4fb07e7013ecd0065'),
         'transactionIndex': 188,
         'blockHash': HexBytes('0x273004c599db110263aa028ee287578d551d053e3de55fdf0e52dc68dd73c64c'), 'logIndex': 746,
         'removed': False}), AttributeDict({'address': '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c', 'topics': [
        HexBytes('0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'),
        HexBytes('0x00000000000000000000000010ed43c718714eb63d5aa57b78b54704e256024e'),
        HexBytes('0x0000000000000000000000009129d017dcf6e6554c6a5aff461b3fdb1913d8e6')],
                                            'data': '0x000000000000000000000000000000000000000000000000136dcc951d8c0000',
                                            'blockNumber': 15647639, 'transactionHash': HexBytes(
            '0x8a47ae500e41ea481289fba363a2bd5cb10295c6a84e61b4fb07e7013ecd0065'), 'transactionIndex': 188,
                                            'blockHash': HexBytes(
                                                '0x273004c599db110263aa028ee287578d551d053e3de55fdf0e52dc68dd73c64c'),
                                            'logIndex': 747, 'removed': False}), AttributeDict(
        {'address': '0x62175af6D9B045D8435CDeDd9Bf542c7bcc56dCC',
         'topics': [HexBytes('0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'),
                    HexBytes('0x0000000000000000000000009129d017dcf6e6554c6a5aff461b3fdb1913d8e6'),
                    HexBytes('0x00000000000000000000000062175af6d9b045d8435cdedd9bf542c7bcc56dcc')],
         'data': '0x000000000000000000000000000000000000000000000014e5f5107a09141e03', 'blockNumber': 15647639,
         'transactionHash': HexBytes('0x8a47ae500e41ea481289fba363a2bd5cb10295c6a84e61b4fb07e7013ecd0065'),
         'transactionIndex': 188,
         'blockHash': HexBytes('0x273004c599db110263aa028ee287578d551d053e3de55fdf0e52dc68dd73c64c'), 'logIndex': 748,
         'removed': False}), AttributeDict({'address': '0x62175af6D9B045D8435CDeDd9Bf542c7bcc56dCC', 'topics': [
        HexBytes('0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'),
        HexBytes('0x0000000000000000000000009129d017dcf6e6554c6a5aff461b3fdb1913d8e6'),
        HexBytes('0x000000000000000000000000ace0551614efd9e6b39d472b8fbd596ead5ac66d')],
                                            'data': '0x0000000000000000000000000000000000000000000000d34e0334d1ea044bea',
                                            'blockNumber': 15647639, 'transactionHash': HexBytes(
            '0x8a47ae500e41ea481289fba363a2bd5cb10295c6a84e61b4fb07e7013ecd0065'), 'transactionIndex': 188,
                                            'blockHash': HexBytes(
                                                '0x273004c599db110263aa028ee287578d551d053e3de55fdf0e52dc68dd73c64c'),
                                            'logIndex': 749, 'removed': False}), AttributeDict(
        {'address': '0x9129d017dcf6E6554c6A5aFf461B3fdB1913D8e6',
         'topics': [HexBytes('0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1')],
         'data': '0x0000000000000000000000000000000000000000000041990b9a2d94c74296f70000000000000000000000000000000000000000000000058d06564a4f4bd26e',
         'blockNumber': 15647639,
         'transactionHash': HexBytes('0x8a47ae500e41ea481289fba363a2bd5cb10295c6a84e61b4fb07e7013ecd0065'),
         'transactionIndex': 188,
         'blockHash': HexBytes('0x273004c599db110263aa028ee287578d551d053e3de55fdf0e52dc68dd73c64c'), 'logIndex': 750,
         'removed': False}), AttributeDict({'address': '0x9129d017dcf6E6554c6A5aFf461B3fdB1913D8e6', 'topics': [
        HexBytes('0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822'),
        HexBytes('0x00000000000000000000000010ed43c718714eb63d5aa57b78b54704e256024e'),
        HexBytes('0x000000000000000000000000ace0551614efd9e6b39d472b8fbd596ead5ac66d')],
                                            'data': '0x0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000136dcc951d8c00000000000000000000000000000000000000000000000000e833f8454bf31869ed0000000000000000000000000000000000000000000000000000000000000000',
                                            'blockNumber': 15647639, 'transactionHash': HexBytes(
            '0x8a47ae500e41ea481289fba363a2bd5cb10295c6a84e61b4fb07e7013ecd0065'), 'transactionIndex': 188,
                                            'blockHash': HexBytes(
                                                '0x273004c599db110263aa028ee287578d551d053e3de55fdf0e52dc68dd73c64c'),
                                            'logIndex': 751, 'removed': False})], 'logsBloom': HexBytes(
        '0x00200200000000000000000080000000000000000000000000000000000000001000200000000010000000000000000000000000400000000020000000200000000000000000000000000008000000200200004000000000000400008000000000000000000000000000000000000000000020000000000000000010000000000000000000000000000000000000000000240001000000080000004080000000000000004000000210000000020000000000000000000000000000000000000000000002000000000000000000000000000000000000001000000000000080000000000000010000000000000000000000000000000000400000000000000000'),
     'status': 1, 'to': '0x10ED43C718714eb63d5aA57B78B54704E256024E',
     'transactionHash': HexBytes('0x8a47ae500e41ea481289fba363a2bd5cb10295c6a84e61b4fb07e7013ecd0065'),
     'transactionIndex': 188, 'type': '0x0'})
