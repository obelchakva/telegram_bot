import telebot
import os
import json
from task_manager import TaskManager
from dotenv import load_dotenv

ADMIN_PASSWORD = "101003"
CANCEL_COMMAND = "/cancel"
CANCEL_BUTTON = "❌ Отмена"
load_dotenv()
bot = telebot.TeleBot(os.getenv('TOKEN'))
task_manager = TaskManager()

bot.set_my_commands([
    telebot.types.BotCommand("start", "Начало работы"),
    telebot.types.BotCommand("help", "Помощь с задачей"),
    telebot.types.BotCommand("admin", "Информация для преподавателей"),
    telebot.types.BotCommand("cancel", "Отменить дейтвие"),
])


user_states = {}
authenticated_users = set()


def create_main_keyboard():
    """Основная клавиатура для главного меню"""
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        telebot.types.KeyboardButton("🏠 Начало"),
        telebot.types.KeyboardButton("❓ Помощь с задачей")
    )
    keyboard.add(
        telebot.types.KeyboardButton("🔐 Авторизация"),
        telebot.types.KeyboardButton("👨‍🏫 Для преподавателей")
    )
    keyboard.add(
        telebot.types.KeyboardButton("❌ Отмена")
    )
    return keyboard

def create_admin_keyboard():
    """Клавиатура для преподавателей после авторизации"""
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        telebot.types.KeyboardButton("📤 Загрузить тесты"),
        telebot.types.KeyboardButton("🗑 Удалить задачу")
    )
    keyboard.add(
        telebot.types.KeyboardButton("💬 Добавить комментарий"),
        telebot.types.KeyboardButton("🗑 Удалить комментарии")
    )
    keyboard.add(
        telebot.types.KeyboardButton("🏠 Начало"),
        telebot.types.KeyboardButton("❌ Отмена")
    )
    return keyboard

def create_choice_keyboard():
    """Клавиатура для выбора Да/Нет"""
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        telebot.types.KeyboardButton("✅ Да"),
        telebot.types.KeyboardButton("❌ Нет"),
        telebot.types.KeyboardButton("❌ Отмена")
    )
    return keyboard

def create_upload_format_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        telebot.types.KeyboardButton("📄 JSON файл"),
        telebot.types.KeyboardButton("📝 Текстовый ввод")
    )
    keyboard.add(
        telebot.types.KeyboardButton("❌ Отмена")
    )
    return keyboard

def create_delete_comment_keyboard():
    """Клавиатура для выбора формата загрузки"""
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        telebot.types.KeyboardButton("🗑 Удалить все комментарии"),
    )
    keyboard.add(
        telebot.types.KeyboardButton("❌ Отмена")
    )
    return keyboard

def create_cancel_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        telebot.types.KeyboardButton("❌ Отмена")
    )
    return keyboard



def admin_required(func):
    def wrapper(message):
        if message.chat.id in authenticated_users:
            if message.chat.id not in user_states:
                user_states[message.chat.id] = {}
            user_states[message.chat.id]['auth'] = True
            return func(message)
        else:
            bot.send_message(message.chat.id, "*Введите пароль для доступа к командам преподавателя:*", parse_mode='Markdown', reply_markup=create_cancel_keyboard())
            bot.register_next_step_handler(message, check_admin_password)
    return wrapper



@bot.message_handler(commands=['start'])
def handle_start_command(message):
    send_welcome(message)
@bot.message_handler(func=lambda message: message.text in ["🏠 Начало"])
def handle_start_button(message):
    send_welcome(message)
def send_welcome(message):
    """Приветственное сообщение"""
    welcome_text = """
*Бот помощи с задачами Informatics*

*Доступные команды:*
/help - Получить помощь с задачей
/admin - Информация для преподавателей
/cancel - Отменить действие

*Как это работает:*
1. Используйте /help чтобы начать
2. Выберите задачу
3. Введите номер теста
4. Получите помощь!

*Используйте кнопки ниже для быстрого доступа к основным функциям*
"""
    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown', reply_markup=create_main_keyboard())

def check_cancel(message):
    """Проверка на cancel"""
    if message.text.strip().lower() == CANCEL_COMMAND.strip().lower() or message.text.strip().lower() == CANCEL_BUTTON.strip().lower():
        user_states.pop(message.chat.id, None)
        bot.send_message(message.chat.id, "Действие отменено!", reply_markup=create_main_keyboard())
        return True
    return False



@bot.message_handler(commands=['login'])
def handle_login_command(message):
    show_admin_commands_login(message)
@bot.message_handler(func=lambda message: message.text in ["🔐 Авторизация"])
def handle_login_button(message):
    show_admin_commands_login(message)
def show_admin_commands_login(message):
    """Вывод информации для преподавателей"""
    if check_cancel(message):
        return
        
    bot.send_message(message.chat.id, "*Введите пароль для доступа к командам преподавателя:*", parse_mode='Markdown', reply_markup=create_cancel_keyboard())
    bot.register_next_step_handler(message, check_admin_password)

