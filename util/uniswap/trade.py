from dataclasses import dataclass

from web3.types import TxData, TxReceipt

from util.bsc.constants import router
from util.eth.abi_force_decoder.decoder import Decoder, pancake_swap_router_signatures
from util.eth.erc20.log_decoder import LogDecoder


@dataclass
class Trade:
    operator: str

    token_in: str
    token_out: str

    amount_in: int
    amount_out: int

    log_decoder = LogDecoder()
    router_decoder = Decoder(pancake_swap_router_signatures)

    @classmethod
    def from_transaction(cls, tx: TxData, receipt: TxReceipt):
        operator = tx['from'].lower()
        fn_details = cls.router_decoder.decode(tx.input)
        fn_name = fn_details[0].fn_name
        fn_inputs = fn_details[1]
        paths = fn_inputs['path']

        token_in = paths[0]
        token_out = paths[-1]

        raw_amount_in = fn_inputs.get('amountIn', 0)
        amount_in = 0
        amount_out = 0

        if fn_name == 'swapExactETHForTokens':
            amount_in = tx['value']

        logs = []
        for log in receipt.logs:
            logs.append(dict(log))
            smart_contract = log["address"]
            dlog = cls.log_decoder.decode(log)
            if not dlog:
                continue
            if dlog['args']['from'].lower() == operator:
                amount_in += dlog['args']['value']

            to = dlog['args']['to'].lower()
            if to == router.lower() or to == operator:
                amount_out += dlog['args']['value']
            print(f"Contract:{dlog['address']}, {dlog['event']}({dict(dlog['args'])})")

        print(f'amount_in={amount_in}/{raw_amount_in}, amount_out={amount_out}')
        return cls(operator=operator, token_in=token_in, token_out=token_out, amount_in=amount_in,
                   amount_out=amount_out)
