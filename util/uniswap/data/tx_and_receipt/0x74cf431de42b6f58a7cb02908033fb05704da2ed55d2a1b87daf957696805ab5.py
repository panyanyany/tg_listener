from hexbytes import HexBytes
from web3.datastructures import AttributeDict

tx_data = AttributeDict({'blockHash': HexBytes('0x3fd1204d83286e496845cae50db44bf96c69490f9b128a9c9967142519f2868e'),
                         'blockNumber': 16189627, 'from': '0x56C8f040d488d703D67a7E66323a11e9AAd0d415', 'gas': 185142,
                         'gasPrice': 6000000000,
                         'hash': HexBytes('0x74cf431de42b6f58a7cb02908033fb05704da2ed55d2a1b87daf957696805ab5'),
                         'input': '0x18cbafe5000000000000000000000000000000000000000000000001158e460913d0000000000000000000000000000000000000000000000000000000a8bb28c842266a00000000000000000000000000000000000000000000000000000000000000a000000000000000000000000056c8f040d488d703d67a7e66323a11e9aad0d41500000000000000000000000000000000000000000000000000000000623590ea000000000000000000000000000000000000000000000000000000000000000200000000000000000000000055d398326f99059ff775485246999027b31979550000000000000000000000000efb5fd2402a0967b92551d6af54de148504a115',
                         'nonce': 4, 'to': '0x1B6C9c20693afDE803B27F8782156c0f892ABC2d', 'transactionIndex': 46,
                         'value': 0, 'type': '0x0', 'v': 147,
                         'r': HexBytes('0xa7846830292bac10705217b90660067e728c8bd5ff60da3767f37ce69a972fc9'),
                         's': HexBytes('0x48a47c7e08cade5ea6e410e6ca8cdcf22dbdb3ea8faf7da35b9f301f83ec4ce4')})
