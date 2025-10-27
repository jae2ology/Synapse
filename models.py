# defines the structure of data in my database

from datetime import datetime
from flask_login import UserMixin
from app import db

#default implementations for methods in flask-login
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128)) # stash hashed passwords
    is_anonymous = db.Column(db.Boolean, default=False) # to tell whos anon and whos not

    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy = 'dynamic')
    votes = db.relationship('Vote', backref='voter', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

# model for posts and main messages
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user_id'))
    channel = db.Column(db.String(64), index=True, default='general') # channels e.g computer_science, electrical_engineering, general

    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade="all, delete-orphan")
    votes = db.relationship('Vote', backref='post', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return '<Post {}>'.format(self.body)

    def total_votes(self):
        # calculate total votes (upvote vs downvote)
        return sum(vote.value for vote in self.votes)

# model for comments
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __repr__(self):
        return '<Comment {}'.format(self.body)


# model for upvoting/downvoting
class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    value = db.Column(db.SmallInteger, default=0) # + 1 for upvote -1 for downvote

    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='_user_post_uc'), ) # one vote per user

    def __repr__(self):
        return '<Vote {} for Post {}>'.format(self.value, self.post_id)

