#!/usr/bin/env python3
# cache.py
# ©2024, Ovais Quraishi

import redis
import logging
import os

# Import required local modules
import logit
from config import get_config
import external

get_config()
caching_srvc_crud_url = os.environ['caching_srvc_crud_url']

# connect to your Redis instance
r = redis.StrictRedis(host=os.environ['redis_host'],
                port=os.environ['redis_port'],
                password=os.environ['redis_password']
               )


def add_key(key):
    """Add a key to a set in redis"""

    if lookup_key(key):
        info_message = f'{key} already exists'
        logging.info(info_message)
        logit.log_message_to_db(os.environ['SRVC_NAME'], logit.get_rollama_version()['version'], 'INFO', info_message)
        return False
    else:
        data_payload = {"command": "WRITE", "key": key, "value" : "", "expire" : -1} #never expire
        json_resp = external.cache_api(caching_srvc_crud_url, payload=data_payload)
        if json_resp['status'] == 'SUCCESS':
            info_message = f'{key} added'
            logging.info(info_message)
            logit.log_message_to_db(os.environ['SRVC_NAME'], logit.get_rollama_version()['version'], 'INFO', info_message)
            return True

def lookup_key(key):
    """Look up if a key exists"""
    
    data_payload = {"command": "READ", "key": key}
    json_resp = external.cache_api(caching_srvc_crud_url, payload=data_payload)
    if json_resp['status'] == 'SUCCESS':
        return True
    else:
        return False

def get_set_contents(set_name):
    """Get contents of a redis set as a list"""

    return list(r.smembers(set_name))