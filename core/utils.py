import asyncio
import random

async def simulated_typing_delay(text: str, read_time: float = 0.0):
    """Wait for a human-like delay: reading time plus a typing time proportional to the text length."""
    write_time = len(text) * random.uniform(0.04, 0.06)
    total_delay = read_time + write_time

    await asyncio.sleep(total_delay)