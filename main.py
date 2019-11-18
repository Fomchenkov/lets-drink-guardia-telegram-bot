#!/usr/bin/env python3

import os
import random
import logging

import telebot
from telebot import apihelper, types

import util
import main_func
import database
import config
import texts


logging.basicConfig(filename='logging.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(config.BOT_TOKEN)

READY_TO_REGISTER = {}

READY_TO_EMAIL = {}

READY_TO_EDIT_NAME = {}
READY_TO_EDIT_AGE = {}
READY_TO_EDIT_ABOUT = {}
READY_TO_EDIT_PHOTO = {}


def clean_all_ready(uid):
	"""
	Очистить все READY TO
	"""

	if uid in READY_TO_REGISTER:
		del READY_TO_REGISTER[uid]
	if uid in READY_TO_EMAIL:
		del READY_TO_EMAIL[uid]
	if uid in READY_TO_EDIT_NAME:
		del READY_TO_EDIT_NAME[uid]
	if uid in READY_TO_EDIT_AGE:
		del READY_TO_EDIT_AGE[uid]
	if uid in READY_TO_EDIT_ABOUT:
		del READY_TO_EDIT_ABOUT[uid]
	if uid in READY_TO_EDIT_PHOTO:
		del READY_TO_EDIT_PHOTO[uid]


@bot.message_handler(commands=['start'])
def start_command_handler(message):
	cid = message.chat.id
	uid = message.from_user.id

	logger.info('Бот запущен {!s} [{!s}]'.format(message.from_user.first_name, uid))

	clean_all_ready(uid)

	query = database.User.select().where(database.User.uid == uid)

	# Проверка на регистрацию пользователя
	if not query.exists():
		READY_TO_REGISTER[uid] = {}
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
		markup.row(message.from_user.first_name)
		return bot.send_message(cid, texts.register_ask_name, reply_markup=markup)

	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=1)
	for x in config.main_markup:
		markup.row(*x)
	return bot.send_message(cid, texts.allready_register, reply_markup=markup)	


@bot.message_handler(commands=['admin'])
def admin_command_handler(message):
	cid = message.chat.id
	uid = message.from_user.id

	# Проверка прав доступа
	if uid not in config.ADMINS:
		logger.info('Несанкционированный доступ к админ-панели {!s} [{!s}]'.format(message.from_user.first_name, uid))
		return bot.send_message(cid, texts.admin_access_denied)

	clean_all_ready(uid)	

	text = 'Админ-панель'
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=1)
	for x in config.admin_markup:
		markup.row(*x)
	return bot.send_message(cid, text, reply_markup=markup)	


'''
@bot.message_handler(content_types=['location'])
def location_content_handler(message):
	cid = message.chat.id
	uid = message.from_user.id

	# Обработка отправки местоположения при регистрации
	if uid in READY_TO_REGISTER:
		if 'about' in READY_TO_REGISTER[uid] and 'location' not in READY_TO_REGISTER[uid]:
			READY_TO_REGISTER[uid]['location'] = {
				'lat': message.location.latitude,
				'long': message.location.longitude,
			}
			logger.info('Successfuly register from {!s}'.format(message.from_user.first_name))

			# Добавление пользователя в базу данных.
			user = database.User(
				uid=uid, name=READY_TO_REGISTER[uid]['name'], age=READY_TO_REGISTER[uid]['age'], 
				gender=READY_TO_REGISTER[uid]['gender'], about=READY_TO_REGISTER[uid]['about'],
				location_lat=READY_TO_REGISTER[uid]['location']['lat'],
				location_long=READY_TO_REGISTER[uid]['location']['long']
			)
			user.save()

			logger.info('Успешная регистрация {!s} [{!s}]'.format(message.from_user.first_name, uid))

			print(READY_TO_REGISTER[uid])

			del READY_TO_REGISTER[uid]
			markup = types.ReplyKeyboardRemove()
			bot.send_message(cid, texts.success_register, reply_markup=markup)

			text = 'Ваша анкета:\n\n{!s}'.format(util.generate_user_text(user))
			markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=1)
			for x in config.main_markup:
				markup.row(*x)
			return bot.send_message(cid, text, reply_markup=markup)
'''


