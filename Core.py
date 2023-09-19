import time
import asyncio


async def gather_dict(tasks: dict):
    async def mark(key, coro):
        try:
            return key, await coro
        except:
            return key, dict()

    return {
        key: result
        for key, result in await asyncio.gather(*(mark(key, coro) for key, coro in tasks.items()))
    }

def timeit(func):
    async def wrapper(*args, **kwargs):
        ts_start = int(time.time() * 1000)
        result = await func(*args, **kwargs)
        result['ts_start'] = ts_start
        result['ts_end'] = int(time.time() * 1000)
        return result
    return wrapper