from hexbytes import HexBytes
from web3.datastructures import AttributeDict
tx_data = AttributeDict({'blockHash': HexBytes('0x520604962f7561994b29f7a15cfb759aa3f2ed6f242ae099bda0b50888d034be'), 'blockNumber': 16153574, 'from': '0x35d07887989F8dc40E49e3daad933Aa23E385182', 'gas': 261158, 'gasPrice': 5000000000, 'hash': HexBytes('0xe7f15771a3cfaca86dd109edd801ad83f1ca3e526e59ae5a370433032874d539'), 'input': '0xf305d7190000000000000000000000002054601f4ad0133f0282f3eba0f4a4ef356309300000000000000000000000000000000000000000000000068155a43676e00000000000000000000000000000000000000000000000000006470c3e771e3c00000000000000000000000000000000000000000000000000001190bd79828b3a7f00000000000000000000000035d07887989f8dc40e49e3daad933aa23e385182000000000000000000000000000000000000000000000000000000006233e613', 'nonce': 164, 'to': '0x10ED43C718714eb63d5aA57B78B54704E256024E', 'transactionIndex': 74, 'value': 1311626761523279187, 'type': '0x0', 'v': 148, 'r': HexBytes('0x2120c6e71ee4cbbc0baebc0ab51618e12c23d97eba71953a984b688c7c01eca9'), 's': HexBytes('0x1f484c63ce0137d2b22af23bd78d368a88849892d7594efe731b1dd925d51618')})
receipt_data = AttributeDict({'blockHash': HexBytes('0x520604962f7561994b29f7a15cfb759aa3f2ed6f242ae099bda0b50888d034be'), 'blockNumber': 16153574, 'contractAddress': None, 'cumulativeGasUsed': 10518782, 'from': '0x35d07887989F8dc40E49e3daad933Aa23E385182', 'gasUsed': 211183, 'logs': [AttributeDict({'address': '0x2054601f4aD0133F0282F3eba0F4A4Ef35630930', 'topics': [HexBytes('0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'), HexBytes('0x00000000000000000000000035d07887989f8dc40e49e3daad933aa23e385182'), HexBytes('0x000000000000000000000000919189364f27db48c27d467d96cc6d814f5212ca')], 'data': '0x00000000000000000000000000000000000000000000000010a741a462780000', 'blockNumber': 16153574, 'transactionHash': HexBytes('0xe7f15771a3cfaca86dd109edd801ad83f1ca3e526e59ae5a370433032874d539'), 'transactionIndex': 74, 'blockHash': HexBytes('0x520604962f7561994b29f7a15cfb759aa3f2ed6f242ae099bda0b50888d034be'), 'logIndex': 320, 'removed': False}), AttributeDict({'address': '0x2054601f4aD0133F0282F3eba0F4A4Ef35630930', 'topics': [HexBytes('0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'), HexBytes('0x00000000000000000000000035d07887989f8dc40e49e3daad933aa23e385182'), HexBytes('0x000000000000000000000000779bfd95476f1f532690aef062e2a70cc9f0c7cf')], 'data': '0x000000000000000000000000000000000000000000000000214e8348c4f00000', 'blockNumber': 16153574, 'transactionHash': HexBytes('0xe7f15771a3cfaca86dd109edd801ad83f1ca3e526e59ae5a370433032874d539'), 'transactionIndex': 74, 'blockHash': HexBytes('0x520604962f7561994b29f7a15cfb759aa3f2ed6f242ae099bda0b50888d034be'), 'logIndex': 321, 'removed': False}), AttributeDict({'address': '0x2054601f4aD0133F0282F3eba0F4A4Ef35630930', 'topics': [HexBytes('0x856af197d834c3fc3bb132a02f7e7e760a2ecd78ecc62fc02c35de22c99c5278')], 'data': '0x000000000000000000000000000000000000000000000000214e8348c4f0000000000000000000000000000035d07887989f8dc40e49e3daad933aa23e385182000000000000000000000000000000000000000000000000000000006233e184', 'blockNumber': 16153574, 'transactionHash': HexBytes('0xe7f15771a3cfaca86dd109edd801ad83f1ca3e526e59ae5a370433032874d539'), 'transactionIndex': 74, 'blockHash': HexBytes('0x520604962f7561994b29f7a15cfb759aa3f2ed6f242ae099bda0b50888d034be'), 'logIndex': 322, 'removed': False}), AttributeDict({'address': '0x2054601f4aD0133F0282F3eba0F4A4Ef35630930', 'topics': [HexBytes('0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'), HexBytes('0x00000000000000000000000035d07887989f8dc40e49e3daad933aa23e385182'), HexBytes('0x0000000000000000000000001370ee455b14a8b9945137ea4a9d00c3033e074a')], 'data': '0x0000000000000000000000000000000000000000000000064f5fdf494f780000', 'blockNumber': 16153574, 'transactionHash': HexBytes('0xe7f15771a3cfaca86dd109edd801ad83f1ca3e526e59ae5a370433032874d539'), 'transactionIndex': 74, 'blockHash': HexBytes('0x520604962f7561994b29f7a15cfb759aa3f2ed6f242ae099bda0b50888d034be'), 'logIndex': 323, 'removed': False}), AttributeDict({'address': '0x2054601f4aD0133F0282F3eba0F4A4Ef35630930', 'topics': [HexBytes('0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925'), HexBytes('0x00000000000000000000000035d07887989f8dc40e49e3daad933aa23e385182'), HexBytes('0x00000000000000000000000010ed43c718714eb63d5aa57b78b54704e256024e')], 'data': '0xffffffffffffffffffffffffffffffffffffffffffffffe8f29afde6f1cb5e30', 'blockNumber': 16153574, 'transactionHash': HexBytes('0xe7f15771a3cfaca86dd109edd801ad83f1ca3e526e59ae5a370433032874d539'), 'transactionIndex': 74, 'blockHash': HexBytes('0x520604962f7561994b29f7a15cfb759aa3f2ed6f242ae099bda0b50888d034be'), 'logIndex': 324, 'removed': False}), AttributeDict({'address': '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c', 'topics': [HexBytes('0xe1fffcc4923d04b559f4d29a8bfc6cda04eb5b0d3c460751c2402c5c5cc9109c'), HexBytes('0x00000000000000000000000010ed43c718714eb63d5aa57b78b54704e256024e')], 'data': '0x0000000000000000000000000000000000000000000000001233d5971e7db553', 'blockNumber': 16153574, 'transactionHash': HexBytes('0xe7f15771a3cfaca86dd109edd801ad83f1ca3e526e59ae5a370433032874d539'), 'transactionIndex': 74, 'blockHash': HexBytes('0x520604962f7561994b29f7a15cfb759aa3f2ed6f242ae099bda0b50888d034be'), 'logIndex': 325, 'removed': False}), AttributeDict({'address': '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c', 'topics': [HexBytes('0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'), HexBytes('0x00000000000000000000000010ed43c718714eb63d5aa57b78b54704e256024e'), HexBytes('0x0000000000000000000000001370ee455b14a8b9945137ea4a9d00c3033e074a')], 'data': '0x0000000000000000000000000000000000000000000000001233d5971e7db553', 'blockNumber': 16153574, 'transactionHash': HexBytes('0xe7f15771a3cfaca86dd109edd801ad83f1ca3e526e59ae5a370433032874d539'), 'transactionIndex': 74, 'blockHash': HexBytes('0x520604962f7561994b29f7a15cfb759aa3f2ed6f242ae099bda0b50888d034be'), 'logIndex': 326, 'removed': False}), AttributeDict({'address': '0x1370EE455b14a8b9945137Ea4A9d00c3033e074a', 'topics': [HexBytes('0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'), HexBytes('0x0000000000000000000000000000000000000000000000000000000000000000'), HexBytes('0x000000000000000000000000b1b9b4bbe8a92d535f5df2368e7fd2ecfb3a1950')], 'data': '0x000000000000000000000000000000000000000000000000009ac015894e6ec6', 'blockNumber': 16153574, 'transactionHash': HexBytes('0xe7f15771a3cfaca86dd109edd801ad83f1ca3e526e59ae5a370433032874d539'), 'transactionIndex': 74, 'blockHash': HexBytes('0x520604962f7561994b29f7a15cfb759aa3f2ed6f242ae099bda0b50888d034be'), 'logIndex': 327, 'removed': False}), AttributeDict({'address': '0x1370EE455b14a8b9945137Ea4A9d00c3033e074a', 'topics': [HexBytes('0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'), HexBytes('0x0000000000000000000000000000000000000000000000000000000000000000'), HexBytes('0x00000000000000000000000035d07887989f8dc40e49e3daad933aa23e385182')], 'data': '0x000000000000000000000000000000000000000000000000a4989309aa3fc7db', 'blockNumber': 16153574, 'transactionHash': HexBytes('0xe7f15771a3cfaca86dd109edd801ad83f1ca3e526e59ae5a370433032874d539'), 'transactionIndex': 74, 'blockHash': HexBytes('0x520604962f7561994b29f7a15cfb759aa3f2ed6f242ae099bda0b50888d034be'), 'logIndex': 328, 'removed': False}), AttributeDict({'address': '0x1370EE455b14a8b9945137Ea4A9d00c3033e074a', 'topics': [HexBytes('0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1')], 'data': '0x000000000000000000000000000000000000000000000ecdee78992a848a6bcb0000000000000000000000000000000000000000000000296d4b47345fbad5ec', 'blockNumber': 16153574, 'transactionHash': HexBytes('0xe7f15771a3cfaca86dd109edd801ad83f1ca3e526e59ae5a370433032874d539'), 'transactionIndex': 74, 'blockHash': HexBytes('0x520604962f7561994b29f7a15cfb759aa3f2ed6f242ae099bda0b50888d034be'), 'logIndex': 329, 'removed': False}), AttributeDict({'address': '0x1370EE455b14a8b9945137Ea4A9d00c3033e074a', 'topics': [HexBytes('0x4c209b5fc8ad50758f13e2e1088ba56a560dff690a1c6fef26394f4c03821c4f'), HexBytes('0x00000000000000000000000010ed43c718714eb63d5aa57b78b54704e256024e')], 'data': '0x0000000000000000000000000000000000000000000000064f5fdf494f7800000000000000000000000000000000000000000000000000001233d5971e7db553', 'blockNumber': 16153574, 'transactionHash': HexBytes('0xe7f15771a3cfaca86dd109edd801ad83f1ca3e526e59ae5a370433032874d539'), 'transactionIndex': 74, 'blockHash': HexBytes('0x520604962f7561994b29f7a15cfb759aa3f2ed6f242ae099bda0b50888d034be'), 'logIndex': 330, 'removed': False})], 'logsBloom': HexBytes('0x000046000000000000000000800000000000000000000000020000000100410000000000000010000000000000208800000000000000040000000000002000000000000000000000000000080000000000000200000400000004000080000000000000000200100000000000000008000000000000080000000000180000000000002000000000000000800000000000002400010000000800000040100000000200000000000000002000000200000000000004000000000000000000000000000000020004000000000000200200000000000000000010000000000000a0000010000000000000000000000000000020000000000000400000000100000000'), 'status': 1, 'to': '0x10ED43C718714eb63d5aA57B78B54704E256024E', 'transactionHash': HexBytes('0xe7f15771a3cfaca86dd109edd801ad83f1ca3e526e59ae5a370433032874d539'), 'transactionIndex': 74, 'type': '0x0'})