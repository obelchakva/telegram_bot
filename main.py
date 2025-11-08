import telebot
import os
import json
from test_manager import TestManager

# Конфигурация
ADMIN_PASSWORD = "123"  # Пароль для загрузки
bot = telebot.TeleBot('7722825450:AAHKyoLykpV63lmZisNIargwPh5qQXqFlTg')
test_manager = TestManager()

bot.set_my_commands([
    telebot.types.BotCommand("start", "Начало работы"),
    telebot.types.BotCommand("help", "Помощь с задачей"),
    telebot.types.BotCommand("tasks", "Список задач"),
    telebot.types.BotCommand("info", "Информация о боте"),
])

user_states = {}


@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
*Бот помощи с задачами Informatics*

*Доступные команды:*
/help - Получить помощь с задачей
/info - Информация о боте
/tasks - Список доступных задач

*Как это работает:*
1. Используйте /help чтобы начать
2. Выберите задачу из списка /tasks
3. Введите номер теста
4. Получите помощь!
    """
    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown')


@bot.message_handler(commands=['admin'])
def show_admin_commands(message):
    """Показывает команды для преподавателей после ввода пароля"""
    bot.send_message(message.chat.id, 
                    "*Введите пароль для доступа к командам преподавателя:*", 
                    parse_mode='Markdown')
    bot.register_next_step_handler(message, check_admin_password)

def check_admin_password(message):
    """Проверяет пароль и показывает админские команды"""
    if message.text == ADMIN_PASSWORD:
        admin_commands_text = """
*Команды для преподавателей:*

/upload - Загрузить новые тесты
/delete - Удалить задачу  
/comment - Добавить комментарий к тесту
/delete_comment - Удалить комментарии

