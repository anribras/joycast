from . import db, TimeStampMixin
from backend.auth import lm
from flask_login import UserMixin, AnonymousUserMixin


class User(TimeStampMixin, UserMixin, db.Model):
    id = db.Column(db.BIGINT, primary_key=True, autoincrement=True)
    username = db.Column(db.VARCHAR(256), nullable=False,index=True, unique=True)
    password = db.Column(db.VARCHAR(256), nullable=False,index=True)
    nickname = db.Column(db.VARCHAR(256))
    avatar = db.Column(db.VARCHAR(1024))
    intro = db.Column(db.VARCHAR(1024))
    user_type = db.Column(db.SMALLINT)

    def __init__(self, username, password, nickname='joycast_rookie', avatar='', intro='new', user_type=1):
        self.username = username
        self.password = password
        self.nickname = nickname
        self.avatar = avatar
        self.intro = intro
        self.user_type = user_type
