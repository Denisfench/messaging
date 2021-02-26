"""
"""
from unittest import TestCase, main
import json
from flask_restplus import Resource
import responses

from APIServer import db

import APIServer.api_endpoints
from APIServer.api_endpoints import app, HelloWorld, MessageFormat, MsgsLists
from APIServer.commons.api_utils import err_return, read_json

test_config_path = 'APIServer/test_data/test_config.json'
APIServer.api_endpoints.config = read_json(test_config_path)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

test_json = read_json('APIServer/test_data/test_json.json')
test_response = read_json('APIServer/test_data/test_response.json')
test_update = read_json('APIServer/test_data/test_update.json')
test_update_response = \
    read_json('APIServer/test_data/test_update_response.json')

SLACK_CONFIG_PATH = 'APIServer/test_data/slack/test_slack.json'
slack_config = read_json(SLACK_CONFIG_PATH)


with app.app_context():
    db.session.remove()
    db.drop_all()


class Test(TestCase):
    def setUp(self):
        # none of the object's members names should have caps!
        self.messageformat = MessageFormat(Resource)
        self.HelloWorld = HelloWorld(Resource)
        self.msgs = MsgsLists(Resource)
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_hello_world(self):
        """
        Testing if HelloWorld works.
        """
        rv = self.HelloWorld.get()
        self.assertEqual(rv, {'hello': 'socnet'})

    def test_get_message_format(self):
        """
        Testing if MessageFormat returns the form.
        """
        rv = self.messageformat.get()
        self.assertEqual(type(rv), dict)

    def test_err_return(self):
        """
        Testing if we are able to get the right error message
        """
        rv = err_return("error message")
        self.assertEqual(rv, {"Error": "error message"})
        rv = read_json('makefile')
        self.assertEqual(rv, {"Error": "Not a valid json file"})
        rv = read_json('fake_file_location')
        self.assertEqual(rv, {"Error": "Json file not found"})
        rv = read_json('test_data/test_json.json')
        self.assertEqual(rv.get('Error'), None)

    def test_endpoints(self):
        """
        Testing if the available endpoints show the right information
        """
        with app.test_client() as c:
            rv = c.get('/endpoints')
            endpoints = eval(
                rv.data.decode('utf-8')[:-1])['Available endpoints']
            self.assertEqual(type(endpoints), dict)
            for ep in endpoints:
                self.assertEqual(type(endpoints[ep]), dict)
                for method in endpoints[ep]:
                    self.assertEqual(type(endpoints[ep][method]), str)

    def test_msgs(self):
        """
        Testing if the msgs module works
        """
        with app.test_client() as c:
            rv = c.get('/msgs')
            self.assertEqual(eval(rv.data.decode('utf-8')[:-1]), [])

            # Should not be able to update or delete msg before inserting
            rv = c.put('/msgs/1', json=test_update)
            self.assertEqual(rv.status_code, 404)

            rv = c.delete('/msgs/1')
            self.assertEqual(rv.status_code, 404)

            rv = c.post('/msgs', json=test_json)
            self.assertEqual(rv.status_code, 200)

            rv = c.get('/msgs/1')
            self.assertEqual(eval(rv.data.decode('utf-8')[:-1]), test_response)

            rv = c.get('/msgs')
            self.assertEqual(eval(rv.data.decode('utf-8')[:-1]),
                             test_response)

            rv = c.put('/msgs/1', json=test_update)
            self.assertEqual(rv.status_code, 200)

            rv = c.get('/msgs/1')
            self.assertEqual(eval(rv.data.decode('utf-8')[:-1]),
                             test_update_response)

            rv = c.get('/msgs')
            self.assertEqual(eval(rv.data.decode('utf-8')[:-1]),
                             test_update_response)

            rv = c.delete('/msgs/1')
            self.assertEqual(rv.status_code, 200)

            rv = c.get('/msgs')
            self.assertEqual(eval(rv.data.decode('utf-8')[:-1]), [])

            rv = c.put('/msgs/1', json=test_update)
            self.assertEqual(rv.status_code, 404)

            rv = c.delete('/msgs/1')
            self.assertEqual(rv.status_code, 404)

    def test_msg_filtering(self):
        """
        Testing if msgs filtering works
        """
        with app.test_client() as c:
            rv = c.get('/msgs')
            self.assertEqual(eval(rv.data.decode('utf-8')[:-1]), [])

            rv = c.post('/msgs', json=test_json)
            self.assertEqual(rv.status_code, 200)

            rv = c.get('/msgs?region=New York')
            self.assertEqual(eval(rv.data.decode('utf-8')[:-1]), test_response)

            rv = c.get('/msgs?region=New Jersey')
            self.assertEqual(eval(rv.data.decode('utf-8')[:-1]), [])

            rv = c.get('/msgs?priority=Low')
            self.assertEqual(eval(rv.data.decode('utf-8')[:-1]), test_response)

            rv = c.get('/msgs?priority=High')
            self.assertEqual(eval(rv.data.decode('utf-8')[:-1]), [])

            rv = c.get('/msgs?type=Fire')
            self.assertEqual(eval(rv.data.decode('utf-8')[:-1]), test_response)

            rv = c.get('/msgs?type=Smoke')
            self.assertEqual(eval(rv.data.decode('utf-8')[:-1]), [])

            rv = c.get('/msgs?date=2019-01-01')
            self.assertEqual(eval(rv.data.decode('utf-8')[:-1]), test_response)

            rv = c.get('/msgs?date=2022-01-01')
            self.assertEqual(eval(rv.data.decode('utf-8')[:-1]), [])

            rv = c.get('/msgs?country=USA')
            self.assertEqual(eval(rv.data.decode('utf-8')[:-1]), test_response)

            rv = c.get('/msgs?country=Canada')
            self.assertEqual(eval(rv.data.decode('utf-8')[:-1]), [])

            rv = c.get('/msgs?active=y')
            self.assertEqual(eval(rv.data.decode('utf-8')[:-1]), test_response)

            rv = c.get('/msgs?active=n')
            self.assertEqual(eval(rv.data.decode('utf-8')[:-1]), [])

            rv = c.get('/msgs?region=\
                New York&priority=Low&type=Fire&country=USA&date=2019-01-01')
            self.assertEqual(eval(rv.data.decode('utf-8')[:-1]), test_response)

            rv = c.put('/msgs/1', json=test_update)
            self.assertEqual(rv.status_code, 200)

            rv = c.get('/msgs?active=n')
            self.assertEqual(eval(rv.data.decode('utf-8')[:-1]),
                             test_update_response)

            rv = c.get('/msgs?active=y')
            self.assertEqual(eval(rv.data.decode('utf-8')[:-1]), [])

    def test_threads(self):
        """
        Testing if threads module works
        """
        with app.test_client() as c:

            rv = c.post('/msgs', json=test_json)
            rv = c.post('/msgs', json=test_json)

            rv = c.put('/threads/1', json={'text': 'some comment'})
            self.assertEqual(rv.status_code, 200)

            rv = c.put('/threads/2', json={'text': 'comment x'})
            self.assertEqual(rv.status_code, 200)

            rv = c.put('/threads/1', json={'text': 'new comment'})
            self.assertEqual(rv.status_code, 200)

            rv = c.put('/threads/1', json={'text': '3rd comment'})
            self.assertEqual(rv.status_code, 200)

            rv = c.put('/threads/2', json={'text': 'comment yy'})
            self.assertEqual(rv.status_code, 200)

            rv = c.put('/threads/2', json={'text': 'comment zzz'})
            self.assertEqual(rv.status_code, 200)

            rv = c.get('/threads/1')
            self.assertEqual(eval(rv.data.decode('utf-8')[:-1]),
                             [{"1": "some comment"},
                              {"3": "new comment"},
                              {"4": "3rd comment"}])

            rv = c.delete('/msgs/1')

            # The thread associated with the msg
            # should be deleted after the msg is deleted
            rv = c.get('/threads/1')
            self.assertEqual(rv.status_code, 404)

            rv = c.get('/threads/2')
            self.assertEqual(eval(rv.data.decode('utf-8')[:-1]),
                             [{"2": "comment x"},
                              {"5": "comment yy"},
                              {"6": "comment zzz"}])

            rv = c.delete('/msgs/2')

            # The thread associated with the msg
            # should be deleted after the msg is deleted
            rv = c.get('/threads/2')
            self.assertEqual(rv.status_code, 404)

    def test_threads_err(self):
        """
        Testing if the threads module returns 404 code
        when a thread does not exist
        """
        with app.test_client() as c:

            rv = c.put('/threads/1', json={'text': 'some comment'})
            self.assertEqual(rv.status_code, 404)

            rv = c.get('/threads/1')
            self.assertEqual(rv.status_code, 404)

    @responses.activate
    def test_slack(self):
        """
        Testing if Slack related endpoints work
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
            'url': slack_config['Post_Chat_URL'],
            'body': 'ok',
            'status': 200,
            'content_type': 'application/json'
        })
        responses.add(**{
            'method': responses.POST,
            'url': slack_config['Views_Open_URL'],
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
        with app.test_client() as c:
            # check if /slack/submit can handle the calls without payload
            rv = c.post('/slack/submit')
            self.assertEqual(rv.status_code, 200)

            # check if /slack/post_msg works (it opens a form in Slack)
            rv = c.post('/slack/post_msg',
                        data=dict(trigger_id='my_trigger_id',
                                  channel_id='my_channel'))
            self.assertEqual(rv.status_code, 200)

            # check if we can post an msg through /slack/submit
            POST_PAYLOAD_PATH = APIServer.api_endpoints.config[
                'slack_post_payload']
            post_msg_payload = read_json(POST_PAYLOAD_PATH)
            rv = c.post('/slack/submit', data=dict(
                payload=json.dumps(post_msg_payload)))
            self.assertEqual(rv.status_code, 200)

            # check if the previous msg was successfully posted
            rv = c.get('msgs/1')
            self.assertEqual(len(eval(rv.data.decode('utf-8')[:-1])), 1)
            msg = eval(rv.data.decode('utf-8')[:-1])
            msg[0][1] = test_response[0][1]  # ignore time
            self.assertEqual(test_response, msg)

            # check if /slack/get_msg works
            rv = c.post('/slack/get_msg',
                        data=dict(text='1', channel_id='my_channel'))
            self.assertEqual(rv.status_code, 200)

            # try to use /slack/submit to get filtered results
            FILTER_PAYLOAD_PATH = APIServer.api_endpoints.config[
                'slack_filter_msgs_payload']
            filter_msgs_payload = read_json(FILTER_PAYLOAD_PATH)
            rv = c.post('/slack/submit',
                        data=dict(payload=json.dumps(filter_msgs_payload)))
            self.assertEqual(rv.status_code, 200)

            # check if /slack/update_msg works (it opens a form in Slack)
            rv = c.post('/slack/update_msg',
                        data=dict(trigger_id='my_trigger_id',
                                  channel_id='my_channel'))
            self.assertEqual(rv.status_code, 200)

            # check if we can update an msg through /slack/submit
            UPDATE_PAYLOAD_PATH = APIServer.api_endpoints.config[
                'slack_update_payload']
            update_msg_payload = read_json(UPDATE_PAYLOAD_PATH)
            rv = c.post('/slack/submit',
                        data=dict(payload=json.dumps(update_msg_payload)))
            new_msg = eval(
                c.get('msgs/1').data.decode('utf-8')[:-1])
            self.assertEqual(rv.status_code, 200)
            self.assertEqual('10003', new_msg[0][2])
            self.assertEqual('Slack', new_msg[0][9])
            self.assertEqual('Not Active', new_msg[0][10])

            # try to use /slack/submit to update an msg that does not exist
            UPDATE_PAYLOAD_PATH = APIServer.api_endpoints.config[
                'slack_update_payload_invalid']
            update_msg_payload = read_json(UPDATE_PAYLOAD_PATH)
            rv = c.post('/slack/submit',
                        data=dict(payload=json.dumps(update_msg_payload)))
            self.assertEqual(rv.status_code, 200)

            # check if /slack/delete_msg works
            rv = c.post('/slack/delete_msg', data=dict(text='1'))
            self.assertEqual(rv.status_code, 200)

            # check if the previous msg was successfully deleted
            rv = c.get('msgs/1')
            self.assertEqual(len(eval(rv.data.decode('utf-8')[:-1])), 0)

            # check if /slack/filter_msgs works (it opens a form in Slack)
            rv = c.post('/slack/filter_msgs',
                        data=dict(trigger_id='my_trigger_id',
                                  channel_id='my_channel'))
            self.assertEqual(rv.status_code, 200)

            # check if /slack/submit works when next_page button is clicked
            NEXT_PAGE_PAYLOAD_PATH = APIServer.api_endpoints.config[
                'slack_next_page_payload']
            next_page_payload = read_json(NEXT_PAGE_PAYLOAD_PATH)
            rv = c.post('/slack/submit',
                        data=dict(payload=json.dumps(next_page_payload)))
            self.assertEqual(rv.status_code, 200)


if __name__ == "__main__":
    main()
