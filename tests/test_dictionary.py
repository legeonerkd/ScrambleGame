# tests/test_dictionary.py
"""Тесты функциональности словаря"""

import pytest
import os
from models.dictionary import ScrabbleDictionary


class TestDictionaryBasics:
    """Базовые тесты словаря"""
    
    def test_dictionary_creation(self):
        """Проверка создания словаря"""
        dictionary = ScrabbleDictionary()
        assert dictionary is not None
        assert len(dictionary.words) > 0
    
    def test_is_word_valid(self):
        """Проверка что валидное слово распознается"""
        dictionary = ScrabbleDictionary()
        # Эти слова точно есть в словаре
        assert dictionary.is_word("КОТ") == True
        assert dictionary.is_word("кот") == True  # регистронезависимо
        assert dictionary.is_word("ДЕЛО") == True
    
    def test_is_word_invalid(self):
        """Проверка что невалидное слово не распознается"""
        dictionary = ScrabbleDictionary()
        assert dictionary.is_word("ХЫХЫХЫ") == False
        assert dictionary.is_word("ЗЗЗ") == False


class TestAddWord:
    """Тесты добавления слов"""
    
    def test_add_valid_word(self):
        """Добавление валидного слова"""
        dictionary = ScrabbleDictionary()
        success, message = dictionary.add_word("ТЕСТОВОЕ")
        assert success == True
        assert "успешно" in message.lower()
        assert dictionary.is_word("ТЕСТОВОЕ") == True
    
    def test_add_word_minimum_length(self):
        """Слово должно быть минимум 3 буквы"""
        dictionary = ScrabbleDictionary()
        
        # 3 буквы - ОК
        success, _ = dictionary.add_word("ААА")
        assert success == True
        
        # 2 буквы - ошибка
        success, message = dictionary.add_word("АА")
        assert success == False
        assert "минимум" in message.lower()
        
        # 1 буква - ошибка
        success, message = dictionary.add_word("А")
        assert success == False
        assert "минимум" in message.lower()
    
    def test_add_empty_word(self):
        """Пустое слово не должно добавляться"""
        dictionary = ScrabbleDictionary()
        success, message = dictionary.add_word("")
        assert success == False
        assert "пустым" in message.lower()
    
    def test_add_word_with_spaces(self):
        """Слово с пробелами обрезается"""
        dictionary = ScrabbleDictionary()
        success, _ = dictionary.add_word("  ТЕСТСЛОВО  ")
        assert success == True
        assert dictionary.is_word("ТЕСТСЛОВО") == True
    
    def test_add_duplicate_word(self):
        """Дублирующее слово не добавляется"""
        dictionary = ScrabbleDictionary()
        
        # Добавляем первый раз (используем явно несуществующее слово)
        success1, _ = dictionary.add_word("АБВГДЕЖЗ")
        assert success1 == True
        
        # Пытаемся добавить еще раз
        success2, message = dictionary.add_word("АБВГДЕЖЗ")
        assert success2 == False
        assert "уже есть" in message.lower()
    
    def test_add_word_already_in_main_dictionary(self):
        """Слово из основного словаря не добавляется в пользовательский"""
        dictionary = ScrabbleDictionary()
        # КОТ точно есть в основном словаре
        success, message = dictionary.add_word("КОТ")
        assert success == False
        assert "уже есть" in message.lower()
    
    def test_add_word_non_cyrillic(self):
        """Слово с нерусскими буквами не добавляется"""
        dictionary = ScrabbleDictionary()
        
        success, message = dictionary.add_word("TEST")
        assert success == False
        assert "русские буквы" in message.lower()
        
        success, message = dictionary.add_word("ТЕСТ123")
        assert success == False
        assert "русские буквы" in message.lower()
    
    def test_add_word_with_yo(self):
        """Слово с буквой Ё добавляется"""
        dictionary = ScrabbleDictionary()
        success, _ = dictionary.add_word("ЁЖ")
        # Не добавится из-за минимальной длины
        assert success == False
        
        success, _ = dictionary.add_word("ЁЖИК")
        assert success == True


class TestCustomWords:
    """Тесты пользовательских слов"""
    
    def test_custom_words_count(self):
        """Проверка подсчета пользовательских слов"""
        dictionary = ScrabbleDictionary()
        initial_count = dictionary.get_custom_words_count()
        
        dictionary.add_word("НОВОЕ")
        assert dictionary.get_custom_words_count() == initial_count + 1
        
        dictionary.add_word("ВТОРОЕ")
        assert dictionary.get_custom_words_count() == initial_count + 2
    
    def test_save_custom_words(self):
        """Тесты сохранения пользовательских слов"""
        dictionary = ScrabbleDictionary()
        
        # Добавляем несколько слов
        dictionary.add_word("ПЕРВОЕ")
        dictionary.add_word("ВТОРОЕ")
        
        # Сохраняем
        result = dictionary.save_custom_words()
        assert result == True
        
        # Проверяем что файл создан
        assert os.path.exists("custom_words.txt")
        
        # Создаем новый словарь и проверяем что слова загрузились
        dictionary2 = ScrabbleDictionary()
        assert dictionary2.is_word("ПЕРВОЕ") == True
        assert dictionary2.is_word("ВТОРОЕ") == True
        
        # Очищаем после теста
        try:
            os.remove("custom_words.txt")
        except:
            pass
    
    def test_total_words_count(self):
        """Проверка общего количества слов"""
        dictionary = ScrabbleDictionary()
        initial_total = len(dictionary)
        
        dictionary.add_word("НОВОЕ")
        assert len(dictionary) == initial_total + 1


class TestDictionaryContains:
    """Тесты оператора 'in'"""
    
    def test_contains_operator(self):
        """Проверка оператора 'in'"""
        dictionary = ScrabbleDictionary()
        
        dictionary.add_word("ТЕСТОВОЕ")
        assert "ТЕСТОВОЕ" in dictionary
        assert "ХЫХЫХЫ" not in dictionary
