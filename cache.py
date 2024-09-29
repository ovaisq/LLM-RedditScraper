#!/usr/bin/env python3
# cache.py
# ©2024, Ovais Quraishi

import logging
import os
import redis

# Import required local modules
from config import get_config

# constants
get_config()

# connect to your Redis instance
r = redis.Redis(host=os.environ['redis_host'],
                port=os.environ['redis_port'],
                password=os.environ['redis_password']
               )

def add_key(setname, key):
    """Add a key to a set in redis"""

    if lookup_key(setname, key):
        logging.info('%s already exists', key)
        return False
    else:
        r.sadd(setname, key)
        logging.info('%s added', key)
        return True

def lookup_key(setname, key):
    """Look up if a key exists in the set"""

    return r.sismember(setname, key)

def get_set_contents(set_name):
    """Get contents of a redis set as a list"""

    return list(r.smembers(set_name))
