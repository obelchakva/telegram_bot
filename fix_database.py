import sqlite3

def fix_database():
    """Удаляет задачу с ID 0 из базы"""
    conn = sqlite3.connect('tests.db')
    cursor = conn.cursor()
    
    # Удаляем тесты задачи 0
    cursor.execute('DELETE FROM tests WHERE task_id = 0')
    tests_deleted = cursor.rowcount
    
    # Удаляем саму задачу 0
    cursor.execute('DELETE FROM tasks WHERE task_id = 0')
    task_deleted = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    print(f"✅ Удалено: задача 0 ({task_deleted}), тестов ({tests_deleted})")

if __name__ == "__main__":
    fix_database()