# models/dictionary.py
"""Модель словаря для игры Scrabble"""

from typing import Set, Tuple
import os


class ScrabbleDictionary:
    """
    Словарь слов для игры Scrabble.
    
    Загружает слова из файла и предоставляет методы для проверки валидности слов.
    Поддерживает добавление новых слов и сохранение в файл.
    """
    
    # Минимальная длина слова
    MIN_WORD_LENGTH = 3
    
    def __init__(self, path: str = "words.txt"):
        """
        Инициализирует словарь из файла.
        
        Args:
            path: Путь к файлу со словами (по умолчанию "words.txt")
        """
        self.path = path
        self.words: Set[str] = set()
        self.custom_words: Set[str] = set()  # Пользовательские слова
        self._load_words()
        self._load_custom_words()
    
    def _load_words(self) -> None:
        """Загружает слова из файла"""
        try:
            with open(self.path, encoding="utf-8") as f:
                self.words = {w.strip().upper() for w in f if w.strip()}
        except FileNotFoundError:
            # Если файл не найден, используем пустой словарь
            # В продакшене здесь должно быть исключение или предупреждение
            self.words = set()
    
    def _load_custom_words(self) -> None:
        """Загружает пользовательские слова из файла"""
        custom_path = "custom_words.txt"
        try:
            with open(custom_path, encoding="utf-8") as f:
                self.custom_words = {w.strip().upper() for w in f if w.strip()}
        except FileNotFoundError:
            self.custom_words = set()
    
    def is_word(self, word: str) -> bool:
        """
        Проверяет наличие слова в словаре.
        
        Args:
            word: Слово для проверки
            
        Returns:
            True если слово есть в словаре, False иначе
        """
        word_upper = word.upper()
        return word_upper in self.words or word_upper in self.custom_words
    
    def add_word(self, word: str) -> Tuple[bool, str]:
        """
        Добавляет новое слово в словарь.
        
        Args:
            word: Слово для добавления
            
        Returns:
            Кортеж (успех, сообщение)
        """
        # Валидация слова
        word_upper = word.strip().upper()
        
        if not word_upper:
            return False, "Слово не может быть пустым"
        
        if len(word_upper) < self.MIN_WORD_LENGTH:
            return False, f"Слово должно содержать минимум {self.MIN_WORD_LENGTH} буквы"
        
        # Проверка что слово содержит только русские буквы
        if not all(c.isalpha() and 'А' <= c <= 'Я' or c == 'Ё' for c in word_upper):
            return False, "Слово должно содержать только русские буквы"
        
        # Проверка что слово уже есть в словаре
        if word_upper in self.words:
            return False, f"Слово '{word_upper}' уже есть в основном словаре"
        
        if word_upper in self.custom_words:
            return False, f"Слово '{word_upper}' уже есть в пользовательском словаре"
        
        # Добавляем слово
        self.custom_words.add(word_upper)
        return True, f"Слово '{word_upper}' успешно добавлено"
    
    def save_custom_words(self) -> bool:
        """
        Сохраняет пользовательские слова в файл.
        
        Returns:
            True если сохранение успешно
        """
        try:
            custom_path = "custom_words.txt"
            with open(custom_path, 'w', encoding='utf-8') as f:
                for word in sorted(self.custom_words):
                    f.write(word + '\n')
            return True
        except Exception as e:
            print(f"Ошибка при сохранении: {e}")
            return False
    
    def get_custom_words_count(self) -> int:
        """Возвращает количество пользовательских слов"""
        return len(self.custom_words)
    
    def __len__(self) -> int:
        """Возвращает общее количество слов в словаре"""
        return len(self.words) + len(self.custom_words)
    
    def __contains__(self, word: str) -> bool:
        """Позволяет использовать оператор 'in'"""
        return self.is_word(word)
