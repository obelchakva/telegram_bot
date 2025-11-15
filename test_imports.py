#!/usr/bin/env python3
"""Проверка импортов"""

import sys
import os

def test_imports():
    print("Проверка импортов...")
    
    # Добавляем текущую директорию в путь
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    try:
        # Пробуем импортировать task_manager
        from task_manager import TaskManager
        print("✅ task_manager импортирован успешно")
        
        # Пробуем создать экземпляр
        manager = TaskManager(':memory:')
        print("✅ TaskManager создан успешно")
        
        # Пробуем импортировать main
        import main
        print("✅ main импортирован успешно")
        
        print("\n🎉 Все импорты работают!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)