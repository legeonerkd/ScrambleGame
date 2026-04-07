# ui_styles.py
"""Стили и константы для UI игры Scrabble"""

# ============ ЦВЕТОВАЯ СХЕМА ============

# Основные цвета (современная темная тема с акцентами)
class Colors:
    # Фон
    BG_DARK = "#1e272e"          # Темный фон
    BG_LIGHT = "#2f3640"         # Светлый фон
    BG_CARD = "#353b48"          # Фон карточек
    
    # Игровое поле
    BOARD_BG = "#8e5d3c"         # Фон доски (дерево)
    CELL_EMPTY = "#f5e6d3"       # Пустая клетка (бежевый)
    CELL_FILLED = "#d4a574"      # Занятая клетка (светло-коричневая)
    CELL_OUTLINE = "#6b4423"     # Обводка клетки (темно-коричневая)
    
    # Буквы
    LETTER_TILE = "#ffd32a"      # Желтая плитка с буквой
    LETTER_TILE_SHADOW = "#ffa801"  # Тень плитки
    LETTER_TEXT = "#2f3542"      # Текст буквы
    LETTER_SELECTED = "#48dbfb" # Выбранная буква
    LETTER_SWAP = "#ff6348"      # Буква для замены
    
    # Бонусы (более насыщенные и контрастные)
    BONUS_WORD_2X = "#fc5c65"    # x2 к слову (красный)
    BONUS_WORD_3X = "#eb3b5a"    # x3 к слову (темно-красный)
    BONUS_LETTER_2X = "#45aaf2"  # x2 к букве (голубой)
    BONUS_LETTER_3X = "#2d98da"  # x3 к букве (синий)
    
    # Подсветка
    HIGHLIGHT = "#10ac84"        # Подсветка нового слова (изумрудный)
    HIGHLIGHT_BORDER = "#01a3a4" # Обводка подсветки
    HIGHLIGHT_TEXT = "#ffffff"   # Белый текст на подсветке
    
    # Превью размещения
    PREVIEW = "#5f27cd"          # Превью буквы (фиолетовый)
    
    # Акценты
    PRIMARY = "#5f27cd"          # Основной (фиолетовый)
    SUCCESS = "#00d2d3"          # Успех (бирюзовый)
    DANGER = "#ee5a6f"           # Опасность (красный)
    WARNING = "#feca57"          # Предупреждение (оранжевый)
    
    # Текст
    TEXT_PRIMARY = "#2f3542"     # Основной текст
    TEXT_SECONDARY = "#57606f"   # Вторичный текст
    TEXT_LIGHT = "#ffffff"       # Светлый текст


# ============ ШРИФТЫ ============

class Fonts:
    # Семейство шрифтов
    FAMILY = "Segoe UI"
    FAMILY_MONO = "Consolas"
    
    # Размеры
    TITLE = ("Segoe UI", 32, "bold")
    SUBTITLE = ("Segoe UI", 14)
    HEADER = ("Segoe UI", 13, "bold")
    BODY = ("Segoe UI", 11)
    SMALL = ("Segoe UI", 9)
    
    # Буквы на плитках
    TILE_LETTER = ("Arial", 18, "bold")
    TILE_LETTER_LARGE = ("Arial", 20, "bold")
    TILE_POINTS = ("Arial", 8)
    
    # Бонусы
    BONUS_TEXT = ("Arial", 8, "bold")
    BONUS_CENTER = ("Arial", 20)
    
    # Очки
    SCORE = ("Segoe UI", 12, "bold")


# ============ РАЗМЕРЫ ============

