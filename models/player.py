# models/player.py
"""Модель игрока для игры Scrabble"""

from typing import List


class Player:
    """
    Модель игрока в игре Scrabble.
    
    Хранит информацию об игроке: имя, стойку с буквами и счет.
    """
    
    def __init__(self, name: str):
        """
        Инициализирует игрока.
        
        Args:
            name: Имя игрока
        """
        self.name = name
        self.rack: List[str] = []
        self.score: int = 0
    
    def add_to_rack(self, letter: str) -> None:
        """
        Добавляет букву в стойку игрока.
        
        Args:
            letter: Буква для добавления
        """
        self.rack.append(letter)
    
    def remove_from_rack(self, letter: str) -> None:
        """
        Удаляет букву из стойки игрока.
        
        Args:
            letter: Буква для удаления
            
        Raises:
            ValueError: Если буквы нет в стойке
        """
        self.rack.remove(letter)
    
    def has_letter(self, letter: str) -> bool:
        """
        Проверяет наличие буквы в стойке.
        
        Args:
            letter: Буква для проверки
            
        Returns:
            True если буква есть в стойке
        """
        return letter in self.rack
    
    def add_score(self, points: int) -> None:
        """
        Добавляет очки к счету игрока.
        
        Args:
            points: Количество очков для добавления
        """
        self.score += points
    
    def __repr__(self) -> str:
        """Строковое представление игрока"""
        return f"Player(name='{self.name}', score={self.score}, rack={self.rack})"
    
    def __str__(self) -> str:
        """Строковое представление для пользователя"""
        return f"{self.name}: {self.score} очков"
