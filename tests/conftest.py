# tests/conftest.py
import pytest
import sys
import os

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine import GameState


class MockDictionary:
    """Мок словаря для тестирования"""
    def __init__(self, words=None):
        self.words = set(words) if words else {
            'СЛОВО', 'ДЕЛО', 'КИНО', 'ТЕСТ', 'КОТ', 'ДОМ', 
            'СТОЛ', 'РЕКА', 'МОРЕ', 'ВОДА', 'ИГРА'
        }
    
    def is_word(self, word):
        return word.upper() in self.words


@pytest.fixture
def mock_dictionary():
    """Фикстура для мок-словаря"""
    return MockDictionary()


@pytest.fixture
def game_state(mock_dictionary):
    """Фикстура для создания игрового состояния"""
    return GameState(['Игрок1', 'Игрок2'], mock_dictionary)


@pytest.fixture
def game_with_words(mock_dictionary):
    """Фикстура для игры с расширенным словарем"""
    dictionary = MockDictionary([
        'СЛОВО', 'ДЕЛО', 'КИНО', 'ТЕСТ', 'КОТ', 'ДОМ',
        'СТОЛ', 'РЕКА', 'МОРЕ', 'ВОДА', 'ИГРА', 'МОСТ',
        'КОРА', 'ЛОДКА', 'СОВА', 'РАМА', 'МАМА', 'ПАПА'
    ])
    return GameState(['Игрок1', 'Игрок2'], dictionary)
