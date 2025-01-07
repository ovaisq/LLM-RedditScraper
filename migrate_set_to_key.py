#!/usr/bin/env python3
# ©2024, Ovais Quraishi

"""Copy contents of a given Redis Set to a Key"""

import asyncio
import os
import redis

# Import required local modules
from config import get_config

get_config()

def redis_client() -> redis.StrictRedis:
    """Configure and return a Redis client instance."""

    host = os.environ["redis_host"]
    port = os.environ["redis_port"]
    password = os.environ["redis_password"]

    return redis.StrictRedis(host=host, port=port, password=password)

def get_set_value(set_name):
    """Get Set values, and return a pythonic list"""

    byte_list = redis_client().smembers(set_name)
    string_list = [set_name + '_' + z.decode("utf-8") for z in byte_list]  # bytes to string

    return string_list

def get_key(key):
    """Read key"""

    a_key = redis_client().get(key)

    return a_key

async def add_key(key):
    """Add Key"""

    redis_client().set(key, '')

    return

async def worker(a_val):
    """Async function"""

    if get_key(a_val) is not None:
        print('Key Already Exists:', a_val)
    else:
        await add_key(a_val)
        if get_key(a_val) is not None:
            print('Key Added:', a_val)
        else:
            print('Key Not Found:', a_val)


async def main():
    """Main"""

    # get set values as a pythonic list
    set_list = get_set_value('comment_id')

    tasks = []

    for a_val in set_list:
        task = asyncio.create_task(worker(a_val))
        tasks.append(task)

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    # run the program using the asyncio event loop 
    #  started at the top level.

    asyncio.run(main())
