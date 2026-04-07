# models/trie.py
"""Trie-структура для быстрого поиска слов"""

from typing import Dict, List, Set, Optional


class TrieNode:
    """Узел в Trie-дереве"""
    
    def __init__(self):
        self.children: Dict[str, 'TrieNode'] = {}
        self.is_word: bool = False
        self.word: Optional[str] = None


class Trie:
    """
    Trie (префиксное дерево) для эффективного поиска слов.
    
    Позволяет:
    - Быстро проверить существование слова O(m), где m - длина слова
    - Найти все слова с определенным префиксом
    - Найти слова используя доступные буквы
    """
    
    def __init__(self):
        self.root = TrieNode()
        self.word_count = 0
    
    def insert(self, word: str) -> None:
        """
        Вставляет слово в Trie.
        
        Args:
            word: Слово для вставки (в верхнем регистре)
        """
        node = self.root
        word = word.upper()
        
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        
        if not node.is_word:
            self.word_count += 1
        node.is_word = True
        node.word = word
    
    def search(self, word: str) -> bool:
        """
        Проверяет наличие слова в Trie.
        
        Args:
            word: Слово для поиска
            
        Returns:
            True если слово есть
        """
        node = self._find_node(word.upper())
        return node is not None and node.is_word
    
    def _find_node(self, word: str) -> Optional[TrieNode]:
        """Находит узел для слова"""
        node = self.root
        for char in word:
            if char not in node.children:
                return None
            node = node.children[char]
        return node
    
    def starts_with(self, prefix: str) -> bool:
        """
        Проверяет существование префикса.
        
        Args:
            prefix: Префикс для проверки
            
        Returns:
            True если есть слова с таким префиксом
        """
        return self._find_node(prefix.upper()) is not None
    
    def find_words_with_letters(self, available_letters: List[str], 
                                min_length: int = 3,
                                max_length: int = 7) -> List[str]:
        """
        Находит все слова которые можно составить из доступных букв.
        
        Args:
            available_letters: Список доступных букв
            min_length: Минимальная длина слова
            max_length: Максимальная длина слова
            
        Returns:
            Список найденных слов
        """
        results = []
        letter_counts = {}
        for letter in available_letters:
            letter_counts[letter] = letter_counts.get(letter, 0) + 1
        
        def dfs(node: TrieNode, path: str, used_counts: Dict[str, int]):
            """Поиск в глубину по Trie"""
            if node.is_word and min_length <= len(path) <= max_length:
                results.append(path)
            
            if len(path) >= max_length:
                return
            
            for char, child in node.children.items():
                if used_counts.get(char, 0) < letter_counts.get(char, 0):
                    new_used = used_counts.copy()
                    new_used[char] = new_used.get(char, 0) + 1
                    dfs(child, path + char, new_used)
        
        dfs(self.root, "", {})
        return results
    
    def find_words_with_pattern(self, pattern: str, available_letters: List[str]) -> List[str]:
        """
        Находит слова соответствующие шаблону с использованием доступных букв.
        
        Args:
            pattern: Шаблон где '?' - любая буква, остальные - конкретные буквы
                    Пример: "К?Т" найдет "КОТ", "КИТ" и т.д.
            available_letters: Доступные буквы для позиций с '?'
            
        Returns:
            Список найденных слов
        """
        results = []
        letter_counts = {}
        for letter in available_letters:
            letter_counts[letter] = letter_counts.get(letter, 0) + 1
        
        def dfs(node: TrieNode, pattern_idx: int, used_counts: Dict[str, int], path: str):
            if pattern_idx == len(pattern):
                if node.is_word:
                    results.append(path)
                return
            
            pattern_char = pattern[pattern_idx]
            
            if pattern_char == '?':
                # Пробуем все доступные буквы
                for char in letter_counts:
                    if char in node.children:
                        if used_counts.get(char, 0) < letter_counts[char]:
                            new_used = used_counts.copy()
                            new_used[char] = new_used.get(char, 0) + 1
                            dfs(node.children[char], pattern_idx + 1, new_used, path + char)
            else:
                # Конкретная буква из шаблона
                if pattern_char in node.children:
                    dfs(node.children[pattern_char], pattern_idx + 1, used_counts, path + pattern_char)
        
        dfs(self.root, 0, {}, "")
        return results
    
    def __len__(self) -> int:
        """Возвращает количество слов в Trie"""
        return self.word_count
    
    def __contains__(self, word: str) -> bool:
        """Позволяет использовать оператор 'in'"""
        return self.search(word)
