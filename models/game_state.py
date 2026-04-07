# models/game_state.py
"""Игровое состояние для Scrabble"""

import random
from typing import Dict, List, Tuple, Set

# Константы
BOARD_SIZE = 15

VOWELS = set("АЕЁИОУЫЭЮЯ")
CONSONANTS = set("БВГДЖЗЙКЛМНПРСТФХЦЧШЩЪЬ")

POINTS = {
    'А': 1, 'Б': 3, 'В': 1, 'Г': 3, 'Д': 2, 'Е': 1, 'Ё': 3, 'Ж': 5, 'З': 5, 'И': 1,
    'Й': 4, 'К': 2, 'Л': 2, 'М': 2, 'Н': 1, 'О': 1, 'П': 2, 'Р': 1, 'С': 1, 'Т': 1,
    'У': 2, 'Ф': 10, 'Х': 5, 'Ц': 5, 'Ч': 5, 'Ш': 8, 'Щ': 10, 'Ъ': 10, 'Ы': 4,
    'Ь': 3, 'Э': 8, 'Ю': 8, 'Я': 3
}

# Типы для подсказок типов
Position = Tuple[int, int]
Letter = Tuple[int, int, str]  # (row, col, char)
BonusType = Tuple[str, int]  # ("LETTER"|"WORD", multiplier)


def generate_bonus_spots() -> Dict[Position, BonusType]:
    """
    Генерирует бонусные клетки на доске.
    
    Returns:
        Словарь позиций бонусов {(r, c): ("LETTER"|"WORD", multiplier)}
    """
    cells = [(r, c) for r in range(15) for c in range(15) if (r, c) != (7, 7)]
    random.shuffle(cells)
    
    bonuses: Dict[Position, BonusType] = {(7, 7): ("WORD", 2)}
    for r, c in cells[:10]:
        bonuses[(r, c)] = (
            random.choice(["LETTER", "WORD"]),
            random.choice([2, 3])
        )
    return bonuses