def check_admin_password(message):
    """Проверка пароля"""
    if check_cancel(message):
        return
        
    if message.text == ADMIN_PASSWORD:
        authenticated_users.add(message.chat.id)
        if message.chat.id not in user_states:
            user_states[message.chat.id] = {}
        user_states[message.chat.id]['auth'] = True
        
        admin_commands_text = f"""
Авторизация прошла успешно!
"""
        bot.send_message(message.chat.id, admin_commands_text, parse_mode='Markdown', reply_markup=create_admin_keyboard())
    else:
        bot.send_message(message.chat.id, "Неверный пароль!", reply_markup=create_main_keyboard())



@bot.message_handler(commands=['admin'])
def handle_admin_command(message):
    show_admin_commands(message)
@bot.message_handler(func=lambda message: message.text in ["👨‍🏫 Для преподавателей"])
def handle_admin_button(message):
    show_admin_commands(message)
@admin_required
def show_admin_commands(message):
    if check_cancel(message):
        return
        
    admin_commands_text = f"""
*Команды для преподавателей:*

/upload - Загрузить новые тесты
/delete - Удалить задачу
/comment - Добавить комментарий к тесту
/deletecomment - Удалить комментарий
/cancel - Отменить действие
"""
    bot.send_message(message.chat.id, admin_commands_text, parse_mode='Markdown', reply_markup=create_admin_keyboard())



@bot.message_handler(commands=['upload'])
def handle_upload_command(message):
    start_upload(message)
@bot.message_handler(func=lambda message: message.text in ["📤 Загрузить тесты"])
def handle_upload_button(message):
    start_upload(message)
@admin_required
def start_upload(message):
    """Загрузка тестов"""
    bot.send_message(message.chat.id,
                    "*Доступ разрешен!*\n\n"
                    "*Выберите формат загрузки (отправьте цифру):*\n"
                    "1. JSON-файл\n"
                    "2. Текстовое сообщение\n\n"
                    "Для отмены введите " + CANCEL_COMMAND,
                    parse_mode='Markdown',
                    reply_markup=create_upload_format_keyboard())
    bot.register_next_step_handler(message, choose_upload_format)

def choose_upload_format(message):
    """Выбор формата загрузки"""
    if check_cancel(message):
        return
        
    if message.chat.id not in authenticated_users:
        bot.send_message(message.chat.id, "Сессия устарела. Начните заново.")
        user_states.pop(message.chat.id, None)
        return
    
    choice = message.text.strip()
    
    if choice == "📄 JSON файл":
        if check_cancel(message):
            return
        
        bot.send_message(message.chat.id,
                        "*Загрузка JSON-файлом*\n\n"
                        "Отправьте JSON файл с тестами, соответствующий шаблону:\n"
                        "```json\n"
                        "{\n"
                        '  "task_id": 0,\n'
                        '  "task_name": "Название задачи",\n'
                        '  "tests": {\n'
                        '    "1": {\n'
                        '      "input": "входные данные",\n'
                        '      "output": "ожидаемый вывод"\n'
                        '    },\n'
                        '    "2": {\n'
                        '      "input": "входные данные",\n'
                        '      "output": "ожидаемый вывод"\n'
                        '    }\n'
                        '  }\n'
                        "}\n"
                        "```\n\n"
                        "*Пояснения:*\n"
                        "• task id - номер задачи (число)\n"
                        "• task name - название задачи\n"
                        "• tests - объект с тестами\n"
                        "• Для переносов строк используйте \\\\n\n\n"
                        "*Рекомендую использовать AI для конвертации файла*\n"
                        "*Просто приложите этот шаблон к запросу*\n"
                        "*Проверьте правильность task_id и task_name!*\n\n"
                        "Или просто выберите другую команду.",
                        parse_mode='Markdown',
                        reply_markup=create_cancel_keyboard())
    elif choice == "📝 Текстовый ввод":
        if check_cancel(message):
            return
        
        user_states[message.chat.id]['upload_format'] = 'text'
        
        tasks = task_manager.get_available_tasks()
        if tasks:
            tasks_text = "\n".join([f"• {task}" for task in tasks])
            bot.send_message(message.chat.id,
                           f"*Существующие задачи:*\n\n{tasks_text}\n\n"
                           f"*Введите номер задачи или* {CANCEL_COMMAND} *для отмены:*",
                           parse_mode='Markdown',
                           reply_markup=create_cancel_keyboard())
        else:
            bot.send_message(message.chat.id,
                           f"*Введите номер новой задачи или* {CANCEL_COMMAND} *для отмены:*",
                           parse_mode='Markdown',
                           reply_markup=create_cancel_keyboard())
        bot.register_next_step_handler(message, get_task_id_for_text_upload)
    else:
        if check_cancel(message):
            return
        
        bot.send_message(message.chat.id, f"Неверный выбор! Введите 📄 JSON файл, 📝 Текстовый ввод или {CANCEL_COMMAND}", parse_mode='Markdown', reply_markup=create_upload_format_keyboard())
        bot.register_next_step_handler(message, choose_upload_format)

