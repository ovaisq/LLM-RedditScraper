#!/usr/bin/env python3
"""Reddit client interaction utils
"""

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
        a_post = REDDIT.submission('1b0yadp')
        a_post.reply("WIP")