class GameState:
    """
    Состояние игры Scrabble.
    
    Управляет игровым полем, стойками игроков, счетом и правилами игры.
    """
    
    def __init__(self, players: List[str], dictionary):
        """
        Инициализирует игровое состояние.
        
        Args:
            players: Список имен игроков
            dictionary: Объект словаря для проверки слов
        """
        self.players = players
        self.dictionary = dictionary
        
        # Игровое поле: {(r,c): ch}
        self.board: Dict[Position, str] = {}
        
        # Бонусные клетки
        self.used_bonus: Set[Position] = set()
        self.bonus_spots = generate_bonus_spots()
        
        # Мешок с буквами и стойки игроков
        self.bag: List[str] = []
        self.racks: Dict[str, List[str]] = {p: [] for p in players}
        self.scores: Dict[str, int] = {p: 0 for p in players}
        self.current = players[0]
        
        # Инициализация игры
        self._init_bag()
        for p in players:
            self._deal_initial_rack(p)
    
    def _init_bag(self) -> None:
        """Инициализирует мешок с буквами"""
        letter_distribution = [
            ('А', 10), ('О', 10), ('Е', 8), ('И', 8), ('Н', 6),
            ('Р', 6), ('Т', 6), ('С', 5), ('В', 4), ('Л', 4),
            ('К', 3), ('М', 3), ('Д', 3), ('П', 3), ('У', 3),
            ('Б', 2), ('Г', 2), ('Ж', 1), ('З', 2), ('Й', 1)
        ]
        
        for ch, cnt in letter_distribution:
            self.bag += [ch] * cnt
        random.shuffle(self.bag)
    
    def _deal_initial_rack(self, player: str) -> None:
        """
        Раздает начальную стойку игроку.
        
        Args:
            player: Имя игрока
        """
        rack = []
        while len(rack) < 7 and self.bag:
            ch = self.bag.pop()
            if rack.count(ch) < 2:
                rack.append(ch)
        self.racks[player] = rack
    
    def refill_rack(self, player: str) -> None:
        """
        Пополняет стойку игрока до 7 букв.
        
        Args:
            player: Имя игрока
        """
        rack = self.racks[player]
        while len(rack) < 7 and self.bag:
            ch = self.bag.pop()
            if rack.count(ch) < 2:
                rack.append(ch)
    
    def is_first_move(self) -> bool:
        """
        Проверяет, является ли ход первым в игре.
        
        Returns:
            True если доска пуста
        """
        return not self.board
    
    def _collect_word(
        self,
        r: int,
        c: int,
        dr: int,
        dc: int,
        placed: Dict[Position, str]
    ) -> Tuple[str, List[Position]]:
        """
        Собирает слово из размещенных букв в указанном направлении.
        
        Args:
            r, c: Начальная позиция
            dr, dc: Направление (1,0) для вертикали, (0,1) для горизонтали
            placed: Словарь размещенных букв в текущем ходе
            
        Returns:
            Кортеж (слово, список координат)
        """
        # Найти начало слова
        while (r - dr, c - dc) in self.board:
            r -= dr
            c -= dc
        
        word = ""
        coords = []
        while (r, c) in self.board or (r, c) in placed:
            ch = placed.get((r, c)) or self.board.get((r, c))
            if ch:
                word += ch
            coords.append((r, c))
            r += dr
            c += dc
        
        return word, coords
    
    def can_place(self, player: str, letters: List[Letter]) -> Tuple[bool, str]:
        """
        Проверяет возможность размещения букв на доске.
        
        Args:
            player: Имя игрока
            letters: Список размещаемых букв [(r, c, ch), ...]
            
        Returns:
            Кортеж (валидность, сообщение об ошибке)
        """
        if not letters:
            return False, "Нет букв"
        
        # НОВОЕ ПРАВИЛО: Проверка что буквы не ставятся на уже занятые клетки
        for r, c, ch in letters:
            if (r, c) in self.board:
                return False, f"Клетка ({r}, {c}) уже занята буквой '{self.board[(r, c)]}'"
        
        placed = {(r, c): ch for r, c, ch in letters}
        rows = {r for r, _, _ in letters}
        cols = {c for _, c, _ in letters}
        
        # Проверка ориентации
        if len(rows) != 1 and len(cols) != 1:
            return False, "Слово должно быть горизонтальным или вертикальным"
        
        # Определение направления
        dr, dc = (0, 1) if len(rows) == 1 else (1, 0)
        r0, c0, _ = letters[0]
        
        # Сбор основного слова
        main_word, coords = self._collect_word(r0, c0, dr, dc, placed)
        
        # Проверка первого хода
        if self.is_first_move() and (7, 7) not in coords:
            return False, "Первое слово должно проходить через центр"
        
        # КЛАССИЧЕСКОЕ ПРАВИЛО SCRABBLE: Новые слова должны использовать существующие буквы
        # (кроме первого хода)
        if not self.is_first_move():
            # Проверяем что основное слово ПРОХОДИТ ЧЕРЕЗ существующую букву
            # (а не просто примыкает рядом)
            uses_existing_letter = False
            
            for pos in coords:
                # Если в составе основного слова есть уже размещенная буква
                if pos in self.board and pos not in placed:
                    uses_existing_letter = True
                    break
            
            # Если не используем существующие буквы в основном слове,
            # проверяем что хотя бы создаем валидное побочное слово
            if not uses_existing_letter:
                # Проверяем создаются ли побочные слова (пересечения)
                has_cross_word = False
                for r, c, ch in letters:
                    sdr, sdc = (1, 0) if dr == 0 else (0, 1)
                    w, wcoords = self._collect_word(r, c, sdr, sdc, placed)
                    # Побочное слово должно включать существующие буквы
                    if len(w) >= 2:
                        for wpos in wcoords:
                            if wpos in self.board and wpos not in placed:
                                has_cross_word = True
                                break
                
                if not uses_existing_letter and not has_cross_word:
                    return False, "Новое слово должно использовать существующие буквы (проходить через них или создавать пересечения)"
        
        # НОВОЕ ПРАВИЛО: Проверка минимальной длины слова (минимум 3 буквы)
        if len(main_word) < 3:
            return False, f"Слово должно содержать минимум 3 буквы (сейчас {len(main_word)})"
        
        # Проверка основного слова в словаре
        if not self.dictionary.is_word(main_word):
            return False, f"Слова «{main_word}» нет в словаре"
        
        # Проверка побочных слов
        for r, c, ch in letters:
            sdr, sdc = (1, 0) if dr == 0 else (0, 1)
            w, _ = self._collect_word(r, c, sdr, sdc, placed)
            # НОВОЕ ПРАВИЛО: Побочные слова тоже должны быть минимум 3 буквы
            if len(w) >= 3 and not self.dictionary.is_word(w):
                return False, f"Побочное слово «{w}» недопустимо"
            elif len(w) == 2:
                return False, f"Побочное слово «{w}» слишком короткое (минимум 3 буквы)"
        
        return True, "OK"
    
    def apply_move(self, player: str, letters: List[Letter]) -> None:
        """
        Применяет ход игрока.
        
        Args:
            player: Имя игрока
            letters: Список размещаемых букв [(r, c, ch), ...]
        """
        score, used = self._calc_score(letters)
        
        # Размещение букв на доске
        for r, c, ch in letters:
            self.board[(r, c)] = ch
            self.racks[player].remove(ch)
        
        # Обновление бонусов и счета
        self.used_bonus |= used
        self.scores[player] += score
        self.refill_rack(player)
        
        # Смена игрока
        self._next_player()
    
    def _next_player(self) -> None:
        """Переключает текущего игрока на следующего"""
        current_idx = self.players.index(self.current)
        self.current = self.players[(current_idx + 1) % len(self.players)]
    
    def _calc_score(self, letters: List[Letter]) -> Tuple[int, Set[Position]]:
        """
        Подсчитывает очки за ход.
        
        Args:
            letters: Список размещаемых букв [(r, c, ch), ...]
            
        Returns:
            Кортеж (очки, множество использованных бонусов)
        """
        total = 0
        word_mult = 1
        used = set()
        
        for r, c, ch in letters:
            ls = POINTS[ch]
            if (r, c) in self.bonus_spots and (r, c) not in self.used_bonus:
                kind, mult = self.bonus_spots[(r, c)]
                if kind == "LETTER":
                    ls *= mult
                else:
                    word_mult *= mult
                used.add((r, c))
            total += ls
        
        # Бонус за использование всех 7 букв
        if len(letters) == 7:
            total += 50
        
        return total * word_mult, used
    
    def swap_letters(self, player: str, letters: List[str]) -> None:
        """
        Обменивает буквы игрока.
        
        Args:
            player: Имя игрока
            letters: Список букв для обмена
        """
        for ch in letters:
            self.racks[player].remove(ch)
            self.bag.append(ch)
        random.shuffle(self.bag)
        self.refill_rack(player)
        self._next_player()
