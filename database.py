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


class BaseModel(Model):
	class Meta:
		database = db


class User(BaseModel):
	uid = IntegerField(unique=True)
	username = IntegerField(default = 0)
	name = TextField()
	age = IntegerField()
	# 0 - Мужчина, 1 - Женщина
	gender = BooleanField()
	about = TextField()
	photo_path = TextField()

class comments(BaseModel):
	uid = IntegerField()
	myuid = IntegerField()
	rating = IntegerField()
	text = TextField()

