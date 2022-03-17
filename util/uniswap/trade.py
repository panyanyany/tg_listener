import dataclasses
import json
import logging
import pickle
from dataclasses import dataclass, field
from typing import Union, Any, List

import redis
from multicall import Multicall, Call
from web3.types import TxData, TxReceipt, EventData

from util.bsc.constants import router, router2, cake, usdc
from util.bsc.pancake_swap.factory import factory
from util.bsc.token import has_canonical
from util.eth.abi_force_decoder.decoder import Decoder, pancake_swap_router_signatures
from util.eth.erc20 import Erc20
from util.eth.log_decoder.log_decoder import LogDecoder
from util.bsc.constants import wbnb, busd, usdt
from util.web3.pair import PricePair, sort_pair
from util.web3.util import bsc_web3, async_bsc_web3

StdToken = {
    wbnb: 'BNB',
    busd: 'BUSD',
    usdt: 'USDT',
    usdc: 'USDC',
    cake: 'CAKE',
}

RDB = redis.Redis(host='localhost', port=6379, db=0)

logger = logging.getLogger(__name__)


def get_token_name(token):
    return StdToken.get(token.lower(), token.lower())


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
    def from_transaction(cls, tx: TxData, receipt: TxReceipt, timestamp=0):
        fn_details = cls.router_decoder.decode(tx['input'])
        if not fn_details:
            return
        if receipt['status'] != 1 or len(receipt['logs']) == 0:
            return
        operator = tx['from'].lower()
        fn_name = fn_details[0].fn_name
        fn_inputs = fn_details[1]
        paths = fn_inputs['path']
        if not has_canonical(paths):
            return
        # print(f'paths: {paths}')

        self = cls(operator=operator, token_in=paths[0].lower(), token_out=paths[-1].lower(), amount_in=0, amount_out=0,
                   timestamp=timestamp,
                   hash=tx['hash'].hex().lower(), logs_sync=[])

        raw_amount_in = fn_inputs.get('amountIn', 0)

        if fn_name in ['swapExactETHForTokens',
                       'swapExactETHForTokensSupportingFeeOnTransferTokens',
                       # 'swapETHForExactTokens',
                       ]:
            self.amount_in = tx['value']

        logs = []
        last_value = 0
        sync_cnt = 0
        transfer_cnt = 0
        for i, log in enumerate(receipt['logs']):
            logs.append(dict(log))
            try:
                dlog: Union[EventData, None] = cls.log_decoder.decode(log)
            except BaseException as e:
                logger.debug('cls.log_decoder.decode, i=%s, hash=%s', i, tx['hash'].hex(), exc_info=e)
                continue
            if not dlog:
                continue
            if dlog['event'] == 'Transfer':
                transfer_cnt += 1
                last_value = self.handle_transfer(operator, fn_name, dlog, i, receipt['logs'])
            elif dlog['event'] == 'Swap':
                self.handle_swap(operator, fn_name, dlog, i, receipt['logs'])
            elif dlog['event'] == 'Sync':
                # self.handle_sync(paths, sync_cnt, dlog)
                self.logs_sync.append(dlog)
                sync_cnt += 1
            # print(f"Contract: {dlog['address']}, {dlog['event']}({dict(dlog['args'])})")

        if transfer_cnt > 4:
            # 转账日志大于4个，极有可能是分红币
            self.is_dividend = True
        # 最后一个可能是其他的 router
        if self.amount_out == 0:
            self.amount_out = last_value
        # print(f'amount_in={amount_in}/{raw_amount_in}, amount_out={amount_out}')
        return self

    def handle_sync(self, paths, sync_index, dlog):
        """根据 LP 变化，分析出交易后价格"""
        # token0 = paths[sync_index].lower()
        # token1 = paths[sync_index + 1].lower()
        # key0 = token0 + ':' + token1
        # key1 = token1 + ':' + token0
        #
        # # 拿 lp 地址
        # pair_addr = RDB.get(key0) or RDB.get(key1)
        # if not pair_addr:
        #     pair_addr = factory.get_pair(token0, token1)
        #     pair_addr = pair_addr.lower()
        #     RDB.set(key0, str(pair_addr).encode())
        # else:
        #     pair_addr = bytes(pair_addr).decode()
        pair_addr = dlog['address'].lower()

        # 拿 lp 里的 token0 和 token1
        pair_info = RDB.get(pair_addr)
        if not pair_info:
            multi = Multicall([
                Call(pair_addr, ['token0()(address)', ], [['token0', None]]),
                Call(pair_addr, ['token1()(address)', ], [['token1', None]]),
            ], _w3=bsc_web3)
            pair_info = multi()
            RDB.set(pair_addr, json.dumps(pair_info).encode())
        else:
            pair_info = json.loads(bytes(pair_info).decode())

        # print(pair_info)

        token0 = pair_info['token0'].lower()
        token1 = pair_info['token1'].lower()
        res0 = dlog['args']['reserve0']
        res1 = dlog['args']['reserve1']

        price_ok = True
        for std in [busd, usdt, wbnb]:
            price_ok = True
            if token0 == std:
                base_token = token0
                base_res = res0
                quote_token = token1
                quote_res = res1
            elif token1 == std:
                base_token = token1
                base_res = res1
                quote_token = token0
                quote_res = res0
            else:
                price_ok = False

            if price_ok:
                break

        if price_ok:
            # 拿 quote 的 decimals
            key = "decimals:" + quote_token
            quote_decimals = RDB.get(key)
            if quote_decimals is None:
                quote_decimals = Erc20(quote_token, web3=bsc_web3).decimals()
                RDB.set(key, pickle.dumps(quote_decimals))
            else:
                quote_decimals = pickle.loads(quote_decimals)

            quote_res_human = quote_res / (10 ** quote_decimals)
            base_res_human = base_res / (10 ** 18)

            # print('quote', quote_res)
            # print('base ', base_res)
            # print(f"{token_name(quote_token)} price: {base_res_human / quote_res_human} {token_name(base_token)}")
        else:
            # print('no price')
            pass

    @classmethod
    def calc_price(cls, dlog, token0, token1, decimals0, decimals1):
        pair = sort_pair(token0, token1, dlog['args']['reserve0'], dlog['args']['reserve1'], decimals0=decimals0,
                         decimals1=decimals1)
        if not pair:
            return None
        quote_res_human = pair.quote_res / (10 ** pair.quote_decimals)
        base_res_human = pair.base_res / (10 ** 18)

        pair = PricePair(**dataclasses.asdict(pair))
        pair.price = base_res_human / quote_res_human
        if pair.base_token in [busd, usdt, usdc]:
            pair.price_in['usd'] = pair.price
        elif pair.base_token in [wbnb]:
            pair.price_in['bnb'] = pair.price
        elif pair.base_token in [cake]:
            pair.price_in['cake'] = pair.price
        return pair

    def handle_swap(self, operator, fn_name, dlog, i, raw_logs):
        if i == len(raw_logs) - 1:
            if self.amount_in == 0:
                self.amount_in = dlog['args']['amount1In'] or dlog['args']['amount0In']
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