def get_task_id_for_text_upload(message):
    """Получение номера задачи для текстовой загрузки"""
    if check_cancel(message):
        return
        
    task_id = message.text.strip()
    
    try:
        task_id_int = int(task_id)
        user_states[message.chat.id]['task_id'] = task_id_int
        
        existing_tests = task_manager.get_available_tests(task_id_int)
        if existing_tests:
            tests_count = len(existing_tests)
            existing_tests_info = ", ".join(existing_tests)
            bot.send_message(message.chat.id,
                           f"*Задача {task_id}!*\n"
                           f"*В этой задаче уже есть {tests_count} тестов:* {existing_tests_info}\n\n"
                           f"*Введите номер нового теста или* {CANCEL_COMMAND} *для отмены:*",
                           parse_mode='Markdown',
                           reply_markup=create_cancel_keyboard())
        else:
            bot.send_message(message.chat.id,
                           f"*Задача {task_id}!*\n"
                           f"*В этой задаче пока нет тестов.*\n\n"
                           f"*Введите номер первого теста или* {CANCEL_COMMAND} *для отмены:*",
                           parse_mode='Markdown',
                           reply_markup=create_cancel_keyboard())
        bot.register_next_step_handler(message, get_test_number_for_text_upload)
        
    except ValueError:
        bot.send_message(message.chat.id, f"Введите число или {CANCEL_COMMAND} для отмены!", parse_mode='Markdown', reply_markup=create_cancel_keyboard())
        bot.register_next_step_handler(message, get_task_id_for_text_upload)

def get_test_number_for_text_upload(message):
    """Получение номера теста для текстовой загрузки"""
    if check_cancel(message):
        return
        
    test_number = message.text.strip()
    user_state = user_states.get(message.chat.id, {})
    task_id = user_state.get('task_id')
    
    try:
        test_number_int = int(test_number)
        user_states[message.chat.id]['test_number'] = test_number_int
        
        bot.send_message(message.chat.id,
                        f"*Тест {test_number}!*\n\n"
                        f"*Введите входные данные или* {CANCEL_COMMAND} *для отмены:*",
                        parse_mode='Markdown',
                        reply_markup=create_cancel_keyboard())
        bot.register_next_step_handler(message, get_input_data_for_text_upload)
        
    except ValueError:
        bot.send_message(message.chat.id, f"Введите число или {CANCEL_COMMAND} для отмены!", parse_mode='Markdown', reply_markup=create_cancel_keyboard())
        bot.register_next_step_handler(message, get_test_number_for_text_upload)

def get_input_data_for_text_upload(message):
    """Получение входных данных для текстовой загрузки"""
    if check_cancel(message):
        return
        
    input_data = message.text.strip()
    user_states[message.chat.id]['input_data'] = input_data
    
    bot.send_message(message.chat.id,
                    "*Входные данные сохранены!*\n\n"
                    f"*Введите ожидаемый вывод или* {CANCEL_COMMAND} *для отмены:*",
                    parse_mode='Markdown',
                    reply_markup=create_cancel_keyboard())
    bot.register_next_step_handler(message, get_output_data_for_text_upload)

def get_output_data_for_text_upload(message):
    """Получение выходных данных для текстовой загрузки"""
    if check_cancel(message):
        return
        
    output_data = message.text.strip()
    user_state = user_states.get(message.chat.id, {})
    
    task_id = user_state.get('task_id')
    test_number = user_state.get('test_number')
    input_data = user_state.get('input_data')
    
    try:
        json_data = {
            "task_id": task_id,
            "task_name": f"Задача {task_id}",
            "tests": {
                str(test_number): {
                    "input": input_data,
                    "output": output_data
                }
            }
        }
        
        success, result_message = task_manager.load_from_json(json.dumps(json_data))
        bot.send_message(message.chat.id, result_message)
        
        ask_add_comment_after_upload(message, task_id, test_number)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка загрузки: {str(e)}", parse_mode='Markdown', reply_markup=create_cancel_keyboard())
        user_states.pop(message.chat.id, None)

def ask_add_comment_after_upload(message, task_id, test_number):
    """Спрашиваем, хочет ли пользователь добавить комментарий к только что загруженному тесту"""
    user_states[message.chat.id] = {
        'auth': True, 
        'action': 'upload', 
        'upload_format': 'text', 
        'task_id': task_id,
        'last_test_number': test_number
    }
    
    bot.send_message(message.chat.id,
                   f"*Тест {test_number} успешно загружен!*\n\n"
                   f"*Хотите добавить комментарий к этому тесту?*\n\n"
                   f"Введите 'ДА' чтобы добавить комментарий\n"
                   f"Введите 'НЕТ' чтобы продолжить без комментария\n"
                   f"Или введите {CANCEL_COMMAND} для выхода",
                   parse_mode='Markdown',
                   reply_markup=create_choice_keyboard())
    bot.register_next_step_handler(message, handle_comment_after_upload_choice)

def handle_comment_after_upload_choice(message):
    """Обработка выбора о добавлении комментария после загрузки"""
    if check_cancel(message):
        return
        
    user_state = user_states.get(message.chat.id, {})
    task_id = user_state.get('task_id')
    test_number = user_state.get('last_test_number')

    choice = message.text.strip()
    
    if choice == "✅ Да":
        user_states[message.chat.id]['action'] = 'comment_after_upload'
        bot.send_message(message.chat.id,
                       "*Введите ваше ФИО:*",
                       parse_mode='Markdown',
                       reply_markup=create_cancel_keyboard())
        bot.register_next_step_handler(message, get_teacher_name_after_upload)
        
    elif choice == "❌ Нет":
        ask_add_another_test(message, task_id)
    else:
        bot.send_message(message.chat.id, "Введите ✅ Да или ❌ Нет", parse_mode='Markdown', reply_markup=create_cancel_keyboard())
        bot.register_next_step_handler(message, handle_comment_after_upload_choice)

