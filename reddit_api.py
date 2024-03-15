# reddit_api.py
# ©2024, Ovais Quraishi
"""Reddit object
"""

import logging
import praw
from praw import exceptions
from config import get_config

def create_reddit_instance():
    """Create and return a Reddit instance"""

    config = get_config()
    try:
        reddit = praw.Reddit(
                             client_id=config.get('reddit', 'client_id'),
                             client_secret=config.get('reddit', 'client_secret'),
                             password=config.get('reddit', 'password'),
                             user_agent=config.get('reddit', 'user_agent'),
                             username=config.get('reddit', 'username'),
                            )
        return reddit
    except exceptions.APIException as e:
        logging.error("Unable to reach Reddit API: %s", e)
        raise
