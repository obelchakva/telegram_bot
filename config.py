import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "ваш_токен_бота")
BASE_DATA_PATH = "bot_data"

TEACHERS = [
    1598734848
]