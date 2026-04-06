# tests/test_scoring.py
"""Тесты системы подсчета очков"""

import pytest
from engine import GameState, POINTS


class TestBasicScoring:
    """Тесты базового подсчета очков"""
    
    def test_simple_word_score(self, game_with_words):
        """Проверка базового подсчета очков без бонусов"""
        state = game_with_words
        
        # Убираем все бонусы для чистого теста
        state.bonus_spots = {}
        
        # Слово "КОТ" - К(2) + О(1) + Т(1) = 4
        letters = [(0, 0, 'К'), (0, 1, 'О'), (0, 2, 'Т')]
        score, _ = state._calc_score(letters)
        expected = POINTS['К'] + POINTS['О'] + POINTS['Т']
        assert score == expected
    
    def test_letter_points_correct(self):
        """Проверка правильности очков за буквы"""
        # Проверяем некоторые ключевые значения
        assert POINTS['А'] == 1  # частая буква
        assert POINTS['Ф'] == 10  # редкая буква
        assert POINTS['Щ'] == 10  # редкая буква


class TestBonusScoring:
    """Тесты подсчета с бонусами"""
    
    def test_letter_bonus_x2(self, game_with_words):
        """Проверка бонуса x2 к букве"""
        state = game_with_words
        
        # Устанавливаем бонус на конкретную клетку
        state.bonus_spots = {(5, 5): ("LETTER", 2)}
        state.used_bonus = set()
        
        # К(2) с бонусом x2 = 4, плюс О(1) + Т(1) = 6
        letters = [(5, 5, 'К'), (5, 6, 'О'), (5, 7, 'Т')]
        score, used = state._calc_score(letters)
        expected = (POINTS['К'] * 2) + POINTS['О'] + POINTS['Т']
        assert score == expected
        assert (5, 5) in used
    
    def test_letter_bonus_x3(self, game_with_words):
        """Проверка бонуса x3 к букве"""
        state = game_with_words
        
        state.bonus_spots = {(5, 5): ("LETTER", 3)}
        state.used_bonus = set()
        
        # К(2) с бонусом x3 = 6, плюс О(1) + Т(1) = 8
        letters = [(5, 5, 'К'), (5, 6, 'О'), (5, 7, 'Т')]
        score, used = state._calc_score(letters)
        expected = (POINTS['К'] * 3) + POINTS['О'] + POINTS['Т']
        assert score == expected
    
    def test_word_bonus_x2(self, game_with_words):
        """Проверка бонуса x2 к слову"""
        state = game_with_words
        
        state.bonus_spots = {(5, 5): ("WORD", 2)}
        state.used_bonus = set()
        
        # (К(2) + О(1) + Т(1)) * 2 = 8
        letters = [(5, 5, 'К'), (5, 6, 'О'), (5, 7, 'Т')]
        score, used = state._calc_score(letters)
        expected = (POINTS['К'] + POINTS['О'] + POINTS['Т']) * 2
        assert score == expected
    
    def test_word_bonus_x3(self, game_with_words):
        """Проверка бонуса x3 к слову"""
        state = game_with_words
        
        state.bonus_spots = {(5, 5): ("WORD", 3)}
        state.used_bonus = set()
        
        # (К(2) + О(1) + Т(1)) * 3 = 12
        letters = [(5, 5, 'К'), (5, 6, 'О'), (5, 7, 'Т')]
        score, used = state._calc_score(letters)
        expected = (POINTS['К'] + POINTS['О'] + POINTS['Т']) * 3
        assert score == expected
    
    def test_multiple_word_bonuses(self, game_with_words):
        """Проверка множественных бонусов к слову"""
        state = game_with_words
        
        # Два бонуса к слову - должны перемножаться
        state.bonus_spots = {
            (5, 5): ("WORD", 2),
            (5, 6): ("WORD", 2)
        }
        state.used_bonus = set()
        
        # (К(2) + О(1) + Т(1)) * 2 * 2 = 16
        letters = [(5, 5, 'К'), (5, 6, 'О'), (5, 7, 'Т')]
        score, used = state._calc_score(letters)
        expected = (POINTS['К'] + POINTS['О'] + POINTS['Т']) * 2 * 2
        assert score == expected
    
    def test_mixed_bonuses(self, game_with_words):
        """Проверка комбинации бонусов к букве и слову"""
        state = game_with_words
        
        # Бонус к букве К и бонус к слову
        state.bonus_spots = {
            (5, 5): ("LETTER", 2),  # К * 2 = 4
            (5, 6): ("WORD", 2)      # всё слово * 2
        }
        state.used_bonus = set()
        
        # (К(2)*2 + О(1) + Т(1)) * 2 = (4 + 1 + 1) * 2 = 12
        letters = [(5, 5, 'К'), (5, 6, 'О'), (5, 7, 'Т')]
        score, used = state._calc_score(letters)
        expected = ((POINTS['К'] * 2) + POINTS['О'] + POINTS['Т']) * 2
        assert score == expected
    
    def test_used_bonus_not_applied(self, game_with_words):
        """Проверка что использованный бонус не применяется повторно"""
        state = game_with_words
        
        state.bonus_spots = {(5, 5): ("WORD", 2)}
        state.used_bonus = {(5, 5)}  # Бонус уже использован
        
        # Бонус не должен применяться
        letters = [(5, 5, 'К'), (5, 6, 'О'), (5, 7, 'Т')]
        score, used = state._calc_score(letters)
        expected = POINTS['К'] + POINTS['О'] + POINTS['Т']
        assert score == expected
        assert len(used) == 0


