# SOCNET API server
from flask import request
from APIServer import create_app
from flask_restplus import Resource, Api, fields
from APIServer.commons.form_api import get_msg_form
from APIServer.commons.api_utils import read_json
from APIServer.commons.endpoint_api import get_endpoints

from APIServer.msgs.operations import read_filtered_msgs
from APIServer.msgs.operations import write_msg
from APIServer.msgs.operations import read_msg
from APIServer.msgs.operations import update_msg
from APIServer.msgs.operations import delete_msg
from APIServer.msgs.operations import number_of_msgs
from APIServer.msgs.operations import newest_msg
from APIServer.msgs.operations import oldest_msg

from APIServer.threads.operations import get_comments
from APIServer.threads.operations import add_comment

from APIServer.slack.push import send_slack_log
from APIServer.slack.push import send_json_to_slack_channel
from APIServer.slack.push import open_form
from APIServer.slack.format import slack_format_msg
from APIServer.slack.operations import handle_interaction

from APIServer.mattermost.push import push_to_mattermost

from werkzeug.middleware.proxy_fix import ProxyFix

import os
import json

CONFIG_PATH = 'api_config.json'
# config is a dictionary of configuration params:
config = read_json(CONFIG_PATH)

port = int(os.environ.get("PORT", config['port']))

app = create_app(config)

# fix the bug that 'no api definition provided'
# when deployed to Heroku
app.wsgi_app = ProxyFix(app.wsgi_app)

api = Api(app, title='MESSAGING SYSTEM API')

app.config.SWAGGER_UI_DOC_EXPANSION = 'list'


@api.route('/hello')
class HelloWorld(Resource):
    def get(self):
        """
        A Hello World API for testing
        """
        return {'hello': 'socnet'}


@api.route('/endpoints')
class Endpoints(Resource):
    def get(self):
        """
        List our endpoints.
        """
        return get_endpoints(api, app)


@api.route('/msg_format')
class MsgFormat(Resource):
    def get(self):
        """
        Get the format of a message
        """
        return get_msg_form(config['msg_format_path'])


@api.route('/filters')
class FilterValues(Resource):
    def get(self):
        """
        Get the values to populate the filter form
        """
        return get_msg_form(config['filter_form_values_path'])


@api.route('/form')
class MessageFormat(Resource):
    def get(self):
        """
        Get the format of a message
        """
        return get_msg_form(config['format_path'])


msg = api.schema_model('Msg',
                       get_msg_form(config['format_path']))


@api.route('/number_of_msgs')
class TotalMsgs(Resource):
    def get(self):
        """
        Get the total number of messages
        """
        return {'number_of_msgs': number_of_msgs()}


@api.route('/newest_msg')
class NewestMsg(Resource):
    def get(self):
        """
        Return the date and time for the latest message
        """
        return {"newest_msg": newest_msg()}


@api.route('/oldest_msg')
class OldestMsg(Resource):
    def get(self):
        """
        Return the date and time for the oldest message
        """
        return {"oldest_msg": oldest_msg()}


@api.route('/msgs')
class MsgsLists(Resource):
    @api.doc(params={'priority': 'Filter messages by priority'})
    @api.doc(params={'date': 'Filter messages by date'})
    @api.doc(params={'type': 'Filter messages by type'})
    @api.doc(params={'region': 'Filter messages by region'})
    @api.doc(params={'country': 'Filter messages by country'})
    @api.doc(params={'active': 'Filter messages by active status. \
        Enter y or n'})
    @api.doc(params={'limit': 'Pagination parameter. \
        Indicate the max number of results returned. \
        If not provided, the default value will be set to 100.'})
    @api.doc(params={'offset': 'Pagination parameter. \
        Indicate the offset of the first result. \
        If not provided, the default value will be set to 0.'})
    def get(self):
        """
        Get multiple (filtered) messages based on the query parameters
        """
        return read_filtered_msgs(request.args)

    @api.expect(msg)
    def post(self):
        """
        Put a new message into the system
        """
        return write_msg(request.json)


@api.route('/msgs/<int:id>')
@api.doc(params={'id': 'An Msg id number'})
class Msgs(Resource):
    def get(self, id):
        """
        Get a specific messages with the given message id
        """
        return read_msg(id)

    @api.expect(msg)
    def put(self, id):
        """
        Update a message in the system with the given message id
        """
        return update_msg(request.json, id)

    def delete(self, id):
        """
        Delete a message in the system with the given message id
        """
        return delete_msg(id)


comment = api.model('Comment', {'text': fields.String})


@api.route('/threads/<int:id>')
@api.doc(params={'id': 'An Msg id number'})
class Threads(Resource):
    def get(self, id):
        """
        List all comments under a thread (thread id is given)
        """
        return get_comments(id)

    @api.expect(comment)
    def put(self, id):
        """
        Post a new comment under a thread (thread id is given)
        """
        return add_comment(request.json, id)


