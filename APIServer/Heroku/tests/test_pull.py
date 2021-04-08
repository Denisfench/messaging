from unittest import TestCase

import responses

from APIServer.commons.api_utils import read_json
from APIServer.Heroku.pull import get_heroku_deployments
from APIServer.Heroku.pull import send_text_to_slack_channel

HEROKU_CONFIG_PATH = 'APIServer/Heroku/heroku_config.json'
heroku_config = read_json(HEROKU_CONFIG_PATH)
SLACK_CONFIG_PATH = 'slack/slack_config.json'
slack_config = read_json(SLACK_CONFIG_PATH)


class HerokuTests(TestCase):
    """
    Tests for all Heroku interaction code.
    """

    @responses.activate
    def testHerokuPull(self):
        """
        Testing if get_heroku_deployments works
        """
        responses.add(**{
            'method': responses.GET,
            'url': heroku_config['Heroku_Status'],
            'body': 'ok',
            'status': 200,
            'content_type': 'application/json'
        })
        responses.add(**{
            'method': responses.GET,
            'url': heroku_config['Heroku_Status'],
            'body': 'not found',
            'status': 404,
            'content_type': 'application/json'
        })
        responses.add(**{
            'method': responses.GET,
            'url': heroku_config['Heroku_Status'],
            'body': 'service unavailable',
            'status': 503,
            'content_type': 'application/json'
        })
        response = get_heroku_deployments({'text': 'Hello, Messaging'})
        if (self.assertEqual('ok', response[200]) is False):
            if (self.assertEqual('not found', response[404]) is False):
                self.assertEqual('service unavailable', response[503])

    @responses.activate
    def testHerokuPush(self):
        """
        Testing if send_text_to_slack_channel works
        """
        responses.add(**{
            'method': responses.POST,
            'url': slack_config['Post_Chat_URL'],
            'body': 'ok',
            'status': 200,
            'content_type': 'application/json'
        })
        responses.add(**{
            'method': responses.POST,
            'url': slack_config['Post_Chat_URL'],
            'body': 'not found',
            'status': 404,
            'content_type': 'application/json'
        })
        responses.add(**{
            'method': responses.POST,
            'url': slack_config['Post_Chat_URL'],
            'body': 'service unavailable',
            'status': 503,
            'content_type': 'application/json'
        })
        response = send_text_to_slack_channel({'text': 'Hello, Messaging'},
                                              'my_channel')
        if (self.assertEqual('ok', response[200]) is False):
            if (self.assertEqual('not found', response[404]) is False):
                self.assertEqual('service unavailable', response[503])
