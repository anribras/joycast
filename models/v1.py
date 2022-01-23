from . import db, TimeStampMixin
from sqlalchemy import UniqueConstraint, Index


class User(TimeStampMixin, db.Model):
    id = db.Column(db.BIGINT, primary_key=True, autoincrement=True)
    username = db.Column(db.VARCHAR(256), nullable=False, index=True, unique=True)
    password = db.Column(db.VARCHAR(256), nullable=False, index=True)
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


class Category(db.Model):
    id = db.Column(db.BIGINT, primary_key=True, autoincrement=True)
    name = db.Column(db.VARCHAR(256), nullable=False, unique=True)

    def __init__(self, name):
        self.name = name


class AlbumStatics(db.Model):
    id = db.Column(db.BIGINT, primary_key=True, autoincrement=True)
    play_counts = db.Column(db.BIGINT, nullable=True)
    subscribe_counts = db.Column(db.BIGINT, nullable=True)
    comment_counts = db.Column(db.BIGINT, nullable=True)
    like_counts = db.Column(db.BIGINT, nullable=True)
    album_id = db.Column(db.BIGINT, nullable=False, unique=True)
    album = db.relationship(
        'Album',
        # foreign_keys means ,
        foreign_keys=[album_id],
        primaryjoin=lambda: AlbumStatics.album_id == Album.id,
        backref='statics',
        lazy=True,
        uselist=False)

    vip_type = db.Column(db.SMALLINT, nullable=True)
    is_finished = db.Column(db.SMALLINT, nullable=True)
    is_public = db.Column(db.BOOLEAN, nullable=True)
    has_buy = db.Column(db.BOOLEAN, nullable=True)
    is_paid = db.Column(db.BOOLEAN, nullable=True)


class AlbumTagPivot(db.Model):
    __tablename__ = 'album_tag_pivot'

    id = db.Column(db.BIGINT, primary_key=True, autoincrement=True)
    album_id = db.Column(db.BIGINT, nullable=False)
    tag_id = db.Column(db.BIGINT, nullable=False)
    extra_ = db.Column(db.VARCHAR(2048), nullable=True)

    def __init__(self, **kwargs):
        super(AlbumTagPivot, self).__init__(**kwargs)


class Album(TimeStampMixin, db.Model):
    id = db.Column(db.BIGINT, primary_key=True, autoincrement=True)
    source_type = db.Column(db.SMALLINT, nullable=False)
    source_id = db.Column(db.BIGINT, nullable=False)
    category_id = db.Column(db.BIGINT, nullable=False)
    category = db.relationship(
        'Category',
        foreign_keys=[category_id],
        primaryjoin=lambda: Album.category_id == Category.id,
        lazy=True,
        uselist=False)
    # as redundant column
    category_name = db.Column(db.VARCHAR(256), nullable=False)

    user_id = db.Column(db.BIGINT, nullable=False)

    # user_id = db.Column(db.BIGINT, db.ForeignKey = True, nullable=False)
    # Dont 'use db foreign keys !, use pure relationship, works like:
    # 1. album.user; 2.user.albums
    user = db.relationship('User', foreign_keys=[user_id],
                           primaryjoin=lambda: Album.user_id == User.id,
                           backref='albums',
                           lazy=True
                           )
    album_create_date = db.Column(db.DateTime, nullable=True)
    album_update_date = db.Column(db.DateTime, nullable=True)
    title = db.Column(db.VARCHAR(1024), nullable=False)
    short_intro = db.Column(db.TEXT, nullable=True)
    rich_intro = db.Column(db.TEXT, nullable=True)
    rich_detail_intro = db.Column(db.TEXT, nullable=True)
    cover = db.Column(db.VARCHAR(1024), nullable=False)
    rss = db.Column(db.VARCHAR(1024), nullable=False)
    track_total_counts = db.Column(db.BIGINT, nullable=False)

    tags = db.relationship('Tag', secondary='album_tag_pivot',
                           primaryjoin=lambda: Album.id == AlbumTagPivot.album_id,
                           secondaryjoin=lambda: AlbumTagPivot.tag_id == Tag.id,
                           lazy=True)
    UniqueConstraint('source_id', 'title')


class Tag(db.Model):
    id = db.Column(db.BIGINT, primary_key=True, autoincrement=True)
    name = db.Column(db.VARCHAR(256), nullable=False)
    is_channel = db.Column(db.BOOLEAN, nullable=False)

    albums = db.relationship('Album', secondary='album_tag_pivot',
                             primaryjoin=lambda: Tag.id == AlbumTagPivot.tag_id,
                             secondaryjoin=lambda: Album.id == AlbumTagPivot.album_id,
                             lazy=True)

    def __init__(self, **kwargs):
        super(Tag, self).__init__(**kwargs)


class TrackStatics(db.Model):
    id = db.Column(db.BIGINT, primary_key=True, autoincrement=True)
    play_counts = db.Column(db.BIGINT, nullable=True)
    subscribe_counts = db.Column(db.BIGINT, nullable=True)
    comment_counts = db.Column(db.BIGINT, nullable=True)
    like_counts = db.Column(db.BIGINT, nullable=True)
    track_id = db.Column(db.BIGINT, nullable=False, unique=True)
    track = db.relationship(
        'Track',
        # foreign_keys means ,
        foreign_keys=[track_id],
        primaryjoin=lambda: TrackStatics.track_id == Track.id,
        backref='statics',
        lazy=True,
        uselist=False)


class Track(TimeStampMixin, db.Model):
    id = db.Column(db.BIGINT, primary_key=True, autoincrement=True)
    source_type = db.Column(db.SMALLINT, nullable=False)
    source_id = db.Column(db.BIGINT, nullable=False)
    index = db.Column(db.BIGINT, nullable=False)
    user_id = db.Column(db.BIGINT, nullable=False)
    user = db.relationship('User', foreign_keys=[user_id], primaryjoin=lambda: User.id == Track.user_id, lazy=True)

    album_id = db.Column(db.BIGINT, nullable=False, index=True)
    album = db.relationship('Album', foreign_keys=[album_id], primaryjoin=lambda: Album.id == Track.album_id, lazy=True)

    audio = db.Column(db.VARCHAR(1024), nullable=False)
    audio_duration = db.Column(db.BIGINT, nullable=False)

    title = db.Column(db.VARCHAR(1024), nullable=False)
    cover = db.Column(db.VARCHAR(1024), nullable=False)
    short_intro = db.Column(db.TEXT, nullable=False)
    rich_intro = db.Column(db.TEXT, nullable=False)

    last_update = db.Column(db.DateTime, nullable=True)

    Index('idx_source_id_title', 'source_id', 'album_id')
