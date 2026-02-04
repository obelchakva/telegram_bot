import telebot
import os
import re
from telebot import types
from config import BOT_TOKEN, BASE_DATA_PATH, TEACHERS

bot = telebot.TeleBot(BOT_TOKEN)

user_states = {}
user_data = {}

bot.set_my_commands([
    telebot.types.BotCommand("help", "Помощь с задачей"),
    telebot.types.BotCommand("cancel", "Отменить дейтвие"),
])

def show_main_keyboard(chat_id):
    """Показать основную клавиатуру"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    btn_tasks = types.KeyboardButton('📋 Список задач')
    btn_choose_task = types.KeyboardButton('🔢 Выбрать задачу')
    btn_choose_test = types.KeyboardButton('🧪 Выбрать тест')
    btn_current_task = types.KeyboardButton('📌 Текущая задача')
    
    markup.add(btn_tasks, btn_choose_task, btn_choose_test, btn_current_task)
    
    if chat_id in TEACHERS:
        btn_add_comment = types.KeyboardButton('💬 Добавить комментарий')
        markup.add(btn_add_comment)
    
    return markup

def get_available_tasks():
    """Получить список доступных задач"""
    if not os.path.exists(BASE_DATA_PATH):
        return []
    
    tasks = []
    for item in os.listdir(BASE_DATA_PATH):
        task_path = os.path.join(BASE_DATA_PATH, item)
        if os.path.isdir(task_path):
            tasks.append(item)
    return sorted(tasks)

def get_available_tests(task_number):
    """Получить список доступных тестов для задачи"""
    task_path = os.path.join(BASE_DATA_PATH, task_number, "tests")
    if not os.path.exists(task_path):
        return []
    
    tests = set()
    for file in os.listdir(task_path):
        match = re.match(r'^(\d+)(?:\..*)?$', file)
        if match:
            tests.add(match.group(1))
    
    return sorted(list(tests), key=int)

def get_task_info(task_number):
    """Получить информацию о задаче"""
    info_path = os.path.join(BASE_DATA_PATH, task_number, "task_info.txt")
    if os.path.exists(info_path):
        with open(info_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Описание задачи отсутствует"

def is_teacher(user_id):
    """Проверка, является ли пользователь преподавателем"""
    return user_id in TEACHERS

@bot.message_handler(commands=['help'])
def send_welcome(message):
    welcome_text = """
*Бот помощи с задачами Informatics*

*Как пользоваться:*
1. Нажмите "Список задач" для просмотра доступных задач
2. Выберите нужную задачу
3. Выберите номер теста для просмотра

