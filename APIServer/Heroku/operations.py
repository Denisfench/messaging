from APIServer.database.models import Status
from APIServer.database.schema import StatusSchema

import json
from APIServer import db

from APIServer.msgs.operations import convert_to_dic_list
from APIServer.msgs.operations import add_filter

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


def dict_lst_to_tuple_lst(obj):
    """
    converts list of dictionaries
    to list of tuples
    """
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
    status = Status.query.order_by(Status.released_at.desc())
    status = add_filter(app_id, status, Status.app_id)
    status = add_filter(name, status, Status.name)
    status = add_filter(released_at, status, Status.released_at)
    status_schema = StatusSchema(many=True)
    status_json = status_schema.dump(status)
    return dict_lst_to_tuple_lst(status_json)
