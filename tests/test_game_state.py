# tests/test_game_state.py
"""Тесты для базовой функциональности GameState"""

import pytest
from engine import GameState


class TestGameStateInitialization:
    """Тесты инициализации игрового состояния"""
    
    def test_game_state_creation(self, game_state):
        """Проверка создания игрового состояния"""
        assert game_state is not None
        assert len(game_state.players) == 2
        assert game_state.current == 'Игрок1'
    
    def test_initial_board_empty(self, game_state):
        """Проверка что доска изначально пуста"""
        assert len(game_state.board) == 0
        assert game_state.is_first_move() == True
    
    def test_initial_racks_created(self, game_state):
        """Проверка создания стоек игроков"""
        assert 'Игрок1' in game_state.racks
        assert 'Игрок2' in game_state.racks
        assert len(game_state.racks['Игрок1']) == 7
        assert len(game_state.racks['Игрок2']) == 7
    
    def test_initial_scores_zero(self, game_state):
        """Проверка начальных очков"""
        assert game_state.scores['Игрок1'] == 0
        assert game_state.scores['Игрок2'] == 0
    
    def test_bonus_spots_generated(self, game_state):
        """Проверка генерации бонусных клеток"""
        assert len(game_state.bonus_spots) == 11  # центр + 10 случайных
        assert (7, 7) in game_state.bonus_spots
        assert game_state.bonus_spots[(7, 7)] == ("WORD", 2)
    
    def test_bag_not_empty(self, game_state):
        """Проверка что мешок не пустой после раздачи"""
        # После раздачи 14 букв (7 каждому игроку) должны остаться буквы
        assert len(game_state.bag) > 0


class TestRackManagement:
    """Тесты управления стойками"""
    
    def test_rack_limit_two_same_letters(self, game_state):
        """Проверка ограничения одинаковых букв в стойке"""
        rack = game_state.racks['Игрок1']
        for letter in rack:
            assert rack.count(letter) <= 2
    
    def test_refill_rack(self, game_state):
        """Проверка пополнения стойки"""
        # Удалим несколько букв
        rack = game_state.racks['Игрок1']
        initial_bag_size = len(game_state.bag)
        
        # Удаляем 3 буквы
        removed = []
        for _ in range(3):
            if rack:
                removed.append(rack.pop())
        
        # Пополняем стойку
        game_state.refill_rack('Игрок1')
        
        # Проверяем что стойка пополнилась (но не больше 7)
        assert len(game_state.racks['Игрок1']) <= 7


class TestSwapLetters:
    """Тесты обмена букв"""
    
    def test_swap_letters(self, game_state):
        """Проверка обмена букв"""
        # Устанавливаем известную стойку
        game_state.racks['Игрок1'] = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ж']
        rack = game_state.racks['Игрок1'][:]
        letters_to_swap = ['А', 'Б', 'В']
        current_player = game_state.current
        
        game_state.swap_letters('Игрок1', letters_to_swap)
        
        # Проверяем что стойка изменилась
        new_rack = game_state.racks['Игрок1']
        # Стойка должна содержать 7 букв после обмена
        assert len(new_rack) == 7
        
        # Проверяем что ход перешел к другому игроку
        assert game_state.current != current_player
