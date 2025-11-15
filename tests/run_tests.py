#!/usr/bin/env python3
"""Запуск всех тестов проекта"""

import pytest
import sys
import os

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Запускаем все тесты с разными опциями
    exit_code = pytest.main([
        "-v",
        "--tb=short", 
        "--cov=main",           # Покрытие для main.py
        "--cov=test_manager",   # Покрытие для test_manager.py
        "--cov-report=term-missing",
        "--cov-report=html",
        "tests/"
    ])
    
    print(f"\nТесты завершены с кодом: {exit_code}")
    sys.exit(exit_code)