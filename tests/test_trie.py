# tests/test_trie.py
"""Тесты для Trie-структуры"""

import pytest
from models.trie import Trie, TrieNode


class TestTrieBasics:
    """Базовые тесты Trie"""
    
    def test_trie_creation(self):
        """Проверка создания Trie"""
        trie = Trie()
        assert trie is not None
        assert len(trie) == 0
    
    def test_insert_word(self):
        """Проверка вставки слова"""
        trie = Trie()
        trie.insert("КОТ")
        assert len(trie) == 1
        assert trie.search("КОТ") == True
    
    def test_insert_multiple_words(self):
        """Проверка вставки нескольких слов"""
        trie = Trie()
        words = ["КОТ", "КИНО", "ДЕЛО", "ТЕСТ"]
        for word in words:
            trie.insert(word)
        
        assert len(trie) == 4
        for word in words:
            assert trie.search(word) == True
    
    def test_search_nonexistent_word(self):
        """Поиск несуществующего слова"""
        trie = Trie()
        trie.insert("КОТ")
        assert trie.search("СОБАКА") == False
    
    def test_case_insensitive(self):
        """Проверка что поиск не зависит от регистра"""
        trie = Trie()
        trie.insert("кот")
        assert trie.search("КОТ") == True
        assert trie.search("кот") == True
        assert trie.search("Кот") == True


class TestTriePrefix:
    """Тесты работы с префиксами"""
    
    def test_starts_with_valid_prefix(self):
        """Проверка существующего префикса"""
        trie = Trie()
        trie.insert("КИНО")
        assert trie.starts_with("К") == True
        assert trie.starts_with("КИ") == True
        assert trie.starts_with("КИН") == True
        assert trie.starts_with("КИНО") == True
    
    def test_starts_with_invalid_prefix(self):
        """Проверка несуществующего префикса"""
        trie = Trie()
        trie.insert("КИНО")
        assert trie.starts_with("Д") == False
        assert trie.starts_with("КА") == False


class TestTrieFindWords:
    """Тесты поиска слов по буквам"""
    
    def test_find_words_with_letters(self):
        """Поиск слов из доступных букв"""
        trie = Trie()
        trie.insert("КОТ")
        trie.insert("ТОК")
        trie.insert("КИНО")
        
        # Ищем слова из букв К, О, Т
        words = trie.find_words_with_letters(['К', 'О', 'Т'])
        assert "КОТ" in words
        assert "ТОК" in words
        assert "КИНО" not in words  # нет буквы И
    
    def test_find_words_respects_letter_count(self):
        """Поиск учитывает количество доступных букв"""
        trie = Trie()
        trie.insert("КОТ")
        trie.insert("КОКОС")
        
        # Только одна буква О
        words = trie.find_words_with_letters(['К', 'О', 'Т', 'С'])
        assert "КОТ" in words
        assert "КОКОС" not in words  # нужно 2 буквы О
    
    def test_find_words_min_max_length(self):
        """Поиск с ограничением длины"""
        trie = Trie()
        trie.insert("КОТ")      # 3 буквы
        trie.insert("КИНО")     # 4 буквы
        trie.insert("КОТИК")    # 5 букв
        
        words = trie.find_words_with_letters(
            ['К', 'О', 'Т', 'И', 'Н'],
            min_length=4,
            max_length=4
        )
        assert "КИНО" in words
        assert "КОТ" not in words     # слишком короткое
        assert "КОТИК" not in words   # слишком длинное


class TestTriePattern:
    """Тесты поиска по шаблону"""
    
    def test_pattern_with_wildcards(self):
        """Поиск по шаблону с подстановочными символами"""
        trie = Trie()
        trie.insert("КОТ")
        trie.insert("КИТ")
        trie.insert("РОТ")
        
        # Шаблон К?Т найдет КОТ и КИТ
        words = trie.find_words_with_pattern("К?Т", ['О', 'И', 'А'])
        assert "КОТ" in words
        assert "КИТ" in words
        assert "РОТ" not in words  # не начинается с К
    
    def test_pattern_no_wildcards(self):
        """Поиск по точному шаблону"""
        trie = Trie()
        trie.insert("КОТ")
        
        words = trie.find_words_with_pattern("КОТ", [])
        assert "КОТ" in words


class TestTrieContains:
    """Тесты оператора 'in'"""
    
    def test_contains_operator(self):
        """Проверка оператора 'in'"""
        trie = Trie()
        trie.insert("КОТ")
        
        assert "КОТ" in trie
        assert "СОБАКА" not in trie