def get_teacher_name_after_upload(message):
    """Получение ФИО преподавателя после загрузки теста"""
    if check_cancel(message):
        return
        
    teacher_name = message.text.strip()
    
    if not teacher_name:
        bot.send_message(message.chat.id, f"ФИО не может быть пустым! Введите ФИО или {CANCEL_COMMAND}", parse_mode='Markdown', reply_markup=create_cancel_keyboard())
        bot.register_next_step_handler(message, get_teacher_name_after_upload)
        return
    
    user_states[message.chat.id]['teacher_name'] = teacher_name
    
    bot.send_message(message.chat.id,
                   "*Введите комментарий к тесту:*",
                   parse_mode='Markdown',
                   reply_markup=create_cancel_keyboard())
    bot.register_next_step_handler(message, save_comment_after_upload)

def save_comment_after_upload(message):
    """Сохранение комментария после загрузки теста"""
    if check_cancel(message):
        return
        
    user_state = user_states.get(message.chat.id, {})
    task_id = user_state.get('task_id')
    test_number = user_state.get('last_test_number')
    teacher_name = user_state.get('teacher_name')
    comment_text = message.text.strip()
    
    if not comment_text:
        bot.send_message(message.chat.id, f"Комментарий не может быть пустым! Введите комментарий или {CANCEL_COMMAND}", parse_mode='Markdown', reply_markup=create_cancel_keyboard())
        bot.register_next_step_handler(message, save_comment_after_upload)
        return
    
    success, result_message = task_manager.add_comment(task_id, test_number, comment_text, teacher_name)
    bot.send_message(message.chat.id, result_message)
    
    ask_add_another_test(message, task_id)

def ask_add_another_test(message, task_id):
    """Спрашиваем, хочет ли пользователь добавить еще тест"""
    user_states[message.chat.id] = {
        'auth': True, 
        'action': 'upload', 
        'upload_format': 'text', 
        'task_id': task_id
    }
    
    existing_tests = task_manager.get_available_tests(task_id)
    tests_count = len(existing_tests)
    existing_tests_info = ", ".join(existing_tests)
    
    bot.send_message(message.chat.id,
                   f"*Текущие тесты задачи {task_id}:* {existing_tests_info}\n"
                   f"*Всего тестов:* {tests_count}\n\n"
                   f"*Хотите добавить еще один тест?*\n\n"
                   f"Введите 'ДА' чтобы добавить следующий тест\n"
                   f"Введите 'НЕТ' чтобы завершить загрузку\n"
                   f"Или введите {CANCEL_COMMAND} для выхода",
                   parse_mode='Markdown',
                   reply_markup=create_choice_keyboard())
    bot.register_next_step_handler(message, handle_add_another_test)

def handle_add_another_test(message):
    """Обработка ответа на вопрос о добавлении еще теста"""
    if check_cancel(message):
        return
        
    user_state = user_states.get(message.chat.id, {})
    task_id = user_state.get('task_id')

    choice = message.text.strip()
    
    if choice == "✅ Да":
        existing_tests = task_manager.get_available_tests(task_id)
        if existing_tests:
            existing_tests_info = ", ".join(existing_tests)
            bot.send_message(message.chat.id,
                           f"*Текущие тесты:* {existing_tests_info}\n\n"
                           f"*Введите номер следующего теста или* {CANCEL_COMMAND} *для отмены:*",
                           parse_mode='Markdown',
                           reply_markup=create_cancel_keyboard())
        else:
            bot.send_message(message.chat.id,
                           f"*Введите номер теста или* {CANCEL_COMMAND} *для отмены:*",
                           parse_mode='Markdown',
                           reply_markup=create_cancel_keyboard())
        bot.register_next_step_handler(message, get_test_number_for_text_upload)
        
    elif choice == "❌ Нет":
        bot.send_message(message.chat.id, 
                        "Загрузка тестов завершена!", 
                        reply_markup=create_admin_keyboard())
        user_states.pop(message.chat.id, None)
    else:
        bot.send_message(message.chat.id, "Введите ✅ Да или ❌ Нет", parse_mode='Markdown', reply_markup=create_cancel_keyboard())
        bot.register_next_step_handler(message, handle_add_another_test)

