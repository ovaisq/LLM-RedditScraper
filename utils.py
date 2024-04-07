# utils.py
# ©2024, Ovais Quraishi
"""Utility functions
"""

import datetime
import logging
import time
import random
import string
from datetime import datetime as DT


# substrings to be rplaced
TBR = ["As an AI language model, I don't have personal preferences or feelings. However,",
       "As an AI language model, I don't have personal preferences or opinions, but ",
       "I'm sorry to hear you're feeling that way! As an AI language model, I don't have access to real-time information on Hypmic or its future plans. However,",
       "As an AI language model, I don't have personal beliefs or experiences. However,",
       "I'm just an AI, I don't have personal beliefs or opinions, and I cannot advocate for or against any particular religion. However,",
       "As an AI, I don't have real-time information on specific individuals or their projects. However,"
      ]

def sanitize_string(a_string):
    """Search and replace AI model related text in strings"""

    for i in TBR:
        if i in a_string:
            a_string = a_string.replace(i,'FWIW - ')
    return a_string

def unix_ts_str():
    """Unix time as a string"""

    dt = str(int(time.time())) # unix time
    return dt

def unix_ts_int():
    """Unix time as a string"""

    dt = int(time.time()) # unix time
    return dt

def ts_int_to_dt_obj():
    """Convert Unix time to date time object for timestamp column in PostgreSQL table"""
    epoch_timestamp = unix_ts_int()
    datetime_object = DT.fromtimestamp(epoch_timestamp, tz=datetime.timezone.utc)
    return datetime_object

def gen_internal_id():
    """Generate 10 number internal document id"""

    ten_alpha_nums = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return ten_alpha_nums

def list_into_chunks(a_list, num_elements_chunk):
    """Split list into list of lists with each list containing
        num_elements_chunk elements
    """

    if len(a_list) > num_elements_chunk:
        for i in range(0, len(a_list), num_elements_chunk):
            yield a_list[i:i + num_elements_chunk]
    else:
        yield a_list

def sleep_to_avoid_429(counter):
    """Sleep for a random number of seconds to avoid 429
        TODO: handle status code from the API
        but it's better not to trigger the 429 at all...
    """

    counter += 1
    if counter > 23: # anecdotal magic number
        sleep_for = random.randrange(75, 445)
        logging.info("Sleeping for %s seconds", sleep_for)
        time.sleep(sleep_for)
        counter = 0
    return counter

def serialize_datetime(obj):
    """Data n Time object serialized for JSON
    """

    if isinstance(obj, (datetime.datetime, datetime.datetime)):
        return obj.isoformat()
    raise TypeError("Type not serializable")

def check_endpoint_health(url):
    """Check if endpoint is available
    """

    try:
        response = requests.head(url)
        if response.status_code == requests.codes.ok:
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        return False

def get_vals_list_of_dicts(dict_key, list_of_dicts):
    """Get values of a given key from a list of dictionaries
    """

    vals = [x[dict_key] for x in list_of_dicts]

    return vals
