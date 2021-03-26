import requests

from APIServer.commons.api_utils import read_json

HEROKU_CONFIG_PATH = 'Heroku/heroku_config.json'
heroku_config = read_json(HEROKU_CONFIG_PATH)


def get_heroku_status(text):
    URL = "https://status.heroku.com/api/v4/current-status"
    response = requests.get(url=URL)
    # data = response.json()
    data = response
    print(response.status_code)
    print(data.text)
    return {response.status_code: data.text}
