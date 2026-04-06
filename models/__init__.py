# models/__init__.py
"""Модели данных игры Scrabble"""

from .dictionary import ScrabbleDictionary
from .player import Player
from .game_state import GameState, POINTS, BOARD_SIZE

__all__ = [
    'ScrabbleDictionary',
    'Player',
    'GameState',
    'POINTS',
    'BOARD_SIZE'
]
