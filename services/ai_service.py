# services/ai_service.py
"""Умный AI для игры Scrabble"""

from typing import List, Tuple, Optional, Set, Dict
import random
from models.trie import Trie
from models.game_state import POINTS


class Move:
    """Представление хода AI"""
    
    def __init__(self, letters: List[Tuple[int, int, str]], score: int, word: str):
        self.letters = letters  # [(r, c, ch), ...]
        self.score = score
        self.word = word
    
    def __repr__(self):
        return f"Move(word='{self.word}', score={self.score})"


class SmartAI:
    """
    Умный AI для Scrabble с использованием продвинутых алгоритмов.
    
    Использует:
    - Trie для быстрого поиска слов
    - Алгоритм якорных точек (anchor points)
    - Оценку позиций и выбор лучшего хода
    """
    
    def __init__(self, dictionary, difficulty: str = "medium"):
        """
        Инициализирует AI.
        
        Args:
            dictionary: Объект словаря
            difficulty: Уровень сложности ('easy', 'medium', 'hard')
        """
        self.dictionary = dictionary
        self.difficulty = difficulty
        self.trie = None
        self._build_trie()
    
    def _build_trie(self):
        """Строит Trie из словаря"""
        print("Building Trie for AI... ", end="")
        self.trie = Trie()
        
        # Добавляем все слова из основного словаря
        for word in self.dictionary.words:
            if len(word) >= 3:
                self.trie.insert(word)
        
        # Добавляем пользовательские слова
        for word in self.dictionary.custom_words:
            if len(word) >= 3:
                self.trie.insert(word)
        
        print(f"Done! {len(self.trie)} words loaded.")
    
    def find_best_move(self, game_state, player: str) -> Optional[Move]:
        """
        Находит лучший ход для AI.
        
        Args:
            game_state: Состояние игры
            player: Имя игрока (AI)
            
        Returns:
            Лучший ход или None если ход невозможен
        """
        rack = game_state.racks[player]
        
        # Если первый ход - простая стратегия
        if game_state.is_first_move():
            return self._find_first_move(game_state, player, rack)
        
        # Находим все возможные ходы
        possible_moves = self._find_all_moves(game_state, player, rack)
        
        if not possible_moves:
            return None
        
        # Выбираем лучший ход в зависимости от сложности
        return self._select_best_move(possible_moves)
    
    def _find_first_move(self, game_state, player: str, rack: List[str]) -> Optional[Move]:
        """Находит ход для первого хода игры"""
        # Ищем все возможные слова из букв в стойке
        possible_words = self.trie.find_words_with_letters(rack, min_length=3, max_length=7)
        
        if not possible_words:
            return None
        
        # Сортируем по длине и очкам
        scored_words = []
        for word in possible_words:
            # Размещаем через центр горизонтально
            start_col = max(0, 7 - len(word) // 2)
            if start_col + len(word) > 15:
                start_col = 15 - len(word)
            
            letters = [(7, start_col + i, ch) for i, ch in enumerate(word)]
            
            # Проверяем валидность
            ok, _ = game_state.can_place(player, letters)
            if ok:
                score, _ = game_state._calc_score(letters)
                scored_words.append((score, word, letters))
        
        if not scored_words:
            return None
        
        # Выбираем слово с максимальными очками
        scored_words.sort(reverse=True)
        score, word, letters = scored_words[0]
        
        return Move(letters, score, word)
    
    def _find_all_moves(self, game_state, player: str, rack: List[str]) -> List[Move]:
        """
        Находит все возможные ходы.
        
        Использует алгоритм якорных точек - для каждой пустой клетки
        рядом с заполненной пробует составить слова.
        """
        moves = []
        anchor_points = self._find_anchor_points(game_state)
        
        # Ограничиваем количество проверяемых якорных точек для производительности
        max_anchors = 20 if self.difficulty == "easy" else 50 if self.difficulty == "medium" else 100
        
        for anchor in anchor_points[:max_anchors]:
            # Пробуем горизонтальные слова
            horizontal_moves = self._try_horizontal_at(game_state, player, rack, anchor)
            moves.extend(horizontal_moves)
            
            # Пробуем вертикальные слова
            vertical_moves = self._try_vertical_at(game_state, player, rack, anchor)
            moves.extend(vertical_moves)
        
        return moves
    
    def _find_anchor_points(self, game_state) -> List[Tuple[int, int]]:
        """
        Находит якорные точки - пустые клетки рядом с занятыми.
        
        Returns:
            Список координат якорных точек
        """
        anchors = set()
        
        for (r, c) in game_state.board.keys():
            # Проверяем соседние клетки
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < 15 and 0 <= nc < 15 and (nr, nc) not in game_state.board:
                    anchors.add((nr, nc))
        
        return list(anchors)
    
    def _try_horizontal_at(self, game_state, player: str, rack: List[str], 
                          anchor: Tuple[int, int]) -> List[Move]:
        """Пробует разместить горизонтальные слова через якорную точку"""
        moves = []
        r, anchor_c = anchor
        
        # Ищем возможные слова длиной 3-7
        possible_words = self.trie.find_words_with_letters(rack, min_length=3, max_length=7)
        
        # Ограничиваем количество проверяемых слов
        max_words = 50 if self.difficulty == "easy" else 150 if self.difficulty == "medium" else 300
        possible_words = possible_words[:max_words]
        
        for word in possible_words:
            # Пробуем разные позиции размещения относительно якорной точки
            for offset in range(len(word)):
                start_c = anchor_c - offset
                if start_c < 0 or start_c + len(word) > 15:
                    continue
                
                letters = [(r, start_c + i, ch) for i, ch in enumerate(word)]
                
                # Проверяем валидность
                ok, _ = game_state.can_place(player, letters)
                if ok:
                    score, _ = game_state._calc_score(letters)
                    moves.append(Move(letters, score, word))
        
        return moves
    
    def _try_vertical_at(self, game_state, player: str, rack: List[str],
                        anchor: Tuple[int, int]) -> List[Move]:
        """Пробует разместить вертикальные слова через якорную точку"""
        moves = []
        anchor_r, c = anchor
        
        # Ищем возможные слова
        possible_words = self.trie.find_words_with_letters(rack, min_length=3, max_length=7)
        
        # Ограничиваем количество проверяемых слов
        max_words = 50 if self.difficulty == "easy" else 150 if self.difficulty == "medium" else 300
        possible_words = possible_words[:max_words]
        
        for word in possible_words:
            # Пробуем разные позиции
            for offset in range(len(word)):
                start_r = anchor_r - offset
                if start_r < 0 or start_r + len(word) > 15:
                    continue
                
                letters = [(start_r + i, c, ch) for i, ch in enumerate(word)]
                
                # Проверяем валидность
                ok, _ = game_state.can_place(player, letters)
                if ok:
                    score, _ = game_state._calc_score(letters)
                    moves.append(Move(letters, score, word))
        
        return moves
    
    def _select_best_move(self, moves: List[Move]) -> Optional[Move]:
        """
        Выбирает лучший ход из списка возможных.
        
        Args:
            moves: Список возможных ходов
            
        Returns:
            Лучший ход
        """
        if not moves:
            return None
        
        # Сортируем по очкам
        moves.sort(key=lambda m: m.score, reverse=True)
        
        if self.difficulty == "easy":
            # Легкий уровень - случайный выбор из топ-30%
            top_count = max(1, len(moves) // 3)
            return random.choice(moves[:top_count])
        
        elif self.difficulty == "medium":
            # Средний уровень - случайный выбор из топ-10%
            top_count = max(1, len(moves) // 10)
            return random.choice(moves[:top_count])
        
        else:  # hard
            # Сложный уровень - всегда лучший ход
            return moves[0]
    
    def __repr__(self):
        return f"SmartAI(difficulty='{self.difficulty}', trie_size={len(self.trie)})"
