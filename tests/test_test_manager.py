import pytest
import json
import os
import sqlite3
from task_manager import TaskManager


class TestTaskManager:
    """Тесты для класса TaskManager"""
    
    def test_init_database(self, task_manager, temp_db):
        """Тест инициализации базы данных"""
        # Проверяем, что таблицы созданы
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        
        # Проверяем существование таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'tasks' in tables
        assert 'tests' in tables
        assert 'comments' in tables
        
        conn.close()
    
    def test_load_from_json_success(self, task_manager, sample_json_data):
        """Тест успешной загрузки данных из JSON"""
        json_content = json.dumps(sample_json_data)
        success, message = task_manager.load_from_json(json_content)
        
        assert success is True
        assert "успешно загружена" in message
        
        # Проверяем, что данные действительно добавлены
        stats = task_manager.get_task_stats(1)
        assert stats is not None
        assert stats['test_count'] == 2
    
    def test_load_from_json_invalid_json(self, task_manager):
        """Тест загрузки с невалидным JSON"""
        success, message = task_manager.load_from_json("invalid json")
        
        assert success is False
        assert "Ошибка загрузки" in message
    
    def test_load_from_json_missing_fields(self, task_manager):
        """Тест загрузки JSON с отсутствующими полями"""
        invalid_data = {"task_id": 1}  # Нет tests
        success, message = task_manager.load_from_json(json.dumps(invalid_data))
        
        assert success is False
    
    def test_add_comment_success(self, task_manager, sample_json_data):
        """Тест успешного добавления комментария"""
        # Сначала загружаем тестовые данные
        task_manager.load_from_json(json.dumps(sample_json_data))
        
        success, message = task_manager.add_comment(1, 1, "Отличный тест!", "Преподаватель")
        
        assert success is True
        assert "Комментарий добавлен" in message
        
        # Проверяем, что комментарий действительно добавлен
        comments = task_manager.get_comments(1, 1)
        assert len(comments) == 1
        assert comments[0]['text'] == "Отличный тест!"
    
    def test_add_comment_to_nonexistent_test(self, task_manager):
        """Тест добавления комментария к несуществующему тесту"""
        success, message = task_manager.add_comment(999, 1, "Комментарий")
        
        assert success is False
        assert "не найден" in message
    
    def test_get_comments_with_ids(self, task_manager, sample_json_data):
        """Тест получения комментариев с ID"""
        task_manager.load_from_json(json.dumps(sample_json_data))
        task_manager.add_comment(1, 1, "Первый комментарий")
        task_manager.add_comment(1, 1, "Второй комментарий")
        
        comments = task_manager.get_comments_with_ids(1, 1)
        
        assert len(comments) == 2
        assert 'id' in comments[0]
        assert comments[0]['text'] == "Первый комментарий"
        assert comments[1]['text'] == "Второй комментарий"
    
    def test_delete_comment_success(self, task_manager, sample_json_data):
        """Тест успешного удаления комментария"""
        task_manager.load_from_json(json.dumps(sample_json_data))
        task_manager.add_comment(1, 1, "Комментарий для удаления")
        
        # Получаем ID комментария
        comments = task_manager.get_comments_with_ids(1, 1)
        comment_id = comments[0]['id']
        
        success, message = task_manager.delete_comment(comment_id)
        
        assert success is True
        assert "Комментарий удален" in message
        
        # Проверяем, что комментарий удален
        comments_after = task_manager.get_comments(1, 1)
        assert len(comments_after) == 0
    
    def test_delete_nonexistent_comment(self, task_manager):
        """Тест удаления несуществующего комментария"""
        success, message = task_manager.delete_comment(999)
        
        assert success is False
        assert "не найден" in message
    
    def test_delete_all_comments(self, task_manager, sample_json_data):
        """Тест удаления всех комментариев для теста"""
        task_manager.load_from_json(json.dumps(sample_json_data))
        task_manager.add_comment(1, 1, "Комментарий 1")
        task_manager.add_comment(1, 1, "Комментарий 2")
        
        success, message = task_manager.delete_all_comments(1, 1)
        
        assert success is True
        assert "Удалено комментариев: 2" in message
        
        comments = task_manager.get_comments(1, 1)
        assert len(comments) == 0
    
    def test_get_test_data_with_comments(self, task_manager, sample_json_data):
        """Тест получения данных теста с комментариями"""
        task_manager.load_from_json(json.dumps(sample_json_data))
        task_manager.add_comment(1, 1, "Тестовый комментарий")
        
        test_data = task_manager.get_test_data(1, 1)
        
        assert test_data is not None
        assert test_data['input'] == "5\n3"
        assert test_data['output'] == "8"
        assert len(test_data['comments']) == 1
        assert test_data['comments'][0]['text'] == "Тестовый комментарий"
    
    def test_get_test_data_nonexistent(self, task_manager):
        """Тест получения данных несуществующего теста"""
        test_data = task_manager.get_test_data(999, 1)
        
        assert test_data is None
    
    def test_get_available_tasks(self, task_manager, sample_json_data):
        """Тест получения списка задач"""
        task_manager.load_from_json(json.dumps(sample_json_data))
        
        tasks = task_manager.get_available_tasks()
        
        assert len(tasks) == 1
        assert "1 - Тестовая задача" in tasks[0]
    
    def test_get_available_tests(self, task_manager, sample_json_data):
        """Тест получения списка тестов для задачи"""
        task_manager.load_from_json(json.dumps(sample_json_data))
        
        tests = task_manager.get_available_tests(1)
        
        assert len(tests) == 2
        assert "1" in tests
        assert "2" in tests
    
    def test_task_exists(self, task_manager, sample_json_data):
        """Тест проверки существования задачи"""
        task_manager.load_from_json(json.dumps(sample_json_data))
        
        assert task_manager.task_exists(1) is True
        assert task_manager.task_exists(999) is False
    
    def test_get_task_name(self, task_manager, sample_json_data):
        """Тест получения названия задачи"""
        task_manager.load_from_json(json.dumps(sample_json_data))
        
        task_name = task_manager.get_task_name(1)
        assert task_name == "Тестовая задача"
        
        # Для несуществующей задачи
        task_name_nonexistent = task_manager.get_task_name(999)
        assert "Задача 999" in task_name_nonexistent
    
    def test_delete_task_success(self, task_manager, sample_json_data):
        """Тест успешного удаления задачи"""
        task_manager.load_from_json(json.dumps(sample_json_data))
        
        success, message = task_manager.delete_task(1)
        
        assert success is True
        assert "удалена" in message
        assert task_manager.task_exists(1) is False
    
    def test_delete_nonexistent_task(self, task_manager):
        """Тест удаления несуществующей задачи"""
        success, message = task_manager.delete_task(999)
        
        assert success is False
        assert "не найдена" in message
    
    def test_get_task_stats(self, task_manager, sample_json_data):
        """Тест получения статистики по задаче"""
        task_manager.load_from_json(json.dumps(sample_json_data))
        
        stats = task_manager.get_task_stats(1)
        
        assert stats is not None
        assert stats['task_name'] == "Тестовая задача"
        assert stats['test_count'] == 2
    
    def test_get_task_stats_nonexistent(self, task_manager):
        """Тест получения статистики по несуществующей задаче"""
        stats = task_manager.get_task_stats(999)
        
        assert stats is None
    
    def test_load_from_json_with_custom_task_id(self, task_manager):
        """Тест загрузки JSON с указанием task_id"""
        json_data = {
            "tests": {
                "1": {"input": "test", "output": "result"}
            }
        }
        
        success, message = task_manager.load_from_json(
            json.dumps(json_data), 
            task_id=5
        )
        
        assert success is True
        assert task_manager.task_exists(5) is True