#!/usr/bin/env python3
# ©2024, Ovais Quraishi
"""Ollama-GPT module
"""

import hashlib
import logging
import os
import httpx

from ollama import AsyncClient
import openlit
from deepeval import evaluate
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric

from config import get_config
from encryption import encrypt_text
from logit import log_message_to_db, get_rollama_version
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
    openlit.init(otlp_endpoint=os.environ['OTLP_ENDPOINT_URL'], collect_gpu_stats=os.environ['COLLECT_GPU_STATS'])
    client = AsyncClient(host=os.environ['OLLAMA_API_URL'])
    logging.info('Running for %s', llm)
    try:
        response = await client.chat(
                                     model=llm,
                                     stream=False,
                                     messages=[
                                               {
                                                'role': 'user',
                                                'content': content
                                               },
                                              ],
                                     options = {
                                                'temperature' : 0.1
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
        log_message_to_db(os.environ['SRVC_NAME'], get_rollama_version(), 'ERROR', e)
        logging.error('%s',e.args[0])
        raise httpx.ConnectError('Unable to reach Ollama Server') from None

def test_answer_relevancy():
    """
        deepeval set-local-model --model-name=phi4 \
        --base-url="http://<OLLAMA URL>/v1/" \
        --api-key="ollama"
    """
    answer_relevancy_metric = AnswerRelevancyMetric(threshold=0.5)
    test_case = LLMTestCase(
        input="What is the recommended daily protein intake for adults?",
        actual_output="The recommended daily protein intake for adults is 0.8 grams per kilogram of body weight.",
        retrieval_context=["""Protein is an essential macronutrient that plays crucial roles in building and 
        repairing tissues.Good sources include lean meats, fish, eggs, and legumes. The recommended 
        daily allowance (RDA) for protein is 0.8 grams per kilogram of body weight for adults. 
        Athletes and active individuals may need more, ranging from 1.2 to 2.0 
        grams per kilogram of body weight."""]
    )
    evaluate([test_case], [answer_relevancy_metric])
