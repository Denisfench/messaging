from APIServer.commons import constants
from APIServer.commons.api_utils import read_json

PAGE_LIMIT = constants.HEROKU_PAGE_LIMIT
MESSAGE_TEMPLATE = 'Heroku/templates/message.json'


def slack_format_msg(msg_json):
    """
    Convert a raw msg (json) to a formatted message in Slack
    """
    if msg_json == []:
        return {'text': 'This msg does not exist or has been deleted.'}

    message = read_json(MESSAGE_TEMPLATE)

    msg_id = msg_json[0][0]
    datetime = msg_json[0][1]
    location = msg_json[0][3] + ', ' \
        + msg_json[0][4] + ', ' \
        + msg_json[0][2] + ', ' \
        + msg_json[0][5]
    event = msg_json[0][6]
    description = msg_json[0][7]
    priority = msg_json[0][8]
    sender = msg_json[0][9]
    active_status = msg_json[0][10]
    THREAD_URL = 'https://gcallah.github.io/socnet/webapp.html#/thread/'
    url = THREAD_URL + str(msg_id)

    message['blocks'][1]['text']['text'] = '*' + event \
        + '* (_' + active_status + '_)\n' + description
    message['blocks'][2]['elements'][0]['text'] = location + '\n' \
        + datetime + '\n' \
        + priority + '\nby *' \
        + sender + '*'
    message['blocks'][3]['accessory']['url'] = url
    return message
