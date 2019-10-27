import os


BOT_TOKEN = os.getenv('BOT_TOKEN')
PROXY = {'https': os.getenv('PROXY_STRING')}
DEBUG = False
DB_NAME = 'database.db'

main_markup = [
    ['Хочу бухать!'],
    ['Моя анкета'],
]