*Как использовать:*
• /upload - загрузите JSON файл с тестами
• /delete - выберите задачу для удаления
• /comment - добавьте пояснение к конкретному тесту
• /delete_comment - управление комментариями
"""
        bot.send_message(message.chat.id, admin_commands_text, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "Неверный пароль!")


@bot.message_handler(commands=['tasks'])
def show_tasks(message):
    """Показать список доступных задач"""
    tasks = test_manager.get_available_tasks()
    if tasks:
        tasks_text = "\n".join([f"• {task}" for task in tasks])
        response = f"*Доступные задачи:*\n\n{tasks_text}"
    else:
        response = "Нет доступных задач. Обратитесь к преподавателю."
    
    bot.send_message(message.chat.id, response, parse_mode='Markdown')


@bot.message_handler(commands=['upload'])
def start_upload(message):
    """Начало загрузки тестов (только для преподавателей)"""
    bot.send_message(message.chat.id, 
                    "*Введите пароль для доступа к загрузке тестов:*", 
                    parse_mode='Markdown')
    bot.register_next_step_handler(message, check_password)

def check_password(message):
    """Проверка пароля"""
    if message.text == ADMIN_PASSWORD:
        user_states[message.chat.id] = {'auth': True}
        bot.send_message(message.chat.id,
                        "*Доступ разрешен!*\n\n"
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
                        "• task_id - номер задачи (число)\n"
                        "• task_name - название задачи\n"
                        "• tests - объект с тестами\n"
                        "• Для переносов строк используйте \\\\n\n\n"
                        "*Рекомендую использовать AI для конвертации файла*\n"
                        "*Просто приложите этот шаблон к запросу*\n"
                        "*Проверьте правильность task_id и task_name!*", 
                        parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "Неверный пароль!")
        user_states.pop(message.chat.id, None)


@bot.message_handler(commands=['delete'])
def start_delete(message):
    """Начало процесса удаления задачи"""
    bot.send_message(message.chat.id, 
                    "*Введите пароль для доступа к удалению задач:*", 
                    parse_mode='Markdown')
    bot.register_next_step_handler(message, check_delete_password)

def check_delete_password(message):
    """Проверка пароля для удаления"""
    if message.text == ADMIN_PASSWORD:
        user_states[message.chat.id] = {'auth': True, 'action': 'delete'}
        
        tasks = test_manager.get_available_tasks()
        if tasks:
            tasks_text = "\n".join([f"• {task}" for task in tasks])
            bot.send_message(message.chat.id,
                           f"*Доступ разрешен!*\n\n"
                           f"*Текущие задачи:*\n\n{tasks_text}\n\n"
                           f"*Введите номер задачи для удаления:*",
                           parse_mode='Markdown')
            bot.register_next_step_handler(message, confirm_delete)
        else:
            bot.send_message(message.chat.id, "Нет задач для удаления.")
            user_states.pop(message.chat.id, None)
    else:
        bot.send_message(message.chat.id, "Неверный пароль!")
        user_states.pop(message.chat.id, None)

def confirm_delete(message):
    """Подтверждение удаления задачи"""
    task_id = message.text.strip()
    
    try:
        task_id_int = int(task_id)
        
        if not test_manager.task_exists(task_id_int):
            bot.send_message(message.chat.id, f"Задача {task_id} не найдена.")
            user_states.pop(message.chat.id, None)
            return
        
        task_name = test_manager.get_task_name(task_id_int)
        
        user_states[message.chat.id]['task_to_delete'] = task_id_int
        
        bot.send_message(message.chat.id,
                       f"*Подтверждение удаления*\n\n"
                       f"Задача: {task_id} - {task_name}\n\n"
                       f"*ВНИМАНИЕ:* Это действие нельзя отменить!\n\n"
                       f"Для подтверждения введите: ДА\n"
                       f"Для отмены введите: НЕТ",
                       parse_mode='Markdown')
        bot.register_next_step_handler(message, execute_delete)
        
    except ValueError:
        bot.send_message(message.chat.id, "Введите число!")
        bot.register_next_step_handler(message, confirm_delete)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {str(e)}")
        user_states.pop(message.chat.id, None)

def execute_delete(message):
    """Выполнение удаления задачи"""
    user_state = user_states.get(message.chat.id, {})
    task_id = user_state.get('task_to_delete')
    
    if not task_id:
        bot.send_message(message.chat.id, "Сессия устарела. Начните заново.")
        user_states.pop(message.chat.id, None)
        return
    
    if message.text.upper() == 'ДА':
        try:
            success, message_text = test_manager.delete_task(task_id)
            bot.send_message(message.chat.id, message_text)
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка удаления: {str(e)}")
    elif message.text.upper() == 'НЕТ':
        bot.send_message(message.chat.id, "Удаление отменено.")
    else:
        bot.send_message(message.chat.id, "Введите 'ДА' или 'НЕТ'")
        bot.register_next_step_handler(message, execute_delete)
    
    user_states.pop(message.chat.id, None)


@bot.message_handler(commands=['comment'])
def start_comment(message):
    """Начало добавления комментария"""
    bot.send_message(message.chat.id, 
                    "*Введите пароль для добавления комментариев:*", 
                    parse_mode='Markdown')
    bot.register_next_step_handler(message, check_comment_password)

def check_comment_password(message):
    """Проверка пароля для комментариев"""
    if message.text == ADMIN_PASSWORD:
        user_states[message.chat.id] = {'auth': True, 'action': 'comment'}
        
        tasks = test_manager.get_available_tasks()
        if tasks:
            tasks_text = "\n".join([f"• {task}" for task in tasks])
            bot.send_message(message.chat.id,
                           f"*Доступ разрешен!*\n\n"
                           f"*Текущие задачи:*\n\n{tasks_text}\n\n"
                           f"*Введите номер задачи для комментария:*",
                           parse_mode='Markdown')
            bot.register_next_step_handler(message, get_task_for_comment)
        else:
            bot.send_message(message.chat.id, "Нет задач для комментирования.")
            user_states.pop(message.chat.id, None)
    else:
        bot.send_message(message.chat.id, "Неверный пароль!")
        user_states.pop(message.chat.id, None)

def get_task_for_comment(message):
    """Получение номера задачи для комментария"""
    task_id = message.text.strip()
    
    try:
        task_id_int = int(task_id)
        
        if not test_manager.task_exists(task_id_int):
            bot.send_message(message.chat.id, f"Задача {task_id} не найдена.")
            user_states.pop(message.chat.id, None)
            return
        
        user_states[message.chat.id]['task_id'] = task_id_int
        
        available_tests = test_manager.get_available_tests(task_id_int)
        if available_tests:
            tests_info = ", ".join(available_tests)
            bot.send_message(message.chat.id,
                           f"*Задача {task_id}!*\n"
                           f"Доступные тесты: {tests_info}\n\n"
                           f"*Введите номер теста для комментария:*",
                           parse_mode='Markdown')
            bot.register_next_step_handler(message, get_test_for_comment)
        else:
            bot.send_message(message.chat.id, f"У задачи {task_id} нет тестов.")
            user_states.pop(message.chat.id, None)
            
    except ValueError:
        bot.send_message(message.chat.id, "Введите число!")
        bot.register_next_step_handler(message, get_task_for_comment)

def get_test_for_comment(message):
    """Получение номера теста для комментария"""
    test_number = message.text.strip()
    user_state = user_states.get(message.chat.id, {})
    task_id = user_state.get('task_id')
    
    try:
        test_number_int = int(test_number)
        
        if not test_manager.get_test_data(task_id, test_number_int):
            bot.send_message(message.chat.id, f"Тест {test_number} для задачи {task_id} не найден.")
            user_states.pop(message.chat.id, None)
            return
        
        user_states[message.chat.id]['test_number'] = test_number_int
        
        current_comments = test_manager.get_comments(task_id, test_number_int)
        if current_comments:
            comments_text = "\n".join([f"{c['text']}" for c in current_comments])
            bot.send_message(message.chat.id,
                           f"*Текущие комментарии к тесту {test_number}:*\n\n{comments_text}\n\n"
                           f"*Введите новый комментарий:*",
                           parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id,
                           f"*Комментариев к тесту {test_number} пока нет.*\n\n"
                           f"*Введите новый комментарий:*",
                           parse_mode='Markdown')
        
        bot.register_next_step_handler(message, save_comment)
        
    except ValueError:
        bot.send_message(message.chat.id, "Введите число!")
        bot.register_next_step_handler(message, get_test_for_comment)

def save_comment(message):
    """Сохранение комментария"""
    user_state = user_states.get(message.chat.id, {})
    task_id = user_state.get('task_id')
    test_number = user_state.get('test_number')
    comment_text = message.text.strip()
    
    if not comment_text:
        bot.send_message(message.chat.id, "Комментарий не может быть пустым.")
        user_states.pop(message.chat.id, None)
        return
    
    success, result_message = test_manager.add_comment(task_id, test_number, comment_text)
    bot.send_message(message.chat.id, result_message)
    
    user_states.pop(message.chat.id, None)


@bot.message_handler(commands=['delete_comment'])
def start_delete_comment(message):
    """Начало удаления комментариев"""
    bot.send_message(message.chat.id, 
                    "*Введите пароль для управления комментариями:*", 
                    parse_mode='Markdown')
    bot.register_next_step_handler(message, check_delete_comment_password)

def check_delete_comment_password(message):
    """Проверка пароля для удаления комментариев"""
    if message.text == ADMIN_PASSWORD:
        user_states[message.chat.id] = {'auth': True, 'action': 'delete_comment'}
        
        tasks = test_manager.get_available_tasks()
        if tasks:
            tasks_text = "\n".join([f"• {task}" for task in tasks])
            bot.send_message(message.chat.id,
                           f"*Доступ разрешен!*\n\n"
                           f"*Текущие задачи:*\n\n{tasks_text}\n\n"
                           f"*Введите номер задачи:*",
                           parse_mode='Markdown')
            bot.register_next_step_handler(message, get_task_for_comment_delete)
        else:
            bot.send_message(message.chat.id, "Нет задач для управления комментариями.")
            user_states.pop(message.chat.id, None)
    else:
        bot.send_message(message.chat.id, "Неверный пароль!")
        user_states.pop(message.chat.id, None)

def get_task_for_comment_delete(message):
    """Получение номера задачи для удаления комментариев"""
    task_id = message.text.strip()
    
    try:
        task_id_int = int(task_id)
        
        if not test_manager.task_exists(task_id_int):
            bot.send_message(message.chat.id, f"Задача {task_id} не найдена.")
            user_states.pop(message.chat.id, None)
            return
        
        user_states[message.chat.id]['task_id'] = task_id_int
        
        available_tests = test_manager.get_available_tests(task_id_int)
        if available_tests:
            tests_info = ", ".join(available_tests)
            bot.send_message(message.chat.id,
                           f"*Задача {task_id}!*\n"
                           f"Доступные тесты: {tests_info}\n\n"
                           f"*Введите номер теста:*",
                           parse_mode='Markdown')
            bot.register_next_step_handler(message, show_comments_for_deletion)
        else:
            bot.send_message(message.chat.id, f"У задачи {task_id} нет тестов.")
            user_states.pop(message.chat.id, None)
            
    except ValueError:
        bot.send_message(message.chat.id, "Введите число!")
        bot.register_next_step_handler(message, get_task_for_comment_delete)

def show_comments_for_deletion(message):
    """Показывает комментарии для удаления"""
    test_number = message.text.strip()
    user_state = user_states.get(message.chat.id, {})
    task_id = user_state.get('task_id')
    
    try:
        test_number_int = int(test_number)
        
        comments = test_manager.get_comments_with_ids(task_id, test_number_int)
        
        if not comments:
            bot.send_message(message.chat.id, 
                           f"У теста {test_number} задачи {task_id} нет комментариев.")
            user_states.pop(message.chat.id, None)
            return
        
        user_states[message.chat.id]['test_number'] = test_number_int
        
        comments_text = ""
        for i, comment in enumerate(comments, 1):
            comments_text += f"{i}. {comment['text']} (ID: {comment['id']})\n"
        
        bot.send_message(message.chat.id,
                       f"*Комментарии к задаче {task_id}, тест {test_number}:*\n\n{comments_text}\n\n"
                       f"*Выберите действие:*\n"
                       f"• Введите номер комментария для удаления (1, 2, 3...)\n"
                       f"• Введите 'ALL' чтобы удалить все комментарии\n"
                       f"• Введите 'CANCEL' для отмены",
                       parse_mode='Markdown')
        bot.register_next_step_handler(message, handle_comment_deletion)
        
    except ValueError:
        bot.send_message(message.chat.id, "Введите число!")
        bot.register_next_step_handler(message, show_comments_for_deletion)

def handle_comment_deletion(message):
    """Обработка выбора удаления комментариев"""
    user_state = user_states.get(message.chat.id, {})
    task_id = user_state.get('task_id')
    test_number = user_state.get('test_number')
    user_choice = message.text.strip().upper()
    
    if user_choice == 'CANCEL':
        bot.send_message(message.chat.id, "Операция отменена.")
        user_states.pop(message.chat.id, None)
        return
    
    elif user_choice == 'ALL':
        success, result_message = test_manager.delete_all_comments(task_id, test_number)
        bot.send_message(message.chat.id, result_message)
        user_states.pop(message.chat.id, None)
        return
    
    else:
        try:
            comments = test_manager.get_comments_with_ids(task_id, test_number)
            comment_index = int(user_choice) - 1
            
            if 0 <= comment_index < len(comments):
                comment_id = comments[comment_index]['id']
                success, result_message = test_manager.delete_comment(comment_id)
                bot.send_message(message.chat.id, result_message)
            else:
                bot.send_message(message.chat.id, "Неверный номер комментария.")
                bot.register_next_step_handler(message, handle_comment_deletion)
                return
                
        except ValueError:
            bot.send_message(message.chat.id, "Введите число, 'ALL' или 'CANCEL'")
            bot.register_next_step_handler(message, handle_comment_deletion)
            return
    
    user_states.pop(message.chat.id, None)


@bot.message_handler(content_types=['document'])
def handle_document(message):
    """Обработка загружаемых файлов"""
    user_state = user_states.get(message.chat.id, {})
    
    if not user_state.get('auth'):
        bot.send_message(message.chat.id, "Сначала получите доступ через /upload")
        return
    
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        if not message.document.file_name.endswith('.json'):
            bot.send_message(message.chat.id, "Файл должен быть в формате JSON")
            return
        
        json_content = downloaded_file.decode('utf-8')
        
        success, result_message = test_manager.load_from_json(json_content)
        
        bot.send_message(message.chat.id, result_message)
        
        user_states.pop(message.chat.id, None)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка обработки файла: {str(e)}")


@bot.message_handler(commands=['help'])
def start_help(message):
    """Начало процесса получения помощи"""
    tasks = test_manager.get_available_tasks()
    if not tasks:
        bot.send_message(message.chat.id, "Нет доступных задач.")
        return
    
    tasks_text = "\n".join([f"• {task}" for task in tasks])
    
    bot.send_message(message.chat.id,
                    f"*Доступные задачи:*\n\n{tasks_text}\n\n"
                    f"*Введите номер задачи:*", 
                    parse_mode='Markdown')
    bot.register_next_step_handler(message, get_task_number)

def get_task_number(message):
    """Обработка номера задачи"""
    task_number = message.text.strip()
    
    try:
        task_id = int(task_number)
        if not test_manager.task_exists(task_id):
            available_tasks = test_manager.get_available_tasks()
            tasks_text = "\n".join([f"• {task}" for task in available_tasks])
            
            bot.send_message(message.chat.id,
                           f"Задача {task_number} не найдена.\n\n"
                           f"*Доступные задачи:*\n\n{tasks_text}\n\n"
                           f"Введите номер задачи из списка:",
                           parse_mode='Markdown')
            bot.register_next_step_handler(message, get_task_number)
            return
    except ValueError:
        bot.send_message(message.chat.id, "Введите число!")
        bot.register_next_step_handler(message, get_task_number)
        return
    
    available_tests = test_manager.get_available_tests(task_id)
    if available_tests:
        tests_info = ", ".join(available_tests)
        bot.send_message(message.chat.id,
                       f"*Задача {task_number}!*\n"
                       f"Доступные тесты: {tests_info}\n\n"
                       f"*Введите номер теста:*",
                       parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id,
                       f"*Задача {task_number}!*\n\n"
                       f"*Введите номер теста:*",
                       parse_mode='Markdown')
    
    bot.register_next_step_handler(message, lambda msg: get_test_number(msg, task_id))

def get_test_number(message, task_id):
    """Обработка номера теста"""
    test_number = message.text.strip()
    
    try:
        test_data = test_manager.get_test_data(task_id, int(test_number))
        
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
            if test_data.get('comments'):
                comments_text = "\n".join([f"*{c['author']}:* {c['text']}" for c in test_data['comments']])
                response += f"\n*Комментарии:*\n{comments_text}"
            
            response += "\n\nДля нового запроса используйте /help"
            
        else:
            available_tests = test_manager.get_available_tests(task_id)
            if available_tests:
                tests_info = ", ".join(available_tests)
                response = f"""