def get_task_number(message):
    """Обработка номера задачи"""
    if check_cancel(message):
        return
        
    task_number = message.text.strip()
    
    try:
        task_id = int(task_number)
        if not task_manager.task_exists(task_id):
            available_tasks = task_manager.get_available_tasks()
            tasks_text = "\n".join([f"• {task}" for task in available_tasks])
            
            bot.send_message(message.chat.id,
                           f"Задача {task_number} не найдена.\n\n"
                           f"*Доступные задачи:*\n\n{tasks_text}\n\n"
                           f"Введите номер задачи из списка или {CANCEL_COMMAND} для отмены:",
                           parse_mode='Markdown',
                           reply_markup=create_cancel_keyboard())
            bot.register_next_step_handler(message, get_task_number)
            return
    except ValueError:
        bot.send_message(message.chat.id, f"Введите число или {CANCEL_COMMAND} для отмены!", parse_mode='Markdown', reply_markup=create_cancel_keyboard())
        bot.register_next_step_handler(message, get_task_number)
        return
    
    available_tests = task_manager.get_available_tests(task_id)
    if available_tests:
        tests_info = ", ".join(available_tests)
        bot.send_message(message.chat.id,
                       f"*Задача {task_number}!*\n"
                       f"Доступные тесты: {tests_info}\n\n"
                       f"*Введите номер теста или* {CANCEL_COMMAND} *для отмены:*",
                       parse_mode='Markdown',
                       reply_markup=create_cancel_keyboard())
    else:
        bot.send_message(message.chat.id,
                       f"*Задача {task_number}!*\n\n"
                       f"*Введите номер теста или* {CANCEL_COMMAND} *для отмены:*",
                       parse_mode='Markdown',
                       reply_markup=create_cancel_keyboard())
    
    bot.register_next_step_handler(message, lambda msg: get_test_number(msg, task_id))

def get_test_number(message, task_id):
    """Обработка номера теста"""
    if check_cancel(message):
        return
        
    test_number = message.text.strip()
    
    try:
        test_data = task_manager.get_test_data(task_id, int(test_number))
        
        if test_data:
            response = f"""
*Тест найден!*

*Задача:* {task_id} - {test_data.get('task_name', '')}
*Тест:* {test_number}

*Входные данные:*

{test_data['input']}


*Ожидаемый вывод:*

{test_data['output']}

"""
            try:
                if hasattr(task_manager, 'get_comments'):
                    comments = task_manager.get_comments(task_id, int(test_number))
                    if comments:
                        comments_text = "\n".join([f"*{c['author']}:* {c['text']}" for c in comments])
                        response += f"\n*Комментарии:*\n{comments_text}"
            except Exception as e:
                print(f"Ошибка при получении комментариев: {e}")
            
            response += "\n\nДля нового запроса используйте /help"
            
        else:
            available_tests = task_manager.get_available_tests(task_id)
            if available_tests:
                tests_info = ", ".join(available_tests)
                response = f"""
*Тест не найден!*

Задача: {task_id}
Тест: {test_number}

*Доступные тесты:* {tests_info}

Проверьте правильность номера теста или введите {CANCEL_COMMAND} для отмены.
"""
            else:
                response = f"Тест {test_number} для задачи {task_id} не найден."
        
        bot.send_message(message.chat.id, response, parse_mode='Markdown', reply_markup=create_main_keyboard())
        
    except ValueError:
        bot.send_message(message.chat.id, f"Введите число для номера теста или {CANCEL_COMMAND} для отмены!", parse_mode='Markdown', reply_markup=create_cancel_keyboard())
        bot.register_next_step_handler(message, lambda msg: get_test_number(msg, task_id))
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {str(e)}", reply_markup=create_main_keyboard())



@bot.message_handler(commands=['help'])
def handle_help_command(message):
    start_help(message)
@bot.message_handler(func=lambda message: message.text in ["❓ Помощь с задачей"])
def handle_help_button(message):
    start_help(message)
def start_help(message):
    """Начало получения помощи"""
    if check_cancel(message):
        return
        
    tasks = task_manager.get_available_tasks()
    if not tasks:
        bot.send_message(message.chat.id, "Нет доступных задач.", parse_mode='Markdown', reply_markup=create_main_keyboard())
        return
    
    tasks_text = "\n".join([f"• {task}" for task in tasks])
    
    bot.send_message(message.chat.id,
                    f"*Доступные задачи:*\n\n{tasks_text}\n\n"
                    f"*Введите номер задачи или* {CANCEL_COMMAND} *для отмены:*", 
                    parse_mode='Markdown',
                    reply_markup=create_cancel_keyboard())
    bot.register_next_step_handler(message, get_task_number)



@bot.message_handler(commands=['delete'])
def handle_delete_command(message):
    start_delete(message)
@bot.message_handler(func=lambda message: message.text in ["🗑 Удалить задачу"])
def handle_delete_button(message):
    start_delete(message)
@admin_required
def start_delete(message):
    """Удаление задачи"""
    tasks = task_manager.get_available_tasks()
    if tasks:
        tasks_text = "\n".join([f"• {task}" for task in tasks])
        bot.send_message(message.chat.id,
                       f"*Текущие задачи:*\n\n{tasks_text}\n\n"
                       f"*Введите номер задачи для удаления:*",
                       parse_mode='Markdown',
                       reply_markup=create_cancel_keyboard())
        bot.register_next_step_handler(message, confirm_delete)
    else:
        bot.send_message(message.chat.id, "Нет задач для удаления.", parse_mode='Markdown', reply_markup=create_cancel_keyboard())

