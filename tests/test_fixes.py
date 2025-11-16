"""Исправления для распространенных проблем в тестах"""
from typing import Any, Tuple

def get_mock_text(call_args):
    """
    Получает текст из аргументов mock вызова.
    Работает с разными форматами вызовов bot.send_message()
    """
    if not call_args:
        return ""
    
    if call_args[0] and len(call_args[0]) > 1:
        return call_args[0][1]
    
    if call_args[1] and 'text' in call_args[1]:
        return call_args[1]['text']
    
    return ""