@bot.message_handler(content_types=['photo'])
def photo_content_handler(message):
	cid = message.chat.id
	uid = message.from_user.id

	# Обработка рассылки сообщений админом
	if uid in READY_TO_EMAIL:
		del READY_TO_EMAIL[uid]
		file_info = bot.get_file(message.photo[-1].file_id)
		photo_path = 'photo.jpg'
		downloaded_file = bot.download_file(file_info.file_path)
		with open(photo_path, 'wb') as new_file:
			new_file.write(downloaded_file)

		followers = database.User.select()

		for x in followers:
			try:
				bot.send_photo(x.uid, open(photo_path, 'rb'), caption=message.caption)
			except Exception as e:
				print(e)
				continue

		logger.info('Рассылка фото {!s} [{!s}]'.format(message.from_user.first_name, uid))

		os.remove(photo_path)
		bot.send_message(cid, texts.success_email_text)

		text = 'Админ-панель'
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=1)
		for x in config.admin_markup:
			markup.row(*x)
		return bot.send_message(cid, text, reply_markup=markup)

	# Отправка фото при регистрации
	if uid in READY_TO_REGISTER:
		if 'photo' not in READY_TO_REGISTER[uid]:

			# Сохранить фото
			file_info = bot.get_file(message.photo[-1].file_id)
			photo_path = '{!s}photo{!s}.jpg'.format(config.photos_path, uid)
			downloaded_file = bot.download_file(file_info.file_path)
			with open(photo_path, 'wb') as new_file:
				new_file.write(downloaded_file)

			READY_TO_REGISTER[uid]['photo'] = photo_path

			logger.info('Успешная регистрация {!s}'.format(message.from_user.first_name))

			# Добавление пользователя в базу данных.
			user = database.User(
				uid=uid, name=READY_TO_REGISTER[uid]['name'], age=READY_TO_REGISTER[uid]['age'], 
				gender=READY_TO_REGISTER[uid]['gender'], about=READY_TO_REGISTER[uid]['about'],
				photo_path=READY_TO_REGISTER[uid]['photo']
			)
			user.save()

			logger.info('Успешная регистрация {!s} [{!s}]'.format(message.from_user.first_name, uid))

			print(READY_TO_REGISTER[uid])

			del READY_TO_REGISTER[uid]
			markup = types.ReplyKeyboardRemove()
			bot.send_message(cid, texts.success_register, reply_markup=markup)

			text = 'Ваша анкета:\n\n{!s}'.format(util.generate_user_text(user))
			markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=1)
			for x in config.main_markup:
				markup.row(*x)
			return bot.send_photo(cid, open(user.photo_path, 'rb'), caption=text, reply_markup=markup)

	# Обработка изменений данных анкеты
	if uid in READY_TO_EDIT_PHOTO:
		if 'photo' not in READY_TO_EDIT_PHOTO[uid]:

			# Сохранить фото
			file_info = bot.get_file(message.photo[-1].file_id)
			photo_path = '{!s}photo{!s}.jpg'.format(config.photos_path, uid)
			downloaded_file = bot.download_file(file_info.file_path)
			with open(photo_path, 'wb') as new_file:
				new_file.write(downloaded_file)

			READY_TO_EDIT_PHOTO[uid]['photo'] = photo_path

			q = database.User.update({database.User.photo_path: READY_TO_EDIT_PHOTO[uid]['photo']}).where(database.User.uid == uid)
			q.execute()

			del READY_TO_EDIT_PHOTO[uid]

			logger.info('Редактирование фото {!s} [{!s}]'.format(message.from_user.first_name, uid))

			text = 'Вы успешно изменили фото'
			markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=1)
			for x in config.main_markup:
				markup.row(*x)
			return bot.send_message(cid, text, reply_markup=markup)


