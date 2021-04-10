from APIServer.database.models import Status
import json
from APIServer import db


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

    for i in range(len(status)):
        """
        which app was last deployed
        """
        inpRow = convert_name(status[i])
        new_status = Status(app_id=inpRow["app_id"],
                            name=inpRow['name'],
                            released_at=inpRow['released_at'])
        db.session.add(new_status)
        db.session.commit()
    return "Status " + str(new_status.id) + " inserted"


def latest_deployment():
    """
    find latest deployments and return it
    """
    s = db.session.query(Status).order_by('released_at')[-1]
    return [s.name, (s.released_at).strftime("%m/%d/%Y, %H:%M:%S")]
