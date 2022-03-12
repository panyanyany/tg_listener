from dataclasses import dataclass
from typing import Union

from web3.types import TxData, TxReceipt, EventData

from util.bsc.constants import router, router2
from util.eth.abi_force_decoder.decoder import Decoder, pancake_swap_router_signatures
from util.eth.log_decoder.log_decoder import LogDecoder


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

        self = cls(operator=operator,
                   token_in=paths[0],
                   token_out=paths[-1],
                   amount_in=0,
                   amount_out=0,
                   hash=tx['hash'].hex(),
                   )

        raw_amount_in = fn_inputs.get('amountIn', 0)

        if fn_name in ['swapExactETHForTokens',
                       'swapExactETHForTokensSupportingFeeOnTransferTokens',
                       # 'swapETHForExactTokens',
                       ]:
            self.amount_in = tx['value']

        logs = []
        last_value = 0
        for i, log in enumerate(receipt['logs']):
            logs.append(dict(log))
            dlog: Union[EventData, None] = cls.log_decoder.decode(log)
            if not dlog:
                continue
            if dlog['event'] == 'Transfer':
                last_value = self.handle_transfer(operator, fn_name, dlog, i, receipt['logs'])
            elif dlog['event'] == 'Swap':
                self.handle_swap(operator, fn_name, dlog, i, receipt['logs'])
            # print(f"Contract: {dlog['address']}, {dlog['event']}({dict(dlog['args'])})")

        # 最后一个可能是其他的 router
        if self.amount_out == 0:
            self.amount_out = last_value
        # print(f'amount_in={amount_in}/{raw_amount_in}, amount_out={amount_out}')
        return self

    def handle_swap(self, operator, fn_name, dlog, i, raw_logs):
        if i == len(raw_logs) - 1:
            if self.amount_in == 0:
                self.amount_in = dlog['args']['amount1In']
            if self.amount_out == 0:
                self.amount_out = dlog['args']['amount1Out']

    def handle_transfer(self, operator, fn_name, dlog, i, raw_logs):
        _from = dlog['args']['from'].lower()
        if _from == operator:
            self.amount_in += dlog['args']['value']
        elif _from == router:
            if fn_name == 'swapETHForExactTokens':
                self.amount_in += dlog['args']['value']

        to = dlog['args']['to'].lower()
        last_value = dlog['args']['value']
        # router2 在这个交易会用到： 0xfcd695e238155d01a42e7fe0a3e668e32a8932e8df81b4e657910d4df08e3016
        if to in [router, operator, router2]:
            # 分红币分的同等数量的不知道啥玩意
            if _from == '0x0000000000000000000000000000000000000000':
                pass
            else:
                self.amount_out += dlog['args']['value']

        return last_value
