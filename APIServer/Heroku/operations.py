from APIServer.database.models import Status
# from APIServer.database.schema import StatusSchema
from APIServer import db


# from dateutil.parser import parse


# from APIServer.Heroku.pull import get_heroku_status


def convert_name(status):
    status_new = {"app_id": status['id'],
                  "name": status['name'],
                  "released_at": status['released_at']}
    return status_new


def write_status(status):
    """
    Add/update an app info to database
    """
    if ("app_id" not in status):
        """
        created new status
        """
        status = convert_name(status)
    new_status = Status(app_id=status['app_id'],
                        name=status['name'],
                        released_at=status['released_at'])
    db.session.add(new_status)
    db.session.commit()
    return "Status " + str(new_status.id) + " inserted"