def confirm_delete(message):
    """Подтверждение удаления задачи"""
    if check_cancel(message):
        return
        
    task_id = message.text.strip()
    
    try:
        task_id_int = int(task_id)
        
        if not task_manager.task_exists(task_id_int):
            bot.send_message(message.chat.id, f"Задача {task_id} не найдена.", parse_mode='Markdown', reply_markup=create_main_keyboard())
            user_states.pop(message.chat.id, None)
            return
        
        task_name = task_manager.get_task_name(task_id_int)
        
        user_states[message.chat.id]['task_to_delete'] = task_id_int
        
        bot.send_message(message.chat.id,
                       f"*Подтверждение удаления*\n\n"
                       f"Задача: {task_id} - {task_name}\n\n"
                       f"*ВНИМАНИЕ:* Это действие нельзя отменить!\n\n"
                       f"Для подтверждения введите: ДА\n"
                       f"Для отмены введите: НЕТ\n"
                       f"Или введите {CANCEL_COMMAND} для выхода",
                       parse_mode='Markdown',
                       reply_markup=create_choice_keyboard())
        bot.register_next_step_handler(message, execute_delete)
        
    except ValueError:
        bot.send_message(message.chat.id, f"Введите число или {CANCEL_COMMAND} для отмены!", parse_mode='Markdown', reply_markup=create_cancel_keyboard())
        bot.register_next_step_handler(message, confirm_delete)

def execute_delete(message):
    """Выполнение удаления задачи"""
    user_state = user_states.get(message.chat.id, {})
    task_id = user_state.get('task_to_delete')
    
    if not task_id:
        bot.send_message(message.chat.id, "Сессия устарела. Начните заново.")
        user_states.pop(message.chat.id, None)
        return
    
    choice = message.text.strip()
    
    if choice == "✅ Да":
        try:
            success, message_text = task_manager.delete_task(task_id)
            bot.send_message(message.chat.id, message_text, reply_markup=create_admin_keyboard())
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка удаления: {str(e)}", reply_markup=create_admin_keyboard())

    elif choice == "❌ Нет":
        bot.send_message(message.chat.id, "Удаление отменено.", reply_markup=create_admin_keyboard())
    else:
        bot.send_message(message.chat.id, "Введите ✅ Да или ❌ Нет", parse_mode='Markdown', reply_markup=create_cancel_keyboard())
        bot.register_next_step_handler(message, execute_delete)
    
    user_states.pop(message.chat.id, None)



@bot.message_handler(commands=['comment'])
def handle_comment_command(message):
    start_comment(message)
@bot.message_handler(func=lambda message: message.text in ["💬 Добавить комментарий"])
def handlecomment_button(message):
    start_comment(message)
@admin_required
def start_comment(message):
    """Начало добавления комментария"""
    bot.send_message(message.chat.id,
                    "*Введите ваше ФИО:*",
                    parse_mode='Markdown',
                    reply_markup=create_cancel_keyboard())
    bot.register_next_step_handler(message, get_teacher_name)

def get_teacher_name(message):
    """Получение ФИО преподавателя"""
    if check_cancel(message):
        return
        
    teacher_name = message.text.strip()
    
    if not teacher_name:
        bot.send_message(message.chat.id, f"ФИО не может быть пустым! Введите ФИО или {CANCEL_COMMAND}", parse_mode='Markdown', reply_markup=create_cancel_keyboard())
        bot.register_next_step_handler(message, get_teacher_name)
        return
    
    user_states[message.chat.id]['teacher_name'] = teacher_name
    
    tasks = task_manager.get_available_tasks()
    if tasks:
        tasks_text = "\n".join([f"• {task}" for task in tasks])
        bot.send_message(message.chat.id,
                       f"*Текущие задачи:*\n\n{tasks_text}\n\n"
                       f"*Введите номер задачи или* {CANCEL_COMMAND} *для отмены:*",
                       parse_mode='Markdown',
                       reply_markup=create_cancel_keyboard())
        bot.register_next_step_handler(message, get_task_for_comment)
    else:
        bot.send_message(message.chat.id, "Нет задач для комментирования.", parse_mode='Markdown', reply_markup=create_admin_keyboard())
        user_states.pop(message.chat.id, None)

def get_task_for_comment(message):
    """Получение номера задачи для комментария"""
    if check_cancel(message):
        return
        
    task_id = message.text.strip()
    
    try:
        task_id_int = int(task_id)
        
        if not task_manager.task_exists(task_id_int):
            bot.send_message(message.chat.id, f"Задача {task_id} не найдена.", parse_mode='Markdown', reply_markup=create_admin_keyboard())
            user_states.pop(message.chat.id, None)
            return
        
        user_states[message.chat.id]['task_id'] = task_id_int
        
        available_tests = task_manager.get_available_tests(task_id_int)
        if available_tests:
            tests_info = ", ".join(available_tests)
            bot.send_message(message.chat.id,
                           f"*Задача {task_id}!*\n"
                           f"Доступные тесты: {tests_info}\n\n"
                           f"*Введите номер теста или* {CANCEL_COMMAND} *для отмены:*",
                           parse_mode='Markdown',
                           reply_markup=create_cancel_keyboard())
            bot.register_next_step_handler(message, get_test_for_comment)
        else:
            bot.send_message(message.chat.id, f"У задачи {task_id} нет тестов.", parse_mode='Markdown', reply_markup=create_admin_keyboard())
            user_states.pop(message.chat.id, None)
            
    except ValueError:
        bot.send_message(message.chat.id, f"Введите число или {CANCEL_COMMAND} для отмены!", parse_mode='Markdown', reply_markup=create_cancel_keyboard())
        bot.register_next_step_handler(message, get_task_for_comment)

