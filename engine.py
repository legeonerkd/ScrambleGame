# engine.py
"""
УСТАРЕВШИЙ МОДУЛЬ - для обратной совместимости.
Используйте models.game_state вместо этого модуля.
"""

# Импортируем из новых модулей для обратной совместимости
from models.game_state import (
    GameState,
    generate_bonus_spots,
    BOARD_SIZE,
    VOWELS,
    CONSONANTS,
    POINTS
)

# Экспортируем все для обратной совместимости
__all__ = [
    'GameState',
    'generate_bonus_spots',
    'BOARD_SIZE',
    'VOWELS',
    'CONSONANTS',
    'POINTS'
]

