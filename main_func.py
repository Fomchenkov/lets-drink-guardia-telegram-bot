import os
import time

from telebot import apihelper

import database
import config


def main(bot):
	database.create_tables()

	# Создать папку для хранения фоток пользователей

	try:
		os.mkdir(config.photos_path)
	except Exception as e:
		print(e)

	if config.DEBUG:
		apihelper.proxy = config.PROXY
		bot.polling()
	else:
		while True:
			try:
				bot.polling(none_stop=True, interval=0)
			except Exception as e:
				print(e)
				time.sleep(30)
				continue
