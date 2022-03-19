import dataclasses
import logging
from dataclasses import dataclass, field
from typing import Union, List

import redis
from web3.types import TxData, TxReceipt, EventData

from util.bsc.constants import router, router2, wbnb
from util.eth.abi_force_decoder.decoder import Decoder, pancake_swap_router_signatures
from util.eth.log_decoder.log_decoder import LogDecoder
from util.web3.pair import PricePair, sort_pair
from util.web3.transaction import ExtendedTxData

RDB = redis.Redis(host='localhost', port=6379, db=0)

logger = logging.getLogger(__name__)

functions_send_eth = {
    'swapETHForExactTokens',
    'swapExactETHForTokens',
    'swapExactETHForTokensSupportingFeeOnTransferTokens',
}


@dataclass
class Trade:
    operator: str

    token_in: str
    token_out: str

    amount_in: int
    amount_out: int

    timestamp: int = 0

    hash: str = ''

    price_pair: PricePair = None

    logs_sync: List[EventData] = field(default_factory=list)

    is_dividend: bool = False

    log_decoder = LogDecoder()
    router_decoder = Decoder(pancake_swap_router_signatures)

    def to_sorted_pair(self):
        return sort_pair(self.token_in, self.token_out, self.amount_in, self.amount_out)

    @classmethod
    def from_extended_tx(cls, tx: ExtendedTxData):
        return cls.from_transaction(tx.to_tx_data(), tx.receipt, fn_details=tx.fn_details, timestamp=tx.timestamp)

    @classmethod
    def from_transaction(cls, tx: TxData, receipt: TxReceipt, timestamp=0, fn_details=None):
        if not fn_details:
            fn_details = cls.router_decoder.decode(tx['input'])
            if not fn_details:
                # print('----- 1')
                return
        if receipt['status'] != 1 or len(receipt['logs']) == 0:
            # print('----- 2')
            return
        operator = tx['from'].lower()
        contract = tx['to'].lower()
        fn_name = fn_details[0].fn_name
        fn_inputs = fn_details[1]
        paths = list(map(lambda e: e.lower(), fn_inputs['path']))
        swap_receipt = fn_inputs['to'].lower()
        # if not has_canonical(paths):
        #     print('----- 3', paths)
        #     return
        # print(f'paths: {paths}')

        self = cls(operator=operator, token_in=paths[0], token_out=paths[-1], amount_in=0, amount_out=0,
                   timestamp=timestamp,
                   hash=tx['hash'].hex().lower(), logs_sync=[])

        raw_amount_in = fn_inputs.get('amountIn', 0)

        if fn_name in ['swapExactETHForTokens',
                       'swapExactETHForTokensSupportingFeeOnTransferTokens',
                       # 'swapETHForExactTokens',
                       ]:
            self.amount_in = tx['value']

        last_value = 0
        sync_cnt = 0
        transfer_cnt = 0
        for i, log in enumerate(receipt['logs']):
            try:
                dlog: Union[EventData, None] = cls.log_decoder.decode(log)
            except BaseException as e:
                logger.debug('cls.log_decoder.decode, i=%s, hash=%s', i, tx['hash'].hex(), exc_info=e)
                continue
            if not dlog:
                continue
            if dlog['event'] == 'Transfer':
                transfer_cnt += 1
                last_value = self.handle_transfer(operator, fn_name, dlog, i, receipt['logs'], paths, swap_receipt,
                                                  contract)
            elif dlog['event'] == 'Swap':
                self.handle_swap(operator, fn_name, dlog, i, receipt['logs'])
            elif dlog['event'] == 'Sync':
                # self.handle_sync(paths, sync_cnt, dlog)
                self.logs_sync.append(dlog)
                sync_cnt += 1
            elif dlog['event'] == 'Withdrawal':
                self.handle_withdrawal(operator, fn_name, dlog, paths)
            # print(f"Contract: {dlog['address']}, {dlog['event']}({dict(dlog['args'])})")

        if transfer_cnt > 4:
            # 转账日志大于4个，极有可能是分红币
            self.is_dividend = True
        # # 最后一个可能是其他的 router
        # if self.amount_out == 0:
        #     self.amount_out = last_value
        # print(f'amount_in={amount_in}/{raw_amount_in}, amount_out={amount_out}')

        if fn_name in (
                'swapExactTokensForETHSupportingFeeOnTransferTokens',
                'swapExactTokensForETHSupportingFeeOnTransferTokens'):
            # 由于有一部分 amount_in 作为手续费消耗掉了，所以日志中看不到，得从参数里拿
            self.amount_in = fn_inputs.get('amountIn')
        if fn_name in ('swapTokensForExactETH',
                       'swapTokensForExactTokens'):
            # exact* 方法
            self.amount_out = fn_inputs.get('amountOut')

        return self

    @classmethod
    def calc_price(cls, dlog, token0, token1, decimals0, decimals1, bnb_price=None, cake_price=None):
        pair = sort_pair(token0, token1, dlog['args']['reserve0'], dlog['args']['reserve1'], decimals0=decimals0,
                         decimals1=decimals1)
        if not pair:
            return None

        pair = PricePair(**dataclasses.asdict(pair), bnb_price=bnb_price, cake_price=cake_price).calc()
        return pair

    def handle_swap(self, operator, fn_name, dlog, i, raw_logs):
        if i == len(raw_logs) - 1:
            if self.amount_in == 0:
                self.amount_in = dlog['args']['amount1In'] or dlog['args']['amount0In']
            if self.amount_out == 0:
                self.amount_out = dlog['args']['amount1Out']

    def handle_transfer(self, operator, fn_name, dlog, i, raw_logs, paths, swap_receipt, tx_contract):
        _from = dlog['args']['from'].lower()
        to = dlog['args']['to'].lower()
        contract = dlog['address'].lower()
        # 计算 in
        if contract == paths[0]:
            if fn_name not in functions_send_eth:
                if _from == operator:
                    self.amount_in += dlog['args']['value']
                    # print(f'in ---- contract:{contract}, from={_from}', dlog['args']['value'], self.amount_in)
        elif contract == paths[-1]:  # 计算 out
            if contract == wbnb:
                if to == operator or to == swap_receipt:
                    self.amount_out = dlog['args']['value']
                # wbnb 的数量从 withdrawal 里拿
                # pass
            elif to == operator or to == swap_receipt:  # 有时候swap得到的token是可以转给别人的
                self.amount_out = dlog['args']['value']
            elif to == tx_contract:  # 如果实在找不到，那可能是直接给 router 了
                self.amount_out = dlog['args']['value']

        to = dlog['args']['to'].lower()
        last_value = dlog['args']['value']
        # # router2 在这个交易会用到： 0xfcd695e238155d01a42e7fe0a3e668e32a8932e8df81b4e657910d4df08e3016
        # if to in [router, operator, router2]:
        #     # 分红币分的同等数量的不知道啥玩意
        #     if _from == '0x0000000000000000000000000000000000000000':
        #         pass
        #     else:
        #         self.amount_out += dlog['args']['value']

        return last_value

    def handle_withdrawal(self, operator, fn_name, dlog, paths):
        contract = dlog['address'].lower()
        if fn_name not in functions_send_eth:
            if contract == paths[0]:
                pass
            elif contract == paths[-1]:
                if contract == wbnb:
                    # 不要加，因为真可能出现多个 withdrawal: 0x105e3130bf0027eceeeabaf52db3f63f4a08f7b4da4718c5326f26b56a1f97a4
                    self.amount_out = dlog['args']['wad']
                    # print(f'out ---- contract:{contract}, withdrawal:', dlog['args']['wad'], self.amount_out)
