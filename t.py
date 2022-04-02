import asyncio


async def eternity():
    while True:
        print('x')
        await asyncio.sleep(0.5)


async def main():
    # Wait for at most 1 second
    try:
        await asyncio.wait_for(eternity(), timeout=1.0)
    except asyncio.TimeoutError:
        print('timeout!')
    await asyncio.sleep(5)


asyncio.run(main())
