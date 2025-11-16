import pytest
import sqlite3
import os
import tempfile
import sys
from unittest.mock import Mock, MagicMock, patch

# Добавляем путь к корневой папке проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from task_manager import TaskManager
import main


@pytest.fixture
def temp_db():
    """Создает временную базу данных для тестов"""
    fd, temp_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    yield temp_path
    
    # Удаляем временный файл после тестов
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def task_manager(temp_db):
    """Создает экземпляр TaskManager с временной БД"""
    return TaskManager(temp_db)


@pytest.fixture
def sample_json_data():
    """Пример JSON данных для тестов"""
    return {
        "task_id": 1,
        "task_name": "Тестовая задача",
        "tests": {
            "1": {
                "input": "5\n3",
                "output": "8"
            },
            "2": {
                "input": "10\n20",
                "output": "30"
            }
        }
    }


@pytest.fixture
def mock_bot():
    """Мок объекта бота"""
    bot = Mock()
    bot.send_message = Mock()
    return bot


@pytest.fixture
def mock_message():
    """Мок сообщения"""
    message = Mock()
    message.chat = Mock()
    message.chat.id = 12345
    message.text = ""
    return message

@pytest.fixture
def mock_telebot():
    """Мок для telebot модуля"""
    with patch('main.telebot') as mock_tb:
        mock_bot = Mock()
        mock_tb.TeleBot.return_value = mock_bot
        yield mock_tb


@pytest.fixture(autouse=True)
def reset_global_state():
    """Автоматически сбрасывает глобальное состояние перед каждым тестом"""
    original_states = getattr(main, 'user_states', {})
    yield
    # Восстанавливаем оригинальное состояние
    main.user_states = original_states.copy() if hasattr(main, 'user_states') else {}


def get_message_text(call_args):
    """Извлекает текст сообщения из аргументов вызова mock бота"""
    if call_args[0]:  # позиционные аргументы (chat_id, text, ...)
        return call_args[0][1] if len(call_args[0]) > 1 else ""
    else:  # именованные аргументы
        return call_args[1].get('text', '')
