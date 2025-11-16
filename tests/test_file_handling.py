import pytest
from unittest.mock import Mock, patch
import main
from .test_fixes import get_mock_text


class TestFileHandling:
    """Тесты обработки файлов"""
    
    @patch('main.task_manager')
    def test_document_handling_json(self, mock_task_manager, mock_bot):
        """Тест обработки JSON файлов"""
        main.bot = mock_bot
        main.user_states[12345] = {'auth': True, 'action': 'upload'}
        
        message = Mock()
        message.chat.id = 12345
        message.document = Mock()
        message.document.file_name = "tests.json"
        
        mock_file_info = Mock()
        mock_file_info.file_path = "test/path"
        mock_bot.get_file.return_value = mock_file_info
        mock_bot.download_file.return_value = b'{"task_id": 1, "tests": {}}'
        
        mock_task_manager.load_from_json.return_value = (True, "Успешно")
        
        main.handle_document(message)
        
        mock_task_manager.load_from_json.assert_called_once()
        mock_bot.send_message.assert_called_once_with(12345, "Успешно")
    
    @patch('main.task_manager')
    def test_document_handling_non_json(self, mock_task_manager, mock_bot):
        """Тест обработки не-JSON файлов"""
        main.bot = mock_bot
        main.user_states[12345] = {'auth': True, 'action': 'upload'}
        
        message = Mock()
        message.chat.id = 12345
        message.document.file_name = "tests.txt"  
        
        main.handle_document(message)
        
        mock_bot.send_message.assert_called_once_with(12345, "Файл должен быть в формате JSON")
    
    def test_document_handling_unauthorized(self, mock_bot):
        """Тест обработки файлов без авторизации"""
        main.bot = mock_bot
        main.user_states = {}  
        
        message = Mock()
        message.chat.id = 12345
        message.document = Mock()
        
        main.handle_document(message)
        
        mock_bot.send_message.assert_called_once_with(12345, "Сначала получите доступ через /upload")