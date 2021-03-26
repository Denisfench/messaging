import unittest

import responses

from APIServer.commons import constants
from APIServer.commons.api_utils import read_json
from APIServer.slack.push import send_slack_log
from APIServer.slack.push import send_json_to_slack_channel
from APIServer.slack.push import open_form
from APIServer.slack.push import update_form
from APIServer.slack.format import get_confirmation_form
from APIServer.slack.format import slack_format_msg
from APIServer.slack.format import create_msg_from_slack_message
from APIServer.slack.format import create_updated_msg_from_slack_message
from APIServer.slack.format import get_id_from_payload
from APIServer.slack.format import get_filter_params_from_slack
from APIServer.slack.format import get_action_value
from APIServer.slack.format import get_page_value
from APIServer.slack.format import get_msgs_count
from APIServer.Heroku.pull import get_heroku_status

SLACK_CONFIG_PATH = \
    'APIServer/test_data/slack/test_slack.json'
SAMPLE_MSG_JSON_PATH = \
    'APIServer/test_data/test_json.json'
POST_MSG_PAYLOAD_PATH = \
    'APIServer/test_data/slack/post_msg_payload.json'
UPDATE_MSG_PAYLOAD_PATH = \
    'APIServer/test_data/slack/update_msg_payload.json'
SAMPLE_MESSAGE_PATH = \
    'APIServer/test_data/slack/formatted_slack_message.json'


HEROKU_CONFIG_PATH = \
    'APIServer/Heroku/heroku_config.json'
TIME = constants.TEST_TIME
slack_config = read_json(SLACK_CONFIG_PATH)
sample_msg_json = read_json(SAMPLE_MSG_JSON_PATH)
post_msg_payload = read_json(POST_MSG_PAYLOAD_PATH)
update_msg_payload = read_json(UPDATE_MSG_PAYLOAD_PATH)
sample_message = read_json(SAMPLE_MESSAGE_PATH)

heroku_config = read_json(HEROKU_CONFIG_PATH)


class TestSlack(unittest.TestCase):

    @responses.activate
    def testLog(self):
        """
        Testing if send_slack_log works
        """
        responses.add(**{
            'method': responses.POST,
            'url': slack_config['Log_URL'],
            'body': 'ok',
            'status': 200,
            'content_type': 'application/json'
        })
        response = send_slack_log('Hello, Socnet')
        self.assertEqual('ok', response[200])

    @responses.activate
    def testPush(self):
        """
        Testing if send_json_to_slack_channel works
        """
        responses.add(**{
            'method': responses.POST,
            'url': slack_config['Post_Chat_URL'],
            'body': 'ok',
            'status': 200,
            'content_type': 'application/json'
        })
        response = send_json_to_slack_channel({'text': 'Hello, Socnet'},
                                              'my_channel')
        self.assertEqual('ok', response[200])

    @responses.activate
    def testOpenForm(self):
        """
        Testing if open_form works
        """
        responses.add(**{
            'method': responses.POST,
            'url': slack_config['Views_Open_URL'],
            'body': 'ok',
            'status': 200,
            'content_type': 'application/json'
        })
        response = open_form('my_channel',
                             'my_tigger_id',
                             'test_data/slack/post_msg_form.json')
        self.assertEqual('ok', response[200])

    @responses.activate
    def testUpdateForm(self):
        """
        Testing if update_form works
        """
        responses.add(**{
            'method': responses.POST,
            'url': slack_config['Log_URL'],
            'body': 'ok',
            'status': 200,
            'content_type': 'application/json'
        })
        responses.add(**{
            'method': responses.POST,
            'url': slack_config['Views_Update_URL'],
            'body': 'ok',
            'status': 200,
            'content_type': 'application/json'
        })
        response = update_form('my_view_id',
                               'my_hash',
                               {})
        self.assertEqual('ok', response[200])

    def testCreateMsgFromSlack(self):
        """
        Testing if create_msg_from_slack_message works
        """
        msg_json = create_msg_from_slack_message(post_msg_payload, TIME)
        self.assertEqual(sample_msg_json, msg_json)

    def testFormatMsg(self):
        """
        Testing if slack_format_msg works
        """
        ret = slack_format_msg([])
        self.assertEqual({'text':
                         'This msg does not exist or has been deleted.'},
                         ret)
        ret = slack_format_msg([(1,
                                 '2020-03-04 17:54:20',
                                 '10001',
                                 'New York City',
                                 'New York',
                                 'USA',
                                 'Fire',
                                 'Fire in the building',
                                 'High',
                                 'Socnet Tester',
                                 'Active')])
        self.assertEqual(sample_message, ret)

    def testUpdateMsg(self):
        """
        Testing if create_updated_msg_from_slack_message works
        """
        msg_json = create_updated_msg_from_slack_message(
            update_msg_payload,
            TIME,
            sample_msg_json)
        # update sample msg json
        self.assertEqual(msg_json['zipcode'], '10003')
        self.assertEqual(msg_json['sender'], 'Slack')
        self.assertEqual(msg_json['active'], 'Not Active')

    def testGetMsgId(self):
        """
        Testing if get_id_from_payload works
        """
        payload = read_json('test_data/slack/update_msg_payload.json')
        msg_id = get_id_from_payload(payload)
        self.assertEqual('1', msg_id)

    def testConfirmation(self):
        """
        Testing if get_confirmation_form works
        """
        sample_message = read_json('test_data/slack/confirmation_message.json')
        response = get_confirmation_form('My Title', 'my message')
        self.assertEqual(sample_message, response)

    def testGetFilterParams(self):
        """
        Testing if get_filter_params_from_slack works
        """
        payload = read_json('test_data/slack/filter_msgs_payload.json')
        response = get_filter_params_from_slack(payload)
        sample_response = {}
        sample_response['country'] = 'USA'
        sample_response['state'] = 'New York'
        sample_response['type'] = 'Fire'
        sample_response['priority'] = 'Low'
        sample_response['date'] = '2019-01-01'
        sample_response['limit'] = 5
        sample_response['active'] = 'y'
        self.assertEqual(sample_response, response)

    def testGetActionPageAndCount(self):
        """
        Testing if get_action_value, get_page_value, get_msgs_count works
        """
        payload = read_json('test_data/slack/next_page_payload.json')
        action = get_action_value(payload)
        page = get_page_value(payload)
        msgs_count = get_msgs_count(payload)
        self.assertEqual('next_page', action)
        self.assertEqual(1, page)
        self.assertEqual(10, msgs_count)

    @responses.activate
    def testHeroku(self):
        """
        Testing if get_heroku_status works
        """
        responses.add(**{
            'method': responses.GET,
            'url': heroku_config['Heroku_Status'],
            'body': 'ok',
            'status': 200,
            'content_type': 'application/json'
        })
        response = get_heroku_status('Hello, Socnet')
        self.assertEqual('ok', response[200])
