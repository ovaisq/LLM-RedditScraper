# database.py
# ©2024, Ovais Quraishi
"""DB Utils
"""

import logging
import os
import psycopg2
from psycopg2 import sql
import cache
from config import get_config
from utils import subtract_lists
import logit

get_config()

def psql_connection(cursorfactory=None):
    """Connect to PostgreSQL server"""

    db_config = {
                 'host' : os.environ['host'],
                 'database' : os.environ['database'],
                 'user' : os.environ['user'],
                 'password' : os.environ['password'],
                 'port' : os.environ['port']
                }
    try:
        psql_conn = psycopg2.connect(**db_config)
        psql_cur = psql_conn.cursor(cursor_factory=cursorfactory)
        return psql_conn, psql_cur
    except psycopg2.Error as e:
        error_message = f'Error connecting to PostgreSQL: {e}'
        logging.error(error_message)
        logit.log_message_to_db(os.environ['SRVC_NAME'], logit.get_rollama_version()['version'], 'ERROR', error_message)
        raise

def execute_query(sql_query):
    """Execute a SQL query"""

    conn, cur = psql_connection()
    try:
        cur.execute(sql_query)
        result = cur.fetchall()
        conn.close()
        return result
    except psycopg2.Error as e:
        error_message = f'{e}'
        logging.error(error_message)
        logit.log_message_to_db(os.environ['SRVC_NAME'], logit.get_rollama_version()['version'], 'ERROR', error_message)
        raise

def insert_data_into_table(table_name, data):
    """Insert data into table"""

    conn, cur = psql_connection()
    try:
        placeholders = ', '.join(['%s'] * len(data))
        columns = sql.SQL(', ').join(map(sql.Identifier, data.keys()))
        table = sql.Identifier(table_name)
        sql_query = sql.SQL("""INSERT INTO {} ({}) VALUES ({}) ON CONFLICT DO NOTHING;""").format(
            table, columns, sql.SQL(placeholders))
        cur.execute(sql_query, list(data.values()))
        conn.commit()
        info_message = f'Inserted into {table_name}'
        logging.info(info_message)
        if table_name not in ['rollamalogs','servicelogs']:
            logit.log_message_to_db(os.environ['SRVC_NAME'], logit.get_rollama_version()['version'], 'INFO', info_message)
    except psycopg2.Error as e:
        logging.error("%s", e)
        conn.close()
        raise

def get_select_query_results(sql_query, params=None):
    """Execute a query, return all rows for the query
    """

    conn, cur = psql_connection()
    try:
        cur.execute(sql_query, params)
        # For SELECT query
        if sql_query.upper().strip().startswith('SELECT'):
            result = cur.fetchall()
            return result
        else:
            # For UPDATE, DELETE, INSERT
            conn.commit()
            return True
    except psycopg2.Error as e:
        error_message = f'{e}'
        logging.error(error_message)
        logit.log_message_to_db(os.environ['SRVC_NAME'], logit.get_rollama_version()['version'], 'ERROR', error_message)
        raise
    finally:
        try:
            cur.close()
        except:
            pass
        try:
            conn.close()
        except:
            pass

def get_select_query_result_dicts(sql_query, params=None):
    """Execute a query, return all rows for the query as list of dictionaries"""

    conn, cur = psql_connection()
    try:
        cur.execute(sql_query, params)
        columns = [desc[0] for desc in cur.description]  # Fetch column names
        result = [dict(zip(columns, row)) for row in cur.fetchall()]
        conn.close()
        return result
    except psycopg2.Error as e:
        error_message = f'{e}'
        logging.error(error_message)
        logit.log_message_to_db(os.environ['SRVC_NAME'], logit.get_rollama_version()['version'], 'ERROR', error_message)
        raise

def get_new_data_ids(table_name, unique_column, reddit_data):
    """Get object ids for new messages on reddit
        query db for existing ids
        query api for all ids
        return the diff from the api
    """

    query = f"SELECT {unique_column} FROM {table_name} GROUP BY {unique_column};"

    data_ids_db = [] # array to hold ids from database table
    data_ids_reddit = [] # arrary to hold ids from reddit api call

    result = get_select_query_results(query)
    for row in result:
        data_ids_db.append(row[0])

    for item in reddit_data:
        data_ids_reddit.append(item.id)

    new_list = set(data_ids_reddit) - set(data_ids_db)
    #TODO new_list_of_lists = list(list_into_chunks(list(newlist), NUM_ELEMENTS_CHUNK))
    return list(new_list)

def db_get_authors():
    """Get list of authors from db table
        return python list
    """

    author_list = []
    query = """SELECT author_name FROM authors GROUP BY author_name;"""
    authors = get_select_query_results(query)
    for row in authors:
        author_list.append(row[0])
    return author_list

def db_get_post_ids():
    """List of post_ids, filtering out pre-analyzed post_ids from this
    """

    post_id_list = []

    sql_query = """
                SELECT post_id
                FROM posts
                WHERE post_body NOT IN ('', '[removed]', '[deleted]')
                AND NOT EXISTS (
                    SELECT 1
                    FROM analysis_documents
                    WHERE analysis_document ->> 'post_id' = posts.post_id
                        AND analysis_document ->> 'post_id' IS NOT NULL
                )
                AND NOT EXISTS (
                    SELECT 1
                    FROM analysis_documents
                    WHERE analysis_document ->> 'reference_id' = posts.post_id
                        AND analysis_document ->> 'reference_id' IS NOT NULL
                );
                """

    post_ids = get_select_query_results(sql_query)
    if not post_ids:
        warn_message = 'db_get_post_ids(): no post_ids found in DB'
        logging.warning(warn_message)
        logit.log_message_to_db(os.environ['SRVC_NAME'], logit.get_rollama_version()['version'], 'WARN', warn_message)
        return False

    for a_post_id in post_ids:
        post_id_list.append(a_post_id[0])

    cached_list = cache.get_set_contents('post_id')
    post_id_list = subtract_lists(post_id_list, cached_list)

    return post_id_list

def db_get_comment_ids():
    """List of comment_ids, filtering out pre-analyzed comment_ids from this
    """

    comment_id_list = []

    sql_query = """
                SELECT comment_id
                FROM comments
                WHERE md5(comment_body) NOT IN (md5(''), md5('[removed]'), md5('[deleted]'))
                AND NOT EXISTS (
                    SELECT 1
                    FROM analysis_documents
                    WHERE (analysis_document ->> 'comment_id' = comments.comment_id
                            OR analysis_document ->> 'reference_id' = comments.comment_id)
                        AND (analysis_document ->> 'comment_id' IS NOT NULL
                            OR analysis_document ->> 'reference_id' IS NOT NULL)
                );
                """

    comment_ids = get_select_query_results(sql_query)
    if not comment_ids:
        warn_message = 'db_get_comment_ids(): no post_ids found in DB'
        logging.warning(warn_message)
        logit.log_message_to_db(os.environ['SRVC_NAME'], logit.get_rollama_version()['version'], 'WARN', warn_message)
        return False

    for a_comment_id in comment_ids:
        comment_id_list.append(a_comment_id[0])

    cached_list = cache.get_set_contents('comment_id')
    comment_id_list = subtract_lists(comment_id_list, cached_list)

    return comment_id_list
