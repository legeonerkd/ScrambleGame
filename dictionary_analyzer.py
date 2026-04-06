# dictionary_analyzer.py
# -*- coding: utf-8 -*-
"""
Скрипт для анализа и улучшения словаря ScrabbleGame
"""
import sys
import io
import re
from collections import Counter

# Настройка кодировки для Windows консоли
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def load_dictionary(filename='words.txt'):
    """Загрузить словарь из файла"""
    try:
        with open(filename, encoding='utf-8') as f:
            words = [w.strip().upper() for w in f if w.strip()]
        return words
    except FileNotFoundError:
        print(f"Файл {filename} не найден!")
        return []

def analyze_dictionary(words):
    """Анализ словаря"""
    print("=" * 60)
    print("АНАЛИЗ СЛОВАРЯ")
    print("=" * 60)
    
    # Общая статистика
    print(f"\n[*] Общая статистика:")
    print(f"   Всего слов: {len(words)}")
    print(f"   Уникальных слов: {len(set(words))}")
    
    # Дубликаты
    duplicates = [word for word, count in Counter(words).items() if count > 1]
    if duplicates:
        print(f"   [!] Дубликаты: {len(duplicates)}")
        print(f"   Примеры: {duplicates[:5]}")
    else:
        print(f"   [+] Дубликатов нет")
    
    # Распределение по длине
    print(f"\n[*] Распределение по длине слов:")
    length_dist = Counter(len(w) for w in words)
    for length in sorted(length_dist.keys())[:15]:
        bar = "#" * (length_dist[length] // 100)
        print(f"   {length:2d} букв: {length_dist[length]:5d} слов {bar}")
    
    # Самые короткие и длинные
    shortest = min(words, key=len)
    longest = max(words, key=len)
    print(f"\n   Самое короткое: '{shortest}' ({len(shortest)} букв)")
    print(f"   Самое длинное: '{longest}' ({len(longest)} букв)")
    
    # Частота букв
    print(f"\n[*] Частота букв:")
    all_letters = ''.join(words)
    letter_freq = Counter(all_letters)
    for letter, count in letter_freq.most_common(15):
        percentage = (count / len(all_letters)) * 100
        bar = "#" * int(percentage)
        print(f"   {letter}: {count:6d} ({percentage:5.2f}%) {bar}")
    
    # Проверка на недопустимые символы
    print(f"\n[*] Проверка на недопустимые символы:")
    russian_letters = set('АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ')
    invalid_words = []
    for word in words:
        if not all(c in russian_letters for c in word):
            invalid_words.append(word)
    
    if invalid_words:
        print(f"   [!] Найдено слов с недопустимыми символами: {len(invalid_words)}")
        print(f"   Примеры: {invalid_words[:10]}")
    else:
        print(f"   [+] Все слова содержат только русские буквы")
    
    # Слова из 2 букв (важны для игры)
    two_letter_words = [w for w in words if len(w) == 2]
    print(f"\n[*] Слова из 2 букв (всего {len(two_letter_words)}):")
    print(f"   {', '.join(sorted(two_letter_words)[:30])}")
    
    return {
        'total': len(words),
        'unique': len(set(words)),
        'duplicates': duplicates,
        'invalid': invalid_words,
        'two_letter': two_letter_words
    }

def clean_dictionary(words):
    """Очистка словаря от дубликатов и недопустимых слов"""
    print("\n" + "=" * 60)
    print("ОЧИСТКА СЛОВАРЯ")
    print("=" * 60)
    
    russian_letters = set('АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ')
    
    # Удалить дубликаты
    original_count = len(words)
    words = list(set(words))
    print(f"[+] Удалено дубликатов: {original_count - len(words)}")
    
    # Удалить слова с недопустимыми символами
    original_count = len(words)
    words = [w for w in words if all(c in russian_letters for c in w)]
    print(f"[+] Удалено слов с недопустимыми символами: {original_count - len(words)}")
    
    # Удалить слова короче 2 букв
    original_count = len(words)
    words = [w for w in words if len(w) >= 2]
    print(f"[+] Удалено слов короче 2 букв: {original_count - len(words)}")
    
    # Сортировка
    words = sorted(words)
    print(f"[+] Словарь отсортирован")
    
    print(f"\n[*] Итого слов в очищенном словаре: {len(words)}")
    
    return words

def save_dictionary(words, filename='words_clean.txt'):
    """Сохранить словарь в файл"""
    with open(filename, 'w', encoding='utf-8') as f:
        for word in words:
            f.write(word + '\n')
    print(f"\n[+] Словарь сохранен в файл: {filename}")

def add_common_words(words):
    """Добавить часто используемые слова, которых может не быть"""
    common_words = [
        # Короткие слова (2 буквы)
        'АХ', 'БА', 'БИ', 'БО', 'БУ', 'ВО', 'ДА', 'ДО', 'ЕЙ', 'ЖЕ',
        'ЗА', 'ИЗ', 'ИХ', 'КО', 'МЫ', 'НА', 'НЕ', 'НО', 'НУ', 'ОБ',
        'ОН', 'ОТ', 'ПО', 'РА', 'СО', 'ТО', 'ТЫ', 'УЖ', 'ХА', 'ЭХ',
        # Короткие слова (3 буквы)
        'БАЛ', 'БАР', 'БАС', 'БЕГ', 'БОБ', 'БОЙ', 'БОК', 'БОР', 'БЫК',
        'ВАЛ', 'ВАР', 'ВЕК', 'ВИД', 'ВОЗ', 'ВОЛ', 'ВОР', 'ГАЗ', 'ГОД',
        'ДАР', 'ДЕД', 'ДОМ', 'ДУБ', 'ДУХ', 'ЕДА', 'ЖАР', 'ЗАЛ', 'ЗОВ',
        'ИГО', 'ИМЯ', 'КАК', 'КОД', 'КОМ', 'КОН', 'КОТ', 'КТО', 'ЛАД',
        'ЛЕВ', 'ЛЕД', 'ЛЕС', 'ЛОБ', 'ЛУГ', 'ЛУК', 'ЛУЧ', 'МАК', 'МАЛ',
        'МАЙ', 'МЕД', 'МЕЛ', 'МИГ', 'МИР', 'МОЛ', 'МОХ', 'МЫС', 'НОС',
        'ОКО', 'ПАР', 'ПИР', 'ПОЛ', 'ПОТ', 'РАБ', 'РАД', 'РАЗ', 'РАЙ',
        'РАК', 'РОВ', 'РОГ', 'РОД', 'РОЙ', 'РОК', 'РОТ', 'РЯД', 'САД',
        'САМ', 'СОК', 'СОМ', 'СОН', 'СОР', 'СУД', 'СУП', 'СЫН', 'СЫР',
        'ТАЗ', 'ТАК', 'ТАМ', 'ТИП', 'ТОК', 'ТОМ', 'ТОН', 'ТУТ', 'УМ',
        'УХО', 'ФОН', 'ХОД', 'ХОР', 'ЦАР', 'ЧАЙ', 'ЧАС', 'ШАГ', 'ШАР',
        'ЭРА', 'ЮГ', 'ЯД'
    ]
    
    added = 0
    words_set = set(words)
    for word in common_words:
        if word not in words_set:
            words.append(word)
            added += 1
    
    if added > 0:
        print(f"\n[+] Добавлено часто используемых слов: {added}")
        words = sorted(words)
    
    return words

def main():
    """Главная функция"""
    print("\n[*] АНАЛИЗАТОР СЛОВАРЯ SCRABBLE GAME\n")
    
    # Загрузить словарь
    words = load_dictionary()
    if not words:
        return
    
    # Анализ
    stats = analyze_dictionary(words)
    
    # Предложить очистку
    if stats['duplicates'] or stats['invalid']:
        print("\n" + "=" * 60)
        response = input("\n[?] Очистить словарь от дубликатов и недопустимых слов? (y/n): ")
        if response.lower() == 'y':
            words = clean_dictionary(words)
            words = add_common_words(words)
            save_dictionary(words)
            
            # Заменить оригинальный файл?
            response = input("\n[?] Заменить оригинальный words.txt? (y/n): ")
            if response.lower() == 'y':
                save_dictionary(words, 'words.txt')
                print("[+] Файл words.txt обновлен!")
    else:
        print("\n[+] Словарь в хорошем состоянии!")
        
        # Добавить часто используемые слова
        response = input("\n[?] Добавить часто используемые короткие слова? (y/n): ")
        if response.lower() == 'y':
            words = add_common_words(words)
            save_dictionary(words, 'words.txt')
            print("[+] Файл words.txt обновлен!")

if __name__ == '__main__':
    main()