class Sizes:
    # Окно - обычный режим
    WINDOW_WIDTH = 950
    WINDOW_HEIGHT = 750
    
    # Окно - полноэкранный режим  
    WINDOW_WIDTH_FULLSCREEN = 1400
    WINDOW_HEIGHT_FULLSCREEN = 900
    
    # Игровое поле - обычный режим
    BOARD_SIZE = 510
    CELL_SIZE = 34
    
    # Игровое поле - полноэкранный режим
    BOARD_SIZE_FULLSCREEN = 750
    CELL_SIZE_FULLSCREEN = 50
    
    # Стойка - обычный режим
    RACK_WIDTH = 510
    RACK_HEIGHT = 110
    TILE_WIDTH = 58
    TILE_HEIGHT = 70
    
    # Стойка - полноэкранный режим
    RACK_WIDTH_FULLSCREEN = 750
    RACK_HEIGHT_FULLSCREEN = 140
    TILE_WIDTH_FULLSCREEN = 90
    TILE_HEIGHT_FULLSCREEN = 100
    
    # Отступы
    PADDING_SMALL = 5
    PADDING_MEDIUM = 10
    PADDING_LARGE = 20
    
    # Границы
    BORDER_THIN = 1
    BORDER_MEDIUM = 2
    BORDER_THICK = 3
    
    # Скругления (для эффекта)
    CORNER_RADIUS = 8


# ============ ЭФФЕКТЫ ============

class Effects:
    # Тени
    SHADOW_OFFSET = 2
    SHADOW_COLOR = "#00000040"  # Черный с прозрачностью
    
    # Анимация
    HIGHLIGHT_DURATION = 2500   # мс
    TRANSITION_DURATION = 300   # мс
    
    # Hover эффекты
    HOVER_BRIGHTNESS = 1.1


# ============ СТИЛИ КНОПОК ============

class ButtonStyles:
    PRIMARY = {
        'bg': Colors.PRIMARY,
        'fg': Colors.TEXT_LIGHT,
        'font': Fonts.HEADER,
        'relief': 'flat',
        'activebackground': '#341f97',
        'cursor': 'hand2',
        'padx': 20,
        'pady': 10
    }
    
    SUCCESS = {
        'bg': Colors.SUCCESS,
        'fg': Colors.TEXT_LIGHT,
        'font': Fonts.HEADER,
        'relief': 'flat',
        'activebackground': '#00a8a8',
        'cursor': 'hand2',
        'padx': 20,
        'pady': 10
    }
    
    DANGER = {
        'bg': Colors.DANGER,
        'fg': Colors.TEXT_LIGHT,
        'font': Fonts.HEADER,
        'relief': 'flat',
        'activebackground': '#c44569',
        'cursor': 'hand2',
        'padx': 20,
        'pady': 10
    }
    
    WARNING = {
        'bg': Colors.WARNING,
        'fg': Colors.TEXT_PRIMARY,
        'font': Fonts.HEADER,
        'relief': 'flat',
        'activebackground': '#f8b500',
        'cursor': 'hand2',
        'padx': 20,
        'pady': 10
    }
    
    SECONDARY = {
        'bg': Colors.BG_CARD,
        'fg': Colors.TEXT_LIGHT,
        'font': Fonts.BODY,
        'relief': 'flat',
        'activebackground': '#2f3640',
        'cursor': 'hand2',
        'padx': 15,
        'pady': 8
    }


# ============ СТИЛИ ИГРОВЫХ ЭЛЕМЕНТОВ ============

class GameStyles:
    """Стили для игровых элементов"""
    
    # Клетки доски
    CELL_NORMAL = {
        'fill': Colors.CELL_EMPTY,
        'outline': Colors.CELL_OUTLINE,
        'width': Sizes.BORDER_THIN
    }
    
    CELL_OCCUPIED = {
        'fill': Colors.CELL_FILLED,
        'outline': Colors.CELL_OUTLINE,
        'width': Sizes.BORDER_THIN
    }
    
    CELL_HIGHLIGHTED = {
        'fill': Colors.HIGHLIGHT,
        'outline': Colors.HIGHLIGHT_BORDER,
        'width': Sizes.BORDER_THICK
    }
    
    # Бонусные клетки
    BONUS_WORD_2X = {
        'fill': Colors.BONUS_WORD_2X,
        'outline': Colors.CELL_OUTLINE,
        'width': Sizes.BORDER_THIN
    }
    
    BONUS_WORD_3X = {
        'fill': Colors.BONUS_WORD_3X,
        'outline': Colors.CELL_OUTLINE,
        'width': Sizes.BORDER_THIN
    }
    
    BONUS_LETTER_2X = {
        'fill': Colors.BONUS_LETTER_2X,
        'outline': Colors.CELL_OUTLINE,
        'width': Sizes.BORDER_THIN
    }
    
    BONUS_LETTER_3X = {
        'fill': Colors.BONUS_LETTER_3X,
        'outline': Colors.CELL_OUTLINE,
        'width': Sizes.BORDER_THIN
    }
    
    # Плитки с буквами
    TILE_NORMAL = {
        'fill': Colors.LETTER_TILE,
        'outline': Colors.LETTER_TILE_SHADOW,
        'width': Sizes.BORDER_MEDIUM
    }
    
    TILE_SELECTED = {
        'fill': Colors.LETTER_SELECTED,
        'outline': '#0abde3',
        'width': Sizes.BORDER_THICK
    }
    
    TILE_SWAP = {
        'fill': Colors.LETTER_SWAP,
        'outline': '#ff4757',
        'width': Sizes.BORDER_THICK
    }


