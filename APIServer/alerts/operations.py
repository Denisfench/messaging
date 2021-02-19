from APIServer.database.models import Message, Thread
from APIServer.database.schema import MessageSchema
from APIServer import db
from APIServer.threads.operations import delete_thread

from dateutil.parser import parse

from APIServer.commons import constants


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


def write_message(msg):
    """
    Add a new message to database
    """
    if ("event_zipcode" not in msg):
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
    # add a new thread for the message
    new_thread = Thread(id=new_msg.id,
                        first_comment_id=-1,
                        last_comment_id=-1)
    db.session.add(new_thread)
    db.session.commit()
    return "Message " + str(new_msg.id) + " inserted"


def update_message(msg, id):
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


def number_of_messages():
    """
    This will return the total number of messages.
    """
    return db.session.query(Message).count()


def newest_message():
    """
    This will return the latest message.
    """
    m = db.session.query(Message).order_by('event_datetime')[-1]
    return m.event_datetime


def oldest_message():
    """
    This will return the oldest message.
    """
    return db.session.query(Message).first().event_datetime


def read_message(id):
    fetched_msg = Message.query.get(id)
    msg_schema = MessageSchema()
    msg_json = msg_schema.dump(fetched_msg)
    return dic_lst_to_tuple_lst([msg_json])


def delete_message(id):
    """
    delete a message and associated thread from the database
    """
    msg = Message.query.get(id)
    if msg is None:
        return {'message': 'Message ' + str(id) + ' does not exist'}, 404
    # delete associated thread
    delete_thread(id)
    # delete message
    db.session.delete(msg)
    db.session.commit()
    return 'Message ' + str(id) + ' deleted'


def read_filtered_messages(query_params):
    priority_value = query_params.get('priority')
    date_value = query_params.get('date')
    type_value = query_params.get('type')
    region_value = query_params.get('region')
    country_value = query_params.get('country')
    limit = query_params.get('limit', DEFAULT_LIMIT)
    offset = query_params.get('offset', DEFAULT_OFFSET)
    active = query_params.get('active')
    msgs = None

    if region_value:
        required_regions = query_params_to_list(region_value)
        # print(required_regions)
        if msgs:
            msgs = Message.query.filter(
                Message.event_state.in_(required_regions))
        else:
            msgs = Message.query.filter(
                Message.event_state.in_(required_regions))

    if active:
        active = active.strip()
        active = active.lower()
        active_bool = True
        non_type = None
        if active == 'n':
            active_bool = False
        if msgs:
            if active_bool is True:
                msgs = msgs.filter(Message.active == active_bool)
            else:
                msgs = msgs.filter(
                    (Message.active == active_bool)
                    | (Message.active == non_type))
        else:
            if active_bool is True:
                msgs = Message.query.filter(Message.active == active_bool)
            else:
                msgs = Message.query.filter(
                    (Message.active == active_bool)
                    | (Message.active == non_type))

    if priority_value:
        required_priority = query_params_to_list(priority_value)
        # print(required_priority)
        if msgs:
            msgs = msgs.filter(Message.event_priority.in_(required_priority))
        else:
            msgs = Message.query.filter(
                Message.event_priority.in_(required_priority))

    if date_value:
        # parse date input in any format (MM-DD-YYY, DD-MM-YYYY, MM/DD/YYYY...)
        required_datetime = parse(date_value, fuzzy=True)
        # print(required_datetime)
        if msgs:
            msgs = msgs.filter(
                Message.event_datetime >= required_datetime)
        else:
            msgs = Message.query.filter(
                Message.event_datetime >= required_datetime)

    if type_value:
        required_type = query_params_to_list(type_value)
        # print(required_type)
        if msgs:
            msgs = msgs.filter(
                Message.event_type.in_(required_type))
        else:
            msgs = Message.query.filter(
                Message.event_type.in_(required_type))

    if country_value:
        required_country = query_params_to_list(country_value)
        # print(required_country)
        if msgs:
            msgs = msgs.filter(
                Message.event_country.in_(required_country))
        else:
            msgs = Message.query.filter(
                Message.event_country.in_(required_country))
    if msgs:
        msgs = msgs.order_by(Message.event_datetime.desc()) \
                       .offset(offset).limit(limit)
    else:
        msgs = Message.query.order_by(Message.event_datetime.desc()) \
                      .offset(offset).limit(limit)

    # msgs = msgs.all()
    # print(msgs)
    msg_schema = MessageSchema(many=True)
    msgs_json = msg_schema.dump(msgs)
    # print(dic_lst_to_tuple_lst(msgs_json))
    return dic_lst_to_tuple_lst(msgs_json)
