from APIServer.commons import constants
from APIServer.commons.api_utils import read_json

import re


PAGE_LIMIT = constants.SLACK_PAGE_LIMIT
MESSAGE_TEMPLATE = 'slack/templates/message.json'
CONFIRM_FORM_LOCATION = 'slack/templates/confirmation.json'


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


def create_msg_from_slack_message(payload, time):
    """
    Create a new raw msg (json) from the new msg form in Slack
    """
    msg_json = {}
    values = payload['view']['state']['values']
    for value in values:
        for key in values[value]:
            if key == 'priority':
                msg_json[key] = \
                    values[value][key]['selected_option']['text']['text']
            else:
                msg_json[key] = values[value][key]['value']
    msg_json['datetime'] = time
    return msg_json


def create_updated_msg_from_slack_message(payload, time, msg_json):
    """
    Create an updated raw msg (json) from an update request in Slack
    """
    values = payload['view']['state']['values']
    for value in values:
        for key in values[value]:
            if key == 'msg_id':
                continue
            if key == 'priority':
                if values[value][key].get('selected_option'):
                    msg_json[key] = \
                        values[value][key]['selected_option']['text']['text']
            if key == 'active':
                if values[value][key].get('selected_option'):
                    msg_json[key] = \
                        values[value][key]['selected_option']['text']['text']
            else:
                if values[value][key].get('value'):
                    msg_json[key] = values[value][key]['value']
    msg_json['datetime'] = time
    return msg_json


def get_id_from_payload(payload):
    """
    Get the msg id from an update request in Slack
    """
    values = payload['view']['state']['values']
    for value in values:
        for key in values[value]:
            if key == 'msg_id':
                msg_id = values[value][key]['value']
                return msg_id


def get_confirmation_form(title, message):
    """
    Create a confirmation message in Slack
    """
    response_json = {}
    form = read_json(CONFIRM_FORM_LOCATION)
    response_json['response_action'] = 'update'
    form['title']['text'] = title
    form['blocks'][0]['text']['text'] = message
    response_json['view'] = form
    return response_json


def get_filter_params_from_slack(payload):
    params = {}
    values = payload['view']['state']['values']
    for value in values:
        for key in values[value]:
            if key == 'since_date':
                if values[value][key].get('selected_date'):
                    params['date'] = values[value][key]['selected_date']
            elif key == 'active':
                if values[value][key].get('selected_option'):
                    params['active'] = \
                        values[value][key]['selected_option']['value']
            else:
                if values[value][key].get('value'):
                    params[key] = values[value][key]['value']
    params['limit'] = PAGE_LIMIT
    return params


def get_msgs_page_form(view_json):
    ret = {}
    ret['response_action'] = 'update'
    ret['view'] = view_json
    return ret


def get_action_value(payload):
    return payload['actions'][0]['value']


def get_page_value(payload):
    text = payload['view']['blocks'][1]['text']['text']
    nums = re.findall(r'\d+', text)
    return int(nums[0])


def get_msgs_count(payload):
    block_count = len(payload['view']['blocks'])
    return (block_count - 3) / 5
