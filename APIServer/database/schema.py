from APIServer.database.models import Message, Thread, Comment
from marshmallow_sqlalchemy import ModelSchema


class MessageSchema(ModelSchema):
    class Meta:
        model = Message


class ThreadSchema(ModelSchema):
    class Meta:
        model = Thread


class CommentSchema(ModelSchema):
    class Meta:
        model = Comment
