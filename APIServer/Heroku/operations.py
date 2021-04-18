from APIServer.database.models import Status
from APIServer.database.schema import StatusSchema

import json
from APIServer import db

from APIServer.msgs.operations import convert_to_dic_list
from APIServer.msgs.operations import query_params_to_list

import pytz
from dateutil.parser import parse


def convert_name(status):
    status_new = {"app_id": status['id'],
                  "name": status['name'],
                  "released_at": parse(status['released_at'])}
    return status_new


def write_status(status):
    """
    Add/update an app info to database
    """
    status = json.loads(str(status[200]))
    print(len(status))
    for i in range(len(status)):
        """
        insert each unique app into db
        """

        inpRow = convert_name(status[i])
        new_status = Status(app_id=inpRow["app_id"],
                            name=inpRow['name'],
                            released_at=inpRow['released_at'])
        check = db.session.query(Status).filter(Status.app_id
                                                == new_status.app_id).first()
        if (not check):
            # unique app found
            db.session.add(new_status)
            db.session.commit()
        else:
            # check if released_at parameter different from db
            utc = pytz.UTC
            new = new_status.released_at
            old = utc.localize(check.released_at)
            if(old < new):
                # need to update released at field
                db.session.query(Status).filter(Status.app_id
                                                == new_status.app_id).update(
                    {Status.released_at: new_status.released_at},
                    synchronize_session=False)
                db.session.commit()

    return "Status " + str(new_status.id) + " inserted"


def latest_deployment():
    """
    find latest deployments and return it
    """
    s = db.session.query(Status).order_by('released_at')[-1]
    return [s.name, (s.released_at).strftime("%m/%d/%Y, %H:%M:%S")]


def dic_lst_to_tuple_lst(obj):
    dic_lst = convert_to_dic_list(obj)
    final_lst = []
    for dic in dic_lst:
        if dic == {}:
            continue
        tup = (dic["app_id"],
               dic["name"],
               dic["released_at"])
        final_lst.append(tup)
    return final_lst


def read_heroku_apps(query_params):
    """
    reads from the database that contains
    all heroku apps and latest deployment
    """
    app_id = query_params.get('app_id')
    name = query_params.get('name')
    released_at = query_params.get('released_at')
    # need to handle multiple filter conditions
    if (app_id):
        required_parameter = query_params_to_list(app_id)
    elif (name):
        required_parameter = query_params_to_list(name)
    elif (released_at):
        required_parameter = query_params_to_list(released_at)
    try:
        status = Status.query.filter(Status.name.in_(required_parameter))
    except Exception:
        status = Status.query.all()
    status_schema = StatusSchema(many=True)
    msgs_json = status_schema.dump(status)
    return dic_lst_to_tuple_lst(msgs_json)
