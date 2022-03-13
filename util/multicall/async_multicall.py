from multicall import Call, Multicall
from multicall.constants import MULTICALL2_ADDRESSES, MULTICALL2_BYTECODE
from multicall.multicall import get_multicall_map


class AsyncCall(Call):
    async def __call__(self, args=None):
        args = args or self.args
        calldata = self.signature.encode_data(args)

        args = [{'to': self.target, 'data': calldata}, self.block_id]

        no_state_override_args = args[:]

        if self.state_override_code:
            args.append({self.target: {'code': self.state_override_code}})

        try:
            output = await self.w3.eth.call(*args)
        except ValueError as val_error:
            print(f"{val_error} retrying without state override")
            output = await self.w3.eth.call(*no_state_override_args)

        return self.decode_output(output)


class AsyncMulticall(Multicall):
    async def __call__(self):
        if self.require_success is True:
            multicall_map = get_multicall_map(await self.w3.eth.chain_id)
            multicall_sig = 'aggregate((address,bytes)[])(uint256,bytes[])'
        else:
            multicall_map = MULTICALL2_ADDRESSES
            multicall_sig = 'tryBlockAndAggregate(bool,(address,bytes)[])(uint256,uint256,(bool,bytes)[])'

        aggregate = AsyncCall(
            multicall_map[await self.w3.eth.chain_id],
            multicall_sig,
            returns=None,
            _w3=self.w3,
            block_id=self.block_id,
            state_override_code=MULTICALL2_BYTECODE
        )

        if self.require_success is True:
            args = [[[call.target, call.data] for call in self.calls]]
            _, outputs = await aggregate(args)
            outputs = ((None, output) for output in outputs)
        else:
            args = [self.require_success, [[call.target, call.data] for call in self.calls]]
            _, _, outputs = await aggregate(args)

        result = {}
        for call, (success, output) in zip(self.calls, outputs):
            result.update(call.decode_output(output, success))

        return result
