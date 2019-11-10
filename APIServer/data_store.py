import os

DB_TEMP = 'db_temp'


def write_alert(msg, key):
    f = open(DB_TEMP, 'a')
    msg_str = 'Record ' + str(key) + ' : ' \
                        + 'Date ' + msg.get('Date', '') + '|' \
                        + 'Time ' + msg.get('Time', '') + '|' \
                        + 'Type ' + msg.get('Type', '') + '|' \
                        + 'Location ' + msg.get('Location', '') + '|' \
                        + 'Text ' + msg.get('Text', '') + '|' \
                        + 'Who ' + msg.get('Who', '') + '|' \
                        + 'Org ' + msg.get('Org', '') + '\n'
    f.write(msg_str)
    f.close()
    return


def read_alert(key):
    f = open(DB_TEMP, 'r')
    for line in f:
        num = line.split(' ')[1]
        if int(num) == key:
            return line
    return 'No record found!'


def db_init():
    if not os.path.isfile(DB_TEMP):
        open(DB_TEMP, 'w+')