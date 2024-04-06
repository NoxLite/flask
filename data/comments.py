import sqlalchemy
from sqlalchemy import orm
from data.user import User
import datetime
from data import db_session
from .db_session import SqlAlchemyBase
db_session.global_init('db/sova.db')
db_sess = db_session.create_session()


class Comments(SqlAlchemyBase):
    __tablename__ = 'comments'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    post_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("posts.id"))
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    text = sqlalchemy.Column(sqlalchemy.String)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)

    def get_user_name(self):
        return db_sess.query(User).filter(User.id == self.user_id).first().name

    def get_user_link(self):
        return f'/profile/{self.user_id}'
