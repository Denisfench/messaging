
"""
This module sends some text to a Mattermost server.
"""
import os
import requests

# we don't know what this URL is: perhaps it was a test server at AWS?
AWS_MATTERMOST_URL = "http://18.235.204.147:8065"
MATTERMOST_URL = os.getenv("MATTERMOST_URL", AWS_MATTERMOST_URL)


def push_to_mattermost(text, channel=None):
    jsonToSend = {'text': str(text)}
    if channel is not None:
        jsonToSend['channel'] = channel
    URL = f'{MATTERMOST_URL}/hooks/dse96wr583gwjesxbx48ykuy6r'
    response = requests.post(URL, json=jsonToSend)
    return {response.status_code: response.text}
