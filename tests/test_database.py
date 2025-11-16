import pytest
import sqlite3
import json
from task_manager import TaskManager


class TestDatabaseOperations:
    """Тесты операций с базой данных"""
    
    def test_database_schema(self, task_manager, temp_db):
        """Тест структуры базы данных"""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(tasks)")
        tasks_columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        assert 'task_id' in tasks_columns
        assert 'task_name' in tasks_columns
        assert tasks_columns['task_id'] == 'INTEGER'
        
        cursor.execute("PRAGMA table_info(tests)")
        tests_columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        assert 'task_id' in tests_columns
        assert 'test_number' in tests_columns
        assert 'input_data' in tests_columns
        assert 'expected_output' in tests_columns
        
        conn.close()
    
    def test_unique_constraint(self, task_manager):
        """Тест уникальности комбинации task_id и test_number"""
        json_data = {
            "task_id": 1,
            "task_name": "Тестовая задача",
            "tests": {
                "1": {"input": "test1", "output": "result1"},
                "1": {"input": "test2", "output": "result2"}
            }
        }
        
        success, message = task_manager.load_from_json(json.dumps(json_data))
        
        tests = task_manager.get_available_tests(1)
        assert len(tests) == 1
    
    def test_foreign_key_constraint(self, task_manager):
        """Тест ограничений внешнего ключа"""
        # Пытаемся добавить комментарий к несуществующей задаче
        success, message = task_manager.add_comment(999, 1, "Комментарий")
        
        assert success is False
        assert "не найден" in message
    
    def test_cascade_operations(self, task_manager):
        """Тест каскадных операций"""
        json_data = {
            "task_id": 1,
            "task_name": "Тестовая задача", 
            "tests": {
                "1": {"input": "test", "output": "result"}
            }
        }
        task_manager.load_from_json(json.dumps(json_data))
        
        task_manager.add_comment(1, 1, "Тестовый комментарий")
        
        task_manager.delete_task(1)
        
        # Проверяем, что все связанные данные удалены
        assert task_manager.task_exists(1) is False
        assert task_manager.get_test_data(1, 1) is None
        
        comments = task_manager.get_comments(1, 1)
        print(f"Комментарии после удаления задачи: {comments}")
    
    def test_indexes_exist(self, task_manager, temp_db):
        """Тест существования индексов"""
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in cursor.fetchall()]
        
        assert 'idx_task_id' in indexes
        assert 'idx_comments_task_test' in indexes
        
        conn.close()