"""Таблица постов"""


import sqlalchemy
import sqlalchemy.orm as orm
import datetime
from .db_session import SqlAlchemyBase


class Posts(SqlAlchemyBase):
    __tablename__ = 'posts'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user_link = sqlalchemy.Column(sqlalchemy.String)
    post_link = sqlalchemy.Column(sqlalchemy.String)
    likes = sqlalchemy.Column(sqlalchemy.Integer)
    user = orm.relationship('User')
