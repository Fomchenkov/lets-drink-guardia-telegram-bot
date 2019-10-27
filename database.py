import datetime

from peewee import *

import config


db = SqliteDatabase(config.DB_NAME)


def create_tables():
    """
    Создать нужные таблицы
    """
    db.connect()
    db.create_tables([User])


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    uid = IntegerField(unique=True)
    name = TextField()
    age = IntegerField()
    # 0 - Мужчина, 1 - Женщина
    gender = BooleanField()
    about = TextField()
    location_lat = TextField()
    location_long = TextField()
