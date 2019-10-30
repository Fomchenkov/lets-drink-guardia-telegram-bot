#!/usr/bin/env python3

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


@bot.message_handler(commands=['start'])
def start_command_handler(message):
	cid = message.chat.id
	uid = message.from_user.id

	logger.info('Bot started by {!s}'.format(message.from_user.first_name))

	try:
		# Проверка на регистрацию пользователя
		user = database.User.get(database.User.uid == uid)
		bot.send_message(cid, texts.allready_register)
		text = 'Ваша анкета:\n\n{!s}'.format(util.generate_user_text(user))
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=1)
		for x in config.main_markup:
			markup.row(*x)
		return bot.send_message(cid, text, reply_markup=markup)
	except Exception as e:
		# Начало регистрации
		READY_TO_REGISTER[uid] = {}
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
		markup.row(message.from_user.first_name)
		return bot.send_message(cid, texts.register_ask_name, reply_markup=markup)


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

			print(READY_TO_REGISTER[uid])

			del READY_TO_REGISTER[uid]
			markup = types.ReplyKeyboardRemove()
			bot.send_message(cid, texts.success_register, reply_markup=markup)

			text = 'Ваша анкета:\n\n{!s}'.format(util.generate_user_text(user))
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
			keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
			keyboard.add(types.KeyboardButton(text='📍 Отправить местоположение', request_location=True))
			return bot.send_message(cid, texts.register_ask_location, reply_markup=keyboard)

		if 'location' not in READY_TO_REGISTER[uid]:
			return bot.send_message(cid, texts.register_ask_location)


	try:
		# Проверка на регистрацию пользователя
		user = database.User.get(database.User.uid == uid)
	except Exception as e:
		# Предложение зарегистрироваться
		bot.send_message(cid, random.choice(texts.sheet_frases), reply_markup=types.ReplyKeyboardRemove())
		bot_start_url = 'https://t.me/{!s}?start={!s}'.format(bot.get_me().username, uid)
		keyboard = types.InlineKeyboardMarkup()
		keyboard.add(types.InlineKeyboardButton('🍾 Регистрация! 🍾', url=bot_start_url))
		return bot.send_message(cid, texts.lets_register, reply_markup=keyboard)

	
	# Обработка кнопок главного меню
	if message.text == 'Хочу бухать!':
		users = database.User.select().where(database.User.uid != uid)
		if len(users) == 0:
			return bot.send_message(cid, texts.no_active_user)
		bot.send_message(cid, texts.lets_drink_text, parse_mode='HTML')
		for x in users:
			text = util.generate_user_text(x)
			keyboard = types.InlineKeyboardMarkup()
			keyboard.add(types.InlineKeyboardButton('🥃 Пригласить бухать! 🥃', callback_data='invitedrink_{!s}'.format(x.id)))
			keyboard.add(
				types.InlineKeyboardButton('⬅️', callback_data='seeleftuser_{!s}'.format(x.id)),  # TODO
				types.InlineKeyboardButton('➡️', callback_data='seerightuser_{!s}'.format(x.id)),  # TODO
			)
			bot.send_message(cid, text, reply_markup=keyboard)
		return
	elif message.text == 'Моя анкета':
		text = 'Ваша анкета:\n\n{!s}'.format(util.generate_user_text(user))
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, row_width=1)
		for x in config.main_markup:
			markup.row(*x)
		return bot.send_message(cid, text, reply_markup=markup)


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

		user = database.User.select().where(database.User.id == user_id)[0]
	
		return bot.send_message(cid, util.generate_user_text(user))
	elif call.data.startswith('invitedrink'):
		user_id = int(call.data.split('_')[1])

		user = database.User.select().where(database.User.id == user_id)[0]
		my_user = database.User.select().where(database.User.uid == uid)[0]

		try:
			keyboard = types.InlineKeyboardMarkup()
			keyboard.add(types.InlineKeyboardButton('👀 Посмотреть анкету 👀', callback_data='seeanket_{!s}'.format(my_user.id)))
			keyboard.add(
				types.InlineKeyboardButton('✅ Согласиться ✅', callback_data='confirmdrink_{!s}'.format(my_user.id)),
				types.InlineKeyboardButton('❌ Послать нахуй ❌', callback_data='notconfirmdrink_{!s}'.format(my_user.id))
			)
			bot.send_message(user.uid, texts.drink_invite, reply_markup=keyboard)
		except Exception as e:
			print(e)

		return bot.send_message(cid, texts.success_inviting.format(user.name))
	elif call.data.startswith('confirmdrink'):
		user_id = int(call.data.split('_')[1])

		user = database.User.select().where(database.User.id == user_id)[0]
		my_user = database.User.select().where(database.User.uid == uid)[0]

		try:
			text = 'Пользователь {!s} согласен бухнуть с вами!'.format(my_user.name)
			keyboard = types.InlineKeyboardMarkup()
			keyboard.add(types.InlineKeyboardButton('Ссылка на ЛС', url='tg://user?id={!s}'.format(my_user.uid)))
			bot.send_message(user.uid, text, parse_mode='HTML', reply_markup=keyboard)
		except Exception as e:
			print(e)

		return bot.edit_message_text('Принято!', chat_id=cid, message_id=call.message.message_id, reply_markup=None)
	elif call.data.startswith('notconfirmdrink'):
		user_id = int(call.data.split('_')[1])

		user = database.User.select().where(database.User.id == user_id)[0]

		try:
			text = 'Пользователь {!s} отказал вам в пьянке'.format(user.name)
			bot.send_message(user.uid, text)
		except Exception as e:
			print(e)

		return bot.edit_message_text('Послан нахуй', chat_id=cid, message_id=call.message.message_id, reply_markup=None)


if __name__ == '__main__':
	main_func.main(bot)
