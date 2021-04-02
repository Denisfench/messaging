import requests

from APIServer.commons.api_utils import read_json

# from APIServer.Heroku.operations import write_status

HEROKU_CONFIG_PATH = 'Heroku/heroku_config.json'
heroku_config = read_json(HEROKU_CONFIG_PATH)
SLACK_CONFIG_PATH = 'slack/slack_config.json'
slack_config = read_json(SLACK_CONFIG_PATH)


def get_heroku_status(text):
    """
    Fetch app info from Heroku API
    """
    URL = "https://api.heroku.com/apps"
    headers = {"Accept": "application/vnd.heroku+json; version=3",
               "Authorization": heroku_config['Heroku_Token']}
    response = requests.get(url=URL, headers=headers)
    # write_status(response.text)
    return {response.status_code: response.text}


def send_text_to_slack_channel(textToSend, channel):
    URL = 'https://slack.com/api/chat.postMessage'
    textToSend['channel'] = channel
    textToSend['channel'] = {'text': str(channel)}
    headers = {"Authorization": slack_config['Bot_Access_Token'],
               "Content-Type": "application/json; charset=utf-8"}
    response = requests.post(URL, json=textToSend, headers=headers)
    return {response.status_code: response.text}
