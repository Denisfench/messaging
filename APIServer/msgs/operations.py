from APIServer.database.models import Message
from APIServer.database.schema import MessageSchema
from APIServer import db


from dateutil.parser import parse

from APIServer.commons import constants
import json


DEFAULT_LIMIT = constants.API_SERVER_DEFAULT_LIMIT
DEFAULT_OFFSET = constants.API_SERVER_DEFAULT_OFFSET


# return a list of dict
def convert_to_dic_list(obj):
    if type(obj) is list:
        # if list contain MarshalResut object
        if (len(obj) > 0) and (type(obj[0]) is not dict):
            return [obj[0].data]
        else:
            return obj
    # if obj is a MarshalResult
    else:
        return obj.data


def dic_lst_to_tuple_lst(obj):
    dic_lst = convert_to_dic_list(obj)
    final_lst = []
    for dic in dic_lst:
        if dic == {}:
            continue
        if dic["active"] is True:
            active_repr = "Active"
        else:
            active_repr = "Not Active"
        tup = (dic["id"],
               dic["event_datetime"],
               dic["event_zipcode"],
               dic["event_city"],
               dic["event_state"],
               dic["event_country"],
               dic["event_type"],
               dic["event_description"],
               dic["event_priority"],
               dic["msg_sender"],
               active_repr)
        final_lst.append(tup)
    return final_lst


def query_params_to_list(query_string):
    # query_string = query_string[1:-1]
    query_list = [elem.strip() for elem in query_string.split(",")]
    return query_list


def convert_name(msg):
    msg_new = {"event_zipcode": msg['zipcode'],
               "event_city": msg['city'],
               "event_state": msg['state'],
               "event_country": msg['country'],
               "event_type": msg['type'],
               "event_description": msg['description'],
               "msg_sender": msg['sender'],
               "event_datetime": msg['datetime'],
               "event_priority": msg['priority']}
    if msg.get('active'):
        msg_new['active'] = msg['active']
    return msg_new


def write_msg(msg):
    """
    Add a new message to database
    """
    if 200 in msg:
        msg = json.loads(str(msg[200]))
        for i in msg:
            """
            insert each unique app into db
            """
            msg = {"event_type": i['id'],
                   "event_description": i['name'],
                   "event_datetime": i['released_at'],
                   "event_priority": 3,
                   "msg_sender": "Heroku"}
            new_msg = Message(event_type=msg['event_type'],
                              event_description=msg['event_description'],
                              event_datetime=msg['event_datetime'],
                              msg_sender=msg['msg_sender'],
                              event_priority=msg['event_priority'])
            database = db.session.query(Message)
            check = database.filter(Message.event_type
                                    == new_msg.event_type).first()
            if (not check):
                # unique app found
                db.session.add(new_msg)
                db.session.commit()
            else:
                # check if released_at parameter different from db
                new = new_msg.event_datetime
                old = check.event_datetime
                if(old < new):
                    # need to update released at field
                    database.filter(Message.event_type
                                    == new_msg.event_type).update(
                        {Message.event_datetime: new_msg.event_datetime},
                        synchronize_session=False)
                    db.session.commit()
    elif ("event_zipcode" not in msg):
        msg = convert_name(msg)
        new_msg = Message(event_zipcode=msg['event_zipcode'],
                          event_city=msg['event_city'],
                          event_state=msg['event_state'],
                          event_country=msg['event_country'],
                          event_type=msg['event_type'],
                          event_description=msg['event_description'],
                          msg_sender=msg['msg_sender'],
                          event_datetime=msg['event_datetime'],
                          event_priority=msg['event_priority'])
        db.session.add(new_msg)
        db.session.commit()
    return "Message " + str(new_msg.id) + " inserted"


def update_msg(msg, id):
    fetched_msg = Message.query.get(id)
    if fetched_msg is None:
        return {'message': 'Message' + str(id) + ' does not exist'}, 404
    if ("event_zipcode" not in msg):
        msg = convert_name(msg)
    fetched_msg.event_zipcode = msg['event_zipcode']
    fetched_msg.event_city = msg['event_city']
    fetched_msg.event_state = msg['event_state']
    fetched_msg.event_country = msg['event_country']
    fetched_msg.event_type = msg['event_type']
    fetched_msg.event_description = msg['event_description']
    fetched_msg.msg_sender = msg['msg_sender']
    fetched_msg.event_datetime = msg['event_datetime']
    fetched_msg.event_priority = msg['event_priority']
    if msg.get('active') and msg['active'] == 'Active':
        fetched_msg.active = True
    if msg.get('active') and msg['active'] == 'Not Active':
        fetched_msg.active = False
    db.session.commit()
    return 'Message ' + str(id) + ' updated'


def number_of_msgs():
    """
    This will return the total number of messages.
    """
    return db.session.query(Message).count()


def newest_msg():
    """
    This will return the latest message.
    """
    m = db.session.query(Message).order_by('event_datetime')[-1]
    return m.event_datetime


def oldest_msg():
    """
    This will return the oldest message.
    """
    return db.session.query(Message).first().event_datetime


def read_msg(id):
    fetched_msg = Message.query.get(id)
    msg_schema = MessageSchema()
    msg_json = msg_schema.dump(fetched_msg)
    return dic_lst_to_tuple_lst([msg_json])


def delete_msg(id):
    """
    delete a message from the database
    """
    msg = Message.query.get(id)
    if msg is None:
        return {'message': 'Message ' + str(id) + ' does not exist'}, 404
    # delete message
    db.session.delete(msg)
    db.session.commit()
    return 'Message ' + str(id) + ' deleted'


def add_filter(filter_cond, msgs, filter_fld):
    # print(filter_cond)
    if filter_cond:
        filter_req = query_params_to_list(filter_cond)
        # print(filter_req)
        msgs = msgs.filter(filter_fld.in_(filter_req))
    return msgs


def read_filtered_msgs(query_params):
    priority = query_params.get('priority')
    date = query_params.get('date')
    msg_type = query_params.get('type')
    region = query_params.get('region')
    country = query_params.get('country')
    sender = query_params.get('sender')
    # limit = query_params.get('limit', DEFAULT_LIMIT)
    # offset = query_params.get('offset', DEFAULT_OFFSET)
    active = query_params.get('active')

    # let's init messages to start!
    msgs = Message.query.order_by(Message.event_datetime.desc())
    # we need to set offset and limit after the filters!
    #                  .offset(offset).limit(limit)

    if active:
        active = active.strip()
        active = active.lower()
        active_bool = True
        non_type = None
        if active == 'n':
            active_bool = False
        if active_bool is True:
            msgs = msgs.filter(Message.active == active_bool)
        else:
            msgs = msgs.filter(
                (Message.active == active_bool)
                | (Message.active == non_type))

    msgs = add_filter(region, msgs, Message.event_state)
    msgs = add_filter(priority, msgs, Message.event_priority)
    msgs = add_filter(msg_type, msgs, Message.event_type)
    msgs = add_filter(country, msgs, Message.event_country)
    msgs = add_filter(sender, msgs, Message.msg_sender)
    if date:
        # parse date input in any format (MM-DD-YYY, DD-MM-YYYY, MM/DD/YYYY...)
        required_datetime = parse(date, fuzzy=True)
        # print(required_datetime)
        msgs = msgs.filter(
            Message.event_datetime >= required_datetime)

    print(msgs)
    msg_schema = MessageSchema(many=True)
    msgs_json = msg_schema.dump(msgs)
    # print(dic_lst_to_tuple_lst(msgs_json))
    return dic_lst_to_tuple_lst(msgs_json)
