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
	db.create_tables([comments])
	db.create_tables([geoposition])


class BaseModel(Model):

	class Meta:
		database = db


class User(BaseModel):
	"""
	Зарегистрированные пользователи в боте
	"""

	uid = IntegerField(unique=True)
	username = TextField(null=True)
	name = TextField()
	age = IntegerField()
	gender = BooleanField()  # 0 - Мужчина, 1 - Женщина
	about = TextField()
	city = TextField(null=True)
	photo_path = TextField()


class comments(BaseModel):
	"""
	Комментарии к пользователям
	"""

	uid = IntegerField()
	myuid = IntegerField()
	rating = IntegerField()
	text = TextField()


class geoposition(BaseModel):
	"""
	Геопозиция пользователей
	"""

	uid = IntegerField(unique=True)
	lat = TextField()
	lon = TextField()
