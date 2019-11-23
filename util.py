import random

import requests
from bs4 import BeautifulSoup

import texts


def generate_user_text(db_user_object):
	"""
	Сгенерировать текст анкеты пользователя
	"""

	gender_text = ''
	if db_user_object.gender == 0 or db_user_object.gender == False:
		gender_text = 'Мужчина'
	elif db_user_object == 1 or db_user_object.gender == True:
		gender_text = 'Женщина'

	return 'Имя: {!s}\n\nВозраст: {!s}\n\nПол: {!s}\n\nОбо мне: {!s}'.format(
		db_user_object.name, db_user_object.age, gender_text, db_user_object.about
	)


def get_tost_text():
	"""
	Получить текст рандомного тоста
	"""

	for error in range(5): 
		try: 
			types = ['prikolnye', 'krasivye', 'korotkie'] 
			url = 'http://pozdravok.ru/toast/{!s}/{!s}.htm'.format(random.choice(types), random.randint(1, 13))
			site = requests.get(url)
			pars = BeautifulSoup(site.text.replace('<br />', '\n'), 'html.parser')
			tosts = pars.findAll('p', class_='sfst')
			return random.choice(tosts)
		except Exception as e:
			print(e)

	return texts.error_tost

def get_stars_assessment(ass):
	"""
	Рейтинг в графическом виде
	"""
	rating = '\U00002606\U00002606\U00002606\U00002606\U00002606'
	for x in range(ass):
		rating = '\U00002605' + rating
		rating = rating[:-1]
	return rating

def get_average_rating(comment):
	"""
	Вычисление рейтинга
	"""
	average = 0
	for x in comment:	
		average += x.rating
	return average/len(comment)

