import requests
from APIServer.commons.api_utils import read_json
# from APIServer.Heroku.operations import latest_deployment
import smtplib
# for dealing with attachement MIME types
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SCOPES = ['https://mail.google.com/']

HEROKU_CONFIG_PATH = \
    'APIServer/Heroku/heroku_config.json'
SLACK_CONFIG_PATH = \
    'APIServer/slack/slack_config.json'
EMAIL_CONFIG_PATH = \
    'APIServer/Heroku/email_config.json'

heroku_config = read_json(HEROKU_CONFIG_PATH)
slack_config = read_json(SLACK_CONFIG_PATH)
email_config = read_json(EMAIL_CONFIG_PATH)


def get_heroku_deployments(server):
    """
    We will return (all?) Heroku deployments for the app of interest.
    """
    URL = heroku_config['Heroku_Status']
    headers = {"Accept": "application/vnd.heroku+json; version=3",
               "Authorization": heroku_config['Heroku_Token']}
    response = requests.get(url=URL, headers=headers)
    return {response.status_code: response.text}


def send_text_to_slack_channel(textToSend, channel):
    URL = slack_config['Slack_Message_Post']
    textToSend['channel'] = channel
    headers = {"Authorization": slack_config['Bot_Access_Token'],
               "Content-Type": "application/json; charset=utf-8"}
    response = requests.post(URL, json=textToSend, headers=headers)
    return {response.status_code: response.text}


def create_email(sender, to):
    """Create a message for an email.

    Returns:
    An object containing a base64url encoded email object.
    """
    message = MIMEMultipart()  # creates message
    message['To'] = to
    message['From'] = sender
    message['Subject'] = " Heroku Deployments Status"
    body = "latest_deployment()"
    body = MIMEText(body, 'plain')
    message.attach(body)

    return message.as_string()  # need to encode


def send_email(to):
    to = to
    sender = "default@gmail.com"

    username = email_config["USER_EMAIL"]
    password = email_config["USER_PASSWORD"]

    server = smtplib.SMTP("smtp.gmail.com", port=587)
    server.starttls()
    server.login(username, password)
    msg = create_email(sender, to)
    server.sendmail(sender, to, msg)
    server.quit()
