from APIServer import db


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    event_datetime = db.Column(db.Text)
    event_zipcode = db.Column(db.Text, default=None)
    event_city = db.Column(db.Text, default=None)
    event_state = db.Column(db.Text, default=None)
    event_country = db.Column(db.Text, default=None)
    event_type = db.Column(db.Text)
    event_description = db.Column(db.Text, default=None)
    event_priority = db.Column(db.Text, default=None)
    msg_sender = db.Column(db.Text, default=None)
    active = db.Column(db.Boolean, default=True)


class Thread(db.Model):
    __tablename__ = "threads"

    id = db.Column(db.Integer, primary_key=True)
    first_comment_id = db.Column(db.Integer, default=-1)
    last_comment_id = db.Column(db.Integer, default=-1)


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text)
    next_comment_id = db.Column(db.Integer, default=-1)


class Status(db.Model):
    __tablename__ = "apps"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    app_id = db.Column(db.Text)
    name = db.Column(db.Text)
    released_at = db.Column(db.DateTime)
