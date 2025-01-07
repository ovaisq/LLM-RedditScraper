#!/usr/bin/env python3
# cache.py
# ©2024, Ovais Quraishi

"""Cache client"""

import redis
import logging
import os

# Import required local modules
import logit
from config import get_config
import external

get_config()


def redis_client() -> redis.StrictRedis:
    """Configure and return a Redis client instance."""

    host = os.environ["redis_host"]
    port = os.environ["redis_port"]
    password = os.environ["redis_password"]

    return redis.StrictRedis(host=host, port=port, password=password)


def add_key(key):
    """Add a key to a set in redis"""

    caching_srvc_crud_url = os.environ["caching_srvc_crud_url"]

    if lookup_key(key):
        info_message = f"{key} already exists"
        logging.info(info_message)
        logit.log_message_to_db(
            os.environ["SRVC_NAME"],
            logit.get_rollama_version()["version"],
            "INFO",
            info_message,
        )
        return False
    else:
        data_payload = {
            "command": "WRITE",
            "key": key,
            "value": "",
            "expire": 2592000,
        }  # Expires in 30 days
        json_resp = external.cache_api(caching_srvc_crud_url, payload=data_payload)
        if json_resp["status"] == "SUCCESS":
            info_message = f"{key} added"
            logging.info(info_message)
            logit.log_message_to_db(
                os.environ["SRVC_NAME"],
                logit.get_rollama_version()["version"],
                "INFO",
                info_message,
            )
            return True

def lookup_key(key):
    """Look up if a key exists"""

    caching_srvc_crud_url = os.environ["caching_srvc_crud_url"]

    data_payload = {"command": "READ", "key": key}
    json_resp = external.cache_api(caching_srvc_crud_url, payload=data_payload)
    if json_resp["status"] == "SUCCESS":
        return True
    else:
        return False


def get_set_contents(set_name):
    """Get contents of a redis set as a list"""

    # now use keys instead of sets
    byte_list = list(redis_client().scan_iter(set_name + "*"))
    string_list = [y.decode("utf-8") for y in byte_list]  # bytes to string

    # update list with just the ids
    for index, value in enumerate(string_list):
        if set_name in value:
            string_list[index] = value.replace(set_name + "_", "")

    return string_list
