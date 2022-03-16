import dataclasses
from dataclasses import dataclass
from typing import Union, Any

from eth_typing import BlockNumber, HexStr, ChecksumAddress
from hexbytes import HexBytes
from web3.types import TxData, AccessList, Wei, Nonce, TxReceipt, BlockData


@dataclass
class ExtendedTxData:
    blockHash: HexBytes
    blockNumber: BlockNumber
    from_: ChecksumAddress
    gas: Wei
    gasPrice: Wei
    hash: HexBytes
    input: HexStr
    nonce: Nonce
    r: HexBytes
    s: HexBytes
    to: ChecksumAddress
    transactionIndex: int
    type: Union[int, HexStr]
    v: int
    value: Wei
    data: Union[bytes, HexStr] = None
    maxFeePerGas: Wei = None
    maxPriorityFeePerGas: Wei = None
    chainId: int = None
    accessList: AccessList = None

    # 跟 TxData 不同之处
    receipt: TxReceipt = None
    fn_details: Any = None
    timestamp: int = 0

    def to_tx_data(self) -> TxData:
        d = dataclasses.asdict(self)
        d['from'] = d['from_']

        del d['receipt']
        del d['from_']
        return TxData(**d)

    @classmethod
    def from_tx_data(cls, block: BlockData, tx: TxData):
        tx = dict(tx)
        tx['from_'] = tx['from']
        tx['timestamp'] = block['timestamp']
        del tx['from']
        return cls(**tx)