@bot.message_handler(content_types=['text'])
def text_content_handler(message):
	cid = message.chat.id
	uid = message.from_user.id


	# Обработка регистрации
	if uid in READY_TO_REGISTER:

		if 'name' not in READY_TO_REGISTER[uid]:
			READY_TO_REGISTER[uid]['name'] = message.text
			markup = types.ReplyKeyboardRemove()
			return bot.send_message(cid, texts.register_ask_age, reply_markup=markup)

		if 'age' not in READY_TO_REGISTER[uid]:
			try:
				int(message.text)
			except Exception as e:
				return bot.send_message(cid, texts.error_integer)

			# Проверка на совершеннолетие
			if int(message.text) < 18:
				return bot.send_message(cid, texts.error_smaller_18_years)

			READY_TO_REGISTER[uid]['age'] = int(message.text)
			keyboard = types.InlineKeyboardMarkup()
			keyboard.add(types.InlineKeyboardButton(text='🤵 Мужчина', callback_data='registergender_0'))
			keyboard.add(types.InlineKeyboardButton(text='👄 Женщина', callback_data='registergender_1'))
			return bot.send_message(cid, texts.register_ask_gender, reply_markup=keyboard)

		if 'gender' not in READY_TO_REGISTER[uid]:
			return bot.send_message(cid, texts.register_select_inline_gender)

		if 'about' not in READY_TO_REGISTER[uid]:
			READY_TO_REGISTER[uid]['about'] = message.text
			return bot.send_message(cid, texts.register_ask_photo)

		if 'photo' not in READY_TO_REGISTER[uid]:
			return bot.send_message(cid, texts.register_invite_photo)

	# Обработать отмену действий админа
	if uid in config.ADMINS:
		if message.text == '❌ Отмена':
			if uid in READY_TO_EMAIL:
				del READY_TO_EMAIL[uid]
			text = 'Действие отменено'
			bot.send_message(cid, text)
			text = 'Админ-панель'
			markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=1)
			for x in config.admin_markup:
				markup.row(*x)
			return bot.send_message(cid, text, reply_markup=markup)

	# Обработать рассылку сообщений
	if uid in READY_TO_EMAIL:
		del READY_TO_EMAIL[uid]
		
		followers = database.User.select()

		for x in followers:
			try:
				bot.send_message(x.uid, message.text)
			except Exception as e:
				print(e)
				continue

		logger.info('Рассылка текста {!s} [{!s}] {!s}'.format(message.from_user.first_name, uid, message.text))

		bot.send_message(cid, texts.success_email_text)
		text = 'Админ-панель'
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=1)
		for x in config.admin_markup:
			markup.row(*x)
		return bot.send_message(cid, text, reply_markup=markup)

	query = database.User.select().where(database.User.uid == uid)

	# Проверка на регистрацию пользователя
	if not query.exists():
		logger.info('Отправка текстового сообщения без регистрации в боте {!s} [{!s}]'.format(message.from_user.first_name, uid))
		bot.send_message(cid, random.choice(texts.sheet_frases), reply_markup=types.ReplyKeyboardRemove())
		bot_start_url = 'https://t.me/{!s}?start={!s}'.format(bot.get_me().username, uid)
		keyboard = types.InlineKeyboardMarkup()
		keyboard.add(types.InlineKeyboardButton('🍾 Регистрация! 🍾', url=bot_start_url))
		return bot.send_message(cid, texts.lets_register, reply_markup=keyboard)

	user = query.get()

	# Обработка отмены пользователей
	if message.text == '❌ Отменить':

		if uid in READY_TO_EDIT_NAME:
			del READY_TO_EDIT_NAME[uid]
		if uid in READY_TO_EDIT_AGE:
			del READY_TO_EDIT_AGE[uid]
		if uid in READY_TO_EDIT_ABOUT:
			del READY_TO_EDIT_ABOUT[uid]
		if uid in READY_TO_EDIT_PHOTO:
			del READY_TO_EDIT_PHOTO[uid]

		text = 'Действие отменено'
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=1)
		for x in config.main_markup:
			markup.row(*x)
		return bot.send_message(cid, text, reply_markup=markup)


	# Обработка изменений данных анкеты
	if uid in READY_TO_EDIT_NAME:
		if 'name' not in READY_TO_EDIT_NAME[uid]:
			READY_TO_EDIT_NAME[uid]['name'] = message.text

			q = database.User.update({database.User.name: READY_TO_EDIT_NAME[uid]['name']}).where(database.User.uid == uid)
			q.execute()

			del READY_TO_EDIT_NAME[uid]

			logger.info('Редактирование имени {!s} [{!s}]'.format(message.from_user.first_name, uid))

			text = 'Вы успешно изменили имя'
			markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=1)
			for x in config.main_markup:
				markup.row(*x)
			return bot.send_message(cid, text, reply_markup=markup)


	# Обработка изменений данных анкеты
	if uid in READY_TO_EDIT_AGE:
		if 'age' not in READY_TO_EDIT_AGE[uid]:
			
			try:
				int(message.text)
			except Exception as e:
				text = 'Введите число!'
				return bot.send_message(cid, text)

			READY_TO_EDIT_AGE[uid]['age'] = int(message.text)

			q = database.User.update({database.User.age: READY_TO_EDIT_AGE[uid]['age']}).where(database.User.uid == uid)
			q.execute()

			del READY_TO_EDIT_AGE[uid]

			logger.info('Редактирование возраста {!s} [{!s}]'.format(message.from_user.first_name, uid))

			text = 'Вы успешно изменили возраст'
			markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=1)
			for x in config.main_markup:
				markup.row(*x)
			return bot.send_message(cid, text, reply_markup=markup)


	# Обработка изменений данных анкеты
	if uid in READY_TO_EDIT_ABOUT:
		if 'about' not in READY_TO_EDIT_ABOUT[uid]:
			READY_TO_EDIT_ABOUT[uid]['about'] = message.text

			q = database.User.update({database.User.about: READY_TO_EDIT_ABOUT[uid]['about']}).where(database.User.uid == uid)
			q.execute()

			del READY_TO_EDIT_ABOUT[uid]

			logger.info('Редактирование о себе {!s} [{!s}]'.format(message.from_user.first_name, uid))

			text = 'Вы успешно изменили описание'
			markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=1)
			for x in config.main_markup:
				markup.row(*x)
			return bot.send_message(cid, text, reply_markup=markup)

	# Обработка изменений данных анкеты
	if uid in READY_TO_EDIT_PHOTO:
		if 'photo' not in READY_TO_EDIT_PHOTO[uid]:
			return bot.send_message(cid, texts.register_invite_photo)

	# Обработка кнопок главного меню
	if message.text == '🍺 Хочу выпить! 🍺':
		logger.info('Хочет пить {!s} [{!s}]'.format(message.from_user.first_name, uid))

		users = database.User.select().where(database.User.uid != uid)
		if len(users) == 0:
			return bot.send_message(cid, texts.no_active_user)
		bot.send_message(cid, texts.lets_drink_text, parse_mode='HTML')
		
		text = util.generate_user_text(users[0])
		keyboard = types.InlineKeyboardMarkup()
		keyboard.add(types.InlineKeyboardButton('🥃 Пригласить выпить! 🥃', callback_data='invitedrink_{!s}'.format(users[0].id)))
		keyboard.add(types.InlineKeyboardButton('🔴 Пожаловаться 🔴', callback_data='report_{!s}'.format(users[0].id)))
		keyboard.add(
			types.InlineKeyboardButton('⬅️', callback_data='seeleftuser_{!s}'.format(users[0].id)),
			types.InlineKeyboardButton('➡️', callback_data='seerightuser_{!s}'.format(users[0].id)),
		)
		return bot.send_photo(cid, open(users[0].photo_path, 'rb'), caption=text, reply_markup=keyboard)
	elif message.text == '👑 Моя анкета 👑':
		logger.info('Просмотр своей анкеты {!s} [{!s}]'.format(message.from_user.first_name, uid))
		text = 'Ваша анкета:\n\n{!s}'.format(util.generate_user_text(user))
		keyboard = types.InlineKeyboardMarkup()
		keyboard.add(types.InlineKeyboardButton('✏️ Изменить имя ✏️', callback_data='editname'))
		keyboard.add(types.InlineKeyboardButton('✏️ Изменить возраст ✏️', callback_data='editage'))
		keyboard.add(types.InlineKeyboardButton('✏️ Изменить описание ✏️', callback_data='editabout'))
		keyboard.add(types.InlineKeyboardButton('✏️ Изменить фото ✏️', callback_data='editphoto'))
		return bot.send_photo(cid, open(user.photo_path, 'rb'), caption=text, reply_markup=keyboard)
	elif message.text == '📨 Поддержка 📨':
		logger.info('Просмотр поддержки {!s} [{!s}]'.format(message.from_user.first_name, uid))
		keyboard = types.InlineKeyboardMarkup()
		keyboard.add(types.InlineKeyboardButton('Написать в поддержку', url=config.support_url))
		return bot.send_message(cid, texts.support_text, reply_markup=keyboard)
	elif message.text == '🥂 Тост! 🥂':
		logger.info('Выдан тост {!s} [{!s}]'.format(message.from_user.first_name, uid))
		text = util.get_tost_text()
		return bot.send_message(cid, text)


	# Обработать клавиатуру админа
	if uid in config.ADMINS:
		if message.text == 'Создать рассылку':
			READY_TO_EMAIL[uid] = {}
			text = 'Введите сообщение для рассылки подписчикам бота'
			markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=1)
			markup.row('❌ Отмена')
			return bot.send_message(cid, text, reply_markup=markup)
		elif message.text == 'Количество пользователей':
			logger.info('Просмотрена статистика {!s} [{!s}]'.format(message.from_user.first_name, uid))
			all_users = database.User.select()
			text = 'Количество пользователей в боте: {!s}'.format(len(all_users))
			return bot.send_message(cid, text)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
	cid = call.message.chat.id
	uid = call.from_user.id

	print(call.data)

	try:
		bot.answer_callback_query(call.id, '✅')
	except Exception as e:
		print(e)

	# Обработка выбора пола при регистрации
	if call.data.startswith('registergender'):
		if uid not in READY_TO_REGISTER:
			bot.send_message(cid, random.choice(texts.sheet_frases), reply_markup=types.ReplyKeyboardRemove())
			bot_start_url = 'https://t.me/{!s}?start={!s}'.format(bot.get_me().username, uid)
			keyboard = types.InlineKeyboardMarkup()
			keyboard.add(types.InlineKeyboardButton('🍾 Регистрация! 🍾', url=bot_start_url))
			return bot.edit_message_text(texts.lets_register, chat_id=cid, message_id=call.message.message_id, reply_markup=keyboard)
		gender = int(call.data.split('_')[1])
		READY_TO_REGISTER[uid]['gender'] = gender
		bot.edit_message_text('✅ Выбрано!', chat_id=cid, message_id=call.message.message_id, reply_markup=None)
		return bot.send_message(cid, texts.register_ask_about)
	elif call.data.startswith('seeanket'):
		user_id = int(call.data.split('_')[1])

		logger.info('Посмотрел анкету {!s} [{!s}]'.format(call.from_user.first_name, uid))

		user = database.User.select().where(database.User.id == user_id)[0]

		text = util.generate_user_text(user)
		return bot.send_photo(cid, open(user.photo_path, 'rb'), caption=text)

	elif call.data.startswith('invitedrink'):
		user_id = int(call.data.split('_')[1])

		logger.info('Пригласил пить {!s} [{!s}]'.format(call.from_user.first_name, uid))

		user = database.User.select().where(database.User.id == user_id)[0]
		my_user = database.User.select().where(database.User.uid == uid)[0]

		try:
			keyboard = types.InlineKeyboardMarkup()
			keyboard.add(types.InlineKeyboardButton('👀 Посмотреть анкету 👀', callback_data='seeanket_{!s}'.format(my_user.id)))
			keyboard.add(
				types.InlineKeyboardButton('✅ Согласиться ✅', callback_data='confirmdrink_{!s}'.format(my_user.id)),
				types.InlineKeyboardButton('❌ Отказаться ❌', callback_data='notconfirmdrink_{!s}'.format(my_user.id))
			)
			bot.send_message(user.uid, texts.drink_invite, reply_markup=keyboard)
		except Exception as e:
			print(e)

		return bot.send_message(cid, texts.success_inviting.format(user.name))
	elif call.data.startswith('confirmdrink'):
		user_id = int(call.data.split('_')[1])

		logger.info('Подтвердил пить {!s} [{!s}]'.format(call.from_user.first_name, uid))

		my_user = database.User.select().where(database.User.uid == uid)[0]
		other_user = database.User.select().where(database.User.id == user_id)[0]

		try:
			text = 'Пользователь {!s} согласен выпить с вами!'.format(my_user.name)

			if call.from_user.username:
				text += '\n\nСсылка: @{!s}'.format(call.from_user.username)

			keyboard = types.InlineKeyboardMarkup()
			keyboard.add(types.InlineKeyboardButton('Ссылка на ЛС', url='tg://user?id={!s}'.format(my_user.uid)))
			bot.send_message(other_user.uid, text, parse_mode='HTML', reply_markup=keyboard)
		except Exception as e:
			print(e)

		text = 'Пользователь {!s} принял ваше приглашение!'.format(other_user.name)
		bot.delete_message(chat_id=cid, message_id=call.message.message_id)
		keyboard = types.InlineKeyboardMarkup()
		keyboard.add(types.InlineKeyboardButton('Ссылка на ЛС', url='tg://user?id={!s}'.format(other_user.uid)))
		return bot.send_message(cid, text, reply_markup=keyboard)
	elif call.data.startswith('notconfirmdrink'):
		user_id = int(call.data.split('_')[1])

		logger.info('Отказался пить {!s} [{!s}]'.format(call.from_user.first_name, uid))

		my_user = database.User.select().where(database.User.uid == uid)[0]
		other_user = database.User.select().where(database.User.id == user_id)[0]

		try:
			text = 'Пользователь {!s} отказал вам в пьянке'.format(my_user.name)
			bot.send_message(other_user.uid, text)
		except Exception as e:
			print(e)

		bot.delete_message(chat_id=cid, message_id=call.message.message_id)
		return bot.send_message(cid, 'Отказано')
	elif call.data.startswith('seeleftuser'):
		user_id = int(call.data.split('_')[1])

		logger.info('Посмотрел анкету {!s} [{!s}]'.format(call.from_user.first_name, uid))

		all_users = database.User.select().where(database.User.uid != uid)

		print(all_users)

		# Найти следующего пользователя
		for i, x in enumerate(all_users):
			if x.id == user_id:
				try:
					prev_user = all_users[i-1]
				except Exception as e:
					# При ошибке выбрать последнего пользователя
					prev_user = all_users[-1]

		text = util.generate_user_text(prev_user)

		# Проверка на ошибку редактирования сообщения
		if call.message.caption == text:
			text = 'Больше нет пользователей'
			return bot.send_message(cid, text)

		keyboard = types.InlineKeyboardMarkup()
		keyboard.add(types.InlineKeyboardButton('🥃 Пригласить выпить! 🥃', callback_data='invitedrink_{!s}'.format(prev_user.id)))
		keyboard.add(types.InlineKeyboardButton('🔴 Пожаловаться 🔴', callback_data='report_{!s}'.format(prev_user.id)))
		keyboard.add(
			types.InlineKeyboardButton('⬅️', callback_data='seeleftuser_{!s}'.format(prev_user.id)),
			types.InlineKeyboardButton('➡️', callback_data='seerightuser_{!s}'.format(prev_user.id)),
		)
		return bot.edit_message_media(media=types.InputMediaPhoto(open(prev_user.photo_path, 'rb'), caption=text), chat_id=cid, message_id=call.message.message_id , reply_markup=keyboard)

	elif call.data.startswith('seerightuser'):
		user_id = int(call.data.split('_')[1])

		logger.info('Посмотрел анкету {!s} [{!s}]'.format(call.from_user.first_name, uid))

		all_users = database.User.select().where(database.User.uid != uid)

		print(all_users)

		# Найти следующего пользователя
		for i, x in enumerate(all_users):
			if x.id == user_id:
				try:
					next_user = all_users[i+1]
				except Exception as e:
					# При ошибке выбрать первого пользователя
					next_user = all_users[0]

		text = util.generate_user_text(next_user)

		# Проверка на ошибку редактирования сообщения
		if call.message.caption == text:
			text = 'Больше нет пользователей'
			return bot.send_message(cid, text)

		keyboard = types.InlineKeyboardMarkup()
		keyboard.add(types.InlineKeyboardButton('🥃 Пригласить выпить! 🥃', callback_data='invitedrink_{!s}'.format(next_user.id)))
		keyboard.add(types.InlineKeyboardButton('🔴 Пожаловаться 🔴', callback_data='report_{!s}'.format(next_user.id)))
		keyboard.add(
			types.InlineKeyboardButton('⬅️', callback_data='seeleftuser_{!s}'.format(next_user.id)),
			types.InlineKeyboardButton('➡️', callback_data='seerightuser_{!s}'.format(next_user.id)),
		)
		return bot.edit_message_media(media=types.InputMediaPhoto(open(next_user.photo_path, 'rb'), caption=text), chat_id=cid, message_id=call.message.message_id , reply_markup=keyboard)
	# Жалобы на анкеты
	if call.data.startswith('report'):
		id = int(call.data.split('_')[1])
		user = database.User.select().where(database.User.uid != uid)
		text = '<b>{!s}</b> \n{!s}'.format(texts.channel_report, util.generate_user_text(].photo_path, 'rb'), caption = text, parse_mode = "HTML", reply_markup = keyboard)

	# Обработка редактирования анкеты
	if call.data == 'editname':
		READY_TO_EDIT_NAME[uid] = {}
		text = 'Введите новое имя'
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=1)
		markup.row('❌ Отменить')
		return bot.send_message(cid, text, reply_markup=markup)
	elif call.data == 'editage':
		READY_TO_EDIT_AGE[uid] = {}
		text = 'Введите ваш возраст'
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=1)
		markup.row('❌ Отменить')
		return bot.send_message(cid, text, reply_markup=markup)
	elif call.data == 'editabout':
		READY_TO_EDIT_ABOUT[uid] = {}
		text = 'Введите новое описание'
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=1)
		markup.row('❌ Отменить')
		return bot.send_message(cid, text, reply_markup=markup)
	elif call.data == 'editphoto':
		READY_TO_EDIT_PHOTO[uid] = {}
		text = 'Отправьте новое фото'
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=1)
		markup.row('❌ Отменить')
		return bot.send_message(cid, text, reply_markup=markup)


if __name__ == '__main__':
	logger.info('Запуск процесса бота')
	main_func.main(bot)
