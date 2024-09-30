# utils.py
# ©2024, Ovais Quraishi
"""Utility functions
"""

import datetime
import json
import logging
import os
import requests
import time
import random
import string
from datetime import datetime as DT
import database
import logit

# substrings to be replaced
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

    if len(a_list) > 0:
        return [a_list[i:i + num_elements_chunk] for i in range(0, len(a_list), num_elements_chunk)]
    else:
        return None

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

def get_model_from_list(name):
    """Retrieve a model from a list of dictionaries based on the provided name.
    """

    # check if name contains a ':latest' suffix
    if ":" in name:
        actual_name = name
    else:
        actual_name = name+':latest'

    dicts = get_model_info(name)
    # find the matching dictionary
    for model in dicts:
        if model['name'] == actual_name:
            return model

    # if no match found, return None
    return None

def calculate_prompt_completion_time(start_time, end_time):
    """Number of seconds between start and end
    """

    return int(end_time - start_time)

def get_semver():
    """Hit the API endpoint for semantic version.
    """

    host = os.environ['OLLAMA_API_URL']
    url = f"{host}/api/version"

    response = requests.get(url)

    # check if the GET request was successful
    if response.status_code == 200:
        # extract semantic version from JSON
        semver = response.json()['version']

        return semver

    else:
        logging.error('Failed to get SemVer. Status code: %s', {response.status_code})
        return False

def get_model_info(llm):
    """Retrieve model information from a specified API endpoint.
    """
    
    host = os.environ['OLLAMA_API_URL']
    url = f"{host}/api/ps" # API URL for getting models

    response = requests.get(url)
    
    response.raise_for_status()
    
    models = response.json()['models']
    
    return models

def store_model_perf_info(llm, analyzed_obj, prompt_completion_time):
    """Store model performance information into a database table.
    """
    
    try:
        model_info_obj = get_model_from_list(llm)
        prompt_completion_info_obj = {
                                       'doc_shasum_512' : analyzed_obj['shasum_512'],
                                       'ollama_host' : '',
                                       'ollama_ver'  : analyzed_obj['ollama_ver'],
                                       'name' : model_info_obj['name'],
                                       'model' : model_info_obj['model'],
                                       'size' : model_info_obj['size'],
                                       'digest' : analyzed_obj['shasum_512'],
                                       'details' : json.dumps(model_info_obj['details']),
                                       'expires_at' : model_info_obj['expires_at'],
                                       'size_vram' : model_info_obj['size_vram'],
                                       'prompt_completion_time' : prompt_completion_time,
                                       'tokens_per_second' : analyzed_obj['tokens_per_second']
                                     }
        database.insert_data_into_table('prompt_completion_details', prompt_completion_info_obj)
    except Exception as e:
        error_message = f'{e}'
        logging.error(error_message)
        logit.log_message_to_db(os.environ['SRVC_NAME'], logit.get_rollama_version()['version'], 'ERROR', error_message)
        return None

def subtract_lists(list1, list2):
    """Subtract two lists and return a single list of contents"""

    return list(set(list1) - set(list2))
