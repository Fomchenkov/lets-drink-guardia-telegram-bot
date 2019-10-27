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

	
	# Обработка кнопрк главного меню
	if message.text == 'Хочу бухать!':
		# TODO
		return bot.send_message(cid, 'В разработке...')
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


if __name__ == '__main__':
	main_func.main(bot)
