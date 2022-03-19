from hexbytes import HexBytes
from web3.datastructures import AttributeDict

tx_data = AttributeDict({'blockHash': HexBytes('0x275b63ef1b1c7657f69767b0c7631ba88a9be8ea0b87d7bd869182dcfdbf429f'),
                         'blockNumber': 16189435, 'from': '0xf51B652888967F0331196B60829c78bE0E08582c', 'gas': 185157,
                         'gasPrice': 5355000000,
                         'hash': HexBytes('0x1bdba7049a089b5d50daa1afe0ece91eb20f9d2952c5a366fadb9093dd5514b4'),
                         'input': '0x4a25d94a00000000000000000000000000000000000000000000000000d529ae9e86000000000000000000000000000000000000000000000000000157a2503beafe7f0d00000000000000000000000000000000000000000000000000000000000000a0000000000000000000000000f51b652888967f0331196b60829c78be0e08582c0000000000000000000000000000000000000000000000000000000062358ea9000000000000000000000000000000000000000000000000000000000000000200000000000000000000000055d398326f99059ff775485246999027b31979550000000000000000000000000efb5fd2402a0967b92551d6af54de148504a115',
                         'nonce': 1, 'to': '0x1B6C9c20693afDE803B27F8782156c0f892ABC2d', 'transactionIndex': 18,
                         'value': 0, 'type': '0x0', 'v': 147,
                         'r': HexBytes('0xf61a0fe4f38367ce5047d1794b73d7e5aac4411b90971c1a5772c4e5a5aa7898'),
                         's': HexBytes('0x26600666d1ac327427e21e83adbc1fd9dea369263bc7bea57b4e8784a8279342')})
