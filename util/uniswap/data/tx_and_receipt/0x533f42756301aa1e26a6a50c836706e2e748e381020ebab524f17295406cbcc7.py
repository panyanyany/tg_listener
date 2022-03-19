from hexbytes import HexBytes
from web3.datastructures import AttributeDict
tx_data = AttributeDict({'blockHash': HexBytes('0xd662ff2d890e14bde82890b65a9adf9c7ff4c17be3094c52e00a72657c3969e0'), 'blockNumber': 15980697, 'from': '0x5d9c02dF43eeE4Dcd943a8Ff40e870a2ce39779f', 'gas': 238798, 'gasPrice': 5000000000, 'hash': HexBytes('0x533f42756301aa1e26a6a50c836706e2e748e381020ebab524f17295406cbcc7'), 'input': '0xfb3bdb410000000000000000000000000000000000000000000000006124fee993bc000000000000000000000000000000000000000000000000000000000000000000800000000000000000000000005d9c02df43eee4dcd943a8ff40e870a2ce39779f00000000000000000000000000000000000000000000000000000000622bf5fc0000000000000000000000000000000000000000000000000000000000000002000000000000000000000000bb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c000000000000000000000000e9e7cea3dedca5984780bafc599bd69add087d56', 'nonce': 635, 'to': '0x05fF2B0DB69458A0750badebc4f9e13aDd608C7F', 'transactionIndex': 45, 'value': 18777433070128717, 'type': '0x0', 'v': 147, 'r': HexBytes('0xecee87c28a4723801084060f7119d5902618c69b2f90e0704791e20e7fbe95b8'), 's': HexBytes('0x13641f997203c95616cdc21d21b56104c4ec45491e305a15acfdcf39cbfca16f')})
receipt_data = AttributeDict({'blockHash': HexBytes('0xd662ff2d890e14bde82890b65a9adf9c7ff4c17be3094c52e00a72657c3969e0'), 'blockNumber': 15980697, 'contractAddress': None, 'cumulativeGasUsed': 10958802, 'from': '0x5d9c02dF43eeE4Dcd943a8Ff40e870a2ce39779f', 'gasUsed': 133915, 'logs': [AttributeDict({'address': '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c', 'topics': [HexBytes('0xe1fffcc4923d04b559f4d29a8bfc6cda04eb5b0d3c460751c2402c5c5cc9109c'), HexBytes('0x00000000000000000000000005ff2b0db69458a0750badebc4f9e13add608c7f')], 'data': '0x000000000000000000000000000000000000000000000000004250230eb9e442', 'blockNumber': 15980697, 'transactionHash': HexBytes('0x533f42756301aa1e26a6a50c836706e2e748e381020ebab524f17295406cbcc7'), 'transactionIndex': 45, 'blockHash': HexBytes('0xd662ff2d890e14bde82890b65a9adf9c7ff4c17be3094c52e00a72657c3969e0'), 'logIndex': 307, 'removed': False}), AttributeDict({'address': '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c', 'topics': [HexBytes('0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'), HexBytes('0x00000000000000000000000005ff2b0db69458a0750badebc4f9e13add608c7f'), HexBytes('0x0000000000000000000000001b96b92314c44b159149f7e0303511fb2fc4774f')], 'data': '0x000000000000000000000000000000000000000000000000004250230eb9e442', 'blockNumber': 15980697, 'transactionHash': HexBytes('0x533f42756301aa1e26a6a50c836706e2e748e381020ebab524f17295406cbcc7'), 'transactionIndex': 45, 'blockHash': HexBytes('0xd662ff2d890e14bde82890b65a9adf9c7ff4c17be3094c52e00a72657c3969e0'), 'logIndex': 308, 'removed': False}), AttributeDict({'address': '0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56', 'topics': [HexBytes('0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'), HexBytes('0x0000000000000000000000001b96b92314c44b159149f7e0303511fb2fc4774f'), HexBytes('0x0000000000000000000000005d9c02df43eee4dcd943a8ff40e870a2ce39779f')], 'data': '0x0000000000000000000000000000000000000000000000006124fee993bc0000', 'blockNumber': 15980697, 'transactionHash': HexBytes('0x533f42756301aa1e26a6a50c836706e2e748e381020ebab524f17295406cbcc7'), 'transactionIndex': 45, 'blockHash': HexBytes('0xd662ff2d890e14bde82890b65a9adf9c7ff4c17be3094c52e00a72657c3969e0'), 'logIndex': 309, 'removed': False}), AttributeDict({'address': '0x1B96B92314C44b159149f7E0303511fB2Fc4774f', 'topics': [HexBytes('0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1')], 'data': '0x00000000000000000000000000000000000000000000009190e3cb2abbb9836500000000000000000000000000000000000000000000d5abca419895acfaad13', 'blockNumber': 15980697, 'transactionHash': HexBytes('0x533f42756301aa1e26a6a50c836706e2e748e381020ebab524f17295406cbcc7'), 'transactionIndex': 45, 'blockHash': HexBytes('0xd662ff2d890e14bde82890b65a9adf9c7ff4c17be3094c52e00a72657c3969e0'), 'logIndex': 310, 'removed': False}), AttributeDict({'address': '0x1B96B92314C44b159149f7E0303511fB2Fc4774f', 'topics': [HexBytes('0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822'), HexBytes('0x00000000000000000000000005ff2b0db69458a0750badebc4f9e13add608c7f'), HexBytes('0x0000000000000000000000005d9c02df43eee4dcd943a8ff40e870a2ce39779f')], 'data': '0x000000000000000000000000000000000000000000000000004250230eb9e442000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000006124fee993bc0000', 'blockNumber': 15980697, 'transactionHash': HexBytes('0x533f42756301aa1e26a6a50c836706e2e748e381020ebab524f17295406cbcc7'), 'transactionIndex': 45, 'blockHash': HexBytes('0xd662ff2d890e14bde82890b65a9adf9c7ff4c17be3094c52e00a72657c3969e0'), 'logIndex': 311, 'removed': False})], 'logsBloom': HexBytes('0x00200000000000100000000080000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000000000000000000000000000200000008000000200000000000000000000400008000000000000000100000000100000000000000000000000080000000000010200000000000000000000000000000000000000000040001000000080000004000000000000000000000000000000000000000000000000000000000002000000000000000000002000000020000000000001000000100000000001000100000000080000000000004000000000000000400002000000000000000400000000000000000'), 'status': 1, 'to': '0x05fF2B0DB69458A0750badebc4f9e13aDd608C7F', 'transactionHash': HexBytes('0x533f42756301aa1e26a6a50c836706e2e748e381020ebab524f17295406cbcc7'), 'transactionIndex': 45, 'type': '0x0'})
