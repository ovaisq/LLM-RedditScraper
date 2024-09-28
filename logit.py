# logit.py
# ©2024, Ovais Quraishi

import datetime
import os
import json
import logging
import re
from pathlib import Path

from database import insert_data_into_table

def log_message_to_db(program_name, host_name, severity, log_message):
    """Log a message to the database.

        Args:
            host_name (str): The name of the host where the program is running.
            program_name (str): The name of the program that generated the log.
            severity (str): The severity level of the log.
            log_message (str): The actual content of the log.

        Returns:
            None

        Notes:
            This function assumes that 'rollamalogs' table exists in the database with required columns.
    """
    
    ts_now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat(timespec='seconds', sep=' ')
    
    if not host_name:
        host_name = 'NO_HOSTNAME_AVAILABLE'
    try:
        # Define a dictionary with placeholder values
        log_data = {
                    'timestamp': ts_now,
                    'host': host_name,
                    'program_name': program_name,
                    'program_version' : get_rollama_version(),
                    'severity': severity,
                    'message': log_message
                   }

        # payload for database
        data = {
                'timestamp' : ts_now,
                'log_json' : json.dumps(log_data)
               }
    
        # insert data into table
        insert_data_into_table('rollamalogs', data)
    except KeyError as e:
        log_message = f"{e}"
        logging.error(log_message)

def get_rollama_version():
    """Reads the first line from /usr/local/rollama/ver.txt,
        checks if it matches semver (0.1.2) format and returns it.

        Returns:
            str: The version string if valid, otherwise False.
    """

    ver_file_path = '/usr/local/rollama/ver.txt'

    try:
        host_name = os.environ['HOSTNAME']
        with open(str(Path(ver_file_path).resolve()), 'r') as f:
            first_line = f.readline().strip()
    except FileNotFoundError:
        log_message = f"File {ver_file_path} not found."
        logging.error(log_message)
        return False
    except KeyError:
        host_name = 'NOT_AVAILABLE'
        log_message = 'Host name not available'
        logging.error(log_message)
        return False

    semver_pattern = r'^\d+\.\d+\.\d+$'

    if re.match(semver_pattern, first_line):
        return {"version":first_line}
    else:
        log_message = "Invalid version format. Expected semver (0.1.2)."
        logging.error(log_message)
        return False
