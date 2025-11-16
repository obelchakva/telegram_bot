import pytest
from unittest.mock import Mock, patch
import main
from .test_fixes import get_mock_text


class TestErrorHandling:
    """Тесты обработки ошибок"""
    
    @patch('main.task_manager')
    @patch('main.bot')
    def test_error_in_get_test_data(self, mock_bot, mock_task_manager, mock_message):
        """Тест обработки ошибок при получении данных теста"""
        main.bot = mock_bot
        mock_task_manager.get_test_data.side_effect = Exception("Database error")
        
        mock_message.text = "1"
        
        main.get_test_number(mock_message, 1)
        
        mock_bot.send_message.assert_called_once()
        text = get_mock_text(mock_bot.send_message.call_args)
        assert "Ошибка" in text
    
    @patch('main.task_manager')
    @patch('main.bot')
    def test_error_in_comments_handling(self, mock_task_manager, mock_bot, mock_message):
        """Тест обработки ошибок при получении комментариев"""
        main.bot = mock_bot
        
        mock_test_data = {
            'input': "test",
            'output': "result", 
            'task_name': "Задача",
            'comments': []
        }
        
        def get_test_data_side_effect(task_id, test_number):
            return mock_test_data
            
        mock_task_manager.get_test_data.side_effect = get_test_data_side_effect
        mock_task_manager.get_comments.side_effect = Exception("Comments error")
        
        mock_message.text = "1"
        
        main.get_test_number(mock_message, 1)
        
        mock_bot.send_message.assert_called_once()
        text = get_mock_text(mock_bot.send_message.call_args)
        
        assert mock_bot.send_message.called
        assert "Тест найден" in text or "test" in text or "result" in text