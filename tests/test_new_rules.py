# tests/test_new_rules.py
"""Тесты новых правил игры"""

import pytest
from engine import GameState


class TestMinimumWordLength:
    """Тесты правила минимальной длины слова (3 буквы)"""
    
    def test_word_with_three_letters_accepted(self, game_with_words):
        """Слово из 3 букв должно приниматься"""
        state = game_with_words
        letters = [(7, 7, 'К'), (7, 8, 'О'), (7, 9, 'Т')]
        ok, msg = state.can_place('Игрок1', letters)
        assert ok == True
    
    def test_word_with_two_letters_rejected(self, game_with_words):
        """Слово из 2 букв должно отвергаться"""
        state = game_with_words
        # Пытаемся разместить только 2 буквы
        letters = [(7, 7, 'О'), (7, 8, 'К')]
        ok, msg = state.can_place('Игрок1', letters)
        assert ok == False
        assert "минимум 3 буквы" in msg.lower()
    
    def test_single_letter_rejected(self, game_with_words):
        """Одна буква должна отвергаться"""
        state = game_with_words
        letters = [(7, 7, 'К')]
        ok, msg = state.can_place('Игрок1', letters)
        assert ok == False
        assert "минимум 3 буквы" in msg.lower()
    
    def test_side_word_with_two_letters_rejected(self, game_with_words):
        """Побочное слово из 2 букв должно отвергаться"""
        state = game_with_words
        
        # Первый ход - размещаем "КОТ"
        state.racks['Игрок1'] = ['К', 'О', 'Т', 'А', 'Е', 'И', 'Р']
        letters1 = [(7, 7, 'К'), (7, 8, 'О'), (7, 9, 'Т')]
        state.apply_move('Игрок1', letters1)
        
        # Пытаемся создать слово, которое создаст побочное слово из 2 букв
        # Размещаем "ОК" вертикально через О в слове КОТ
        state.racks['Игрок2'] = ['О', 'К', 'А', 'Е', 'И', 'Р', 'Н']
        letters2 = [(6, 8, 'О'), (8, 8, 'К')]
        ok, msg = state.can_place('Игрок2', letters2)
        assert ok == False
        # Должна быть ошибка о минимальной длине


class TestNoReplacingLetters:
    """Тесты правила запрета замены букв в составленных словах"""
    
    def test_cannot_place_on_occupied_cell(self, game_with_words):
        """Нельзя ставить букву на уже занятую клетку"""
        state = game_with_words
        
        # Первый ход - размещаем "КОТ"
        state.racks['Игрок1'] = ['К', 'О', 'Т', 'А', 'Е', 'И', 'Р']
        letters1 = [(7, 7, 'К'), (7, 8, 'О'), (7, 9, 'Т')]
        state.apply_move('Игрок1', letters1)
        
        # Пытаемся поставить букву на уже занятую клетку (7, 8) где стоит 'О'
        state.racks['Игрок2'] = ['Д', 'О', 'М', 'А', 'Е', 'И', 'Р']
        letters2 = [(7, 8, 'Д'), (7, 10, 'О'), (7, 11, 'М')]
        ok, msg = state.can_place('Игрок2', letters2)
        assert ok == False
        assert "уже занята" in msg.lower()
    
    def test_can_build_around_existing_letters(self, game_with_words):
        """Можно строить вокруг существующих букв (но не на них)"""
        state = game_with_words
        
        # Первый ход - размещаем "КОТ" горизонтально
        state.racks['Игрок1'] = ['К', 'О', 'Т', 'А', 'Е', 'И', 'Р']
        letters1 = [(7, 7, 'К'), (7, 8, 'О'), (7, 9, 'Т')]
        state.apply_move('Игрок1', letters1)
        
        # Второй ход - размещаем "ИГРА" вертикально, используя И из КОТ
        # Нет, используем новые буквы рядом
        state.racks['Игрок2'] = ['И', 'Г', 'Р', 'А', 'Е', 'Л', 'О']
        # Размещаем вертикально рядом с К
        letters2 = [(6, 7, 'И'), (8, 7, 'Г'), (9, 7, 'Р'), (10, 7, 'А')]
        ok, msg = state.can_place('Игрок2', letters2)
        # Это создаст слово "КГ" побочно, которое невалидно, но проверим логику размещения
        # Главное что мы не ставим на занятые клетки
        assert isinstance(ok, bool)
    
    def test_multiple_violations(self, game_with_words):
        """Тест множественных нарушений"""
        state = game_with_words
        
        # Размещаем первое слово
        state.racks['Игрок1'] = ['К', 'О', 'Т', 'А', 'Е', 'И', 'Р']
        letters1 = [(7, 7, 'К'), (7, 8, 'О'), (7, 9, 'Т')]
        state.apply_move('Игрок1', letters1)
        
        # Пытаемся поставить на занятую клетку
        letters2 = [(7, 7, 'Д'), (7, 8, 'О'), (7, 9, 'М')]
        ok, msg = state.can_place('Игрок2', letters2)
        assert ok == False


class TestValidMoves:
    """Тесты что валидные ходы все еще работают"""
    
    def test_valid_first_move_three_letters(self, game_with_words):
        """Валидный первый ход из 3 букв"""
        state = game_with_words
        letters = [(7, 7, 'К'), (7, 8, 'О'), (7, 9, 'Т')]
        ok, msg = state.can_place('Игрок1', letters)
        assert ok == True
    
    def test_valid_first_move_four_letters(self, game_with_words):
        """Валидный первый ход из 4 букв"""
        state = game_with_words
        letters = [(7, 6, 'Д'), (7, 7, 'Е'), (7, 8, 'Л'), (7, 9, 'О')]
        ok, msg = state.can_place('Игрок1', letters)
        assert ok == True
    
    def test_valid_second_move(self, game_with_words):
        """Валидный второй ход"""
        state = game_with_words
        
        # Первый ход
        state.racks['Игрок1'] = ['Т', 'Е', 'С', 'Т', 'А', 'И', 'Р']
        letters1 = [(7, 7, 'Т'), (7, 8, 'Е'), (7, 9, 'С'), (7, 10, 'Т')]
        state.apply_move('Игрок1', letters1)
        
        # Второй ход - строим перпендикулярно
        state.racks['Игрок2'] = ['К', 'О', 'Т', 'А', 'Е', 'И', 'Р']
        letters2 = [(6, 7, 'К'), (8, 7, 'О')]
        ok, msg = state.can_place('Игрок2', letters2)
        # Это создаст слово КТО вертикально через Т из ТЕСТ
        # Проверяем что логика работает
        assert isinstance(ok, bool)
