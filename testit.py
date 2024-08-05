#!/usr/bin/env python3
# ©2024, Ovais Quraishi

import unittest
import json
from unittest.mock import patch, MagicMock

from config import get_config
get_config()
SRVC_SHARED_SECRET=os.environ['SRVC_SHARED_SECRET']

# Import the Flask app
from zollama import app

class TestFlaskApp(unittest.TestCase):

    def setUp(self):
        """Set up Flask app for testing."""
        app.config['TESTING'] = True
        self.app = app.test_client()

        # Perform login to obtain JWT token
        self.jwt_token = self.perform_login()

    def tearDown(self):
        """Tear down Flask app after testing."""
        pass

    def perform_login(self):
        """Perform login to obtain JWT token."""

        # Define login data
        login_data = {
            'api_key': SRVC_SHARED_SECRET
        }
        headers = {
            'Content-Type' : 'application/json'
            }

        # Send POST request to /login endpoint
        response = self.app.post('/login', json=login_data, headers=headers)

        # Extract JWT token from response
        data = json.loads(response.data)
        jwt_token = data.get('access_token')

        return jwt_token


    # Add more test cases for other endpoints...

if __name__ == '__main__':
    unittest.main()
