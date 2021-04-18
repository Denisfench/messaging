import requests
from APIServer.commons.api_utils import read_json


# for dealing with attachement MIME types
from email.mime.text import MIMEText

SCOPES = ['https://mail.google.com/']
our_email = 'rabiya.sharieff@gmail.com'  # for testing

HEROKU_CONFIG_PATH = 'Heroku/heroku_config.json'
heroku_config = read_json(HEROKU_CONFIG_PATH)
SLACK_CONFIG_PATH = 'slack/slack_config.json'
slack_config = read_json(SLACK_CONFIG_PATH)
EMAIL_CONFIG_PATH = 'Heroku/email_config.json'
email_config = read_json(EMAIL_CONFIG_PATH)


def get_heroku_deployments(server):
    """
    We will return (all?) Heroku deployments for the app of interest.
    """
    URL = "https://api.heroku.com/apps"
    headers = {"Accept": "application/vnd.heroku+json; version=3",
               "Authorization": heroku_config['Heroku_Token']}
    response = requests.get(url=URL, headers=headers)
    return {response.status_code: response.text}


def send_text_to_slack_channel(textToSend, channel):
    URL = 'https://slack.com/api/chat.postMessage'
    textToSend['channel'] = channel
    headers = {"Authorization": slack_config['Bot_Access_Token'],
               "Content-Type": "application/json; charset=utf-8"}
    response = requests.post(URL, json=textToSend, headers=headers)
    return {response.status_code: response.text}


def create_email(sender, to, subject, message_text):
    """Create a message for an email.

    Returns:
    An object containing a base64url encoded email object.
    """
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': (message.as_string())}


def send_email(textToSend, email):
    URL = email_config["URL"]
    headers = {"Authorization": email_config['Email_Token'],
               "Content-Type": "application/json"}
    response = requests.post(URL, json=textToSend, headers=headers)
    # need to complete
    return response
