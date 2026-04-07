# main.py
import tkinter as tk
from tkinter import messagebox
import ctypes
import random
import math
from models.dictionary import ScrabbleDictionary
from models.game_state import GameState
from ui_styles import Colors, Fonts, Sizes, ButtonStyles, GameStyles, create_3d_tile
from animations import (ScorePopupAnimation, PulseAnimation, ShakeAnimation, 
                       ParticleEffect, create_float_text, create_shake_effect)

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass


# ---------- APP ----------
class ScrabbleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Scrabble - Эрудит")
        
        # Определяем размер экрана
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Выбираем режим в зависимости от размера экрана
        self.is_fullscreen_mode = screen_width >= 1600 and screen_height >= 900
        
        if self.is_fullscreen_mode:
            # Полноэкранный режим для больших мониторов
            self.window_width = Sizes.WINDOW_WIDTH_FULLSCREEN
            self.window_height = Sizes.WINDOW_HEIGHT_FULLSCREEN
            self.board_size = Sizes.BOARD_SIZE_FULLSCREEN
            self.cell_size = Sizes.CELL_SIZE_FULLSCREEN
            self.rack_width = Sizes.RACK_WIDTH_FULLSCREEN
            self.rack_height = Sizes.RACK_HEIGHT_FULLSCREEN
            self.tile_width = Sizes.TILE_WIDTH_FULLSCREEN
            self.tile_height = Sizes.TILE_HEIGHT_FULLSCREEN
            self.tile_spacing = 100
        else:
            # Обычный режим
            self.window_width = Sizes.WINDOW_WIDTH
            self.window_height = Sizes.WINDOW_HEIGHT
            self.board_size = Sizes.BOARD_SIZE
            self.cell_size = Sizes.CELL_SIZE
            self.rack_width = Sizes.RACK_WIDTH
            self.rack_height = Sizes.RACK_HEIGHT
            self.tile_width = Sizes.TILE_WIDTH
            self.tile_height = Sizes.TILE_HEIGHT
            self.tile_spacing = 70
        
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        self.root.configure(bg=Colors.BG_DARK)
        
        # Центрируем окно
        x = (screen_width - self.window_width) // 2
        y = (screen_height - self.window_height) // 2
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

        self.selected_tile = None      # (index, ch)
        self.turn_letters = []         # [(r,c,index,ch)]

        self.swap_mode = False
        self.swap_selected = []
        self.swap_cooldown = 0
        
        # Для подсветки последнего хода
        self.last_move = []            # [(r, c)] - координаты последнего хода
        self.highlight_timer = None    # Таймер для анимации
        
        # Для Drag & Drop
        self.dragging = False          # Идет ли перетаскивание
        self.drag_letter = None        # (index, ch) - перетаскиваемая буква
        self.drag_preview = None       # ID элемента превью на canvas
        self.drag_start_x = 0          # Начальная позиция X
        self.drag_start_y = 0          # Начальная позиция Y
        self.hover_cell = None         # (r, c) - клетка под курсором
        
        # Для анимаций
        self.pulse_animation = PulseAnimation()  # Пульсация бонусов
        self.pulse_time = 0
        self.particles = []            # Активные частицы
        self.fade_in_letters = {}      # {(r, c): progress} - буквы в процессе появления
        self.fade_timer = None

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
        
        # Выбор сложности AI
        self.difficulty_frame = tk.Frame(mode_frame, bg=Colors.BG_CARD)
        
        tk.Label(self.difficulty_frame, text="   Сложность AI:", 
                font=Fonts.SMALL,
                bg=Colors.BG_CARD,
                fg=Colors.TEXT_SECONDARY).pack(anchor='w', pady=(10, 5))
        
        self.ai_difficulty = tk.StringVar(value="medium")
        
        diff_buttons = tk.Frame(self.difficulty_frame, bg=Colors.BG_CARD)
        diff_buttons.pack(anchor='w', padx=20)
        
        tk.Radiobutton(diff_buttons, text="Легко", variable=self.ai_difficulty,
                      value="easy", bg=Colors.BG_CARD, fg=Colors.TEXT_LIGHT,
                      selectcolor=Colors.BG_LIGHT, font=Fonts.SMALL,
                      activebackground=Colors.BG_CARD).pack(side='left', padx=5)
        tk.Radiobutton(diff_buttons, text="Средне", variable=self.ai_difficulty,
                      value="medium", bg=Colors.BG_CARD, fg=Colors.TEXT_LIGHT,
                      selectcolor=Colors.BG_LIGHT, font=Fonts.SMALL,
                      activebackground=Colors.BG_CARD).pack(side='left', padx=5)
        tk.Radiobutton(diff_buttons, text="Сложно", variable=self.ai_difficulty,
                      value="hard", bg=Colors.BG_CARD, fg=Colors.TEXT_LIGHT,
                      selectcolor=Colors.BG_LIGHT, font=Fonts.SMALL,
                      activebackground=Colors.BG_CARD).pack(side='left', padx=5)

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
            # Показываем выбор сложности AI
            if hasattr(self, 'difficulty_frame'):
                self.difficulty_frame.pack(anchor='w', pady=5)
        else:
            # Скрываем выбор сложности AI
            if hasattr(self, 'difficulty_frame'):
                self.difficulty_frame.pack_forget()
            if not self.e2_label.winfo_ismapped():
                self.e2_label.pack(anchor='w')
                self.e2.pack(pady=(5, 10), ipady=5)

    # ---------- START ----------
    def start_game(self):
        self.player1 = self.e1.get()
        if self.mode.get() == "ai":
            self.player2 = "🤖 Степан (AI)"
            self.is_ai = True
        else:
            self.player2 = self.e2.get()
            self.is_ai = False

        self.menu.destroy()

        self.dictionary = ScrabbleDictionary()
        self.state = GameState([self.player1, self.player2], self.dictionary)
        self.current = self.state.current
        
        # Инициализируем SmartAI если играем против AI
        if self.is_ai:
            from services.ai_service import SmartAI
            difficulty = self.ai_difficulty.get()
            self.smart_ai = SmartAI(self.dictionary, difficulty=difficulty)
        else:
            self.smart_ai = None

        self.build_ui()
        self.refresh()
        
        # Запускаем цикл анимации пульсации
        self.animate_pulse()

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
                              width=self.board_size, 
                              height=self.board_size,
                              bg=Colors.BOARD_BG,
                              highlightthickness=0)
        self.board.pack(padx=5, pady=5)
        # Обработчики для клика и drop
        self.board.bind("<Button-1>", self.on_board_click)
        self.board.bind("<Motion>", self.on_board_motion)
        self.board.bind("<ButtonRelease-1>", self.on_board_drop)
        # Правая кнопка для отмены выбора
        self.board.bind("<Button-3>", self.on_board_right_click)

        # Стойка с буквами
        rack_frame = tk.Frame(main_container, bg=Colors.BG_CARD, 
                             relief='flat', borderwidth=0)
        rack_frame.pack(pady=(0, 15))
        
        tk.Label(rack_frame, text="Ваши буквы (перетащите на доску мышью):", 
                font=Fonts.BODY,
                bg=Colors.BG_CARD,
                fg=Colors.TEXT_SECONDARY).pack(pady=(5, 5))
        
        self.rack = tk.Canvas(rack_frame, 
                             width=self.rack_width, 
                             height=self.rack_height,
                             bg=Colors.BG_CARD,
                             highlightthickness=0)
        self.rack.pack(padx=10, pady=(0, 10))
        # Привязываем события для Drag & Drop
        self.rack.bind("<Button-1>", self.on_rack_press)
        self.rack.bind("<B1-Motion>", self.on_rack_drag)
        self.rack.bind("<ButtonRelease-1>", self.on_rack_release)

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

    # ---------- ANIMATIONS ----------
    def animate_pulse(self):
        """Цикл анимации пульсации бонусных клеток"""
        self.pulse_time += 50
        
        # Обновляем частицы
        self.particles = [p for p in self.particles if not p.update(self.pulse_time)]
        
        self.refresh()
        self.root.after(50, self.animate_pulse)  # 20 FPS для пульсации
    
    # ---------- DRAW ----------
    def refresh(self):
        self.board.delete("all")
        
        # Вычисляем масштаб для пульсации
        pulse_scale = self.pulse_animation.get_scale(self.pulse_time)

        for r in range(15):
            for c in range(15):
                x, y = c * self.cell_size, r * self.cell_size
                
                # Определяем стиль клетки
                if self.hover_cell and self.hover_cell == (r, c):
                    # Подсветка клетки под курсором при перетаскивании
                    self.board.create_rectangle(
                        x + 1, y + 1, x + self.cell_size - 1, y + self.cell_size - 1,
                        fill="#a29bfe", outline="#6c5ce7", width=3
                    )
                elif (r, c) in self.last_move:
                    # Подсветка последнего хода - яркая с тенью
                    # Тень (используем серый вместо прозрачного)
                    self.board.create_rectangle(
                        x + 2, y + 2, x + self.cell_size + 2, y + self.cell_size + 2,
                        fill="#7f8c8d", outline=""
                    )
                    # Клетка
                    self.board.create_rectangle(
                        x + 1, y + 1, x + self.cell_size - 1, y + self.cell_size - 1,
                        fill=Colors.HIGHLIGHT, outline=Colors.HIGHLIGHT_BORDER, width=3
                    )
                elif (r, c) in self.state.board:
                    # Занятая клетка - с легкой тенью
                    self.board.create_rectangle(
                        x + 1, y + 1, x + self.cell_size - 1, y + self.cell_size - 1,
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
                        x + 1, y + 1, x + self.cell_size - 1, y + self.cell_size - 1,
                        fill=fill, outline=Colors.CELL_OUTLINE, width=1
                    )
                else:
                    # Обычная пустая клетка
                    self.board.create_rectangle(
                        x + 1, y + 1, x + self.cell_size - 1, y + self.cell_size - 1,
                        fill=Colors.CELL_EMPTY, outline=Colors.CELL_OUTLINE, width=1
                    )
                
                # Центр доски - большая звездочка с пульсацией
                if (r, c) == (7, 7) and (r, c) not in self.state.board:
                    # Пульсирующая звездочка
                    star_size = int(20 * pulse_scale)
                    self.board.create_text(
                        x + self.cell_size // 2, 
                        y + self.cell_size // 2,
                        text="★", font=("Arial", star_size), fill=Colors.BONUS_WORD_2X
                    )

                # Текст бонуса с пульсацией
                elif (r, c) in self.state.bonus_spots and (r, c) not in self.state.board and (r, c) != (7, 7):
                    kind, mult = self.state.bonus_spots[(r, c)]
                    bonus_text = f"×{mult}"
                    text_color = Colors.TEXT_LIGHT
                    
                    # Размер текста с пульсацией
                    bonus_size = int(8 * pulse_scale)
                    self.board.create_text(
                        x + self.cell_size // 2, 
                        y + self.cell_size // 2,
                        text=bonus_text, 
                        font=("Arial", bonus_size, "bold"),
                        fill=text_color
                    )

        # Рисуем буквы на доске
        from models.game_state import POINTS
        for (r, c), ch in self.state.board.items():
            x, y = c * self.cell_size, r * self.cell_size
            
            # Проверяем fade-in анимацию
            fade_progress = self.fade_in_letters.get((r, c), 1.0)
            is_fading = (r, c) in self.fade_in_letters
            
            # Эффект масштабирования при появлении
            if is_fading:
                scale = 0.5 + 0.5 * fade_progress
                font_size = int(18 * scale)
                letter_font = ("Arial", font_size, "bold")
            else:
                letter_font = Fonts.TILE_LETTER_LARGE if (r, c) in self.last_move else Fonts.TILE_LETTER
            
            if (r, c) in self.last_move:
                # Подсвеченная буква - белая и крупная
                self.board.create_text(
                    x + self.cell_size // 2,
                    y + self.cell_size // 2,
                    text=ch, 
                    font=letter_font,
                    fill=Colors.HIGHLIGHT_TEXT
                )
                # Очки за букву
                points = POINTS.get(ch, 0)
                self.board.create_text(
                    x + self.cell_size - 6,
                    y + self.cell_size - 6,
                    text=str(points),
                    font=Fonts.TILE_POINTS,
                    fill=Colors.HIGHLIGHT_TEXT
                )
            else:
                # Обычная буква - темная на светлой клетке
                self.board.create_text(
                    x + self.cell_size // 2,
                    y + self.cell_size // 2,
                    text=ch, 
                    font=letter_font,
                    fill="#2c3e50"
                )
                # Очки за букву в правом нижнем углу
                points = POINTS.get(ch, 0)
                self.board.create_text(
                    x + self.cell_size - 6,
                    y + self.cell_size - 6,
                    text=str(points),
                    font=Fonts.TILE_POINTS,
                    fill="#7f8c8d"
                )

        # Рисуем превью размещения (буквы которые игрок сейчас ставит)
        for r, c, _, ch in self.turn_letters:
            x, y = c * self.cell_size, r * self.cell_size
            
            # Тень превью (используем темно-фиолетовый)
            self.board.create_rectangle(
                x + 2, y + 2, x + self.cell_size + 1, y + self.cell_size + 1,
                fill="#6c5ce7", outline=""
            )
            # Клетка превью
            self.board.create_rectangle(
                x + 1, y + 1, x + self.cell_size - 1, y + self.cell_size - 1,
                fill="#9b59b6", outline="#8e44ad", width=2
            )
            # Буква превью
            self.board.create_text(
                x + self.cell_size // 2,
                y + self.cell_size // 2,
                text=ch, 
                font=Fonts.TILE_LETTER,
                fill="white"
            )
            # Очки
            points = POINTS.get(ch, 0)
            self.board.create_text(
                x + self.cell_size - 6,
                y + self.cell_size - 6,
                text=str(points),
                font=Fonts.TILE_POINTS,
                fill="white"
            )

        # Рисуем стойку с буквами
        self.rack.delete("all")
        used = {idx for _, _, idx, _ in self.turn_letters}

        from models.game_state import POINTS
        
        current_rack = self.state.racks.get(self.current, [])
        
        for i, ch in enumerate(current_rack):
            if i in used:
                continue
            
            # Простой расчет позиции
            x = i * self.tile_spacing + 45
            y = self.rack_height // 2
            
            # Определяем цвет плитки
            if self.selected_tile and self.selected_tile[0] == i:
                fill_color = Colors.LETTER_SELECTED
                outline_color = "#0abde3"
            elif i in self.swap_selected:
                fill_color = Colors.LETTER_SWAP
                outline_color = "#ff4757"
            else:
                fill_color = Colors.LETTER_TILE
                outline_color = Colors.LETTER_TILE_SHADOW
            
            # Рисуем плитку простым способом (без 3D пока)
            half_w = self.tile_width // 2
            half_h = self.tile_height // 2
            
            # Тень
            self.rack.create_rectangle(
                x - half_w + 3, y - half_h + 3,
                x + half_w + 3, y + half_h + 3,
                fill=outline_color, outline=""
            )
            
            # Основная плитка
            self.rack.create_rectangle(
                x - half_w, y - half_h,
                x + half_w, y + half_h,
                fill=fill_color, outline=outline_color, width=2
            )
            
            # Буква
            self.rack.create_text(x, y, 
                                 text=ch, 
                                 font=Fonts.TILE_LETTER,
                                 fill=Colors.LETTER_TEXT,
                                 anchor="center")
            
            # Очки за букву
            points = POINTS.get(ch, 0)
            self.rack.create_text(x + half_w - 10, y + half_h - 10, 
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

    # ---------- DRAG & DROP ----------
    def on_rack_press(self, e):
        """Начало перетаскивания буквы"""
        idx = e.x // self.tile_spacing
        rack = self.state.racks[self.current]

        if not (0 <= idx < len(rack)):
            return
        
        # Проверяем что буква не используется
        used = {i for _, _, i, _ in self.turn_letters}
        if idx in used:
            return

        if self.swap_mode:
            # В режиме замены - просто выбираем
            if idx in self.swap_selected:
                self.swap_selected.remove(idx)
            elif len(self.swap_selected) < 3:
                self.swap_selected.append(idx)
            self.refresh()
        else:
            # Начинаем перетаскивание
            self.dragging = True
            self.drag_letter = (idx, rack[idx])
            self.drag_start_x = e.x
            self.drag_start_y = e.y
            self.selected_tile = (idx, rack[idx])
            self.refresh()
    
    def on_rack_drag(self, e):
        """Перетаскивание буквы по стойке"""
        if not self.dragging or not self.drag_letter:
            return
        
        # Если курсор над доской - показываем где упадет буква
        # Преобразуем координаты из rack в board
        board_widget = self.board
        
        # Получаем координаты доски относительно окна
        try:
            board_x = board_widget.winfo_rootx()
            board_y = board_widget.winfo_rooty()
            rack_x = self.rack.winfo_rootx()
            rack_y = self.rack.winfo_rooty()
            
            # Координаты курсора относительно окна
            cursor_x = rack_x + e.x
            cursor_y = rack_y + e.y
            
            # Проверяем находится ли курсор над доской
            if (board_x <= cursor_x <= board_x + self.board_size and
                board_y <= cursor_y <= board_y + self.board_size):
                # Вычисляем клетку на доске
                rel_x = cursor_x - board_x
                rel_y = cursor_y - board_y
                c = rel_x // self.cell_size
                r = rel_y // self.cell_size
                
                if 0 <= r < 15 and 0 <= c < 15:
                    self.hover_cell = (r, c)
                    self.refresh()
        except:
            pass
    
    def on_rack_release(self, e):
        """Отпускание кнопки мыши на стойке"""
        if self.dragging:
            self.dragging = False
            # Буква осталась выбранной для размещения на доске
    
    def on_board_motion(self, e):
        """Движение мыши над доской (для превью позиции)"""
        if not self.selected_tile or self.swap_mode:
            self.hover_cell = None
            return
        
        # Определяем клетку под курсором
        r, c = e.y // self.cell_size, e.x // self.cell_size
        
        if 0 <= r < 15 and 0 <= c < 15 and (r, c) not in self.state.board:
            if self.hover_cell != (r, c):
                self.hover_cell = (r, c)
                self.refresh()
        else:
            if self.hover_cell is not None:
                self.hover_cell = None
                self.refresh()
    
    def on_board_drop(self, e):
        """Отпускание буквы на доске (Drag & Drop)"""
        if not self.selected_tile or self.swap_mode:
            return

        r, c = e.y // self.cell_size, e.x // self.cell_size
        
        # Проверяем границы
        if not (0 <= r < 15 and 0 <= c < 15):
            return
        
        if (r, c) in self.state.board:
            return

        idx, ch = self.selected_tile
        self.turn_letters.append((r, c, idx, ch))
        self.selected_tile = None
        self.dragging = False
        self.refresh()

    def on_board_click(self, e):
        """Клик на доске (старый метод, для обратной совместимости)"""
        # Теперь используется on_board_drop, но оставляем для совместимости
        pass
    
    def on_board_right_click(self, e):
        """Правый клик на доске - возврат последней буквы на стойку"""
        if not self.turn_letters:
            return
        
        # Убираем последнюю размещенную букву
        self.turn_letters.pop()
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
            # Встряхивание при ошибке
            messagebox.showerror("Ошибка", msg)
            self.cancel_turn()
            return

        # Вычисляем очки ДО применения хода
        score, _ = self.state._calc_score(letters)
        
        # Применяем ход с подсветкой
        self.apply_move_with_highlight(self.current, letters)
        
        # Анимация всплывающих очков в центре слова
        if letters:
            center_r = sum(r for r, c, _ in letters) // len(letters)
            center_c = sum(c for r, c, _ in letters) // len(letters)
            x = center_c * self.cell_size + self.cell_size // 2
            y = center_r * self.cell_size + self.cell_size // 2
            
            # Всплывающий текст с очками
            create_float_text(self.board, x, y + 30, f"+{score}", Colors.SUCCESS, 1200)
            
            # Если использовали все 7 букв - конфетти!
            if len(letters) == 7:
                particle = ParticleEffect(self.board, x, y, count=30)
                self.particles.append(particle)
        
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
        """Применяет ход с подсветкой и анимациями"""
        # Сохраняем координаты для подсветки
        self.last_move = [(r, c) for r, c, _ in letters]
        
        # Добавляем буквы в fade-in анимацию
        for r, c, _ in letters:
            self.fade_in_letters[(r, c)] = 0.0
        
        # Применяем ход
        self.state.apply_move(player, letters)
        
        # Запускаем анимацию fade-in
        self.animate_fade_in()
        
        # Запускаем таймер для отключения подсветки
        if self.highlight_timer:
            self.root.after_cancel(self.highlight_timer)
        self.highlight_timer = self.root.after(2500, self.clear_highlight)
    
    def animate_fade_in(self):
        """Анимация плавного появления букв"""
        if not self.fade_in_letters:
            return
        
        # Обновляем прогресс всех букв
        completed = []
        for pos in self.fade_in_letters:
            self.fade_in_letters[pos] += 0.1
            if self.fade_in_letters[pos] >= 1.0:
                completed.append(pos)
        
        # Удаляем завершенные
        for pos in completed:
            del self.fade_in_letters[pos]
        
        self.refresh()
        
        # Продолжаем если есть незавершенные
        if self.fade_in_letters:
            self.fade_timer = self.root.after(30, self.animate_fade_in)
    
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
        """Умный AI с использованием Trie и алгоритма якорных точек"""
        
        # Используем SmartAI если доступен
        if hasattr(self, 'smart_ai') and self.smart_ai:
            best_move = self.smart_ai.find_best_move(self.state, self.player2)
            
            if best_move:
                # Сбрасываем счетчик замен при успешном ходе
                self.ai_swap_counter = 0
                
                # Используем слово из best_move (уже собрано полное слово в SmartAI)
                full_word = best_move.word
                
                # Применяем найденный ход
                self.apply_move_with_highlight(self.player2, best_move.letters)
                
                # Анимация всплывающих очков для AI
                if best_move.letters:
                    center_r = sum(r for r, c, _ in best_move.letters) // len(best_move.letters)
                    center_c = sum(c for r, c, _ in best_move.letters) // len(best_move.letters)
                    x = center_c * self.cell_size + self.cell_size // 2
                    y = center_r * self.cell_size + self.cell_size // 2
                    
                    create_float_text(self.board, x, y + 30, f"+{best_move.score}", Colors.DANGER, 1200)
                    
                    # Конфетти если 7 букв
                    if len(best_move.letters) == 7:
                        particle = ParticleEffect(self.board, x, y, count=30)
                        self.particles.append(particle)
                
                # Показываем ПОЛНОЕ слово, а не только добавленные буквы
                messagebox.showinfo("Ход AI", 
                                  f"🤖 AI составил слово: {full_word}\n"
                                  f"✨ Очки: {best_move.score}")
                self.end_turn()
                return
        
        # Если SmartAI не смог найти ход, используем резервную стратегию
        rack = self.state.racks[self.player2][:]
        
        # Резервная стратегия: пробуем добавить 1 букву рядом
        for (r, c) in self.state.board.keys():
            for letter in rack:
                # Пробуем 4 направления
                for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < 15 and 0 <= nc < 15 and (nr, nc) not in self.state.board:
                        test_letters = [(nr, nc, letter)]
                        ok, _ = self.state.can_place(self.player2, test_letters)
                        if ok:
                            # Сбрасываем счетчик при успешном ходе
                            self.ai_swap_counter = 0
                            self.apply_move_with_highlight(self.player2, test_letters)
                            self.end_turn()
                            return
        
        # Если не нашли ход - меняем буквы или пропускаем
        # ВАЖНО: Ограничиваем количество замен подряд
        if not hasattr(self, 'ai_swap_counter'):
            self.ai_swap_counter = 0
        
        if len(rack) >= 3 and len(self.state.bag) >= 3 and self.ai_swap_counter < 2:
            # Меняем буквы (максимум 2 раза подряд)
            to_swap = random.sample(rack, min(3, len(rack)))
            self.state.swap_letters(self.player2, to_swap)
            self.ai_swap_counter += 1
            messagebox.showinfo("Ход AI", f"🤖 AI меняет {len(to_swap)} буквы")
            
            # ВАЖНО: Обновляем интерфейс и завершаем ход
            self.refresh()
            self.end_turn()
        else:
            # Пропускаем ход и сбрасываем счетчик
            self.ai_swap_counter = 0
            messagebox.showinfo("Ход AI", "🤖 AI пропускает ход")
            
            # Переключаем игрока вручную и обновляем
            self.current = self.player1
            self.state.current = self.player1
            self.refresh()
            self.end_turn()
    
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