# ============ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ============

def create_gradient_rect(canvas, x1, y1, x2, y2, color1, color2, steps=50):
    """
    Создает прямоугольник с градиентом (вертикальным).
    
    Args:
        canvas: Canvas для рисования
        x1, y1, x2, y2: Координаты прямоугольника
        color1: Начальный цвет (hex)
        color2: Конечный цвет (hex)
        steps: Количество шагов градиента
    """
    height = y2 - y1
    step_height = height / steps
    
    # Преобразуем hex в RGB
    r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
    r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
    
    for i in range(steps):
        # Интерполяция цвета
        r = int(r1 + (r2 - r1) * i / steps)
        g = int(g1 + (g2 - g1) * i / steps)
        b = int(b1 + (b2 - b1) * i / steps)
        color = f'#{r:02x}{g:02x}{b:02x}'
        
        y_start = y1 + i * step_height
        y_end = y_start + step_height
        
        canvas.create_rectangle(x1, y_start, x2, y_end, fill=color, outline=color)


def create_rounded_rect(canvas, x1, y1, x2, y2, radius=10, **kwargs):
    """
    Создает прямоугольник со скругленными углами.
    
    Args:
        canvas: Canvas для рисования
        x1, y1, x2, y2: Координаты
        radius: Радиус скругления
        **kwargs: Дополнительные параметры (fill, outline, width)
    """
    points = [
        x1+radius, y1,
        x1+radius, y1,
        x2-radius, y1,
        x2-radius, y1,
        x2, y1,
        x2, y1+radius,
        x2, y1+radius,
        x2, y2-radius,
        x2, y2-radius,
        x2, y2,
        x2-radius, y2,
        x2-radius, y2,
        x1+radius, y2,
        x1+radius, y2,
        x1, y2,
        x1, y2-radius,
        x1, y2-radius,
        x1, y1+radius,
        x1, y1+radius,
        x1, y1
    ]
    return canvas.create_polygon(points, **kwargs, smooth=True)


def create_3d_tile(canvas, x, y, width, height, color_top, color_side, text="", text_color="#000"):
    """
    Создает плитку с 3D эффектом.
    
    Args:
        canvas: Canvas для рисования
        x, y: Позиция (центр)
        width, height: Размеры
        color_top: Цвет верхней грани
        color_side: Цвет боковой грани (тени)
        text: Текст на плитке
        text_color: Цвет текста
    """
    offset = 3  # Глубина 3D эффекта
    
    # Тень (боковая грань)
    canvas.create_rectangle(
        x - width//2 + offset, y - height//2 + offset,
        x + width//2 + offset, y + height//2 + offset,
        fill=color_side, outline=color_side
    )
    
    # Основная плитка
    canvas.create_rectangle(
        x - width//2, y - height//2,
        x + width//2, y + height//2,
        fill=color_top, outline=color_side, width=2
    )
    
    # Текст
    if text:
        canvas.create_text(x, y, text=text, font=Fonts.TILE_LETTER, 
                          fill=text_color, anchor="center")
