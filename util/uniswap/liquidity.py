import dataclasses
import logging
from typing import Union

from web3.types import TxData, TxReceipt, EventData

from util.bsc.constants import wbnb
from util.bsc.token import canonicals, get_token_name
from util.eth.abi_force_decoder.decoder import Decoder, pancake_swap_router_signatures
from util.eth.log_decoder.log_decoder import LogDecoder

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class LiquidityChange:
    method_type: str

    token0: str
    amount0: int

    token1: str
    amount1: int

    timestamp: int = 0
    hash: str = ''
    operator: str = ''

    amount_in: dict = dataclasses.field(default_factory=dict)

    log_decoder = LogDecoder()
    router_decoder = Decoder(pancake_swap_router_signatures)

    @classmethod
    def from_transaction(cls, tx: TxData, receipt: TxReceipt, timestamp=0):
        fn_details = cls.router_decoder.decode(tx['input'])
        if not fn_details:
            return
        if receipt['status'] != 1 or len(receipt['logs']) == 0:
            return

        operator = tx['from'].lower()
        tx_contract = tx['to'].lower()
        fn_name = fn_details[0].fn_name
        fn_inputs = fn_details[1]
        if fn_name.startswith('add'):
            method_type = 'add'
        else:
            method_type = 'remove'

        if fn_name in ['addLiquidity', 'removeLiquidity', 'removeLiquidityWithPermit']:
            token0 = fn_inputs['tokenA']
            token1 = fn_inputs['tokenB']
        elif fn_name in ['addLiquidityETH', 'removeLiquidityETH', 'removeLiquidityETHSupportingFeeOnTransferTokens',
                         'removeLiquidityETHWithPermit', 'removeLiquidityETHWithPermitSupportingFeeOnTransferTokens']:
            token0 = fn_inputs['token']
            token1 = wbnb
        else:
            logger.warning('invalid liq function: %s, hash=%s', fn_name, tx['hex'].hex())
            return

        logs = []
        lp_addr = ''
        tokens = [token0.lower(), token1.lower()]
        amounts = dict(zip(tokens, [0, 0]))

        for i in range(len(receipt['logs']) - 1, -1, -1):
            log = receipt['logs'][i]
            logs.append(dict(log))
            try:
                dlog: Union[EventData, None] = cls.log_decoder.decode(log)
            except BaseException as e:
                logger.debug('cls.log_decoder.decode, i=%s, hash=%s', i, tx['hash'].hex(), exc_info=e)
                continue
            if not dlog:
                continue

            contract = dlog['address'].lower()
            if dlog['event'] == 'Sync':
                # 拿 lp 地址
                lp_addr = dlog['address'].lower()
            elif dlog['event'] == 'Transfer':
                if method_type == 'add':
                    if contract in amounts:
                        if dlog['args']['to'].lower() == lp_addr:
                            amounts[contract] += dlog['args']['value']
                if method_type == 'remove':
                    if contract in amounts:
                        if dlog['args']['from'].lower() == lp_addr:
                            amounts[contract] += dlog['args']['value']
                            # print(f"---- send {contract}: {dlog['args']['value']} = {amounts[contract]}")
                        # elif dlog['args']['from'].lower() == tx_contract:
                        #     amounts[contract] += dlog['args']['value']
                        #     print(f"---- router send {contract}: {dlog['args']['value']} = {amounts[contract]}")
            # elif dlog['event'] == 'Withdrawal':
            #     if method_type == 'remove' and 'ETH' in fn_name:
            #         """removeLiquidityETH* 之类的方法，eth 返回记录会出现在 Withdrawal 事件里, 而且不是直接返回给 op 的"""
            #         tokens.append(dlog['address'].lower())
            #         amounts.append(dlog['args']['wad'])

        if len(tokens) != 2:
            logger.warning(f'tokens == {len(tokens)}, txh={tx["hash"].hex()}')
            return
        self = cls(method_type=method_type, token0=tokens[0], token1=tokens[1], amount0=amounts[tokens[0]],
                   amount1=amounts[tokens[1]],
                   timestamp=timestamp, hash=tx['hash'].hex(), operator=operator)
        if self.token0 in canonicals:
            self.amount_in[get_token_name(self.token0)] = self.amount0
        elif self.token1 in canonicals:
            self.amount_in[get_token_name(self.token1)] = self.amount1
        return self
        # if fn_name in ['addLiquidityETH']:
        #     # addLiquidityETH {'token': '0x2054601f4aD0133F0282F3eba0F4A4Ef35630930', 'amountTokenDesired': 120000000000000000000, 'amountTokenMin': 115800000000000000000, 'amountETHMin': 1265719824869964415, 'to': '0x35d07887989F8dc40E49e3daad933Aa23E385182', 'deadline': 1647568403}
        #     pass
        # self = cls(method_type=method_type, fn_inputs)
