from . import db, TimeStampMixin


class User(TimeStampMixin, db.Model):

    id = db.Column(db.BIGINT, primary_key=True, autoincrement=True)
    username = db.Column(db.String(256))