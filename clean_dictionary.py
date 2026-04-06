#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Скрипт для удаления слов из 1-2 букв из словаря"""

def clean_dictionary(input_file='words.txt', output_file='words.txt', min_length=3):
    """
    Удаляет короткие слова из словаря.
    
    Args:
        input_file: Входной файл со словами
        output_file: Выходной файл (можно тот же)
        min_length: Минимальная длина слова (по умолчанию 3)
    """
    # Читаем все слова
    with open(input_file, 'r', encoding='utf-8') as f:
        words = [w.strip() for w in f if w.strip()]
    
    print(f"Total words: {len(words)}")
    
    # Находим короткие слова
    short_words = [w for w in words if len(w) < min_length]
    print(f"Words shorter than {min_length} letters: {len(short_words)}")
    
    # Сохраняем короткие слова в отдельный файл для справки
    if short_words:
        with open('removed_short_words.txt', 'w', encoding='utf-8') as f:
            for w in short_words:
                f.write(f"{w}\n")
        print(f"Short words saved to removed_short_words.txt")
    
    # Фильтруем слова
    filtered_words = [w for w in words if len(w) >= min_length]
    print(f"\nWords after filtering: {len(filtered_words)}")
    print(f"Removed words: {len(words) - len(filtered_words)}")
    
    # Сохраняем обратно
    with open(output_file, 'w', encoding='utf-8') as f:
        for word in filtered_words:
            f.write(word + '\n')
    
    print(f"\nDictionary saved to {output_file}")

if __name__ == '__main__':
    clean_dictionary()
