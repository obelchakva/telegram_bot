import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "7722825450:AAHKyoLykpV63lmZisNIargwPh5qQXqFlTg")
BASE_DATA_PATH = "bot_data"

TEACHERS = [
    1598734848,
    1006419056
]