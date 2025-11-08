import telebot
import os
from test_parser import TestParser

if not os.path.exists('test_data'):
    os.makedirs('test_data')

bot = telebot.TeleBot('7722825450:AAHKyoLykpV63lmZisNIargwPh5qQXqFlTg')

test_parser = TestParser()

test_parser.load_all_tests()

bot.set_my_commands([
    telebot.types.BotCommand("/start", "Начало работы"),
    telebot.types.BotCommand("/help", "Помощь с задачей"),
    telebot.types.BotCommand("/info", "Информация о боте")
])

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
*Добро пожаловать в бот помощи с задачами!*

*Доступные команды:*

/start - Начало работы
/help - Получить помощь с задачей
/info - Информация о боте

*Как это работает:*
1. Используйте /help чтобы начать
2. Введите номер задачи
3. Введите номер теста
4. Получите помощь!

Для начала работы напишите /help
    """
    bot.send_message(message.from_user.id, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['info'])
def send_info(message):
    info_text = """
*Информация о боте*

*Назначение:* Помощь с учебными задачами и тестами
*Разработчик:* Обельчак Вячеслав Андреевич
*Версия:* 1.0

*Функциональность:*
• Регистрация запросов на помощь
• Обработка номеров задач и тестов

Для получения помощи используйте команду /help
    """
    bot.send_message(message.from_user.id, info_text, parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def start_help(message):
    bot.send_message(message.from_user.id, "*С какой задачей вам нужна помощь? Введите номер задачи:*", parse_mode='Markdown')
    bot.register_next_step_handler(message, get_task_number)

def get_task_number(message):
    if message.text.startswith('/'):
        bot.send_message(message.from_user.id, "Пожалуйста, введите номер задачи, а не команду:")
        bot.register_next_step_handler(message, get_task_number)
        return
        
    global task_number
    task_number = message.text.strip()
    available_tasks = ['619', '3580']

    if task_number not in available_tasks:
        bot.send_message(message.from_user.id,
                         f"Задача {task_number} не найдена.\n"
                         f"Доступные задачи: {', '.join(available_tasks)}")
        return
    

    bot.send_message(message.from_user.id, "Принято! Теперь *введите номер теста:*", parse_mode='Markdown')
    bot.register_next_step_handler(message, get_test_number)

def get_test_number(message):
    if message.text.startswith('/'):
        bot.send_message(message.from_user.id, "Пожалуйста, введите номер теста, а не команду:")
        bot.register_next_step_handler(message, get_test_number)
        return
        
    global test_number
    test_number = message.text.strip()
    
    try:
        task_num = int(task_number)
        test_num = int(test_number)
        
        confirm_text = f"""
*Запрос зарегистрирован!*

*Задача:* {task_number}
*Тест:* {test_number}

Ваш запрос принят в обработку. 
        """
        bot.send_message(message.from_user.id, confirm_text, parse_mode='Markdown')
        
    except ValueError:
        error_text = """
*Ошибка ввода!*

Нужно ввести числа для номера задачи и теста.
Давайте начнем заново.

Используйте /help для нового запроса
        """
        bot.send_message(message.from_user.id, error_text, parse_mode='Markdown')

    try:
        test_data = test_parser.get_test_data(task_number, test_number)

        if test_data:
            response = f"""
*Тест найден!*
            
Задача: {task_number}
Тест: {test_number}

*Входные данные:*

{test_data['input']}

*Ожидаемый вывод*

{test_data['output']}

Используйте /help для нового запроса
        """

        else:
            response = f"""
*Тест не найден!*

Задача: {task_number}
Тест: {test_num}

Проверьте:
• Правильность номера задачи
• Правильность номера теста
• Доступность задачи в базе
        """

        bot.send_message(message.from_user.id, response, parse_mode='Markdown')
        
    except Exception as e:
        bot.send_message(message.from_user.id, f"Ошибка: {str(e)}")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text.lower() == "привет" or "Привет":
        bot.send_message(message.from_user.id, "Привет! Используйте /start для просмотра команд")
    else:
        help_text = """
Не понимаю ваше сообщение.

*Доступные команды:*
/start - Начало работы и список команд
/help - Получить помощь с задачей
/info - Информация о боте

Выберите нужную команду из меню или введите её вручную.
        """
        bot.send_message(message.from_user.id, help_text, parse_mode='Markdown')

task_number = ''
test_number = ''

bot.polling(none_stop=True, interval=0)