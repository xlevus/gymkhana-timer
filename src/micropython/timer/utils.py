import random
import asyncio

def rand_str():
    return "%s.%s" % (
        random.getrandbits(32),
        random.getrandbits(32),
    )


async def _wait_first(event, coro):
    try:
        return await coro
    finally:
        event.set()


async def wait_first(awaitables):
    event = asyncio.Event()

    tasks = [asyncio.create_task(_wait_first(event, coro)) for coro in awaitables]

    await event.wait()

    try:
        for task in tasks:
            if task.done():
                return task, task.data
    finally:
        for task in tasks:
            task.cancel()
    