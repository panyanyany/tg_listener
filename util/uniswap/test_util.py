import importlib
from pathlib import Path

from web3.types import TxReceipt

from util.web3.util import bsc_web3


def get_tx_n_receipt(txh):
    try:
        module = importlib.import_module('util.uniswap.data.tx_and_receipt.' + txh)
        tx = module.tx_data
        rec = module.receipt_data
    except ModuleNotFoundError:
        tx = bsc_web3.eth.get_transaction(txh)
        rec: TxReceipt = bsc_web3.eth.get_transaction_receipt(txh)
        filepath = Path(__file__).parent.joinpath('data', 'tx_and_receipt', txh + '.py')
        with filepath.open('w+') as fp:
            fp.write("from hexbytes import HexBytes\n")
            fp.write("from web3.datastructures import AttributeDict\n")
            fp.write(f"tx_data = {str(tx)}\n")
            fp.write(f"receipt_data = {str(rec)}\n")
    return tx, rec
