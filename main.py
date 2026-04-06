# main.py
import tkinter as tk
from tkinter import messagebox
import ctypes
import random
from models.dictionary import ScrabbleDictionary
from models.game_state import GameState
from ui_styles import Colors, Fonts, Sizes, ButtonStyles, GameStyles, create_3d_tile

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass


# ---------- APP ----------
class ScrabbleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Scrabble - Эрудит")
        self.root.geometry(f"{Sizes.WINDOW_WIDTH}x{Sizes.WINDOW_HEIGHT}")
        self.root.configure(bg=Colors.BG_DARK)

        self.selected_tile = None      # (index, ch)
        self.turn_letters = []         # [(r,c,index,ch)]

        self.swap_mode = False
        self.swap_selected = []
        self.swap_cooldown = 0
        
        # Для подсветки последнего хода
        self.last_move = []            # [(r, c)] - координаты последнего хода
        self.highlight_timer = None    # Таймер для анимации

        self.build_menu()

    # ---------- MENU ----------
    def build_menu(self):
        self.menu = tk.Frame(self.root, bg=Colors.BG_DARK, padx=40, pady=40)
        self.menu.pack(expand=True, fill='both')

        # Заголовок с эффектом
        title = tk.Label(self.menu, text="🎲 SCRABBLE", 
                        font=Fonts.TITLE,
                        bg=Colors.BG_DARK,
                        fg=Colors.PRIMARY)
        title.pack(pady=(20, 10))
        
        subtitle = tk.Label(self.menu, text="Эрудит - Русская версия", 
                           font=Fonts.SMALL,
                           bg=Colors.BG_DARK,
                           fg=Colors.TEXT_SECONDARY)
        subtitle.pack(pady=(0, 30))

        # Рамка для выбора режима
        mode_frame = tk.Frame(self.menu, bg=Colors.BG_CARD, padx=20, pady=20)
        mode_frame.pack(pady=10, fill='x')
        
        tk.Label(mode_frame, text="Выберите режим игры:", 
                font=Fonts.HEADER,
                bg=Colors.BG_CARD,
                fg=Colors.TEXT_LIGHT).pack(anchor='w', pady=(0, 10))

        self.mode = tk.StringVar(value="pvp")
        
        rb1 = tk.Radiobutton(mode_frame, text="👥 Игрок против Игрока (PvP)", 
                            variable=self.mode,
                            value="pvp", 
                            command=self.update_menu,
                            bg=Colors.BG_CARD,
                            fg=Colors.TEXT_LIGHT,
                            font=Fonts.BODY,
                            selectcolor=Colors.BG_LIGHT,
                            activebackground=Colors.BG_CARD,
                            activeforeground=Colors.SUCCESS,
                            cursor='hand2')
        rb1.pack(anchor="w", pady=5)
        
        rb2 = tk.Radiobutton(mode_frame, text="🤖 Игрок против AI", 
                            variable=self.mode,
                            value="ai", 
                            command=self.update_menu,
                            bg=Colors.BG_CARD,
                            fg=Colors.TEXT_LIGHT,
                            font=Fonts.BODY,
                            selectcolor=Colors.BG_LIGHT,
                            activebackground=Colors.BG_CARD,
                            activeforeground=Colors.SUCCESS,
                            cursor='hand2')
        rb2.pack(anchor="w", pady=5)

        # Поля ввода имен
        input_frame = tk.Frame(self.menu, bg=Colors.BG_DARK)
        input_frame.pack(pady=20)
        
        tk.Label(input_frame, text="Имя игрока 1:", 
                font=Fonts.BODY,
                bg=Colors.BG_DARK,
                fg=Colors.TEXT_SECONDARY).pack(anchor='w')
        
        self.e1 = tk.Entry(input_frame, 
                          font=Fonts.HEADER,
                          bg=Colors.BG_CARD,
                          fg=Colors.TEXT_LIGHT,
                          insertbackground=Colors.TEXT_LIGHT,
                          relief='flat',
                          width=25)
        self.e1.insert(0, "Игрок 1")
        self.e1.pack(pady=(5, 15), ipady=5)

        self.e2_label = tk.Label(input_frame, text="Имя игрока 2:", 
                                font=Fonts.BODY,
                                bg=Colors.BG_DARK,
                                fg=Colors.TEXT_SECONDARY)
        self.e2_label.pack(anchor='w')
        
        self.e2 = tk.Entry(input_frame,
                          font=Fonts.HEADER,
                          bg=Colors.BG_CARD,
                          fg=Colors.TEXT_LIGHT,
                          insertbackground=Colors.TEXT_LIGHT,
                          relief='flat',
                          width=25)
        self.e2.insert(0, "Игрок 2")
        self.e2.pack(pady=(5, 10), ipady=5)

        self.update_menu()

        # Кнопка запуска
        start_btn = tk.Button(self.menu, text="▶ НАЧАТЬ ИГРУ",
                             command=self.start_game,
                             **ButtonStyles.PRIMARY)
        start_btn.pack(pady=30)

    def update_menu(self):
        if self.mode.get() == "ai":
            self.e2.pack_forget()
            self.e2_label.pack_forget()
        else:
            if not self.e2_label.winfo_ismapped():
                self.e2_label.pack(anchor='w')
                self.e2.pack(pady=(5, 10), ipady=5)

    # ---------- START ----------
    def start_game(self):
        self.player1 = self.e1.get()
        if self.mode.get() == "ai":
            self.player2 = "Степан"
            self.is_ai = True
        else:
            self.player2 = self.e2.get()
            self.is_ai = False

        self.menu.destroy()

        self.dictionary = ScrabbleDictionary()
        self.state = GameState([self.player1, self.player2], self.dictionary)
        self.current = self.state.current

        self.build_ui()
        self.refresh()

    # ---------- UI ----------
    def build_ui(self):
        # Главный контейнер
        main_container = tk.Frame(self.root, bg=Colors.BG_DARK)
        main_container.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Панель информации (сверху) - двухцветная
        info_panel = tk.Frame(main_container, bg=Colors.BG_CARD, height=85)
        info_panel.pack(fill='x', pady=(0, 15))
        info_panel.pack_propagate(False)
        
        self.info = tk.Label(info_panel, 
                            font=Fonts.SCORE,
                            bg=Colors.BG_CARD,
                            fg=Colors.TEXT_LIGHT,
                            pady=15,
                            justify='center')
        self.info.pack(expand=True)
        
        # Игровое поле
        board_container = tk.Frame(main_container, bg=Colors.BG_DARK)
        board_container.pack(pady=(0, 15))
        
        # Заголовок доски
        tk.Label(board_container, text="Игровое поле 15×15", 
                font=Fonts.BODY,
                bg=Colors.BG_DARK,
                fg=Colors.TEXT_SECONDARY).pack(pady=(0, 5))
        
        board_frame = tk.Frame(board_container, bg=Colors.BOARD_BG, 
                              relief='raised', borderwidth=4)
        board_frame.pack()
        
        self.board = tk.Canvas(board_frame, 
                              width=Sizes.BOARD_SIZE, 
                              height=Sizes.BOARD_SIZE,
                              bg=Colors.BOARD_BG,
                              highlightthickness=0)
        self.board.pack(padx=5, pady=5)
        self.board.bind("<Button-1>", self.on_board_click)

        # Стойка с буквами
        rack_frame = tk.Frame(main_container, bg=Colors.BG_CARD, 
                             relief='flat', borderwidth=0)
        rack_frame.pack(pady=(0, 15))
        
        tk.Label(rack_frame, text="Ваши буквы:", 
                font=Fonts.BODY,
                bg=Colors.BG_CARD,
                fg=Colors.TEXT_SECONDARY).pack(pady=(5, 5))
        
        self.rack = tk.Canvas(rack_frame, 
                             width=Sizes.RACK_WIDTH, 
                             height=Sizes.RACK_HEIGHT,
                             bg=Colors.BG_CARD,
                             highlightthickness=0)
        self.rack.pack(padx=10, pady=(0, 10))
        self.rack.bind("<Button-1>", self.on_rack_click)

        # Кнопки управления
        btns = tk.Frame(main_container, bg=Colors.BG_DARK)
        btns.pack(pady=(0, 10))

        tk.Button(btns, text="✓ Ход",
                  command=self.confirm_turn,
                  **ButtonStyles.SUCCESS).pack(side="left", padx=5)
        
        tk.Button(btns, text="↩ Отмена",
                  command=self.cancel_turn,
                  **ButtonStyles.SECONDARY).pack(side="left", padx=5)
        
        tk.Button(btns, text="🔁 Замена",
                  command=self.toggle_swap,
                  **ButtonStyles.WARNING).pack(side="left", padx=5)
        
        tk.Button(btns, text="📖 Словарь",
                  command=self.add_word_to_dictionary,
                  **ButtonStyles.PRIMARY).pack(side="left", padx=5)

    # ---------- DRAW ----------
    def refresh(self):
        self.board.delete("all")

        for r in range(15):
            for c in range(15):
                x, y = c * Sizes.CELL_SIZE, r * Sizes.CELL_SIZE
                
                # Определяем стиль клетки
                if (r, c) in self.last_move:
                    # Подсветка последнего хода - яркая с тенью
                    # Тень
                    self.board.create_rectangle(
                        x + 2, y + 2, x + Sizes.CELL_SIZE + 2, y + Sizes.CELL_SIZE + 2,
                        fill="#00000030", outline=""
                    )
                    # Клетка
                    self.board.create_rectangle(
                        x + 1, y + 1, x + Sizes.CELL_SIZE - 1, y + Sizes.CELL_SIZE - 1,
                        fill=Colors.HIGHLIGHT, outline=Colors.HIGHLIGHT_BORDER, width=3
                    )
                elif (r, c) in self.state.board:
                    # Занятая клетка - с легкой тенью
                    self.board.create_rectangle(
                        x + 1, y + 1, x + Sizes.CELL_SIZE - 1, y + Sizes.CELL_SIZE - 1,
                        fill=Colors.CELL_FILLED, outline=Colors.CELL_OUTLINE, width=1
                    )
                elif (r, c) in self.state.bonus_spots:
                    kind, mult = self.state.bonus_spots[(r, c)]
                    if kind == "WORD":
                        fill = Colors.BONUS_WORD_3X if mult == 3 else Colors.BONUS_WORD_2X
                    else:
                        fill = Colors.BONUS_LETTER_3X if mult == 3 else Colors.BONUS_LETTER_2X
                    
                    # Бонусная клетка с градиентом (упрощенный)
                    self.board.create_rectangle(
                        x + 1, y + 1, x + Sizes.CELL_SIZE - 1, y + Sizes.CELL_SIZE - 1,
                        fill=fill, outline=Colors.CELL_OUTLINE, width=1
                    )
                else:
                    # Обычная пустая клетка
                    self.board.create_rectangle(
                        x + 1, y + 1, x + Sizes.CELL_SIZE - 1, y + Sizes.CELL_SIZE - 1,
                        fill=Colors.CELL_EMPTY, outline=Colors.CELL_OUTLINE, width=1
                    )
                
                # Центр доски - большая звездочка
                if (r, c) == (7, 7) and (r, c) not in self.state.board:
                    self.board.create_text(
                        x + Sizes.CELL_SIZE // 2, 
                        y + Sizes.CELL_SIZE // 2,
                        text="★", font=Fonts.BONUS_CENTER, fill=Colors.BONUS_WORD_2X
                    )

                # Текст бонуса
                elif (r, c) in self.state.bonus_spots and (r, c) not in self.state.board and (r, c) != (7, 7):
                    kind, mult = self.state.bonus_spots[(r, c)]
                    bonus_text = f"×{mult}"
                    text_color = Colors.TEXT_LIGHT
                    self.board.create_text(
                        x + Sizes.CELL_SIZE // 2, 
                        y + Sizes.CELL_SIZE // 2,
                        text=bonus_text, 
                        font=Fonts.BONUS_TEXT,
                        fill=text_color
                    )

        # Рисуем буквы на доске
        from models.game_state import POINTS
        for (r, c), ch in self.state.board.items():
            x, y = c * Sizes.CELL_SIZE, r * Sizes.CELL_SIZE
            
            if (r, c) in self.last_move:
                # Подсвеченная буква - белая и крупная
                self.board.create_text(
                    x + Sizes.CELL_SIZE // 2,
                    y + Sizes.CELL_SIZE // 2,
                    text=ch, 
                    font=Fonts.TILE_LETTER_LARGE,
                    fill=Colors.HIGHLIGHT_TEXT
                )
                # Очки за букву
                points = POINTS.get(ch, 0)
                self.board.create_text(
                    x + Sizes.CELL_SIZE - 6,
                    y + Sizes.CELL_SIZE - 6,
                    text=str(points),
                    font=Fonts.TILE_POINTS,
                    fill=Colors.HIGHLIGHT_TEXT
                )
            else:
                # Обычная буква - темная на светлой клетке
                self.board.create_text(
                    x + Sizes.CELL_SIZE // 2,
                    y + Sizes.CELL_SIZE // 2,
                    text=ch, 
                    font=Fonts.TILE_LETTER,
                    fill="#2c3e50"
                )
                # Очки за букву в правом нижнем углу
                points = POINTS.get(ch, 0)
                self.board.create_text(
                    x + Sizes.CELL_SIZE - 6,
                    y + Sizes.CELL_SIZE - 6,
                    text=str(points),
                    font=Fonts.TILE_POINTS,
                    fill="#7f8c8d"
                )

        # Рисуем превью размещения (буквы которые игрок сейчас ставит)
        for r, c, _, ch in self.turn_letters:
            x, y = c * Sizes.CELL_SIZE, r * Sizes.CELL_SIZE
            
            # Тень превью
            self.board.create_rectangle(
                x + 2, y + 2, x + Sizes.CELL_SIZE + 1, y + Sizes.CELL_SIZE + 1,
                fill="#00000020", outline=""
            )
            # Клетка превью
            self.board.create_rectangle(
                x + 1, y + 1, x + Sizes.CELL_SIZE - 1, y + Sizes.CELL_SIZE - 1,
                fill="#9b59b6", outline="#8e44ad", width=2
            )
            # Буква превью
            self.board.create_text(
                x + Sizes.CELL_SIZE // 2,
                y + Sizes.CELL_SIZE // 2,
                text=ch, 
                font=Fonts.TILE_LETTER,
                fill="white"
            )
            # Очки
            points = POINTS.get(ch, 0)
            self.board.create_text(
                x + Sizes.CELL_SIZE - 6,
                y + Sizes.CELL_SIZE - 6,
                text=str(points),
                font=Fonts.TILE_POINTS,
                fill="white"
            )

        # Рисуем стойку с буквами
        self.rack.delete("all")
        used = {idx for _, _, idx, _ in self.turn_letters}

        from models.game_state import POINTS
        
        for i, ch in enumerate(self.state.racks[self.current]):
            if i in used:
                continue
            
            x = i * 70 + 40
            
            # Определяем цвет плитки
            if self.selected_tile and self.selected_tile[0] == i:
                color_top = Colors.LETTER_SELECTED
                color_shadow = "#0abde3"
            elif i in self.swap_selected:
                color_top = Colors.LETTER_SWAP
                color_shadow = "#ff4757"
            else:
                color_top = Colors.LETTER_TILE
                color_shadow = Colors.LETTER_TILE_SHADOW
            
            # Рисуем плитку с 3D эффектом
            create_3d_tile(self.rack, x, 55, 
                          Sizes.TILE_WIDTH, Sizes.TILE_HEIGHT,
                          color_top, color_shadow, ch, Colors.LETTER_TEXT)
            
            # Очки за букву в углу плитки
            points = POINTS.get(ch, 0)
            self.rack.create_text(x + 22, 82, 
                                 text=str(points), 
                                 font=("Arial", 9, "bold"),
                                 fill="#34495e")

        # Обновляем информационную панель с красивым форматированием
        p1_score = self.state.scores[self.player1]
        p2_score = self.state.scores[self.player2]
        bag_count = len(self.state.bag)
        current_marker = "▶"
        
        # Многострочная информация
        line1 = f"{current_marker if self.current == self.player1 else '  '} {self.player1}: {p1_score} очков"
        line1 += f"     |     {current_marker if self.current == self.player2 else '  '} {self.player2}: {p2_score} очков"
        line2 = f"\n🎲 Букв в мешке: {bag_count}  |  Ход: {self.current}"
        
        self.info.config(text=line1 + line2)

    # ---------- INPUT ----------
    def on_rack_click(self, e):
        idx = e.x // 70  # Обновлено под новые размеры
        rack = self.state.racks[self.current]

        if not (0 <= idx < len(rack)):
            return

        if self.swap_mode:
            if idx in self.swap_selected:
                self.swap_selected.remove(idx)
            elif len(self.swap_selected) < 3:
                self.swap_selected.append(idx)
        else:
            self.selected_tile = (idx, rack[idx])

        self.refresh()

    def on_board_click(self, e):
        if not self.selected_tile or self.swap_mode:
            return

        r, c = e.y // Sizes.CELL_SIZE, e.x // Sizes.CELL_SIZE  # Используем константу
        if (r, c) in self.state.board:
            return

        idx, ch = self.selected_tile
        self.turn_letters.append((r, c, idx, ch))
        self.selected_tile = None
        self.refresh()

    # ---------- TURN ----------
    def cancel_turn(self):
        self.turn_letters.clear()
        self.selected_tile = None
        self.swap_selected.clear()
        self.swap_mode = False
        self.refresh()

    def confirm_turn(self):
        if not self.turn_letters:
            return

        letters = [(r, c, ch) for r, c, _, ch in self.turn_letters]
        ok, msg = self.state.can_place(self.current, letters)

        if not ok:
            messagebox.showerror("Ошибка", msg)
            self.cancel_turn()
            return

        # Применяем ход с подсветкой
        self.apply_move_with_highlight(self.current, letters)
        self.turn_letters.clear()
        self.end_turn()

    # ---------- SWAP ----------
    def toggle_swap(self):
        if self.swap_cooldown > 0:
            messagebox.showinfo("Замена", "Замена доступна раз в 3 хода")
            return

        if not self.swap_mode:
            self.swap_mode = True
            self.swap_selected.clear()
        else:
            if len(self.swap_selected) != 3:
                messagebox.showinfo("Замена", "Выберите ровно 3 буквы")
                return

            letters = [self.state.racks[self.current][i]
                       for i in self.swap_selected]
            self.state.swap_letters(self.current, letters)
            self.swap_selected.clear()
            self.swap_mode = False
            self.swap_cooldown = 1
            self.end_turn()
            return

        self.refresh()

    # ---------- HIGHLIGHT ----------
    def clear_highlight(self):
        """Убирает подсветку последнего хода"""
        self.last_move = []
        self.refresh()
    
    def apply_move_with_highlight(self, player, letters):
        """Применяет ход с подсветкой"""
        # Сохраняем координаты для подсветки
        self.last_move = [(r, c) for r, c, _ in letters]
        
        # Применяем ход
        self.state.apply_move(player, letters)
        
        # Запускаем таймер для отключения подсветки
        if self.highlight_timer:
            self.root.after_cancel(self.highlight_timer)
        self.highlight_timer = self.root.after(2500, self.clear_highlight)
    
    # ---------- END TURN ----------
    def end_turn(self):
        self.current = self.state.current

        if self.swap_cooldown > 0:
            self.swap_cooldown += 1
            if self.swap_cooldown >= 3:
                self.swap_cooldown = 0

        self.selected_tile = None
        self.swap_selected.clear()
        self.swap_mode = False
        self.refresh()

        if self.is_ai and self.current == self.player2:
            self.root.after(600, self.make_ai_move)
        elif not self.is_ai:
            messagebox.showinfo("Ход", f"Ход игрока: {self.current}")

    # ---------- AI ----------
    def make_ai_move(self):
        """Упрощенный AI - пытается найти слово из имеющихся букв"""
        rack = self.state.racks[self.player2][:]
        
        # Получаем все слова из обоих словарей
        all_words = list(self.dictionary.words | self.dictionary.custom_words)
        
        # Фильтруем только слова длиной 3-7 букв
        all_words = [w for w in all_words if 3 <= len(w) <= 7]
        all_words.sort(key=len)
        random.shuffle(all_words)
        
        # Если это первый ход - пытаемся разместить в центре
        if self.state.is_first_move():
            for word in all_words[:1000]:
                if all(rack.count(c) >= word.count(c) for c in word):
                    start_col = max(0, 7 - len(word) // 2)
                    if start_col + len(word) > 15:
                        start_col = 15 - len(word)
                    
                    letters = [(7, start_col + i, ch) for i, ch in enumerate(word)]
                    ok, msg = self.state.can_place(self.player2, letters)
                    if ok:
                        # Сохраняем координаты для подсветки
                        self.last_move = [(r, c) for r, c, _ in letters]
                        self.state.apply_move(self.player2, letters)
                        # Запускаем таймер для отключения подсветки
                        if self.highlight_timer:
                            self.root.after_cancel(self.highlight_timer)
                        self.highlight_timer = self.root.after(2500, self.clear_highlight)
                        self.end_turn()
                        return
        else:
            # Не первый ход - ПРОСТАЯ СТРАТЕГИЯ: добавляем 2-3 буквы рядом
            
            # Стратегия 1: Добавляем 2 буквы рядом с существующими
            for (r, c) in self.state.board.keys():
                # Пробуем все комбинации из 2 букв из стойки
                for i, letter1 in enumerate(rack):
                    for j, letter2 in enumerate(rack):
                        if i >= j:
                            continue
                        
                        # Горизонтально справа
                        if c < 13 and (r, c+1) not in self.state.board and (r, c+2) not in self.state.board:
                            test_letters = [(r, c+1, letter1), (r, c+2, letter2)]
                            ok, _ = self.state.can_place(self.player2, test_letters)
                            if ok:
                                self.apply_move_with_highlight(self.player2, test_letters)
                                self.end_turn()
                                return
                        
                        # Горизонтально слева
                        if c > 1 and (r, c-1) not in self.state.board and (r, c-2) not in self.state.board:
                            test_letters = [(r, c-2, letter1), (r, c-1, letter2)]
                            ok, _ = self.state.can_place(self.player2, test_letters)
                            if ok:
                                self.apply_move_with_highlight(self.player2, test_letters)
                                self.end_turn()
                                return
                        
                        # Вертикально вниз
                        if r < 13 and (r+1, c) not in self.state.board and (r+2, c) not in self.state.board:
                            test_letters = [(r+1, c, letter1), (r+2, c, letter2)]
                            ok, _ = self.state.can_place(self.player2, test_letters)
                            if ok:
                                self.apply_move_with_highlight(self.player2, test_letters)
                                self.end_turn()
                                return
                        
                        # Вертикально вверх
                        if r > 1 and (r-1, c) not in self.state.board and (r-2, c) not in self.state.board:
                            test_letters = [(r-2, c, letter1), (r-1, c, letter2)]
                            ok, _ = self.state.can_place(self.player2, test_letters)
                            if ok:
                                self.apply_move_with_highlight(self.player2, test_letters)
                                self.end_turn()
                                return
            
            # Стратегия 2: Добавляем 1 букву
            for (r, c) in self.state.board.keys():
                for letter in rack:
                    # Справа
                    if c < 14 and (r, c+1) not in self.state.board:
                        test_letters = [(r, c+1, letter)]
                        ok, _ = self.state.can_place(self.player2, test_letters)
                        if ok:
                            self.apply_move_with_highlight(self.player2, test_letters)
                            self.end_turn()
                            return
                    # Слева
                    if c > 0 and (r, c-1) not in self.state.board:
                        test_letters = [(r, c-1, letter)]
                        ok, _ = self.state.can_place(self.player2, test_letters)
                        if ok:
                            self.apply_move_with_highlight(self.player2, test_letters)
                            self.end_turn()
                            return
                    # Снизу
                    if r < 14 and (r+1, c) not in self.state.board:
                        test_letters = [(r+1, c, letter)]
                        ok, _ = self.state.can_place(self.player2, test_letters)
                        if ok:
                            self.apply_move_with_highlight(self.player2, test_letters)
                            self.end_turn()
                            return
                    # Сверху
                    if r > 0 and (r-1, c) not in self.state.board:
                        test_letters = [(r-1, c, letter)]
                        ok, _ = self.state.can_place(self.player2, test_letters)
                        if ok:
                            self.apply_move_with_highlight(self.player2, test_letters)
                            self.end_turn()
                            return
        
        # Если не нашли ход - меняем буквы или пропускаем
        if len(rack) >= 3 and len(self.state.bag) >= 3:
            to_swap = random.sample(rack, 3)
            self.state.swap_letters(self.player2, to_swap)
            messagebox.showinfo("Ход AI", "AI меняет 3 буквы")
        else:
            self.current = self.player1
            self.state.current = self.player1
            messagebox.showinfo("Ход AI", "AI пропускает ход")
        
        self.refresh()
    
    # ---------- ADD WORD TO DICTIONARY ----------
    def add_word_to_dictionary(self):
        """Открывает диалог для добавления нового слова в словарь"""
        # Создаем диалоговое окно
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить слово в словарь")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Заголовок
        tk.Label(dialog, text="Добавить новое слово", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        # Информация
        info_text = f"Словарь содержит {len(self.dictionary.words)} слов\n"
        if self.dictionary.custom_words:
            info_text += f"Пользовательских слов: {len(self.dictionary.custom_words)}"
        tk.Label(dialog, text=info_text, 
                font=("Arial", 9)).pack(pady=5)
        
        # Поле ввода
        tk.Label(dialog, text="Введите слово (минимум 3 буквы):",
                font=("Arial", 10)).pack(pady=5)
        
        word_entry = tk.Entry(dialog, font=("Arial", 12), width=30)
        word_entry.pack(pady=5)
        word_entry.focus()
        
        # Сообщение об ошибке/успехе
        result_label = tk.Label(dialog, text="", font=("Arial", 9))
        result_label.pack(pady=5)
        
        def add_word():
            """Добавляет слово в словарь"""
            word = word_entry.get().strip()
            success, message = self.dictionary.add_word(word)
            
            if success:
                # Сохраняем в файл
                if self.dictionary.save_custom_words():
                    result_label.config(text=message, fg="green")
                    word_entry.delete(0, tk.END)
                    # Обновляем информацию
                    info_text = f"Словарь содержит {len(self.dictionary.words)} слов\n"
                    info_text += f"Пользовательских слов: {len(self.dictionary.custom_words)}"
                else:
                    result_label.config(text="Ошибка при сохранении!", fg="red")
            else:
                result_label.config(text=message, fg="red")
        
        # Кнопки
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Добавить", width=12,
                 command=add_word).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Закрыть", width=12,
                 command=dialog.destroy).pack(side="left", padx=5)
        
        # Enter для добавления
        word_entry.bind('<Return>', lambda e: add_word())


# ---------- RUN ----------
if __name__ == "__main__":
    root = tk.Tk()
    ScrabbleApp(root)
    root.mainloop()