*Тест не найден!*

Задача: {task_id}
Тест: {test_number}

*Доступные тесты:* {tests_info}

Проверьте правильность номера теста.
"""
            else:
                response = f"Тест {test_number} для задачи {task_id} не найден."
        
        bot.send_message(message.chat.id, response, parse_mode='Markdown')
        
    except ValueError:
        bot.send_message(message.chat.id, "Введите число для номера теста!")
        bot.register_next_step_handler(message, lambda msg: get_test_number(msg, task_id))
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {str(e)}")


@bot.message_handler(commands=['info'])
def send_info(message):
    info_text = """
*Информация о боте*

*Назначение:* Помощь с учебными задачами и тестами
*Разработчик:* Обельчак Вячеслав Андреевич
*Версия:* 2.0

*Новые возможности:*
• Загрузка тестов через бота
• База данных задач
• Удобный поиск

Для получения помощи используйте /help
    """
    bot.send_message(message.chat.id, info_text, parse_mode='Markdown')

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text.lower() == "привет":
        bot.send_message(message.chat.id, "Привет! Используйте /start для просмотра команд")
    else:
        bot.send_message(message.chat.id,
                        "Не понимаю ваше сообщение.\n\n"
                        "*Доступные команды:*\n"
                        "/start - Начало работы\n"
                        "/help - Получить помощь\n"
                        "/tasks - Список задач\n"
                        "/info - Информация",
                        parse_mode='Markdown')

if __name__ == "__main__":
    print("Бот запущен!")
    bot.polling(none_stop=True, interval=0)