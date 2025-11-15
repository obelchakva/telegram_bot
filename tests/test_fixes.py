"""Исправления для распространенных проблем в тестах"""
from typing import Any, Tuple

def get_mock_text(call_args):
    """
    Получает текст из аргументов mock вызова.
    Работает с разными форматами вызовов bot.send_message()
    """
    if not call_args:
        return ""
    
    # Позиционные аргументы: (chat_id, text, parse_mode, ...)
    if call_args[0] and len(call_args[0]) > 1:
        return call_args[0][1]
    
    # Именованные аргументы: {'chat_id': 123, 'text': 'message', 'parse_mode': 'Markdown'}
    if call_args[1] and 'text' in call_args[1]:
        return call_args[1]['text']
    
    return ""