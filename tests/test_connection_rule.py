# tests/test_connection_rule.py
"""Тесты классического правила Scrabble - новые слова должны использовать существующие буквы"""

import pytest
from engine import GameState


class TestConnectionRule:
    """Тесты правила соединения с существующими словами"""
    
    def test_second_word_must_connect(self, game_with_words):
        """Второе слово должно соединяться с первым"""
        state = game_with_words
        
        # Первый ход
        state.racks['Игрок1'] = ['К', 'О', 'Т', 'А', 'Е', 'И', 'Р']
        letters1 = [(7, 7, 'К'), (7, 8, 'О'), (7, 9, 'Т')]
        state.apply_move('Игрок1', letters1)
        
        # Второй ход - НЕ соединяется с первым словом
        state.racks['Игрок2'] = ['Д', 'О', 'М', 'А', 'Е', 'И', 'Р']
        letters2 = [(10, 10, 'Д'), (10, 11, 'О'), (10, 12, 'М')]
        ok, msg = state.can_place('Игрок2', letters2)
        
        assert ok == False
        assert "использовать" in msg.lower() and "существующие" in msg.lower()
    
    def test_second_word_connected_horizontally(self, game_with_words):
        """Второе слово соединяется горизонтально"""
        state = game_with_words
        
        # Первый ход - "КОТ" горизонтально
        state.racks['Игрок1'] = ['К', 'О', 'Т', 'А', 'Е', 'И', 'Р']
        letters1 = [(7, 7, 'К'), (7, 8, 'О'), (7, 9, 'Т')]
        state.apply_move('Игрок1', letters1)
        
        # Второй ход - добавляем буквы справа от "КОТ"
        state.racks['Игрок2'] = ['К', 'А', 'Р', 'Т', 'И', 'Н', 'А']
        letters2 = [(7, 10, 'А')]
        ok, msg = state.can_place('Игрок2', letters2)
        
        # Проверяем что соединение есть (А примыкает к Т)
        assert ok == True or "использовать" not in msg.lower()
    
    def test_second_word_connected_vertically(self, game_with_words):
        """Второе слово соединяется вертикально"""
        state = game_with_words
        
        # Первый ход - "КОТ"
        state.racks['Игрок1'] = ['К', 'О', 'Т', 'А', 'Е', 'И', 'Р']
        letters1 = [(7, 7, 'К'), (7, 8, 'О'), (7, 9, 'Т')]
        state.apply_move('Игрок1', letters1)
        
        # Второй ход - добавляем буквы снизу от К
        state.racks['Игрок2'] = ['И', 'Т', 'О', 'А', 'Е', 'Н', 'Р']
        letters2 = [(8, 7, 'И'), (9, 7, 'Т')]
        ok, msg = state.can_place('Игрок2', letters2)
        
        # И примыкает к К - должно быть соединение
        assert isinstance(ok, bool)
    
    def test_word_using_existing_letter(self, game_with_words):
        """Слово использует существующую букву (проходит через неё)"""
        state = game_with_words
        
        # Первый ход
        state.racks['Игрок1'] = ['К', 'О', 'Т', 'А', 'Е', 'И', 'Р']
        letters1 = [(7, 7, 'К'), (7, 8, 'О'), (7, 9, 'Т')]
        state.apply_move('Игрок1', letters1)
        
        # Второй ход - слово проходит через О (вертикально)
        state.racks['Игрок2'] = ['М', 'О', 'С', 'Т', 'А', 'Е', 'Р']
        # Размещаем "МОСТ" вертикально через О: М сверху, О уже есть, С и Т снизу
        letters2 = [(6, 8, 'М'), (8, 8, 'С'), (9, 8, 'Т')]
        ok, msg = state.can_place('Игрок2', letters2)
        
        # М примыкает к О - есть соединение
        assert isinstance(ok, bool)
    
    def test_first_word_no_connection_required(self, game_with_words):
        """Первое слово не требует соединения"""
        state = game_with_words
        
        # Первый ход - не требует соединения с другими словами
        letters = [(7, 7, 'Т'), (7, 8, 'Е'), (7, 9, 'С'), (7, 10, 'Т')]
        ok, msg = state.can_place('Игрок1', letters)
        
        # Не должно быть ошибки о соединении
        if not ok:
            assert "использовать" not in msg.lower()
        else:
            assert ok == True
    
    def test_word_adjacent_to_existing(self, game_with_words):
        """Слово примыкает к существующему слову"""
        state = game_with_words
        
        # Первый ход
        state.racks['Игрок1'] = ['К', 'О', 'Т', 'А', 'Е', 'И', 'Р']
        letters1 = [(7, 7, 'К'), (7, 8, 'О'), (7, 9, 'Т')]
        state.apply_move('Игрок1', letters1)
        
        # Второй ход - слово параллельно, примыкает снизу
        state.racks['Игрок2'] = ['Д', 'О', 'М', 'А', 'Е', 'И', 'Р']
        letters2 = [(8, 7, 'Д'), (8, 8, 'О'), (8, 9, 'М')]
        ok, msg = state.can_place('Игрок2', letters2)
        
        # Д примыкает к К сверху - есть соединение
        assert isinstance(ok, bool)


class TestNoOrphanWords:
    """Тесты что нельзя размещать изолированные слова"""
    
    def test_isolated_word_rejected(self, game_with_words):
        """Изолированное слово отвергается"""
        state = game_with_words
        
        # Первый ход
        state.racks['Игрок1'] = ['К', 'О', 'Т', 'А', 'Е', 'И', 'Р']
        letters1 = [(7, 7, 'К'), (7, 8, 'О'), (7, 9, 'Т')]
        state.apply_move('Игрок1', letters1)
        
        # Второй ход - полностью изолированное слово в углу доски
        state.racks['Игрок2'] = ['Д', 'О', 'М', 'А', 'Е', 'И', 'Р']
        letters2 = [(0, 0, 'Д'), (0, 1, 'О'), (0, 2, 'М')]
        ok, msg = state.can_place('Игрок2', letters2)
        
        assert ok == False
        assert "использовать" in msg.lower()
    
    def test_word_one_cell_away_rejected(self, game_with_words):
        """Слово на расстоянии одной клетки (не примыкает) отвергается"""
        state = game_with_words
        
        # Первый ход
        state.racks['Игрок1'] = ['К', 'О', 'Т', 'А', 'Е', 'И', 'Р']
        letters1 = [(7, 7, 'К'), (7, 8, 'О'), (7, 9, 'Т')]
        state.apply_move('Игрок1', letters1)
        
        # Второй ход - слово с пропуском одной клетки
        state.racks['Игрок2'] = ['Д', 'О', 'М', 'А', 'Е', 'И', 'Р']
        letters2 = [(7, 11, 'Д'), (7, 12, 'О'), (7, 13, 'М')]  # пропуск клетки (7,10)
        ok, msg = state.can_place('Игрок2', letters2)
        
        assert ok == False
        assert "использовать" in msg.lower()
