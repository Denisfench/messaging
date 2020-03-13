import os
import sqlite3

from APIServer.database.sqlite import get_db
from APIServer import db
from APIServer.database.models import Thread,Comment

def add_comment(comment, thread_id):
    fetched_thread = Thread.query.get(thread_id)
    if fetched_thread is None:
        return {'message' : 'Thread ' + str(thread_id) + ' does not exist'}, 404
    first_comment_id = fetched_thread.first_comment_id
    last_comment_id = fetched_thread.last_comment_id
    comment_text = comment['text']
    new_comment = Comment(content=comment_text)
    db.session.add(new_comment)
    db.session.commit()

    new_id = new_comment.id
    fetched_thread.last_comment_id = new_id
    if first_comment_id == -1:
        fetched_thread.first_comment_id = new_id
    if last_comment_id != -1:
        fetched_comment = Comment.query.get(last_comment_id)
        fetched_comment.next_comment_id = new_id
    db.session.commit()
    return 'Comment %d inserted to thread %d' % (new_id, thread_id)


def get_comments(thread_id):
    fetched_thread = Thread.query.get(thread_id)
    if fetched_thread is None:
        return {'message' : 'Thread ' + str(thread_id) + ' does not exist'}, 404
    first_comment_id = fetched_thread.first_comment_id
    comment_id = first_comment_id
    comments = []
    while comment_id != -1:
        fetched_comment = Comment.query.get(comment_id)
        comments.append({comment_id: fetched_comment.content})
        comment_id = fetched_comment.next_comment_id
    return comments