@api.route('/slack/post_msg')
class SlackPostMsg(Resource):
    def post(self):
        """
        Post a new message into the system through a Slack message
        """
        send_slack_log('Entered /slack/post_msg')
        send_slack_log('Request info:')
        send_slack_log(str(request.form))
        trigger_id = request.form['trigger_id']
        channel_id = request.form['channel_id']
        response = open_form(channel_id,
                             trigger_id,
                             config['slack_post_form_path'])
        send_slack_log('Response info:')
        send_slack_log(str(response))
        return 'Please enter the new msg information in the form'


@api.route('/slack/get_msg')
class SlackGetMsg(Resource):
    def post(self):
        """
        Get a specific message with the given message id and send it to Slack
        """
        send_slack_log('Entered /slack/get_msg')
        send_slack_log('Request info:')
        send_slack_log(str(request.form))
        msg_id = request.form['text']
        channel_id = request.form['channel_id']
        try:
            id = int(msg_id)
        except ValueError:
            return "Invalid Msg ID: " + str(msg_id)
        text = read_msg(id)
        formated_msg = slack_format_msg(text)
        response = send_json_to_slack_channel(formated_msg, channel_id)
        send_slack_log('Response info:')
        send_slack_log(response)
        return "Msg " + str(id) + " fetched"


@api.route('/slack/update_msg')
class SlackUpdateMsg(Resource):
    def post(self):
        """
        Update a message in the system through a Slack message
        """
        send_slack_log('Entered /slack/update_msg')
        send_slack_log('Request info:')
        send_slack_log(str(request.form))
        trigger_id = request.form['trigger_id']
        channel_id = request.form['channel_id']
        response = open_form(channel_id,
                             trigger_id,
                             config['slack_update_form_path'])
        send_slack_log('Response info:')
        send_slack_log(str(response))
        return 'Please enter the updated msg information in the form'


@api.route('/slack/delete_msg')
class SlackDeleteMsg(Resource):
    def post(self):
        """
        Delete a message in the system through a Slack message
        """
        send_slack_log('Entered /slack/delete_msg')
        send_slack_log('Request info:')
        send_slack_log(str(request.form))
        msg_id = json.loads(request.form['text'])
        return delete_msg(int(msg_id))


@api.route('/slack/filter_msgs')
class SlacFilterMsgs(Resource):
    def post(self):
        """
        Filter messages in the system through a Slack message
        """
        send_slack_log('Entered /slack/filter_msgs')
        send_slack_log('Request info:')
        send_slack_log(str(request.form))
        trigger_id = request.form['trigger_id']
        channel_id = request.form['channel_id']
        response = open_form(channel_id,
                             trigger_id,
                             config['slack_filter_form_path'])
        send_slack_log('Response info:')
        send_slack_log(str(response))
        return 'Please enter msgs filtering information in the form'


@api.route('/slack/submit')
class SlackSubmit(Resource):
    @api.doc(responses={200: 'OK'})
    def post(self):
        """
        An API that handles all Slack submit events (interactions)
        """
        send_slack_log('Entered /slack/submit')
        send_slack_log('Request info:')
        send_slack_log(str(request.form))
        if request.form.get('payload') is None:
            send_slack_log('Invalid request: no payload')
            return
        else:
            return handle_interaction(json.loads(request.form['payload']))


@api.route('/mattermost_hello')
class MattermostHello(Resource):
    def post(self):
        """
        An API to send hello_world messages to Mattermost
        """
        text = 'HELLO from socnet API Server!'
        return push_to_mattermost(text)


@api.route('/mattermost_msg')
class MattermostMsg(Resource):
    def post(self):
        """
        Get message with the requested message id and return to mattermost
        """
        try:
            msgId = int(request.form['text'])
        except ValueError:
            return {"text": "please enter a valid integer as msg Id."}
        msg = str(read_msg(msgId))
        return {"text": msg}


@api.route('/mattermost_echo')
class MattermostEcho(Resource):
    def post(self):
        """
        A test API for echoing back Mattermost messages
        """
        user = request.form['user_name']
        text = request.form['text']
        return {"text": 'msg sent successfully.\ntext:'
                + text + '\nuser:' + user}


@api.route('/mattermost_msgs')
class MattermostMsgs(Resource):
    def get(self):
        """
        Get all messages and send it to Mattermost
        """
        text = read_filtered_msgs(request.args)
        return push_to_mattermost(text)

    def post(self):
        """
        Put a new message into the system through a Mattermost message
        """
        try:
            msg_json = json.loads(request.form['text'])
        except json.decoder.JSONDecodeError:
            return {"text": "Failed to send msg. Incorrect json format."}
        msgId = write_msg(msg_json)
        responseText = 'successfully created msg ' \
                       'with id: ' + msgId
        return {"text": responseText}


if __name__ == '__main__':
    app.run(host=config['host'], port=port, debug=config['debug'])
