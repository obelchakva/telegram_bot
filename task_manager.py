import os
import json
import sqlite3

class TaskManager:
    def __init__(self, db_path='tests.db'):
        self.db_path = db_path
        self.init_database()
    

    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Таблица для задач
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                task_id INTEGER PRIMARY KEY,
                task_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица для тестов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                test_number INTEGER,
                input_data TEXT,
                expected_output TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks (task_id),
                UNIQUE(task_id, test_number)
            )
        ''')

        #Таблица для комментариев
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                test_number INTEGER,
                comment_text TEXT,
                author TEXT DEFAULT 'Преподаватель',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks (task_id),
                FOREIGN KEY (task_id, test_number) REFERENCES tests (task_id, test_number)
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_id ON tests(task_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_task_test ON comments(task_id, test_number)')
        conn.commit()
        conn.close()
    

    def load_from_json(self, json_content, task_id=None):
        """Загрузка тестов из JSON"""
        try:
            data = json.loads(json_content)
            
            # Если task_id не указан, берем из JSON
            if task_id is None:
                task_id = data['task_id']
            
            task_name = data.get('task_name', f'Задача {task_id}')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Добавляем задачу
            cursor.execute('''
                INSERT OR REPLACE INTO tasks (task_id, task_name) 
                VALUES (?, ?)
            ''', (task_id, task_name))
            
            # Добавляем тесты
            for test_num, test_data in data['tests'].items():
                cursor.execute('''
                    INSERT OR REPLACE INTO tests 
                    (task_id, test_number, input_data, expected_output) 
                    VALUES (?, ?, ?, ?)
                ''', (task_id, int(test_num), test_data['input'], test_data['output']))
            
            conn.commit()
            conn.close()
            
            return True, f"Задача {task_id} успешно загружена! Добавлено {len(data['tests'])} тестов."
            
        except Exception as e:
            return False, f"Ошибка загрузки: {str(e)}"
    

    def add_comment(self, task_id, test_number, comment_text, author="Преподаватель"):
        """Добавляем комментарий к тесту"""
        try:
            # Проверяем существование теста
            if not self.get_test_data(task_id, test_number):
                return False, f"Тест {test_number} для задачи {task_id} не найден"
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Добавляем комментарий
            cursor.execute('''
                INSERT INTO comments (task_id, test_number, comment_text, author)
                VALUES (?, ?, ?, ?)
            ''', (task_id, test_number, comment_text, author))
            
            conn.commit()
            conn.close()
            
            return True, f"Комментарий добавлен к задаче {task_id}, тест {test_number}"
            
        except Exception as e:
            return False, f"Ошибка добавления комментария: {str(e)}"


    def get_comments(self, task_id, test_number):
        """Получаем все комментарии для теста"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT comment_text, author, created_at 
            FROM comments 
            WHERE task_id = ? AND test_number = ?
            ORDER BY created_at
        ''', (task_id, test_number))
        
        comments = []
        for row in cursor.fetchall():
            comments.append({
                'text': row[0],
                'author': row[1],
                'created_at': row[2]
            })
        
        conn.close()
        return comments
    

    def get_comments_with_ids(self, task_id, test_number):
        """Получаем все комментарии для теста с их ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, comment_text, author, created_at 
            FROM comments 
            WHERE task_id = ? AND test_number = ?
            ORDER BY created_at
        ''', (task_id, test_number))
        
        comments = []
        for row in cursor.fetchall():
            comments.append({
                'id': row[0],
                'text': row[1],
                'author': row[2],
                'created_at': row[3]
            })
        
        conn.close()
        return comments


    def delete_comment(self, comment_id):
        """Удаляем комментарий по ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Сначала получаем информацию о комментарии для сообщения
            cursor.execute('''
                SELECT task_id, test_number, comment_text 
                FROM comments 
                WHERE id = ?
            ''', (comment_id,))
            
            comment_info = cursor.fetchone()
            if not comment_info:
                return False, "Комментарий не найден"
            
            task_id, test_number, comment_text = comment_info
            
            # Удаляем комментарий
            cursor.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
            conn.commit()
            conn.close()
            
            return True, f"Комментарий удален (Задача {task_id}, тест {test_number})"
            
        except Exception as e:
            return False, f"Ошибка удаления комментария: {str(e)}"


    def delete_all_comments(self, task_id, test_number):
        """Удаляем все комментарии для теста"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM comments 
                WHERE task_id = ? AND test_number = ?
            ''', (task_id, test_number))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            return True, f"Удалено комментариев: {deleted_count} (Задача {task_id}, тест {test_number})"
            
        except Exception as e:
            return False, f"Ошибка удаления комментариев: {str(e)}"


    def get_test_data(self, task_id, test_number):
        """Получаем данные теста с комментариями"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT t.input_data, t.expected_output, ts.task_name
            FROM tests t
            JOIN tasks ts ON t.task_id = ts.task_id
            WHERE t.task_id = ? AND t.test_number = ?
        ''', (task_id, test_number))
        
        result = cursor.fetchone()
        
        if result:

            comments = self.get_comments(task_id, test_number)
            
            test_data = {
                'input': result['input_data'],
                'output': result['expected_output'],
                'task_name': result['task_name'],
                'comments': comments
            }
        else:
            test_data = None
        
        conn.close()
        return test_data
    

    def get_available_tasks(self):
        """Список всех доступных задач"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT task_id, task_name FROM tasks ORDER BY task_id')
        tasks = [f"{row[0]} - {row[1]}" for row in cursor.fetchall()]
        
        conn.close()
        return tasks
    

    def get_available_tests(self, task_id):
        """Список доступных тестов для задачи"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT test_number FROM tests 
            WHERE task_id = ? 
            ORDER BY test_number
        ''', (task_id,))
        
        tests = [str(row[0]) for row in cursor.fetchall()]
        conn.close()
        return tests


    def task_exists(self, task_id):
        """Проверяем, существует ли задача"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT 1 FROM tasks WHERE task_id = ?', (task_id,))
        exists = cursor.fetchone() is not None
        
        conn.close()
        return exists
    

    def get_task_name(self, task_id):
        """Получаем название задачи"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT task_name FROM tasks WHERE task_id = ?', (task_id,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else f"Задача {task_id}"


    def delete_task(self, task_id):
        """Удаляем задачу и все её тесты"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Получаем информацию о задаче для сообщения
            cursor.execute('SELECT task_name FROM tasks WHERE task_id = ?', (task_id,))
            task_info = cursor.fetchone()
            task_name = task_info[0] if task_info else f"Задача {task_id}"
            
            # Удаляем тесты
            cursor.execute('DELETE FROM tests WHERE task_id = ?', (task_id,))
            tests_deleted = cursor.rowcount
            
            # Удаляем задачу
            cursor.execute('DELETE FROM tasks WHERE task_id = ?', (task_id,))
            task_deleted = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            if task_deleted > 0:
                return True, f"Задача {task_id} - '{task_name}' удалена!\nУдалено тестов: {tests_deleted}"
            else:
                return False, f"Задача {task_id} не найдена."
                
        except Exception as e:
            return False, f"Ошибка при удалении: {str(e)}"


    def get_task_stats(self, task_id):
        """Получаем статистику по задаче"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                t.task_name,
                COUNT(ts.test_number) as test_count
            FROM tasks t
            LEFT JOIN tests ts ON t.task_id = ts.task_id
            WHERE t.task_id = ?
            GROUP BY t.task_id
        ''', (task_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'task_name': result[0],
                'test_count': result[1]
            }
        return None