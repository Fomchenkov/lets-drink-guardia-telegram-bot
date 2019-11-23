import os


BOT_TOKEN = os.getenv('BOT_TOKEN')
PROXY = {'https': os.getenv('PROXY_STRING')}
DEBUG = False
DB_NAME = os.getcwd() + '/database.db'
LOG_PATH = os.getcwd() + '/logging.log'

ADMINS = [217166737, 295720203]

report_channel_id = -1001162281937

main_markup = [
	['🍺 Хочу выпить! 🍺'],
	['👑 Моя анкета 👑'],
	['🥂 Тост! 🥂'],
	['📨 Поддержка 📨'],
]

admin_markup = [
	['Создать рассылку'],
	['Количество пользователей'],
]

support_url = 'https://t.me/fomchenkov_v'
photos_path = os.getcwd() + '/user_photos/'
