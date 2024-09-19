#!/usr/bin/env python3

import os
import json
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import psycopg2
from queue import Queue

# Configuration for PostgreSQL connection
DB_HOST = 'host'
DB_NAME = 'database'
DB_USER = 'user'
DB_PASSWORD = 'password'

# Journal service name to monitor
SERVICE_NAME = 'ollama'

# Define the logger to handle journald messages
logger = logging.getLogger('journal_service')
logger.setLevel(logging.INFO)

"""Output logs to a file, rolling over after a certain size and keeping N files.
	Handler is used by the logger to output logs in a human-readable format.

	Parms:
		- filename (str): The path where the log file will be written.
		- maxBytes (int): Maximum bytes that can be written to a single log file.
		- backupCount (int): Number of previous log files to keep before rolling over.
"""

handler = RotatingFileHandler('/var/log/journal_to_postgres.log', maxBytes=1000000, backupCount=10)
handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
logger.addHandler(handler)

# Connect to PostgreSQL and write messages to the servicelogs table
def store_journald_messages_in_postgres():
    """Reads journald messages from the ollama service (assumed in JSON format) and
		inserts them into the servicelogs table.

		Params:
			None

		Returns:
			bool: True if successful, False otherwise.
    """

    try:
        # Establish a connection to the PostgreSQL database
        conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )

        cur = conn.cursor()

        # Read journald messages from the ollama service (assumed in JSON format)
        journal_output = os.popen(f"journalctl -u {SERVICE_NAME} --since=-10m --output=json").read()

        # Process each message individually
        for line in journal_output.strip().split('\n'):
            try:
                json_msg = json.loads(line)

                # Insert the entire journald message into the servicelogs table as a JSONB field
                cur.execute("INSERT INTO servicelogs (host_name, service_name, message) VALUES (%s, %s, %s)",
                            (os.uname()[1], SERVICE_NAME, json.dumps(json_msg)))
                conn.commit()
                logger.info(f'Successfully stored {json.dumps(json_msg)} into PostgreSQL')
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON message: {line}")

        # Close the database connection
        cur.close()
        conn.close()

    except Exception as e:
        logger.error(f'An error occurred while storing journald messages in PostgreSQL: {str(e)}')
        return False

    return True

# Run the service periodically or at startup
def main():
    """Run this function whenever you want to process new messages from journald.

		Params:
			None

		Returns:
			None
    """

    if store_journald_messages_in_postgres():
        logger.info('Journal messages successfully stored in PostgreSQL')

if __name__ == "__main__":
    main()
