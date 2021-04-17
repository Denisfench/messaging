import requests
from APIServer.commons.api_utils import read_json

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

import datetime
from datetime import date

HEROKU_CONFIG_PATH = 'Heroku/heroku_config.json'
heroku_config = read_json(HEROKU_CONFIG_PATH)
SLACK_CONFIG_PATH = 'slack/slack_config.json'
slack_config = read_json(SLACK_CONFIG_PATH)
EMAIL_CONFIG_PATH = 'Heroku/email_config.json'
email_config = read_json(EMAIL_CONFIG_PATH)
#SENDGRID_API_KEY = <need to make>


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


def send_email(textToSend, email):
    URL = email_config["URL"]
    headers = {"Authorization": email_config['Email_Token'],
               "Content-Type": "application/json"}
    response = requests.post(URL, json=textToSend, headers=headers)
    today = date.today()
    message = Mail(
        #need to find from_email
        from_email='from_email@example.com',
        to_emails='ejc369@nyu.edu',
        subject='DevOps: Messaging Deployments - '+today,
        html_content='<strong>response</strong>')
    try:
        #need to make new constant SENDGRID_API_KEY
        #https://sendgrid.com/docs/ui/account-and-settings/api-keys/
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
    except Exception as e:
        print(e.message)
    # need to complete
    # using SENDGRID API https://sendgrid.com/solutions/email-api/
    return response
