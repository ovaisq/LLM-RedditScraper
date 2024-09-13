#!/usr/bin/env python3
"""Reddit client interaction utils
    ©2024, Ovais Quraishi
"""

import logging

from prawcore import exceptions

# Import required local modules
from config import get_config
from database import get_select_query_results
from reddit_api import create_reddit_instance

# constants
CONFIG = get_config()
REDDIT = create_reddit_instance()


def reply_post(post_id):
    """WIP"""
    # filter out non answers
    sql_query = f"""select
                        analysis_document ->> 'post_id' as post_id,
                        analysis_document ->> 'analysis' as analysis
                    from
                        analysis_documents
                    where
                        analysis_document ->> 'post_id' = '{post_id}'
                        and analysis_document ->> 'analysis' not like '%therefore I cannot answer this question.%';
                 """

    analyzed_data = get_select_query_results(sql_query)

    if analyzed_data:
        a_post = REDDIT.submission("1b0yadp")
        a_post.reply("WIP")

def get_upvote_count(post_id):
    """Get upvote count for a post id"""

    try:
        latest_post_upvote_count = REDDIT.submission(post_id).ups
        return latest_post_upvote_count
    except (AttributeError, TypeError, exceptions.NotFound) as e:
        logging.error("Error: %s", e)
        return False

def update_upvote_count(post_id, latest_post_upvote_count):
    """Update vote count for a given post_id(s)
        expects a list of 1 or more
    """

    column_name = "post_upvote_count"
    sql_query = ''

    sql_query = f"""UPDATE posts SET {column_name} = '{latest_post_upvote_count}' \
                    WHERE post_id = '{post_id}';"""
    if get_select_query_results(sql_query):
        logging.info('Post ID %s updated', post_id)
    else:
        logging.error('Post ID %s was not updated', post_id)