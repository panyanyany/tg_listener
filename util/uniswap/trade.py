from dataclasses import dataclass

from web3.types import TxData, TxReceipt

from util.bsc.constants import router, router2
from util.eth.abi_force_decoder.decoder import Decoder, pancake_swap_router_signatures
from util.eth.erc20.log_decoder import LogDecoder


@dataclass
class Trade:
    operator: str

    token_in: str
    token_out: str

    amount_in: int
    amount_out: int

    hash: str = ''

    log_decoder = LogDecoder()
    router_decoder = Decoder(pancake_swap_router_signatures)

    @classmethod
    def from_transaction(cls, tx: TxData, receipt: TxReceipt):
        fn_details = cls.router_decoder.decode(tx['input'])
        if not fn_details:
            return
        if receipt['status'] != 1 or len(receipt['logs']) == 0:
            return
        operator = tx['from'].lower()
        fn_name = fn_details[0].fn_name
        fn_inputs = fn_details[1]
        paths = fn_inputs['path']

        token_in = paths[0]
        token_out = paths[-1]

        raw_amount_in = fn_inputs.get('amountIn', 0)
        amount_in = 0
        amount_out = 0

        if fn_name in ['swapExactETHForTokens', 'swapExactETHForTokensSupportingFeeOnTransferTokens']:
            amount_in = tx['value']

        logs = []
        last_value = 0
        for log in receipt['logs']:
            logs.append(dict(log))
            smart_contract = log["address"]
            dlog = cls.log_decoder.decode(log)
            if not dlog:
                continue
            _from = dlog['args']['from'].lower()
            if _from == operator:
                amount_in += dlog['args']['value']
            elif _from == router:
                if fn_name == 'swapETHForExactTokens':
                    amount_in += dlog['args']['value']

            to = dlog['args']['to'].lower()
            last_value = dlog['args']['value']
            # router2 在这个交易会用到： 0xfcd695e238155d01a42e7fe0a3e668e32a8932e8df81b4e657910d4df08e3016
            if to in [router, operator, router2]:
                # 分红币分的同等数量的不知道啥玩意
                if _from == '0x0000000000000000000000000000000000000000':
                    pass
                else:
                    amount_out += dlog['args']['value']
            # print(f"Contract:{dlog['address']}, {dlog['event']}({dict(dlog['args'])})")

        # 最后一个可能是其他的 router
        if amount_out == 0:
            amount_out = last_value
        # print(f'amount_in={amount_in}/{raw_amount_in}, amount_out={amount_out}')
        return cls(operator=operator, token_in=token_in, token_out=token_out, amount_in=amount_in,
                   amount_out=amount_out,
                   hash=tx['hash'].hex(),
                   )
