import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main
from .test_fixes import get_mock_text


class TestMainIntegration:
    """Интеграционные тесты для main.py"""
    
    def setup_method(self):
        """Сброс состояния перед каждым тестом"""
        main.user_states = {}
    
    def test_check_cancel_commands(self):
        """Тест различных вариантов команды отмены"""
        message = Mock()
        
        # Тестируем разные варианты написания
        test_cases = [
            "/cancel", "/CANCEL", "/Cancel", " /cancel ", 
            "/cancel extra", "something /cancel"
        ]
        
        for text in test_cases:
            message.text = text
            # Должно возвращать True только для чистых команд
            result = main.check_cancel(message)
            expected = text.strip().lower() == "/cancel"
            assert result == expected, f"Failed for: '{text}'"
    
    @patch('main.task_manager')
    def test_get_task_number_valid(self, mock_task_manager, mock_bot, mock_message):
        """Тест обработки валидного номера задачи"""
        main.bot = mock_bot
        mock_task_manager.task_exists.return_value = True
        mock_task_manager.get_available_tests.return_value = ["1", "2"]
        
        mock_message.text = "1"
        main.get_task_number(mock_message)
        
        mock_bot.send_message.assert_called_once()
        mock_bot.register_next_step_handler.assert_called_once()
    
    @patch('main.task_manager')
    @patch('main.bot')
    def test_get_task_number_invalid(self, mock_bot, mock_task_manager, mock_message):
        """Тест обработки невалидного номера задачи"""
        mock_task_manager.task_exists.return_value = False
        mock_task_manager.get_available_tasks.return_value = ["1 - Задача 1"]
        
        mock_message.text = "999"  # Несуществующая задача
        main.get_task_number(mock_message)
        
        # Должен запросить корректный номер
        assert mock_bot.send_message.called
        # ЗАМЕНИТЕ:
        # assert "не найдена" in mock_bot.send_message.call_args[1]['text']
        # НА:
        text = get_mock_text(mock_bot.send_message.call_args)
        assert "не найдена" in text
    
    @patch('main.task_manager')
    @patch('main.bot')
    def test_get_test_number_success(self, mock_task_manager, mock_bot, mock_message):
        """Тест успешного получения данных теста"""
        main.bot = mock_bot
        mock_task_manager.get_test_data.return_value = {
            'input': "5\n3",
            'output': "8",
            'task_name': "Сумма", 
            'comments': []
        }
        
        mock_message.text = "1"
        main.get_test_number(mock_message, 1)
        
        mock_bot.send_message.assert_called_once()
        # ИСПРАВЬТЕ:
        # assert "Тест найден" in kwargs['text']
        # НА:
        text = get_mock_text(mock_bot.send_message.call_args)
        assert "Тест найден" in text

    @patch('main.task_manager')
    @patch('main.bot') 
    def test_get_test_number_with_comments(self, mock_task_manager, mock_bot, mock_message):
        """Тест получения теста с комментариями"""
        main.bot = mock_bot
        mock_task_manager.get_test_data.return_value = {
            'input': "test",
            'output': "result",
            'task_name': "Задача",
            'comments': [
                {'author': 'Преподаватель', 'text': 'Хороший тест!'}
            ]
        }
        mock_task_manager.get_comments.return_value = [
            {'author': 'Преподаватель', 'text': 'Хороший тест!'}
        ]
        
        mock_message.text = "1"
        main.get_test_number(mock_message, 1)
        
        # ИСПРАВЬТЕ:
        # assert "Комментарии" in kwargs['text']
        # НА:
        text = get_mock_text(mock_bot.send_message.call_args)
        assert "Комментарии" in text

    @patch('main.bot')
    def test_get_test_number_not_found(self, mock_bot, mock_message):
        """Тест обработки несуществующего теста"""
        main.bot = mock_bot
        
        print("=== НАЧАЛО ТЕСТА ===")
        
        # Используем patch как context manager внутри теста
        with patch('main.task_manager') as mock_task_manager:
            # Настраиваем мок
            mock_task_manager.get_test_data.return_value = None
            mock_task_manager.get_available_tests.return_value = ["1", "2", "3"]
            mock_task_manager.get_comments.return_value = []
            
            print(f"get_test_data настроен: {mock_task_manager.get_test_data.return_value}")
            
            mock_message.text = "999"
            print("Вызываем get_test_number...")
            main.get_test_number(mock_message, 1)
        
        print("Проверяем вызовы...")
        assert mock_bot.send_message.called, "send_message не был вызван!"
        
        call_args = mock_bot.send_message.call_args
        text = call_args[0][1] if len(call_args[0]) > 1 else call_args[1].get('text', '')
        
        print(f"Текст сообщения: {text}")
        print("=== КОНЕЦ ТЕСТА ===")
        
        # Проверяем, что в ответе есть сообщение об ошибке
        assert "Тест не найден" in text, f"Текст не содержит сообщения об ошибке: {text}"

    @patch('main.bot')
    def test_admin_password_flow(self, mock_bot):
        """Тест потока ввода пароля администратора"""
        message = Mock()
        message.chat.id = 12345
        message.text = "101003"  # Правильный пароль
        
        main.check_admin_password(message)
        
        mock_bot.send_message.assert_called_once()
        # ИСПРАВЬТЕ:
        # assert "Команды для преподавателей" in kwargs['text']
        # НА:
        text = get_mock_text(mock_bot.send_message.call_args)
        assert "Команды для преподавателей" in text

    @patch('main.bot')
    def test_admin_password_wrong(self, mock_bot):
        """Тест неправильного пароля администратора"""
        message = Mock()
        message.chat.id = 12345
        message.text = "wrong_password"
        
        main.check_admin_password(message)
        
        mock_bot.send_message.assert_called_once()
        # ИСПРАВЬТЕ:
        # assert "Неверный пароль" in mock_bot.send_message.call_args[1]['text']
        # НА:
        text = get_mock_text(mock_bot.send_message.call_args)
        assert "Неверный пароль" in text
    
    @patch('main.task_manager')
    @patch('main.bot') 
    def test_get_test_number_with_comments(self, mock_task_manager, mock_bot, mock_message):
        """Тест получения теста с комментариями"""
        main.bot = mock_bot
        mock_task_manager.get_test_data.return_value = {
            'input': "test",
            'output': "result",
            'task_name': "Задача",
            'comments': [
                {'author': 'Преподаватель', 'text': 'Хороший тест!'}
            ]
        }
        mock_task_manager.get_comments.return_value = [
            {'author': 'Преподаватель', 'text': 'Хороший тест!'}
        ]
        
        mock_message.text = "1"
        main.get_test_number(mock_message, 1)
        
        # ИСПРАВЬТЕ:
        # assert "Комментарии" in kwargs['text']
        # НА:
        text = get_mock_text(mock_bot.send_message.call_args)
        assert "Комментарии" in text


    def test_user_states_management(self):
        """Тест управления состоянием пользователей"""
        # Имитируем добавление состояния
        test_user_id = 12345
        test_state = {'action': 'upload', 'auth': True}
        
        main.user_states[test_user_id] = test_state
        
        # Проверяем, что состояние сохранилось
        assert test_user_id in main.user_states
        assert main.user_states[test_user_id] == test_state
        
        # Имитируем удаление состояния
        main.user_states.pop(test_user_id, None)
        assert test_user_id not in main.user_states
    
 
    @patch('main.bot')
    def test_admin_password_flow(self, mock_bot):
        """Тест потока ввода пароля администратора"""
        message = Mock()
        message.chat.id = 12345
        message.text = "101003"  # Правильный пароль
        
        main.check_admin_password(message)
        
        mock_bot.send_message.assert_called_once()
        # ИСПРАВЬТЕ:
        # assert "Команды для преподавателей" in kwargs['text']
        # НА:
        text = get_mock_text(mock_bot.send_message.call_args)
        assert "Команды для преподавателей" in text

    @patch('main.bot')
    def test_admin_password_wrong(self, mock_bot):
        """Тест неправильного пароля администратора"""
        message = Mock()
        message.chat.id = 12345
        message.text = "wrong_password"
        
        main.check_admin_password(message)
        
        mock_bot.send_message.assert_called_once()
        # ИСПРАВЬТЕ:
        # assert "Неверный пароль" in mock_bot.send_message.call_args[1]['text']
        # НА:
        text = get_mock_text(mock_bot.send_message.call_args)
        assert "Неверный пароль" in text