def get_test_for_comment(message):
    """Получение номера теста для комментария"""
    if check_cancel(message):
        return
        
    test_number = message.text.strip()
    user_state = user_states.get(message.chat.id, {})
    task_id = user_state.get('task_id')
    
    try:
        test_number_int = int(test_number)
        
        if not task_manager.get_test_data(task_id, test_number_int):
            bot.send_message(message.chat.id, f"Тест {test_number} для задачи {task_id} не найден.", parse_mode='Markdown', reply_markup=create_admin_keyboard())
            user_states.pop(message.chat.id, None)
            return
        
        user_states[message.chat.id]['test_number'] = test_number_int
        
        current_comments = task_manager.get_comments(task_id, test_number_int)
        if current_comments:
            comments_text = "\n".join([f"*{c['author']}:* {c['text']}" for c in current_comments])
            bot.send_message(message.chat.id,
                           f"*Текущие комментарии к тесту {test_number}:*\n\n{comments_text}\n\n"
                           f"*Введите новый комментарий или* {CANCEL_COMMAND} *для отмены:*",
                           parse_mode='Markdown',
                           reply_markup=create_cancel_keyboard())
        else:
            bot.send_message(message.chat.id,
                           f"*Комментариев к тесту {test_number} пока нет.*\n\n"
                           f"*Введите новый комментарий или* {CANCEL_COMMAND} *для отмены:*",
                           parse_mode='Markdown',
                           reply_markup=create_cancel_keyboard())
        
        bot.register_next_step_handler(message, save_comment)
        
    except ValueError:
        bot.send_message(message.chat.id, f"Введите число или {CANCEL_COMMAND} для отмены!", parse_mode='Markdown', reply_markup=create_cancel_keyboard())
        bot.register_next_step_handler(message, get_test_for_comment)

def save_comment(message):
    """Сохранение комментария"""
    if check_cancel(message):
        return
        
    user_state = user_states.get(message.chat.id, {})
    task_id = user_state.get('task_id')
    test_number = user_state.get('test_number')
    teacher_name = user_state.get('teacher_name')
    comment_text = message.text.strip()
    
    if not comment_text:
        bot.send_message(message.chat.id, f"Комментарий не может быть пустым! Введите комментарий или {CANCEL_COMMAND}", parse_mode='Markdown', reply_markup=create_cancel_keyboard())
        bot.register_next_step_handler(message, save_comment)
        return
    
    success, result_message = task_manager.add_comment(task_id, test_number, comment_text, teacher_name)
    bot.send_message(message.chat.id, result_message, reply_markup=create_cancel_keyboard())
    
    user_states.pop(message.chat.id, None)



@bot.message_handler(commands=['deletecomment'])
def handle_deletecomment_command(message):
    start_deletecomment(message)
@bot.message_handler(func=lambda message: message.text in ["🗑 Удалить комментарии"])
def handle_deletecomment_button(message):
    start_deletecomment(message)
@admin_required
def start_deletecomment(message):
    """Начало удаления комментариев"""
    tasks = task_manager.get_available_tasks()
    if tasks:
        tasks_text = "\n".join([f"• {task}" for task in tasks])
        bot.send_message(message.chat.id,
                       f"*Текущие задачи:*\n\n{tasks_text}\n\n"
                       f"*Введите номер задачи или* {CANCEL_COMMAND} *для отмены:*",
                       parse_mode='Markdown',
                       reply_markup=create_cancel_keyboard())
        bot.register_next_step_handler(message, get_task_for_comment_delete)
    else:
        bot.send_message(message.chat.id, "Нет задач для управления комментариями.", parse_mode='Markdown', reply_markup=create_admin_keyboard())

def get_task_for_comment_delete(message):
    """Получение номера задачи для удаления комментариев"""
    if check_cancel(message):
        return
        
    task_id = message.text.strip()
    
    try:
        task_id_int = int(task_id)
        
        if not task_manager.task_exists(task_id_int):
            bot.send_message(message.chat.id, f"Задача {task_id} не найдена.", parse_mode='Markdown', reply_markup=create_admin_keyboard())
            user_states.pop(message.chat.id, None)
            return
        
        user_states[message.chat.id]['task_id'] = task_id_int
        
        available_tests = task_manager.get_available_tests(task_id_int)
        if available_tests:
            tests_info = ", ".join(available_tests)
            bot.send_message(message.chat.id,
                           f"*Задача {task_id}!*\n"
                           f"Доступные тесты: {tests_info}\n\n"
                           f"*Введите номер теста или* {CANCEL_COMMAND} *для отмены:*",
                           parse_mode='Markdown',
                           reply_markup=create_cancel_keyboard())
            bot.register_next_step_handler(message, show_comments_for_deletion)
        else:
            bot.send_message(message.chat.id, f"У задачи {task_id} нет тестов.", parse_mode='Markdown', reply_markup=create_admin_keyboard())
            user_states.pop(message.chat.id, None)
            
    except ValueError:
        bot.send_message(message.chat.id, f"Введите число или {CANCEL_COMMAND} для отмены!", parse_mode='Markdown', reply_markup=create_cancel_keyboard())
        bot.register_next_step_handler(message, get_task_for_comment_delete)

