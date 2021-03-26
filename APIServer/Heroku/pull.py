import requests

from APIServer.commons.api_utils import read_json

HEROKU_CONFIG_PATH = 'Heroku/heroku_config.json'
heroku_config = read_json(HEROKU_CONFIG_PATH)

def get_heroku_status(text):
    #jsonToSend = {'text': str(text)}
    URL = "https://status.heroku.com/api/v4/current-status"
    response = requests.get(url = URL)
    data =response.json()
    #response = requests.post(URL, json=jsonToSend)
    print(response.status_code)
    print(data)
    return {response.status_code: data}



# def send_json_to_slack_channel(jsonToSend, channel):
#     URL = 'https://slack.com/api/chat.postMessage'
#     jsonToSend['channel'] = channel
#     headers = {"Authorization": slack_config['Bot_Access_Token'],
#                "Content-Type": "application/json; charset=utf-8"}
#     response = requests.post(URL, json=jsonToSend, headers=headers)
#     return {response.status_code: response.text}


# def open_form(channel, trigger_id, form_location):
#     URL = 'https://slack.com/api/views.open'
#     form = read_json(form_location)
#     textToSend = {'channel': channel, 'trigger_id': trigger_id, 'view': form}
#     headers = {"Authorization": slack_config['Bot_Access_Token'],
#                "Content-Type": "application/json; charset=utf-8"}
#     response = requests.post(URL, json=textToSend, headers=headers)
#     return {response.status_code: response.text}


# def update_form(view_id, hash_value, view):
#     URL = 'https://slack.com/api/views.update'
#     textToSend = {'view_id': view_id, 'hash': hash_value, 'view': view}
#     headers = {"Authorization": slack_config['Bot_Access_Token'],
#                "Content-Type": "application/json; charset=utf-8"}
#     response = requests.post(URL, json=textToSend, headers=headers)
#     return {response.status_code: response.text}