receipt_data = AttributeDict(
    {'blockHash': HexBytes('0x3fd1204d83286e496845cae50db44bf96c69490f9b128a9c9967142519f2868e'),
     'blockNumber': 16189627, 'contractAddress': None, 'cumulativeGasUsed': 4505436,
     'from': '0x56C8f040d488d703D67a7E66323a11e9AAd0d415', 'gasUsed': 129003, 'logs': [AttributeDict(
        {'address': '0x55d398326f99059fF775485246999027B3197955',
         'topics': [HexBytes('0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'),
                    HexBytes('0x00000000000000000000000056c8f040d488d703d67a7e66323a11e9aad0d415'),
                    HexBytes('0x000000000000000000000000f615e5434d594dc0cc377f6c940fb052d28a1ae2')],
         'data': '0x000000000000000000000000000000000000000000000001158e460913d00000', 'blockNumber': 16189627,
         'transactionHash': HexBytes('0x74cf431de42b6f58a7cb02908033fb05704da2ed55d2a1b87daf957696805ab5'),
         'transactionIndex': 46,
         'blockHash': HexBytes('0x3fd1204d83286e496845cae50db44bf96c69490f9b128a9c9967142519f2868e'), 'logIndex': 117,
         'removed': False}), AttributeDict({'address': '0x55d398326f99059fF775485246999027B3197955', 'topics': [
        HexBytes('0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925'),
        HexBytes('0x00000000000000000000000056c8f040d488d703d67a7e66323a11e9aad0d415'),
        HexBytes('0x0000000000000000000000001b6c9c20693afde803b27f8782156c0f892abc2d')],
                                            'data': '0xfffffffffffffffffffffffffffffffffffffffffffffffeea71b9f6ec2fffff',
                                            'blockNumber': 16189627, 'transactionHash': HexBytes(
            '0x74cf431de42b6f58a7cb02908033fb05704da2ed55d2a1b87daf957696805ab5'), 'transactionIndex': 46,
                                            'blockHash': HexBytes(
                                                '0x3fd1204d83286e496845cae50db44bf96c69490f9b128a9c9967142519f2868e'),
                                            'logIndex': 118, 'removed': False}), AttributeDict(
        {'address': '0x0efb5FD2402A0967B92551d6AF54De148504A115',
         'topics': [HexBytes('0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'),
                    HexBytes('0x000000000000000000000000f615e5434d594dc0cc377f6c940fb052d28a1ae2'),
                    HexBytes('0x0000000000000000000000001b6c9c20693afde803b27f8782156c0f892abc2d')],
         'data': '0x00000000000000000000000000000000000000000000000000a99322960f47e3', 'blockNumber': 16189627,
         'transactionHash': HexBytes('0x74cf431de42b6f58a7cb02908033fb05704da2ed55d2a1b87daf957696805ab5'),
         'transactionIndex': 46,
         'blockHash': HexBytes('0x3fd1204d83286e496845cae50db44bf96c69490f9b128a9c9967142519f2868e'), 'logIndex': 119,
         'removed': False}), AttributeDict({'address': '0xf615e5434D594dC0cC377f6C940FB052D28A1AE2', 'topics': [
        HexBytes('0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1')],
                                            'data': '0x00000000000000000000000000000000000000000000000023ffd7d5a29f1ba700000000000000000000000000000000000000000000003bd4913aad5e9f1734',
                                            'blockNumber': 16189627, 'transactionHash': HexBytes(
            '0x74cf431de42b6f58a7cb02908033fb05704da2ed55d2a1b87daf957696805ab5'), 'transactionIndex': 46,
                                            'blockHash': HexBytes(
                                                '0x3fd1204d83286e496845cae50db44bf96c69490f9b128a9c9967142519f2868e'),
                                            'logIndex': 120, 'removed': False}), AttributeDict(
        {'address': '0xf615e5434D594dC0cC377f6C940FB052D28A1AE2',
         'topics': [HexBytes('0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822'),
                    HexBytes('0x0000000000000000000000001b6c9c20693afde803b27f8782156c0f892abc2d'),
                    HexBytes('0x0000000000000000000000001b6c9c20693afde803b27f8782156c0f892abc2d')],
         'data': '0x0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001158e460913d0000000000000000000000000000000000000000000000000000000a99322960f47e30000000000000000000000000000000000000000000000000000000000000000',
         'blockNumber': 16189627,
         'transactionHash': HexBytes('0x74cf431de42b6f58a7cb02908033fb05704da2ed55d2a1b87daf957696805ab5'),
         'transactionIndex': 46,
         'blockHash': HexBytes('0x3fd1204d83286e496845cae50db44bf96c69490f9b128a9c9967142519f2868e'), 'logIndex': 121,
         'removed': False}), AttributeDict({'address': '0x0efb5FD2402A0967B92551d6AF54De148504A115', 'topics': [
        HexBytes('0x7fcf532c15f0a6db0bd6d0e038bea71d30d808c7d98cb3bf7268a95bf5081b65'),
        HexBytes('0x0000000000000000000000001b6c9c20693afde803b27f8782156c0f892abc2d')],
                                            'data': '0x00000000000000000000000000000000000000000000000000a99322960f47e3',
                                            'blockNumber': 16189627, 'transactionHash': HexBytes(
            '0x74cf431de42b6f58a7cb02908033fb05704da2ed55d2a1b87daf957696805ab5'), 'transactionIndex': 46,
                                            'blockHash': HexBytes(
                                                '0x3fd1204d83286e496845cae50db44bf96c69490f9b128a9c9967142519f2868e'),
                                            'logIndex': 122, 'removed': False})], 'logsBloom': HexBytes(
        '0x00200000000000000800200080000001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000200000000000040040000041000008000000200402000000c00000000000000000000000000000000000000000000000000000000000000000040000000010000000000000000000000000008000000010000000000000000000080000004000000000020000000000000000000000000008000000001000000000000000010200000000000002000000000000000000000000200000000000001000000002000000000010000000000000000000000000000000000000000000000000000100000000'),
     'status': 1, 'to': '0x1B6C9c20693afDE803B27F8782156c0f892ABC2d',
     'transactionHash': HexBytes('0x74cf431de42b6f58a7cb02908033fb05704da2ed55d2a1b87daf957696805ab5'),
     'transactionIndex': 46, 'type': '0x0'})
