#!/usr/bin/env python3
"""External Service connectivity function live here"""

import jwt
import os
import time
import requests


def cache_api(endpoint_url, payload=None):
    """Call a protected endpoint with a JSON payload."""

    caching_srvc_login_url = os.environ["caching_srvc_login_url"]
    caching_srvc_secret = os.environ["caching_srvc_secret"]
    caching_srvc_headers = {"Content-Type": "application/json"}
    caching_srvc_payload = {
        "client_id": "rollama",
        "api_key": caching_srvc_secret,
        "grant_type": "client_credentials",
    }
    curr_token = get_jwt_token(
        caching_srvc_login_url, caching_srvc_payload, caching_srvc_headers
    )

    url = f"{endpoint_url}"
    headers = {
        "Authorization": f"Bearer {curr_token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        response_json = response.json()
        return response_json  # Return the JSON response
    except requests.exceptions.RequestException as e:
        print(f"Error calling protected API: {e}")
        raise


def get_jwt_token(srvc_url, srvc_payload, headers):
    """Fetch JWT token using the provided authentication payload.
    """

    response = requests.post(srvc_url, json=srvc_payload, headers=headers)
    response.raise_for_status()  # Raise error for bad HTTP response
    token_data = response.json()

    return token_data["access_token"]


def check_and_refresh_token(jwt_token):
    """Check if a JWT token has expired and refresh it using get_jwt_token if necessary."""

    try:
        # Decode the token without verifying the signature
        decoded_token = jwt.decode(jwt_token, options={"verify_signature": False})

        # Extract expiration time (exp claim)
        expiration_time = decoded_token.get("exp")

        if not expiration_time:
            raise ValueError("Expiration time ('exp') claim not found in the token.")

        # Compare the current time with the expiration time
        current_time = time.time()

        if current_time > expiration_time:
            # Token is expired; fetch a new one using the get_jwt_token function
            print("Token has expired. Fetching a new token...")
            return get_jwt_token()

        # Token is still valid
        return jwt_token

    except jwt.InvalidTokenError:
        raise ValueError("Invalid JWT token.")  # Raise an exception for invalid tokens
