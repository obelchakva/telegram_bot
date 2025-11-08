import telebot
print("Библиотека telebot успешно установлена и работает!")

# Можно добавить простой тест бота
try:
    bot = telebot.TeleBot('7722825450:AAHKyoLykpV63lmZisNIargwPh5qQXqFlTg')
    print("Бот создан успешно!")
except Exception as e:
    print(f"Ошибка: {e}")