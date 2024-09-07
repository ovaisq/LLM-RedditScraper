#!/usr/bin/env python3
"""Reddit client interaction utils
"""

# Import required local modules
from config import get_config
from database import get_select_query_results
from database import execute_query
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

def update_upvote_count(post_ids):
    """Update vote count for a given post_id(s)
        expects a list of 1 or more
    """

    column_name = "post_upvote_count"
    sql_query = ''

    # batch updates if list > 1
    if len(post_ids) > 1:
        for post_id in post_ids:
            latest_post_upvote_count = REDDIT.submission(post_id).ups
            sql_query += f"""UPDATE posts SET '{column_name}' = '{latest_post_upvote_count}' \
                            WHERE post_id = '{post_id}';"""
        execute_query(sql_query)
    else:
        for post_id in post_ids:
            latest_post_upvote_count = REDDIT.submission(post_id).ups
            sql_query = f"""UPDATE posts SET '{column_name}' = '{latest_post_upvote_count}' \
                            WHERE post_id = '{post_id}';"""
            execute_query(sql_query)