receipt_data = AttributeDict(
    {'blockHash': HexBytes('0x275b63ef1b1c7657f69767b0c7631ba88a9be8ea0b87d7bd869182dcfdbf429f'),
     'blockNumber': 16189435, 'contractAddress': None, 'cumulativeGasUsed': 1757433,
     'from': '0xf51B652888967F0331196B60829c78bE0E08582c', 'gasUsed': 129016, 'logs': [AttributeDict(
        {'address': '0x55d398326f99059fF775485246999027B3197955',
         'topics': [HexBytes('0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'),
                    HexBytes('0x000000000000000000000000f51b652888967f0331196b60829c78be0e08582c'),
                    HexBytes('0x000000000000000000000000f615e5434d594dc0cc377f6c940fb052d28a1ae2')],
         'data': '0x00000000000000000000000000000000000000000000000155eca6711cc530bb', 'blockNumber': 16189435,
         'transactionHash': HexBytes('0x1bdba7049a089b5d50daa1afe0ece91eb20f9d2952c5a366fadb9093dd5514b4'),
         'transactionIndex': 18,
         'blockHash': HexBytes('0x275b63ef1b1c7657f69767b0c7631ba88a9be8ea0b87d7bd869182dcfdbf429f'), 'logIndex': 48,
         'removed': False}), AttributeDict({'address': '0x55d398326f99059fF775485246999027B3197955', 'topics': [
        HexBytes('0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925'),
        HexBytes('0x000000000000000000000000f51b652888967f0331196b60829c78be0e08582c'),
        HexBytes('0x0000000000000000000000001b6c9c20693afde803b27f8782156c0f892abc2d')],
                                            'data': '0xfffffffffffffffffffffffffffffffffffffffffffffffeaa13598ee33acf44',
                                            'blockNumber': 16189435, 'transactionHash': HexBytes(
            '0x1bdba7049a089b5d50daa1afe0ece91eb20f9d2952c5a366fadb9093dd5514b4'), 'transactionIndex': 18,
                                            'blockHash': HexBytes(
                                                '0x275b63ef1b1c7657f69767b0c7631ba88a9be8ea0b87d7bd869182dcfdbf429f'),
                                            'logIndex': 49, 'removed': False}), AttributeDict(
        {'address': '0x0efb5FD2402A0967B92551d6AF54De148504A115',
         'topics': [HexBytes('0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'),
                    HexBytes('0x000000000000000000000000f615e5434d594dc0cc377f6c940fb052d28a1ae2'),
                    HexBytes('0x0000000000000000000000001b6c9c20693afde803b27f8782156c0f892abc2d')],
         'data': '0x00000000000000000000000000000000000000000000000000d529ae9e860000', 'blockNumber': 16189435,
         'transactionHash': HexBytes('0x1bdba7049a089b5d50daa1afe0ece91eb20f9d2952c5a366fadb9093dd5514b4'),
         'transactionIndex': 18,
         'blockHash': HexBytes('0x275b63ef1b1c7657f69767b0c7631ba88a9be8ea0b87d7bd869182dcfdbf429f'), 'logIndex': 50,
         'removed': False}), AttributeDict({'address': '0xf615e5434D594dC0cC377f6C940FB052D28A1AE2', 'topics': [
        HexBytes('0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1')],
                                            'data': '0x00000000000000000000000000000000000000000000000024476f37f2dd9dee00000000000000000000000000000000000000000000003b5ac44f2e731ed132',
                                            'blockNumber': 16189435, 'transactionHash': HexBytes(
            '0x1bdba7049a089b5d50daa1afe0ece91eb20f9d2952c5a366fadb9093dd5514b4'), 'transactionIndex': 18,
                                            'blockHash': HexBytes(
                                                '0x275b63ef1b1c7657f69767b0c7631ba88a9be8ea0b87d7bd869182dcfdbf429f'),
                                            'logIndex': 51, 'removed': False}), AttributeDict(
        {'address': '0xf615e5434D594dC0cC377f6C940FB052D28A1AE2',
         'topics': [HexBytes('0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822'),
                    HexBytes('0x0000000000000000000000001b6c9c20693afde803b27f8782156c0f892abc2d'),
                    HexBytes('0x0000000000000000000000001b6c9c20693afde803b27f8782156c0f892abc2d')],
         'data': '0x000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000155eca6711cc530bb00000000000000000000000000000000000000000000000000d529ae9e8600000000000000000000000000000000000000000000000000000000000000000000',
         'blockNumber': 16189435,
         'transactionHash': HexBytes('0x1bdba7049a089b5d50daa1afe0ece91eb20f9d2952c5a366fadb9093dd5514b4'),
         'transactionIndex': 18,
         'blockHash': HexBytes('0x275b63ef1b1c7657f69767b0c7631ba88a9be8ea0b87d7bd869182dcfdbf429f'), 'logIndex': 52,
         'removed': False}), AttributeDict({'address': '0x0efb5FD2402A0967B92551d6AF54De148504A115', 'topics': [
        HexBytes('0x7fcf532c15f0a6db0bd6d0e038bea71d30d808c7d98cb3bf7268a95bf5081b65'),
        HexBytes('0x0000000000000000000000001b6c9c20693afde803b27f8782156c0f892abc2d')],
                                            'data': '0x00000000000000000000000000000000000000000000000000d529ae9e860000',
                                            'blockNumber': 16189435, 'transactionHash': HexBytes(
            '0x1bdba7049a089b5d50daa1afe0ece91eb20f9d2952c5a366fadb9093dd5514b4'), 'transactionIndex': 18,
                                            'blockHash': HexBytes(
                                                '0x275b63ef1b1c7657f69767b0c7631ba88a9be8ea0b87d7bd869182dcfdbf429f'),
                                            'logIndex': 53, 'removed': False})], 'logsBloom': HexBytes(
        '0x00200000000000000800000080000000000000000000000000010000000000000000000000000000000000000000000000000000000000000000000000200000000000040040000041000008000000200402000000c00000000000000000000000000000000400000000000000000000000000000000040000000010000000000000000000000000008000000000000000000000000000080000004000000000020040000000000000000000000008000000001000000000000000010200000000000002000000000000000000000000200000000000001000000002000000000010000000000000000000000000000000000000000000000000000100000000'),
     'status': 1, 'to': '0x1B6C9c20693afDE803B27F8782156c0f892ABC2d',
     'transactionHash': HexBytes('0x1bdba7049a089b5d50daa1afe0ece91eb20f9d2952c5a366fadb9093dd5514b4'),
     'transactionIndex': 18, 'type': '0x0'})