class TestSevenLetterBonus:
    """Тесты бонуса за использование всех 7 букв"""
    
    def test_seven_letter_bonus(self, game_with_words):
        """Проверка бонуса +50 за 7 букв"""
        state = game_with_words
        state.bonus_spots = {}
        
        # 7 букв
        letters = [
            (5, 5, 'С'), (5, 6, 'Л'), (5, 7, 'О'), (5, 8, 'В'),
            (5, 9, 'О'), (5, 10, 'К'), (5, 11, 'О')
        ]
        score, _ = state._calc_score(letters)
        
        base_score = sum(POINTS[ch] for _, _, ch in letters)
        expected = base_score + 50
        assert score == expected
    
    def test_six_letters_no_bonus(self, game_with_words):
        """Проверка отсутствия бонуса при 6 буквах"""
        state = game_with_words
        state.bonus_spots = {}
        
        # 6 букв - бонус не должен применяться
        letters = [
            (5, 5, 'С'), (5, 6, 'Л'), (5, 7, 'О'), (5, 8, 'В'),
            (5, 9, 'О'), (5, 10, 'К')
        ]
        score, _ = state._calc_score(letters)
        
        expected = sum(POINTS[ch] for _, _, ch in letters)
        assert score == expected  # Без бонуса +50


class TestScoreApplication:
    """Тесты применения очков к игроку"""
    
    def test_score_added_to_player(self, game_with_words):
        """Проверка что очки добавляются к счету игрока"""
        state = game_with_words
        
        initial_score = state.scores['Игрок1']
        
        # Делаем ход - сначала добавим нужные буквы в стойку
        state.racks['Игрок1'] = ['К', 'О', 'Т', 'А', 'Е', 'И', 'Р']
        letters = [(7, 7, 'К'), (7, 8, 'О'), (7, 9, 'Т')]
        state.apply_move('Игрок1', letters)
        
        # Счет должен увеличиться
        assert state.scores['Игрок1'] > initial_score
    
    def test_scores_independent(self, game_with_words):
        """Проверка что счета игроков независимы"""
        state = game_with_words
        
        # Первый ход
        state.racks['Игрок1'] = ['К', 'О', 'Т', 'А', 'Е', 'И', 'Р']
        letters1 = [(7, 7, 'К'), (7, 8, 'О'), (7, 9, 'Т')]
        state.apply_move('Игрок1', letters1)
        score1 = state.scores['Игрок1']
        
        # Второй игрок делает ход
        letters2 = [(8, 7, 'И'), (9, 7, 'Т')]
        if state.can_place('Игрок2', letters2)[0]:
            state.apply_move('Игрок2', letters2)
            
            # Счет первого игрока не должен измениться
            assert state.scores['Игрок1'] == score1
            # Счет второго игрока должен быть больше 0
            assert state.scores['Игрок2'] > 0
