import os


BOT_TOKEN = os.getenv('BOT_TOKEN')
PROXY = {'https': os.getenv('PROXY_STRING')}
DEBUG = False
DB_NAME = 'database.db'

ADMINS = [217166737, 295720203]

main_markup = [
	['🍺 Хочу выпить! 🍺'],
	['👑 Моя анкета 👑'],
	['📨 Поддержка 📨'],
]

admin_markup = [
	['Создать рассылку'],
	['Количество пользователей'],
]

support_url = 'https://t.me/fomchenkov_v'
