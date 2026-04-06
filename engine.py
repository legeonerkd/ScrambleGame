# engine.py
import random

BOARD_SIZE = 15

VOWELS = set("АЕЁИОУЫЭЮЯ")
CONSONANTS = set("БВГДЖЗЙКЛМНПРСТФХЦЧШЩЪЬ")

POINTS = {
    'А':1,'Б':3,'В':1,'Г':3,'Д':2,'Е':1,'Ё':3,'Ж':5,'З':5,'И':1,
    'Й':4,'К':2,'Л':2,'М':2,'Н':1,'О':1,'П':2,'Р':1,'С':1,'Т':1,
    'У':2,'Ф':10,'Х':5,'Ц':5,'Ч':5,'Ш':8,'Щ':10,'Ъ':10,'Ы':4,
    'Ь':3,'Э':8,'Ю':8,'Я':3
}

# ---------- БОНУСЫ ----------
def generate_bonus_spots():
    cells = [(r, c) for r in range(15) for c in range(15) if (r, c) != (7, 7)]
    random.shuffle(cells)

    bonuses = {(7, 7): ("WORD", 2)}
    for r, c in cells[:10]:
        bonuses[(r, c)] = (
            random.choice(["LETTER", "WORD"]),
            random.choice([2, 3])
        )
    return bonuses

# ---------- GAME STATE ----------
class GameState:
    def __init__(self, players, dictionary):
        self.players = players
        self.dictionary = dictionary

        self.board = {}          # {(r,c): ch}
        self.used_bonus = set()
        self.bonus_spots = generate_bonus_spots()

        self.bag = []
        self.racks = {p: [] for p in players}
        self.scores = {p: 0 for p in players}
        self.current = players[0]

        self._init_bag()
        for p in players:
            self._deal_initial_rack(p)

    # ---------- МЕШОК ----------
    def _init_bag(self):
        for ch, cnt in [
            ('А',10),('О',10),('Е',8),('И',8),('Н',6),
            ('Р',6),('Т',6),('С',5),('В',4),('Л',4),
            ('К',3),('М',3),('Д',3),('П',3),('У',3),
            ('Б',2),('Г',2),('Ж',1),('З',2),('Й',1)
        ]:
            self.bag += [ch]*cnt
        random.shuffle(self.bag)

    def _deal_initial_rack(self, player):
        rack = []
        while len(rack) < 7 and self.bag:
            ch = self.bag.pop()
            if rack.count(ch) < 2:
                rack.append(ch)
        self.racks[player] = rack

    def refill_rack(self, player):
        rack = self.racks[player]
        while len(rack) < 7 and self.bag:
            ch = self.bag.pop()
            if rack.count(ch) < 2:
                rack.append(ch)

    # ---------- ПРОВЕРКИ ----------
    def is_first_move(self):
        return not self.board

    def _collect_word(self, r, c, dr, dc, placed):
        while (r-dr, c-dc) in self.board:
            r -= dr
            c -= dc

        word = ""
        coords = []
        while (r, c) in self.board or (r, c) in placed:
            word += placed.get((r, c), self.board.get((r, c)))
            coords.append((r, c))
            r += dr
            c += dc
        return word, coords

    def can_place(self, player, letters):
        if not letters:
            return False, "Нет букв"

        placed = {(r, c): ch for r, c, ch in letters}
        rows = {r for r, _, _ in letters}
        cols = {c for _, c, _ in letters}

        if len(rows) != 1 and len(cols) != 1:
            return False, "Слово должно быть горизонтальным или вертикальным"

        dr, dc = (0, 1) if len(rows) == 1 else (1, 0)
        r0, c0, _ = letters[0]

        main_word, coords = self._collect_word(r0, c0, dr, dc, placed)

        if self.is_first_move() and (7, 7) not in coords:
            return False, "Первое слово должно проходить через центр"

        if len(main_word) < 2 or not self.dictionary.is_word(main_word):
            return False, f"Слова «{main_word}» нет в словаре"

        # побочные слова
        for r, c, ch in letters:
            sdr, sdc = (1, 0) if dr == 0 else (0, 1)
            w, _ = self._collect_word(r, c, sdr, sdc, placed)
            if len(w) >= 2 and not self.dictionary.is_word(w):
                return False, f"Побочное слово «{w}» недопустимо"

        return True, "OK"

    # ---------- ХОД ----------
    def apply_move(self, player, letters):
        score, used = self._calc_score(letters)

        for r, c, ch in letters:
            self.board[(r, c)] = ch
            self.racks[player].remove(ch)

        self.used_bonus |= used
        self.scores[player] += score
        self.refill_rack(player)

        self.current = self.players[1] if player == self.players[0] else self.players[0]

    # ---------- ОЧКИ ----------
    def _calc_score(self, letters):
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

        if len(letters) == 7:
            total += 50

        return total * word_mult, used

    # ---------- ЗАМЕНА ----------
    def swap_letters(self, player, letters):
        for ch in letters:
            self.racks[player].remove(ch)
            self.bag.append(ch)
        random.shuffle(self.bag)
        self.refill_rack(player)
        self.current = self.players[1] if player == self.players[0] else self.players[0]

