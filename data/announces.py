import datetime

import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Announces(SqlAlchemyBase):
    __tablename__ = 'announces'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    fandom = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    exchange = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    cost = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='no_photo.png')
    claim = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True, default=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')