def show_comments_for_deletion(message):
    """Показывает комментарии для удаления"""
    if check_cancel(message):
        return
        
    test_number = message.text.strip()
    user_state = user_states.get(message.chat.id, {})
    task_id = user_state.get('task_id')
    
    try:
        test_number_int = int(test_number)
        
        comments = task_manager.get_comments_with_ids(task_id, test_number_int)
        
        if not comments:
            bot.send_message(message.chat.id, 
                           f"У теста {test_number} задачи {task_id} нет комментариев.", parse_mode='Markdown', reply_markup=create_admin_keyboard())
            user_states.pop(message.chat.id, None)
            return
        
        user_states[message.chat.id]['test_number'] = test_number_int
        
        comments_text = ""
        for i, comment in enumerate(comments, 1):
            comment_preview = comment['text'][:50] + "..." if len(comment['text']) > 50 else comment['text']
            comments_text += f"{i}. {comment_preview}\n"
        
        bot.send_message(message.chat.id,
                       f"*Комментарии к задаче {task_id}, тест {test_number}:*\n\n{comments_text}\n\n"
                       f"*Выберите действие:*\n"
                       f"• Введите номер комментария для удаления (1, 2, 3...)\n"
                       f"• Введите 'ALL' чтобы удалить все комментарии\n"
                       f"• Введите 'CANCEL' для отмены\n"
                       f"• Или введите {CANCEL_COMMAND} для выхода",
                       parse_mode='Markdown',
                       reply_markup=create_delete_comment_keyboard())
        bot.register_next_step_handler(message, handle_comment_deletion)
        
    except ValueError:
        bot.send_message(message.chat.id, f"Введите число или {CANCEL_COMMAND} для отмены!", parse_mode='Markdown', reply_markup=create_cancel_keyboard())
        bot.register_next_step_handler(message, show_comments_for_deletion)

def handle_comment_deletion(message):
    """Обработка выбора удаления комментариев"""
    if check_cancel(message):
        return
        
    user_state = user_states.get(message.chat.id, {})
    task_id = user_state.get('task_id')
    test_number = user_state.get('test_number')
    choice = message.text.strip()
    
    if choice == "❌ Отмена":
        bot.send_message(message.chat.id, "Операция отменена.")
        user_states.pop(message.chat.id, None)
        return
    
    elif choice == "🗑 Удалить все комментарии":
        success, result_message = task_manager.delete_all_comments(task_id, test_number)
        bot.send_message(message.chat.id, result_message)
        user_states.pop(message.chat.id, None)
        return
    
    else:
        try:
            comments = task_manager.get_comments_with_ids(task_id, test_number)
            comment_index = int(choice) - 1
            
            if 0 <= comment_index < len(comments):
                comment_id = comments[comment_index]['id']
                success, result_message = task_manager.deletecomment(comment_id)
                bot.send_message(message.chat.id, result_message, reply_markup=create_admin_keyboard())
            else:
                bot.send_message(message.chat.id, f"Неверный номер комментария! Введите число от 1 до {len(comments)} или {CANCEL_COMMAND}", parse_mode='Markdown', reply_markup=create_cancel_keyboard())
                bot.register_next_step_handler(message, handle_comment_deletion)
                return
                
        except ValueError:
            bot.send_message(message.chat.id, f"Введите число, 🗑 Удалить все комментарии, ❌ Отмена или {CANCEL_COMMAND}", parse_mode='Markdown', reply_markup=create_delete_comment_keyboard())
            bot.register_next_step_handler(message, handle_comment_deletion)
            return
    
    user_states.pop(message.chat.id, None)



@bot.message_handler(content_types=['document'])
def handle_document(message):
    """Обработка загружаемых файлов"""
    user_state = user_states.get(message.chat.id, {})
    
    if not user_state.get('auth'):
        bot.send_message(message.chat.id, "Сначала получите доступ", parse_mode='Markdown', reply_markup=create_cancel_keyboard())
        return
    
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        if not message.document.file_name.endswith('.json'):
            bot.send_message(message.chat.id, "Файл должен быть в формате JSON", parse_mode='Markdown', reply_markup=create_cancel_keyboard())
            return
        
        json_content = downloaded_file.decode('utf-8')
        
        success, result_message = task_manager.load_from_json(json_content)
        
        bot.send_message(message.chat.id, result_message, reply_markup=create_main_keyboard())
        
        user_states.pop(message.chat.id, None)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка обработки файла: {str(e)}", reply_markup=create_admin_keyboard())



@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text.lower() == "привет":
        bot.send_message(message.chat.id, "Привет! Используйте /start для просмотра команд", reply_markup=create_main_keyboard())
    else:
        bot.send_message(message.chat.id,
                        "Не понимаю ваше сообщение.\n\n"
                        "*Используйте кнопки ниже или команды:*\n"
                        "/start - Начало работы\n"
                        "/help - Получить помощь\n"
                        "/admin - Для преподавателей",
                        parse_mode='Markdown', 
                        reply_markup=create_main_keyboard())

if __name__ == "__main__":
    print("Бот запущен!")
    bot.polling(none_stop=True, interval=0)