# database.py
# ©2024, Ovais Quraishi
"""DB Utils
"""

import logging
import psycopg2
from config import get_config

def psql_connection():
    """Connect to PostgreSQL server"""
    db_config = get_config()['psqldb']
    try:
        psql_conn = psycopg2.connect(**db_config)
        psql_cur = psql_conn.cursor()
        return psql_conn, psql_cur
    except psycopg2.Error as e:
        logging.error("Error connecting to PostgreSQL: %s", e)
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
        logging.error("%s", e)
        raise

def insert_data_into_table(table_name, data):
    """Insert data into table"""
    conn, cur = psql_connection()
    try:
        placeholders = ', '.join(['%s'] * len(data))
        columns = ', '.join(data.keys())
        # Since the table keys that matter are set to UNIQUE value,
        #   I find the ON CONFLICT DO NOTHING more effecient than
        #   doing a lookup before INSERT. This way original content
        #   is preserved by default. In case of updating existing
        #   data, one can write a method to safely update data
        #   while also preserving original data. For example use
        #   ON CONFLICT DO UPDATE. For now this'd do.
        sql_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) \
                     ON CONFLICT DO NOTHING;"
        cur.execute(sql_query, list(data.values()))
        conn.commit()
    except psycopg2.Error as e:
        logging.error("%s", e)
        raise

def get_select_query_results(sql_query):
    """Execute a query, return all rows for the query
    """

    conn, cur = psql_connection()
    try:
        cur.execute(sql_query)
        result = cur.fetchall()
        conn.close()
        return result
    except psycopg2.Error as e:
        logging.error("%s", e)
        raise

def get_select_query_result_dicts(sql_query):
    """Execute a query, return all rows for the query as list of dictionaries"""

    conn, cur = psql_connection()
    try:
        cur.execute(sql_query)
        columns = [desc[0] for desc in cur.description]  # Fetch column names
        result = [dict(zip(columns, row)) for row in cur.fetchall()]
        conn.close()
        return result
    except psycopg2.Error as e:
        logging.error("%s", e)
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
    sql_query = """SELECT post_id
                   FROM posts
                   WHERE post_body NOT IN ('', '[removed]', '[deleted]')
                   AND post_id NOT IN (SELECT analysis_document ->> 'post_id' AS pid
                                       FROM analysis_documents
                                       WHERE analysis_document ->> 'post_id' IS NOT NULL
                                       GROUP BY pid);"""
    post_ids = get_select_query_results(sql_query)
    if not post_ids:
        logging.warning("db_get_post_ids(): no post_ids found in DB")
        return False

    for a_post_id in post_ids:
        post_id_list.append(a_post_id[0])

    return post_id_list

def db_get_comment_ids():
    """List of post_ids, filtering out pre-analyzed post_ids from this
    """

    comment_id_list = []
    sql_query = """SELECT comment_id
                   FROM comments
                   WHERE comment_body NOT IN ('', '[removed]', '[deleted]')
                   AND comment_id NOT IN (SELECT analysis_document ->> 'comment_id' AS pid
                                          FROM analysis_documents
                                          WHERE analysis_document ->> 'comment_id' is NOT null
                                          GROUP BY pid);"""
    comment_ids = get_select_query_results(sql_query)
    if not comment_ids:
        logging.warning("db_get_comment_ids(): no post_ids found in DB")
        return False

    for a_comment_id in comment_ids:
        comment_id_list.append(a_comment_id[0])

    return comment_id_list
