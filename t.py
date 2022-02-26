import asyncio
import threading


def keep_alive():
    async def ping():
        while True:
            await asyncio.sleep(1)
            print('hi')

    asyncio.run(ping())


threading.Thread(target=keep_alive, daemon=True).start()

print('1')
