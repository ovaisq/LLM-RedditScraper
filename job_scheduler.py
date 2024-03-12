#!/usr/bin/env python3
"""Schedule API polling from Reddit

    LICENSE: The 3-Clause BSD License - license.txt
    
    ©2024, Ovais Quraishi
"""

import daemon
import requests
import schedule
import time
import urllib3
# disable warning for self-signed SSL cert
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Constants
CONFIG_FILE = 'setup.config'
CONFIG = configparser.RawConfigParser()
CONFIG.read(CONFIG_FILE)

LOGIN_HEADERS = {
                 'Content-Type' : 'application/json'
                }

def get_auth_token():

    end_point = 'login'
    url = CONFIG.get('service','ENDPOINT_URL') + end_point
    svc_shared_secret = CONFIG.get('service','SRVC_SHARED_SECRET')
    auth_data = {
                  'api_key' : svc_shared_secret
                 }
    response = requests.post(url,
                             headers=LOGIN_HEADERS,
                             data=json.dumps(auth_data),
                             verify=True)
    response_json = response.json()['access_token']
    return response_json

def do_get(end_point):
    url = CONFIG.get('service','ENDPOINT_URL') + end_point
    auth_token = get_auth_token()
    headers = {
               'Authorization' : f'Bearer {auth_token}'
              }
    response = requests.get(url, headers=headers, verify=True)
    response_json = response.json()['access_token']
    return response_json

# Tasks setup
def get_authors_comments():
    print("Get all comments of all authors listed in the author table")
    do_get('get_authors_comments')

def join_new_subs():
    print("Join new subreddits listed in the subscription table")

def get_sub_posts():
    print("Get all submissions from a subreddit")

# Task scheduling
# After every 5 to 10mins in between run get_sub_posts()
schedule.every(5).to(10).minutes.do(get_sub_posts)

# Every monday join_new_subs() is called
schedule.every().monday.do(join_new_subs)

# Every tuesday at 18:00 get_authors_comments() is called
schedule.every().tuesday.at("18:00").do(get_authors_comments)

def main():
    # Loop so that the scheduling task
    #  keeps on running 
    while True:
        # Checks whether a scheduled task
        #  is pending to run or not
        schedule.run_pending()
        time.sleep(2)

if __name__ == '__main__':
    with daemon.DaemonContext():
        main()
