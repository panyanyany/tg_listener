import asyncio

from multicall import Call

from util.bsc.constants import busd, usdt
from util.multicall.async_multicall import AsyncMulticall
from util.web3.util import async_bsc_web3

provider = "https://bsc-dataseed1.binance.org/"  # can also be set through the environment variable `PROVIDER`


async def main():
    calls = [
        Call(busd, ['decimals()(uint8)', ], [[busd, None]]),
        Call(usdt, ['decimals()(uint8)', ], [[usdt, None]]),
    ]
    multi = AsyncMulticall(calls, _w3=async_bsc_web3)
    results = await multi()
    print(results)


asyncio.run(main())
