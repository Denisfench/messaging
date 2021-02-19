from APIServer.commons.api_utils import read_json


def get_message_form(path):
    return read_json(path)


def create_message_json(msg_tuple):
    '''
    Create msg_json from a message tuple
    '''
    msg_json = {}
    msg_json['datetime'] = msg_tuple[1]
    msg_json['zipcode'] = msg_tuple[2]
    msg_json['city'] = msg_tuple[3]
    msg_json['state'] = msg_tuple[4]
    msg_json['country'] = msg_tuple[5]
    msg_json['type'] = msg_tuple[6]
    msg_json['description'] = msg_tuple[7]
    msg_json['priority'] = msg_tuple[8]
    msg_json['sender'] = msg_tuple[9]
    return msg_json
