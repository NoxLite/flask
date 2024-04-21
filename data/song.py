import sqlalchemy
import sqlalchemy.orm as orm
import datetime
from .db_session import SqlAlchemyBase


class Song(SqlAlchemyBase):
    __tablename__ = 'songs'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user_link = sqlalchemy.Column(sqlalchemy.String)
    cover = sqlalchemy.Column(sqlalchemy.String, default='pipstatic/inf/covers/classic.png')
    likes = sqlalchemy.Column(sqlalchemy.Integer)
    genre = sqlalchemy.Column(sqlalchemy.String, default='0')
    link_spotify = sqlalchemy.Column(sqlalchemy.String, default=None)
    link_yandex = sqlalchemy.Column(sqlalchemy.String, default=None)
    link_youtube = sqlalchemy.Column(sqlalchemy.String, default=None)
    user = orm.relationship('User')