Тесты и комментарии загружаются преподавателями.
    """
    
    bot.send_message(message.chat.id, welcome_text, 
                     parse_mode='Markdown', 
                     reply_markup=show_main_keyboard(message.chat.id))

@bot.message_handler(func=lambda message: message.text == '📋 Список задач')
def list_tasks(message):
    tasks = get_available_tasks()
    
    if not tasks:
        bot.send_message(message.chat.id, "❌ Задачи еще не загружены.")
        return
    
    tasks_text = "📚 *Доступные задачи:*\n\n"
    for i, task in enumerate(tasks, 1):
        description = get_task_info(task)
        first_line = description.split('\n')[0] if description else "Нет описания"
        tasks_text += f"*{task}* - {first_line}\n"
    
    bot.send_message(message.chat.id, tasks_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == '🔢 Выбрать задачу')
def choose_task_handler(message):
    tasks = get_available_tasks()
    
    if not tasks:
        bot.send_message(message.chat.id, "❌ Задачи еще не загружены.")
        return
    
    # Создаем клавиатуру с номерами задач
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    task_buttons = [types.KeyboardButton(task) for task in tasks]
    markup.add(*task_buttons)
    markup.add(types.KeyboardButton('↩️ Назад'))
    
    bot.send_message(message.chat.id, 
                     "Выберите номер задачи из списка:",
                     reply_markup=markup)
    
    user_states[message.chat.id] = 'waiting_for_task_selection'

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'waiting_for_task_selection')
def handle_task_selection(message):
    if message.text == '↩️ Назад':
        bot.send_message(message.chat.id, "Главное меню:", 
                         reply_markup=show_main_keyboard(message.chat.id))
        user_states.pop(message.chat.id, None)
        return
    
    task_number = message.text.strip()
    
    if task_number in get_available_tasks():
        # Сохраняем выбранную задачу для пользователя
        if message.chat.id not in user_data:
            user_data[message.chat.id] = {}
        user_data[message.chat.id]['task'] = task_number
        
        # Получаем информацию о задаче
        task_info = get_task_info(task_number)
        
        # Получаем список тестов
        tests = get_available_tests(task_number)
        
        response = f"✅ *Задача {task_number} выбрана*\n\n"
        response += f"*Описание:*\n{task_info}\n\n"
        
        if tests:
            response += f"*Доступные тесты:* {', '.join(tests[:10])}"
            if len(tests) > 10:
                response += f" и еще {len(tests) - 10}..."
        else:
            response += "❌ *Тесты для этой задачи отсутствуют*"
        
        bot.send_message(message.chat.id, response, parse_mode='Markdown')
        
        bot.send_message(message.chat.id, "Главное меню:", 
                         reply_markup=show_main_keyboard(message.chat.id))
        user_states.pop(message.chat.id, None)
    else:
        bot.send_message(message.chat.id, 
                        "❌ Задача не найдена. Выберите задачу из списка.")

@bot.message_handler(func=lambda message: message.text == '🧪 Выбрать тест')
def choose_test_handler(message):
    if message.chat.id not in user_data or 'task' not in user_data[message.chat.id]:
        bot.send_message(message.chat.id, 
                        "❌ Сначала выберите задачу через 'Выбрать задачу'")
        return
    
    task_number = user_data[message.chat.id]['task']
    tests = get_available_tests(task_number)
    
    if not tests:
        bot.send_message(message.chat.id, 
                        f"❌ Для задачи {task_number} нет доступных тестов.")
        return
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=5)
    test_buttons = [types.KeyboardButton(test) for test in tests[:15]]
    markup.add(*test_buttons)
    markup.add(types.KeyboardButton('↩️ Назад'))
    
    bot.send_message(message.chat.id,
                    f"Задача: {task_number}\nВыберите номер теста:",
                    reply_markup=markup)
    
    user_states[message.chat.id] = 'waiting_for_test_selection'

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'waiting_for_test_selection')
def handle_test_selection(message):
    if message.text == '↩️ Назад':
        bot.send_message(message.chat.id, "Главное меню:", 
                         reply_markup=show_main_keyboard(message.chat.id))
        user_states.pop(message.chat.id, None)
        return
    
    if message.chat.id not in user_data or 'task' not in user_data[message.chat.id]:
        bot.send_message(message.chat.id, "❌ Ошибка: задача не выбрана.")
        user_states.pop(message.chat.id, None)
        return
    
    task_number = user_data[message.chat.id]['task']
    test_number = message.text.strip()
    
    base_path = os.path.join(BASE_DATA_PATH, task_number, "tests", test_number)
    input_file = base_path
    output_file = base_path + ".a"
    comment_file = base_path + ".comment"
    
    if not os.path.exists(input_file):
        bot.send_message(message.chat.id, 
                        f"❌ Тест {test_number} для задачи {task_number} не найден.")
        return
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            input_data = f.read()
        
        output_data = ""
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                output_data = f.read()
        
        comment = ""
        if os.path.exists(comment_file):
            with open(comment_file, 'r', encoding='utf-8') as f:
                comment = f.read()
        
        response = f"📊 *Задача {task_number}, Тест {test_number}*\n\n"
        response += "```\n" + input_data + "\n```\n\n"
        
        if output_data:
            response += f"*Ожидаемый вывод:*\n```\n{output_data}\n```\n\n"
        
        if comment:
            response += f"*Комментарий преподавателя:*\n{comment}\n\n"
        
        if is_teacher(message.chat.id):
            markup = types.InlineKeyboardMarkup()
            btn_edit_comment = types.InlineKeyboardButton(
                "✏️ Редактировать комментарий", 
                callback_data=f"edit_comment:{task_number}:{test_number}"
            )
            markup.add(btn_edit_comment)
            bot.send_message(message.chat.id, response, 
                           parse_mode='Markdown', 
                           reply_markup=markup)
        else:
            bot.send_message(message.chat.id, response, parse_mode='Markdown')
            
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка при чтении теста: {str(e)}")

@bot.message_handler(func=lambda message: message.text == '💬 Добавить комментарий')
def add_comment_handler(message):
    """Обработчик добавления комментария (только для преподавателей)"""
    if not is_teacher(message.chat.id):
        bot.send_message(message.chat.id, "❌ Эта функция доступна только преподавателям.")
        return
    
    if message.chat.id not in user_data or 'task' not in user_data[message.chat.id]:
        bot.send_message(message.chat.id, 
                        "❌ Сначала выберите задачу через 'Выбрать задачу'")
        return
    
    task_number = user_data[message.chat.id]['task']
    tests = get_available_tests(task_number)
    
    if not tests:
        bot.send_message(message.chat.id, 
                        f"❌ Для задачи {task_number} нет доступных тестов.")
        return
    
    # Создаем клавиатуру с тестами для выбора
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=5)
    test_buttons = [types.KeyboardButton(test) for test in tests[:15]]
    markup.add(*test_buttons)
    markup.add(types.KeyboardButton('↩️ Назад'))
    
    bot.send_message(message.chat.id,
                    f"Задача: {task_number}\nВыберите номер теста для добавления комментария:",
                    reply_markup=markup)
    
    user_states[message.chat.id] = 'waiting_for_test_to_comment'

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'waiting_for_test_to_comment')
def handle_test_for_comment(message):
    if message.text == '↩️ Назад':
        bot.send_message(message.chat.id, "Главное меню:", 
                         reply_markup=show_main_keyboard(message.chat.id))
        user_states.pop(message.chat.id, None)
        return
    
    task_number = user_data[message.chat.id]['task']
    test_number = message.text.strip()
    
    input_file = os.path.join(BASE_DATA_PATH, task_number, "tests", test_number)
    
    if not os.path.exists(input_file):
        bot.send_message(message.chat.id, 
                        f"❌ Тест {test_number} для задачи {task_number} не найден.")
        return
    
    if 'comment_data' not in user_data[message.chat.id]:
        user_data[message.chat.id]['comment_data'] = {}
    user_data[message.chat.id]['comment_data']['task'] = task_number
    user_data[message.chat.id]['comment_data']['test'] = test_number
    
    # Проверяем, есть ли существующий комментарий
    comment_file = input_file + ".comment"
    existing_comment = ""
    if os.path.exists(comment_file):
        with open(comment_file, 'r', encoding='utf-8') as f:
            existing_comment = f.read()
    
    if existing_comment:
        bot.send_message(message.chat.id, 
                        f"📝 *Текущий комментарий к тесту {test_number}:*\n{existing_comment}\n\n"
                        f"Введите новый комментарий (или /cancel для отмены):",
                        parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, 
                        f"Введите комментарий для теста {test_number} (или /cancel для отмены):")
    
    user_states[message.chat.id] = 'waiting_for_comment_text'

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'waiting_for_comment_text')
def handle_comment_text(message):
    if message.text == '/cancel':
        bot.send_message(message.chat.id, "❌ Добавление комментария отменено.",
                         reply_markup=show_main_keyboard(message.chat.id))
        user_states.pop(message.chat.id, None)
        if 'comment_data' in user_data[message.chat.id]:
            del user_data[message.chat.id]['comment_data']
        return
    
    if 'comment_data' not in user_data[message.chat.id]:
        bot.send_message(message.chat.id, "❌ Ошибка: данные о тесте не найдены.")
        user_states.pop(message.chat.id, None)
        return
    
    task_number = user_data[message.chat.id]['comment_data']['task']
    test_number = user_data[message.chat.id]['comment_data']['test']
    comment_text = message.text
    
    # Сохраняем комментарий в файл
    try:
        comment_file = os.path.join(BASE_DATA_PATH, task_number, "tests", test_number + ".comment")
        
        with open(comment_file, 'w', encoding='utf-8') as f:
            f.write(comment_text)
        
        bot.send_message(message.chat.id, 
                        f"✅ Комментарий к тесту {test_number} (задача {task_number}) успешно сохранен!",
                        reply_markup=show_main_keyboard(message.chat.id))
        
        del user_data[message.chat.id]['comment_data']
        user_states.pop(message.chat.id, None)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка при сохранении комментария: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_comment:'))
def handle_edit_comment(call):
    """Обработчик редактирования комментария через inline-кнопку"""
    if not is_teacher(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Эта функция доступна только преподавателям.")
        return
    
    _, task_number, test_number = call.data.split(':')
    
    if call.from_user.id not in user_data:
        user_data[call.from_user.id] = {}
    user_data[call.from_user.id]['comment_data'] = {
        'task': task_number,
        'test': test_number
    }
    
    user_states[call.from_user.id] = 'waiting_for_comment_text'
    
    bot.send_message(call.from_user.id, 
                    f"Введите комментарий для теста {test_number} (задача {task_number}):\n"
                    f"(или /cancel для отмены)")
    
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda message: message.text == '📌 Текущая задача')
def show_current_task(message):
    if message.chat.id in user_data and 'task' in user_data[message.chat.id]:
        task_number = user_data[message.chat.id]['task']
        task_info = get_task_info(task_number)
        
        response = f"📌 *Текущая задача: {task_number}*\n\n"
        response += f"{task_info}\n\n"
        
        tests = get_available_tests(task_number)
        if tests:
            response += f"Доступно тестов: {len(tests)}"
        else:
            response += "Тесты отсутствуют"
        
        bot.send_message(message.chat.id, response, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "❌ Задача не выбрана.")

@bot.message_handler(commands=['cancel'])
def cancel_operation(message):
    """Отмена текущей операции"""
    if message.chat.id in user_states:
        bot.send_message(message.chat.id, "Операция отменена.",
                         reply_markup=show_main_keyboard(message.chat.id))
        user_states.pop(message.chat.id, None)
        
        if message.chat.id in user_data and 'comment_data' in user_data[message.chat.id]:
            del user_data[message.chat.id]['comment_data']
    else:
        bot.send_message(message.chat.id, "Нет активной операции для отмены.")

@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    """Обработка произвольных сообщений (номера задач/тестов напрямую)"""
    text = message.text.strip()
    
    if text.isdigit() and text in get_available_tasks():
        user_data[message.chat.id] = {'task': text}
        task_info = get_task_info(text)
        
        response = f"✅ *Задача {text} выбрана*\n\n"
        response += f"{task_info}\n\n"
        response += "Теперь выберите 'Выбрать тест' для просмотра тестов."
        
        bot.send_message(message.chat.id, response, 
                        parse_mode='Markdown',
                        reply_markup=show_main_keyboard(message.chat.id))
    else:
        bot.send_message(message.chat.id, 
                        "Используйте кнопки меню для навигации или введите номер доступной задачи.")

if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()