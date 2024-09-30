# reddit_api.py
# ©2024, Ovais Quraishi
"""Reddit object
"""

import logging
import os
import praw
import logit
from praw import exceptions
from config import get_config

def create_reddit_instance():
    """Create and return a Reddit instance"""

    get_config()

    try:
        reddit = praw.Reddit(
                             client_id=os.environ['client_id'],
                             client_secret=os.environ['client_secret'],
                             password=os.environ['rpassword'],
                             user_agent=os.environ['user_agent'],
                             username=os.environ['username'],
                            )
        return reddit
    except exceptions.APIException as e:
        error_message = f'Unable to reach Reddit API: {e}'
        logging.error(error_message)
        logit.log_message_to_db(os.environ['SRVC_NAME'], logit.get_rollama_version()['version'], 'ERROR', error_message)
        raise
