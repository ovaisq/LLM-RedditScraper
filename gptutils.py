#!/usr/bin/env python3
# ©2024, Ovais Quraishi
"""Ollama-GPT module
"""

import hashlib
import logging
import os
import httpx

from ollama import AsyncClient

from config import get_config
from encryption import encrypt_text
from utils import ts_int_to_dt_obj
from utils import sanitize_string
from utils import get_semver

get_config()

async def prompt_chat(llm,
                      content,
                      encrypt_analysis=False,
                     ):
    """Llama Chat Prompting and response
    """

    dt = ts_int_to_dt_obj()
    OLLAMA_VER = get_semver()
    client = AsyncClient(host=os.environ['OLLAMA_API_URL'])
    logging.info('Running for %s', llm)
    try:
        response = await client.chat(
                                     model=llm,
                                     stream=False,
                                     messages=[
                                               {
                                                'role': 'user',
                                                'content': content,
                                                'keep_alive' : 0
                                               },
                                              ],
                                     options = {
                                                'temperature' : 0
                                               }
                                    )

        # chatgpt analysis
        analysis = response['message']['content']
        analysis = sanitize_string(analysis)
        tokens_per_second = (response['eval_count']/response['eval_duration'] * 1000000000)

        # this is for the analysis text only - the idea is to avoid
        #  duplicate text document, to allow indexing the column so
        #  to speed up search/lookups
        analysis_sha512 = hashlib.sha512(str.encode(analysis)).hexdigest()

        # see encryption.py module
        # encrypt text *** make sure that encryption key file is secure! ***

        if encrypt_analysis:
            analysis = encrypt_text(analysis).decode('utf-8')

        analyzed_obj = {
                        'timestamp' : dt,
                        'shasum_512' : analysis_sha512,
                        'analysis' : analysis,
                        'ollama_ver': OLLAMA_VER,
                        'tokens_per_second' : tokens_per_second
                        }

        return analyzed_obj, encrypt_analysis
    except (httpx.ReadError, httpx.ConnectError) as e:
        logging.error('%s',e.args[0])
        raise httpx.ConnectError('Unable to reach Ollama Server') from None
