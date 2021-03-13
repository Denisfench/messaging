import datetime

from APIServer.slack.format import slack_format_msg
from APIServer.slack.format import create_msg_from_slack_message
from APIServer.slack.format import create_updated_msg_from_slack_message
from APIServer.slack.format import get_confirmation_form
from APIServer.slack.format import get_msgs_page_form
from APIServer.slack.format import get_id_from_payload
from APIServer.slack.format import get_filter_params_from_slack
from APIServer.slack.format import get_action_value
from APIServer.slack.format import get_page_value
from APIServer.slack.format import get_msgs_count
from APIServer.slack.push import send_slack_log
from APIServer.slack.push import update_form
from APIServer.msgs.operations import write_msg
from APIServer.msgs.operations import read_msg
from APIServer.msgs.operations import update_msg
from APIServer.msgs.operations import read_filtered_msgs
from APIServer.commons.api_utils import read_json
from APIServer.commons.form_api import create_msg_json
from APIServer.commons import constants


PAGE_LIMIT = constants.SLACK_PAGE_LIMIT
MSG_LIST_TEMPLATE = 'slack/templates/msg_lists.json'


def create_msgs_page_view(params):
    msg_list = read_filtered_msgs(params)
    view = read_json(MSG_LIST_TEMPLATE)
    for msg_json in msg_list:
        formated_msg = slack_format_msg([msg_json])
        for section in formated_msg['blocks']:
            view['blocks'].append(section)
    return view


def handle_interaction(payload_json):
    if payload_json['type'] == 'view_submission':
        send_slack_log('Payload type: view_submission')
        time = datetime.datetime.now() \
                       .strftime('%Y-%m-%d %H:%M:%S')
        if payload_json['view']['callback_id'] == 'post_msg':
            send_slack_log('callback_id: ' + 'post_msg')
            msg_json = create_msg_from_slack_message(payload_json,
                                                     time)
            send_slack_log('New message json: ' + str(msg_json))
            response = write_msg(msg_json)
            send_slack_log('Response info: ')
            send_slack_log(response)
            return get_confirmation_form('Success', response)
        elif payload_json['view']['callback_id'] == 'update_msg':
            send_slack_log('callback_id: ' + 'update_msg')
            msg_id = get_id_from_payload(payload_json)
            send_slack_log('Message id: ' + str(msg_id))
            ret = read_msg(msg_id)
            if len(ret) == 0:
                send_slack_log('Invalid Message ID')
                return {'response_action': 'clear'}
            msg_json = create_msg_json(ret[0])
            send_slack_log('Old message json: ' + str(msg_json))
            msg_json = create_updated_msg_from_slack_message(
                payload_json,
                time,
                msg_json)
            send_slack_log('New message json: ' + str(msg_json))
            response = update_msg(msg_json, msg_id)
            send_slack_log('Response info: ')
            send_slack_log(response)
            return get_confirmation_form('Success', response)
        elif payload_json['view']['callback_id'] == 'filter_msgs':
            send_slack_log('callback_id: ' + 'filter_msgs')
            params = get_filter_params_from_slack(payload_json)
            view = create_msgs_page_view(params)
            return get_msgs_page_form(view)
        else:
            send_slack_log('Unknown callback_id in view_submission')
            return
    elif payload_json['type'] == 'block_actions':
        send_slack_log('Payload type: block_actions')
        action = get_action_value(payload_json)
        params = get_filter_params_from_slack(payload_json)
        page = get_page_value(payload_json)
        msgs_count = get_msgs_count(payload_json)
        if action == 'next_page':
            if msgs_count == PAGE_LIMIT:
                page = page + 1
        elif action == 'prev_page':
            if page > 1:
                page = page - 1
        else:
            send_slack_log('Invalid action')
            return
        params['offset'] = PAGE_LIMIT * (page - 1)
        send_slack_log('Parameters: ' + str(params))
        view = create_msgs_page_view(params)
        view['blocks'][1]['text']['text'] = \
            "*Showing page " + str(page) + " (max " + \
            str(PAGE_LIMIT) + " messages per page)*"
        view_id = payload_json['view']['id']
        hash_value = payload_json['view']['hash']
        return update_form(view_id, hash_value, view)
    else:
        send_slack_log('No action needed for this interaction')
        return
