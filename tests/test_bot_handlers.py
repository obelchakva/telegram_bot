import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main
from .test_fixes import get_mock_text


class TestBotHandlers:
    """Тесты обработчиков бота"""
    
    def setup_method(self):
        """Сброс состояния перед каждым тестом"""
        main.user_states = {}
    
    @patch('main.bot')
    def test_send_welcome(self, mock_bot, mock_message):
        """Тест команды /start"""
        main.send_welcome(mock_message)
        
        mock_bot.send_message.assert_called_once()
        text = get_mock_text(mock_bot.send_message.call_args)
        assert "Бот помощи с задачами" in text
    
    @patch('main.bot')
    def test_check_cancel_true(self, mock_bot, mock_message):
        """Тест проверки отмены - True"""
        mock_message.text = "/cancel"
        result = main.check_cancel(mock_message)
        assert result is True
        
        mock_bot.send_message.assert_called_once()
        text = get_mock_text(mock_bot.send_message.call_args)
        assert "Действие отменено" in text
    
    def test_check_cancel_false(self, mock_message):
        """Тест проверки отмены - False"""
        mock_message.text = "другой текст"
        result = main.check_cancel(mock_message)
        assert result is False
    
    @patch('main.bot')
    def test_show_tasks(self, mock_bot, mock_message, task_manager):
        """Тест команды /tasks"""
        main.task_manager = task_manager
        
        json_data = {
            "task_id": 1,
            "task_name": "Тестовая задача",
            "tests": {"1": {"input": "test", "output": "result"}}
        }
        task_manager.load_from_json(json.dumps(json_data))
        
        main.show_tasks(mock_message)
        
        mock_bot.send_message.assert_called_once()
        text = get_mock_text(mock_bot.send_message.call_args)
        assert "Доступные задачи" in text
        assert "1 - Тестовая задача" in text
    
    @patch('main.bot')
    def test_show_tasks_empty(self, mock_bot, mock_message, task_manager):
        """Тест команды /tasks когда нет задач"""
        main.task_manager = task_manager
        
        main.show_tasks(mock_message)
        
        mock_bot.send_message.assert_called_once()
        text = get_mock_text(mock_bot.send_message.call_args)
        assert "Нет доступных задач" in text
    
    @patch('main.task_manager')
    @patch('main.bot')
    def test_start_help(self, mock_bot, mock_task_manager, mock_message):
        """Тест начала процесса помощи"""
        mock_task_manager.get_available_tasks.return_value = ["1 - Задача 1", "2 - Задача 2"]
        
        main.start_help(mock_message)
        
        mock_bot.send_message.assert_called_once()
        mock_bot.register_next_step_handler.assert_called_once()
    
    @patch('main.task_manager')
    @patch('main.bot')
    def test_start_help_no_tasks(self, mock_bot, mock_task_manager, mock_message):
        """Тест начала помощи когда нет задач"""
        mock_task_manager.get_available_tasks.return_value = []
        
        main.start_help(mock_message)
        
        mock_bot.send_message.assert_called_once()
        text = get_mock_text(mock_bot.send_message.call_args)
        assert "Нет доступных задач" in text
    
    @patch('main.bot')
    def test_handle_text_unknown(self, mock_bot, mock_message):
        """Тест обработки неизвестного текста"""
        mock_message.text = "неизвестная команда"
        
        main.handle_text(mock_message)
        
        mock_bot.send_message.assert_called_once()
        text = get_mock_text(mock_bot.send_message.call_args)
        assert "Не понимаю ваше сообщение" in text
    
    @patch('main.bot')
    def test_handle_text_hello(self, mock_bot, mock_message):
        """Тест обработки приветствия"""
        mock_message.text = "привет"
        
        main.handle_text(mock_message)
        
        mock_bot.send_message.assert_called_once()
        text = get_mock_text(mock_bot.send_message.call_args)
        assert "Привет! Используйте /start" in text