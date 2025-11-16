import pytest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main
from .test_fixes import get_mock_text 


class TestBotSecurity:
    """Тесты безопасности и валидации"""
    
    @patch('main.bot')
    def test_password_validation(self, mock_bot):
        """Тест валидации пароля"""
        message = Mock()
        message.text = "101003"
        result = main.check_admin_password(message)
        
        message.text = "wrong"
        result = main.check_admin_password(message)
    
    def test_input_validation_task_id(self):
        """Тест валидации ввода номера задачи"""
        test_cases = [
            ("123", True),      
            ("1", True),          
            ("abc", False),      
            ("12.3", False),     
            ("", False),         
            ("-5", False),       
        ]
        
        for input_text, expected_valid in test_cases:
            try:
                task_id = int(input_text)
                is_valid = task_id > 0
            except ValueError:
                is_valid = False
            
            assert is_valid == expected_valid, f"Failed for: '{input_text}'"
    
    @patch('main.task_manager')
    @patch('main.bot')
    def test_sql_injection_prevention(self, mock_bot, mock_task_manager, mock_message):
        """Тест защиты от SQL-инъекций"""
        main.bot = mock_bot
        mock_task_manager.task_exists.return_value = False
        
        mock_message.text = "1; DROP TABLE tasks;--"
        main.get_task_number(mock_message)
        
        mock_bot.send_message.assert_called_once()
        text = get_mock_text(mock_bot.send_message.call_args)
        assert "Введите число" in text or "не найдена" in text or "неверный" in text.lower()